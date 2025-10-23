"""
Figma Integration Routes
Handles Figma design file processing and code generation
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, File
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.models.schemas import FigmaGenerateRequest, FigmaGenerateResponse
from app.controllers.figma_controller import FigmaController
from app.core.security import get_current_user
from app.core.config import get_settings

router = APIRouter(prefix="/figma", tags=["Figma Integration"])
settings = get_settings()

# Initialize controller
figma_controller = FigmaController()


class FigmaFileRequest(BaseModel):
    """Request for processing Figma file"""
    file_id: str = Field(..., description="Figma file ID")
    node_ids: Optional[List[str]] = Field(default=None, description="Specific node IDs to process")
    export_format: str = Field(default="png", description="Export format (png, svg, pdf)")
    scale: float = Field(default=2.0, description="Export scale factor")
    include_metadata: bool = Field(default=True, description="Include design metadata")


class FigmaDesignAnalysis(BaseModel):
    """Request for design analysis"""
    file_id: str = Field(..., description="Figma file ID")
    analysis_type: str = Field(default="comprehensive", description="Type of analysis")
    include_components: bool = Field(default=True, description="Include component analysis")
    include_layout: bool = Field(default=True, description="Include layout analysis")
    include_styling: bool = Field(default=True, description="Include styling analysis")


@router.post("/connect")
async def connect_figma(
    access_token: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Connect to Figma account
    """
    try:
        result = await figma_controller.connect_account(
            access_token=access_token,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Figma connection failed: {str(e)}")


@router.get("/files")
async def get_figma_files(
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's Figma files
    """
    try:
        files = await figma_controller.get_user_files(
            user_id=current_user.get("id")
        )
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Figma files: {str(e)}")


@router.get("/files/{file_id}")
async def get_figma_file_details(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed information about a Figma file
    """
    try:
        file_details = await figma_controller.get_file_details(
            file_id=file_id,
            user_id=current_user.get("id")
        )
        return file_details
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Figma file not found: {str(e)}")


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_figma_design(
    request: FigmaDesignAnalysis,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze Figma design for code generation
    """
    try:
        analysis = await figma_controller.analyze_design(
            request=request,
            background_tasks=background_tasks,
            user_id=current_user.get("id")
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Design analysis failed: {str(e)}")


@router.post("/generate", response_model=FigmaGenerateResponse)
async def generate_from_figma(
    request: FigmaGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate code from Figma design
    """
    try:
        result = await figma_controller.generate_code(
            request=request,
            background_tasks=background_tasks,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code generation failed: {str(e)}")


@router.post("/process-url")
async def process_figma_url(
    figma_url: str,
    user_message: Optional[str] = None,
    framework: str = "react",
    backend_framework: str = "nodejs",
    current_user: dict = Depends(get_current_user)
):
    """
    Process Figma URL through complete pipeline
    """
    try:
        result = await figma_controller.process_figma_url(
            figma_url=figma_url,
            user_message=user_message,
            framework=framework,
            backend_framework=backend_framework,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Figma URL processing failed: {str(e)}")


@router.post("/extract-file-key")
async def extract_file_key(
    figma_url: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Extract file key from Figma URL
    """
    try:
        result = await figma_controller.extract_file_key_from_url(figma_url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File key extraction failed: {str(e)}")


@router.post("/validate-json")
async def validate_figma_json(
    file_key: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Validate Figma JSON structure and size
    """
    try:
        result = await figma_controller.validate_figma_json(
            file_key=file_key,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JSON validation failed: {str(e)}")


@router.post("/image-references")
async def get_image_references(
    file_key: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Extract image references from Figma file
    """
    try:
        result = await figma_controller.get_image_references(
            file_key=file_key,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image reference extraction failed: {str(e)}")


@router.post("/export")
async def export_figma_assets(
    request: FigmaFileRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Export assets from Figma file
    """
    try:
        assets = await figma_controller.export_assets(
            request=request,
            user_id=current_user.get("id")
        )
        return assets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Asset export failed: {str(e)}")


@router.get("/components/{file_id}")
async def get_figma_components(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get components from Figma file
    """
    try:
        components = await figma_controller.get_components(
            file_id=file_id,
            user_id=current_user.get("id")
        )
        return {"components": components}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get components: {str(e)}")


@router.post("/preview")
async def preview_generation(
    file_id: str,
    node_ids: List[str],
    framework: str = "react",
    current_user: dict = Depends(get_current_user)
):
    """
    Preview code generation without full generation
    """
    try:
        preview = await figma_controller.preview_generation(
            file_id=file_id,
            node_ids=node_ids,
            framework=framework,
            user_id=current_user.get("id")
        )
        return preview
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview generation failed: {str(e)}")


@router.get("/templates")
async def get_figma_templates():
    """
    Get available Figma code generation templates
    """
    try:
        templates = await figma_controller.get_available_templates()
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")


@router.post("/webhook")
async def figma_webhook(
    webhook_data: Dict[str, Any]
):
    """
    Handle Figma webhook events
    """
    try:
        result = await figma_controller.handle_webhook(webhook_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook processing failed: {str(e)}")
