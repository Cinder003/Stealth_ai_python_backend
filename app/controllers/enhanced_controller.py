"""
Enhanced Code Generation Controller
Handles advanced code generation with multiple strategies
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import time

from app.models.schemas import (
    EnhancedGenerateRequest, 
    EnhancedGenerateResponse,
    MultiFrameworkRequest,
    BatchGenerateRequest,
    GenerateCodeRequest
)
from app.services.llm_service import LLMService
from app.services.code_extraction_service import CodeExtractionService
from app.services.cache_service import CacheService
from app.services.observability_service import ObservabilityService
from app.helpers.prompt_builder import PromptBuilder
from app.helpers.validation import ValidationHelper
from app.core.config import get_settings

settings = get_settings()


class EnhancedGenerationController:
    """Controller for enhanced code generation"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.code_extraction_service = CodeExtractionService()
        self.cache_service = CacheService()
        self.observability_service = ObservabilityService()
        self.prompt_builder = PromptBuilder()
        self.validation_helper = ValidationHelper()
    
    async def generate_multi_framework(
        self,
        request: MultiFrameworkRequest,
        background_tasks,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate code for multiple frameworks simultaneously
        """
        start_time = time.time()
        
        try:
            # Create tasks for each framework
            tasks = []
            for framework in request.frameworks:
                task = self._generate_for_framework(
                    description=request.description,
                    framework=framework,
                    features=request.features,
                    architecture=request.architecture,
                    database=request.database,
                    authentication=request.authentication,
                    testing=request.testing,
                    documentation=request.documentation
                )
                tasks.append(task)
            
            # Execute all tasks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            framework_results = {}
            for i, result in enumerate(results):
                framework = request.frameworks[i]
                if isinstance(result, Exception):
                    framework_results[framework] = {
                        "success": False,
                        "error": str(result),
                        "code": {}
                    }
                else:
                    framework_results[framework] = result
            
            # Generate architecture diagram if multiple frameworks
            architecture_diagram = None
            if len(request.frameworks) > 1:
                architecture_diagram = await self._generate_architecture_diagram(
                    frameworks=request.frameworks,
                    architecture=request.architecture
                )
            
            # Generate deployment guide
            deployment_guide = await self._generate_deployment_guide(
                frameworks=request.frameworks,
                architecture=request.architecture
            )
            
            return {
                "success": True,
                "projects": framework_results,
                "architecture_diagram": architecture_diagram,
                "deployment_guide": deployment_guide,
                "metadata": {
                    "frameworks": request.frameworks,
                    "architecture": request.architecture,
                    "execution_time": time.time() - start_time,
                    "user_id": user_id
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "projects": {},
                "execution_time": time.time() - start_time
            }
    
    async def batch_generate(
        self,
        request: BatchGenerateRequest,
        background_tasks,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple code projects in batch
        """
        try:
            if request.parallel:
                # Process requests in parallel with concurrency limit
                semaphore = asyncio.Semaphore(request.max_concurrent)
                
                async def process_request(req):
                    async with semaphore:
                        return await self._process_single_request(req, user_id)
                
                tasks = [process_request(req) for req in request.requests]
                results = await asyncio.gather(*tasks, return_exceptions=True)
            else:
                # Process requests sequentially
                results = []
                for req in request.requests:
                    result = await self._process_single_request(req, user_id)
                    results.append(result)
            
            return results
            
        except Exception as e:
            return [{"success": False, "error": str(e)} for _ in request.requests]
    
    async def iterative_generate(
        self,
        request: EnhancedGenerateRequest,
        background_tasks,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate code with iterative refinement
        """
        try:
            # Initial generation
            initial_result = await self._generate_initial_code(request)
            
            # Iterative refinement
            refined_result = await self._refine_code(
                initial_code=initial_result,
                request=request,
                iterations=3
            )
            
            return {
                "success": True,
                "generated_code": refined_result["code"],
                "iterations": refined_result["iterations"],
                "improvements": refined_result["improvements"],
                "metadata": {
                    "original_quality": initial_result["quality_score"],
                    "final_quality": refined_result["quality_score"],
                    "user_id": user_id
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def template_based_generate(
        self,
        request: EnhancedGenerateRequest,
        background_tasks,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate code using predefined templates
        """
        try:
            # Get appropriate template
            template = await self._get_template(
                frameworks=request.frameworks,
                architecture=request.architecture,
                features=request.features
            )
            
            # Generate code using template
            generated_code = await self._generate_from_template(
                template=template,
                request=request
            )
            
            return {
                "success": True,
                "generated_code": generated_code,
                "template_used": template["name"],
                "metadata": {
                    "template_version": template["version"],
                    "user_id": user_id
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get available code generation templates"""
        return [
            {
                "name": "fullstack_react_nodejs",
                "description": "Full-stack React + Node.js application",
                "frameworks": ["react", "nodejs"],
                "architecture": "monolith",
                "features": ["authentication", "api", "database", "frontend"]
            },
            {
                "name": "microservices_fastapi_react",
                "description": "Microservices with FastAPI backend and React frontend",
                "frameworks": ["fastapi", "react"],
                "architecture": "microservices",
                "features": ["api_gateway", "authentication", "database", "frontend"]
            },
            {
                "name": "spa_vue_express",
                "description": "Single Page Application with Vue.js and Express",
                "frameworks": ["vue", "express"],
                "architecture": "spa",
                "features": ["routing", "state_management", "api", "authentication"]
            }
        ]
    
    async def validate_architecture(
        self,
        architecture: str,
        frameworks: List[str],
        features: List[str]
    ) -> Dict[str, Any]:
        """Validate architecture compatibility"""
        try:
            # Define architecture constraints
            constraints = {
                "monolith": {
                    "max_frameworks": 3,
                    "supported_frameworks": ["react", "vue", "nodejs", "fastapi", "express"],
                    "required_features": []
                },
                "microservices": {
                    "max_frameworks": 5,
                    "supported_frameworks": ["react", "vue", "nodejs", "fastapi", "express"],
                    "required_features": ["api_gateway"]
                },
                "spa": {
                    "max_frameworks": 2,
                    "supported_frameworks": ["react", "vue", "angular", "nodejs", "express"],
                    "required_features": ["routing"]
                }
            }
            
            if architecture not in constraints:
                return {
                    "valid": False,
                    "error": f"Unknown architecture: {architecture}",
                    "suggestions": list(constraints.keys())
                }
            
            constraint = constraints[architecture]
            
            # Validate frameworks
            unsupported_frameworks = [
                f for f in frameworks 
                if f not in constraint["supported_frameworks"]
            ]
            
            if unsupported_frameworks:
                return {
                    "valid": False,
                    "error": f"Unsupported frameworks for {architecture}: {unsupported_frameworks}",
                    "supported_frameworks": constraint["supported_frameworks"]
                }
            
            # Validate framework count
            if len(frameworks) > constraint["max_frameworks"]:
                return {
                    "valid": False,
                    "error": f"Too many frameworks for {architecture}. Max: {constraint['max_frameworks']}",
                    "current_count": len(frameworks)
                }
            
            # Validate required features
            missing_features = [
                f for f in constraint["required_features"]
                if f not in features
            ]
            
            if missing_features:
                return {
                    "valid": False,
                    "error": f"Missing required features for {architecture}: {missing_features}",
                    "required_features": constraint["required_features"]
                }
            
            return {
                "valid": True,
                "architecture": architecture,
                "frameworks": frameworks,
                "features": features,
                "constraints": constraint
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    # Private helper methods
    
    async def _generate_for_framework(
        self,
        description: str,
        framework: str,
        features: List[str],
        architecture: str,
        database: Optional[str],
        authentication: bool,
        testing: bool,
        documentation: bool
    ) -> Dict[str, Any]:
        """Generate code for a specific framework"""
        try:
            # Build fullstack prompt for better integration
            prompt = self.prompt_builder.build_fullstack_production_prompt(
                user_prompt=f"Create a {framework} application with the following features: {description}",
                frontend_framework=Framework.REACT if framework in ['react', 'vue', 'angular'] else Framework.REACT,
                backend_framework=Framework.NODEJS if framework in ['nodejs', 'express', 'nestjs'] else Framework.NODEJS,
                production_ready=True,
                include_tests=testing,
                styling="tailwindcss"
            )
            
            # Generate code
            llm_response = await self.llm_service.generate_code(
                prompt=prompt,
                model="gemini-2.0-flash-exp",
                temperature=0.7,
                max_tokens=6000
            )
            
            # Extract code
            extracted_code = await self.code_extraction_service.extract_code_blocks(
                llm_response.content
            )
            
            return {
                "success": True,
                "code": extracted_code,
                "framework": framework,
                "tokens_used": llm_response.usage.get("total_tokens") if llm_response.usage else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "framework": framework
            }
    
    async def _process_single_request(
        self,
        request: GenerateCodeRequest,
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Process a single generation request"""
        try:
            # This would use the basic generation controller
            # For now, return a placeholder
            return {
                "success": True,
                "generated_code": {"main.py": "# Generated code placeholder"},
                "metadata": {"user_id": user_id}
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _generate_architecture_diagram(
        self,
        frameworks: List[str],
        architecture: str
    ) -> str:
        """Generate architecture diagram"""
        # This would generate a Mermaid or similar diagram
        return f"# Architecture Diagram for {architecture} with {', '.join(frameworks)}"
    
    async def _generate_deployment_guide(
        self,
        frameworks: List[str],
        architecture: str
    ) -> str:
        """Generate deployment guide"""
        return f"# Deployment Guide for {architecture} with {', '.join(frameworks)}"
    
    async def _get_template(
        self,
        frameworks: List[str],
        architecture: str,
        features: List[str]
    ) -> Dict[str, Any]:
        """Get appropriate template"""
        # This would select the best template based on requirements
        return {
            "name": "default_template",
            "version": "1.0.0",
            "content": "# Template content"
        }
    
    async def _generate_from_template(
        self,
        template: Dict[str, Any],
        request: EnhancedGenerateRequest
    ) -> Dict[str, str]:
        """Generate code from template"""
        # This would use the template to generate code
        return {"main.py": "# Generated from template"}
