"""
Figma LLM Processor
Handles LLM inference for Figma chunks with retry and caching
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

from app.services.llm_service import LLMService, LLMRequest, LLMResponse
from app.services.cache_service import CacheService
from app.helpers.retry import RetryHelper, RetryConfig
from app.helpers.common import CommonUtils


@dataclass
class ChunkResult:
    """Result of processing a chunk"""
    chunk_id: str
    success: bool
    generated_code: str
    error: Optional[str] = None
    tokens_used: int = 0
    processing_time: float = 0.0


@dataclass
class MergedResult:
    """Result of merging code snippets"""
    frontend_code: Dict[str, str]  # file_path -> content
    backend_code: Dict[str, str]   # file_path -> content
    components: List[Dict[str, Any]]
    total_tokens: int
    processing_time: float


class FigmaLLMProcessor:
    """Processes Figma chunks through LLM with retry and caching"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.cache_service = CacheService()
        self.retry_helper = RetryHelper()
        self.common_utils = CommonUtils()
        
        # Retry configuration for LLM calls
        self.retry_config = RetryConfig(
            max_attempts=3,
            base_delay=1.0,
            max_delay=10.0,
            strategy="exponential",
            jitter=True
        )
    
    async def process_chunks(
        self,
        chunks: List[Dict[str, Any]],
        framework: str = "react",
        backend_framework: str = "nodejs",
        user_message: Optional[str] = None
    ) -> List[ChunkResult]:
        """Process Figma chunks through LLM sequentially"""
        results = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"chunk_{i}_{chunk.get('frame_id', 'unknown')}"
            
            try:
                # Check cache first
                cache_key = f"figma_chunk:{chunk_id}:{framework}:{backend_framework}"
                cached_result = await self.cache_service.get(cache_key)
                
                if cached_result:
                    results.append(ChunkResult(
                        chunk_id=chunk_id,
                        success=True,
                        generated_code=cached_result["code"],
                        tokens_used=cached_result.get("tokens", 0),
                        processing_time=cached_result.get("time", 0.0)
                    ))
                    continue
                
                # Process chunk through LLM
                result = await self._process_single_chunk(
                    chunk=chunk,
                    chunk_id=chunk_id,
                    framework=framework,
                    backend_framework=backend_framework,
                    user_message=user_message
                )
                
                # Cache successful results
                if result.success:
                    await self.cache_service.set(
                        cache_key,
                        {
                            "code": result.generated_code,
                            "tokens": result.tokens_used,
                            "time": result.processing_time
                        },
                        ttl=3600  # 1 hour
                    )
                
                results.append(result)
                
                # Add delay between chunks to avoid rate limiting
                if i < len(chunks) - 1:
                    await asyncio.sleep(0.5)
                    
            except Exception as e:
                results.append(ChunkResult(
                    chunk_id=chunk_id,
                    success=False,
                    generated_code="",
                    error=str(e)
                ))
        
        return results
    
    async def _process_single_chunk(
        self,
        chunk: Dict[str, Any],
        chunk_id: str,
        framework: str,
        backend_framework: str,
        user_message: Optional[str] = None
    ) -> ChunkResult:
        """Process a single chunk through LLM with retry"""
        start_time = datetime.now()
        
        try:
            # Build prompt for chunk
            prompt = self._build_chunk_prompt(
                chunk=chunk,
                framework=framework,
                backend_framework=backend_framework,
                user_message=user_message
            )
            
            # Create LLM request
            llm_request = LLMRequest(
                prompt=prompt,
                model="gemini-1.5-pro",
                max_tokens=4000,
                temperature=0.1,
                top_p=0.9
            )
            
            # Call LLM with retry
            llm_response = await self.retry_helper.retry_async(
                func=self.llm_service.generate_completion,
                config=self.retry_config,
                request=llm_request
            )
            
            if llm_response.success:
                processing_time = (datetime.now() - start_time).total_seconds()
                
                return ChunkResult(
                    chunk_id=chunk_id,
                    success=True,
                    generated_code=llm_response.content,
                    tokens_used=llm_response.tokens_used,
                    processing_time=processing_time
                )
            else:
                return ChunkResult(
                    chunk_id=chunk_id,
                    success=False,
                    generated_code="",
                    error=llm_response.error
                )
                
        except Exception as e:
            return ChunkResult(
                chunk_id=chunk_id,
                success=False,
                generated_code="",
                error=str(e)
            )
    
    def _build_chunk_prompt(
        self,
        chunk: Dict[str, Any],
        framework: str,
        backend_framework: str,
        user_message: Optional[str] = None
    ) -> str:
        """Build prompt for processing a Figma chunk"""
        
        # Get chunk information
        chunk_type = chunk.get("type", "unknown")
        frame_name = chunk.get("frame_name", "")
        component_name = chunk.get("component_name", "")
        chunk_data = chunk.get("data", {})
        
        # Build base prompt
        prompt_parts = [
            f"# Figma Design to Code Generation",
            f"",
            f"**Task**: Convert this Figma design chunk to {framework} frontend and {backend_framework} backend code.",
            f"",
            f"**Chunk Type**: {chunk_type}",
            f"**Frame**: {frame_name}",
        ]
        
        if component_name:
            prompt_parts.append(f"**Component**: {component_name}")
        
        if user_message:
            prompt_parts.extend([
                f"",
                f"**User Requirements**: {user_message}",
            ])
        
        prompt_parts.extend([
            f"",
            f"**Design Data**:",
            f"```json",
            json.dumps(chunk_data, indent=2),
            f"```",
            f"",
            f"**Instructions**:",
            f"1. Generate clean, production-ready {framework} frontend code",
            f"2. Generate corresponding {backend_framework} backend API endpoints",
            f"3. Include proper TypeScript types and interfaces",
            f"4. Add responsive design considerations",
            f"5. Include accessibility features",
            f"6. Use modern best practices and patterns",
            f"",
            f"**Output Format**:",
            f"```",
            f"## Frontend Code",
            f"",
            f"### [filename].tsx",
            f"```tsx",
            f"// React component code here",
            f"```",
            f"",
            f"### [filename].css",
            f"```css",
            f"/* CSS styles here */",
            f"```",
            f"",
            f"## Backend Code",
            f"",
            f"### [filename].ts",
            f"```typescript",
            f"// Backend API code here",
            f"```",
            f"",
            f"### [filename].types.ts",
            f"```typescript",
            f"// TypeScript interfaces here",
            f"```",
            f"```",
        ])
        
        return "\n".join(prompt_parts)
    
    async def merge_code_results(
        self,
        chunk_results: List[ChunkResult],
        framework: str = "react",
        backend_framework: str = "nodejs"
    ) -> MergedResult:
        """Merge code snippets from multiple chunks intelligently"""
        start_time = datetime.now()
        
        frontend_files = {}
        backend_files = {}
        components = []
        total_tokens = 0
        
        for result in chunk_results:
            if not result.success:
                continue
            
            total_tokens += result.tokens_used
            
            # Parse generated code
            parsed_code = self._parse_generated_code(result.generated_code)
            
            # Merge frontend files
            for file_path, content in parsed_code.get("frontend", {}).items():
                if file_path in frontend_files:
                    # Merge content intelligently
                    frontend_files[file_path] = self._merge_file_content(
                        frontend_files[file_path],
                        content,
                        file_path
                    )
                else:
                    frontend_files[file_path] = content
            
            # Merge backend files
            for file_path, content in parsed_code.get("backend", {}).items():
                if file_path in backend_files:
                    # Merge content intelligently
                    backend_files[file_path] = self._merge_file_content(
                        backend_files[file_path],
                        content,
                        file_path
                    )
                else:
                    backend_files[file_path] = content
            
            # Collect components
            if parsed_code.get("components"):
                components.extend(parsed_code["components"])
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return MergedResult(
            frontend_code=frontend_files,
            backend_code=backend_files,
            components=components,
            total_tokens=total_tokens,
            processing_time=processing_time
        )
    
    def _parse_generated_code(self, code_text: str) -> Dict[str, Any]:
        """Parse generated code text into structured format"""
        result = {
            "frontend": {},
            "backend": {},
            "components": []
        }
        
        lines = code_text.split('\n')
        current_section = None
        current_file = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            
            # Detect section headers
            if line.startswith('## Frontend Code'):
                current_section = 'frontend'
                continue
            elif line.startswith('## Backend Code'):
                current_section = 'backend'
                continue
            
            # Detect file headers
            if line.startswith('### ') and current_section:
                # Save previous file
                if current_file and current_content:
                    result[current_section][current_file] = '\n'.join(current_content)
                
                # Start new file
                current_file = line[4:].strip()
                current_content = []
                continue
            
            # Detect code blocks
            if line.startswith('```'):
                continue
            
            # Collect content
            if current_file and current_section:
                current_content.append(line)
        
        # Save last file
        if current_file and current_content:
            result[current_section][current_file] = '\n'.join(current_content)
        
        return result
    
    def _merge_file_content(
        self,
        existing_content: str,
        new_content: str,
        file_path: str
    ) -> str:
        """Merge file content intelligently"""
        # Simple merge strategy - in production, use more sophisticated merging
        if not existing_content:
            return new_content
        
        if not new_content:
            return existing_content
        
        # For now, append with separator
        # In production, implement proper code merging
        return f"{existing_content}\n\n// === Merged Content ===\n\n{new_content}"
    
    async def process_figma_to_code(
        self,
        figma_chunks: List[Dict[str, Any]],
        user_message: Optional[str] = None,
        framework: str = "react",
        backend_framework: str = "nodejs"
    ) -> Dict[str, Any]:
        """Complete Figma to code processing pipeline"""
        try:
            # Process chunks through LLM
            chunk_results = await self.process_chunks(
                chunks=figma_chunks,
                framework=framework,
                backend_framework=backend_framework,
                user_message=user_message
            )
            
            # Calculate success rate
            successful_chunks = [r for r in chunk_results if r.success]
            success_rate = len(successful_chunks) / len(chunk_results) if chunk_results else 0
            
            # Merge results
            merged_result = await self.merge_code_results(
                chunk_results=chunk_results,
                framework=framework,
                backend_framework=backend_framework
            )
            
            return {
                "success": True,
                "frontend_code": merged_result.frontend_code,
                "backend_code": merged_result.backend_code,
                "components": merged_result.components,
                "statistics": {
                    "total_chunks": len(chunk_results),
                    "successful_chunks": len(successful_chunks),
                    "success_rate": success_rate,
                    "total_tokens": merged_result.total_tokens,
                    "processing_time": merged_result.processing_time
                },
                "chunk_results": [
                    {
                        "chunk_id": r.chunk_id,
                        "success": r.success,
                        "error": r.error,
                        "tokens_used": r.tokens_used,
                        "processing_time": r.processing_time
                    }
                    for r in chunk_results
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "frontend_code": {},
                "backend_code": {},
                "components": [],
                "statistics": {
                    "total_chunks": 0,
                    "successful_chunks": 0,
                    "success_rate": 0,
                    "total_tokens": 0,
                    "processing_time": 0
                }
            }
