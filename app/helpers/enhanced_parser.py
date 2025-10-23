"""
Enhanced Parser
Advanced parsing with AI-powered content analysis
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from .parser import CodeParser, CodeBlock


class ContentType(Enum):
    """Content type enumeration"""
    CODE = "code"
    TEXT = "text"
    MIXED = "mixed"
    DOCUMENTATION = "documentation"
    CONFIGURATION = "configuration"


@dataclass
class ParsingContext:
    """Context for parsing operations"""
    source_type: str
    expected_languages: List[str]
    confidence_threshold: float
    enable_ai_analysis: bool
    metadata: Dict[str, Any]


class EnhancedParser:
    """Enhanced parser with AI-powered analysis"""
    
    def __init__(self):
        self.basic_parser = CodeParser()
        self.language_patterns = self._build_language_patterns()
        self.context_patterns = self._build_context_patterns()
    
    def parse_with_context(
        self,
        text: str,
        context: ParsingContext
    ) -> List[CodeBlock]:
        """Parse with contextual information"""
        # Pre-process based on context
        processed_text = self._preprocess_with_context(text, context)
        
        # Parse using appropriate strategy
        if context.enable_ai_analysis:
            return self._parse_with_ai_analysis(processed_text, context)
        else:
            return self._parse_with_patterns(processed_text, context)
    
    def parse_mixed_content(self, text: str) -> List[CodeBlock]:
        """Parse mixed content with intelligent separation"""
        # Analyze content structure
        content_analysis = self._analyze_content_structure(text)
        
        # Separate different content types
        separated_content = self._separate_content_types(text, content_analysis)
        
        # Parse each content type
        all_blocks = []
        for content_type, content in separated_content.items():
            if content_type == ContentType.CODE:
                blocks = self._parse_code_content(content)
            elif content_type == ContentType.DOCUMENTATION:
                blocks = self._parse_documentation_content(content)
            elif content_type == ContentType.CONFIGURATION:
                blocks = self._parse_configuration_content(content)
            else:
                blocks = self._parse_text_content(content)
            
            all_blocks.extend(blocks)
        
        return self._merge_and_optimize_blocks(all_blocks)
    
    def parse_with_language_detection(self, text: str) -> List[CodeBlock]:
        """Parse with automatic language detection"""
        # Detect languages in text
        detected_languages = self._detect_languages_in_text(text)
        
        # Create context for each detected language
        contexts = []
        for language in detected_languages:
            context = ParsingContext(
                source_type="mixed",
                expected_languages=[language],
                confidence_threshold=0.7,
                enable_ai_analysis=True,
                metadata={"detected_language": language}
            )
            contexts.append(context)
        
        # Parse with each context
        all_blocks = []
        for context in contexts:
            blocks = self.parse_with_context(text, context)
            all_blocks.extend(blocks)
        
        return self._deduplicate_blocks(all_blocks)
    
    def parse_with_semantic_analysis(self, text: str) -> List[CodeBlock]:
        """Parse with semantic analysis"""
        # Analyze semantic structure
        semantic_structure = self._analyze_semantic_structure(text)
        
        # Extract code blocks based on semantic boundaries
        blocks = []
        for section in semantic_structure:
            if section["type"] == "code":
                code_blocks = self._extract_code_from_section(section)
                blocks.extend(code_blocks)
        
        return blocks
    
    def _preprocess_with_context(self, text: str, context: ParsingContext) -> str:
        """Preprocess text based on context"""
        processed = text
        
        # Apply context-specific preprocessing
        if context.source_type == "markdown":
            processed = self._preprocess_markdown(processed)
        elif context.source_type == "html":
            processed = self._preprocess_html(processed)
        elif context.source_type == "json":
            processed = self._preprocess_json(processed)
        
        # Apply language-specific preprocessing
        for language in context.expected_languages:
            processed = self._preprocess_for_language(processed, language)
        
        return processed
    
    def _parse_with_ai_analysis(self, text: str, context: ParsingContext) -> List[CodeBlock]:
        """Parse with AI-powered analysis"""
        # This would integrate with an AI service for content analysis
        # For now, use enhanced pattern matching
        
        blocks = []
        
        # Analyze text structure
        structure = self._analyze_text_structure(text)
        
        # Extract code blocks using structure information
        for segment in structure:
            if segment["type"] == "code":
                code_blocks = self._extract_code_from_segment(segment, context)
                blocks.extend(code_blocks)
        
        return blocks
    
    def _parse_with_patterns(self, text: str, context: ParsingContext) -> List[CodeBlock]:
        """Parse using pattern matching with context"""
        blocks = []
        
        # Use context-specific patterns
        patterns = self._get_context_patterns(context)
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            
            for match in matches:
                block = self._create_block_from_match(match, context)
                if block:
                    blocks.append(block)
        
        return blocks
    
    def _analyze_content_structure(self, text: str) -> Dict[str, Any]:
        """Analyze the structure of mixed content"""
        analysis = {
            "total_lines": len(text.split('\n')),
            "total_chars": len(text),
            "code_indicators": 0,
            "documentation_indicators": 0,
            "configuration_indicators": 0,
            "sections": []
        }
        
        lines = text.split('\n')
        current_section = {"type": "text", "start": 0, "content": []}
        
        for i, line in enumerate(lines):
            line_type = self._classify_line_type(line)
            
            if line_type != current_section["type"]:
                # End current section
                current_section["end"] = i
                current_section["content"] = '\n'.join(current_section["content"])
                analysis["sections"].append(current_section)
                
                # Start new section
                current_section = {
                    "type": line_type,
                    "start": i,
                    "content": [line]
                }
            else:
                current_section["content"].append(line)
        
        # Add final section
        current_section["end"] = len(lines)
        current_section["content"] = '\n'.join(current_section["content"])
        analysis["sections"].append(current_section)
        
        return analysis
    
    def _separate_content_types(self, text: str, analysis: Dict[str, Any]) -> Dict[ContentType, str]:
        """Separate content by type"""
        separated = {}
        
        for section in analysis["sections"]:
            content_type = ContentType(section["type"])
            if content_type not in separated:
                separated[content_type] = []
            separated[content_type].append(section["content"])
        
        # Join sections of the same type
        for content_type in separated:
            separated[content_type] = '\n'.join(separated[content_type])
        
        return separated
    
    def _classify_line_type(self, line: str) -> str:
        """Classify a line as code, documentation, or text"""
        stripped = line.strip()
        
        if not stripped:
            return "text"
        
        # Check for code indicators
        code_indicators = [
            r'^\s*(def|class|function|const|let|var|import|from)\s+',
            r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*[=\(]',
            r'^\s*[{}]',
            r'^\s*#',
            r'^\s*//',
            r'^\s*/\*',
            r'^\s*<[a-zA-Z]',
            r'^\s*</',
            r'^\s*(SELECT|INSERT|UPDATE|DELETE)\s+'
        ]
        
        for pattern in code_indicators:
            if re.match(pattern, stripped):
                return "code"
        
        # Check for documentation indicators
        doc_indicators = [
            r'^\s*#\s+',  # Markdown headers
            r'^\s*\*\s+',  # JSDoc comments
            r'^\s*"""',  # Python docstrings
            r'^\s*/\*\*',  # JavaDoc comments
        ]
        
        for pattern in doc_indicators:
            if re.match(pattern, stripped):
                return "documentation"
        
        # Check for configuration indicators
        config_indicators = [
            r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*[:=]',
            r'^\s*<[a-zA-Z][^>]*>',
            r'^\s*"[^"]*"\s*:',
        ]
        
        for pattern in config_indicators:
            if re.match(pattern, stripped):
                return "configuration"
        
        return "text"
    
    def _parse_code_content(self, content: str) -> List[CodeBlock]:
        """Parse code content"""
        return self.basic_parser.parse_code_blocks(content)
    
    def _parse_documentation_content(self, content: str) -> List[CodeBlock]:
        """Parse documentation content"""
        blocks = []
        
        # Look for code examples in documentation
        code_patterns = [
            r'```(\w+)?\n(.*?)\n```',
            r'`([^`]+)`',
            r'<code[^>]*>(.*?)</code>'
        ]
        
        for pattern in code_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            
            for match in matches:
                groups = match.groups()
                
                if len(groups) >= 2:
                    language = groups[0] or 'text'
                    code_content = groups[1].strip()
                else:
                    language = 'text'
                    code_content = groups[0].strip()
                
                if code_content:
                    start_line = content[:match.start()].count('\n') + 1
                    end_line = start_line + code_content.count('\n')
                    
                    block = CodeBlock(
                        language=language,
                        content=code_content,
                        start_line=start_line,
                        end_line=end_line,
                        metadata={"source": "documentation"}
                    )
                    blocks.append(block)
        
        return blocks
    
    def _parse_configuration_content(self, content: str) -> List[CodeBlock]:
        """Parse configuration content"""
        blocks = []
        
        # Look for code in configuration files
        lines = content.split('\n')
        current_block = []
        current_language = 'text'
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if self._looks_like_code_in_config(stripped):
                if not current_block:
                    current_language = self._detect_language_from_config_line(stripped)
                current_block.append(line)
            else:
                if current_block:
                    # End of code block
                    code_content = '\n'.join(current_block)
                    
                    block = CodeBlock(
                        language=current_language,
                        content=code_content,
                        start_line=i - len(current_block) + 1,
                        end_line=i,
                        metadata={"source": "configuration"}
                    )
                    blocks.append(block)
                    
                    current_block = []
        
        # Handle final block
        if current_block:
            code_content = '\n'.join(current_block)
            block = CodeBlock(
                language=current_language,
                content=code_content,
                start_line=len(lines) - len(current_block) + 1,
                end_line=len(lines),
                metadata={"source": "configuration"}
            )
            blocks.append(block)
        
        return blocks
    
    def _parse_text_content(self, content: str) -> List[CodeBlock]:
        """Parse text content for embedded code"""
        blocks = []
        
        # Look for inline code
        inline_pattern = r'`([^`]+)`'
        matches = re.finditer(inline_pattern, content)
        
        for match in matches:
            code_content = match.group(1).strip()
            
            if self._looks_like_code(code_content):
                start_line = content[:match.start()].count('\n') + 1
                
                block = CodeBlock(
                    language='text',
                    content=code_content,
                    start_line=start_line,
                    end_line=start_line,
                    metadata={"source": "text", "inline": True}
                )
                blocks.append(block)
        
        return blocks
    
    def _looks_like_code_in_config(self, line: str) -> bool:
        """Check if line looks like code in configuration context"""
        code_patterns = [
            r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*[=\(]',
            r'^\s*[{}]',
            r'^\s*#',
            r'^\s*//',
            r'^\s*<[a-zA-Z]',
            r'^\s*</'
        ]
        
        for pattern in code_patterns:
            if re.match(pattern, line):
                return True
        
        return False
    
    def _detect_language_from_config_line(self, line: str) -> str:
        """Detect language from configuration line"""
        if re.match(r'^\s*(def|class|import|from)\s+', line):
            return 'python'
        elif re.match(r'^\s*(function|const|let|var)\s+', line):
            return 'javascript'
        elif re.match(r'^\s*<[a-zA-Z]', line):
            return 'html'
        else:
            return 'text'
    
    def _looks_like_code(self, text: str) -> bool:
        """Check if text looks like code"""
        if len(text) < 3:
            return False
        
        # Check for code patterns
        code_patterns = [
            r'[a-zA-Z_][a-zA-Z0-9_]*\s*[=\(]',
            r'[{}]',
            r'#',
            r'//',
            r'<[a-zA-Z]',
            r'</'
        ]
        
        for pattern in code_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def _merge_and_optimize_blocks(self, blocks: List[CodeBlock]) -> List[CodeBlock]:
        """Merge and optimize code blocks"""
        if not blocks:
            return []
        
        # Remove duplicates
        unique_blocks = self._deduplicate_blocks(blocks)
        
        # Merge adjacent blocks of the same language
        merged_blocks = self._merge_adjacent_blocks(unique_blocks)
        
        # Optimize block content
        optimized_blocks = []
        for block in merged_blocks:
            optimized_block = self._optimize_block(block)
            if optimized_block:
                optimized_blocks.append(optimized_block)
        
        return optimized_blocks
    
    def _deduplicate_blocks(self, blocks: List[CodeBlock]) -> List[CodeBlock]:
        """Remove duplicate blocks"""
        seen = set()
        unique_blocks = []
        
        for block in blocks:
            # Create a hash of the block content
            block_hash = hash(block.content.strip())
            
            if block_hash not in seen:
                seen.add(block_hash)
                unique_blocks.append(block)
        
        return unique_blocks
    
    def _merge_adjacent_blocks(self, blocks: List[CodeBlock]) -> List[CodeBlock]:
        """Merge adjacent blocks of the same language"""
        if not blocks:
            return []
        
        # Sort by start line
        sorted_blocks = sorted(blocks, key=lambda b: b.start_line)
        merged = [sorted_blocks[0]]
        
        for block in sorted_blocks[1:]:
            last_merged = merged[-1]
            
            # Check if blocks can be merged
            if (block.language == last_merged.language and
                block.start_line <= last_merged.end_line + 1):
                # Merge blocks
                last_merged.content += '\n' + block.content
                last_merged.end_line = max(last_merged.end_line, block.end_line)
            else:
                merged.append(block)
        
        return merged
    
    def _optimize_block(self, block: CodeBlock) -> Optional[CodeBlock]:
        """Optimize a code block"""
        # Clean content
        content = block.content.strip()
        
        # Remove common artifacts
        content = re.sub(r'^```\w*\n', '', content)
        content = re.sub(r'\n```$', '', content)
        content = re.sub(r'^`([^`]+)`$', r'\1', content)
        
        if not content:
            return None
        
        # Update block
        block.content = content
        
        return block
    
    def _build_language_patterns(self) -> Dict[str, List[str]]:
        """Build language-specific patterns"""
        return {
            'python': [
                r'^\s*(def|class|import|from)\s+',
                r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*[=\(]',
                r'^\s*#',
                r'^\s*"""',
                r'^\s*if\s+',
                r'^\s*for\s+',
                r'^\s*while\s+'
            ],
            'javascript': [
                r'^\s*(function|const|let|var)\s+',
                r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*[=\(]',
                r'^\s*//',
                r'^\s*/\*',
                r'^\s*if\s+\(',
                r'^\s*for\s+\(',
                r'^\s*while\s+\('
            ],
            'html': [
                r'^\s*<[a-zA-Z]',
                r'^\s*</',
                r'^\s*<!DOCTYPE',
                r'^\s*<!--'
            ],
            'css': [
                r'^\s*[a-zA-Z-]+\s*{',
                r'^\s*@',
                r'^\s*/\*'
            ]
        }
    
    def _build_context_patterns(self) -> Dict[str, List[str]]:
        """Build context-specific patterns"""
        return {
            'markdown': [
                r'```(\w+)?\n(.*?)\n```',
                r'`([^`]+)`'
            ],
            'html': [
                r'<pre[^>]*><code[^>]*>(.*?)</code></pre>',
                r'<code[^>]*>(.*?)</code>'
            ],
            'json': [
                r'"code":\s*"([^"]+)"',
                r'"content":\s*"([^"]+)"'
            ]
        }
    
    def _get_context_patterns(self, context: ParsingContext) -> List[str]:
        """Get patterns for a specific context"""
        patterns = []
        
        # Add context-specific patterns
        if context.source_type in self.context_patterns:
            patterns.extend(self.context_patterns[context.source_type])
        
        # Add language-specific patterns
        for language in context.expected_languages:
            if language in self.language_patterns:
                patterns.extend(self.language_patterns[language])
        
        return patterns
    
    def _create_block_from_match(self, match, context: ParsingContext) -> Optional[CodeBlock]:
        """Create a code block from a regex match"""
        try:
            groups = match.groups()
            
            if len(groups) >= 2:
                language = groups[0] or 'text'
                content = groups[1].strip()
            else:
                language = 'text'
                content = groups[0].strip()
            
            if not content:
                return None
            
            # Detect language if not specified
            if language == 'text':
                language = self._detect_language_from_content(content)
            
            start_line = match.string[:match.start()].count('\n') + 1
            end_line = start_line + content.count('\n')
            
            return CodeBlock(
                language=language,
                content=content,
                start_line=start_line,
                end_line=end_line,
                metadata={"context": context.source_type}
            )
        
        except Exception:
            return None
    
    def _detect_language_from_content(self, content: str) -> str:
        """Detect language from content"""
        # Use basic parser's language detection
        return self.basic_parser.extract_language_from_content(content)
    
    def _preprocess_markdown(self, text: str) -> str:
        """Preprocess markdown text"""
        # Fix common markdown issues
        text = re.sub(r'```([^`]*)$', r'```\1\n```', text, flags=re.MULTILINE)
        text = re.sub(r'```\n', '```text\n', text)
        return text
    
    def _preprocess_html(self, text: str) -> str:
        """Preprocess HTML text"""
        # Fix common HTML issues
        text = re.sub(r'<code([^>]*)>([^<]*)', r'<code\1>\2</code>', text)
        return text
    
    def _preprocess_json(self, text: str) -> str:
        """Preprocess JSON text"""
        # Fix common JSON issues
        text = re.sub(r'\\n', '\n', text)
        text = re.sub(r'\\t', '\t', text)
        return text
    
    def _preprocess_for_language(self, text: str, language: str) -> str:
        """Preprocess text for specific language"""
        if language == 'python':
            # Fix Python-specific issues
            text = re.sub(r'^\s*>>>\s*', '', text, flags=re.MULTILINE)
        elif language == 'javascript':
            # Fix JavaScript-specific issues
            text = re.sub(r'^\s*>\s*', '', text, flags=re.MULTILINE)
        
        return text
    
    def _analyze_text_structure(self, text: str) -> List[Dict[str, Any]]:
        """Analyze text structure"""
        # This would be more sophisticated in practice
        # For now, use basic analysis
        structure = []
        
        lines = text.split('\n')
        current_section = {"type": "text", "start": 0, "content": []}
        
        for i, line in enumerate(lines):
            line_type = self._classify_line_type(line)
            
            if line_type != current_section["type"]:
                # End current section
                current_section["end"] = i
                current_section["content"] = '\n'.join(current_section["content"])
                structure.append(current_section)
                
                # Start new section
                current_section = {
                    "type": line_type,
                    "start": i,
                    "content": [line]
                }
            else:
                current_section["content"].append(line)
        
        # Add final section
        current_section["end"] = len(lines)
        current_section["content"] = '\n'.join(current_section["content"])
        structure.append(current_section)
        
        return structure
    
    def _extract_code_from_segment(self, segment: Dict[str, Any], context: ParsingContext) -> List[CodeBlock]:
        """Extract code from a text segment"""
        content = segment["content"]
        
        # Use basic parser for code extraction
        blocks = self.basic_parser.parse_code_blocks(content)
        
        # Adjust line numbers
        for block in blocks:
            block.start_line += segment["start"]
            block.end_line += segment["start"]
        
        return blocks
    
    def _analyze_semantic_structure(self, text: str) -> List[Dict[str, Any]]:
        """Analyze semantic structure of text"""
        # This would use more sophisticated NLP in practice
        # For now, use basic analysis
        structure = []
        
        lines = text.split('\n')
        current_section = {"type": "text", "start": 0, "content": []}
        
        for i, line in enumerate(lines):
            line_type = self._classify_line_type(line)
            
            if line_type != current_section["type"]:
                # End current section
                current_section["end"] = i
                current_section["content"] = '\n'.join(current_section["content"])
                structure.append(current_section)
                
                # Start new section
                current_section = {
                    "type": line_type,
                    "start": i,
                    "content": [line]
                }
            else:
                current_section["content"].append(line)
        
        # Add final section
        current_section["end"] = len(lines)
        current_section["content"] = '\n'.join(current_section["content"])
        structure.append(current_section)
        
        return structure
    
    def _extract_code_from_section(self, section: Dict[str, Any]) -> List[CodeBlock]:
        """Extract code from a semantic section"""
        content = section["content"]
        
        # Use basic parser for code extraction
        blocks = self.basic_parser.parse_code_blocks(content)
        
        # Adjust line numbers
        for block in blocks:
            block.start_line += section["start"]
            block.end_line += section["start"]
        
        return blocks
    
    def _detect_languages_in_text(self, text: str) -> List[str]:
        """Detect languages present in text"""
        languages = set()
        
        # Use language patterns to detect languages
        for language, patterns in self.language_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.MULTILINE):
                    languages.add(language)
        
        return list(languages)
