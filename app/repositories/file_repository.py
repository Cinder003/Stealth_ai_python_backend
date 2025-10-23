"""
File Repository
Handles file system operations
"""

import os
import shutil
from typing import Dict, List, Optional, Any
from pathlib import Path

from app.core.config import get_settings

settings = get_settings()


class FileRepository:
    """Repository for file system operations"""
    
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
            self.logs_path
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def save_file(
        self,
        file_path: str,
        content: str,
        create_dirs: bool = True
    ) -> bool:
        """Save content to file"""
        try:
            if create_dirs:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception:
            return False
    
    def read_file(self, file_path: str) -> Optional[str]:
        """Read content from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        return os.path.isfile(file_path)
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size"""
        try:
            return os.path.getsize(file_path)
        except Exception:
            return 0
    
    def list_files(
        self,
        directory: str,
        pattern: str = "*",
        recursive: bool = False
    ) -> List[str]:
        """List files in directory"""
        try:
            if recursive:
                return [str(f) for f in Path(directory).rglob(pattern) if f.is_file()]
            else:
                return [str(f) for f in Path(directory).glob(pattern) if f.is_file()]
        except Exception:
            return []
    
    def create_directory(self, directory: str) -> bool:
        """Create directory"""
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except Exception:
            return False
    
    def delete_directory(self, directory: str) -> bool:
        """Delete directory"""
        try:
            if os.path.exists(directory):
                shutil.rmtree(directory)
                return True
            return False
        except Exception:
            return False
