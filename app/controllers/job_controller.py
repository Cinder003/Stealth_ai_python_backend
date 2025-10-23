"""
Job Management Controller
Handles background job status, monitoring, and management
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

from app.models.schemas import JobStatusResponse, JobListResponse, JobStatus, JobType
from app.services.job_service import JobService
from app.services.cache_service import CacheService
from app.services.observability_service import ObservabilityService
from app.core.config import get_settings

settings = get_settings()


class JobController:
    """Controller for job management"""
    
    def __init__(self):
        self.job_service = JobService()
        self.cache_service = CacheService()
        self.observability_service = ObservabilityService()
    
    async def list_jobs(
        self,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> JobListResponse:
        """
        List jobs with optional filtering
        """
        try:
            # Get jobs from service
            jobs_data = await self.job_service.list_jobs(
                limit=limit,
                offset=offset,
                filters=filters,
                user_id=user_id
            )
            
            # Convert to response format
            jobs = []
            for job_data in jobs_data.get("jobs", []):
                job = JobStatusResponse(
                    job_id=job_data["job_id"],
                    status=JobStatus(job_data["status"]),
                    job_type=JobType(job_data["job_type"]),
                    progress=job_data.get("progress", 0.0),
                    created_at=datetime.fromisoformat(job_data["created_at"]),
                    started_at=datetime.fromisoformat(job_data["started_at"]) if job_data.get("started_at") else None,
                    completed_at=datetime.fromisoformat(job_data["completed_at"]) if job_data.get("completed_at") else None,
                    result=job_data.get("result"),
                    error=job_data.get("error"),
                    metadata=job_data.get("metadata", {})
                )
                jobs.append(job)
            
            return JobListResponse(
                success=True,
                jobs=jobs,
                total=jobs_data.get("total", 0),
                limit=limit,
                offset=offset
            )
            
        except Exception as e:
            return JobListResponse(
                success=False,
                jobs=[],
                total=0,
                limit=limit,
                offset=offset
            )
    
    async def get_job_status(
        self,
        job_id: str,
        user_id: Optional[str] = None
    ) -> JobStatusResponse:
        """
        Get job status and details
        """
        try:
            # Get job from service
            job_data = await self.job_service.get_job(
                job_id=job_id,
                user_id=user_id
            )
            
            if not job_data:
                raise Exception("Job not found")
            
            return JobStatusResponse(
                job_id=job_data["job_id"],
                status=JobStatus(job_data["status"]),
                job_type=JobType(job_data["job_type"]),
                progress=job_data.get("progress", 0.0),
                created_at=datetime.fromisoformat(job_data["created_at"]),
                started_at=datetime.fromisoformat(job_data["started_at"]) if job_data.get("started_at") else None,
                completed_at=datetime.fromisoformat(job_data["completed_at"]) if job_data.get("completed_at") else None,
                result=job_data.get("result"),
                error=job_data.get("error"),
                metadata=job_data.get("metadata", {})
            )
            
        except Exception as e:
            return JobStatusResponse(
                job_id=job_id,
                status=JobStatus.FAILED,
                job_type=JobType.CODE_GENERATION,
                progress=0.0,
                created_at=datetime.utcnow(),
                error=str(e)
            )
    
    async def cancel_job(
        self,
        job_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cancel a running job
        """
        try:
            result = await self.job_service.cancel_job(
                job_id=job_id,
                user_id=user_id
            )
            
            return {
                "success": True,
                "job_id": job_id,
                "cancelled": result.get("cancelled", False)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def retry_job(
        self,
        job_id: str,
        request: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retry a failed job
        """
        try:
            result = await self.job_service.retry_job(
                job_id=job_id,
                reset_status=request.get("reset_status", True) if request else True,
                max_retries=request.get("max_retries", 3) if request else 3,
                user_id=user_id
            )
            
            return {
                "success": True,
                "job_id": job_id,
                "retry_scheduled": result.get("retry_scheduled", False)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_job(
        self,
        job_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete a job and its associated data
        """
        try:
            result = await self.job_service.delete_job(
                job_id=job_id,
                user_id=user_id
            )
            
            return {
                "success": True,
                "job_id": job_id,
                "deleted": result.get("deleted", False)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_job_logs(
        self,
        job_id: str,
        limit: int = 100,
        offset: int = 0,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get job execution logs
        """
        try:
            logs = await self.job_service.get_job_logs(
                job_id=job_id,
                limit=limit,
                offset=offset,
                user_id=user_id
            )
            
            return {
                "success": True,
                "logs": logs
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_job_progress(
        self,
        job_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get job progress information
        """
        try:
            progress = await self.job_service.get_job_progress(
                job_id=job_id,
                user_id=user_id
            )
            
            return {
                "success": True,
                "progress": progress
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_job_result(
        self,
        job_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get job result data
        """
        try:
            result = await self.job_service.get_job_result(
                job_id=job_id,
                user_id=user_id
            )
            
            return {
                "success": True,
                "result": result
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def cleanup_jobs(
        self,
        older_than_days: int = 7,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Clean up old completed jobs
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
            
            result = await self.job_service.cleanup_jobs(
                cutoff_date=cutoff_date,
                user_id=user_id
            )
            
            return {
                "success": True,
                "cleaned_jobs": result.get("cleaned_count", 0),
                "cutoff_date": cutoff_date.isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_job_statistics(
        self,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get job statistics
        """
        try:
            stats = await self.job_service.get_job_statistics(
                user_id=user_id
            )
            
            return {
                "success": True,
                "statistics": stats
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_available_job_types(self) -> List[Dict[str, Any]]:
        """Get available job types"""
        return [
            {
                "type": "code_generation",
                "description": "Generate code from description",
                "estimated_duration": "30-120 seconds",
                "resource_usage": "medium"
            },
            {
                "type": "file_processing",
                "description": "Process uploaded files",
                "estimated_duration": "10-60 seconds",
                "resource_usage": "low"
            },
            {
                "type": "figma_analysis",
                "description": "Analyze Figma design files",
                "estimated_duration": "60-300 seconds",
                "resource_usage": "high"
            },
            {
                "type": "github_deploy",
                "description": "Deploy code to GitHub",
                "estimated_duration": "30-180 seconds",
                "resource_usage": "medium"
            },
            {
                "type": "cleanup",
                "description": "Clean up old files and data",
                "estimated_duration": "5-30 seconds",
                "resource_usage": "low"
            }
        ]
