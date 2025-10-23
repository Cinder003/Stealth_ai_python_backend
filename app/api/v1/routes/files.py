"""
File Operations Routes
Handles file management, upload, download, and organization
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.models.schemas import FileUploadResponse, FileListResponse
from app.controllers.file_controller import FileController
from app.core.security import get_current_user
from app.core.config import get_settings

router = APIRouter(prefix="/files", tags=["File Operations"])
settings = get_settings()

# Initialize controller
file_controller = FileController()


class FileSearchRequest(BaseModel):
    """Request for file search"""
    query: str = Field(..., description="Search query")
    file_types: Optional[List[str]] = Field(default=None, description="File types to search")
    project_id: Optional[str] = Field(default=None, description="Project ID to search within")
    recursive: bool = Field(default=True, description="Search recursively")


class FileOrganizeRequest(BaseModel):
    """Request for file organization"""
    project_id: str = Field(..., description="Project ID")
    organization_strategy: str = Field(default="framework", description="Organization strategy")
    create_directories: bool = Field(default=True, description="Create directory structure")
    move_files: bool = Field(default=False, description="Move files to organized structure")


class FileCompressRequest(BaseModel):
    """Request for file compression"""
    file_paths: List[str] = Field(..., description="Paths to compress")
    compression_format: str = Field(default="zip", description="Compression format")
    compression_level: int = Field(default=6, description="Compression level (1-9)")


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    project_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Upload a file
    """
    try:
        result = await file_controller.upload_file(
            file=file,
            project_id=project_id,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@router.post("/upload-multiple", response_model=List[FileUploadResponse])
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    project_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Upload multiple files
    """
    try:
        results = await file_controller.upload_multiple_files(
            files=files,
            project_id=project_id,
            user_id=current_user.get("id")
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multiple file upload failed: {str(e)}")


@router.get("/list", response_model=FileListResponse)
async def list_files(
    project_id: Optional[str] = None,
    file_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """
    List files with optional filtering
    """
    try:
        result = await file_controller.list_files(
            project_id=project_id,
            file_type=file_type,
            limit=limit,
            offset=offset,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")


@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Download a file
    """
    try:
        file_data = await file_controller.download_file(
            file_id=file_id,
            user_id=current_user.get("id")
        )
        return file_data
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a file
    """
    try:
        result = await file_controller.delete_file(
            file_id=file_id,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File deletion failed: {str(e)}")


@router.post("/search", response_model=List[Dict[str, Any]])
async def search_files(
    request: FileSearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Search files by content or metadata
    """
    try:
        results = await file_controller.search_files(
            request=request,
            user_id=current_user.get("id")
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File search failed: {str(e)}")


@router.post("/organize")
async def organize_files(
    request: FileOrganizeRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Organize files in a project
    """
    try:
        result = await file_controller.organize_files(
            request=request,
            background_tasks=background_tasks,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File organization failed: {str(e)}")


@router.post("/compress")
async def compress_files(
    request: FileCompressRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Compress files into archive
    """
    try:
        result = await file_controller.compress_files(
            request=request,
            background_tasks=background_tasks,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File compression failed: {str(e)}")


@router.get("/info/{file_id}")
async def get_file_info(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed file information
    """
    try:
        info = await file_controller.get_file_info(
            file_id=file_id,
            user_id=current_user.get("id")
        )
        return info
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")


@router.post("/validate")
async def validate_files(
    file_paths: List[str],
    validation_rules: Optional[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Validate files against rules
    """
    try:
        results = await file_controller.validate_files(
            file_paths=file_paths,
            validation_rules=validation_rules,
            user_id=current_user.get("id")
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File validation failed: {str(e)}")


@router.get("/templates")
async def get_file_templates():
    """
    Get available file templates
    """
    try:
        templates = await file_controller.get_available_templates()
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")
