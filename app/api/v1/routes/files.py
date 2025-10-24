"""
File download endpoints
Handles serving generated project files and ZIP downloads
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pathlib import Path
from app.core.security import validate_api_key

router = APIRouter(prefix="/files", tags=["File Downloads"])

@router.get("/download/{zip_name}")
async def download_project_zip(
    zip_name: str,
    api_key: str = Depends(validate_api_key)
):
    """
    Download a generated project ZIP file
    
    Args:
        zip_name: Name of the ZIP file to download
        api_key: API key for authentication
        
    Returns:
        FileResponse: The ZIP file for download
    """
    # Validate zip_name for security
    if not zip_name.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Invalid file format")
    
    # Check for path traversal attempts
    if '..' in zip_name or '/' in zip_name or '\\' in zip_name:
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    zip_path = Path("/app/storage/generated") / zip_name
    
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="ZIP file not found")
    
    if not zip_path.is_file():
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    return FileResponse(
        path=str(zip_path),
        media_type="application/zip",
        filename=zip_name,
        headers={"Content-Disposition": f"attachment; filename={zip_name}"}
    )

@router.get("/project/{project_id}/files")
async def list_project_files(
    project_id: str,
    api_key: str = Depends(validate_api_key)
):
    """
    List all files in a generated project
    
    Args:
        project_id: UUID of the project
        api_key: API key for authentication
        
    Returns:
        dict: List of files in the project
    """
    # Validate project_id for security
    if '..' in project_id or '/' in project_id or '\\' in project_id:
        raise HTTPException(status_code=400, detail="Invalid project ID")
    
    project_path = Path("/app/storage/generated") / project_id
    
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = []
    for file_path in project_path.rglob("*"):
        if file_path.is_file():
            rel_path = file_path.relative_to(project_path)
            files.append({
                "path": str(rel_path),
                "size": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime
            })
    
    return {
        "project_id": project_id,
        "files": files,
        "total_files": len(files)
    }