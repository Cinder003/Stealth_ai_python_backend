"""
Async Job Management Routes
Handles background job status, monitoring, and management
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from app.models.schemas import JobStatusResponse, JobListResponse
from app.controllers.job_controller import JobController
from app.core.security import get_current_user
from app.core.config import get_settings

router = APIRouter(prefix="/jobs", tags=["Job Management"])
settings = get_settings()

# Initialize controller
job_controller = JobController()


class JobStatus(str, Enum):
    """Job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobFilterRequest(BaseModel):
    """Request for filtering jobs"""
    status: Optional[JobStatus] = Field(default=None, description="Filter by job status")
    job_type: Optional[str] = Field(default=None, description="Filter by job type")
    project_id: Optional[str] = Field(default=None, description="Filter by project ID")
    user_id: Optional[str] = Field(default=None, description="Filter by user ID")
    created_after: Optional[str] = Field(default=None, description="Filter jobs created after date")
    created_before: Optional[str] = Field(default=None, description="Filter jobs created before date")


class JobRetryRequest(BaseModel):
    """Request for retrying a job"""
    job_id: str = Field(..., description="Job ID to retry")
    reset_status: bool = Field(default=True, description="Reset job status before retry")
    max_retries: int = Field(default=3, description="Maximum retry attempts")


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    limit: int = 50,
    offset: int = 0,
    filters: Optional[JobFilterRequest] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    List jobs with optional filtering
    """
    try:
        result = await job_controller.list_jobs(
            limit=limit,
            offset=offset,
            filters=filters,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get job status and details
    """
    try:
        result = await job_controller.get_job_status(
            job_id=job_id,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job not found: {str(e)}")


@router.post("/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Cancel a running job
    """
    try:
        result = await job_controller.cancel_job(
            job_id=job_id,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job cancellation failed: {str(e)}")


@router.post("/{job_id}/retry")
async def retry_job(
    job_id: str,
    request: Optional[JobRetryRequest] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Retry a failed job
    """
    try:
        result = await job_controller.retry_job(
            job_id=job_id,
            request=request,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job retry failed: {str(e)}")


@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a job and its associated data
    """
    try:
        result = await job_controller.delete_job(
            job_id=job_id,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job deletion failed: {str(e)}")


@router.get("/{job_id}/logs")
async def get_job_logs(
    job_id: str,
    limit: int = 100,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """
    Get job execution logs
    """
    try:
        logs = await job_controller.get_job_logs(
            job_id=job_id,
            limit=limit,
            offset=offset,
            user_id=current_user.get("id")
        )
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job logs not found: {str(e)}")


@router.get("/{job_id}/progress")
async def get_job_progress(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get job progress information
    """
    try:
        progress = await job_controller.get_job_progress(
            job_id=job_id,
            user_id=current_user.get("id")
        )
        return progress
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job progress not found: {str(e)}")


@router.get("/{job_id}/result")
async def get_job_result(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get job result data
    """
    try:
        result = await job_controller.get_job_result(
            job_id=job_id,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job result not found: {str(e)}")


@router.post("/cleanup")
async def cleanup_completed_jobs(
    older_than_days: int = 7,
    current_user: dict = Depends(get_current_user)
):
    """
    Clean up old completed jobs
    """
    try:
        result = await job_controller.cleanup_jobs(
            older_than_days=older_than_days,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job cleanup failed: {str(e)}")


@router.get("/stats")
async def get_job_statistics(
    current_user: dict = Depends(get_current_user)
):
    """
    Get job statistics
    """
    try:
        stats = await job_controller.get_job_statistics(
            user_id=current_user.get("id")
        )
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job statistics: {str(e)}")


@router.get("/types")
async def get_job_types():
    """
    Get available job types
    """
    try:
        types = await job_controller.get_available_job_types()
        return {"job_types": types}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job types: {str(e)}")
