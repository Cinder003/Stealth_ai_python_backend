"""Code generation endpoints"""

import time
import logging
from fastapi import APIRouter, Depends, status
from app.models.schemas import GenerateCodeRequest, GenerateCodeResponse, FileOutput
from app.models.enums import Framework, CodeType
from app.services.llm_service import get_llm_service, LLMService
from app.services.code_extraction_service import get_code_extraction_service, CodeExtractionService
from app.services.cache_service import get_cache_service, CacheService
from app.services.file_service import FileService
from app.helpers.prompt_builder import PromptBuilder
from app.helpers.validation import validate_code_request
from app.helpers.rate_limiter import get_rate_limiter
from app.core.security import validate_api_key

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/generate_code",
    response_model=GenerateCodeResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate code",
    description="Generate frontend or backend code based on natural language description"
)
async def generate_code(
    request: GenerateCodeRequest,
    api_key: str = Depends(validate_api_key)
):
    """
    Generate code based on user prompt
    
    This endpoint generates production-ready code using Gemini LLM.
    Supports React, Vue, Angular for frontend and Node.js, Express, FastAPI for backend.
    """
    start_time = time.time()
    
    try:
        # Validate request
        validate_code_request(request)
        
        # Check rate limit
        rate_limiter = get_rate_limiter()
        rate_limiter.check_rate_limit(api_key)
        
        logger.info(
            f"Code generation request: type={request.code_type}, framework={request.framework}, "
            f"production={request.production_ready}"
        )
        
        # Check cache first
        cache_service = await get_cache_service()
        cached_result = await cache_service.get_cached_generation(
            prompt=request.prompt,
            model=request.model.value,
            code_type=request.code_type.value,
            framework=request.framework.value if request.framework else None,
            production_ready=request.production_ready
        )
        
        if cached_result:
            logger.info("Cache hit! Returning cached result")
            cached_result["generation_time_seconds"] = time.time() - start_time
            return GenerateCodeResponse(**cached_result)
        
        # Determine framework if not provided
        framework = request.framework
        if not framework:
            framework = _auto_detect_framework(request.code_type, request.prompt)
            logger.info(f"Auto-detected framework: {framework}")
        
        # Build prompt
        prompt_builder = PromptBuilder()
        complete_prompt = prompt_builder.build_prompt(
            user_prompt=request.prompt,
            code_type=request.code_type,
            framework=framework,
            production_ready=request.production_ready,
            include_tests=request.include_tests,
            styling=request.styling
        )
        
        logger.debug(f"Generated prompt (length: {len(complete_prompt)})")
        
        # Generate code using LLM
        llm_service = get_llm_service()
        llm_response = await llm_service.generate_code(
            prompt=complete_prompt,
            model=request.model.value,
            max_tokens=8000,
            temperature=0.7 if not request.production_ready else 0.5
        )
        
        logger.info(f"LLM response received (length: {len(llm_response)})")
        
        # Log the raw LLM response for debugging
        logger.info("=" * 80)
        logger.info("RAW GEMINI OUTPUT:")
        logger.info("=" * 80)
        logger.info(llm_response)
        logger.info("=" * 80)
        
        # Extract code files from response
        extraction_service = get_code_extraction_service()
        generated_files = extraction_service.extract_files_from_response(llm_response)
        
        if not generated_files:
            logger.warning("No files were extracted from LLM response")
            # Try alternative parsing
            generated_files = extraction_service.parse_structured_response(llm_response)
        
        logger.info(f"Extracted {len(generated_files)} files")
        
        # Save files to disk using the new file saving system
        try:
            from app.services.llm_result_handler import handle_and_save
            save_result = handle_and_save(llm_response, create_zip=True)
            logger.info(f"Files saved to project: {save_result['project_id']}")
            logger.info(f"Download URL: {save_result['download_url']}")
        except Exception as save_error:
            logger.warning(f"File saving failed: {save_error}")
            # Continue without failing the request
            save_result = {"project_id": None, "download_url": None, "saved_files_count": 0}
        
        # Convert to response format
        file_outputs = [
            FileOutput(
                path=f.path,
                content=f.content,
                language=f.language,
                size=f.size_bytes
            )
            for f in generated_files
        ]
        
        # Calculate metrics
        total_lines = sum(len(f.content.splitlines()) for f in generated_files)
        generation_time = time.time() - start_time
        
        # Build response
        response = GenerateCodeResponse(
            success=True,
            files=file_outputs,
            framework_detected=framework,
            total_files=len(file_outputs),
            total_lines=total_lines,
            generation_time_seconds=round(generation_time, 2),
            model_used=request.model.value,
            message="Code generated successfully"
        )
        
        # Add file saving information to response
        if save_result.get("project_id"):
            response.project_id = save_result["project_id"]
            response.download_url = save_result["download_url"]
            response.saved_files_count = save_result["saved_files_count"]
        
        # Cache the result
        await cache_service.cache_generation(
            prompt=request.prompt,
            model=request.model.value,
            result=response.model_dump(),
            code_type=request.code_type.value,
            framework=framework.value if framework else None,
            production_ready=request.production_ready
        )
        
        logger.info(
            f"Code generation completed successfully in {generation_time:.2f}s. "
            f"Files: {len(file_outputs)}, Lines: {total_lines}"
        )
        
        return response
        
    except Exception as e:
        logger.exception(f"Error generating code: {e}")
        raise


def _auto_detect_framework(code_type: CodeType, prompt: str) -> Framework:
    """Auto-detect framework from prompt"""
    prompt_lower = prompt.lower()
    
    if code_type == CodeType.FRONTEND:
        if "react" in prompt_lower or "jsx" in prompt_lower:
            if "typescript" in prompt_lower or "tsx" in prompt_lower:
                return Framework.REACT_TYPESCRIPT
            return Framework.REACT
        elif "vue" in prompt_lower:
            return Framework.VUE
        elif "angular" in prompt_lower:
            return Framework.ANGULAR
        elif "next" in prompt_lower or "nextjs" in prompt_lower:
            return Framework.NEXT
        else:
            # Default to React
            return Framework.REACT
    
    elif code_type == CodeType.BACKEND:
        if "express" in prompt_lower:
            return Framework.EXPRESS
        elif "fastapi" in prompt_lower or "python" in prompt_lower:
            return Framework.FASTAPI
        elif "nest" in prompt_lower or "nestjs" in prompt_lower:
            return Framework.NEST
        elif "node" in prompt_lower or "nodejs" in prompt_lower:
            return Framework.NODEJS
        else:
            # Default to Node.js
            return Framework.NODEJS
    
    # Default fallback
    return Framework.REACT if code_type == CodeType.FRONTEND else Framework.NODEJS

