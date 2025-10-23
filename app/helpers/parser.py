"""
Code Parser
Basic code block parsing utilities
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class CodeBlock:
    """Represents a parsed code block"""
    language: str
    content: str
    start_line: int
    end_line: int
    metadata: Optional[Dict] = None


class CodeParser:
    """Basic code block parser"""
    
    def __init__(self):
        self.code_block_patterns = [
            # Markdown code blocks
            r'```(\w+)?\n(.*?)\n```',
            # HTML code blocks
            r'<code[^>]*class="language-(\w+)"[^>]*>(.*?)</code>',
            # Generic code blocks
            r'<pre[^>]*><code[^>]*>(.*?)</code></pre>',
            # Inline code
            r'`([^`]+)`'
        ]
    
    def parse_code_blocks(self, text: str) -> List[CodeBlock]:
        """Parse code blocks from text"""
        code_blocks = []
        
        for pattern in self.code_block_patterns:
            matches = re.finditer(pattern, text, re.DOTALL | re.MULTILINE)
            
            for match in matches:
                groups = match.groups()
                
                if len(groups) >= 2:
                    language = groups[0] or 'text'
                    content = groups[1].strip()
                else:
                    language = 'text'
                    content = groups[0].strip()
                
                if content:
                    # Calculate line numbers
                    start_line = text[:match.start()].count('\n') + 1
                    end_line = start_line + content.count('\n')
                    
                    code_block = CodeBlock(
                        language=language,
                        content=content,
                        start_line=start_line,
                        end_line=end_line
                    )
                    
                    code_blocks.append(code_block)
        
        return code_blocks
    
    def extract_language_from_content(self, content: str) -> str:
        """Extract programming language from content"""
        # Check for language-specific patterns
        if 'import ' in content or 'from ' in content or 'def ' in content:
            return 'python'
        elif 'function ' in content or 'const ' in content or 'let ' in content:
            return 'javascript'
        elif 'interface ' in content or 'type ' in content:
            return 'typescript'
        elif '<html>' in content or '<div>' in content:
            return 'html'
        elif '{' in content and '}' in content and ':' in content:
            return 'css'
        elif 'SELECT' in content or 'INSERT' in content or 'UPDATE' in content:
            return 'sql'
        else:
            return 'text'
    
    def clean_code_content(self, content: str) -> str:
        """Clean and normalize code content"""
        # Remove leading/trailing whitespace
        content = content.strip()
        
        # Remove common prefixes/suffixes
        content = re.sub(r'^```\w*\n', '', content)
        content = re.sub(r'\n```$', '', content)
        
        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        return content
    
    def validate_code_block(self, code_block: CodeBlock) -> bool:
        """Validate a code block"""
        if not code_block.content.strip():
            return False
        
        # Check for minimum content length
        if len(code_block.content.strip()) < 3:
            return False
        
        # Check for balanced brackets (basic check)
        if not self._check_balanced_brackets(code_block.content):
            return False
        
        return True
    
    def get_code_statistics(self, code_blocks: List[CodeBlock]) -> Dict:
        """Get statistics about code blocks"""
        if not code_blocks:
            return {
                "total_blocks": 0,
                "languages": {},
                "total_lines": 0,
                "total_characters": 0
            }
        
        languages = {}
        total_lines = 0
        total_characters = 0
        
        for block in code_blocks:
            # Count languages
            languages[block.language] = languages.get(block.language, 0) + 1
            
            # Count lines and characters
            lines = block.content.count('\n') + 1
            total_lines += lines
            total_characters += len(block.content)
        
        return {
            "total_blocks": len(code_blocks),
            "languages": languages,
            "total_lines": total_lines,
            "total_characters": total_characters,
            "average_lines_per_block": total_lines / len(code_blocks)
        }
    
    def _check_balanced_brackets(self, content: str) -> bool:
        """Check if brackets are balanced"""
        brackets = {'(': ')', '[': ']', '{': '}'}
        stack = []
        
        for char in content:
            if char in brackets:
                stack.append(char)
            elif char in brackets.values():
                if not stack:
                    return False
                if brackets[stack.pop()] != char:
                    return False
        
        return len(stack) == 0
    
    def merge_adjacent_blocks(self, code_blocks: List[CodeBlock]) -> List[CodeBlock]:
        """Merge adjacent code blocks of the same language"""
        if not code_blocks:
            return []
        
        merged = []
        current_block = code_blocks[0]
        
        for block in code_blocks[1:]:
            if (block.language == current_block.language and 
                block.start_line == current_block.end_line + 1):
                # Merge blocks
                current_block.content += '\n' + block.content
                current_block.end_line = block.end_line
            else:
                # Add current block and start new one
                merged.append(current_block)
                current_block = block
        
        merged.append(current_block)
        return merged
    
    def filter_by_language(self, code_blocks: List[CodeBlock], language: str) -> List[CodeBlock]:
        """Filter code blocks by language"""
        return [block for block in code_blocks if block.language == language]
    
    def filter_by_size(self, code_blocks: List[CodeBlock], min_lines: int = 1, max_lines: int = None) -> List[CodeBlock]:
        """Filter code blocks by size"""
        filtered = []
        
        for block in code_blocks:
            lines = block.content.count('\n') + 1
            
            if lines >= min_lines:
                if max_lines is None or lines <= max_lines:
                    filtered.append(block)
        
        return filtered
