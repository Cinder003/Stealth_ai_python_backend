"""
Job Service
Handles background job management and monitoring
"""

import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

from app.core.config import get_settings

settings = get_settings()


class JobStatus(str, Enum):
    """Job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, Enum):
    """Job type enumeration"""
    CODE_GENERATION = "code_generation"
    FILE_PROCESSING = "file_processing"
    FIGMA_ANALYSIS = "figma_analysis"
    GITHUB_DEPLOY = "github_deploy"
    CLEANUP = "cleanup"


class JobService:
    """Service for job management"""
    
    def __init__(self):
        self.jobs = {}  # In-memory storage (replace with database in production)
        self.job_logs = {}  # In-memory logs storage
    
    async def create_job(
        self,
        job_type: JobType,
        payload: Dict[str, Any],
        user_id: Optional[str] = None,
        priority: int = 0
    ) -> str:
        """Create a new job"""
        try:
            job_id = str(uuid.uuid4())
            
            job_data = {
                "job_id": job_id,
                "job_type": job_type.value,
                "status": JobStatus.PENDING.value,
                "payload": payload,
                "user_id": user_id,
                "priority": priority,
                "created_at": datetime.utcnow().isoformat(),
                "started_at": None,
                "completed_at": None,
                "progress": 0.0,
                "result": None,
                "error": None,
                "retry_count": 0,
                "max_retries": 3,
                "metadata": {}
            }
            
            self.jobs[job_id] = job_data
            
            # Initialize logs
            self.job_logs[job_id] = []
            
            # Log job creation
            await self._log_job_event(job_id, "Job created", {"job_type": job_type.value})
            
            return job_id
            
        except Exception as e:
            raise Exception(f"Job creation failed: {str(e)}")
    
    async def get_job(
        self,
        job_id: str,
        user_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get job details"""
        try:
            job_data = self.jobs.get(job_id)
            
            if not job_data:
                return None
            
            # Check user permissions
            if user_id and job_data.get("user_id") != user_id:
                return None
            
            return job_data
            
        except Exception as e:
            raise Exception(f"Job retrieval failed: {str(e)}")
    
    async def list_jobs(
        self,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """List jobs with filtering"""
        try:
            jobs = list(self.jobs.values())
            
            # Apply user filter
            if user_id:
                jobs = [job for job in jobs if job.get("user_id") == user_id]
            
            # Apply additional filters
            if filters:
                if filters.get("status"):
                    jobs = [job for job in jobs if job["status"] == filters["status"]]
                
                if filters.get("job_type"):
                    jobs = [job for job in jobs if job["job_type"] == filters["job_type"]]
                
                if filters.get("created_after"):
                    cutoff_date = datetime.fromisoformat(filters["created_after"])
                    jobs = [job for job in jobs if datetime.fromisoformat(job["created_at"]) >= cutoff_date]
                
                if filters.get("created_before"):
                    cutoff_date = datetime.fromisoformat(filters["created_before"])
                    jobs = [job for job in jobs if datetime.fromisoformat(job["created_at"]) <= cutoff_date]
            
            # Sort by creation time (newest first)
            jobs.sort(key=lambda x: x["created_at"], reverse=True)
            
            # Apply pagination
            total = len(jobs)
            jobs = jobs[offset:offset + limit]
            
            return {
                "jobs": jobs,
                "total": total
            }
            
        except Exception as e:
            raise Exception(f"Job listing failed: {str(e)}")
    
    async def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: Optional[float] = None,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> bool:
        """Update job status"""
        try:
            if job_id not in self.jobs:
                return False
            
            job_data = self.jobs[job_id]
            job_data["status"] = status.value
            
            if progress is not None:
                job_data["progress"] = progress
            
            if result is not None:
                job_data["result"] = result
            
            if error is not None:
                job_data["error"] = error
            
            # Update timestamps
            if status == JobStatus.RUNNING and not job_data["started_at"]:
                job_data["started_at"] = datetime.utcnow().isoformat()
            elif status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                job_data["completed_at"] = datetime.utcnow().isoformat()
            
            # Log status change
            await self._log_job_event(job_id, f"Status changed to {status.value}", {
                "progress": progress,
                "has_result": result is not None,
                "has_error": error is not None
            })
            
            return True
            
        except Exception as e:
            raise Exception(f"Job status update failed: {str(e)}")
    
    async def cancel_job(
        self,
        job_id: str,
        user_id: Optional[str] = None
    ) -> bool:
        """Cancel a job"""
        try:
            job_data = self.jobs.get(job_id)
            
            if not job_data:
                return False
            
            # Check permissions
            if user_id and job_data.get("user_id") != user_id:
                return False
            
            # Only cancel pending or running jobs
            if job_data["status"] not in [JobStatus.PENDING.value, JobStatus.RUNNING.value]:
                return False
            
            # Update status
            await self.update_job_status(
                job_id=job_id,
                status=JobStatus.CANCELLED,
                error="Job cancelled by user"
            )
            
            return True
            
        except Exception as e:
            raise Exception(f"Job cancellation failed: {str(e)}")
    
    async def retry_job(
        self,
        job_id: str,
        reset_status: bool = True,
        max_retries: int = 3,
        user_id: Optional[str] = None
    ) -> bool:
        """Retry a failed job"""
        try:
            job_data = self.jobs.get(job_id)
            
            if not job_data:
                return False
            
            # Check permissions
            if user_id and job_data.get("user_id") != user_id:
                return False
            
            # Only retry failed jobs
            if job_data["status"] != JobStatus.FAILED.value:
                return False
            
            # Check retry count
            if job_data.get("retry_count", 0) >= max_retries:
                return False
            
            # Reset job
            job_data["retry_count"] = job_data.get("retry_count", 0) + 1
            job_data["error"] = None
            
            if reset_status:
                job_data["status"] = JobStatus.PENDING.value
                job_data["started_at"] = None
                job_data["completed_at"] = None
                job_data["progress"] = 0.0
                job_data["result"] = None
            
            # Log retry
            await self._log_job_event(job_id, f"Job retry #{job_data['retry_count']}", {
                "reset_status": reset_status,
                "max_retries": max_retries
            })
            
            return True
            
        except Exception as e:
            raise Exception(f"Job retry failed: {str(e)}")
    
    async def delete_job(
        self,
        job_id: str,
        user_id: Optional[str] = None
    ) -> bool:
        """Delete a job"""
        try:
            job_data = self.jobs.get(job_id)
            
            if not job_data:
                return False
            
            # Check permissions
            if user_id and job_data.get("user_id") != user_id:
                return False
            
            # Delete job and logs
            if job_id in self.jobs:
                del self.jobs[job_id]
            
            if job_id in self.job_logs:
                del self.job_logs[job_id]
            
            return True
            
        except Exception as e:
            raise Exception(f"Job deletion failed: {str(e)}")
    
    async def get_job_logs(
        self,
        job_id: str,
        limit: int = 100,
        offset: int = 0,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get job execution logs"""
        try:
            # Check job exists and permissions
            job_data = await self.get_job(job_id, user_id)
            if not job_data:
                return []
            
            logs = self.job_logs.get(job_id, [])
            
            # Apply pagination
            return logs[offset:offset + limit]
            
        except Exception as e:
            raise Exception(f"Job logs retrieval failed: {str(e)}")
    
    async def get_job_progress(
        self,
        job_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get job progress information"""
        try:
            job_data = await self.get_job(job_id, user_id)
            
            if not job_data:
                return {}
            
            return {
                "job_id": job_id,
                "status": job_data["status"],
                "progress": job_data.get("progress", 0.0),
                "created_at": job_data["created_at"],
                "started_at": job_data.get("started_at"),
                "estimated_completion": await self._estimate_completion(job_data)
            }
            
        except Exception as e:
            raise Exception(f"Job progress retrieval failed: {str(e)}")
    
    async def get_job_result(
        self,
        job_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get job result data"""
        try:
            job_data = await self.get_job(job_id, user_id)
            
            if not job_data:
                return {}
            
            return {
                "job_id": job_id,
                "status": job_data["status"],
                "result": job_data.get("result"),
                "error": job_data.get("error"),
                "completed_at": job_data.get("completed_at")
            }
            
        except Exception as e:
            raise Exception(f"Job result retrieval failed: {str(e)}")
    
    async def cleanup_jobs(
        self,
        cutoff_date: datetime,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Clean up old completed jobs"""
        try:
            cleaned_count = 0
            jobs_to_delete = []
            
            for job_id, job_data in self.jobs.items():
                # Check user filter
                if user_id and job_data.get("user_id") != user_id:
                    continue
                
                # Check if job is old and completed
                if job_data["status"] in [JobStatus.COMPLETED.value, JobStatus.FAILED.value, JobStatus.CANCELLED.value]:
                    created_at = datetime.fromisoformat(job_data["created_at"])
                    if created_at < cutoff_date:
                        jobs_to_delete.append(job_id)
            
            # Delete old jobs
            for job_id in jobs_to_delete:
                await self.delete_job(job_id, user_id)
                cleaned_count += 1
            
            return {
                "cleaned_count": cleaned_count,
                "cutoff_date": cutoff_date.isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Job cleanup failed: {str(e)}")
    
    async def get_job_statistics(
        self,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get job statistics"""
        try:
            jobs = list(self.jobs.values())
            
            # Apply user filter
            if user_id:
                jobs = [job for job in jobs if job.get("user_id") == user_id]
            
            # Calculate statistics
            total_jobs = len(jobs)
            status_counts = {}
            type_counts = {}
            
            for job in jobs:
                status = job["status"]
                job_type = job["job_type"]
                
                status_counts[status] = status_counts.get(status, 0) + 1
                type_counts[job_type] = type_counts.get(job_type, 0) + 1
            
            # Calculate success rate
            completed_jobs = status_counts.get(JobStatus.COMPLETED.value, 0)
            failed_jobs = status_counts.get(JobStatus.FAILED.value, 0)
            success_rate = completed_jobs / (completed_jobs + failed_jobs) if (completed_jobs + failed_jobs) > 0 else 0
            
            return {
                "total_jobs": total_jobs,
                "status_counts": status_counts,
                "type_counts": type_counts,
                "success_rate": success_rate,
                "completed_jobs": completed_jobs,
                "failed_jobs": failed_jobs
            }
            
        except Exception as e:
            raise Exception(f"Job statistics retrieval failed: {str(e)}")
    
    # Private helper methods
    
    async def _log_job_event(
        self,
        job_id: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """Log job event"""
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "message": message,
                "data": data or {}
            }
            
            if job_id not in self.job_logs:
                self.job_logs[job_id] = []
            
            self.job_logs[job_id].append(log_entry)
            
        except Exception:
            # Ignore logging errors
            pass
    
    async def _estimate_completion(self, job_data: Dict[str, Any]) -> Optional[str]:
        """Estimate job completion time"""
        try:
            if job_data["status"] != JobStatus.RUNNING.value:
                return None
            
            started_at = job_data.get("started_at")
            if not started_at:
                return None
            
            start_time = datetime.fromisoformat(started_at)
            elapsed = datetime.utcnow() - start_time
            
            progress = job_data.get("progress", 0.0)
            if progress > 0:
                estimated_total = elapsed / progress
                remaining = estimated_total - elapsed
                completion_time = datetime.utcnow() + remaining
                return completion_time.isoformat()
            
            return None
            
        except Exception:
            return None
