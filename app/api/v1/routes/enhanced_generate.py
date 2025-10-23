"""
Enhanced Code Generation Routes
Provides advanced code generation capabilities with multiple strategies
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.models.schemas import (
    GenerateCodeRequest,
    GenerateCodeResponse,
    EnhancedGenerateRequest,
    EnhancedGenerateResponse
)
from app.controllers.enhanced_controller import EnhancedGenerationController
from app.core.security import get_current_user
from app.core.config import get_settings

router = APIRouter(prefix="/enhanced", tags=["Enhanced Generation"])
settings = get_settings()

# Initialize controller
enhanced_controller = EnhancedGenerationController()


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
    parallel: bool = Field(default=True, description="Process requests in parallel")
    max_concurrent: int = Field(default=5, description="Maximum concurrent generations")


@router.post("/multi-framework", response_model=Dict[str, Any])
async def generate_multi_framework(
    request: MultiFrameworkRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate code for multiple frameworks simultaneously
    """
    try:
        result = await enhanced_controller.generate_multi_framework(
            request=request,
            background_tasks=background_tasks,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-framework generation failed: {str(e)}")


@router.post("/batch", response_model=List[GenerateCodeResponse])
async def batch_generate(
    request: BatchGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate multiple code projects in batch
    """
    try:
        results = await enhanced_controller.batch_generate(
            request=request,
            background_tasks=background_tasks,
            user_id=current_user.get("id")
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch generation failed: {str(e)}")


@router.post("/iterative", response_model=GenerateCodeResponse)
async def iterative_generate(
    request: EnhancedGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate code with iterative refinement
    """
    try:
        result = await enhanced_controller.iterative_generate(
            request=request,
            background_tasks=background_tasks,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Iterative generation failed: {str(e)}")


@router.post("/template-based", response_model=GenerateCodeResponse)
async def template_based_generate(
    request: EnhancedGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate code using predefined templates
    """
    try:
        result = await enhanced_controller.template_based_generate(
            request=request,
            background_tasks=background_tasks,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Template-based generation failed: {str(e)}")


@router.get("/strategies")
async def get_generation_strategies():
    """
    Get available generation strategies
    """
    return {
        "strategies": [
            {
                "name": "multi_framework",
                "description": "Generate for multiple frameworks simultaneously",
                "features": ["parallel_processing", "framework_comparison"]
            },
            {
                "name": "iterative",
                "description": "Generate with iterative refinement",
                "features": ["feedback_loop", "quality_improvement"]
            },
            {
                "name": "template_based",
                "description": "Generate using predefined templates",
                "features": ["consistency", "best_practices"]
            },
            {
                "name": "batch",
                "description": "Generate multiple projects in batch",
                "features": ["bulk_processing", "resource_optimization"]
            }
        ]
    }


@router.get("/templates")
async def get_available_templates():
    """
    Get available code generation templates
    """
    try:
        templates = await enhanced_controller.get_available_templates()
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")


@router.post("/validate-architecture")
async def validate_architecture(
    architecture: str,
    frameworks: List[str],
    features: List[str]
):
    """
    Validate architecture compatibility with frameworks and features
    """
    try:
        validation_result = await enhanced_controller.validate_architecture(
            architecture=architecture,
            frameworks=frameworks,
            features=features
        )
        return validation_result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Architecture validation failed: {str(e)}")
