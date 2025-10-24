# app/services/llm_result_handler.py
import uuid
import logging
from fastapi import HTTPException
from .code_extractor import CodeExtractor, CodeExtractorError

logger = logging.getLogger("llm_result_handler")

extractor = CodeExtractor(base_storage_path="/app/storage/generated")  # matches Docker volume

def handle_and_save(llm_text: str, project_id: str = None, create_zip: bool = True):
    """
    Parse LLM output -> save files -> optionally create zip -> return metadata
    """
    if not project_id:
        # generate a UUID project id
        project_id = str(uuid.uuid4())

    # parse
    files = extractor.extract_files(llm_text)
    if not files:
        raise HTTPException(status_code=400, detail="No files found in LLM output")

    try:
        saved_paths = extractor.save_files_for_project(project_id, files)
    except CodeExtractorError as e:
        logger.exception("Error while saving files: %s", e)
        raise HTTPException(status_code=400, detail=f"File save error: {str(e)}")

    zip_path = None
    if create_zip:
        zip_path = extractor.create_project_zip(project_id)
    # Build response: relative paths + download URL
    saved_rel = [str(p.relative_to("/app/storage")) for p in saved_paths]  # e.g., generated/{id}/frontend/...
    resp = {
        "project_id": project_id,
        "saved_files_count": len(saved_paths),
        "saved_files": saved_rel,
        "zip_path": str(zip_path.relative_to("/app/storage")) if zip_path else None,
        "download_url": f"/download/{zip_path.name}" if zip_path else None
    }
    return resp
