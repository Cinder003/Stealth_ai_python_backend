"""
Figma Service
Handles Figma API integration and design processing
"""

import httpx
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.config import get_settings

settings = get_settings()


class FigmaService:
    """Service for Figma API integration"""
    
    def __init__(self):
        self.base_url = "https://api.figma.com/v1"
        self.timeout = 30.0
    
    async def validate_token(self, access_token: str) -> Dict[str, Any]:
        """Validate Figma access token"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/me",
                    headers={"X-Figma-Token": access_token}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"Figma token validation failed: {str(e)}")
    
    async def get_user_files(self, access_token: str) -> List[Dict[str, Any]]:
        """Get user's Figma files"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/files",
                    headers={"X-Figma-Token": access_token}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("files", [])
            except httpx.HTTPError as e:
                raise Exception(f"Failed to get Figma files: {str(e)}")
    
    async def get_file_details(self, file_id: str, access_token: str) -> Dict[str, Any]:
        """Get detailed file information"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/files/{file_id}",
                    headers={"X-Figma-Token": access_token}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"Failed to get file details: {str(e)}")
    
    async def get_file_data(self, file_id: str, access_token: str) -> Dict[str, Any]:
        """Get complete file data including nodes"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/files/{file_id}",
                    headers={"X-Figma-Token": access_token}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"Failed to get file data: {str(e)}")
    
    async def analyze_design(
        self,
        file_data: Dict[str, Any],
        analysis_type: str = "comprehensive",
        include_components: bool = True,
        include_layout: bool = True,
        include_styling: bool = True
    ) -> Dict[str, Any]:
        """Analyze Figma design for code generation"""
        try:
            analysis = {
                "analysis_type": analysis_type,
                "timestamp": datetime.utcnow().isoformat(),
                "components": [],
                "layout": {},
                "styling": {},
                "colors": [],
                "typography": [],
                "spacing": {},
                "dimensions": {}
            }
            
            # Extract components
            if include_components:
                analysis["components"] = await self._extract_components(file_data)
            
            # Analyze layout
            if include_layout:
                analysis["layout"] = await self._analyze_layout(file_data)
            
            # Analyze styling
            if include_styling:
                analysis["styling"] = await self._analyze_styling(file_data)
                analysis["colors"] = await self._extract_colors(file_data)
                analysis["typography"] = await self._extract_typography(file_data)
                analysis["spacing"] = await self._analyze_spacing(file_data)
                analysis["dimensions"] = await self._analyze_dimensions(file_data)
            
            return analysis
            
        except Exception as e:
            raise Exception(f"Design analysis failed: {str(e)}")
    
    async def export_assets(
        self,
        file_id: str,
        node_ids: List[str],
        format: str = "png",
        scale: float = 2.0,
        access_token: str = ""
    ) -> Dict[str, str]:
        """Export assets from Figma file"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Request export
                export_data = {
                    "ids": ",".join(node_ids),
                    "format": format,
                    "scale": scale
                }
                
                response = await client.get(
                    f"{self.base_url}/images/{file_id}",
                    params=export_data,
                    headers={"X-Figma-Token": access_token}
                )
                response.raise_for_status()
                
                export_result = response.json()
                images = export_result.get("images", {})
                
                # Download assets
                assets = {}
                for node_id, url in images.items():
                    if url:
                        asset_content = await self._download_asset(url)
                        assets[f"{node_id}.{format}"] = asset_content
                
                return assets
                
            except httpx.HTTPError as e:
                raise Exception(f"Asset export failed: {str(e)}")
    
    async def get_components(self, file_id: str, access_token: str) -> List[Dict[str, Any]]:
        """Get components from Figma file"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/files/{file_id}/components",
                    headers={"X-Figma-Token": access_token}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("meta", {}).get("components", [])
            except httpx.HTTPError as e:
                raise Exception(f"Failed to get components: {str(e)}")
    
    async def get_nodes(
        self,
        file_id: str,
        node_ids: List[str],
        access_token: str
    ) -> Dict[str, Any]:
        """Get specific nodes from Figma file"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                params = {"ids": ",".join(node_ids)}
                response = await client.get(
                    f"{self.base_url}/files/{file_id}/nodes",
                    params=params,
                    headers={"X-Figma-Token": access_token}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"Failed to get nodes: {str(e)}")
    
    async def generate_preview(
        self,
        node_data: Dict[str, Any],
        framework: str
    ) -> Dict[str, Any]:
        """Generate code preview from node data"""
        try:
            preview = {
                "framework": framework,
                "components": [],
                "styles": {},
                "layout": {}
            }
            
            # Process nodes for preview
            nodes = node_data.get("nodes", {})
            for node_id, node_info in nodes.items():
                component_preview = await self._generate_component_preview(
                    node_info, framework
                )
                preview["components"].append(component_preview)
            
            return preview
            
        except Exception as e:
            raise Exception(f"Preview generation failed: {str(e)}")
    
    # Private helper methods
    
    async def _extract_components(self, file_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract components from file data"""
        components = []
        document = file_data.get("document", {})
        
        def traverse_nodes(node):
            if node.get("type") == "COMPONENT":
                components.append({
                    "id": node.get("id"),
                    "name": node.get("name"),
                    "type": node.get("type"),
                    "bounds": node.get("absoluteBoundingBox", {}),
                    "fills": node.get("fills", []),
                    "strokes": node.get("strokes", []),
                    "effects": node.get("effects", [])
                })
            
            for child in node.get("children", []):
                traverse_nodes(child)
        
        traverse_nodes(document)
        return components
    
    async def _analyze_layout(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze layout structure"""
        layout = {
            "type": "unknown",
            "direction": "vertical",
            "alignment": "start",
            "spacing": 0,
            "padding": {},
            "grid": {}
        }
        
        # Analyze layout based on document structure
        document = file_data.get("document", {})
        if document.get("type") == "FRAME":
            layout["type"] = "frame"
            layout["direction"] = document.get("layoutMode", "NONE")
            layout["spacing"] = document.get("itemSpacing", 0)
        
        return layout
    
    async def _analyze_styling(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze styling patterns"""
        styling = {
            "color_scheme": "light",
            "primary_colors": [],
            "secondary_colors": [],
            "text_styles": [],
            "border_radius": 0,
            "shadows": []
        }
        
        # Extract styling information from document
        # This would analyze fills, strokes, effects, etc.
        
        return styling
    
    async def _extract_colors(self, file_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract color palette"""
        colors = []
        
        def extract_colors_from_node(node):
            for fill in node.get("fills", []):
                if fill.get("type") == "SOLID":
                    color = fill.get("color", {})
                    colors.append({
                        "r": color.get("r", 0),
                        "g": color.get("g", 0),
                        "b": color.get("b", 0),
                        "a": color.get("a", 1)
                    })
            
            for child in node.get("children", []):
                extract_colors_from_node(child)
        
        document = file_data.get("document", {})
        extract_colors_from_node(document)
        
        return colors
    
    async def _extract_typography(self, file_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract typography information"""
        typography = []
        
        def extract_typography_from_node(node):
            if node.get("type") == "TEXT":
                style = node.get("style", {})
                typography.append({
                    "font_family": style.get("fontFamily"),
                    "font_size": style.get("fontSize"),
                    "font_weight": style.get("fontWeight"),
                    "line_height": style.get("lineHeightPx"),
                    "text_align": style.get("textAlignHorizontal")
                })
            
            for child in node.get("children", []):
                extract_typography_from_node(child)
        
        document = file_data.get("document", {})
        extract_typography_from_node(document)
        
        return typography
    
    async def _analyze_spacing(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze spacing patterns"""
        spacing = {
            "padding": {},
            "margins": {},
            "gaps": []
        }
        
        # Analyze spacing from layout properties
        # This would extract padding, margins, gaps from frames and components
        
        return spacing
    
    async def _analyze_dimensions(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze dimension patterns"""
        dimensions = {
            "width": 0,
            "height": 0,
            "responsive_breakpoints": [],
            "min_width": 0,
            "max_width": 0
        }
        
        # Analyze dimensions from document bounds
        document = file_data.get("document", {})
        bounds = document.get("absoluteBoundingBox", {})
        if bounds:
            dimensions["width"] = bounds.get("width", 0)
            dimensions["height"] = bounds.get("height", 0)
        
        return dimensions
    
    async def _generate_component_preview(
        self,
        node_info: Dict[str, Any],
        framework: str
    ) -> Dict[str, Any]:
        """Generate component preview"""
        node = node_info.get("document", {})
        
        return {
            "id": node.get("id"),
            "name": node.get("name"),
            "type": node.get("type"),
            "framework": framework,
            "preview_code": f"// {framework} component preview",
            "props": [],
            "styles": {}
        }
    
    async def _download_asset(self, url: str) -> bytes:
        """Download asset from URL"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.content
            except httpx.HTTPError as e:
                raise Exception(f"Failed to download asset: {str(e)}")
