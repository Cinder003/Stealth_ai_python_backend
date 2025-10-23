"""
Code Formatter
Handles code formatting and beautification
"""

import re
import subprocess
import tempfile
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class FormattingStyle(Enum):
    """Code formatting style enumeration"""
    PEP8 = "pep8"
    BLACK = "black"
    PRETTIER = "prettier"
    ESLINT = "eslint"
    STANDARD = "standard"


@dataclass
class FormattingResult:
    """Result of code formatting"""
    success: bool
    formatted_code: str
    original_code: str
    changes_made: List[str]
    errors: List[str]
    warnings: List[str]


class CodeFormatter:
    """Handles code formatting and beautification"""
    
    def __init__(self):
        self.supported_languages = {
            'python': self._format_python,
            'javascript': self._format_javascript,
            'typescript': self._format_typescript,
            'html': self._format_html,
            'css': self._format_css,
            'json': self._format_json,
            'yaml': self._format_yaml,
            'sql': self._format_sql
        }
        
        self.formatting_tools = {
            'python': ['black', 'autopep8', 'yapf'],
            'javascript': ['prettier', 'eslint'],
            'typescript': ['prettier', 'eslint'],
            'html': ['prettier', 'js-beautify'],
            'css': ['prettier', 'js-beautify'],
            'json': ['prettier', 'jq'],
            'yaml': ['prettier', 'yamlfmt'],
            'sql': ['sqlfluff', 'sqlformat']
        }
    
    def format_code(
        self,
        code: str,
        language: str,
        style: Optional[FormattingStyle] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> FormattingResult:
        """Format code using appropriate formatter"""
        if language not in self.supported_languages:
            return FormattingResult(
                success=False,
                formatted_code=code,
                original_code=code,
                changes_made=[],
                errors=[f"Unsupported language: {language}"],
                warnings=[]
            )
        
        formatter_func = self.supported_languages[language]
        
        try:
            result = formatter_func(code, style, options)
            return result
        except Exception as e:
            return FormattingResult(
                success=False,
                formatted_code=code,
                original_code=code,
                changes_made=[],
                errors=[f"Formatting failed: {str(e)}"],
                warnings=[]
            )
    
    def format_multiple_files(
        self,
        files: Dict[str, str],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, FormattingResult]:
        """Format multiple files"""
        results = {}
        
        for file_path, code in files.items():
            # Detect language from file extension
            language = self._detect_language_from_path(file_path)
            
            # Format code
            result = self.format_code(code, language, options=options)
            results[file_path] = result
        
        return results
    
    def check_formatting(
        self,
        code: str,
        language: str,
        style: Optional[FormattingStyle] = None
    ) -> bool:
        """Check if code is properly formatted"""
        result = self.format_code(code, language, style)
        return result.success and result.formatted_code == code
    
    def get_formatting_suggestions(
        self,
        code: str,
        language: str
    ) -> List[str]:
        """Get formatting suggestions for code"""
        suggestions = []
        
        if language == 'python':
            suggestions.extend(self._get_python_suggestions(code))
        elif language == 'javascript':
            suggestions.extend(self._get_javascript_suggestions(code))
        elif language == 'html':
            suggestions.extend(self._get_html_suggestions(code))
        elif language == 'css':
            suggestions.extend(self._get_css_suggestions(code))
        
        return suggestions
    
    def _format_python(
        self,
        code: str,
        style: Optional[FormattingStyle] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> FormattingResult:
        """Format Python code"""
        if style is None:
            style = FormattingStyle.BLACK
        
        # Try external formatters first
        if style == FormattingStyle.BLACK:
            result = self._format_with_black(code, options)
            if result.success:
                return result
        
        if style == FormattingStyle.PEP8:
            result = self._format_with_autopep8(code, options)
            if result.success:
                return result
        
        # Fallback to basic formatting
        return self._format_python_basic(code, options)
    
    def _format_javascript(
        self,
        code: str,
        style: Optional[FormattingStyle] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> FormattingResult:
        """Format JavaScript code"""
        if style is None:
            style = FormattingStyle.PRETTIER
        
        # Try external formatters first
        if style == FormattingStyle.PRETTIER:
            result = self._format_with_prettier(code, 'javascript', options)
            if result.success:
                return result
        
        if style == FormattingStyle.ESLINT:
            result = self._format_with_eslint(code, options)
            if result.success:
                return result
        
        # Fallback to basic formatting
        return self._format_javascript_basic(code, options)
    
    def _format_typescript(
        self,
        code: str,
        style: Optional[FormattingStyle] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> FormattingResult:
        """Format TypeScript code"""
        if style is None:
            style = FormattingStyle.PRETTIER
        
        # Try external formatters first
        if style == FormattingStyle.PRETTIER:
            result = self._format_with_prettier(code, 'typescript', options)
            if result.success:
                return result
        
        # Fallback to basic formatting
        return self._format_typescript_basic(code, options)
    
    def _format_html(
        self,
        code: str,
        style: Optional[FormattingStyle] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> FormattingResult:
        """Format HTML code"""
        # Try external formatters first
        result = self._format_with_prettier(code, 'html', options)
        if result.success:
            return result
        
        # Fallback to basic formatting
        return self._format_html_basic(code, options)
    
    def _format_css(
        self,
        code: str,
        style: Optional[FormattingStyle] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> FormattingResult:
        """Format CSS code"""
        # Try external formatters first
        result = self._format_with_prettier(code, 'css', options)
        if result.success:
            return result
        
        # Fallback to basic formatting
        return self._format_css_basic(code, options)
    
    def _format_json(
        self,
        code: str,
        style: Optional[FormattingStyle] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> FormattingResult:
        """Format JSON code"""
        try:
            import json
            
            # Parse and reformat JSON
            data = json.loads(code)
            formatted = json.dumps(data, indent=2, sort_keys=True)
            
            return FormattingResult(
                success=True,
                formatted_code=formatted,
                original_code=code,
                changes_made=["Applied JSON formatting"],
                errors=[],
                warnings=[]
            )
        
        except json.JSONDecodeError as e:
            return FormattingResult(
                success=False,
                formatted_code=code,
                original_code=code,
                changes_made=[],
                errors=[f"Invalid JSON: {str(e)}"],
                warnings=[]
            )
    
    def _format_yaml(
        self,
        code: str,
        style: Optional[FormattingStyle] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> FormattingResult:
        """Format YAML code"""
        try:
            import yaml
            
            # Parse and reformat YAML
            data = yaml.safe_load(code)
            formatted = yaml.dump(data, default_flow_style=False, indent=2)
            
            return FormattingResult(
                success=True,
                formatted_code=formatted,
                original_code=code,
                changes_made=["Applied YAML formatting"],
                errors=[],
                warnings=[]
            )
        
        except yaml.YAMLError as e:
            return FormattingResult(
                success=False,
                formatted_code=code,
                original_code=code,
                changes_made=[],
                errors=[f"Invalid YAML: {str(e)}"],
                warnings=[]
            )
    
    def _format_sql(
        self,
        code: str,
        style: Optional[FormattingStyle] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> FormattingResult:
        """Format SQL code"""
        # Basic SQL formatting
        formatted = self._format_sql_basic(code)
        
        return FormattingResult(
            success=True,
            formatted_code=formatted,
            original_code=code,
            changes_made=["Applied SQL formatting"],
            errors=[],
            warnings=[]
        )
    
    # External formatter methods
    
    def _format_with_black(
        self,
        code: str,
        options: Optional[Dict[str, Any]] = None
    ) -> FormattingResult:
        """Format Python code with Black"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Run Black
            cmd = ['black', '--quiet', temp_file]
            if options and 'line_length' in options:
                cmd.extend(['--line-length', str(options['line_length'])])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                with open(temp_file, 'r') as f:
                    formatted_code = f.read()
                
                os.unlink(temp_file)
                
                return FormattingResult(
                    success=True,
                    formatted_code=formatted_code,
                    original_code=code,
                    changes_made=["Applied Black formatting"],
                    errors=[],
                    warnings=[]
                )
            else:
                os.unlink(temp_file)
                return FormattingResult(
                    success=False,
                    formatted_code=code,
                    original_code=code,
                    changes_made=[],
                    errors=[f"Black failed: {result.stderr}"],
                    warnings=[]
                )
        
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            return FormattingResult(
                success=False,
                formatted_code=code,
                original_code=code,
                changes_made=[],
                errors=[f"Black formatting failed: {str(e)}"],
                warnings=[]
            )
    
    def _format_with_autopep8(
        self,
        code: str,
        options: Optional[Dict[str, Any]] = None
    ) -> FormattingResult:
        """Format Python code with autopep8"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Run autopep8
            cmd = ['autopep8', '--in-place', temp_file]
            if options and 'max_line_length' in options:
                cmd.extend(['--max-line-length', str(options['max_line_length'])])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                with open(temp_file, 'r') as f:
                    formatted_code = f.read()
                
                os.unlink(temp_file)
                
                return FormattingResult(
                    success=True,
                    formatted_code=formatted_code,
                    original_code=code,
                    changes_made=["Applied autopep8 formatting"],
                    errors=[],
                    warnings=[]
                )
            else:
                os.unlink(temp_file)
                return FormattingResult(
                    success=False,
                    formatted_code=code,
                    original_code=code,
                    changes_made=[],
                    errors=[f"autopep8 failed: {result.stderr}"],
                    warnings=[]
                )
        
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            return FormattingResult(
                success=False,
                formatted_code=code,
                original_code=code,
                changes_made=[],
                errors=[f"autopep8 formatting failed: {str(e)}"],
                warnings=[]
            )
    
    def _format_with_prettier(
        self,
        code: str,
        language: str,
        options: Optional[Dict[str, Any]] = None
    ) -> FormattingResult:
        """Format code with Prettier"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{language}', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Run Prettier
            cmd = ['prettier', '--write', temp_file]
            if options and 'tab_width' in options:
                cmd.extend(['--tab-width', str(options['tab_width'])])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                with open(temp_file, 'r') as f:
                    formatted_code = f.read()
                
                os.unlink(temp_file)
                
                return FormattingResult(
                    success=True,
                    formatted_code=formatted_code,
                    original_code=code,
                    changes_made=["Applied Prettier formatting"],
                    errors=[],
                    warnings=[]
                )
            else:
                os.unlink(temp_file)
                return FormattingResult(
                    success=False,
                    formatted_code=code,
                    original_code=code,
                    changes_made=[],
                    errors=[f"Prettier failed: {result.stderr}"],
                    warnings=[]
                )
        
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            return FormattingResult(
                success=False,
                formatted_code=code,
                original_code=code,
                changes_made=[],
                errors=[f"Prettier formatting failed: {str(e)}"],
                warnings=[]
            )
    
    def _format_with_eslint(
        self,
        code: str,
        options: Optional[Dict[str, Any]] = None
    ) -> FormattingResult:
        """Format JavaScript code with ESLint"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Run ESLint with --fix
            cmd = ['eslint', '--fix', temp_file]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            with open(temp_file, 'r') as f:
                formatted_code = f.read()
            
            os.unlink(temp_file)
            
            return FormattingResult(
                success=True,
                formatted_code=formatted_code,
                original_code=code,
                changes_made=["Applied ESLint formatting"],
                errors=[],
                warnings=[]
            )
        
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            return FormattingResult(
                success=False,
                formatted_code=code,
                original_code=code,
                changes_made=[],
                errors=[f"ESLint formatting failed: {str(e)}"],
                warnings=[]
            )
    
    # Basic formatter methods
    
    def _format_python_basic(self, code: str, options: Optional[Dict[str, Any]] = None) -> FormattingResult:
        """Basic Python formatting"""
        changes = []
        
        # Normalize line endings
        formatted = code.replace('\r\n', '\n').replace('\r', '\n')
        if formatted != code:
            changes.append("Normalized line endings")
        
        # Remove trailing whitespace
        lines = formatted.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        formatted = '\n'.join(cleaned_lines)
        if formatted != code:
            changes.append("Removed trailing whitespace")
        
        # Ensure final newline
        if formatted and not formatted.endswith('\n'):
            formatted += '\n'
            changes.append("Added final newline")
        
        return FormattingResult(
            success=True,
            formatted_code=formatted,
            original_code=code,
            changes_made=changes,
            errors=[],
            warnings=[]
        )
    
    def _format_javascript_basic(self, code: str, options: Optional[Dict[str, Any]] = None) -> FormattingResult:
        """Basic JavaScript formatting"""
        changes = []
        
        # Normalize line endings
        formatted = code.replace('\r\n', '\n').replace('\r', '\n')
        if formatted != code:
            changes.append("Normalized line endings")
        
        # Basic indentation fix
        lines = formatted.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue
            
            # Decrease indent for closing braces
            if stripped.startswith('}') or stripped.startswith(']'):
                indent_level = max(0, indent_level - 1)
            
            # Add indented line
            formatted_lines.append('  ' * indent_level + stripped)
            
            # Increase indent for opening braces
            if stripped.endswith('{') or stripped.endswith('['):
                indent_level += 1
        
        formatted = '\n'.join(formatted_lines)
        if formatted != code:
            changes.append("Applied basic indentation")
        
        return FormattingResult(
            success=True,
            formatted_code=formatted,
            original_code=code,
            changes_made=changes,
            errors=[],
            warnings=[]
        )
    
    def _format_typescript_basic(self, code: str, options: Optional[Dict[str, Any]] = None) -> FormattingResult:
        """Basic TypeScript formatting"""
        # TypeScript formatting is similar to JavaScript
        return self._format_javascript_basic(code, options)
    
    def _format_html_basic(self, code: str, options: Optional[Dict[str, Any]] = None) -> FormattingResult:
        """Basic HTML formatting"""
        changes = []
        
        # Normalize line endings
        formatted = code.replace('\r\n', '\n').replace('\r', '\n')
        if formatted != code:
            changes.append("Normalized line endings")
        
        # Basic HTML indentation
        lines = formatted.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue
            
            # Decrease indent for closing tags
            if stripped.startswith('</'):
                indent_level = max(0, indent_level - 1)
            
            # Add indented line
            formatted_lines.append('  ' * indent_level + stripped)
            
            # Increase indent for opening tags (but not self-closing)
            if (stripped.startswith('<') and 
                not stripped.startswith('</') and 
                not stripped.endswith('/>') and
                not stripped.endswith('>')):
                indent_level += 1
        
        formatted = '\n'.join(formatted_lines)
        if formatted != code:
            changes.append("Applied basic HTML indentation")
        
        return FormattingResult(
            success=True,
            formatted_code=formatted,
            original_code=code,
            changes_made=changes,
            errors=[],
            warnings=[]
        )
    
    def _format_css_basic(self, code: str, options: Optional[Dict[str, Any]] = None) -> FormattingResult:
        """Basic CSS formatting"""
        changes = []
        
        # Normalize line endings
        formatted = code.replace('\r\n', '\n').replace('\r', '\n')
        if formatted != code:
            changes.append("Normalized line endings")
        
        # Basic CSS formatting
        formatted = re.sub(r'{\s*', ' {\n  ', formatted)
        formatted = re.sub(r';\s*', ';\n', formatted)
        formatted = re.sub(r'}\s*', '\n}\n', formatted)
        
        if formatted != code:
            changes.append("Applied basic CSS formatting")
        
        return FormattingResult(
            success=True,
            formatted_code=formatted,
            original_code=code,
            changes_made=changes,
            errors=[],
            warnings=[]
        )
    
    def _format_sql_basic(self, code: str) -> str:
        """Basic SQL formatting"""
        # Convert to uppercase for keywords
        keywords = ['SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']
        
        formatted = code
        for keyword in keywords:
            formatted = re.sub(rf'\b{keyword.lower()}\b', keyword, formatted, flags=re.IGNORECASE)
        
        # Add line breaks after keywords
        formatted = re.sub(r'\b(SELECT|FROM|WHERE|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\b', r'\n\1', formatted)
        
        # Clean up multiple newlines
        formatted = re.sub(r'\n+', '\n', formatted)
        formatted = formatted.strip()
        
        return formatted
    
    # Suggestion methods
    
    def _get_python_suggestions(self, code: str) -> List[str]:
        """Get Python formatting suggestions"""
        suggestions = []
        
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > 79:
                suggestions.append(f"Line {i}: Line too long ({len(line)} > 79)")
            
            # Check for trailing whitespace
            if line.rstrip() != line:
                suggestions.append(f"Line {i}: Trailing whitespace")
            
            # Check for mixed tabs and spaces
            if '\t' in line and ' ' in line:
                suggestions.append(f"Line {i}: Mixed tabs and spaces")
        
        return suggestions
    
    def _get_javascript_suggestions(self, code: str) -> List[str]:
        """Get JavaScript formatting suggestions"""
        suggestions = []
        
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for semicolons
            stripped = line.strip()
            if (stripped and 
                not stripped.startswith('//') and 
                not stripped.startswith('/*') and
                not stripped.endswith(';') and
                not stripped.endswith('{') and
                not stripped.endswith('}') and
                not stripped.startswith('if') and
                not stripped.startswith('for') and
                not stripped.startswith('while')):
                suggestions.append(f"Line {i}: Consider adding semicolon")
        
        return suggestions
    
    def _get_html_suggestions(self, code: str) -> List[str]:
        """Get HTML formatting suggestions"""
        suggestions = []
        
        # Check for missing alt attributes
        if '<img' in code and 'alt=' not in code:
            suggestions.append("Images should have alt attributes")
        
        # Check for proper indentation
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                if '<' in line and not line.startswith('<!'):
                    suggestions.append(f"Line {i}: Consider proper indentation")
        
        return suggestions
    
    def _get_css_suggestions(self, code: str) -> List[str]:
        """Get CSS formatting suggestions"""
        suggestions = []
        
        # Check for vendor prefixes
        if 'transform' in code and '-webkit-transform' not in code:
            suggestions.append("Consider adding vendor prefixes for better browser compatibility")
        
        # Check for shorthand properties
        if 'margin-top' in code and 'margin-bottom' in code:
            suggestions.append("Consider using shorthand margin property")
        
        return suggestions
    
    def _detect_language_from_path(self, file_path: str) -> str:
        """Detect language from file path"""
        import os
        
        extension = os.path.splitext(file_path)[1].lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.html': 'html',
            '.htm': 'html',
            '.css': 'css',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.sql': 'sql'
        }
        
        return language_map.get(extension, 'text')
