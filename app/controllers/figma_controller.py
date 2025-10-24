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
from app.services.figma_streaming_processor import FigmaStreamingProcessor
from app.services.figma_fast_processor import FigmaFastProcessor
from app.services.figma_lossless_processor import FigmaLosslessProcessor
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
        self.figma_streaming_processor = FigmaStreamingProcessor()
        self.figma_fast_processor = FigmaFastProcessor()
        self.figma_lossless_processor = FigmaLosslessProcessor()
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
    
    async def _generate_code_screen_by_screen(
        self,
        request: FigmaGenerateRequest,
        analysis: Dict[str, Any],
        connection: Dict[str, Any],
        background_tasks,
        user_id: Optional[str] = None
    ) -> FigmaGenerateResponse:
        """Generate code for large Figma files using screen-by-screen processing"""
        start_time = time.time()
        
        try:
            screens = analysis.get("screens", {})
            shared_components = analysis.get("shared_components", [])
            navigation = analysis.get("navigation", {})
            
            # Process each screen through LLM
            processed_screens = {}
            total_tokens = 0
            
            for screen_name, screen_data in screens.items():
                if not screen_data.get("success", False):
                    continue
                
                # Process screen chunks through LLM
                from app.services.figma_llm_processor import FigmaLLMProcessor
                llm_processor = FigmaLLMProcessor()
                
                screen_chunks = screen_data.get("chunks", [])
                if screen_chunks:
                    chunk_results = await llm_processor.process_chunks(
                        chunks=screen_chunks,
                        framework=request.framework,
                        backend_framework=request.backend_framework,
                        user_message=request.user_message
                    )
                    
                    # Merge results for this screen
                    merged_result = await llm_processor.merge_code_results(
                        chunk_results=chunk_results,
                        framework=request.framework,
                        backend_framework=request.backend_framework
                    )
                    
                    processed_screens[screen_name] = {
                        "success": True,
                        "frontend_code": merged_result.frontend_code,
                        "backend_code": merged_result.backend_code,
                        "components": merged_result.components,
                        "tokens_used": merged_result.total_tokens,
                        "processing_time": merged_result.processing_time
                    }
                    
                    total_tokens += merged_result.total_tokens
            
            # Generate shared component library
            shared_component_code = {}
            if shared_components:
                shared_component_code = await self._generate_shared_components(
                    shared_components, request.framework
                )
            
            # Generate navigation/routing code
            navigation_code = await self._generate_navigation_code(
                navigation, request.framework
            )
            
            # Combine all generated code
            combined_code = {
                **processed_screens,
                "shared_components": shared_component_code,
                "navigation": navigation_code,
                "app_structure": {
                    "type": "multi_screen_app",
                    "framework": request.framework,
                    "routing": navigation.get("navigation", {}),
                    "total_screens": len(processed_screens),
                    "shared_components_count": len(shared_components)
                }
            }
            
            return FigmaGenerateResponse(
                success=True,
                generated_code=combined_code,
                assets={},  # Assets handled per screen
                design_analysis=analysis,
                metadata={
                    "processing_mode": "screen_by_screen",
                    "framework": request.framework,
                    "total_screens": len(processed_screens),
                    "total_tokens": total_tokens,
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
    
    async def _generate_shared_components(
        self,
        shared_components: List[Dict[str, Any]],
        framework: str
    ) -> Dict[str, str]:
        """Generate shared component library"""
        # This would generate a component library from shared components
        # For now, return a placeholder
        return {
            "components/index.ts": "// Shared component library",
            "components/Button.tsx": "// Button component",
            "components/Input.tsx": "// Input component"
        }
    
    async def _generate_navigation_code(
        self,
        navigation: Dict[str, Any],
        framework: str
    ) -> Dict[str, str]:
        """Generate navigation/routing code"""
        # This would generate routing code based on the navigation structure
        # For now, return a placeholder
        return {
            "App.tsx": "// Main app with routing",
            "routes/index.ts": "// Route definitions",
            "components/Navigation.tsx": "// Navigation component"
        }
    
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
            
            # Check if this is a large file that needs screen-by-screen processing
            if analysis.get("processing_mode") == "screen_by_screen":
                return await self._generate_code_screen_by_screen(
                    request, analysis, connection, background_tasks, user_id
                )
            
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
                model="gemini-2.5-pro",
                temperature=0.7,
                max_tokens=12000  # Increased for complete Figma processing
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
    
    async def process_figma_url_streaming(
        self,
        figma_url: str,
        user_message: Optional[str] = None,
        framework: str = "react",
        backend_framework: str = "nodejs",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process Figma URL using streaming approach to avoid token explosion
        """
        try:
            # Get connection
            connection = await self.cache_service.get(f"figma_connection:{user_id}")
            if not connection:
                if settings.FIGMA_ACCESS_TOKEN:
                    connection = {"access_token": settings.FIGMA_ACCESS_TOKEN}
                else:
                    raise Exception("Figma account not connected and no global access token configured")
            
            # Get Figma JSON
            file_key = self.figma_processor.extract_file_key(figma_url)
            if not file_key:
                raise Exception("Could not extract file key from URL")
            
            figma_json = await self.figma_processor.get_figma_json(
                file_key=file_key,
                access_token=connection["access_token"]
            )
            
            # Process using streaming approach
            result = await self.figma_streaming_processor.process_figma_to_fullstack(
                figma_json=figma_json,
                user_message=user_message,
                framework=framework,
                backend_framework=backend_framework
            )
            
            if result.success:
                # Save generated code to files
                saved_files = await self._save_streaming_generated_code(
                    result.frontend_code,
                    result.backend_code,
                    result.component_registry,
                    result.design_tokens
                )
                
                return {
                    "success": True,
                    "file_key": file_key,
                    "processing_mode": "streaming",
                    "frontend_code": result.frontend_code,
                    "backend_code": result.backend_code,
                    "component_registry": result.component_registry,
                    "design_tokens": result.design_tokens,
                    "statistics": result.statistics,
                    "saved_files": saved_files
                }
            else:
                return {
                    "success": False,
                    "error": "; ".join(result.errors)
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def process_figma_url_fast(
        self,
        figma_url: str,
        user_message: Optional[str] = None,
        framework: str = "react",
        backend_framework: str = "nodejs",
        user_id: Optional[str] = None,
        max_batch_size: int = 10,
        max_concurrent_batches: int = 5
    ) -> Dict[str, Any]:
        """
        Process Figma URL using ULTRA-FAST approach
        - Batch size: 10 components (vs 3)
        - Parallel batches: 5 concurrent (vs 1)
        - Reduced delays: 0.5s (vs 2s)
        - Optimized prompts: shorter, focused
        - Expected speedup: 10-15x faster
        """
        try:
            # Get connection
            connection = await self.cache_service.get(f"figma_connection:{user_id}")
            if not connection:
                if settings.FIGMA_ACCESS_TOKEN:
                    connection = {"access_token": settings.FIGMA_ACCESS_TOKEN}
                else:
                    raise Exception("Figma account not connected and no global access token configured")
            
            # Get Figma JSON
            file_key = self.figma_processor.extract_file_key(figma_url)
            if not file_key:
                raise Exception("Could not extract file key from URL")
            
            figma_json = await self.figma_processor.get_figma_json(
                file_key=file_key,
                access_token=connection["access_token"]
            )
            
            # Process using ULTRA-FAST approach
            result = await self.figma_fast_processor.process_figma_fast(
                figma_json=figma_json,
                user_message=user_message,
                framework=framework,
                backend_framework=backend_framework,
                max_batch_size=max_batch_size,
                max_concurrent_batches=max_concurrent_batches
            )
            
            if result["success"]:
                # Save generated code to files
                saved_files = await self._save_fast_generated_code(
                    result["frontend_code"],
                    result["backend_code"],
                    result["component_registry"],
                    result["design_tokens"]
                )
                
                return {
                    "success": True,
                    "file_key": file_key,
                    "processing_mode": "ultra_fast",
                    "frontend_code": result["frontend_code"],
                    "backend_code": result["backend_code"],
                    "component_registry": result["component_registry"],
                    "design_tokens": result["design_tokens"],
                    "statistics": result["statistics"],
                    "saved_files": saved_files
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def process_figma_url_lossless(
        self,
        figma_url: str,
        user_message: Optional[str] = None,
        framework: str = "react",
        backend_framework: str = "nodejs",
        user_id: Optional[str] = None,
        max_batch_size: int = 8,
        max_concurrent_batches: int = 3
    ) -> Dict[str, Any]:
        """
        Process Figma URL using TRULY LOSSLESS approach
        - Multi-pass architecture (6 passes)
        - Global layout graph extraction
        - Centralized design system
        - Context-aware component generation
        - Backend from real functional context
        - Consistency validation
        - Expected time: 20-40 minutes (vs 3-6 hours)
        """
        try:
            # Get connection
            connection = await self.cache_service.get(f"figma_connection:{user_id}")
            if not connection:
                if settings.FIGMA_ACCESS_TOKEN:
                    connection = {"access_token": settings.FIGMA_ACCESS_TOKEN}
                else:
                    raise Exception("Figma account not connected and no global access token configured")
            
            # Get Figma JSON
            file_key = self.figma_processor.extract_file_key(figma_url)
            if not file_key:
                raise Exception("Could not extract file key from URL")
            
            figma_json = await self.figma_processor.get_figma_json(
                file_key=file_key,
                access_token=connection["access_token"]
            )
            
            # Process using LOSSLESS approach
            result = await self.figma_lossless_processor.process_figma_lossless(
                figma_json=figma_json,
                user_message=user_message,
                framework=framework,
                backend_framework=backend_framework,
                max_batch_size=max_batch_size,
                max_concurrent_batches=max_concurrent_batches
            )
            
            if result["success"]:
                # Save generated code to files
                saved_files = await self._save_lossless_generated_code(
                    result["frontend_code"],
                    result["backend_code"],
                    result["component_registry"],
                    result["design_system"],
                    result["layout_graph"],
                    result["backend_system"]
                )
                
                return {
                    "success": True,
                    "file_key": file_key,
                    "processing_mode": "lossless",
                    "frontend_code": result["frontend_code"],
                    "backend_code": result["backend_code"],
                    "component_registry": result["component_registry"],
                    "design_system": result["design_system"],
                    "layout_graph": result["layout_graph"],
                    "backend_system": result["backend_system"],
                    "statistics": result["statistics"],
                    "saved_files": saved_files
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}

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
                chunk_size=3000  # Larger chunks for better efficiency
            )
            
            # Check if this is a screen-by-screen processing result
            if processing_result.get("processing_mode") == "screen_by_screen":
                # Process screens in parallel for speed
                import asyncio
                
                async def process_screen_parallel(screen_name, screen_data):
                    print(f"DEBUG: Processing screen: {screen_name}")
                    print(f"DEBUG: Screen data success: {screen_data.get('success', False)}")
                    print(f"DEBUG: Screen data keys: {list(screen_data.keys())}")
                    
                    if screen_data.get("success", False):
                        try:
                            print(f"DEBUG: Calling LLM for screen: {screen_name}")
                            screen_llm_result = await self.figma_llm_processor.process_figma_to_code(
                                figma_chunks=screen_data["chunks"],
                                user_message=user_message,
                                framework=framework,
                                backend_framework=backend_framework
                            )
                            
                            # Save generated code to files
                            saved_files = await self._save_generated_code(
                                screen_llm_result.get("frontend_code", {}),
                                screen_llm_result.get("backend_code", {}),
                                screen_name
                            )
                            
                            return screen_name, {
                                "success": True,
                                "frontend_code": screen_llm_result.get("frontend_code", {}),
                                "backend_code": screen_llm_result.get("backend_code", {}),
                                "components": screen_llm_result.get("components", []),
                                "statistics": screen_llm_result.get("statistics", {}),
                                "saved_files": saved_files
                            }
                        except Exception as e:
                            print(f"DEBUG: Error processing screen {screen_name}: {str(e)}")
                            return screen_name, {
                                "success": False,
                                "error": str(e)
                            }
                    else:
                        print(f"DEBUG: Screen {screen_name} failed: {screen_data.get('error', 'Unknown error')}")
                        return screen_name, {
                            "success": False,
                            "error": screen_data.get("error", "Unknown error")
                        }
                
                # Process all screens in parallel (max 5 concurrent)
                screen_tasks = []
                for screen_name, screen_data in processing_result["screens"].items():
                    screen_tasks.append(process_screen_parallel(screen_name, screen_data))
                
                # Execute in batches of 5 for optimal performance
                screen_results = {}
                all_frontend_code = {}
                all_backend_code = {}
                all_components = []
                all_statistics = {"total_screens": 0, "successful_screens": 0}
                
                # Process in batches of 1 screen at a time to avoid rate limiting
                batch_size = 1
                total_batches = (len(screen_tasks) + batch_size - 1) // batch_size
                
                for i in range(0, len(screen_tasks), batch_size):
                    batch = screen_tasks[i:i + batch_size]
                    batch_num = (i // batch_size) + 1
                    
                    print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} screens)")
                    batch_results = await asyncio.gather(*batch, return_exceptions=True)
                    
                    # Add delay between batches to avoid rate limiting
                    if batch_num < total_batches:
                        print(f"Waiting 5 seconds before next batch...")
                        await asyncio.sleep(5)
                    
                    for result in batch_results:
                        if isinstance(result, Exception):
                            continue
                        screen_name, screen_result = result
                        screen_results[screen_name] = screen_result
                        
                        if screen_result.get("success", False):
                            all_frontend_code.update(screen_result.get("frontend_code", {}))
                            all_backend_code.update(screen_result.get("backend_code", {}))
                            all_components.extend(screen_result.get("components", []))
                            all_statistics["successful_screens"] += 1
                        
                        all_statistics["total_screens"] += 1
                
                return {
                    "success": True,
                    "file_key": processing_result["file_key"],
                    "file_name": processing_result["file_name"],
                    "processing_mode": "screen_by_screen",
                    "screens": screen_results,
                    "shared_components": processing_result.get("shared_components", []),
                    "navigation": processing_result.get("navigation", {}),
                    "frontend_code": all_frontend_code,
                    "backend_code": all_backend_code,
                    "components": all_components,
                    "statistics": all_statistics,
                    "metadata": processing_result.get("metadata", {})
                }
            else:
                # Standard processing for smaller files
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
                    "processing_mode": "standard",
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
    
    async def _save_generated_code(self, frontend_code: Dict[str, str], backend_code: Dict[str, str], screen_name: str) -> Dict[str, Any]:
        """Save generated code to files"""
        import os
        import uuid
        from datetime import datetime
        
        try:
            # Create project directory
            project_id = f"figma_{screen_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            project_dir = f"/app/storage/generated/{project_id}"
            os.makedirs(project_dir, exist_ok=True)
            
            saved_files = {
                "project_id": project_id,
                "project_path": project_dir,
                "frontend_files": [],
                "backend_files": [],
                "total_files": 0
            }
            
            # Save frontend files
            if frontend_code:
                frontend_dir = os.path.join(project_dir, "frontend")
                os.makedirs(frontend_dir, exist_ok=True)
                
                for filename, content in frontend_code.items():
                    # Create directory structure if needed
                    file_path = os.path.join(frontend_dir, filename)
                    file_dir = os.path.dirname(file_path)
                    os.makedirs(file_dir, exist_ok=True)
                    
                    # Write file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    saved_files["frontend_files"].append({
                        "filename": filename,
                        "path": file_path,
                        "size": len(content)
                    })
                    print(f"DEBUG: Saved frontend file: {filename}")
            
            # Save backend files
            if backend_code:
                backend_dir = os.path.join(project_dir, "backend")
                os.makedirs(backend_dir, exist_ok=True)
                
                for filename, content in backend_code.items():
                    # Create directory structure if needed
                    file_path = os.path.join(backend_dir, filename)
                    file_dir = os.path.dirname(file_path)
                    os.makedirs(file_dir, exist_ok=True)
                    
                    # Write file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    saved_files["backend_files"].append({
                        "filename": filename,
                        "path": file_path,
                        "size": len(content)
                    })
                    print(f"DEBUG: Saved backend file: {filename}")
            
            saved_files["total_files"] = len(saved_files["frontend_files"]) + len(saved_files["backend_files"])
            print(f"DEBUG: Saved {saved_files['total_files']} files to {project_dir}")
            
            return saved_files
            
        except Exception as e:
            print(f"DEBUG: Error saving files: {str(e)}")
            return {"error": str(e)}
    
    async def _save_streaming_generated_code(
        self, 
        frontend_code: Dict[str, str], 
        backend_code: Dict[str, str],
        component_registry: Dict[str, Any],
        design_tokens: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save streaming generated code to files"""
        import os
        import uuid
        from datetime import datetime
        
        try:
            # Create project directory
            project_id = f"streaming_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            project_dir = f"/app/storage/generated/{project_id}"
            os.makedirs(project_dir, exist_ok=True)
            
            saved_files = {
                "project_id": project_id,
                "project_path": project_dir,
                "frontend_files": [],
                "backend_files": [],
                "total_files": 0
            }
            
            # Save frontend files
            if frontend_code:
                frontend_dir = os.path.join(project_dir, "frontend")
                os.makedirs(frontend_dir, exist_ok=True)
                
                for filename, content in frontend_code.items():
                    file_path = os.path.join(frontend_dir, filename)
                    file_dir = os.path.dirname(file_path)
                    os.makedirs(file_dir, exist_ok=True)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    saved_files["frontend_files"].append({
                        "filename": filename,
                        "path": file_path,
                        "size": len(content)
                    })
            
            # Save backend files
            if backend_code:
                backend_dir = os.path.join(project_dir, "backend")
                os.makedirs(backend_dir, exist_ok=True)
                
                for filename, content in backend_code.items():
                    file_path = os.path.join(backend_dir, filename)
                    file_dir = os.path.dirname(file_path)
                    os.makedirs(file_dir, exist_ok=True)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    saved_files["backend_files"].append({
                        "filename": filename,
                        "path": file_path,
                        "size": len(content)
                    })
            
            # Save component registry
            registry_path = os.path.join(project_dir, "component-registry.json")
            with open(registry_path, 'w', encoding='utf-8') as f:
                json.dump(component_registry, f, indent=2)
            
            # Save design tokens
            tokens_path = os.path.join(project_dir, "design-tokens.json")
            with open(tokens_path, 'w', encoding='utf-8') as f:
                json.dump(design_tokens, f, indent=2)
            
            saved_files["total_files"] = len(saved_files["frontend_files"]) + len(saved_files["backend_files"]) + 2
            print(f"DEBUG: Saved {saved_files['total_files']} files to {project_dir}")
            
            return saved_files
            
        except Exception as e:
            print(f"DEBUG: Error saving streaming files: {str(e)}")
            return {"error": str(e)}
