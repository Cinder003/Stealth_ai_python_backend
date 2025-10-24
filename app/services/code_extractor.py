# app/services/code_extractor.py
import re
import os
import textwrap
import shutil
import zipfile
import logging
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger("code_extractor")
logger.setLevel(logging.INFO)

# Regex: captures `File: path` followed by a fenced code block ```lang\n...```
FILE_BLOCK_RE = re.compile(
    r"File:\s*(?P<path>[^\n]+)\n```(?:[a-zA-Z0-9+-]*)\n(?P<content>.*?)```",
    re.DOTALL | re.MULTILINE
)

# Allowed filename characters - avoid weird/unicode control sequences.
SAFE_FILENAME_RE = re.compile(r"^[\w\-\./]+$")

# Max file size to write (in bytes) - prevent massive single-file writes
MAX_FILE_BYTES = int(os.getenv("MAX_FILE_BYTES", 5 * 1024 * 1024))  # default 5MB

class CodeExtractorError(Exception):
    pass

class CodeExtractor:
    def __init__(self, base_storage_path: str = "/app/storage/generated"):
        self.base_storage = Path(base_storage_path)
        logger.debug("CodeExtractor base storage: %s", self.base_storage)

    def _sanitize_and_validate_path(self, relative_path: str) -> Path:
        """
        Normalize and validate a relative path:
        - no absolute paths
        - no path traversal (..)
        - only allowed characters
        """
        # Normalize
        norm = os.path.normpath(relative_path).lstrip(os.sep)
        # Prevent path traversal
        if norm.startswith("..") or ".." in norm.split(os.sep):
            raise CodeExtractorError(f"Invalid path (path traversal): {relative_path}")

        # Allow only safe characters
        if not SAFE_FILENAME_RE.match(norm):
            raise CodeExtractorError(f"Invalid filename characters in: {relative_path}")

        return Path(norm)

    def extract_files(self, llm_text: str) -> List[Tuple[str, str]]:
        """
        Parse LLM output and return [(relative_path, content), ...]
        """
        matches = list(FILE_BLOCK_RE.finditer(llm_text))
        logger.info("Found %d file blocks in LLM output", len(matches))
        files = []
        for m in matches:
            rel_path = m.group("path").strip()
            content = m.group("content")
            # dedent
            content = textwrap.dedent(content).rstrip() + "\n"
            files.append((rel_path, content))
        return files

    def save_files_for_project(self, project_id: str, files: List[Tuple[str, str]]) -> List[Path]:
        """
        Save files under /base_storage/{project_id}/frontend or /backend depending on path
        Returns list of absolute saved Paths.
        """
        saved = []
        project_root = self.base_storage / project_id
        for rel_path, content in files:
            # Determine frontend/backend root based on first path segment
            # User chose A; we'll accept 'frontend/' or 'backend/' prefix, else place in backend by default
            rel_path_obj = Path(rel_path)
            parts = rel_path_obj.parts
            if len(parts) == 0:
                raise CodeExtractorError("Empty path in LLM output")

            # If no top-level 'frontend' or 'backend', infer based on file extension:
            top = parts[0].lower()
            if top in ("frontend", "frontend/") or top == "frontend":
                target_base = project_root / "frontend"
                # remove leading 'frontend' prefix
                safe_rel = Path(*parts[1:]) if len(parts) > 1 else Path(rel_path_obj.name)
            elif top in ("backend", "backend/") or top == "backend":
                target_base = project_root / "backend"
                safe_rel = Path(*parts[1:]) if len(parts) > 1 else Path(rel_path_obj.name)
            else:
                # fallback heuristic by extension
                ext = rel_path_obj.suffix.lower()
                if ext in (".js", ".ts", ".json", ".yml", ".yaml", ".md"):
                    target_base = project_root / "frontend"  # many frontend files are js/ts
                    safe_rel = rel_path_obj
                else:
                    target_base = project_root / "backend"
                    safe_rel = rel_path_obj

            # sanitize final path
            safe_rel_posix = str(safe_rel.as_posix())
            validated_rel = self._sanitize_and_validate_path(safe_rel_posix)
            abs_path = (target_base / validated_rel).resolve()

            # Ensure abs_path is inside our project_root (avoid escapes)
            if project_root.resolve() not in abs_path.parents and abs_path.resolve() != project_root.resolve():
                # make sure file is within project_root
                if project_root.resolve() != abs_path.resolve() and project_root.resolve() not in abs_path.parents:
                    raise CodeExtractorError(f"Resolved path escapes project root: {abs_path}")

            # create parent
            abs_path.parent.mkdir(parents=True, exist_ok=True)

            # size guard
            if len(content.encode("utf-8")) > MAX_FILE_BYTES:
                raise CodeExtractorError(f"File {rel_path} is too large (> {MAX_FILE_BYTES} bytes)")

            # write file
            with open(abs_path, "w", encoding="utf-8") as fh:
                fh.write(content)

            logger.info("Saved file: %s", abs_path)
            saved.append(abs_path)

        return saved

    def create_project_zip(self, project_id: str, zip_name: str = None) -> Path:
        """
        Zip the project folder and return path to zip.
        """
        project_root = self.base_storage / project_id
        if not project_root.exists():
            raise CodeExtractorError("Project root does not exist: " + str(project_root))

        if zip_name is None:
            zip_name = f"{project_id}.zip"
        zip_path = self.base_storage / zip_name

        # Create zip (overwrite if exists)
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(project_root):
                for file in files:
                    abs_file = Path(root) / file
                    # store with relative path inside zip
                    rel = abs_file.relative_to(self.base_storage)
                    zf.write(abs_file, arcname=str(rel))
        logger.info("Created project zip: %s", zip_path)
        return zip_path

    def cleanup_project(self, project_id: str):
        """
        Remove entire project folder (useful for tests/cleanup).
        """
        project_root = self.base_storage / project_id
        if project_root.exists() and project_root.is_dir():
            shutil.rmtree(project_root)
            logger.info("Cleaned up project: %s", project_root)
