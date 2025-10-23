"""
Basic Code Generation Controller
Handles standard code generation requests
"""

from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import time

from app.models.schemas import GenerateCodeRequest, GenerateCodeResponse
from app.services.llm_service import LLMService
from app.services.code_extraction_service import CodeExtractionService
from app.services.cache_service import CacheService
from app.services.observability_service import ObservabilityService
from app.helpers.prompt_builder import PromptBuilder
from app.helpers.validation import ValidationHelper
from app.core.config import get_settings

settings = get_settings()


class GenerateController:
    """Controller for basic code generation"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.code_extraction_service = CodeExtractionService()
        self.cache_service = CacheService()
        self.observability_service = ObservabilityService()
        self.prompt_builder = PromptBuilder()
        self.validation_helper = ValidationHelper()
    
    async def generate_code(
        self,
        request: GenerateCodeRequest,
        user_id: Optional[str] = None
    ) -> GenerateCodeResponse:
        """
        Generate code based on request
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(request)
            cached_result = await self.cache_service.get(cache_key)
            if cached_result:
                return GenerateCodeResponse(**cached_result)
            
            # Build prompt
            prompt = await self.prompt_builder.build_generation_prompt(
                description=request.description,
                code_type=request.code_type,
                framework=request.framework,
                language=request.language,
                features=request.features,
                style_preferences=request.style_preferences,
                include_tests=request.include_tests,
                include_documentation=request.include_documentation
            )
            
            # Generate code using LLM
            llm_response = await self.llm_service.generate_code(
                prompt=prompt,
                model="gemini-2.0-flash-exp",
                temperature=0.7,
                max_tokens=4000
            )
            
            # Extract code from response
            extracted_code = await self.code_extraction_service.extract_code_blocks(
                llm_response.content
            )
            
            # Validate generated code
            validation_result = await self.validation_helper.validate_code(
                code=extracted_code,
                framework=request.framework,
                language=request.language
            )
            
            # Prepare response
            response = GenerateCodeResponse(
                success=True,
                generated_code=extracted_code,
                metadata={
                    "framework": request.framework,
                    "language": request.language,
                    "features": request.features,
                    "validation": validation_result,
                    "user_id": user_id
                },
                execution_time=time.time() - start_time,
                tokens_used=llm_response.usage.get("total_tokens") if llm_response.usage else None,
                model_used=llm_response.model
            )
            
            # Cache the result
            await self.cache_service.set(
                cache_key,
                response.dict(),
                ttl=settings.CACHE_TTL
            )
            
            # Log to observability
            await self.observability_service.log_generation(
                request=request,
                response=response,
                user_id=user_id
            )
            
            return response
            
        except Exception as e:
            # Log error
            await self.observability_service.log_error(
                error=str(e),
                context={"request": request.dict(), "user_id": user_id}
            )
            
            return GenerateCodeResponse(
                success=False,
                generated_code={},
                metadata={"error": str(e)},
                execution_time=time.time() - start_time
            )
    
    def _generate_cache_key(self, request: GenerateCodeRequest) -> str:
        """Generate cache key for request"""
        import hashlib
        
        key_data = {
            "description": request.description,
            "code_type": request.code_type,
            "framework": request.framework,
            "language": request.language,
            "features": sorted(request.features),
            "include_tests": request.include_tests,
            "include_documentation": request.include_documentation
        }
        
        key_string = str(key_data)
        return f"codegen:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    async def get_generation_history(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get user's generation history"""
        try:
            history = await self.cache_service.get_user_history(
                user_id=user_id,
                limit=limit,
                offset=offset
            )
            return {"success": True, "history": history}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_supported_frameworks(self) -> Dict[str, Any]:
        """Get supported frameworks and their capabilities"""
        return {
            "frontend": {
                "react": {
                    "languages": ["javascript", "typescript"],
                    "features": ["components", "hooks", "routing", "state_management"],
                    "templates": ["component", "page", "layout"]
                },
                "vue": {
                    "languages": ["javascript", "typescript"],
                    "features": ["components", "composition_api", "routing", "state_management"],
                    "templates": ["component", "page", "layout"]
                },
                "angular": {
                    "languages": ["typescript"],
                    "features": ["components", "services", "routing", "forms"],
                    "templates": ["component", "service", "module"]
                }
            },
            "backend": {
                "nodejs": {
                    "languages": ["javascript", "typescript"],
                    "features": ["api", "middleware", "authentication", "database"],
                    "templates": ["api", "service", "controller"]
                },
                "fastapi": {
                    "languages": ["python"],
                    "features": ["api", "middleware", "authentication", "database"],
                    "templates": ["endpoint", "service", "model"]
                },
                "express": {
                    "languages": ["javascript", "typescript"],
                    "features": ["api", "middleware", "authentication", "database"],
                    "templates": ["route", "middleware", "controller"]
                }
            }
        }
