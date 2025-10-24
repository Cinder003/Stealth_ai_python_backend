"""
Figma Integration Controller
Handles Figma design file processing and code generation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import time

from app.models.schemas import FigmaGenerateRequest, FigmaGenerateResponse
from app.services.figma_service import FigmaService
from app.services.figma_processor import FigmaProcessor
from app.services.figma_llm_processor import FigmaLLMProcessor
from app.services.llm_service import LLMService
from app.services.cache_service import CacheService
from app.services.observability_service import ObservabilityService
from app.helpers.prompt_builder import PromptBuilder
from app.core.config import get_settings

settings = get_settings()


class FigmaController:
    """Controller for Figma integration"""
    
    def __init__(self):
        self.figma_service = FigmaService()
        self.figma_processor = FigmaProcessor()
        self.figma_llm_processor = FigmaLLMProcessor()
        self.llm_service = LLMService()
        self.cache_service = CacheService()
        self.observability_service = ObservabilityService()
        self.prompt_builder = PromptBuilder()
    
    async def connect_account(
        self,
        access_token: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Connect to Figma account
        """
        try:
            # Validate token
            user_info = await self.figma_service.validate_token(access_token)
            
            # Store connection
            connection_data = {
                "access_token": access_token,
                "user_id": user_id,
                "figma_user_id": user_info.get("id"),
                "connected_at": datetime.utcnow().isoformat()
            }
            
            await self.cache_service.set(
                f"figma_connection:{user_id}",
                connection_data,
                ttl=86400 * 30  # 30 days
            )
            
            return {
                "success": True,
                "user_info": user_info,
                "connected_at": connection_data["connected_at"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_user_files(
        self,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user's Figma files
        """
        try:
            # Get connection
            connection = await self.cache_service.get(f"figma_connection:{user_id}")
            if not connection:
                raise Exception("Figma account not connected")
            
            # Get files from Figma API
            files = await self.figma_service.get_user_files(
                access_token=connection["access_token"]
            )
            
            return files
            
        except Exception as e:
            raise Exception(f"Failed to get Figma files: {str(e)}")
    
    async def get_file_details(
        self,
        file_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get detailed information about a Figma file
        """
        try:
            # Get connection
            connection = await self.cache_service.get(f"figma_connection:{user_id}")
            if not connection:
                raise Exception("Figma account not connected")
            
            # Get file details
            file_details = await self.figma_service.get_file_details(
                file_id=file_id,
                access_token=connection["access_token"]
            )
            
            return file_details
            
        except Exception as e:
            raise Exception(f"Failed to get file details: {str(e)}")
    
    async def analyze_design(
        self,
        request: Dict[str, Any],
        background_tasks,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze Figma design for code generation
        """
        try:
            # Get connection
            connection = await self.cache_service.get(f"figma_connection:{user_id}")
            if not connection:
                raise Exception("Figma account not connected")
            
            # Get file data
            file_data = await self.figma_service.get_file_data(
                file_id=request["file_id"],
                access_token=connection["access_token"]
            )
            
            # Analyze design
            analysis = await self.figma_service.analyze_design(
                file_data=file_data,
                analysis_type=request.get("analysis_type", "comprehensive"),
                include_components=request.get("include_components", True),
                include_layout=request.get("include_layout", True),
                include_styling=request.get("include_styling", True)
            )
            
            # Store analysis results
            analysis_key = f"figma_analysis:{request['file_id']}:{user_id}"
            await self.cache_service.set(
                analysis_key,
                analysis,
                ttl=3600  # 1 hour
            )
            
            return {
                "success": True,
                "analysis": analysis,
                "file_id": request["file_id"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def generate_code(
        self,
        request: FigmaGenerateRequest,
        background_tasks,
        user_id: Optional[str] = None
    ) -> FigmaGenerateResponse:
        """
        Generate code from Figma design
        """
        start_time = time.time()
        
        try:
            # Get connection
            connection = await self.cache_service.get(f"figma_connection:{user_id}")
            if not connection:
                raise Exception("Figma account not connected")
            
            # Get design analysis
            analysis_key = f"figma_analysis:{request.file_id}:{user_id}"
            analysis = await self.cache_service.get(analysis_key)
            
            if not analysis:
                # Perform analysis if not cached
                analysis = await self.analyze_design(
                    request={"file_id": request.file_id},
                    background_tasks=background_tasks,
                    user_id=user_id
                )
                analysis = analysis.get("analysis", {})
            
            # Export assets if needed
            assets = {}
            if request.include_assets:
                assets = await self.figma_service.export_assets(
                    file_id=request.file_id,
                    node_ids=request.node_ids,
                    format=request.export_format,
                    access_token=connection["access_token"]
                )
            
            # Build generation prompt
            prompt = await self.prompt_builder.build_figma_prompt(
                analysis=analysis,
                framework=request.framework,
                node_ids=request.node_ids,
                responsive=request.responsive,
                accessibility=request.accessibility
            )
            
            # Generate code
            llm_response = await self.llm_service.generate_code(
                prompt=prompt,
                model="gemini-2.0-flash-exp",
                temperature=0.7,
                max_tokens=6000
            )
            
            # Extract code
            from app.services.code_extraction_service import CodeExtractionService
            code_extractor = CodeExtractionService()
            extracted_code = await code_extractor.extract_code_blocks(
                llm_response.content
            )
            
            # Log generation
            await self.observability_service.log_figma_generation(
                request=request,
                analysis=analysis,
                user_id=user_id
            )
            
            return FigmaGenerateResponse(
                success=True,
                generated_code=extracted_code,
                assets=assets,
                design_analysis=analysis,
                metadata={
                    "framework": request.framework,
                    "node_ids": request.node_ids,
                    "execution_time": time.time() - start_time,
                    "user_id": user_id
                }
            )
            
        except Exception as e:
            return FigmaGenerateResponse(
                success=False,
                generated_code={},
                assets={},
                design_analysis={},
                metadata={"error": str(e)}
            )
    
    async def export_assets(
        self,
        request: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export assets from Figma file
        """
        try:
            # Get connection
            connection = await self.cache_service.get(f"figma_connection:{user_id}")
            if not connection:
                raise Exception("Figma account not connected")
            
            # Export assets
            assets = await self.figma_service.export_assets(
                file_id=request["file_id"],
                node_ids=request.get("node_ids", []),
                format=request.get("export_format", "png"),
                scale=request.get("scale", 2.0),
                access_token=connection["access_token"]
            )
            
            return {
                "success": True,
                "assets": assets,
                "count": len(assets)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_components(
        self,
        file_id: str,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get components from Figma file
        """
        try:
            # Get connection
            connection = await self.cache_service.get(f"figma_connection:{user_id}")
            if not connection:
                raise Exception("Figma account not connected")
            
            # Get components
            components = await self.figma_service.get_components(
                file_id=file_id,
                access_token=connection["access_token"]
            )
            
            return components
            
        except Exception as e:
            raise Exception(f"Failed to get components: {str(e)}")
    
    async def preview_generation(
        self,
        file_id: str,
        node_ids: List[str],
        framework: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Preview code generation without full generation
        """
        try:
            # Get connection
            connection = await self.cache_service.get(f"figma_connection:{user_id}")
            if not connection:
                raise Exception("Figma account not connected")
            
            # Get node data
            node_data = await self.figma_service.get_nodes(
                file_id=file_id,
                node_ids=node_ids,
                access_token=connection["access_token"]
            )
            
            # Generate preview
            preview = await self.figma_service.generate_preview(
                node_data=node_data,
                framework=framework
            )
            
            return {
                "success": True,
                "preview": preview,
                "node_count": len(node_ids)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get available Figma code generation templates"""
        return [
            {
                "name": "react_component",
                "description": "React component from Figma design",
                "framework": "react",
                "features": ["props", "styling", "responsive"]
            },
            {
                "name": "vue_component",
                "description": "Vue component from Figma design",
                "framework": "vue",
                "features": ["props", "styling", "responsive"]
            },
            {
                "name": "html_css",
                "description": "HTML/CSS from Figma design",
                "framework": "html",
                "features": ["semantic_html", "css_grid", "flexbox"]
            }
        ]
    
    async def handle_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Figma webhook events"""
        try:
            event_type = webhook_data.get("event_type")
            
            if event_type == "file_update":
                # Handle file update
                file_id = webhook_data.get("file_id")
                await self._handle_file_update(file_id)
            elif event_type == "comment_added":
                # Handle comment
                comment_data = webhook_data.get("comment")
                await self._handle_comment(comment_data)
            
            return {"success": True, "event_processed": event_type}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_file_update(self, file_id: str):
        """Handle file update webhook"""
        # Invalidate cached analysis
        await self.cache_service.delete_pattern(f"figma_analysis:{file_id}:*")
    
    async def _handle_comment(self, comment_data: Dict[str, Any]):
        """Handle comment webhook"""
        # Process comment for potential code generation triggers
        pass
    
    async def process_figma_url(
        self,
        figma_url: str,
        user_message: Optional[str] = None,
        framework: str = "react",
        backend_framework: str = "nodejs",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process Figma URL through complete pipeline
        """
        try:
            # Get connection - try user-specific first, then fallback to global
            connection = await self.cache_service.get(f"figma_connection:{user_id}")
            if not connection:
                # Fallback to global access token from environment
                print(f"DEBUG: FIGMA_ACCESS_TOKEN from settings: {settings.FIGMA_ACCESS_TOKEN}")
                if settings.FIGMA_ACCESS_TOKEN:
                    connection = {"access_token": settings.FIGMA_ACCESS_TOKEN}
                    print(f"DEBUG: Using global access token: {settings.FIGMA_ACCESS_TOKEN[:10]}...")
                else:
                    print("DEBUG: No global access token found")
                    raise Exception("Figma account not connected and no global access token configured")
            
            # Process Figma URL through new pipeline
            processing_result = await self.figma_processor.process_figma_url(
                figma_url=figma_url,
                access_token=connection["access_token"],
                include_images=True,
                chunk_size=1000
            )
            
            # Process chunks through LLM
            llm_result = await self.figma_llm_processor.process_figma_to_code(
                figma_chunks=processing_result["chunks"],
                user_message=user_message,
                framework=framework,
                backend_framework=backend_framework
            )
            
            return {
                "success": True,
                "file_key": processing_result["file_key"],
                "file_name": processing_result["file_name"],
                "frontend_code": llm_result.get("frontend_code", {}),
                "backend_code": llm_result.get("backend_code", {}),
                "components": llm_result.get("components", []),
                "statistics": llm_result.get("statistics", {}),
                "chunk_results": llm_result.get("chunk_results", [])
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def extract_file_key_from_url(self, figma_url: str) -> Dict[str, Any]:
        """
        Extract file key from Figma URL
        """
        try:
            file_key = self.figma_processor.extract_file_key(figma_url)
            
            if file_key:
                return {
                    "success": True,
                    "file_key": file_key,
                    "url": figma_url
                }
            else:
                return {
                    "success": False,
                    "error": "Could not extract file key from URL",
                    "url": figma_url
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def validate_figma_json(
        self,
        file_key: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate Figma JSON structure and size
        """
        try:
            # Get connection - try user-specific first, then fallback to global
            connection = await self.cache_service.get(f"figma_connection:{user_id}")
            if not connection:
                # Fallback to global access token from environment
                if settings.FIGMA_ACCESS_TOKEN:
                    connection = {"access_token": settings.FIGMA_ACCESS_TOKEN}
                else:
                    raise Exception("Figma account not connected and no global access token configured")
            
            # Get Figma JSON
            figma_json = await self.figma_processor.get_figma_json(
                file_key=file_key,
                access_token=connection["access_token"]
            )
            
            # Validate JSON
            is_valid, errors = self.figma_processor.validate_figma_json(figma_json)
            
            return {
                "success": is_valid,
                "errors": errors,
                "file_name": figma_json.get("name", ""),
                "node_count": self.figma_processor._count_nodes(figma_json)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_image_references(
        self,
        file_key: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract image references from Figma file
        """
        try:
            # Get connection - try user-specific first, then fallback to global
            connection = await self.cache_service.get(f"figma_connection:{user_id}")
            if not connection:
                # Fallback to global access token from environment
                if settings.FIGMA_ACCESS_TOKEN:
                    connection = {"access_token": settings.FIGMA_ACCESS_TOKEN}
                else:
                    raise Exception("Figma account not connected and no global access token configured")
            
            # Get Figma JSON
            figma_json = await self.figma_processor.get_figma_json(
                file_key=file_key,
                access_token=connection["access_token"]
            )
            
            # Extract image references
            image_refs = self.figma_processor.extract_image_references(figma_json)
            
            # Get actual image URLs
            if image_refs:
                node_ids = [ref.node_id for ref in image_refs]
                image_urls = await self.figma_processor.get_figma_image_urls(
                    file_key=file_key,
                    node_ids=node_ids,
                    access_token=connection["access_token"]
                )
                
                # Update references with URLs
                for ref in image_refs:
                    if ref.node_id in image_urls:
                        ref.image_url = image_urls[ref.node_id]
            
            return {
                "success": True,
                "image_references": [
                    {
                        "node_id": ref.node_id,
                        "image_ref": ref.image_ref,
                        "image_url": ref.image_url,
                        "format": ref.format,
                        "scale": ref.scale
                    }
                    for ref in image_refs
                ],
                "count": len(image_refs)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
