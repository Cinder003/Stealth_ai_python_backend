"""Domain models for business logic"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from .enums import CodeType, Framework, JobStatus


@dataclass
class CodeGenerationJob:
    """Domain model for code generation job"""
    
    job_id: str
    prompt: str
    code_type: CodeType
    framework: Optional[Framework]
    status: JobStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    progress: int = 0
    
    def update_status(self, status: JobStatus, error: Optional[str] = None):
        """Update job status"""
        self.status = status
        self.updated_at = datetime.utcnow()
        if error:
            self.error = error
        if status == JobStatus.COMPLETED or status == JobStatus.FAILED:
            self.completed_at = datetime.utcnow()


@dataclass
class GeneratedFile:
    """Domain model for a generated file"""
    
    path: str
    content: str
    language: Optional[str] = None
    size_bytes: int = 0
    
    def __post_init__(self):
        """Calculate size after initialization"""
        if self.size_bytes == 0:
            self.size_bytes = len(self.content.encode('utf-8'))


@dataclass
class GenerationResult:
    """Domain model for generation result"""
    
    files: List[GeneratedFile]
    framework_detected: Optional[Framework] = None
    model_used: str = ""
    tokens_used: int = 0
    generation_time_seconds: float = 0.0
    total_lines: int = 0
    
    @property
    def total_files(self) -> int:
        """Get total number of files"""
        return len(self.files)
    
    def calculate_total_lines(self) -> int:
        """Calculate total lines across all files"""
        total = 0
        for file in self.files:
            total += len(file.content.splitlines())
        self.total_lines = total
        return total


@dataclass
class LLMRequest:
    """Domain model for LLM request"""
    
    model: str
    prompt: str
    max_tokens: int = 20000  # Pushing to maximum possible limit for Gemini models
    temperature: float = 0.7
    top_p: float = 0.9
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """Domain model for LLM response"""
    
    content: str
    model: str
    tokens_used: int
    finish_reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)

