"""
Figma Streaming Processor
Uses streaming parser to extract components and generate both frontend and backend code
without token explosion
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
class ComponentGenerationResult:
    """Result of component generation"""
    component_name: str
    success: bool
    frontend_files: Dict[str, str]
    backend_files: Dict[str, str]
    registry_entry: Dict[str, Any]
    tokens_used: int
    processing_time: float
    error: Optional[str] = None


@dataclass
class ProjectGenerationResult:
    """Result of complete project generation"""
    success: bool
    frontend_code: Dict[str, str]
    backend_code: Dict[str, str]
    component_registry: Dict[str, Any]
    design_tokens: Dict[str, Any]
    statistics: Dict[str, Any]
    errors: List[str]


class FigmaStreamingProcessor:
    """Processes Figma designs using streaming approach to generate fullstack code"""
    
    def __init__(self):
        self.streaming_parser = FigmaStreamingParser()
        self.llm_service = LLMService()
        self.cache_service = CacheService()
        self.retry_helper = RetryHelper()
        
        # Retry configuration
        self.retry_config = RetryConfig(
            max_attempts=3,
            base_delay=1.0,
            max_delay=10.0,
            strategy="exponential",
            jitter=True
        )
    
    async def process_figma_to_fullstack(
        self,
        figma_json: Dict[str, Any],
        user_message: Optional[str] = None,
        framework: str = "react",
        backend_framework: str = "nodejs",
        target_screens: Optional[List[str]] = None
    ) -> ProjectGenerationResult:
        """
        Process Figma JSON to generate fullstack code using streaming approach
        
        Args:
            figma_json: Full Figma JSON data
            user_message: User requirements
            framework: Frontend framework
            backend_framework: Backend framework
            target_screens: Specific screens to process (None = all)
        """
        start_time = datetime.now()
        
        try:
            print("DEBUG: Starting streaming fullstack generation")
            
            # Step 1: Extract components using streaming parser
            extraction_result = await self.streaming_parser.extract_components(
                figma_json=figma_json,
                target_screens=target_screens
            )
            
            print(f"DEBUG: Extracted {len(extraction_result.components)} components")
            
            # Step 2: Generate code for each component
            component_results = []
            all_frontend_code = {}
            all_backend_code = {}
            component_registry = {}
            total_tokens = 0
            
            # Process components in batches to avoid rate limiting
            batch_size = 3
            components = extraction_result.components
            
            for i in range(0, len(components), batch_size):
                batch = components[i:i + batch_size]
                print(f"DEBUG: Processing batch {i//batch_size + 1}/{(len(components) + batch_size - 1)//batch_size}")
                
                # Process batch in parallel
                batch_tasks = [
                    self._generate_component_code(
                        component=component,
                        user_message=user_message,
                        framework=framework,
                        backend_framework=backend_framework,
                        design_tokens=extraction_result.design_tokens
                    )
                    for component in batch
                ]
                
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Process results
                for result in batch_results:
                    if isinstance(result, Exception):
                        print(f"DEBUG: Component generation failed: {str(result)}")
                        continue
                    
                    if result.success:
                        component_results.append(result)
                        all_frontend_code.update(result.frontend_files)
                        all_backend_code.update(result.backend_files)
                        component_registry[result.component_name] = result.registry_entry
                        total_tokens += result.tokens_used
                
                # Add delay between batches
                if i + batch_size < len(components):
                    await asyncio.sleep(2)
            
            # Step 3: Generate project structure files
            project_files = await self._generate_project_structure(
                component_registry=component_registry,
                design_tokens=extraction_result.design_tokens,
                framework=framework,
                backend_framework=backend_framework
            )
            
            # Merge project files
            all_frontend_code.update(project_files.get("frontend", {}))
            all_backend_code.update(project_files.get("backend", {}))
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProjectGenerationResult(
                success=True,
                frontend_code=all_frontend_code,
                backend_code=all_backend_code,
                component_registry=component_registry,
                design_tokens=extraction_result.design_tokens,
                statistics={
                    "total_components": len(component_results),
                    "successful_components": len([r for r in component_results if r.success]),
                    "total_tokens": total_tokens,
                    "processing_time": processing_time,
                    "frontend_files": len(all_frontend_code),
                    "backend_files": len(all_backend_code)
                },
                errors=[]
            )
            
        except Exception as e:
            return ProjectGenerationResult(
                success=False,
                frontend_code={},
                backend_code={},
                component_registry={},
                design_tokens={},
                statistics={},
                errors=[str(e)]
            )
    
    async def _generate_component_code(
        self,
        component: ComponentNode,
        user_message: Optional[str],
        framework: str,
        backend_framework: str,
        design_tokens: Dict[str, Any]
    ) -> ComponentGenerationResult:
        """Generate code for a single component"""
        start_time = datetime.now()
        
        try:
            # Build component-specific prompt
            prompt = self._build_component_prompt(
                component=component,
                user_message=user_message,
                framework=framework,
                backend_framework=backend_framework,
                design_tokens=design_tokens
            )
            
            # Create LLM request
            llm_request = LLMRequest(
                prompt=prompt,
                model="gemini-2.5-pro",
                max_tokens=8000,  # Reduced to prevent token explosion
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
                # Parse JSON response
                response_data = json.loads(llm_response.content)
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                return ComponentGenerationResult(
                    component_name=component.name,
                    success=True,
                    frontend_files=response_data.get("files", {}),
                    backend_files=response_data.get("backendFiles", {}),
                    registry_entry=response_data.get("registryEntry", {}),
                    tokens_used=llm_response.tokens_used,
                    processing_time=processing_time
                )
            else:
                return ComponentGenerationResult(
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
            return ComponentGenerationResult(
                component_name=component.name,
                success=False,
                frontend_files={},
                backend_files={},
                registry_entry={},
                tokens_used=0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                error=str(e)
            )
    
    def _build_component_prompt(
        self,
        component: ComponentNode,
        user_message: Optional[str],
        framework: str,
        backend_framework: str,
        design_tokens: Dict[str, Any]
    ) -> str:
        """Build prompt for component generation"""
        
        prompt_parts = [
            f"# Component Generation: {component.name}",
            f"",
            f"**Task**: Generate {framework} frontend component and {backend_framework} backend API for this Figma component.",
            f"",
            f"**Component Details**:",
            f"- Name: {component.name}",
            f"- Type: {component.component_type}",
            f"- Node ID: {component.node_id}",
            f"- Bounds: {component.bounds}",
        ]
        
        if user_message:
            prompt_parts.extend([
                f"",
                f"**User Requirements**: {user_message}",
            ])
        
        prompt_parts.extend([
            f"",
            f"**Design Tokens Available**:",
            json.dumps(design_tokens, indent=2),
            f"",
            f"**Component Styles**:",
            json.dumps(component.styles, indent=2),
            f"",
            f"**Instructions**:",
            f"1. Generate ONLY the component and its related API endpoints",
            f"2. Use the design tokens provided",
            f"3. Include proper TypeScript types",
            f"4. Add accessibility features",
            f"5. Use modern best practices",
            f"6. Output JSON format as specified in the component-only prompt template",
            f"",
            f"**Output Format**: JSON with files, backendFiles, and registryEntry keys",
        ])
        
        return "\n".join(prompt_parts)
    
    async def _generate_project_structure(
        self,
        component_registry: Dict[str, Any],
        design_tokens: Dict[str, Any],
        framework: str,
        backend_framework: str
    ) -> Dict[str, Dict[str, str]]:
        """Generate project structure files"""
        
        # Generate design tokens file
        design_tokens_file = self._generate_design_tokens_file(design_tokens)
        
        # Generate component registry file
        registry_file = self._generate_component_registry_file(component_registry)
        
        # Generate main app file
        app_file = self._generate_main_app_file(component_registry, framework)
        
        # Generate server setup
        server_file = self._generate_server_file(component_registry, backend_framework)
        
        return {
            "frontend": {
                "src/design-tokens.ts": design_tokens_file,
                "src/component-registry.json": registry_file,
                "src/App.tsx": app_file
            },
            "backend": {
                "src/server.ts": server_file,
                "src/types/index.ts": self._generate_types_file()
            }
        }
    
    def _generate_design_tokens_file(self, design_tokens: Dict[str, Any]) -> str:
        """Generate design tokens TypeScript file"""
        return f"""// Design Tokens
// Generated from Figma design

export const designTokens = {json.dumps(design_tokens, indent=2)};

export type DesignTokens = typeof designTokens;
"""
    
    def _generate_component_registry_file(self, component_registry: Dict[str, Any]) -> str:
        """Generate component registry JSON file"""
        return json.dumps(component_registry, indent=2)
    
    def _generate_main_app_file(self, component_registry: Dict[str, Any], framework: str) -> str:
        """Generate main App component"""
        if framework == "react":
            return f"""import React from 'react';
import {{ designTokens }} from './design-tokens';
import componentRegistry from './component-registry.json';

const App: React.FC = () => {{
  return (
    <div className="app">
      <h1>Generated App</h1>
      <p>Components: {{Object.keys(componentRegistry).length}}</p>
    </div>
  );
}};

export default App;
"""
        return "// App component"
    
    def _generate_server_file(self, component_registry: Dict[str, Any], backend_framework: str) -> str:
        """Generate server setup file"""
        if backend_framework == "nodejs":
            return f"""import express from 'express';
import cors from 'cors';

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {{
  res.json({{ status: 'ok', components: {len(component_registry)} }});
}});

app.listen(PORT, () => {{
  console.log(`Server running on port ${{PORT}}`);
}});
"""
        return "// Server setup"
    
    def _generate_types_file(self) -> str:
        """Generate TypeScript types file"""
        return """// TypeScript types for generated project

export interface ComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  error?: string;
}
"""
