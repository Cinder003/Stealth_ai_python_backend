"""
Robust Parser
Advanced code parsing with error recovery and multiple delimiters
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

from .parser import CodeParser, CodeBlock


class DelimiterType(Enum):
    """Code block delimiter types"""
    MARKDOWN = "markdown"
    HTML = "html"
    INLINE = "inline"
    CUSTOM = "custom"
    INDENTED = "indented"


@dataclass
class DelimiterPattern:
    """Represents a delimiter pattern"""
    name: str
    start_pattern: str
    end_pattern: str
    language_group: int
    content_group: int
    delimiter_type: DelimiterType
    flags: int = re.MULTILINE | re.DOTALL


class RobustParser:
    """Robust parser with error recovery and multiple delimiters"""
    
    def __init__(self):
        self.basic_parser = CodeParser()
        self.logger = logging.getLogger(__name__)
        
        # Define delimiter patterns
        self.delimiter_patterns = [
            # Markdown code blocks
            DelimiterPattern(
                name="markdown_triple_backticks",
                start_pattern=r'```(\w+)?\n',
                end_pattern=r'\n```',
                language_group=1,
                content_group=0,
                delimiter_type=DelimiterType.MARKDOWN
            ),
            # Markdown inline code
            DelimiterPattern(
                name="markdown_inline",
                start_pattern=r'`([^`]+)`',
                end_pattern=r'',
                language_group=0,
                content_group=1,
                delimiter_type=DelimiterType.INLINE
            ),
            # HTML code blocks
            DelimiterPattern(
                name="html_pre_code",
                start_pattern=r'<pre[^>]*><code[^>]*class="[^"]*language-(\w+)[^"]*"[^>]*>',
                end_pattern=r'</code></pre>',
                language_group=1,
                content_group=0,
                delimiter_type=DelimiterType.HTML
            ),
            # HTML simple code
            DelimiterPattern(
                name="html_code",
                start_pattern=r'<code[^>]*class="[^"]*language-(\w+)[^"]*"[^>]*>',
                end_pattern=r'</code>',
                language_group=1,
                content_group=0,
                delimiter_type=DelimiterType.HTML
            ),
            # Custom delimiters
            DelimiterPattern(
                name="custom_start_end",
                start_pattern=r'<!--\s*CODE:\s*(\w+)\s*-->',
                end_pattern=r'<!--\s*END\s*-->',
                language_group=1,
                content_group=0,
                delimiter_type=DelimiterType.CUSTOM
            ),
            # Indented code blocks
            DelimiterPattern(
                name="indented",
                start_pattern=r'^(\s{4,})(.*?)$',
                end_pattern=r'',
                language_group=0,
                content_group=2,
                delimiter_type=DelimiterType.INDENTED
            )
        ]
        
        # Error recovery patterns
        self.error_recovery_patterns = [
            r'```[^`]*$',  # Unclosed markdown
            r'<code[^>]*>[^<]*$',  # Unclosed HTML
            r'`[^`]*$',  # Unclosed inline
        ]
    
    def parse_robust(self, text: str, max_attempts: int = 3) -> List[CodeBlock]:
        """Parse with robust error recovery"""
        all_blocks = []
        remaining_text = text
        
        for attempt in range(max_attempts):
            try:
                blocks = self._parse_with_delimiters(remaining_text)
                all_blocks.extend(blocks)
                
                # Remove parsed content from remaining text
                remaining_text = self._remove_parsed_content(remaining_text, blocks)
                
                if not remaining_text.strip():
                    break
                    
            except Exception as e:
                self.logger.warning(f"Parse attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_attempts - 1:
                    # Final attempt with error recovery
                    blocks = self._parse_with_error_recovery(remaining_text)
                    all_blocks.extend(blocks)
        
        # Post-process and validate blocks
        return self._post_process_blocks(all_blocks)
    
    def parse_with_delimiters(self, text: str, delimiter_types: Optional[List[DelimiterType]] = None) -> List[CodeBlock]:
        """Parse using specific delimiter types"""
        if delimiter_types is None:
            delimiter_types = [dt for dt in DelimiterType]
        
        # Filter patterns by delimiter types
        patterns = [p for p in self.delimiter_patterns if p.delimiter_type in delimiter_types]
        
        return self._parse_with_patterns(text, patterns)
    
    def parse_markdown_robust(self, text: str) -> List[CodeBlock]:
        """Robust markdown parsing with error recovery"""
        blocks = []
        
        # Handle malformed markdown
        text = self._fix_malformed_markdown(text)
        
        # Parse with multiple markdown patterns
        markdown_patterns = [
            p for p in self.delimiter_patterns 
            if p.delimiter_type == DelimiterType.MARKDOWN
        ]
        
        blocks.extend(self._parse_with_patterns(text, markdown_patterns))
        
        # Handle unclosed blocks
        unclosed_blocks = self._find_unclosed_blocks(text)
        blocks.extend(unclosed_blocks)
        
        return self._post_process_blocks(blocks)
    
    def parse_html_robust(self, text: str) -> List[CodeBlock]:
        """Robust HTML parsing with error recovery"""
        blocks = []
        
        # Handle malformed HTML
        text = self._fix_malformed_html(text)
        
        # Parse with HTML patterns
        html_patterns = [
            p for p in self.delimiter_patterns 
            if p.delimiter_type == DelimiterType.HTML
        ]
        
        blocks.extend(self._parse_with_patterns(text, html_patterns))
        
        return self._post_process_blocks(blocks)
    
    def parse_mixed_content(self, text: str) -> List[CodeBlock]:
        """Parse mixed content with multiple delimiter types"""
        all_blocks = []
        
        # Try each delimiter type
        for delimiter_type in DelimiterType:
            try:
                blocks = self.parse_with_delimiters(text, [delimiter_type])
                all_blocks.extend(blocks)
            except Exception as e:
                self.logger.warning(f"Failed to parse with {delimiter_type}: {str(e)}")
        
        # Remove duplicates and merge overlapping blocks
        return self._merge_overlapping_blocks(all_blocks)
    
    def _parse_with_delimiters(self, text: str) -> List[CodeBlock]:
        """Parse using all available delimiters"""
        return self._parse_with_patterns(text, self.delimiter_patterns)
    
    def _parse_with_patterns(self, text: str, patterns: List[DelimiterPattern]) -> List[CodeBlock]:
        """Parse using specific patterns"""
        blocks = []
        
        for pattern in patterns:
            try:
                if pattern.end_pattern:
                    # Pattern with start and end
                    full_pattern = f"{pattern.start_pattern}(.*?){pattern.end_pattern}"
                    matches = re.finditer(full_pattern, text, pattern.flags)
                else:
                    # Pattern without end (like inline code)
                    matches = re.finditer(pattern.start_pattern, text, pattern.flags)
                
                for match in matches:
                    try:
                        # Extract language and content
                        if pattern.language_group > 0 and pattern.language_group <= len(match.groups()):
                            language = match.group(pattern.language_group) or 'text'
                        else:
                            language = 'text'
                        
                        if pattern.content_group > 0 and pattern.content_group <= len(match.groups()):
                            content = match.group(pattern.content_group).strip()
                        else:
                            # For patterns without content group, use the full match
                            content = match.group(0).strip()
                        
                        if content:
                            # Calculate line numbers
                            start_line = text[:match.start()].count('\n') + 1
                            end_line = start_line + content.count('\n')
                            
                            block = CodeBlock(
                                language=language,
                                content=content,
                                start_line=start_line,
                                end_line=end_line,
                                metadata={
                                    "delimiter": pattern.name,
                                    "type": pattern.delimiter_type.value
                                }
                            )
                            blocks.append(block)
                    
                    except Exception as e:
                        self.logger.warning(f"Failed to process match for pattern {pattern.name}: {str(e)}")
                        continue
            
            except Exception as e:
                self.logger.warning(f"Failed to parse with pattern {pattern.name}: {str(e)}")
                continue
        
        return blocks
    
    def _parse_with_error_recovery(self, text: str) -> List[CodeBlock]:
        """Parse with error recovery mechanisms"""
        blocks = []
        
        # Try to fix common issues
        fixed_text = self._fix_common_issues(text)
        
        # Use basic parser as fallback
        try:
            basic_blocks = self.basic_parser.parse_code_blocks(fixed_text)
            blocks.extend(basic_blocks)
        except Exception as e:
            self.logger.warning(f"Basic parser fallback failed: {str(e)}")
        
        # Try heuristic parsing
        heuristic_blocks = self._parse_heuristic(fixed_text)
        blocks.extend(heuristic_blocks)
        
        return blocks
    
    def _fix_malformed_markdown(self, text: str) -> str:
        """Fix common markdown issues"""
        # Fix unclosed code blocks
        text = re.sub(r'```([^`]*)$', r'```\1\n```', text, flags=re.MULTILINE)
        
        # Fix missing language specifiers
        text = re.sub(r'```\n', '```text\n', text)
        
        # Fix mixed backticks
        text = re.sub(r'``([^`]+)``', r'`\1`', text)
        
        return text
    
    def _fix_malformed_html(self, text: str) -> str:
        """Fix common HTML issues"""
        # Fix unclosed tags
        text = re.sub(r'<code([^>]*)>([^<]*)', r'<code\1>\2</code>', text)
        text = re.sub(r'<pre([^>]*)>([^<]*)', r'<pre\1>\2</pre>', text)
        
        # Fix missing closing tags
        text = re.sub(r'<code([^>]*)>([^<]*)</pre>', r'<code\1>\2</code></pre>', text)
        
        return text
    
    def _fix_common_issues(self, text: str) -> str:
        """Fix common parsing issues"""
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Fix mixed indentation
        text = re.sub(r'^(\s*)\t', r'\1    ', text, flags=re.MULTILINE)
        
        # Fix trailing whitespace
        text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)
        
        return text
    
    def _find_unclosed_blocks(self, text: str) -> List[CodeBlock]:
        """Find and handle unclosed code blocks"""
        blocks = []
        
        # Look for unclosed markdown blocks
        unclosed_pattern = r'```(\w+)?\n(.*?)$'
        matches = re.finditer(unclosed_pattern, text, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            language = match.group(1) or 'text'
            content = match.group(2).strip()
            
            if content:
                start_line = text[:match.start()].count('\n') + 1
                end_line = start_line + content.count('\n')
                
                block = CodeBlock(
                    language=language,
                    content=content,
                    start_line=start_line,
                    end_line=end_line,
                    metadata={"unclosed": True, "recovered": True}
                )
                blocks.append(block)
        
        return blocks
    
    def _parse_heuristic(self, text: str) -> List[CodeBlock]:
        """Heuristic parsing for unrecognized patterns"""
        blocks = []
        lines = text.split('\n')
        
        current_block = []
        current_language = 'text'
        in_code_block = False
        indent_level = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if not stripped:
                if in_code_block:
                    current_block.append(line)
                continue
            
            # Detect code start
            if not in_code_block:
                if self._looks_like_code(line):
                    in_code_block = True
                    current_language = self._detect_language_heuristic(line)
                    current_block = [line]
                    indent_level = len(line) - len(line.lstrip())
                continue
            
            # Check if we're still in a code block
            current_indent = len(line) - len(line.lstrip())
            
            if (current_indent >= indent_level and 
                (self._looks_like_code(line) or line.startswith(' ') or not stripped)):
                current_block.append(line)
            else:
                # End of code block
                if current_block:
                    content = '\n'.join(current_block)
                    
                    block = CodeBlock(
                        language=current_language,
                        content=content,
                        start_line=i - len(current_block) + 1,
                        end_line=i,
                        metadata={"heuristic": True}
                    )
                    blocks.append(block)
                
                current_block = []
                in_code_block = False
                
                # Check if this line starts a new code block
                if self._looks_like_code(line):
                    in_code_block = True
                    current_language = self._detect_language_heuristic(line)
                    current_block = [line]
                    indent_level = current_indent
        
        # Handle final block
        if current_block:
            content = '\n'.join(current_block)
            block = CodeBlock(
                language=current_language,
                content=content,
                start_line=len(lines) - len(current_block) + 1,
                end_line=len(lines),
                metadata={"heuristic": True}
            )
            blocks.append(block)
        
        return blocks
    
    def _looks_like_code(self, line: str) -> bool:
        """Check if line looks like code"""
        stripped = line.strip()
        
        if not stripped:
            return False
        
        # Common code patterns
        code_patterns = [
            r'^\s*(def|class|function|const|let|var|import|from)\s+',
            r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*[=\(]',
            r'^\s*[{}]',
            r'^\s*#',
            r'^\s*//',
            r'^\s*/\*',
            r'^\s*<[a-zA-Z]',
            r'^\s*</',
            r'^\s*(SELECT|INSERT|UPDATE|DELETE)\s+',
            r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*:\s*',
            r'^\s*return\s+',
            r'^\s*if\s+\(',
            r'^\s*for\s+\(',
            r'^\s*while\s+\('
        ]
        
        for pattern in code_patterns:
            if re.match(pattern, stripped):
                return True
        
        return False
    
    def _detect_language_heuristic(self, line: str) -> str:
        """Detect language using heuristics"""
        stripped = line.strip()
        
        if re.match(r'^\s*(def|class|import|from)\s+', stripped):
            return 'python'
        elif re.match(r'^\s*(function|const|let|var)\s+', stripped):
            return 'javascript'
        elif re.match(r'^\s*(interface|type)\s+', stripped):
            return 'typescript'
        elif re.match(r'^\s*<[a-zA-Z]', stripped):
            return 'html'
        elif re.match(r'^\s*[a-zA-Z-]+\s*{', stripped):
            return 'css'
        elif re.match(r'^\s*(SELECT|INSERT|UPDATE|DELETE)\s+', stripped):
            return 'sql'
        else:
            return 'text'
    
    def _remove_parsed_content(self, text: str, blocks: List[CodeBlock]) -> str:
        """Remove parsed content from text"""
        # This is a simplified implementation
        # In practice, you'd want to track exact positions
        remaining = text
        
        for block in blocks:
            # Remove the block content
            remaining = remaining.replace(block.content, '', 1)
        
        return remaining
    
    def _merge_overlapping_blocks(self, blocks: List[CodeBlock]) -> List[CodeBlock]:
        """Merge overlapping code blocks"""
        if not blocks:
            return []
        
        # Sort by start line
        sorted_blocks = sorted(blocks, key=lambda b: b.start_line)
        merged = [sorted_blocks[0]]
        
        for block in sorted_blocks[1:]:
            last_merged = merged[-1]
            
            # Check for overlap
            if block.start_line <= last_merged.end_line:
                # Merge blocks
                if block.end_line > last_merged.end_line:
                    last_merged.end_line = block.end_line
                    last_merged.content = self._merge_content(
                        last_merged.content, 
                        block.content
                    )
            else:
                merged.append(block)
        
        return merged
    
    def _merge_content(self, content1: str, content2: str) -> str:
        """Merge two content strings"""
        # Simple merge - in practice, you'd want smarter merging
        return content1 + '\n' + content2
    
    def _post_process_blocks(self, blocks: List[CodeBlock]) -> List[CodeBlock]:
        """Post-process and validate blocks"""
        processed = []
        
        for block in blocks:
            # Clean content
            block.content = block.content.strip()
            
            # Validate block
            if self.basic_parser.validate_code_block(block):
                processed.append(block)
            else:
                # Try to fix the block
                fixed_block = self._fix_block(block)
                if fixed_block and self.basic_parser.validate_code_block(fixed_block):
                    processed.append(fixed_block)
        
        return processed
    
    def _fix_block(self, block: CodeBlock) -> Optional[CodeBlock]:
        """Try to fix a malformed block"""
        try:
            # Clean content
            content = block.content.strip()
            
            # Remove common artifacts
            content = re.sub(r'^```\w*\n', '', content)
            content = re.sub(r'\n```$', '', content)
            content = re.sub(r'^`([^`]+)`$', r'\1', content)
            
            if content:
                return CodeBlock(
                    language=block.language,
                    content=content,
                    start_line=block.start_line,
                    end_line=block.end_line,
                    metadata=block.metadata
                )
        except Exception:
            pass
        
        return None
