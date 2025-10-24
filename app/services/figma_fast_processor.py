"""
Fast Figma Processor
Optimized for high-speed processing with larger batches and parallel execution
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from app.services.figma_streaming_parser import FigmaStreamingParser, ExtractionResult, ComponentNode
from app.services.llm_service import LLMService, LLMRequest, LLMResponse
from app.services.cache_service import CacheService
from app.helpers.retry import RetryHelper, RetryConfig


@dataclass
class FastComponentResult:
    """Result of fast component generation"""
    component_name: str
    success: bool
    frontend_files: Dict[str, str]
    backend_files: Dict[str, str]
    registry_entry: Dict[str, Any]
    tokens_used: int
    processing_time: float
    error: Optional[str] = None


class FigmaFastProcessor:
    """Ultra-fast Figma processor with optimized batch processing"""
    
    def __init__(self):
        self.streaming_parser = FigmaStreamingParser()
        self.llm_service = LLMService()
        self.cache_service = CacheService()
        self.retry_helper = RetryHelper()
        
        # Optimized retry configuration (balanced for speed + reliability)
        self.retry_config = RetryConfig(
            max_attempts=3,  # Restored to 3 for reliability
            base_delay=0.5,  # Kept fast
            max_delay=8.0,   # Increased for better rate limit handling
            strategy="exponential",
            jitter=True
        )
    
    async def process_figma_fast(
        self,
        figma_json: Dict[str, Any],
        user_message: Optional[str] = None,
        framework: str = "react",
        backend_framework: str = "nodejs",
        target_screens: Optional[List[str]] = None,
        max_batch_size: int = 10,  # Increased from 3
        max_concurrent_batches: int = 5  # New: parallel batch processing
    ) -> Dict[str, Any]:
        """
        Ultra-fast Figma processing with optimized batching
        
        Args:
            figma_json: Full Figma JSON data
            user_message: User requirements
            framework: Frontend framework
            backend_framework: Backend framework
            target_screens: Specific screens to process
            max_batch_size: Maximum components per batch (default: 10)
            max_concurrent_batches: Number of batches to process in parallel (default: 5)
        """
        start_time = datetime.now()
        
        try:
            print(f"DEBUG: Starting FAST processing with batch_size={max_batch_size}, concurrent_batches={max_concurrent_batches}")
            
            # Step 1: Extract components using streaming parser
            extraction_result = await self.streaming_parser.extract_components(
                figma_json=figma_json,
                target_screens=target_screens
            )
            
            print(f"DEBUG: Extracted {len(extraction_result.components)} components")
            
            # Step 2: Fast parallel processing
            all_frontend_code = {}
            all_backend_code = {}
            component_registry = {}
            total_tokens = 0
            successful_components = 0
            
            components = extraction_result.components
            total_batches = (len(components) + max_batch_size - 1) // max_batch_size
            
            print(f"DEBUG: Processing {len(components)} components in {total_batches} batches")
            
            # Process components in parallel batches
            for i in range(0, len(components), max_batch_size * max_concurrent_batches):
                # Create multiple batches to process in parallel
                batch_groups = []
                for j in range(max_concurrent_batches):
                    batch_start = i + (j * max_batch_size)
                    batch_end = min(batch_start + max_batch_size, len(components))
                    
                    if batch_start >= len(components):
                        break
                    
                    batch_components = components[batch_start:batch_end]
                    if batch_components:
                        batch_groups.append(batch_components)
                
                if not batch_groups:
                    break
                
                # Process all batches in parallel
                batch_tasks = []
                for batch_components in batch_groups:
                    task = self._process_batch_fast(
                        batch_components,
                        user_message,
                        framework,
                        backend_framework,
                        extraction_result.design_tokens
                    )
                    batch_tasks.append(task)
                
                # Execute all batches in parallel
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Process results
                for batch_result in batch_results:
                    if isinstance(batch_result, Exception):
                        print(f"DEBUG: Batch processing failed: {str(batch_result)}")
                        continue
                    
                    for result in batch_result:
                        if result.success:
                            all_frontend_code.update(result.frontend_files)
                            all_backend_code.update(result.backend_files)
                            component_registry[result.component_name] = result.registry_entry
                            total_tokens += result.tokens_used
                            successful_components += 1
                
                # Minimal delay between batch groups (reduced from 2 seconds)
                if i + (max_batch_size * max_concurrent_batches) < len(components):
                    await asyncio.sleep(0.5)  # Reduced from 2 seconds
                
                # Progress update
                processed = min(i + (max_batch_size * max_concurrent_batches), len(components))
                progress = (processed / len(components)) * 100
                print(f"DEBUG: Progress: {processed}/{len(components)} ({progress:.1f}%) - {successful_components} successful")
            
            # Step 3: Generate project structure files
            project_files = await self._generate_project_structure_fast(
                component_registry=component_registry,
                design_tokens=extraction_result.design_tokens,
                framework=framework,
                backend_framework=backend_framework
            )
            
            # Merge project files
            all_frontend_code.update(project_files.get("frontend", {}))
            all_backend_code.update(project_files.get("backend", {}))
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            print(f"DEBUG: FAST processing completed in {processing_time:.2f} seconds")
            print(f"DEBUG: Generated {len(all_frontend_code)} frontend files, {len(all_backend_code)} backend files")
            
            return {
                "success": True,
                "frontend_code": all_frontend_code,
                "backend_code": all_backend_code,
                "component_registry": component_registry,
                "design_tokens": extraction_result.design_tokens,
                "statistics": {
                    "total_components": len(components),
                    "successful_components": successful_components,
                    "total_tokens": total_tokens,
                    "processing_time": processing_time,
                    "frontend_files": len(all_frontend_code),
                    "backend_files": len(all_backend_code),
                    "components_per_second": len(components) / processing_time if processing_time > 0 else 0
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "frontend_code": {},
                "backend_code": {},
                "component_registry": {},
                "design_tokens": {},
                "statistics": {}
            }
    
    async def _process_batch_fast(
        self,
        batch_components: List[ComponentNode],
        user_message: Optional[str],
        framework: str,
        backend_framework: str,
        design_tokens: Dict[str, Any]
    ) -> List[FastComponentResult]:
        """Process a batch of components in parallel"""
        batch_tasks = []
        
        for component in batch_components:
            task = self._generate_component_fast(
                component=component,
                user_message=user_message,
                framework=framework,
                backend_framework=backend_framework,
                design_tokens=design_tokens
            )
            batch_tasks.append(task)
        
        # Process all components in the batch in parallel
        results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        # Convert exceptions to failed results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append(FastComponentResult(
                    component_name="unknown",
                    success=False,
                    frontend_files={},
                    backend_files={},
                    registry_entry={},
                    tokens_used=0,
                    processing_time=0,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _generate_component_fast(
        self,
        component: ComponentNode,
        user_message: Optional[str],
        framework: str,
        backend_framework: str,
        design_tokens: Dict[str, Any]
    ) -> FastComponentResult:
        """Generate code for a single component with optimized settings"""
        start_time = datetime.now()
        
        try:
            # Build optimized prompt (shorter, more focused)
            prompt = self._build_fast_prompt(
                component=component,
                user_message=user_message,
                framework=framework,
                backend_framework=backend_framework,
                design_tokens=design_tokens
            )
            
            # Create optimized LLM request
            llm_request = LLMRequest(
                prompt=prompt,
                model="gemini-2.5-pro",
                max_tokens=8000,  # Restored to 8000 for lossless processing
                temperature=0.1,
                top_p=0.9
            )
            
            # Call LLM with fast retry
            llm_response = await self.retry_helper.retry_async(
                func=self.llm_service.generate_completion,
                config=self.retry_config,
                request=llm_request
            )
            
            if llm_response.success:
                # Parse JSON response quickly
                try:
                    response_data = json.loads(llm_response.content)
                except json.JSONDecodeError:
                    # Fallback parsing for malformed JSON
                    response_data = self._parse_fallback_json(llm_response.content)
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                return FastComponentResult(
                    component_name=component.name,
                    success=True,
                    frontend_files=response_data.get("files", {}),
                    backend_files=response_data.get("backendFiles", {}),
                    registry_entry=response_data.get("registryEntry", {}),
                    tokens_used=llm_response.tokens_used,
                    processing_time=processing_time
                )
            else:
                return FastComponentResult(
                    component_name=component.name,
                    success=False,
                    frontend_files={},
                    backend_files={},
                    registry_entry={},
                    tokens_used=0,
                    processing_time=(datetime.now() - start_time).total_seconds(),
                    error=llm_response.error
                )
                
        except Exception as e:
            return FastComponentResult(
                component_name=component.name,
                success=False,
                frontend_files={},
                backend_files={},
                registry_entry={},
                tokens_used=0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                error=str(e)
            )
    
    def _build_fast_prompt(
        self,
        component: ComponentNode,
        user_message: Optional[str],
        framework: str,
        backend_framework: str,
        design_tokens: Dict[str, Any]
    ) -> str:
        """Build optimized, shorter prompt for faster processing"""
        
        prompt_parts = [
            f"# Fast Component Generation: {component.name}",
            f"Generate {framework} frontend + {backend_framework} backend for this component.",
            f"",
            f"**Component**: {component.name} ({component.component_type})",
        ]
        
        if user_message:
            prompt_parts.append(f"**Requirements**: {user_message}")
        
        prompt_parts.extend([
            f"",
            f"**Output JSON format**:",
            f'{{"files": [{{"path": "filename.tsx", "content": "code"}}], "backendFiles": [{{"path": "api.ts", "content": "code"}}], "registryEntry": {{"componentName": "Name", "path": "file.tsx", "tokens": ["token1"], "apiEndpoints": ["/api/endpoint"]}}}}',
            f"",
            f"Generate clean, production-ready code with TypeScript types.",
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_fallback_json(self, content: str) -> Dict[str, Any]:
        """Fallback JSON parsing for malformed responses"""
        try:
            # Try to extract JSON from markdown code blocks
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                if end > start:
                    json_content = content[start:end].strip()
                    return json.loads(json_content)
            
            # Try to find JSON object in content
            start = content.find("{")
            if start >= 0:
                # Find matching closing brace
                brace_count = 0
                for i, char in enumerate(content[start:], start):
                    if char == "{":
                        brace_count += 1
                    elif char == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            json_content = content[start:i+1]
                            return json.loads(json_content)
            
            # Return empty structure if parsing fails
            return {
                "files": [],
                "backendFiles": [],
                "registryEntry": {}
            }
            
        except Exception:
            return {
                "files": [],
                "backendFiles": [],
                "registryEntry": {}
            }
    
    async def _generate_project_structure_fast(
        self,
        component_registry: Dict[str, Any],
        design_tokens: Dict[str, Any],
        framework: str,
        backend_framework: str
    ) -> Dict[str, Dict[str, str]]:
        """Generate minimal project structure files"""
        
        return {
            "frontend": {
                "src/design-tokens.ts": f"export const designTokens = {json.dumps(design_tokens, indent=2)};",
                "src/component-registry.json": json.dumps(component_registry, indent=2)
            },
            "backend": {
                "src/server.ts": "import express from 'express';\nconst app = express();\napp.use(express.json());\napp.listen(3001, () => console.log('Server running on port 3001'));"
            }
        }
