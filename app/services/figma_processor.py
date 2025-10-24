"""
Figma Processor
Handles Figma URL processing, JSON extraction, and image processing
"""

import re
import httpx
import json
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse, parse_qs
from dataclasses import dataclass

from app.core.config import get_settings

settings = get_settings()


@dataclass
class FigmaFileInfo:
    """Figma file information"""
    file_key: str
    file_id: str
    file_name: str
    url: str
    access_token: str


@dataclass
class ImageReference:
    """Image reference information"""
    node_id: str
    image_ref: str
    image_url: Optional[str] = None
    format: str = "png"
    scale: float = 2.0


class FigmaProcessor:
    """Processes Figma files and extracts design data"""
    
    def __init__(self):
        self.base_url = "https://api.figma.com/v1"
        self.timeout = 120.0  # Increased for large file processing
        
        # Regex patterns for Figma URL parsing
        self.url_patterns = [
            # Standard Figma file URLs
            r'https://www\.figma\.com/file/([a-zA-Z0-9]+)',
            r'https://figma\.com/file/([a-zA-Z0-9]+)',
            # Figma dev URLs
            r'https://www\.figma\.com/design/([a-zA-Z0-9]+)',
            r'https://figma\.com/design/([a-zA-Z0-9]+)',
            # Figma prototype URLs
            r'https://www\.figma\.com/proto/([a-zA-Z0-9]+)',
            r'https://figma\.com/proto/([a-zA-Z0-9]+)'
        ]
    
    def extract_file_key(self, figma_url: str) -> Optional[str]:
        """Extract file key from Figma URL using regex"""
        try:
            for pattern in self.url_patterns:
                match = re.search(pattern, figma_url)
                if match:
                    return match.group(1)
            
            # Try parsing as URL with query parameters
            parsed_url = urlparse(figma_url)
            if 'figma.com' in parsed_url.netloc:
                path_parts = parsed_url.path.split('/')
                for part in path_parts:
                    if part and len(part) > 10:  # Figma file keys are typically long
                        return part
            
            return None
            
        except Exception as e:
            print(f"Error extracting file key: {str(e)}")
            return None
    
    async def get_figma_json(
        self,
        file_key: str,
        access_token: str
    ) -> Dict[str, Any]:
        """Get Figma file JSON using REST API"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                headers = {"X-Figma-Token": access_token}
                response = await client.get(
                    f"{self.base_url}/files/{file_key}",
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"Failed to fetch Figma JSON: {str(e)}")
    
    def extract_image_references(self, figma_json: Dict[str, Any]) -> List[ImageReference]:
        """Extract image references from Figma JSON"""
        image_refs = []
        
        def traverse_nodes(node: Dict[str, Any], parent_path: str = ""):
            """Recursively traverse nodes to find image references"""
            if not isinstance(node, dict):
                return
            
            # Check for image fills
            fills = node.get("fills", [])
            for fill in fills:
                if fill.get("type") == "IMAGE":
                    image_ref = fill.get("imageRef")
                    if image_ref:
                        image_refs.append(ImageReference(
                            node_id=node.get("id", ""),
                            image_ref=image_ref,
                            format="png",
                            scale=2.0
                        ))
            
            # Traverse children
            children = node.get("children", [])
            for child in children:
                traverse_nodes(child, f"{parent_path}.{child.get('name', '')}")
        
        # Start traversal from document
        document = figma_json.get("document", {})
        traverse_nodes(document)
        
        return image_refs
    
    async def get_figma_image_urls(
        self,
        file_key: str,
        node_ids: List[str],
        access_token: str,
        format: str = "png",
        scale: float = 2.0
    ) -> Dict[str, str]:
        """Get actual image URLs from Figma Image API"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                headers = {"X-Figma-Token": access_token}
                ids_param = ",".join(node_ids)
                
                response = await client.get(
                    f"{self.base_url}/images/{file_key}",
                    params={
                        "ids": ids_param,
                        "format": format,
                        "scale": scale
                    },
                    headers=headers
                )
                response.raise_for_status()
                
                result = response.json()
                return result.get("images", {})
                
            except httpx.HTTPError as e:
                raise Exception(f"Failed to get image URLs: {str(e)}")
    
    def replace_image_refs_with_urls(
        self,
        figma_json: Dict[str, Any],
        image_urls: Dict[str, str]
    ) -> Dict[str, Any]:
        """Replace imageRef in nodes with actual image URLs"""
        def replace_in_node(node: Dict[str, Any]):
            """Recursively replace image references"""
            if not isinstance(node, dict):
                return
            
            # Replace imageRef in fills
            fills = node.get("fills", [])
            for fill in fills:
                if fill.get("type") == "IMAGE":
                    node_id = node.get("id")
                    if node_id in image_urls:
                        fill["imageUrl"] = image_urls[node_id]
                        # Keep imageRef for reference
                        fill["originalImageRef"] = fill.get("imageRef")
            
            # Process children
            children = node.get("children", [])
            for child in children:
                replace_in_node(child)
        
        # Create a copy to avoid modifying original
        processed_json = json.loads(json.dumps(figma_json))
        
        # Replace image references
        document = processed_json.get("document", {})
        replace_in_node(document)
        
        return processed_json
    
    def validate_figma_json(self, figma_json: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate Figma JSON structure and size with intelligent processing for large files"""
        errors = []
        
        # Check required fields
        required_fields = ["document", "name"]
        for field in required_fields:
            if field not in figma_json:
                errors.append(f"Missing required field: {field}")
        
        # Check document structure
        document = figma_json.get("document", {})
        if not isinstance(document, dict):
            errors.append("Document must be an object")
        elif "children" not in document:
            errors.append("Document must have children")
        
        # Check JSON size
        json_str = json.dumps(figma_json)
        json_size = len(json_str.encode('utf-8'))
        
        if json_size > 50 * 1024 * 1024:  # 50MB limit
            errors.append(f"JSON too large: {json_size / 1024 / 1024:.1f}MB")
        
        # Check node count - use intelligent processing for large files
        node_count = self._count_nodes(figma_json)
        if node_count > 10000:  # 10k nodes limit
            # Instead of rejecting, analyze structure for screen-by-screen processing
            structure_analysis = self._analyze_file_structure(figma_json)
            if structure_analysis['can_process_screen_by_screen']:
                # Mark for screen-by-screen processing instead of error
                figma_json['_processing_mode'] = 'screen_by_screen'
                figma_json['_structure_analysis'] = structure_analysis
            else:
                errors.append(f"Too many nodes: {node_count} (cannot process screen-by-screen)")
        
        return len(errors) == 0, errors
    
    def _count_nodes(self, figma_json: Dict[str, Any]) -> int:
        """Count total nodes in Figma JSON"""
        count = 0
        
        def count_in_node(node: Dict[str, Any]):
            nonlocal count
            if isinstance(node, dict):
                count += 1
                children = node.get("children", [])
                for child in children:
                    count_in_node(child)
        
        document = figma_json.get("document", {})
        count_in_node(document)
        
        return count
    
    def _analyze_file_structure(self, figma_json: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Figma file structure to determine processing strategy"""
        document = figma_json.get("document", {})
        pages = document.get("children", [])
        
        analysis = {
            "page_count": len(pages),
            "screen_count": 0,
            "total_nodes": self._count_nodes(figma_json),
            "can_process_screen_by_screen": False,
            "screens": []
        }
        
        # Analyze each page for screens/frames
        for page in pages:
            if page.get("type") == "CANVAS":
                frames = [child for child in page.get("children", []) 
                         if child.get("type") == "FRAME"]
                
                for frame in frames:
                    frame_node_count = self._count_nodes({"document": frame})
                    analysis["screens"].append({
                        "name": frame.get("name", "Unnamed"),
                        "id": frame.get("id", ""),
                        "page_name": page.get("name", ""),
                        "node_count": frame_node_count,
                        "can_process": frame_node_count <= 10000
                    })
                    analysis["screen_count"] += 1
        
        # Determine if we can process screen-by-screen
        analysis["can_process_screen_by_screen"] = (
            analysis["screen_count"] > 1 and 
            all(screen["can_process"] for screen in analysis["screens"])
        )
        
        return analysis
    
    def _select_priority_screens(self, screens: List[Dict[str, Any]], max_screens: int) -> List[Dict[str, Any]]:
        """Select the most important screens for processing"""
        # Priority keywords for screen selection
        priority_keywords = [
            'home', 'dashboard', 'main', 'landing', 'login', 'signup', 'profile',
            'settings', 'admin', 'index', 'app', 'mobile', 'desktop'
        ]
        
        # Score screens based on name and importance
        scored_screens = []
        for screen in screens:
            score = 0
            screen_name = screen.get('name', '').lower()
            
            # Check for priority keywords
            for keyword in priority_keywords:
                if keyword in screen_name:
                    score += 10
            
            # Prefer larger screens (more content)
            node_count = screen.get('metadata', {}).get('node_count', 0)
            score += min(node_count / 100, 5)  # Cap at 5 points
            
            # Prefer screens with more components
            component_count = len(screen.get('components', []))
            score += min(component_count, 3)  # Cap at 3 points
            
            scored_screens.append((score, screen))
        
        # Sort by score and take top screens
        scored_screens.sort(key=lambda x: x[0], reverse=True)
        return [screen for _, screen in scored_screens[:max_screens]]
    
    def process_large_figma_screen_by_screen(
        self, 
        figma_json: Dict[str, Any],
        max_screens: int = 20  # Process more screens but still limit for speed
    ) -> Dict[str, Any]:
        """Process large Figma files by processing each screen separately"""
        structure_analysis = figma_json.get('_structure_analysis', {})
        screens = structure_analysis.get('screens', [])
        
        if not screens:
            raise Exception("No screens found for screen-by-screen processing")
        
        # Smart screen selection - prioritize main screens
        if len(screens) > max_screens:
            screens = self._select_priority_screens(screens, max_screens)
        
        processed_screens = {}
        shared_components = []
        
        for screen in screens:
            try:
                # Extract screen data
                screen_data = self._extract_screen_data(figma_json, screen)
                
                # Process screen
                screen_result = self._process_single_screen(screen_data)
                processed_screens[screen['name']] = screen_result
                
                # Extract shared components
                screen_components = self._extract_components_from_screen(screen_data)
                shared_components.extend(screen_components)
                
            except Exception as e:
                processed_screens[screen['name']] = {
                    "success": False,
                    "error": str(e),
                    "code": {}
                }
        
        # Deduplicate shared components
        unique_components = self._deduplicate_components(shared_components)
        
        return {
            "success": True,
            "processing_mode": "screen_by_screen",
            "screens": processed_screens,
            "shared_components": unique_components,
            "navigation": self._generate_navigation_structure(screens),
            "metadata": {
                "total_screens": len(screens),
                "successful_screens": len([s for s in processed_screens.values() if s.get("success", False)]),
                "original_preserved": True
            }
        }
    
    def _extract_screen_data(self, figma_json: Dict[str, Any], screen: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data for a specific screen"""
        # Find the screen in the original JSON
        document = figma_json.get("document", {})
        
        for page in document.get("children", []):
            if page.get("type") == "CANVAS":
                for frame in page.get("children", []):
                    if frame.get("id") == screen["id"]:
                        return {
                            "screen": frame,
                            "page": page,
                            "metadata": {
                                "screen_name": screen["name"],
                                "page_name": page.get("name", ""),
                                "node_count": screen["node_count"]
                            }
                        }
        
        raise Exception(f"Screen {screen['name']} not found in original JSON")
    
    def _process_single_screen(self, screen_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single screen through the standard pipeline"""
        screen = screen_data["screen"]
        
        # Create a proper Figma JSON structure for this screen
        screen_json = {
            "name": f"Screen: {screen_data['metadata']['screen_name']}",
            "document": {
                "id": screen["id"],
                "name": screen["name"],
                "type": "CANVAS",
                "children": [screen]  # Wrap screen in a canvas structure
            }
        }
        
        # Process through standard chunking with larger chunks for efficiency
        chunks = self.chunk_figma_json(screen_json, max_chunk_size=5000)
        
        return {
            "success": True,
            "screen_name": screen_data['metadata']['screen_name'],
            "chunks": chunks,
            "chunk_count": len(chunks),
            "node_count": screen_data['metadata']['node_count']
        }
    
    def _extract_components_from_screen(self, screen_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract reusable components from a screen"""
        screen = screen_data["screen"]
        components = []
        
        def find_components(node: Dict[str, Any]):
            if node.get("type") == "COMPONENT":
                components.append({
                    "id": node.get("id"),
                    "name": node.get("name"),
                    "type": node.get("type"),
                    "screen": screen_data['metadata']['screen_name']
                })
            
            for child in node.get("children", []):
                find_components(child)
        
        find_components(screen)
        return components
    
    def _deduplicate_components(self, components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate components based on name and structure"""
        seen = set()
        unique_components = []
        
        for component in components:
            # Create a key based on name and type
            key = f"{component['name']}_{component['type']}"
            if key not in seen:
                seen.add(key)
                unique_components.append(component)
        
        return unique_components
    
    def _generate_navigation_structure(self, screens: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate navigation structure for multi-screen app"""
        return {
            "type": "multi_screen_app",
            "screens": [
                {
                    "name": screen["name"],
                    "route": f"/{screen['name'].lower().replace(' ', '-')}",
                    "component": f"{screen['name'].replace(' ', '')}Screen"
                }
                for screen in screens
            ],
            "navigation": {
                "type": "react_router",
                "routes": [
                    {
                        "path": f"/{screen['name'].lower().replace(' ', '-')}",
                        "component": f"{screen['name'].replace(' ', '')}Screen"
                    }
                    for screen in screens
                ]
            }
        }
    
    def chunk_figma_json(
        self,
        figma_json: Dict[str, Any],
        max_chunk_size: int = 5000  # Much larger chunks for better efficiency
    ) -> List[Dict[str, Any]]:
        """Split Figma JSON into logical chunks"""
        chunks = []
        
        # Extract pages
        document = figma_json.get("document", {})
        pages = document.get("children", [])
        
        # Handle case where document itself is a CANVAS (screen-by-screen processing)
        if document.get("type") == "CANVAS":
            frames = document.get("children", [])
            for frame in frames:
                if frame.get("type") == "FRAME":
                    # Create chunk for frame
                    chunk = {
                        "type": "frame",
                        "page_name": document.get("name", ""),
                        "frame_name": frame.get("name", ""),
                        "frame_id": frame.get("id", ""),
                        "data": self._clean_node(frame),
                        "metadata": {
                            "page_id": document.get("id", ""),
                            "frame_id": frame.get("id", ""),
                            "chunk_type": "frame"
                        }
                    }
                    chunks.append(chunk)
        else:
            # Standard processing for pages
            for page in pages:
                if page.get("type") == "CANVAS":
                    # Extract frames from page
                    frames = page.get("children", [])
                    
                    for frame in frames:
                        if frame.get("type") == "FRAME":
                            # Create chunk for frame
                            chunk = {
                                "type": "frame",
                                "page_name": page.get("name", ""),
                                "frame_name": frame.get("name", ""),
                                "frame_id": frame.get("id", ""),
                                "data": self._clean_node(frame),
                                "metadata": {
                                    "page_id": page.get("id", ""),
                                    "frame_id": frame.get("id", ""),
                                    "chunk_type": "frame"
                                }
                            }
                            chunks.append(chunk)
                        
                        # Extract components from frame
                        components = self._extract_components(frame)
                        for component in components:
                            component_chunk = {
                                "type": "component",
                                "page_name": page.get("name", ""),
                                "frame_name": frame.get("name", ""),
                                "component_name": component.get("name", ""),
                                "component_id": component.get("id", ""),
                                "data": self._clean_node(component),
                                "metadata": {
                                    "page_id": page.get("id", ""),
                                    "frame_id": frame.get("id", ""),
                                    "component_id": component.get("id", ""),
                                    "chunk_type": "component"
                                }
                            }
                            chunks.append(component_chunk)
        
        return chunks
    
    def _clean_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Remove non-critical fields from node"""
        # Fields to keep
        keep_fields = {
            "id", "name", "type", "visible", "locked",
            "absoluteBoundingBox", "constraints", "layoutAlign",
            "layoutGrow", "layoutMode", "itemSpacing",
            "paddingLeft", "paddingRight", "paddingTop", "paddingBottom",
            "fills", "strokes", "strokeWeight", "strokeAlign",
            "cornerRadius", "cornerSmoothing",
            "children", "characters", "style", "characterStyleOverrides",
            "styleOverrideTable", "lineTypes", "lineIndentations"
        }
        
        def clean_recursive(node: Dict[str, Any]) -> Dict[str, Any]:
            if not isinstance(node, dict):
                return node
            
            cleaned = {}
            for key, value in node.items():
                if key in keep_fields:
                    if key == "children" and isinstance(value, list):
                        cleaned[key] = [clean_recursive(child) for child in value]
                    else:
                        cleaned[key] = value
            
            return cleaned
        
        return clean_recursive(node)
    
    def _extract_components(self, frame: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract components from frame"""
        components = []
        
        def find_components(node: Dict[str, Any]):
            if not isinstance(node, dict):
                return
            
            if node.get("type") == "COMPONENT":
                components.append(node)
            
            children = node.get("children", [])
            for child in children:
                find_components(child)
        
        find_components(frame)
        return components
    
    def summarize_large_nodes(
        self,
        figma_json: Dict[str, Any],
        max_node_size: int = 1000
    ) -> Dict[str, Any]:
        """Summarize large nodes to reduce size"""
        def summarize_node(node: Dict[str, Any]) -> Dict[str, Any]:
            if not isinstance(node, dict):
                return node
            
            # Check if node is too large
            node_str = json.dumps(node)
            if len(node_str) > max_node_size:
                # Create summary
                summary = {
                    "id": node.get("id"),
                    "name": node.get("name"),
                    "type": node.get("type"),
                    "absoluteBoundingBox": node.get("absoluteBoundingBox"),
                    "children_count": len(node.get("children", [])),
                    "summary": "Large node summarized",
                    "original_size": len(node_str)
                }
                
                # Keep children if they're small
                children = node.get("children", [])
                if children:
                    summary["children"] = [summarize_node(child) for child in children[:5]]  # Limit to 5 children
                
                return summary
            else:
                # Process children recursively
                children = node.get("children", [])
                if children:
                    node["children"] = [summarize_node(child) for child in children]
                return node
        
        # Create a copy to avoid modifying original
        processed_json = json.loads(json.dumps(figma_json))
        
        # Summarize document
        document = processed_json.get("document", {})
        processed_json["document"] = summarize_node(document)
        
        return processed_json
    
    async def process_figma_url(
        self,
        figma_url: str,
        access_token: str,
        include_images: bool = True,
        chunk_size: int = 1000
    ) -> Dict[str, Any]:
        """Complete Figma processing pipeline"""
        try:
            # 1. Extract file key from URL
            file_key = self.extract_file_key(figma_url)
            if not file_key:
                raise Exception("Could not extract file key from URL")
            
            # 2. Get Figma JSON
            figma_json = await self.get_figma_json(file_key, access_token)
            
            # 3. Validate JSON
            is_valid, errors = self.validate_figma_json(figma_json)
            if not is_valid:
                raise Exception(f"Invalid Figma JSON: {', '.join(errors)}")
            
            # 3.5. Check if we need screen-by-screen processing
            if figma_json.get('_processing_mode') == 'screen_by_screen':
                # Process large files screen-by-screen
                screen_by_screen_result = self.process_large_figma_screen_by_screen(figma_json)
                return {
                    "file_key": file_key,
                    "file_name": figma_json.get("name", ""),
                    "processing_mode": "screen_by_screen",
                    "screens": screen_by_screen_result["screens"],
                    "shared_components": screen_by_screen_result["shared_components"],
                    "navigation": screen_by_screen_result["navigation"],
                    "metadata": screen_by_screen_result["metadata"]
                }
            
            # 4. Extract and process images if requested
            if include_images:
                image_refs = self.extract_image_references(figma_json)
                if image_refs:
                    node_ids = [ref.node_id for ref in image_refs]
                    image_urls = await self.get_figma_image_urls(
                        file_key, node_ids, access_token
                    )
                    figma_json = self.replace_image_refs_with_urls(figma_json, image_urls)
            
            # 5. Summarize large nodes
            figma_json = self.summarize_large_nodes(figma_json)
            
            # 6. Chunk JSON
            chunks = self.chunk_figma_json(figma_json, chunk_size)
            
            return {
                "file_key": file_key,
                "file_name": figma_json.get("name", ""),
                "chunks": chunks,
                "total_chunks": len(chunks),
                "processed_json": figma_json,
                "image_count": len(image_refs) if include_images else 0
            }
            
        except Exception as e:
            raise Exception(f"Figma processing failed: {str(e)}")
