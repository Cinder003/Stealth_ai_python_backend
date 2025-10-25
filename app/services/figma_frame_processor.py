"""
Figma Frame-Specific Processor
Processes individual frames using get_nodes() API for optimal performance
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from app.services.figma_service import FigmaService
from app.services.llm_service import LLMService
from app.services.observability_service import ObservabilityService
from app.core.config import settings


@dataclass
class FrameResult:
    """Result of processing a single frame"""
    frame_id: str
    frame_name: str
    success: bool
    frontend_files: Dict[str, str]
    backend_files: Dict[str, str]
    tokens_used: int
    processing_time: float
    error: Optional[str] = None


class FigmaFrameProcessor:
    """
    Process individual Figma frames using get_nodes() API
    This eliminates token explosion by processing only frame + children
    """
    
    def __init__(self):
        self.figma_service = FigmaService()
        self.llm_service = LLMService()
        self.observability_service = ObservabilityService()
    
    async def process_figma_frames(
        self,
        file_key: str,
        access_token: str,
        user_message: Optional[str] = None,
        framework: str = "react",
        backend_framework: str = "nodejs",
        target_frames: Optional[List[str]] = None,
        figma_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process Figma file by individual frames using get_nodes() API
        
        Args:
            file_key: Figma file key
            access_token: Figma access token
            user_message: User's additional requirements
            framework: Frontend framework
            backend_framework: Backend framework
            target_frames: Specific frame IDs to process (if None, processes all frames)
        
        Returns:
            Dict containing all generated files and metadata
        """
        try:
            # Step 1: Extract specific node IDs from URL if provided
            if figma_url:
                print("🎯 Extracting specific node IDs from prototype URL...")
                frame_ids = self._extract_node_ids_from_url(figma_url)
                if frame_ids:
                    print(f"✅ Found {len(frame_ids)} specific frames from URL: {frame_ids}")
                else:
                    print("⚠️  No specific frames found in URL, falling back to all frames")
                    # Fallback to getting all frames
                    file_structure = await self._get_file_structure(file_key, access_token)
                    frame_ids = self._extract_frame_ids(file_structure)
            elif target_frames:
                frame_ids = target_frames
                print(f"📋 Using provided target frames: {frame_ids}")
            else:
                # Step 1: Get file structure to identify frames
                print("🔍 Analyzing Figma file structure...")
                file_structure = await self._get_file_structure(file_key, access_token)
                frame_ids = self._extract_frame_ids(file_structure)
            
            print(f"📋 Processing {len(frame_ids)} frames")
            
            # Step 3: Process each frame individually
            frame_results = []
            all_files = {"frontend": {}, "backend": {}}
            component_registry = {}
            design_tokens = {}
            
            for i, frame_id in enumerate(frame_ids):
                print(f"\n🎯 Processing frame {i+1}/{len(frame_ids)}: {frame_id}")
                print(f"⏱️  Progress: {((i+1)/len(frame_ids)*100):.1f}%")
                
                try:
                    # Get frame data using get_nodes() API
                    print(f"📡 Fetching frame data using get_nodes() API...")
                    frame_data = await self.figma_service.get_nodes(
                        file_id=file_key,
                        node_ids=[frame_id],
                        access_token=access_token
                    )
                    print(f"✅ Frame data received: {len(str(frame_data))} characters")
                    
                    # Process frame with LLM
                    print(f"🧠 Processing with LLM...")
                    frame_result = await self._process_single_frame(
                        frame_data=frame_data,
                        frame_id=frame_id,
                        user_message=user_message,
                        framework=framework,
                        backend_framework=backend_framework
                    )
                    
                    frame_results.append(frame_result)
                    
                    if frame_result.success:
                        print(f"✅ Frame '{frame_result.frame_name}' processed successfully!")
                        print(f"   ⏱️  Processing time: {frame_result.processing_time:.2f}s")
                        print(f"   🔢 Tokens used: {frame_result.tokens_used}")
                        
                        # Merge files
                        all_files["frontend"].update(frame_result.frontend_files)
                        all_files["backend"].update(frame_result.backend_files)
                        
                        print(f"   📁 Total files so far: {len(all_files['frontend']) + len(all_files['backend'])}")
                    else:
                        print(f"❌ Frame '{frame_result.frame_name}' failed: {frame_result.error}")
                        
                        # Update registry and tokens
                        if hasattr(frame_result, 'registry_entry'):
                            component_registry.update(frame_result.registry_entry)
                        if hasattr(frame_result, 'design_tokens'):
                            design_tokens.update(frame_result.design_tokens)
                    
                except Exception as e:
                    print(f"❌ Error processing frame {frame_id}: {str(e)}")
                    frame_results.append(FrameResult(
                        frame_id=frame_id,
                        frame_name="Unknown",
                        success=False,
                        frontend_files={},
                        backend_files={},
                        tokens_used=0,
                        processing_time=0,
                        error=str(e)
                    ))
            
            # Step 4: Generate project structure
            print(f"\n📁 Generating project structure...")
            project_files = await self._generate_project_structure(
                all_files, component_registry, design_tokens, framework, backend_framework
            )
            
            # Step 5: Create final result
            successful_frames = [r for r in frame_results if r.success]
            total_processing_time = sum(r.processing_time for r in frame_results)
            total_tokens = sum(r.tokens_used for r in frame_results)
            
            result = {
                "success": True,
                "project_id": f"figma_{file_key}_{int(datetime.now().timestamp())}",
                "frames_processed": len(successful_frames),
                "total_frames": len(frame_results),
                "files": project_files,
                "metadata": {
                    "framework": framework,
                    "backend_framework": backend_framework,
                    "processing_time": total_processing_time,
                    "total_tokens": total_tokens,
                    "frame_results": [
                        {
                            "frame_id": r.frame_id,
                            "frame_name": r.frame_name,
                            "success": r.success,
                            "tokens_used": r.tokens_used,
                            "processing_time": r.processing_time,
                            "error": r.error
                        } for r in frame_results
                    ]
                }
            }
            
            # Final summary logging
            print(f"\n🎉 PROCESSING COMPLETE!")
            print(f"=" * 60)
            print(f"📊 Summary:")
            print(f"   ✅ Successful frames: {len(successful_frames)}/{len(frame_results)}")
            print(f"   ⏱️  Total processing time: {total_processing_time:.2f}s")
            print(f"   🔢 Total tokens used: {total_tokens:,}")
            print(f"   📁 Total files generated: {len(project_files)}")
            print(f"   🎯 Average time per frame: {total_processing_time/len(frame_results):.2f}s")
            print(f"   🚀 Tokens per second: {total_tokens/total_processing_time:.0f}")
            print(f"=" * 60)
            
            return result
            
        except Exception as e:
            print(f"❌ Error in frame processing: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "files": {},
                "metadata": {}
            }
    
    async def _get_file_structure(self, file_key: str, access_token: str) -> Dict[str, Any]:
        """Get basic file structure to identify frames"""
        # We still need the full file to identify frames, but this is much smaller
        # than the processing we do later
        try:
            # Use the existing method to get file structure
            from app.services.figma_processor import FigmaProcessor
            processor = FigmaProcessor()
            return await processor.get_figma_json(file_key, access_token)
        except Exception as e:
            raise Exception(f"Failed to get file structure: {str(e)}")
    
    def _extract_node_ids_from_url(self, figma_url: str) -> List[str]:
        """Extract specific node IDs from prototype URL"""
        import re
        from urllib.parse import urlparse, parse_qs
        
        try:
            # Parse the URL
            parsed_url = urlparse(figma_url)
            query_params = parse_qs(parsed_url.query)
            
            node_ids = []
            
            # Extract node IDs from query parameters
            if 'node-id' in query_params:
                node_ids.extend(query_params['node-id'])
            
            if 'starting-point-node-id' in query_params:
                node_ids.extend(query_params['starting-point-node-id'])
            
            # Clean up the node IDs (remove URL encoding)
            cleaned_ids = []
            for node_id in node_ids:
                # Decode URL encoding
                cleaned_id = node_id.replace('%3A', ':')
                cleaned_ids.append(cleaned_id)
            
            print(f"🎯 Extracted node IDs from URL: {cleaned_ids}")
            return cleaned_ids
            
        except Exception as e:
            print(f"❌ Error extracting node IDs from URL: {str(e)}")
            return []
    
    def _extract_frame_ids(self, file_structure: Dict[str, Any]) -> List[str]:
        """Extract frame IDs from file structure"""
        frame_ids = []
        
        def find_frames(node: Dict[str, Any]):
            if node.get("type") == "FRAME":
                frame_ids.append(node.get("id"))
            
            for child in node.get("children", []):
                find_frames(child)
        
        document = file_structure.get("document", {})
        find_frames(document)
        
        return frame_ids
    
    async def _process_single_frame(
        self,
        frame_data: Dict[str, Any],
        frame_id: str,
        user_message: Optional[str],
        framework: str,
        backend_framework: str
    ) -> FrameResult:
        """Process a single frame with LLM"""
        start_time = datetime.now()
        
        try:
            # Extract frame information
            frame_name = self._extract_frame_name(frame_data)
            
            # Build prompt for this specific frame
            prompt = self._build_frame_prompt(
                frame_data=frame_data,
                frame_id=frame_id,
                frame_name=frame_name,
                user_message=user_message,
                framework=framework,
                backend_framework=backend_framework
            )
            
            # Generate code using LLM
            llm_request = {
                "prompt": prompt,
                "model": "gemini-2.5-pro",
                "max_tokens": 8000,  # Perfect size for single frame
                "temperature": 0.1
            }
            
            print(f"🤖 Sending prompt to LLM for frame: {frame_name}")
            print(f"📏 Prompt length: {len(prompt)} characters")
            
            response = await self.llm_service.generate_code(
                prompt=prompt,
                model="gemini-2.5-pro",
                max_tokens=8000,
                temperature=0.1
            )
            
            # Log the raw LLM response for debugging
            print(f"🎯 LLM Response for frame '{frame_name}' ({frame_id}):")
            print("=" * 80)
            print(response)
            print("=" * 80)
            print(f"📊 Response length: {len(response)} characters")
            
            # Parse generated code
            parsed_code = self._parse_generated_code(response)
            
            # Log parsed results
            print(f"📁 Parsed files for frame '{frame_name}':")
            print(f"   Frontend files: {len(parsed_code.get('frontend', {}))}")
            print(f"   Backend files: {len(parsed_code.get('backend', {}))}")
            
            # Show file paths
            for file_path in parsed_code.get('frontend', {}).keys():
                print(f"   📄 Frontend: {file_path}")
            for file_path in parsed_code.get('backend', {}).keys():
                print(f"   📄 Backend: {file_path}")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return FrameResult(
                frame_id=frame_id,
                frame_name=frame_name,
                success=True,
                frontend_files=parsed_code.get("frontend", {}),
                backend_files=parsed_code.get("backend", {}),
                tokens_used=len(prompt.split()) + len(response.split()),  # Approximate
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            return FrameResult(
                frame_id=frame_id,
                frame_name="Unknown",
                success=False,
                frontend_files={},
                backend_files={},
                tokens_used=0,
                processing_time=processing_time,
                error=str(e)
            )
    
    def _extract_frame_name(self, frame_data: Dict[str, Any]) -> str:
        """Extract frame name from frame data"""
        try:
            nodes = frame_data.get("nodes", {})
            for node_id, node in nodes.items():
                if node.get("type") == "FRAME":
                    return node.get("name", f"Frame_{node_id[:8]}")
            return "Unknown_Frame"
        except:
            return "Unknown_Frame"
    
    def _build_frame_prompt(
        self,
        frame_data: Dict[str, Any],
        frame_id: str,
        frame_name: str,
        user_message: Optional[str],
        framework: str,
        backend_framework: str
    ) -> str:
        """Build prompt for single frame processing"""
        
        prompt_parts = [
            f"# Generate {framework} Frontend + {backend_framework} Backend for Frame: {frame_name}",
            "",
            f"**Frame ID**: {frame_id}",
            f"**Frame Name**: {frame_name}",
            "",
            "## Frame Data (Complete JSON):",
            "```json",
            json.dumps(frame_data, indent=2),
            "```",
            "",
            "## Instructions:",
            "1. Generate clean, production-ready React/TypeScript frontend code",
            "2. Generate corresponding Node.js/Express backend API endpoints",
            "3. Include proper TypeScript types and interfaces",
            "4. Add responsive design with Tailwind CSS",
            "5. Include proper error handling and validation",
            "",
            "## Output Format:",
            "Return a JSON object with the following structure:",
            "```json",
            "{",
            '  "frontend": {',
            '    "path/to/component.tsx": "component code here"',
            "  },",
            '  "backend": {',
            '    "path/to/api.ts": "API code here"',
            "  },",
            '  "registryEntry": {',
            '    "componentName": "ComponentName",',
            '    "path": "src/components/ComponentName.tsx",',
            '    "variants": ["desktop", "mobile"],',
            '    "tokens": ["--color-primary", "--spacing-md"]',
            '    "screensUsed": ["FrameName"]',
            '    "dependencies": [],',
            '    "apiEndpoints": ["/api/endpoint"]',
            '    "lastGenerated": "2025-01-25T12:00:00Z"',
            "  }",
            "}",
            "```",
            ""
        ]
        
        if user_message:
            prompt_parts.extend([
                "## User Requirements:",
                user_message,
                ""
            ])
        
        return "\n".join(prompt_parts)
    
    def _parse_generated_code(self, code_text: str) -> Dict[str, Any]:
        """Parse generated code text into structured format"""
        print(f"🔍 Parsing generated code...")
        print(f"   📏 Code length: {len(code_text)} characters")
        print(f"   🔤 Starts with: {code_text[:50]}...")
        
        try:
            # Try to parse as JSON first
            if code_text.strip().startswith('{'):
                print(f"   📋 Detected JSON format, parsing...")
                parsed = json.loads(code_text)
                print(f"   ✅ JSON parsing successful!")
                print(f"   📁 Frontend files: {len(parsed.get('frontend', {}))}")
                print(f"   📁 Backend files: {len(parsed.get('backend', {}))}")
                return parsed
            
            # Look for JSON blocks in the text
            import re
            json_pattern = r'```json\s*(\{.*?\})\s*```'
            json_matches = re.findall(json_pattern, code_text, re.DOTALL)
            
            if json_matches:
                print(f"   📋 Found {len(json_matches)} JSON blocks in text")
                for i, json_block in enumerate(json_matches):
                    try:
                        parsed = json.loads(json_block)
                        print(f"   ✅ JSON block {i+1} parsed successfully!")
                        print(f"   📁 Frontend files: {len(parsed.get('frontend', {}))}")
                        print(f"   📁 Backend files: {len(parsed.get('backend', {}))}")
                        return parsed
                    except json.JSONDecodeError as e:
                        print(f"   ⚠️  JSON block {i+1} failed to parse: {str(e)}")
                        continue
            
            # If no JSON blocks found, try to extract from text format
            print(f"   📋 No JSON blocks found, trying text extraction...")
            result = {
                "frontend": {},
                "backend": {},
                "registryEntry": {}
            }
            
            # Look for file patterns like "File: path/to/file.tsx"
            file_pattern = r'File:\s*([^\n]+)\n```(?:tsx?|js|ts|json)?\n(.*?)\n```'
            file_matches = re.findall(file_pattern, code_text, re.DOTALL)
            
            print(f"   🔍 Found {len(file_matches)} file matches")
            
            for file_path, content in file_matches:
                file_path = file_path.strip()
                content = content.strip()
                
                # Determine if it's frontend or backend based on path
                if any(ext in file_path for ext in ['.tsx', '.jsx', '.css', '.scss']):
                    result["frontend"][file_path] = content
                    print(f"   📄 Frontend: {file_path}")
                elif any(ext in file_path for ext in ['.ts', '.js', '.py']):
                    result["backend"][file_path] = content
                    print(f"   📄 Backend: {file_path}")
                else:
                    # Default to frontend if unclear
                    result["frontend"][file_path] = content
                    print(f"   📄 Frontend (default): {file_path}")
            
            print(f"   ✅ Text parsing complete!")
            print(f"   📁 Frontend files: {len(result['frontend'])}")
            print(f"   📁 Backend files: {len(result['backend'])}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error parsing generated code: {str(e)}")
            print(f"   🔍 Code preview: {code_text[:200]}...")
            return {
                "frontend": {},
                "backend": {},
                "registryEntry": {}
            }
    
    async def _generate_project_structure(
        self,
        all_files: Dict[str, Dict[str, str]],
        component_registry: Dict[str, Any],
        design_tokens: Dict[str, Any],
        framework: str,
        backend_framework: str
    ) -> Dict[str, str]:
        """Generate final project structure following figma_fullstack.md structure"""
        
        project_files = {}
        
        # Organize frontend files according to figma_fullstack.md structure
        for file_path, content in all_files.get("frontend", {}).items():
            # Ensure proper frontend structure
            if not file_path.startswith("src/"):
                file_path = f"src/{file_path}"
            
            # Categorize files by type
            if "components/" in file_path:
                project_files[f"frontend/{file_path}"] = content
            elif "pages/" in file_path:
                project_files[f"frontend/{file_path}"] = content
            elif "hooks/" in file_path:
                project_files[f"frontend/{file_path}"] = content
            elif "context/" in file_path:
                project_files[f"frontend/{file_path}"] = content
            elif "services/" in file_path:
                project_files[f"frontend/{file_path}"] = content
            elif "types/" in file_path:
                project_files[f"frontend/{file_path}"] = content
            elif "utils/" in file_path:
                project_files[f"frontend/{file_path}"] = content
            elif "styles/" in file_path:
                project_files[f"frontend/{file_path}"] = content
            elif file_path.endswith("App.tsx") or file_path.endswith("index.tsx"):
                project_files[f"frontend/{file_path}"] = content
            else:
                # Default to components if unclear
                project_files[f"frontend/src/components/{file_path}"] = content
        
        # Organize backend files according to figma_fullstack.md structure
        for file_path, content in all_files.get("backend", {}).items():
            # Ensure proper backend structure
            if not file_path.startswith("src/"):
                file_path = f"src/{file_path}"
            
            # Categorize files by type
            if "routes/" in file_path:
                project_files[f"backend/{file_path}"] = content
            elif "controllers/" in file_path:
                project_files[f"backend/{file_path}"] = content
            elif "services/" in file_path:
                project_files[f"backend/{file_path}"] = content
            elif "models/" in file_path:
                project_files[f"backend/{file_path}"] = content
            elif "middleware/" in file_path:
                project_files[f"backend/{file_path}"] = content
            elif "utils/" in file_path:
                project_files[f"backend/{file_path}"] = content
            elif "types/" in file_path:
                project_files[f"backend/{file_path}"] = content
            elif file_path.endswith("server.ts") or file_path.endswith("app.ts"):
                project_files[f"backend/{file_path}"] = content
            else:
                # Default to routes if unclear
                project_files[f"backend/src/routes/{file_path}"] = content
        
        # Add shared types if any
        shared_types = {}
        for file_path, content in all_files.get("frontend", {}).items():
            if "types/" in file_path and file_path.endswith(".ts"):
                shared_types[f"shared/types/{file_path.split('/')[-1]}"] = content
        
        for file_path, content in all_files.get("backend", {}).items():
            if "types/" in file_path and file_path.endswith(".ts"):
                shared_types[f"shared/types/{file_path.split('/')[-1]}"] = content
        
        project_files.update(shared_types)
        
        # Add project configuration files
        project_files.update({
            "frontend/package.json": self._generate_frontend_package_json(framework),
            "backend/package.json": self._generate_backend_package_json(backend_framework),
            "docker-compose.yml": self._generate_docker_compose(),
            "README.md": self._generate_readme(),
            "component-registry.json": json.dumps(component_registry, indent=2),
            "design-tokens.json": json.dumps(design_tokens, indent=2)
        })
        
        return project_files
    
    def _generate_frontend_package_json(self, framework: str) -> str:
        """Generate frontend package.json"""
        return json.dumps({
            "name": "figma-frontend",
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "tsc && vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.8.0",
                "lucide-react": "^0.263.1",
                "axios": "^1.3.0"
            },
            "devDependencies": {
                "@types/react": "^18.0.28",
                "@types/react-dom": "^18.0.11",
                "@vitejs/plugin-react": "^3.1.0",
                "typescript": "^4.9.3",
                "vite": "^4.1.0",
                "tailwindcss": "^3.2.7",
                "autoprefixer": "^10.4.14",
                "postcss": "^8.4.21"
            }
        }, indent=2)
    
    def _generate_backend_package_json(self, backend_framework: str) -> str:
        """Generate backend package.json"""
        return json.dumps({
            "name": "figma-backend",
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "dev": "tsx watch src/server.ts",
                "build": "tsc",
                "start": "node dist/server.js"
            },
            "dependencies": {
                "express": "^4.18.2",
                "cors": "^2.8.5",
                "helmet": "^6.0.1",
                "jsonwebtoken": "^9.0.0",
                "bcryptjs": "^2.4.3",
                "prisma": "^4.11.0",
                "@prisma/client": "^4.11.0",
                "winston": "^3.8.2"
            },
            "devDependencies": {
                "@types/express": "^4.17.17",
                "@types/cors": "^2.8.13",
                "@types/jsonwebtoken": "^9.0.1",
                "@types/bcryptjs": "^2.4.2",
                "typescript": "^4.9.5",
                "tsx": "^3.12.0"
            }
        }, indent=2)
    
    def _generate_docker_compose(self) -> str:
        """Generate docker-compose.yml"""
        return """version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
    volumes:
      - ./frontend:/app
      - /app/node_modules
  
  backend:
    build: ./backend
    ports:
      - "3001:3001"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://user:password@db:5432/figma_app
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=figma_app
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
"""
    
    def _generate_readme(self) -> str:
        """Generate README for the project"""
        return """# Figma Generated Application

This application was generated from a Figma design using AI.

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start development servers:
   ```bash
   npm run dev
   ```

3. Open your browser to see the application.

## Project Structure

- `frontend/` - React/TypeScript frontend
- `backend/` - Node.js/Express backend
- `component-registry.json` - Component registry
- `design-tokens.json` - Design tokens

## Generated Components

This project includes components generated from your Figma design frames.
"""
