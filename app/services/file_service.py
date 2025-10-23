"""
File Service
Handles file storage, retrieval, and management operations
"""

import os
import uuid
import mimetypes
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from app.core.config import get_settings

settings = get_settings()


class FileService:
    """Service for file operations"""
    
    def __init__(self):
        self.storage_path = settings.STORAGE_PATH
        self.temp_path = settings.TEMP_PATH
        self.cache_path = settings.CACHE_PATH
        self.logs_path = settings.LOGS_PATH
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        directories = [
            self.storage_path,
            self.temp_path,
            self.cache_path,
            self.logs_path,
            os.path.join(self.storage_path, "generated"),
            os.path.join(self.storage_path, "uploads"),
            os.path.join(self.storage_path, "projects")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    async def store_file(
        self,
        file_id: str,
        content: bytes,
        filename: str,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> str:
        """Store file content"""
        try:
            # Determine storage path
            if project_id:
                storage_dir = os.path.join(self.storage_path, "projects", project_id)
            else:
                storage_dir = os.path.join(self.storage_path, "uploads")
            
            os.makedirs(storage_dir, exist_ok=True)
            
            # Generate file path
            file_extension = os.path.splitext(filename)[1]
            file_path = os.path.join(storage_dir, f"{file_id}{file_extension}")
            
            # Write file
            with open(file_path, "wb") as f:
                f.write(content)
            
            return file_path
            
        except Exception as e:
            raise Exception(f"File storage failed: {str(e)}")
    
    async def get_file_content(
        self,
        file_id: str,
        upload_path: str
    ) -> bytes:
        """Get file content"""
        try:
            if not os.path.exists(upload_path):
                raise Exception("File not found")
            
            with open(upload_path, "rb") as f:
                return f.read()
                
        except Exception as e:
            raise Exception(f"File retrieval failed: {str(e)}")
    
    async def delete_file(
        self,
        file_id: str,
        upload_path: str
    ) -> bool:
        """Delete file"""
        try:
            if os.path.exists(upload_path):
                os.remove(upload_path)
                return True
            return False
            
        except Exception as e:
            raise Exception(f"File deletion failed: {str(e)}")
    
    async def list_files(
        self,
        project_id: Optional[str] = None,
        file_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List files with filtering"""
        try:
            files = []
            
            # Determine search directory
            if project_id:
                search_dir = os.path.join(self.storage_path, "projects", project_id)
            else:
                search_dir = os.path.join(self.storage_path, "uploads")
            
            if not os.path.exists(search_dir):
                return files
            
            # Get all files
            for root, dirs, filenames in os.walk(search_dir):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    file_stat = os.stat(file_path)
                    
                    # Get file info
                    file_info = {
                        "filename": filename,
                        "path": file_path,
                        "size": file_stat.st_size,
                        "created_at": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                        "modified_at": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        "file_type": os.path.splitext(filename)[1].lower().lstrip('.'),
                        "mime_type": mimetypes.guess_type(filename)[0] or "application/octet-stream"
                    }
                    
                    # Apply filters
                    if file_type and file_info["file_type"] != file_type:
                        continue
                    
                    files.append(file_info)
            
            # Sort by modified time (newest first)
            files.sort(key=lambda x: x["modified_at"], reverse=True)
            
            # Apply pagination
            return files[offset:offset + limit]
            
        except Exception as e:
            raise Exception(f"File listing failed: {str(e)}")
    
    async def count_files(
        self,
        project_id: Optional[str] = None,
        file_type: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> int:
        """Count files with filtering"""
        try:
            count = 0
            
            # Determine search directory
            if project_id:
                search_dir = os.path.join(self.storage_path, "projects", project_id)
            else:
                search_dir = os.path.join(self.storage_path, "uploads")
            
            if not os.path.exists(search_dir):
                return count
            
            # Count files
            for root, dirs, filenames in os.walk(search_dir):
                for filename in filenames:
                    if file_type:
                        file_ext = os.path.splitext(filename)[1].lower().lstrip('.')
                        if file_ext != file_type:
                            continue
                    count += 1
            
            return count
            
        except Exception as e:
            raise Exception(f"File counting failed: {str(e)}")
    
    async def search_files(
        self,
        query: str,
        file_types: Optional[List[str]] = None,
        project_id: Optional[str] = None,
        recursive: bool = True,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search files by content or metadata"""
        try:
            results = []
            
            # Determine search directory
            if project_id:
                search_dir = os.path.join(self.storage_path, "projects", project_id)
            else:
                search_dir = os.path.join(self.storage_path, "uploads")
            
            if not os.path.exists(search_dir):
                return results
            
            # Search files
            for root, dirs, filenames in os.walk(search_dir):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    
                    # Check file type filter
                    if file_types:
                        file_ext = os.path.splitext(filename)[1].lower().lstrip('.')
                        if file_ext not in file_types:
                            continue
                    
                    # Search in filename
                    if query.lower() in filename.lower():
                        file_info = await self._get_file_info(file_path)
                        results.append(file_info)
                        continue
                    
                    # Search in file content (for text files)
                    if self._is_text_file(filename):
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                                if query.lower() in content.lower():
                                    file_info = await self._get_file_info(file_path)
                                    results.append(file_info)
                        except (UnicodeDecodeError, PermissionError):
                            # Skip binary files or files with encoding issues
                            continue
            
            return results
            
        except Exception as e:
            raise Exception(f"File search failed: {str(e)}")
    
    async def get_file_info(
        self,
        file_id: str,
        upload_path: str
    ) -> Dict[str, Any]:
        """Get detailed file information"""
        try:
            if not os.path.exists(upload_path):
                raise Exception("File not found")
            
            file_stat = os.stat(upload_path)
            
            return {
                "file_id": file_id,
                "path": upload_path,
                "size": file_stat.st_size,
                "created_at": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                "is_file": os.path.isfile(upload_path),
                "is_directory": os.path.isdir(upload_path),
                "permissions": oct(file_stat.st_mode)[-3:],
                "hash": await self._calculate_file_hash(upload_path)
            }
            
        except Exception as e:
            raise Exception(f"File info retrieval failed: {str(e)}")
    
    async def validate_files(
        self,
        file_paths: List[str],
        validation_rules: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate files against rules"""
        try:
            results = {
                "valid_files": [],
                "invalid_files": [],
                "errors": []
            }
            
            for file_path in file_paths:
                try:
                    # Check if file exists
                    if not os.path.exists(file_path):
                        results["invalid_files"].append({
                            "path": file_path,
                            "error": "File not found"
                        })
                        continue
                    
                    # Get file info
                    file_info = await self._get_file_info(str(uuid.uuid4()), file_path)
                    
                    # Apply validation rules
                    is_valid = True
                    errors = []
                    
                    if validation_rules:
                        # Check file size
                        max_size = validation_rules.get("max_size")
                        if max_size and file_info["size"] > max_size:
                            is_valid = False
                            errors.append(f"File too large: {file_info['size']} > {max_size}")
                        
                        # Check file type
                        allowed_types = validation_rules.get("allowed_types")
                        if allowed_types:
                            file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')
                            if file_ext not in allowed_types:
                                is_valid = False
                                errors.append(f"File type not allowed: {file_ext}")
                    
                    if is_valid:
                        results["valid_files"].append({
                            "path": file_path,
                            "info": file_info
                        })
                    else:
                        results["invalid_files"].append({
                            "path": file_path,
                            "errors": errors
                        })
                
                except Exception as e:
                    results["errors"].append({
                        "path": file_path,
                        "error": str(e)
                    })
            
            return results
            
        except Exception as e:
            raise Exception(f"File validation failed: {str(e)}")
    
    async def create_project_directory(
        self,
        project_id: str,
        user_id: Optional[str] = None
    ) -> str:
        """Create project directory structure"""
        try:
            project_dir = os.path.join(self.storage_path, "projects", project_id)
            
            # Create directory structure
            directories = [
                project_dir,
                os.path.join(project_dir, "frontend"),
                os.path.join(project_dir, "backend"),
                os.path.join(project_dir, "assets"),
                os.path.join(project_dir, "docs"),
                os.path.join(project_dir, "tests")
            ]
            
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
            
            return project_dir
            
        except Exception as e:
            raise Exception(f"Project directory creation failed: {str(e)}")
    
    # Private helper methods
    
    async def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information"""
        file_stat = os.stat(file_path)
        
        return {
            "filename": os.path.basename(file_path),
            "path": file_path,
            "size": file_stat.st_size,
            "created_at": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            "file_type": os.path.splitext(file_path)[1].lower().lstrip('.'),
            "mime_type": mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        }
    
    def _is_text_file(self, filename: str) -> bool:
        """Check if file is likely a text file"""
        text_extensions = {
            'txt', 'md', 'json', 'xml', 'html', 'css', 'js', 'jsx', 'ts', 'tsx',
            'py', 'java', 'cpp', 'c', 'h', 'php', 'rb', 'go', 'rs', 'swift',
            'yaml', 'yml', 'toml', 'ini', 'cfg', 'conf', 'log'
        }
        
        file_ext = os.path.splitext(filename)[1].lower().lstrip('.')
        return file_ext in text_extensions
    
    async def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate file hash"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
