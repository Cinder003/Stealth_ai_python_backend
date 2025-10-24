"""
Local Storage API Routes
Handles local file management and downloads
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import List, Dict, Any
import logging

from app.services.local_storage_service import LocalStorageService
from app.core.security import validate_api_key

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/local-storage", tags=["Local Storage"])

# Initialize service
local_storage_service = LocalStorageService()


@router.get("/projects")
async def get_local_projects(
    api_key: str = Depends(validate_api_key)
) -> List[Dict[str, Any]]:
    """
    Get list of locally saved projects
    """
    try:
        projects = local_storage_service.get_local_projects()
        return projects
    except Exception as e:
        logger.error(f"Failed to get local projects: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get projects: {str(e)}")


@router.get("/projects/{project_id}/files")
async def get_project_files(
    project_id: str,
    api_key: str = Depends(validate_api_key)
) -> List[Dict[str, Any]]:
    """
    Get files in a specific project
    """
    try:
        files = local_storage_service.get_project_files(project_id)
        return files
    except Exception as e:
        logger.error(f"Failed to get project files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get files: {str(e)}")


@router.get("/download/{project_id}")
async def download_project(
    project_id: str,
    api_key: str = Depends(validate_api_key)
):
    """
    Download a project as ZIP file
    """
    try:
        zip_path = local_storage_service.download_project(project_id)
        
        if not zip_path or not zip_path.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        return FileResponse(
            path=str(zip_path),
            filename=f"{project_id}.zip",
            media_type="application/zip"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.get("/info")
async def get_storage_info(
    api_key: str = Depends(validate_api_key)
) -> Dict[str, Any]:
    """
    Get local storage information
    """
    try:
        info = local_storage_service.get_storage_info()
        return info
    except Exception as e:
        logger.error(f"Failed to get storage info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get info: {str(e)}")


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    api_key: str = Depends(validate_api_key)
) -> Dict[str, Any]:
    """
    Delete a local project
    """
    try:
        import shutil
        from pathlib import Path
        
        project_dir = Path(f"./generated_projects/{project_id}")
        if project_dir.exists():
            shutil.rmtree(project_dir)
            logger.info(f"Deleted project: {project_id}")
            return {"success": True, "message": f"Project {project_id} deleted"}
        else:
            raise HTTPException(status_code=404, detail="Project not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.post("/cleanup")
async def cleanup_old_projects(
    days: int = 7,
    api_key: str = Depends(validate_api_key)
) -> Dict[str, Any]:
    """
    Clean up projects older than specified days
    """
    try:
        local_storage_service.cleanup_old_projects(days)
        return {"success": True, "message": f"Cleaned up projects older than {days} days"}
    except Exception as e:
        logger.error(f"Failed to cleanup projects: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")
