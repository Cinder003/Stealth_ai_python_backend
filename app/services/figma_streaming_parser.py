"""
Figma JSON Streaming Parser
Extracts only relevant nodes for component generation without loading the entire JSON
"""

import json
import re
from typing import Dict, List, Any, Optional, Iterator, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ComponentNode:
    """Represents a component extracted from Figma JSON"""
    node_id: str
    name: str
    node_type: str
    component_type: str  # 'button', 'input', 'card', 'layout', etc.
    bounds: Dict[str, float]
    styles: Dict[str, Any]
    children: List['ComponentNode']
    parent_id: Optional[str]
    is_component: bool
    is_instance: bool
    design_tokens: Dict[str, Any]
    image_refs: List[str]
    layout_constraints: Dict[str, Any]


@dataclass
class ExtractionResult:
    """Result of streaming extraction"""
    components: List[ComponentNode]
    design_tokens: Dict[str, Any]
    layout_hierarchy: Dict[str, Any]
    image_references: List[Dict[str, Any]]
    processing_metadata: Dict[str, Any]


class FigmaStreamingParser:
    """Streams and parses Figma JSON to extract only relevant component data"""
    
    def __init__(self):
        self.component_classifiers = {
            'button': self._classify_button,
            'input': self._classify_input,
            'card': self._classify_card,
            'layout': self._classify_layout,
            'navigation': self._classify_navigation,
            'text': self._classify_text,
            'image': self._classify_image
        }
        
        self.design_token_extractors = {
            'color': self._extract_color_tokens,
            'typography': self._extract_typography_tokens,
            'spacing': self._extract_spacing_tokens,
            'border': self._extract_border_tokens,
            'shadow': self._extract_shadow_tokens
        }
    
    async def extract_components(
        self,
        figma_json: Dict[str, Any],
        target_screens: Optional[List[str]] = None,
        component_types: Optional[List[str]] = None
    ) -> ExtractionResult:
        """
        Extract components from Figma JSON using streaming approach
        
        Args:
            figma_json: Full Figma JSON data
            target_screens: Specific screens to extract (None = all)
            component_types: Specific component types to extract (None = all)
        """
        print("DEBUG: Starting streaming component extraction")
        
        # Extract design tokens first
        design_tokens = await self._extract_all_design_tokens(figma_json)
        print(f"DEBUG: Extracted {len(design_tokens)} design token categories")
        
        # Extract components
        components = []
        image_references = []
        
        # Process document tree
        document = figma_json.get('document', {})
        if document:
            extracted_components = await self._extract_from_node(
                document,
                parent_id=None,
                target_screens=target_screens,
                component_types=component_types
            )
            components.extend(extracted_components)
        
        # Extract image references
        image_references = await self._extract_image_references(figma_json)
        
        # Build layout hierarchy
        layout_hierarchy = await self._build_layout_hierarchy(components)
        
        print(f"DEBUG: Extracted {len(components)} components")
        print(f"DEBUG: Found {len(image_references)} image references")
        
        return ExtractionResult(
            components=components,
            design_tokens=design_tokens,
            layout_hierarchy=layout_hierarchy,
            image_references=image_references,
            processing_metadata={
                "extraction_time": datetime.now().isoformat(),
                "total_components": len(components),
                "total_images": len(image_references),
                "token_categories": list(design_tokens.keys())
            }
        )
    
    async def _extract_from_node(
        self,
        node: Dict[str, Any],
        parent_id: Optional[str] = None,
        target_screens: Optional[List[str]] = None,
        component_types: Optional[List[str]] = None
    ) -> List[ComponentNode]:
        """Extract components from a single node and its children"""
        components = []
        
        node_id = node.get('id', '')
        node_name = node.get('name', '')
        node_type = node.get('type', '')
        
        # Check if this node should be processed
        if self._should_process_node(node, target_screens, component_types):
            component = await self._create_component_node(node, parent_id)
            if component:
                components.append(component)
        
        # Process children recursively
        children = node.get('children', [])
        for child in children:
            child_components = await self._extract_from_node(
                child,
                parent_id=node_id,
                target_screens=target_screens,
                component_types=component_types
            )
            components.extend(child_components)
        
        return components
    
    def _should_process_node(
        self,
        node: Dict[str, Any],
        target_screens: Optional[List[str]] = None,
        component_types: Optional[List[str]] = None
    ) -> bool:
        """Determine if a node should be processed"""
        node_name = node.get('name', '').lower()
        node_type = node.get('type', '')
        
        # Skip certain node types
        skip_types = ['DOCUMENT', 'PAGE', 'FRAME', 'GROUP']
        if node_type in skip_types:
            return False
        
        # Check target screens
        if target_screens:
            # Check if node is in target screens
            if not any(screen.lower() in node_name for screen in target_screens):
                return False
        
        # Check component types
        if component_types:
            component_type = self._classify_component_type(node)
            if component_type not in component_types:
                return False
        
        return True
    
    async def _create_component_node(
        self,
        node: Dict[str, Any],
        parent_id: Optional[str]
    ) -> Optional[ComponentNode]:
        """Create a ComponentNode from a Figma node"""
        try:
            node_id = node.get('id', '')
            name = node.get('name', '')
            node_type = node.get('type', '')
            
            # Classify component type
            component_type = self._classify_component_type(node)
            
            # Extract bounds
            bounds = self._extract_bounds(node)
            
            # Extract styles
            styles = await self._extract_node_styles(node)
            
            # Extract design tokens
            design_tokens = await self._extract_node_tokens(node)
            
            # Extract image references
            image_refs = self._extract_node_image_refs(node)
            
            # Extract layout constraints
            layout_constraints = self._extract_layout_constraints(node)
            
            # Check if it's a component or instance
            is_component = node.get('componentPropertyDefinitions') is not None
            is_instance = node.get('componentId') is not None
            
            return ComponentNode(
                node_id=node_id,
                name=name,
                node_type=node_type,
                component_type=component_type,
                bounds=bounds,
                styles=styles,
                children=[],  # Will be populated by parent
                parent_id=parent_id,
                is_component=is_component,
                is_instance=is_instance,
                design_tokens=design_tokens,
                image_refs=image_refs,
                layout_constraints=layout_constraints
            )
            
        except Exception as e:
            print(f"DEBUG: Error creating component node: {str(e)}")
            return None
    
    def _classify_component_type(self, node: Dict[str, Any]) -> str:
        """Classify the component type based on node properties"""
        node_name = node.get('name', '').lower()
        node_type = node.get('type', '')
        
        # Check for specific patterns
        if 'button' in node_name or node_type == 'RECTANGLE':
            return 'button'
        elif 'input' in node_name or 'field' in node_name:
            return 'input'
        elif 'card' in node_name or 'container' in node_name:
            return 'card'
        elif 'nav' in node_name or 'menu' in node_name:
            return 'navigation'
        elif 'text' in node_name or node_type == 'TEXT':
            return 'text'
        elif 'image' in node_name or node_type == 'RECTANGLE':
            return 'image'
        else:
            return 'layout'
    
    async def _extract_all_design_tokens(self, figma_json: Dict[str, Any]) -> Dict[str, Any]:
        """Extract all design tokens from the Figma JSON"""
        tokens = {}
        
        for token_type, extractor in self.design_token_extractors.items():
            try:
                token_data = await extractor(figma_json)
                if token_data:
                    tokens[token_type] = token_data
            except Exception as e:
                print(f"DEBUG: Error extracting {token_type} tokens: {str(e)}")
        
        return tokens
    
    async def _extract_color_tokens(self, figma_json: Dict[str, Any]) -> Dict[str, Any]:
        """Extract color design tokens"""
        colors = {}
        
        # Extract from styles
        styles = figma_json.get('styles', {})
        for style_id, style_data in styles.items():
            if style_data.get('styleType') == 'FILL':
                color_data = style_data.get('description', '')
                if color_data:
                    colors[style_id] = {
                        'name': style_data.get('name', ''),
                        'description': color_data,
                        'type': 'color'
                    }
        
        return colors
    
    async def _extract_typography_tokens(self, figma_json: Dict[str, Any]) -> Dict[str, Any]:
        """Extract typography design tokens"""
        typography = {}
        
        # Extract from styles
        styles = figma_json.get('styles', {})
        for style_id, style_data in styles.items():
            if style_data.get('styleType') == 'TEXT':
                typography[style_id] = {
                    'name': style_data.get('name', ''),
                    'description': style_data.get('description', ''),
                    'type': 'typography'
                }
        
        return typography
    
    async def _extract_spacing_tokens(self, figma_json: Dict[str, Any]) -> Dict[str, Any]:
        """Extract spacing design tokens"""
        # This would extract spacing values from the design
        # For now, return common spacing scale
        return {
            'xs': '4px',
            'sm': '8px',
            'md': '16px',
            'lg': '24px',
            'xl': '32px',
            '2xl': '48px'
        }
    
    async def _extract_border_tokens(self, figma_json: Dict[str, Any]) -> Dict[str, Any]:
        """Extract border design tokens"""
        return {
            'radius_sm': '4px',
            'radius_md': '8px',
            'radius_lg': '12px',
            'radius_xl': '16px'
        }
    
    async def _extract_shadow_tokens(self, figma_json: Dict[str, Any]) -> Dict[str, Any]:
        """Extract shadow design tokens"""
        return {
            'shadow_sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
            'shadow_md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            'shadow_lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
        }
    
    def _extract_bounds(self, node: Dict[str, Any]) -> Dict[str, float]:
        """Extract bounds information from node"""
        absolute_bounding_box = node.get('absoluteBoundingBox', {})
        return {
            'x': absolute_bounding_box.get('x', 0),
            'y': absolute_bounding_box.get('y', 0),
            'width': absolute_bounding_box.get('width', 0),
            'height': absolute_bounding_box.get('height', 0)
        }
    
    async def _extract_node_styles(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Extract styles from a node"""
        styles = {}
        
        # Extract fill styles
        fills = node.get('fills', [])
        if fills:
            styles['fills'] = fills
        
        # Extract stroke styles
        strokes = node.get('strokes', [])
        if strokes:
            styles['strokes'] = strokes
        
        # Extract effects (shadows, blurs)
        effects = node.get('effects', [])
        if effects:
            styles['effects'] = effects
        
        return styles
    
    async def _extract_node_tokens(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Extract design tokens from a node"""
        tokens = {}
        
        # Extract color tokens
        fills = node.get('fills', [])
        for fill in fills:
            if fill.get('type') == 'SOLID':
                color = fill.get('color', {})
                if color:
                    tokens['color'] = {
                        'r': color.get('r', 0),
                        'g': color.get('g', 0),
                        'b': color.get('b', 0),
                        'a': color.get('a', 1)
                    }
        
        # Extract typography tokens
        style = node.get('style', {})
        if style:
            tokens['typography'] = {
                'font_family': style.get('fontFamily', ''),
                'font_size': style.get('fontSize', 0),
                'font_weight': style.get('fontWeight', 400),
                'line_height': style.get('lineHeightPx', 0)
            }
        
        return tokens
    
    def _extract_node_image_refs(self, node: Dict[str, Any]) -> List[str]:
        """Extract image references from a node"""
        image_refs = []
        
        # Check fills for images
        fills = node.get('fills', [])
        for fill in fills:
            if fill.get('type') == 'IMAGE':
                image_ref = fill.get('imageRef', '')
                if image_ref:
                    image_refs.append(image_ref)
        
        return image_refs
    
    def _extract_layout_constraints(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Extract layout constraints from a node"""
        constraints = node.get('constraints', {})
        layout_align = node.get('layoutAlign', '')
        layout_grow = node.get('layoutGrow', 0)
        
        return {
            'constraints': constraints,
            'layout_align': layout_align,
            'layout_grow': layout_grow
        }
    
    async def _extract_image_references(self, figma_json: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all image references from the Figma JSON"""
        image_refs = []
        
        # This would traverse the entire JSON to find image references
        # For now, return empty list
        return image_refs
    
    async def _build_layout_hierarchy(self, components: List[ComponentNode]) -> Dict[str, Any]:
        """Build layout hierarchy from components"""
        hierarchy = {
            'root': None,
            'components': {},
            'relationships': []
        }
        
        # Build component map
        for component in components:
            hierarchy['components'][component.node_id] = {
                'name': component.name,
                'type': component.component_type,
                'parent_id': component.parent_id,
                'children': []
            }
        
        # Build relationships
        for component in components:
            if component.parent_id and component.parent_id in hierarchy['components']:
                hierarchy['components'][component.parent_id]['children'].append(component.node_id)
            else:
                hierarchy['root'] = component.node_id
        
        return hierarchy
    
    # Component classification methods
    def _classify_button(self, node: Dict[str, Any]) -> bool:
        """Classify if node is a button"""
        name = node.get('name', '').lower()
        return 'button' in name or 'btn' in name
    
    def _classify_input(self, node: Dict[str, Any]) -> bool:
        """Classify if node is an input"""
        name = node.get('name', '').lower()
        return 'input' in name or 'field' in name or 'textfield' in name
    
    def _classify_card(self, node: Dict[str, Any]) -> bool:
        """Classify if node is a card"""
        name = node.get('name', '').lower()
        return 'card' in name or 'container' in name
    
    def _classify_layout(self, node: Dict[str, Any]) -> bool:
        """Classify if node is a layout component"""
        node_type = node.get('type', '')
        return node_type in ['FRAME', 'GROUP']
    
    def _classify_navigation(self, node: Dict[str, Any]) -> bool:
        """Classify if node is navigation"""
        name = node.get('name', '').lower()
        return 'nav' in name or 'menu' in name or 'header' in name or 'footer' in name
    
    def _classify_text(self, node: Dict[str, Any]) -> bool:
        """Classify if node is text"""
        node_type = node.get('type', '')
        return node_type == 'TEXT'
    
    def _classify_image(self, node: Dict[str, Any]) -> bool:
        """Classify if node is an image"""
        fills = node.get('fills', [])
        return any(fill.get('type') == 'IMAGE' for fill in fills)
