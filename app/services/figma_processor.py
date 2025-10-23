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
        self.timeout = 30.0
        
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
        """Validate Figma JSON structure and size"""
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
        
        # Check node count
        node_count = self._count_nodes(figma_json)
        if node_count > 10000:  # 10k nodes limit
            errors.append(f"Too many nodes: {node_count}")
        
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
    
    def chunk_figma_json(
        self,
        figma_json: Dict[str, Any],
        max_chunk_size: int = 1000
    ) -> List[Dict[str, Any]]:
        """Split Figma JSON into logical chunks"""
        chunks = []
        
        # Extract pages
        document = figma_json.get("document", {})
        pages = document.get("children", [])
        
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
