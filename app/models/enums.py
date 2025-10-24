"""Application enumerations"""

from enum import Enum


class CodeType(str, Enum):
    """Type of code to generate"""
    FRONTEND = "frontend"
    BACKEND = "backend"
    FULLSTACK = "fullstack"
    COMPONENT = "component"
    API = "api"
    UTILITY = "utility"


class Framework(str, Enum):
    """Supported frameworks"""
    # Frontend
    REACT = "react"
    REACT_TYPESCRIPT = "react-typescript"
    VUE = "vue"
    ANGULAR = "angular"
    SVELTE = "svelte"
    NEXT = "nextjs"
    
    # Backend
    NODEJS = "nodejs"
    EXPRESS = "express"
    FASTAPI = "fastapi"
    FLASK = "flask"
    DJANGO = "django"
    NEST = "nestjs"


class OutputFormat(str, Enum):
    """Output format options"""
    JSON = "json"
    ZIP = "zip"
    TAR = "tar"
    FILES = "files"


class JobStatus(str, Enum):
    """Background job status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LLMModel(str, Enum):
    """Supported LLM models"""
    GEMINI_PRO = "gemini-2.5-pro"
    GEMINI_PRO_VISION = "gemini-2.5-pro"
    GEMINI_15_PRO = "gemini-2.5-pro"
    GEMINI_15_FLASH = "gemini-2.5-flash"
    GEMINI_20_FLASH = "gemini-2.5-flash"


class PromptType(str, Enum):
    """Prompt template types"""
    BASIC_FRONTEND = "basic_frontend"
    PRODUCTION_FRONTEND = "production_frontend"
    BASIC_BACKEND = "basic_backend"
    PRODUCTION_BACKEND = "production_backend"
    FULLSTACK = "fullstack"
    COMPONENT = "component"
    API_ENDPOINT = "api_endpoint"

