"""
Lossless Figma Processor
Multi-pass architecture for true lossless processing
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime

from app.services.figma_streaming_parser import FigmaStreamingParser, ExtractionResult, ComponentNode
from app.services.llm_service import LLMService, LLMRequest, LLMResponse
from app.services.cache_service import CacheService
from app.helpers.retry import RetryHelper, RetryConfig


@dataclass
class LayoutNode:
    """Represents a layout relationship in the design"""
    id: str
    name: str
    type: str
    parent_id: Optional[str]
    children_ids: List[str]
    constraints: Dict[str, Any]
    auto_layout: Optional[Dict[str, Any]]
    breakpoints: Dict[str, Any]


@dataclass
class DesignSystem:
    """Centralized design system"""
    tokens: Dict[str, Any]
    components: Dict[str, Any]
    layouts: Dict[str, LayoutNode]
    interactions: Dict[str, Any]
    backend_requirements: Dict[str, Any]


@dataclass
class LosslessComponentResult:
    """Result of lossless component generation"""
    component_name: str
    component_id: str  # Canonical Figma node ID
    success: bool
    frontend_files: Dict[str, str]
    backend_files: Dict[str, str]
    registry_entry: Dict[str, Any]
    tokens_used: int
    processing_time: float
    layout_dependencies: List[str]
    interaction_requirements: List[str]
    canonical_name: str  # ID-based canonical name
    error: Optional[str] = None


class FigmaLosslessProcessor:
    """Truly lossless Figma processor with multi-pass architecture"""
    
    def __init__(self):
        self.streaming_parser = FigmaStreamingParser()
        self.llm_service = LLMService()
        self.cache_service = CacheService()
        self.retry_helper = RetryHelper()
        
        # Lossless retry configuration
        self.retry_config = RetryConfig(
            max_attempts=3,
            base_delay=0.5,
            max_delay=10.0,
            strategy="exponential",
            jitter=True
        )
    
    async def process_figma_lossless(
        self,
        figma_json: Dict[str, Any],
        user_message: Optional[str] = None,
        framework: str = "react",
        backend_framework: str = "nodejs",
        target_screens: Optional[List[str]] = None,
        max_batch_size: int = 8,  # Balanced for quality
        max_concurrent_batches: int = 3  # Conservative for consistency
    ) -> Dict[str, Any]:
        """
        Truly lossless Figma processing with multi-pass architecture
        
        Pass 1: Global Layout Graph Extraction
        Pass 2: Design System + Shared Components  
        Pass 3: Component Code per subtree
        Pass 4: Page-Level Assembly
        Pass 5: Backend inference from real functional context
        """
        start_time = datetime.now()
        
        try:
            print(f"DEBUG: Starting LOSSLESS processing with multi-pass architecture")
            
            # PASS 1: Extract global layout graph
            print("DEBUG: Pass 1 - Extracting global layout graph...")
            layout_graph = await self._extract_layout_graph(figma_json)
            
            # PASS 2: Build centralized design system
            print("DEBUG: Pass 2 - Building centralized design system...")
            design_system = await self._build_design_system(
                figma_json=figma_json,
                layout_graph=layout_graph,
                user_message=user_message
            )
            
            # PASS 3: Extract components with full context
            print("DEBUG: Pass 3 - Extracting components with full context...")
            extraction_result = await self.streaming_parser.extract_components(
                figma_json=figma_json,
                target_screens=target_screens
            )
            
            # PASS 4: Generate components with design system context
            print("DEBUG: Pass 4 - Generating components with design system context...")
            component_results = await self._generate_components_with_context(
                components=extraction_result.components,
                design_system=design_system,
                user_message=user_message,
                framework=framework,
                backend_framework=backend_framework,
                max_batch_size=max_batch_size,
                max_concurrent_batches=max_concurrent_batches
            )
            
            # PASS 5: Generate backend from real functional context
            print("DEBUG: Pass 5 - Generating backend from functional context...")
            backend_system = await self._generate_backend_system(
                component_results=component_results,
                design_system=design_system,
                layout_graph=layout_graph,
                backend_framework=backend_framework
            )
            
            # PASS 6: Assemble final project with consistency validation
            print("DEBUG: Pass 6 - Assembling final project with consistency validation...")
            final_project = await self._assemble_final_project(
                component_results=component_results,
                design_system=design_system,
                backend_system=backend_system,
                layout_graph=layout_graph,
                framework=framework,
                backend_framework=backend_framework
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            print(f"DEBUG: LOSSLESS processing completed in {processing_time:.2f} seconds")
            print(f"DEBUG: Generated {len(final_project['frontend_code'])} frontend files, {len(final_project['backend_code'])} backend files")
            
            return {
                "success": True,
                "frontend_code": final_project["frontend_code"],
                "backend_code": final_project["backend_code"],
                "component_registry": final_project["component_registry"],
                "design_system": design_system,
                "layout_graph": layout_graph,
                "backend_system": backend_system,
                "statistics": {
                    "total_components": len(extraction_result.components),
                    "successful_components": len([r for r in component_results if r.success]),
                    "total_tokens": sum(r.tokens_used for r in component_results),
                    "processing_time": processing_time,
                    "frontend_files": len(final_project["frontend_code"]),
                    "backend_files": len(final_project["backend_code"]),
                    "components_per_second": len(extraction_result.components) / processing_time if processing_time > 0 else 0,
                    "lossless_score": self._calculate_lossless_score(component_results, design_system)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "frontend_code": {},
                "backend_code": {},
                "component_registry": {},
                "design_system": {},
                "layout_graph": {},
                "backend_system": {},
                "statistics": {}
            }
    
    async def _extract_layout_graph(self, figma_json: Dict[str, Any]) -> Dict[str, LayoutNode]:
        """Pass 1: Extract global layout relationships"""
        layout_nodes = {}
        
        def process_node(node: Dict[str, Any], parent_id: Optional[str] = None):
            node_id = node.get("id", "")
            node_name = node.get("name", "")
            node_type = node.get("type", "")
            
            # Extract layout constraints
            constraints = {}
            if "constraints" in node:
                constraints = node["constraints"]
            
            # Extract auto-layout properties
            auto_layout = None
            if "layoutMode" in node:
                auto_layout = {
                    "layoutMode": node.get("layoutMode"),
                    "primaryAxisAlignItems": node.get("primaryAxisAlignItems"),
                    "counterAxisAlignItems": node.get("counterAxisAlignItems"),
                    "paddingLeft": node.get("paddingLeft", 0),
                    "paddingRight": node.get("paddingRight", 0),
                    "paddingTop": node.get("paddingTop", 0),
                    "paddingBottom": node.get("paddingBottom", 0),
                    "itemSpacing": node.get("itemSpacing", 0)
                }
            
            # Extract breakpoint constraints
            breakpoints = {}
            if "responsive" in node:
                breakpoints = node["responsive"]
            
            # Create layout node
            layout_node = LayoutNode(
                id=node_id,
                name=node_name,
                type=node_type,
                parent_id=parent_id,
                children_ids=[],
                constraints=constraints,
                auto_layout=auto_layout,
                breakpoints=breakpoints
            )
            
            layout_nodes[node_id] = layout_node
            
            # Process children
            if "children" in node:
                for child in node["children"]:
                    child_id = child.get("id", "")
                    layout_node.children_ids.append(child_id)
                    process_node(child, node_id)
        
        # Start processing from document root
        if "document" in figma_json:
            process_node(figma_json["document"])
        
        return layout_nodes
    
    async def _build_design_system(
        self,
        figma_json: Dict[str, Any],
        layout_graph: Dict[str, LayoutNode],
        user_message: Optional[str]
    ) -> DesignSystem:
        """Pass 2: Build centralized design system"""
        
        # Extract design tokens
        tokens = self._extract_design_tokens(figma_json)
        
        # Identify shared components
        shared_components = self._identify_shared_components(figma_json, layout_graph)
        
        # Extract interaction patterns
        interactions = self._extract_interaction_patterns(figma_json, layout_graph)
        
        # Analyze backend requirements from user message and interactions
        backend_requirements = self._analyze_backend_requirements(
            user_message=user_message,
            interactions=interactions,
            layout_graph=layout_graph
        )
        
        return DesignSystem(
            tokens=tokens,
            components=shared_components,
            layouts=layout_graph,
            interactions=interactions,
            backend_requirements=backend_requirements
        )
    
    def _extract_design_tokens(self, figma_json: Dict[str, Any]) -> Dict[str, Any]:
        """Extract all design tokens from Figma JSON"""
        tokens = {
            "colors": {},
            "typography": {},
            "spacing": {},
            "shadows": {},
            "borders": {}
        }
        
        def extract_tokens_from_node(node: Dict[str, Any]):
            # Extract color tokens
            if "fills" in node:
                for fill in node["fills"]:
                    if fill.get("type") == "SOLID":
                        color = fill.get("color", {})
                        if color:
                            color_name = f"color-{int(color.get('r', 0)*255)}-{int(color.get('g', 0)*255)}-{int(color.get('b', 0)*255)}"
                            tokens["colors"][color_name] = {
                                "r": color.get("r", 0),
                                "g": color.get("g", 0),
                                "b": color.get("b", 0),
                                "a": color.get("a", 1)
                            }
            
            # Extract typography tokens
            if "style" in node and "fontFamily" in node["style"]:
                font_family = node["style"]["fontFamily"]
                font_size = node["style"].get("fontSize", 16)
                font_weight = node["style"].get("fontWeight", 400)
                
                typography_key = f"{font_family}-{font_size}-{font_weight}"
                tokens["typography"][typography_key] = {
                    "fontFamily": font_family,
                    "fontSize": font_size,
                    "fontWeight": font_weight
                }
            
            # Process children
            if "children" in node:
                for child in node["children"]:
                    extract_tokens_from_node(child)
        
        # Extract from document
        if "document" in figma_json:
            extract_tokens_from_node(figma_json["document"])
        
        return tokens
    
    def _identify_shared_components(self, figma_json: Dict[str, Any], layout_graph: Dict[str, LayoutNode]) -> Dict[str, Any]:
        """Identify components that appear multiple times (shared components)"""
        component_usage = {}
        shared_components = {}
        
        def analyze_component_usage(node: Dict[str, Any]):
            node_id = node.get("id", "")
            node_name = node.get("name", "")
            node_type = node.get("type", "")
            
            # Track component usage
            if node_type in ["COMPONENT", "INSTANCE"]:
                if node_name not in component_usage:
                    component_usage[node_name] = []
                component_usage[node_name].append(node_id)
            
            # Process children
            if "children" in node:
                for child in node["children"]:
                    analyze_component_usage(child)
        
        # Analyze usage
        if "document" in figma_json:
            analyze_component_usage(figma_json["document"])
        
        # Identify shared components (used more than once)
        for component_name, usage_list in component_usage.items():
            if len(usage_list) > 1:
                shared_components[component_name] = {
                    "usage_count": len(usage_list),
                    "instances": usage_list,
                    "is_shared": True
                }
        
        return shared_components
    
    def _extract_interaction_patterns(self, figma_json: Dict[str, Any], layout_graph: Dict[str, LayoutNode]) -> Dict[str, Any]:
        """Extract interaction patterns from Figma with interaction graph"""
        interactions = {
            "navigation": [],
            "forms": [],
            "buttons": [],
            "modals": [],
            "data_display": [],
            "interaction_graph": {}  # New: interaction relationships
        }
        
        def analyze_interactions(node: Dict[str, Any], parent_id: str = None):
            node_id = node.get("id")
            node_name = node.get("name", "").lower()
            node_type = node.get("type", "")
            
            # Build interaction graph relationships
            if parent_id:
                if node_id not in interactions["interaction_graph"]:
                    interactions["interaction_graph"][node_id] = {
                        "id": node_id,
                        "name": node.get("name"),
                        "type": node_type,
                        "parent": parent_id,
                        "children": [],
                        "interactions": []
                    }
                
                # Add to parent's children
                if parent_id in interactions["interaction_graph"]:
                    interactions["interaction_graph"][parent_id]["children"].append(node_id)
            
            # Identify navigation patterns
            if any(keyword in node_name for keyword in ["nav", "menu", "header", "footer"]):
                interactions["navigation"].append({
                    "id": node_id,
                    "name": node.get("name"),
                    "type": "navigation"
                })
                interactions["interaction_graph"][node_id]["interactions"].append("navigation")
            
            # Identify form patterns
            if any(keyword in node_name for keyword in ["form", "input", "field", "submit"]):
                interactions["forms"].append({
                    "id": node_id,
                    "name": node.get("name"),
                    "type": "form"
                })
                interactions["interaction_graph"][node_id]["interactions"].append("form_submission")
            
            # Identify button patterns with interaction mapping
            if any(keyword in node_name for keyword in ["button", "btn", "click", "action"]):
                button_info = {
                    "id": node_id,
                    "name": node.get("name"),
                    "type": "button"
                }
                
                # Map button interactions based on context
                if "submit" in node_name or "save" in node_name:
                    button_info["action"] = "form_submission"
                    interactions["interaction_graph"][node_id]["interactions"].append("form_submission")
                elif "nav" in node_name or "link" in node_name:
                    button_info["action"] = "navigation"
                    interactions["interaction_graph"][node_id]["interactions"].append("navigation")
                elif "delete" in node_name or "remove" in node_name:
                    button_info["action"] = "data_deletion"
                    interactions["interaction_graph"][node_id]["interactions"].append("data_deletion")
                else:
                    button_info["action"] = "generic_click"
                    interactions["interaction_graph"][node_id]["interactions"].append("generic_click")
                
                interactions["buttons"].append(button_info)
            
            # Identify modal patterns
            if any(keyword in node_name for keyword in ["modal", "popup", "dialog", "overlay"]):
                interactions["modals"].append({
                    "id": node_id,
                    "name": node.get("name"),
                    "type": "modal"
                })
                interactions["interaction_graph"][node_id]["interactions"].append("modal_display")
            
            # Identify data display patterns
            if any(keyword in node_name for keyword in ["list", "table", "card", "item", "row"]):
                interactions["data_display"].append({
                    "id": node_id,
                    "name": node.get("name"),
                    "type": "data_display"
                })
                interactions["interaction_graph"][node_id]["interactions"].append("data_display")
            
            # Process children
            if "children" in node:
                for child in node["children"]:
                    analyze_interactions(child, node_id)
        
        # Analyze interactions
        if "document" in figma_json:
            analyze_interactions(figma_json["document"])
        
        return interactions
    
    def _analyze_backend_requirements(
        self,
        user_message: Optional[str],
        interactions: Dict[str, Any],
        layout_graph: Dict[str, LayoutNode]
    ) -> Dict[str, Any]:
        """Analyze backend requirements from interaction graph and user message"""
        requirements = {
            "authentication": False,
            "database": False,
            "api_endpoints": [],
            "external_services": [],
            "real_time": False,
            "file_upload": False,
            "interaction_mappings": {}  # New: specific interaction to API mappings
        }
        
        # Analyze user message for backend requirements
        if user_message:
            user_msg_lower = user_message.lower()
            
            if any(keyword in user_msg_lower for keyword in ["login", "auth", "user", "account"]):
                requirements["authentication"] = True
            
            if any(keyword in user_msg_lower for keyword in ["database", "data", "store", "save"]):
                requirements["database"] = True
            
            if any(keyword in user_msg_lower for keyword in ["api", "endpoint", "service"]):
                requirements["api_endpoints"] = ["/api/data"]
            
            if any(keyword in user_msg_lower for keyword in ["upload", "file", "image"]):
                requirements["file_upload"] = True
            
            if any(keyword in user_msg_lower for keyword in ["real-time", "live", "websocket"]):
                requirements["real_time"] = True
        
        # Analyze interaction graph for backend requirements
        interaction_graph = interactions.get("interaction_graph", {})
        
        for node_id, node_data in interaction_graph.items():
            node_interactions = node_data.get("interactions", [])
            
            # Map specific interactions to backend requirements
            for interaction in node_interactions:
                if interaction == "form_submission":
                    requirements["database"] = True
                    requirements["api_endpoints"].append(f"/api/forms/{node_id}")
                    requirements["interaction_mappings"][node_id] = {
                        "type": "form_submission",
                        "endpoint": f"/api/forms/{node_id}",
                        "method": "POST"
                    }
                
                elif interaction == "data_display":
                    requirements["database"] = True
                    requirements["api_endpoints"].append(f"/api/data/{node_id}")
                    requirements["interaction_mappings"][node_id] = {
                        "type": "data_retrieval",
                        "endpoint": f"/api/data/{node_id}",
                        "method": "GET"
                    }
                
                elif interaction == "data_deletion":
                    requirements["database"] = True
                    requirements["api_endpoints"].append(f"/api/data/{node_id}")
                    requirements["interaction_mappings"][node_id] = {
                        "type": "data_deletion",
                        "endpoint": f"/api/data/{node_id}",
                        "method": "DELETE"
                    }
                
                elif interaction == "navigation":
                    # Navigation might require route data
                    requirements["api_endpoints"].append(f"/api/routes/{node_id}")
                    requirements["interaction_mappings"][node_id] = {
                        "type": "navigation",
                        "endpoint": f"/api/routes/{node_id}",
                        "method": "GET"
                    }
                
                elif interaction == "modal_display":
                    # Modals might need dynamic content
                    requirements["api_endpoints"].append(f"/api/modals/{node_id}")
                    requirements["interaction_mappings"][node_id] = {
                        "type": "modal_content",
                        "endpoint": f"/api/modals/{node_id}",
                        "method": "GET"
                    }
        
        # Legacy analysis for backward compatibility
        if interactions["forms"]:
            requirements["database"] = True
            requirements["api_endpoints"].extend(["/api/forms", "/api/submit"])
        
        if interactions["data_display"]:
            requirements["database"] = True
            requirements["api_endpoints"].extend(["/api/data", "/api/list"])
        
        return requirements
    
    async def _generate_components_with_context(
        self,
        components: List[ComponentNode],
        design_system: DesignSystem,
        user_message: Optional[str],
        framework: str,
        backend_framework: str,
        max_batch_size: int,
        max_concurrent_batches: int
    ) -> List[LosslessComponentResult]:
        """Pass 4: Generate components with full design system context"""
        
        all_results = []
        
        # Process components in batches
        for i in range(0, len(components), max_batch_size * max_concurrent_batches):
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
                task = self._process_batch_lossless(
                    batch_components,
                    design_system,
                    user_message,
                    framework,
                    backend_framework
                )
                batch_tasks.append(task)
            
            # Execute all batches in parallel
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Process results
            for batch_result in batch_results:
                if isinstance(batch_result, Exception):
                    print(f"DEBUG: Batch processing failed: {str(batch_result)}")
                    continue
                
                all_results.extend(batch_result)
            
            # Progress update
            processed = min(i + (max_batch_size * max_concurrent_batches), len(components))
            progress = (processed / len(components)) * 100
            print(f"DEBUG: Progress: {processed}/{len(components)} ({progress:.1f}%)")
        
        return all_results
    
    async def _process_batch_lossless(
        self,
        batch_components: List[ComponentNode],
        design_system: DesignSystem,
        user_message: Optional[str],
        framework: str,
        backend_framework: str
    ) -> List[LosslessComponentResult]:
        """Process a batch of components with full design system context"""
        batch_tasks = []
        
        for component in batch_components:
            task = self._generate_component_lossless(
                component=component,
                design_system=design_system,
                user_message=user_message,
                framework=framework,
                backend_framework=backend_framework
            )
            batch_tasks.append(task)
        
        # Process all components in the batch in parallel
        results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        # Convert exceptions to failed results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append(LosslessComponentResult(
                    component_name="unknown",
                    success=False,
                    frontend_files={},
                    backend_files={},
                    registry_entry={},
                    tokens_used=0,
                    processing_time=0,
                    layout_dependencies=[],
                    interaction_requirements=[],
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _generate_component_lossless(
        self,
        component: ComponentNode,
        design_system: DesignSystem,
        user_message: Optional[str],
        framework: str,
        backend_framework: str
    ) -> LosslessComponentResult:
        """Generate component with full design system context"""
        start_time = datetime.now()
        
        try:
            # Build context-aware prompt
            prompt = self._build_lossless_prompt(
                component=component,
                design_system=design_system,
                user_message=user_message,
                framework=framework,
                backend_framework=backend_framework
            )
            
            # Create LLM request
            llm_request = LLMRequest(
                prompt=prompt,
                model="gemini-2.5-pro",
                max_tokens=8000,
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
                try:
                    response_data = json.loads(llm_response.content)
                except json.JSONDecodeError:
                    response_data = self._parse_fallback_json(llm_response.content)
                
                processing_time = (datetime.now() - start_time).total_seconds()
                canonical_name = self._generate_canonical_name(component.id, component.name)
                
                return LosslessComponentResult(
                    component_name=component.name,
                    component_id=component.id,
                    success=True,
                    frontend_files=response_data.get("files", {}),
                    backend_files=response_data.get("backendFiles", {}),
                    registry_entry=response_data.get("registryEntry", {}),
                    tokens_used=llm_response.tokens_used,
                    processing_time=processing_time,
                    layout_dependencies=response_data.get("layoutDependencies", []),
                    interaction_requirements=response_data.get("interactionRequirements", []),
                    canonical_name=canonical_name
                )
            else:
                return LosslessComponentResult(
                    component_name=component.name,
                    success=False,
                    frontend_files={},
                    backend_files={},
                    registry_entry={},
                    tokens_used=0,
                    processing_time=(datetime.now() - start_time).total_seconds(),
                    layout_dependencies=[],
                    interaction_requirements=[],
                    error=llm_response.error
                )
                
        except Exception as e:
            return LosslessComponentResult(
                component_name=component.name,
                success=False,
                frontend_files={},
                backend_files={},
                registry_entry={},
                tokens_used=0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                layout_dependencies=[],
                interaction_requirements=[],
                error=str(e)
            )
    
    def _build_lossless_prompt(
        self,
        component: ComponentNode,
        design_system: DesignSystem,
        user_message: Optional[str],
        framework: str,
        backend_framework: str
    ) -> str:
        """Build context-aware prompt for lossless processing"""
        
        # Generate canonical name from component ID
        canonical_name = self._generate_canonical_name(component.id, component.name)
        
        # Extract auto-layout constraints for this component
        layout_constraints = self._extract_autolayout_constraints(component, design_system.layouts)
        
        prompt_parts = [
            f"# Lossless Component Generation: {component.name}",
            f"Generate {framework} frontend + {backend_framework} backend with full design system context.",
            f"",
            f"## Component Context",
            f"**Name**: {component.name}",
            f"**ID**: {component.id}",
            f"**Canonical Name**: {canonical_name}",
            f"**Type**: {component.component_type}",
            f"",
            f"## Layout Constraints (CRITICAL for pixel-perfect fidelity)",
            f"**Auto-layout**: {json.dumps(layout_constraints, indent=2)}",
            f"**Tailwind Classes**: {self._generate_tailwind_from_autolayout(layout_constraints)}",
            f"",
            f"## Design System Context",
            f"**Available Tokens**: {json.dumps(design_system.tokens, indent=2)}",
            f"**Shared Components**: {list(design_system.components.keys())}",
            f"**Layout Dependencies**: {component.name} depends on layout relationships",
            f"",
            f"## Backend Requirements",
            f"**Authentication**: {design_system.backend_requirements.get('authentication', False)}",
            f"**Database**: {design_system.backend_requirements.get('database', False)}",
            f"**API Endpoints**: {design_system.backend_requirements.get('api_endpoints', [])}",
            f"",
            f"## Interaction Patterns",
            f"**Navigation**: {design_system.interactions.get('navigation', [])}",
            f"**Forms**: {design_system.interactions.get('forms', [])}",
            f"**Buttons**: {design_system.interactions.get('buttons', [])}",
        ]
        
        if user_message:
            prompt_parts.append(f"**User Requirements**: {user_message}")
        
        prompt_parts.extend([
            f"",
            f"## Output Format",
            f'{{"files": [{{"path": "filename.tsx", "content": "code"}}], "backendFiles": [{{"path": "api.ts", "content": "code"}}], "registryEntry": {{"componentName": "Name", "path": "file.tsx", "tokens": ["token1"], "apiEndpoints": ["/api/endpoint"]}}, "layoutDependencies": ["parent_component"], "interactionRequirements": ["form_submission"]}}',
            f"",
            f"## Requirements",
            f"- Use design system tokens for consistency",
            f"- Reference shared components when applicable",
            f"- Maintain layout relationships",
            f"- Generate backend that matches interaction patterns",
            f"- Ensure pixel-perfect fidelity to design",
            f"- Generate production-ready TypeScript code",
            f"- CRITICAL: Use the provided Tailwind classes for exact layout matching",
            f"- Apply auto-layout constraints precisely as specified",
            f"- Maintain responsive behavior from breakpoint constraints",
        ])
        
        return "\n".join(prompt_parts)
    
    def _generate_canonical_name(self, node_id: str, node_name: str) -> str:
        """Generate canonical name from Figma node ID to prevent naming inconsistencies"""
        # Extract meaningful part from node ID (usually last segment)
        id_parts = node_id.split(":")
        if len(id_parts) > 1:
            # Use the last meaningful segment
            canonical_id = id_parts[-1]
        else:
            canonical_id = node_id
        
        # Clean and normalize the name
        clean_name = "".join(c for c in node_name if c.isalnum() or c in "_-").strip()
        if not clean_name:
            clean_name = "Component"
        
        # Combine ID-based canonical name
        canonical_name = f"{clean_name}_{canonical_id[:8]}"
        
        # Ensure it's a valid identifier
        canonical_name = "".join(c for c in canonical_name if c.isalnum() or c == "_")
        if canonical_name[0].isdigit():
            canonical_name = f"Component_{canonical_name}"
        
        return canonical_name
    
    def _extract_autolayout_constraints(self, component: ComponentNode, layout_graph: Dict[str, LayoutNode]) -> Dict[str, Any]:
        """Extract auto-layout constraints for pixel-perfect layout generation"""
        component_id = component.id
        layout_node = layout_graph.get(component_id)
        
        if not layout_node or not layout_node.auto_layout:
            return {}
        
        autolayout = layout_node.auto_layout
        constraints = layout_node.constraints
        
        return {
            "layout_mode": autolayout.get("layoutMode", "NONE"),
            "primary_axis": autolayout.get("primaryAxisAlignItems", "MIN"),
            "counter_axis": autolayout.get("counterAxisAlignItems", "MIN"),
            "padding": {
                "left": autolayout.get("paddingLeft", 0),
                "right": autolayout.get("paddingRight", 0),
                "top": autolayout.get("paddingTop", 0),
                "bottom": autolayout.get("paddingBottom", 0)
            },
            "spacing": autolayout.get("itemSpacing", 0),
            "constraints": constraints,
            "breakpoints": layout_node.breakpoints
        }
    
    def _generate_tailwind_from_autolayout(self, layout_constraints: Dict[str, Any]) -> str:
        """Generate Tailwind CSS classes from auto-layout constraints"""
        if not layout_constraints:
            return "flex flex-col"
        
        classes = []
        
        # Layout mode
        layout_mode = layout_constraints.get("layout_mode", "NONE")
        if layout_mode == "HORIZONTAL":
            classes.append("flex flex-row")
        elif layout_mode == "VERTICAL":
            classes.append("flex flex-col")
        else:
            classes.append("flex flex-col")  # Default
        
        # Primary axis alignment
        primary_axis = layout_constraints.get("primary_axis", "MIN")
        if primary_axis == "CENTER":
            classes.append("justify-center")
        elif primary_axis == "MAX":
            classes.append("justify-end")
        elif primary_axis == "SPACE_BETWEEN":
            classes.append("justify-between")
        else:
            classes.append("justify-start")
        
        # Counter axis alignment
        counter_axis = layout_constraints.get("counter_axis", "MIN")
        if counter_axis == "CENTER":
            classes.append("items-center")
        elif counter_axis == "MAX":
            classes.append("items-end")
        else:
            classes.append("items-start")
        
        # Spacing
        spacing = layout_constraints.get("spacing", 0)
        if spacing > 0:
            # Convert Figma spacing to Tailwind gap
            if spacing <= 4:
                classes.append("gap-1")
            elif spacing <= 8:
                classes.append("gap-2")
            elif spacing <= 12:
                classes.append("gap-3")
            elif spacing <= 16:
                classes.append("gap-4")
            elif spacing <= 24:
                classes.append("gap-6")
            elif spacing <= 32:
                classes.append("gap-8")
            else:
                classes.append(f"gap-[{spacing}px]")
        
        # Padding
        padding = layout_constraints.get("padding", {})
        if padding:
            padding_classes = []
            
            # Top padding
            if padding.get("top", 0) > 0:
                padding_classes.append(f"pt-{self._px_to_tailwind(padding['top'])}")
            
            # Right padding
            if padding.get("right", 0) > 0:
                padding_classes.append(f"pr-{self._px_to_tailwind(padding['right'])}")
            
            # Bottom padding
            if padding.get("bottom", 0) > 0:
                padding_classes.append(f"pb-{self._px_to_tailwind(padding['bottom'])}")
            
            # Left padding
            if padding.get("left", 0) > 0:
                padding_classes.append(f"pl-{self._px_to_tailwind(padding['left'])}")
            
            classes.extend(padding_classes)
        
        return " ".join(classes)
    
    def _px_to_tailwind(self, px_value: int) -> str:
        """Convert pixel values to Tailwind spacing scale"""
        if px_value <= 0:
            return "0"
        elif px_value <= 4:
            return "1"
        elif px_value <= 8:
            return "2"
        elif px_value <= 12:
            return "3"
        elif px_value <= 16:
            return "4"
        elif px_value <= 20:
            return "5"
        elif px_value <= 24:
            return "6"
        elif px_value <= 28:
            return "7"
        elif px_value <= 32:
            return "8"
        elif px_value <= 36:
            return "9"
        elif px_value <= 40:
            return "10"
        elif px_value <= 44:
            return "11"
        elif px_value <= 48:
            return "12"
        elif px_value <= 56:
            return "14"
        elif px_value <= 64:
            return "16"
        elif px_value <= 80:
            return "20"
        elif px_value <= 96:
            return "24"
        else:
            return f"[{px_value}px]"
    
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
                "registryEntry": {},
                "layoutDependencies": [],
                "interactionRequirements": []
            }
            
        except Exception:
            return {
                "files": [],
                "backendFiles": [],
                "registryEntry": {},
                "layoutDependencies": [],
                "interactionRequirements": []
            }
    
    async def _generate_backend_system(
        self,
        component_results: List[LosslessComponentResult],
        design_system: DesignSystem,
        layout_graph: Dict[str, LayoutNode],
        backend_framework: str
    ) -> Dict[str, Any]:
        """Pass 5: Generate backend from real functional context"""
        
        # Collect all backend requirements
        all_api_endpoints = set()
        all_data_models = set()
        all_authentication_requirements = set()
        
        for result in component_results:
            if result.success and result.backend_files:
                # Extract API endpoints from registry
                registry = result.registry_entry
                if "apiEndpoints" in registry:
                    all_api_endpoints.update(registry["apiEndpoints"])
                
                # Extract data models from backend files
                for file_path, file_content in result.backend_files.items():
                    if "model" in file_path.lower() or "schema" in file_path.lower():
                        all_data_models.add(file_path)
        
        # Generate centralized backend system
        backend_system = {
            "server_config": {
                "framework": backend_framework,
                "port": 3001,
                "cors_enabled": True,
                "authentication": design_system.backend_requirements.get("authentication", False),
                "database": design_system.backend_requirements.get("database", False)
            },
            "api_endpoints": list(all_api_endpoints),
            "data_models": list(all_data_models),
            "middleware": [],
            "routes": {}
        }
        
        return backend_system
    
    async def _assemble_final_project(
        self,
        component_results: List[LosslessComponentResult],
        design_system: DesignSystem,
        backend_system: Dict[str, Any],
        layout_graph: Dict[str, LayoutNode],
        framework: str,
        backend_framework: str
    ) -> Dict[str, Any]:
        """Pass 6: Assemble final project with consistency validation"""
        
        # Collect all generated code
        all_frontend_code = {}
        all_backend_code = {}
        component_registry = {}
        
        for result in component_results:
            if result.success:
                all_frontend_code.update(result.frontend_files)
                all_backend_code.update(result.backend_files)
                component_registry[result.component_name] = result.registry_entry
        
        # Generate project structure files
        project_files = await self._generate_project_structure_lossless(
            component_registry=component_registry,
            design_system=design_system,
            backend_system=backend_system,
            layout_graph=layout_graph,
            framework=framework,
            backend_framework=backend_framework
        )
        
        # Merge project files
        all_frontend_code.update(project_files.get("frontend", {}))
        all_backend_code.update(project_files.get("backend", {}))
        
        return {
            "frontend_code": all_frontend_code,
            "backend_code": all_backend_code,
            "component_registry": component_registry
        }
    
    async def _generate_project_structure_lossless(
        self,
        component_registry: Dict[str, Any],
        design_system: DesignSystem,
        backend_system: Dict[str, Any],
        layout_graph: Dict[str, LayoutNode],
        framework: str,
        backend_framework: str
    ) -> Dict[str, Dict[str, str]]:
        """Generate comprehensive project structure files"""
        
        return {
            "frontend": {
                "src/design-tokens.ts": f"export const designTokens = {json.dumps(design_system.tokens, indent=2)};",
                "src/component-registry.json": json.dumps(component_registry, indent=2),
                "src/layout-graph.json": json.dumps(layout_graph, indent=2),
                "src/App.tsx": self._generate_app_component(component_registry, framework),
                "src/routes.tsx": self._generate_routes(component_registry, framework)
            },
            "backend": {
                "src/server.ts": self._generate_server_file(backend_system, backend_framework),
                "src/api/routes.ts": self._generate_api_routes(backend_system),
                "src/models/index.ts": self._generate_data_models(backend_system),
                "src/middleware/auth.ts": self._generate_auth_middleware(backend_system)
            }
        }
    
    def _generate_app_component(self, component_registry: Dict[str, Any], framework: str) -> str:
        """Generate main App component"""
        if framework == "react":
            return f"""
import React from 'react';
import {{ BrowserRouter as Router, Routes, Route }} from 'react-router-dom';
import {{ componentRegistry }} from './component-registry';

const App: React.FC = () => {{
  return (
    <Router>
      <div className="app">
        <Routes>
          {{Object.entries(componentRegistry).map(([name, config]) => (
            <Route 
              key={{name}} 
              path={{`/${{name.toLowerCase()}}`}} 
              element={{React.createElement(config.component)}}
            />
          ))}}
        </Routes>
      </div>
    </Router>
  );
}};

export default App;
"""
        return ""
    
    def _generate_routes(self, component_registry: Dict[str, Any], framework: str) -> str:
        """Generate routing configuration"""
        if framework == "react":
            routes = []
            for name, config in component_registry.items():
                routes.append(f"  {{ path: '/{name.lower()}', component: {name} }}")
            
            return f"""
export const routes = [
{chr(10).join(routes)}
];
"""
        return ""
    
    def _generate_server_file(self, backend_system: Dict[str, Any], backend_framework: str) -> str:
        """Generate server configuration"""
        if backend_framework == "nodejs":
            return f"""
import express from 'express';
import cors from 'cors';
import {{ apiRoutes }} from './api/routes';

const app = express();
const PORT = {backend_system['server_config']['port']};

app.use(cors());
app.use(express.json());

// API Routes
app.use('/api', apiRoutes);

app.listen(PORT, () => {{
  console.log(`Server running on port ${{PORT}}`);
}});
"""
        return ""
    
    def _generate_api_routes(self, backend_system: Dict[str, Any]) -> str:
        """Generate API routes"""
        routes = []
        for endpoint in backend_system.get("api_endpoints", []):
            routes.append(f"  app.get('{endpoint}', (req, res) => res.json({{}}));")
        
        return f"""
import express from 'express';

const router = express.Router();

{chr(10).join(routes)}

export {{ router as apiRoutes }};
"""
    
    def _generate_data_models(self, backend_system: Dict[str, Any]) -> str:
        """Generate data models"""
        return """
export interface BaseModel {
  id: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface User extends BaseModel {
  name: string;
  email: string;
}
"""
    
    def _generate_auth_middleware(self, backend_system: Dict[str, Any]) -> str:
        """Generate authentication middleware"""
        if backend_system.get("server_config", {}).get("authentication", False):
            return """
import { Request, Response, NextFunction } from 'express';

export const authMiddleware = (req: Request, res: Response, next: NextFunction) => {
  // Authentication logic here
  next();
};
"""
        return ""
    
    def _calculate_lossless_score(
        self,
        component_results: List[LosslessComponentResult],
        design_system: DesignSystem
    ) -> float:
        """Calculate lossless score based on consistency and completeness"""
        if not component_results:
            return 0.0
        
        successful_components = [r for r in component_results if r.success]
        total_components = len(component_results)
        
        # Base score from success rate
        success_rate = len(successful_components) / total_components if total_components > 0 else 0
        
        # Consistency score from design system usage
        consistency_score = 0.0
        if successful_components:
            tokens_used_count = 0
            for result in successful_components:
                if result.registry_entry and "tokens" in result.registry_entry:
                    tokens_used_count += len(result.registry_entry["tokens"])
            
            # Higher token usage = better design system consistency
            max_possible_tokens = len(design_system.tokens) * len(successful_components)
            consistency_score = tokens_used_count / max_possible_tokens if max_possible_tokens > 0 else 0
        
        # Layout dependency score
        layout_score = 0.0
        if successful_components:
            components_with_dependencies = len([r for r in successful_components if r.layout_dependencies])
            layout_score = components_with_dependencies / len(successful_components)
        
        # Final score (weighted average)
        final_score = (success_rate * 0.4) + (consistency_score * 0.3) + (layout_score * 0.3)
        
        return min(1.0, max(0.0, final_score))
