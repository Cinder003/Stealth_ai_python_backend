# app/services/llm_result_handler.py
import uuid
import logging
from fastapi import HTTPException
from .code_extractor import CodeExtractor, CodeExtractorError
from .local_storage_service import LocalStorageService

logger = logging.getLogger("llm_result_handler")

extractor = CodeExtractor(base_storage_path="/app/storage/generated")  # matches Docker volume
local_storage = LocalStorageService()  # Local storage service

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
    
    # Save to local machine as well
    try:
        # Prepare project data for local storage
        project_data = {
            "files": {},
            "metadata": {
                "project_id": project_id,
                "created_at": str(uuid.uuid4()),  # Use timestamp instead
                "source": "llm_generation"
            }
        }
        
        # Read files and prepare for local storage
        for saved_path in saved_paths:
            try:
                with open(saved_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Calculate relative path correctly
                    if str(saved_path).startswith("/app/storage/generated/"):
                        relative_path = str(saved_path)[len("/app/storage/generated/"):]
                    else:
                        # Fallback: use just the filename
                        relative_path = saved_path.name
                    project_data["files"][relative_path] = content
                    logger.info(f"Read file for local storage: {saved_path} -> {relative_path} ({len(content)} chars)")
            except Exception as e:
                logger.error(f"Failed to read file for local storage: {saved_path}, {e}")
        
        # Save to local storage
        local_result = local_storage.save_project_locally(project_id, project_data, create_zip)
        logger.info(f"Project saved locally: {local_result}")
        
    except Exception as e:
        logger.error(f"Failed to save project locally: {e}")
        # Continue without failing the main process
    
    # Build response: relative paths + download URL
    saved_rel = [str(p.relative_to("/app/storage")) for p in saved_paths]  # e.g., generated/{id}/frontend/...
    resp = {
        "project_id": project_id,
        "saved_files_count": len(saved_paths),
        "saved_files": saved_rel,
        "zip_path": str(zip_path.relative_to("/app/storage")) if zip_path else None,
        "download_url": f"/download/{zip_path.name}" if zip_path else None,
        "local_project_path": f"./generated_projects/{project_id}",
        "local_download_path": f"./downloads/{project_id}.zip" if create_zip else None
    }
    return resp
