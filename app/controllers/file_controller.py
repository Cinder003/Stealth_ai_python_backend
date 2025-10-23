"""
File Operations Controller
Handles file management, upload, download, and organization
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import uuid
import mimetypes

from app.models.schemas import FileUploadResponse, FileListResponse
from app.services.file_service import FileService
from app.services.cache_service import CacheService
from app.services.observability_service import ObservabilityService
from app.helpers.file_organizer import FileOrganizer
from app.helpers.compression import CompressionHelper
from app.core.config import get_settings

settings = get_settings()


class FileController:
    """Controller for file operations"""
    
    def __init__(self):
        self.file_service = FileService()
        self.cache_service = CacheService()
        self.observability_service = ObservabilityService()
        self.file_organizer = FileOrganizer()
        self.compression_helper = CompressionHelper()
    
    async def upload_file(
        self,
        file,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> FileUploadResponse:
        """
        Upload a file
        """
        try:
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            
            # Get file metadata
            filename = file.filename
            content_type = file.content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
            
            # Read file content
            content = await file.read()
            size = len(content)
            
            # Validate file
            if size > settings.MAX_FILE_SIZE:
                raise ValueError(f"File too large. Max size: {settings.MAX_FILE_SIZE} bytes")
            
            # Check file extension
            file_ext = os.path.splitext(filename)[1].lower().lstrip('.')
            if file_ext not in settings.ALLOWED_EXTENSIONS.split(','):
                raise ValueError(f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}")
            
            # Store file
            upload_path = await self.file_service.store_file(
                file_id=file_id,
                content=content,
                filename=filename,
                project_id=project_id,
                user_id=user_id
            )
            
            # Store metadata
            metadata = {
                "file_id": file_id,
                "filename": filename,
                "size": size,
                "content_type": content_type,
                "upload_path": upload_path,
                "project_id": project_id,
                "user_id": user_id,
                "uploaded_at": datetime.utcnow().isoformat()
            }
            
            await self.cache_service.set(
                f"file_metadata:{file_id}",
                metadata,
                ttl=86400 * 30  # 30 days
            )
            
            # Log upload
            await self.observability_service.log_file_upload(
                file_id=file_id,
                filename=filename,
                size=size,
                user_id=user_id
            )
            
            return FileUploadResponse(
                success=True,
                file_id=file_id,
                filename=filename,
                size=size,
                content_type=content_type,
                upload_path=upload_path,
                metadata=metadata
            )
            
        except Exception as e:
            return FileUploadResponse(
                success=False,
                file_id="",
                filename=file.filename if hasattr(file, 'filename') else "",
                size=0,
                content_type="",
                upload_path="",
                metadata={"error": str(e)}
            )
    
    async def upload_multiple_files(
        self,
        files: List,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[FileUploadResponse]:
        """
        Upload multiple files
        """
        results = []
        
        for file in files:
            result = await self.upload_file(
                file=file,
                project_id=project_id,
                user_id=user_id
            )
            results.append(result)
        
        return results
    
    async def list_files(
        self,
        project_id: Optional[str] = None,
        file_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        user_id: Optional[str] = None
    ) -> FileListResponse:
        """
        List files with optional filtering
        """
        try:
            # Get files from storage
            files = await self.file_service.list_files(
                project_id=project_id,
                file_type=file_type,
                limit=limit,
                offset=offset,
                user_id=user_id
            )
            
            # Get total count
            total = await self.file_service.count_files(
                project_id=project_id,
                file_type=file_type,
                user_id=user_id
            )
            
            return FileListResponse(
                success=True,
                files=files,
                total=total,
                limit=limit,
                offset=offset
            )
            
        except Exception as e:
            return FileListResponse(
                success=False,
                files=[],
                total=0,
                limit=limit,
                offset=offset
            )
    
    async def download_file(
        self,
        file_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Download a file
        """
        try:
            # Get file metadata
            metadata = await self.cache_service.get(f"file_metadata:{file_id}")
            if not metadata:
                raise Exception("File not found")
            
            # Check permissions
            if metadata.get("user_id") != user_id:
                raise Exception("Access denied")
            
            # Get file content
            content = await self.file_service.get_file_content(
                file_id=file_id,
                upload_path=metadata["upload_path"]
            )
            
            return {
                "success": True,
                "content": content,
                "filename": metadata["filename"],
                "content_type": metadata["content_type"],
                "size": metadata["size"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_file(
        self,
        file_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete a file
        """
        try:
            # Get file metadata
            metadata = await self.cache_service.get(f"file_metadata:{file_id}")
            if not metadata:
                raise Exception("File not found")
            
            # Check permissions
            if metadata.get("user_id") != user_id:
                raise Exception("Access denied")
            
            # Delete file from storage
            await self.file_service.delete_file(
                file_id=file_id,
                upload_path=metadata["upload_path"]
            )
            
            # Remove metadata from cache
            await self.cache_service.delete(f"file_metadata:{file_id}")
            
            return {"success": True, "file_id": file_id}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def search_files(
        self,
        request: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search files by content or metadata
        """
        try:
            results = await self.file_service.search_files(
                query=request["query"],
                file_types=request.get("file_types"),
                project_id=request.get("project_id"),
                recursive=request.get("recursive", True),
                user_id=user_id
            )
            
            return results
            
        except Exception as e:
            return []
    
    async def organize_files(
        self,
        request: Dict[str, Any],
        background_tasks,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Organize files in a project
        """
        try:
            result = await self.file_organizer.organize_project(
                project_id=request["project_id"],
                strategy=request.get("organization_strategy", "framework"),
                create_directories=request.get("create_directories", True),
                move_files=request.get("move_files", False),
                user_id=user_id
            )
            
            return {
                "success": True,
                "organization_result": result
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def compress_files(
        self,
        request: Dict[str, Any],
        background_tasks,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compress files into archive
        """
        try:
            result = await self.compression_helper.compress_files(
                file_paths=request["file_paths"],
                compression_format=request.get("compression_format", "zip"),
                compression_level=request.get("compression_level", 6),
                user_id=user_id
            )
            
            return {
                "success": True,
                "archive_path": result["archive_path"],
                "compressed_size": result["compressed_size"],
                "compression_ratio": result["compression_ratio"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_file_info(
        self,
        file_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get detailed file information
        """
        try:
            # Get file metadata
            metadata = await self.cache_service.get(f"file_metadata:{file_id}")
            if not metadata:
                raise Exception("File not found")
            
            # Check permissions
            if metadata.get("user_id") != user_id:
                raise Exception("Access denied")
            
            # Get additional file info
            file_info = await self.file_service.get_file_info(
                file_id=file_id,
                upload_path=metadata["upload_path"]
            )
            
            return {
                "success": True,
                "file_info": {**metadata, **file_info}
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def validate_files(
        self,
        file_paths: List[str],
        validation_rules: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate files against rules
        """
        try:
            results = await self.file_service.validate_files(
                file_paths=file_paths,
                validation_rules=validation_rules,
                user_id=user_id
            )
            
            return {
                "success": True,
                "validation_results": results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get available file templates"""
        return [
            {
                "name": "react_component",
                "description": "React component template",
                "files": ["Component.jsx", "Component.css", "Component.test.js"]
            },
            {
                "name": "api_endpoint",
                "description": "API endpoint template",
                "files": ["endpoint.py", "test_endpoint.py", "schema.py"]
            },
            {
                "name": "database_model",
                "description": "Database model template",
                "files": ["model.py", "migration.py", "test_model.py"]
            }
        ]
