"""
Integrated Parser
Multi-strategy code parsing with fallback mechanisms
"""

import re
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

from .parser import CodeParser, CodeBlock


class ParseStrategy(Enum):
    """Parsing strategy enumeration"""
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    XML = "xml"
    REGEX = "regex"
    AST = "ast"
    HEURISTIC = "heuristic"


@dataclass
class ParseResult:
    """Result of parsing operation"""
    success: bool
    code_blocks: List[CodeBlock]
    strategy_used: ParseStrategy
    confidence: float
    errors: List[str]
    metadata: Dict


class IntegratedParser:
    """Integrated parser with multiple strategies"""
    
    def __init__(self):
        self.basic_parser = CodeParser()
        self.strategies = {
            ParseStrategy.MARKDOWN: self._parse_markdown,
            ParseStrategy.HTML: self._parse_html,
            ParseStrategy.JSON: self._parse_json,
            ParseStrategy.XML: self._parse_xml,
            ParseStrategy.REGEX: self._parse_regex,
            ParseStrategy.AST: self._parse_ast,
            ParseStrategy.HEURISTIC: self._parse_heuristic
        }
        self.strategy_weights = {
            ParseStrategy.MARKDOWN: 0.9,
            ParseStrategy.HTML: 0.8,
            ParseStrategy.JSON: 0.7,
            ParseStrategy.XML: 0.6,
            ParseStrategy.REGEX: 0.5,
            ParseStrategy.AST: 0.8,
            ParseStrategy.HEURISTIC: 0.3
        }
    
    def parse(self, text: str, preferred_strategy: Optional[ParseStrategy] = None) -> ParseResult:
        """Parse text using integrated strategies"""
        if not text.strip():
            return ParseResult(
                success=False,
                code_blocks=[],
                strategy_used=ParseStrategy.HEURISTIC,
                confidence=0.0,
                errors=["Empty input text"],
                metadata={}
            )
        
        # Try preferred strategy first
        if preferred_strategy and preferred_strategy in self.strategies:
            result = self._try_strategy(text, preferred_strategy)
            if result.success and result.confidence > 0.7:
                return result
        
        # Try all strategies and pick the best one
        results = []
        for strategy in self.strategies:
            result = self._try_strategy(text, strategy)
            results.append(result)
        
        # Select best result
        best_result = max(results, key=lambda r: r.confidence)
        
        return best_result
    
    def parse_with_fallback(self, text: str) -> List[CodeBlock]:
        """Parse with automatic fallback between strategies"""
        result = self.parse(text)
        
        if result.success:
            return result.code_blocks
        
        # Fallback to basic parser
        try:
            basic_blocks = self.basic_parser.parse_code_blocks(text)
            return basic_blocks
        except Exception:
            return []
    
    def _try_strategy(self, text: str, strategy: ParseStrategy) -> ParseResult:
        """Try a specific parsing strategy"""
        try:
            parser_func = self.strategies[strategy]
            code_blocks = parser_func(text)
            
            # Calculate confidence
            confidence = self._calculate_confidence(code_blocks, strategy)
            
            # Validate results
            valid_blocks = [block for block in code_blocks if self.basic_parser.validate_code_block(block)]
            
            return ParseResult(
                success=len(valid_blocks) > 0,
                code_blocks=valid_blocks,
                strategy_used=strategy,
                confidence=confidence,
                errors=[],
                metadata={"total_blocks": len(code_blocks), "valid_blocks": len(valid_blocks)}
            )
            
        except Exception as e:
            return ParseResult(
                success=False,
                code_blocks=[],
                strategy_used=strategy,
                confidence=0.0,
                errors=[str(e)],
                metadata={}
            )
    
    def _parse_markdown(self, text: str) -> List[CodeBlock]:
        """Parse markdown code blocks"""
        code_blocks = []
        
        # Standard markdown code blocks
        pattern = r'```(\w+)?\n(.*?)\n```'
        matches = re.finditer(pattern, text, re.DOTALL)
        
        for match in matches:
            language = match.group(1) or 'text'
            content = match.group(2).strip()
            
            if content:
                start_line = text[:match.start()].count('\n') + 1
                end_line = start_line + content.count('\n')
                
                code_block = CodeBlock(
                    language=language,
                    content=content,
                    start_line=start_line,
                    end_line=end_line,
                    metadata={"source": "markdown"}
                )
                code_blocks.append(code_block)
        
        return code_blocks
    
    def _parse_html(self, text: str) -> List[CodeBlock]:
        """Parse HTML code blocks"""
        code_blocks = []
        
        # HTML code blocks with language classes
        patterns = [
            r'<pre[^>]*><code[^>]*class="[^"]*language-(\w+)[^"]*"[^>]*>(.*?)</code></pre>',
            r'<code[^>]*class="[^"]*language-(\w+)[^"]*"[^>]*>(.*?)</code>',
            r'<pre[^>]*><code[^>]*>(.*?)</code></pre>'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.DOTALL)
            
            for match in matches:
                groups = match.groups()
                
                if len(groups) >= 2:
                    language = groups[0] or 'text'
                    content = groups[1].strip()
                else:
                    language = 'text'
                    content = groups[0].strip()
                
                if content:
                    start_line = text[:match.start()].count('\n') + 1
                    end_line = start_line + content.count('\n')
                    
                    code_block = CodeBlock(
                        language=language,
                        content=content,
                        start_line=start_line,
                        end_line=end_line,
                        metadata={"source": "html"}
                    )
                    code_blocks.append(code_block)
        
        return code_blocks
    
    def _parse_json(self, text: str) -> List[CodeBlock]:
        """Parse JSON-formatted code blocks"""
        code_blocks = []
        
        try:
            import json
            data = json.loads(text)
            
            if isinstance(data, dict) and 'code_blocks' in data:
                for i, block_data in enumerate(data['code_blocks']):
                    if isinstance(block_data, dict):
                        language = block_data.get('language', 'text')
                        content = block_data.get('content', '')
                        
                        if content:
                            code_block = CodeBlock(
                                language=language,
                                content=content,
                                start_line=i + 1,
                                end_line=i + 1 + content.count('\n'),
                                metadata={"source": "json", "index": i}
                            )
                            code_blocks.append(code_block)
        
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
        
        return code_blocks
    
    def _parse_xml(self, text: str) -> List[CodeBlock]:
        """Parse XML-formatted code blocks"""
        code_blocks = []
        
        # XML code blocks
        pattern = r'<codeblock[^>]*language="(\w+)"[^>]*>(.*?)</codeblock>'
        matches = re.finditer(pattern, text, re.DOTALL)
        
        for match in matches:
            language = match.group(1)
            content = match.group(2).strip()
            
            if content:
                start_line = text[:match.start()].count('\n') + 1
                end_line = start_line + content.count('\n')
                
                code_block = CodeBlock(
                    language=language,
                    content=content,
                    start_line=start_line,
                    end_line=end_line,
                    metadata={"source": "xml"}
                )
                code_blocks.append(code_block)
        
        return code_blocks
    
    def _parse_regex(self, text: str) -> List[CodeBlock]:
        """Parse using custom regex patterns"""
        code_blocks = []
        
        # Custom regex patterns for various formats
        patterns = [
            # Python docstring format
            r'"""\s*(\w+)\s*\n(.*?)\n"""',
            # JavaScript comment format
            r'/\*\s*(\w+)\s*\n(.*?)\n\*/',
            # Generic code markers
            r'#\s*CODE:\s*(\w+)\s*\n(.*?)\n#\s*END',
            # Indented code blocks
            r'^(\s{4,})(.*?)$'
        ]
        
        for pattern in patterns:
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
                    start_line = text[:match.start()].count('\n') + 1
                    end_line = start_line + content.count('\n')
                    
                    code_block = CodeBlock(
                        language=language,
                        content=content,
                        start_line=start_line,
                        end_line=end_line,
                        metadata={"source": "regex", "pattern": pattern}
                    )
                    code_blocks.append(code_block)
        
        return code_blocks
    
    def _parse_ast(self, text: str) -> List[CodeBlock]:
        """Parse using AST analysis"""
        code_blocks = []
        
        try:
            import ast
            
            # Try to parse as Python code
            try:
                tree = ast.parse(text)
                
                # Extract function and class definitions
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        # Extract the source code for this node
                        start_line = node.lineno
                        end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
                        
                        lines = text.split('\n')
                        content = '\n'.join(lines[start_line-1:end_line])
                        
                        code_block = CodeBlock(
                            language='python',
                            content=content,
                            start_line=start_line,
                            end_line=end_line,
                            metadata={"source": "ast", "type": type(node).__name__}
                        )
                        code_blocks.append(code_block)
            
            except SyntaxError:
                # Not valid Python, try other languages
                pass
        
        except ImportError:
            pass
        
        return code_blocks
    
    def _parse_heuristic(self, text: str) -> List[CodeBlock]:
        """Parse using heuristic analysis"""
        code_blocks = []
        
        lines = text.split('\n')
        current_block = []
        current_language = 'text'
        in_code_block = False
        
        for i, line in enumerate(lines):
            # Detect code block start
            if not in_code_block:
                if self._is_code_line(line):
                    in_code_block = True
                    current_language = self._detect_language_from_line(line)
                    current_block = [line]
                continue
            
            # Detect code block end
            if in_code_block:
                if self._is_code_line(line):
                    current_block.append(line)
                else:
                    # End of code block
                    if current_block:
                        content = '\n'.join(current_block)
                        
                        code_block = CodeBlock(
                            language=current_language,
                            content=content,
                            start_line=i - len(current_block) + 1,
                            end_line=i,
                            metadata={"source": "heuristic"}
                        )
                        code_blocks.append(code_block)
                    
                    current_block = []
                    in_code_block = False
        
        # Handle case where code block goes to end of text
        if current_block:
            content = '\n'.join(current_block)
            code_block = CodeBlock(
                language=current_language,
                content=content,
                start_line=len(lines) - len(current_block) + 1,
                end_line=len(lines),
                metadata={"source": "heuristic"}
            )
            code_blocks.append(code_block)
        
        return code_blocks
    
    def _is_code_line(self, line: str) -> bool:
        """Check if line looks like code"""
        line = line.strip()
        
        if not line:
            return False
        
        # Check for common code patterns
        code_indicators = [
            r'^\s*(def|class|function|const|let|var|import|from)\s+',
            r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*[=\(]',
            r'^\s*[{}]',
            r'^\s*#',
            r'^\s*//',
            r'^\s*/\*',
            r'^\s*<[a-zA-Z]',
            r'^\s*</',
            r'^\s*SELECT\s+',
            r'^\s*INSERT\s+',
            r'^\s*UPDATE\s+',
            r'^\s*DELETE\s+'
        ]
        
        for pattern in code_indicators:
            if re.match(pattern, line):
                return True
        
        return False
    
    def _detect_language_from_line(self, line: str) -> str:
        """Detect programming language from a line"""
        line = line.strip()
        
        if re.match(r'^\s*(def|class|import|from)\s+', line):
            return 'python'
        elif re.match(r'^\s*(function|const|let|var)\s+', line):
            return 'javascript'
        elif re.match(r'^\s*(interface|type)\s+', line):
            return 'typescript'
        elif re.match(r'^\s*<[a-zA-Z]', line):
            return 'html'
        elif re.match(r'^\s*[a-zA-Z-]+\s*{', line):
            return 'css'
        elif re.match(r'^\s*(SELECT|INSERT|UPDATE|DELETE)\s+', line):
            return 'sql'
        else:
            return 'text'
    
    def _calculate_confidence(self, code_blocks: List[CodeBlock], strategy: ParseStrategy) -> float:
        """Calculate confidence score for parsing result"""
        if not code_blocks:
            return 0.0
        
        base_confidence = self.strategy_weights.get(strategy, 0.5)
        
        # Adjust based on block quality
        quality_score = 0.0
        for block in code_blocks:
            if self.basic_parser.validate_code_block(block):
                quality_score += 1.0
        
        quality_score /= len(code_blocks)
        
        # Adjust based on content length
        total_content = sum(len(block.content) for block in code_blocks)
        length_score = min(1.0, total_content / 1000.0)  # Normalize to 1000 chars
        
        # Combine scores
        confidence = (base_confidence * 0.4 + quality_score * 0.4 + length_score * 0.2)
        
        return min(1.0, confidence)
