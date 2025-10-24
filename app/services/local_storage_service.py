"""
Local Storage Service
Handles saving generated code to local machine directories
"""

import os
import shutil
import zipfile
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class LocalStorageService:
    """Service for managing local file storage and downloads"""
    
    def __init__(self):
        # Local paths (relative to project root)
        self.local_projects_path = Path("./generated_projects")
        self.local_downloads_path = Path("./downloads")
        self.auto_download_enabled = True
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create local directories if they don't exist"""
        self.local_projects_path.mkdir(parents=True, exist_ok=True)
        self.local_downloads_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Local storage directories created: {self.local_projects_path}, {self.local_downloads_path}")
    
    def save_project_locally(
        self, 
        project_id: str, 
        project_data: Dict[str, Any],
        create_zip: bool = True
    ) -> Dict[str, Any]:
        """
        Save generated project to local machine
        
        Args:
            project_id: Unique project identifier
            project_data: Generated code files and metadata
            create_zip: Whether to create a ZIP archive
            
        Returns:
            Dict with local paths and download info
        """
        try:
            # Create project directory
            project_dir = self.local_projects_path / project_id
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # Save individual files
            saved_files = []
            files_data = project_data.get("files", {})
            logger.info(f"Saving {len(files_data)} files to local storage")
            
            for file_path, content in files_data.items():
                try:
                    local_file_path = project_dir / file_path
                    local_file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Ensure content is not empty
                    if not content or len(content.strip()) == 0:
                        logger.warning(f"Empty content for file: {file_path}")
                        continue
                    
                    with open(local_file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    saved_files.append(str(local_file_path.relative_to(self.local_projects_path)))
                    logger.info(f"Saved file locally: {local_file_path} ({len(content)} chars)")
                except Exception as e:
                    logger.error(f"Failed to save file {file_path}: {e}")
                    continue
            
            # Create ZIP archive if requested
            zip_path = None
            if create_zip:
                zip_path = self._create_project_zip(project_id, project_dir)
            
            # Copy to downloads folder for easy access
            if self.auto_download_enabled and zip_path:
                download_path = self.local_downloads_path / f"{project_id}.zip"
                shutil.copy2(zip_path, download_path)
                logger.info(f"Project copied to downloads: {download_path}")
            
            return {
                "success": True,
                "project_id": project_id,
                "local_project_path": str(project_dir),
                "saved_files": saved_files,
                "zip_path": str(zip_path) if zip_path else None,
                "download_path": str(self.local_downloads_path / f"{project_id}.zip") if zip_path else None,
                "total_files": len(saved_files)
            }
            
        except Exception as e:
            logger.error(f"Failed to save project locally: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_project_zip(self, project_id: str, project_dir: Path) -> Path:
        """Create ZIP archive of the project"""
        zip_path = self.local_projects_path / f"{project_id}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in project_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(project_dir)
                    zipf.write(file_path, arcname)
        
        logger.info(f"Created project ZIP: {zip_path}")
        return zip_path
    
    def get_local_projects(self) -> list:
        """Get list of locally saved projects"""
        projects = []
        
        for project_dir in self.local_projects_path.iterdir():
            if project_dir.is_dir():
                projects.append({
                    "project_id": project_dir.name,
                    "path": str(project_dir),
                    "created_at": datetime.fromtimestamp(project_dir.stat().st_ctime).isoformat(),
                    "files_count": len(list(project_dir.rglob('*')))
                })
        
        return sorted(projects, key=lambda x: x["created_at"], reverse=True)
    
    def get_project_files(self, project_id: str) -> list:
        """Get files in a specific project"""
        project_dir = self.local_projects_path / project_id
        
        if not project_dir.exists():
            return []
        
        files = []
        for file_path in project_dir.rglob('*'):
            if file_path.is_file():
                files.append({
                    "path": str(file_path.relative_to(project_dir)),
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
        
        return files
    
    def download_project(self, project_id: str) -> Optional[Path]:
        """Get download path for a project"""
        zip_path = self.local_downloads_path / f"{project_id}.zip"
        
        if zip_path.exists():
            return zip_path
        
        # Create download if it doesn't exist
        project_dir = self.local_projects_path / project_id
        if project_dir.exists():
            return self._create_project_zip(project_id, project_dir)
        
        return None
    
    def cleanup_old_projects(self, days: int = 7):
        """Clean up projects older than specified days"""
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for project_dir in self.local_projects_path.iterdir():
            if project_dir.is_dir() and project_dir.stat().st_ctime < cutoff_time:
                shutil.rmtree(project_dir)
                logger.info(f"Cleaned up old project: {project_dir}")
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get local storage information"""
        total_size = sum(f.stat().st_size for f in self.local_projects_path.rglob('*') if f.is_file())
        project_count = len([d for d in self.local_projects_path.iterdir() if d.is_dir()])
        
        return {
            "local_projects_path": str(self.local_projects_path),
            "local_downloads_path": str(self.local_downloads_path),
            "total_projects": project_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "auto_download_enabled": self.auto_download_enabled
        }
