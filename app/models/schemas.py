"""
Pydantic Request/Response Schemas
Defines all API request and response models
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
from app.models.enums import CodeType, Framework, OutputFormat, JobStatus, LLMModel


# ============================================
# ENUMS
# ============================================

class CodeType(str, Enum):
    """Code generation types"""
    FRONTEND = "frontend"
    BACKEND = "backend"
    FULLSTACK = "fullstack"
    COMPONENT = "component"
    API = "api"
    DATABASE = "database"


class Framework(str, Enum):
    """Supported frameworks"""
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    NODEJS = "nodejs"
    FASTAPI = "fastapi"
    EXPRESS = "express"
    DJANGO = "django"
    FLASK = "flask"


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


# ============================================
# BASE SCHEMAS
# ============================================

class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: str = "Operation completed successfully"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================
# HEALTH CHECK SCHEMAS
# ============================================

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    services: Dict[str, str] = {}

class HealthResponse(BaseModel):
    """Health response"""
    status: str = Field(..., description="Service status")
    message: str = Field(default="Service is healthy", description="Status message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Current timestamp")


# ============================================
# CODE GENERATION SCHEMAS
# ============================================

class GenerateCodeRequest(BaseModel):
    """Basic code generation request"""
    description: str = Field(..., description="Description of the code to generate")
    code_type: CodeType = Field(..., description="Type of code to generate")
    framework: Framework = Field(..., description="Target framework")
    language: str = Field(default="javascript", description="Programming language")
    features: List[str] = Field(default=[], description="Additional features to include")
    style_preferences: Optional[Dict[str, Any]] = Field(default=None, description="Styling preferences")
    include_tests: bool = Field(default=True, description="Include test files")
    include_documentation: bool = Field(default=True, description="Include documentation")
    
    # Additional fields expected by the code
    prompt: Optional[str] = Field(default=None, description="User prompt for code generation")
    model: LLMModel = Field(default=LLMModel.GEMINI_PRO, description="LLM model to use")
    production_ready: bool = Field(default=True, description="Generate production-ready code")
    styling: str = Field(default="tailwindcss", description="CSS framework for styling")
    
    def __init__(self, **data):
        # If prompt is not provided, use description as prompt
        if 'prompt' not in data or data['prompt'] is None:
            data['prompt'] = data.get('description', '')
        super().__init__(**data)


class FileOutput(BaseModel):
    """File output model"""
    path: str = Field(..., description="File path")
    content: str = Field(..., description="File content")
    language: str = Field(..., description="Programming language")
    size: int = Field(..., description="File size in bytes")
    metadata: Dict[str, Any] = Field(default={}, description="File metadata")


class GenerateCodeResponse(BaseModel):
    """Code generation response"""
    success: bool = True
    files: List[FileOutput] = Field(..., description="Generated code files")
    framework_detected: str = Field(..., description="Detected framework")
    total_files: int = Field(..., description="Total number of files generated")
    total_lines: int = Field(..., description="Total lines of code generated")
    generation_time_seconds: float = Field(..., description="Generation time in seconds")
    model_used: Optional[str] = Field(default=None, description="LLM model used")
    message: str = Field(default="Code generated successfully", description="Response message")
    
    # File saving information
    project_id: Optional[str] = Field(default=None, description="Project ID for saved files")
    download_url: Optional[str] = Field(default=None, description="URL to download project ZIP")
    saved_files_count: Optional[int] = Field(default=None, description="Number of files saved to disk")


class EnhancedGenerateRequest(BaseModel):
    """Enhanced code generation request"""
    description: str = Field(..., description="Description of the application to generate")
    code_type: CodeType = Field(..., description="Type of code to generate")
    frameworks: List[Framework] = Field(..., description="Target frameworks")
    architecture: str = Field(default="monolith", description="Architecture pattern")
    features: List[str] = Field(default=[], description="Additional features")
    database: Optional[str] = Field(default=None, description="Database type")
    authentication: bool = Field(default=True, description="Include authentication")
    testing: bool = Field(default=True, description="Include test files")
    documentation: bool = Field(default=True, description="Include documentation")
    deployment: bool = Field(default=False, description="Include deployment config")
    monitoring: bool = Field(default=False, description="Include monitoring setup")


class EnhancedGenerateResponse(BaseModel):
    """Enhanced code generation response"""
    success: bool = True
    projects: Dict[str, Dict[str, str]] = Field(..., description="Generated projects by framework")
    architecture_diagram: Optional[str] = Field(default=None, description="Architecture diagram")
    deployment_guide: Optional[str] = Field(default=None, description="Deployment instructions")
    metadata: Dict[str, Any] = Field(default={}, description="Generation metadata")
    execution_time: float = Field(..., description="Generation time in seconds")


# ============================================
# FIGMA INTEGRATION SCHEMAS
# ============================================

class FigmaGenerateRequest(BaseModel):
    """Figma-based code generation request"""
    file_id: str = Field(..., description="Figma file ID")
    node_ids: List[str] = Field(..., description="Figma node IDs to process")
    framework: Framework = Field(..., description="Target framework")
    export_format: str = Field(default="png", description="Asset export format")
    include_assets: bool = Field(default=True, description="Include exported assets")
    responsive: bool = Field(default=True, description="Generate responsive code")
    accessibility: bool = Field(default=True, description="Include accessibility features")


class FigmaGenerateResponse(BaseModel):
    """Figma-based code generation response"""
    success: bool = True
    generated_code: Dict[str, str] = Field(..., description="Generated code files")
    assets: Dict[str, str] = Field(default={}, description="Exported assets")
    design_analysis: Dict[str, Any] = Field(default={}, description="Design analysis results")
    metadata: Dict[str, Any] = Field(default={}, description="Generation metadata")


# ============================================
# GITHUB INTEGRATION SCHEMAS
# ============================================

class GitHubDeployRequest(BaseModel):
    """GitHub deployment request"""
    repository: str = Field(..., description="Repository name (owner/repo)")
    branch: str = Field(default="main", description="Target branch")
    files: Dict[str, str] = Field(..., description="Files to deploy (path: content)")
    commit_message: str = Field(..., description="Commit message")
    create_pr: bool = Field(default=False, description="Create pull request")
    pr_title: Optional[str] = Field(default=None, description="Pull request title")
    pr_description: Optional[str] = Field(default=None, description="Pull request description")


class GitHubDeployResponse(BaseModel):
    """GitHub deployment response"""
    success: bool = True
    commit_sha: Optional[str] = Field(default=None, description="Commit SHA")
    pr_url: Optional[str] = Field(default=None, description="Pull request URL")
    repository_url: str = Field(..., description="Repository URL")
    deployment_url: Optional[str] = Field(default=None, description="Deployment URL")


# ============================================
# FILE OPERATION SCHEMAS
# ============================================

class FileUploadResponse(BaseModel):
    """File upload response"""
    success: bool = True
    file_id: str = Field(..., description="Unique file identifier")
    filename: str = Field(..., description="Original filename")
    size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="File MIME type")
    upload_path: str = Field(..., description="File storage path")
    metadata: Dict[str, Any] = Field(default={}, description="File metadata")


class FileListResponse(BaseModel):
    """File list response"""
    success: bool = True
    files: List[Dict[str, Any]] = Field(..., description="List of files")
    total: int = Field(..., description="Total number of files")
    limit: int = Field(..., description="Results limit")
    offset: int = Field(..., description="Results offset")


# ============================================
# JOB MANAGEMENT SCHEMAS
# ============================================

class JobStatusResponse(BaseModel):
    """Job status response"""
    job_id: str = Field(..., description="Job identifier")
    status: JobStatus = Field(..., description="Current job status")
    job_type: JobType = Field(..., description="Type of job")
    progress: float = Field(default=0.0, description="Job progress (0.0-1.0)")
    created_at: datetime = Field(..., description="Job creation time")
    started_at: Optional[datetime] = Field(default=None, description="Job start time")
    completed_at: Optional[datetime] = Field(default=None, description="Job completion time")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Job result data")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default={}, description="Job metadata")


class JobListResponse(BaseModel):
    """Job list response"""
    success: bool = True
    jobs: List[JobStatusResponse] = Field(..., description="List of jobs")
    total: int = Field(..., description="Total number of jobs")
    limit: int = Field(..., description="Results limit")
    offset: int = Field(..., description="Results offset")


# ============================================
# MONITORING SCHEMAS
# ============================================

class MetricsResponse(BaseModel):
    """Metrics response"""
    success: bool = True
    metrics: Dict[str, Any] = Field(..., description="Application metrics")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================
# VALIDATION SCHEMAS
# ============================================

class ValidationRequest(BaseModel):
    """Code validation request"""
    code: str = Field(..., description="Code to validate")
    language: str = Field(..., description="Programming language")
    rules: Optional[Dict[str, Any]] = Field(default=None, description="Validation rules")
    framework: Optional[Framework] = Field(default=None, description="Target framework")


class ValidationResponse(BaseModel):
    """Code validation response"""
    success: bool = True
    is_valid: bool = Field(..., description="Whether code is valid")
    errors: List[str] = Field(default=[], description="Validation errors")
    warnings: List[str] = Field(default=[], description="Validation warnings")
    suggestions: List[str] = Field(default=[], description="Improvement suggestions")
    score: float = Field(default=0.0, description="Code quality score (0.0-1.0)")


# ============================================
# UTILITY SCHEMAS
# ============================================

class PaginationRequest(BaseModel):
    """Pagination request"""
    limit: int = Field(default=50, ge=1, le=1000, description="Number of items per page")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")


class SearchRequest(BaseModel):
    """Search request"""
    query: str = Field(..., description="Search query")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Search filters")
    sort_by: Optional[str] = Field(default=None, description="Sort field")
    sort_order: str = Field(default="asc", description="Sort order (asc/desc)")


# ============================================
# VALIDATORS
# ============================================

class MultiFrameworkRequest(BaseModel):
    """Request for multi-framework generation"""
    description: str = Field(..., description="Description of the application to generate")
    frameworks: List[str] = Field(..., description="List of frameworks to generate for")
    features: List[str] = Field(default=[], description="Additional features to include")
    architecture: str = Field(default="monolith", description="Architecture pattern")
    database: Optional[str] = Field(default=None, description="Database type")
    authentication: bool = Field(default=True, description="Include authentication")
    testing: bool = Field(default=True, description="Include test files")
    documentation: bool = Field(default=True, description="Include documentation")


class BatchGenerateRequest(BaseModel):
    """Request for batch generation"""
    requests: List[GenerateCodeRequest] = Field(..., description="List of generation requests")
    parallel: bool = Field(default=False, description="Process requests in parallel")
    max_concurrent: int = Field(default=3, description="Maximum concurrent requests")


class GenerateCodeRequestValidator:
    """Validator for code generation requests"""
    
    @staticmethod
    def validate_framework_compatibility(code_type: CodeType, framework: Framework) -> bool:
        """Validate framework compatibility with code type"""
        frontend_frameworks = {Framework.REACT, Framework.VUE, Framework.ANGULAR}
        backend_frameworks = {Framework.NODEJS, Framework.FASTAPI, Framework.EXPRESS, Framework.DJANGO, Framework.FLASK}
        
        if code_type == CodeType.FRONTEND and framework not in frontend_frameworks:
            return False
        elif code_type == CodeType.BACKEND and framework not in backend_frameworks:
            return False
        
        return True


# ============================================
# RESPONSE WRAPPERS
# ============================================

class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool = True
    data: Optional[Any] = None
    message: str = "Success"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None


class PaginatedResponse(APIResponse):
    """Paginated API response"""
    pagination: Dict[str, Any] = Field(..., description="Pagination information")