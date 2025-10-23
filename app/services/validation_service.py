"""
Validation Service
Handles code validation and quality checks
"""

import ast
import re
import subprocess
import tempfile
import os
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from app.core.config import get_settings

settings = get_settings()


class ValidationService:
    """Service for code validation and quality checks"""
    
    def __init__(self):
        self.supported_languages = {
            'python': self._validate_python,
            'javascript': self._validate_javascript,
            'typescript': self._validate_typescript,
            'html': self._validate_html,
            'css': self._validate_css,
            'json': self._validate_json
        }
    
    async def validate_code(
        self,
        code: str,
        language: str,
        framework: Optional[str] = None,
        rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate code for syntax and quality"""
        try:
            # Get validation function
            validator = self.supported_languages.get(language.lower())
            if not validator:
                return {
                    "valid": False,
                    "errors": [f"Unsupported language: {language}"],
                    "warnings": [],
                    "suggestions": []
                }
            
            # Run validation
            result = await validator(code, framework, rules)
            
            return result
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation failed: {str(e)}"],
                "warnings": [],
                "suggestions": []
            }
    
    async def validate_files(
        self,
        files: Dict[str, str],
        rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate multiple files"""
        try:
            results = {
                "valid_files": [],
                "invalid_files": [],
                "total_files": len(files),
                "valid_count": 0,
                "invalid_count": 0
            }
            
            for file_path, content in files.items():
                # Determine language from file extension
                language = self._get_language_from_path(file_path)
                
                # Validate file
                validation_result = await self.validate_code(
                    code=content,
                    language=language,
                    rules=rules
                )
                
                file_result = {
                    "file_path": file_path,
                    "language": language,
                    "validation": validation_result
                }
                
                if validation_result["valid"]:
                    results["valid_files"].append(file_result)
                    results["valid_count"] += 1
                else:
                    results["invalid_files"].append(file_result)
                    results["invalid_count"] += 1
            
            return results
            
        except Exception as e:
            return {
                "valid_files": [],
                "invalid_files": [],
                "total_files": 0,
                "valid_count": 0,
                "invalid_count": 0,
                "error": str(e)
            }
    
    async def get_quality_score(
        self,
        code: str,
        language: str
    ) -> float:
        """Get code quality score (0.0-1.0)"""
        try:
            validation_result = await self.validate_code(code, language)
            
            if not validation_result["valid"]:
                return 0.0
            
            # Calculate score based on various factors
            score = 1.0
            
            # Deduct for warnings
            warning_count = len(validation_result.get("warnings", []))
            score -= warning_count * 0.1
            
            # Deduct for suggestions
            suggestion_count = len(validation_result.get("suggestions", []))
            score -= suggestion_count * 0.05
            
            # Check code complexity
            complexity_score = await self._calculate_complexity_score(code, language)
            score *= complexity_score
            
            return max(0.0, min(1.0, score))
            
        except Exception:
            return 0.0
    
    async def get_validation_rules(self, language: str) -> Dict[str, Any]:
        """Get validation rules for a language"""
        rules = {
            "python": {
                "syntax_check": True,
                "pep8_check": True,
                "import_check": True,
                "naming_conventions": True,
                "docstring_check": False,
                "complexity_check": True
            },
            "javascript": {
                "syntax_check": True,
                "eslint_check": True,
                "import_check": True,
                "naming_conventions": True,
                "console_check": True,
                "complexity_check": True
            },
            "typescript": {
                "syntax_check": True,
                "type_check": True,
                "eslint_check": True,
                "import_check": True,
                "naming_conventions": True,
                "complexity_check": True
            },
            "html": {
                "syntax_check": True,
                "accessibility_check": True,
                "semantic_check": True,
                "seo_check": False
            },
            "css": {
                "syntax_check": True,
                "vendor_prefixes": True,
                "browser_compatibility": True,
                "performance_check": True
            }
        }
        
        return rules.get(language.lower(), {})
    
    # Language-specific validators
    
    async def _validate_python(
        self,
        code: str,
        framework: Optional[str] = None,
        rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate Python code"""
        errors = []
        warnings = []
        suggestions = []
        
        try:
            # Syntax check
            try:
                ast.parse(code)
            except SyntaxError as e:
                errors.append(f"Syntax error: {str(e)}")
                return {
                    "valid": False,
                    "errors": errors,
                    "warnings": warnings,
                    "suggestions": suggestions
                }
            
            # PEP 8 style check (basic)
            if rules and rules.get("pep8_check", True):
                pep8_issues = await self._check_pep8(code)
                warnings.extend(pep8_issues)
            
            # Import check
            if rules and rules.get("import_check", True):
                import_issues = await self._check_imports(code)
                warnings.extend(import_issues)
            
            # Naming conventions
            if rules and rules.get("naming_conventions", True):
                naming_issues = await self._check_python_naming(code)
                suggestions.extend(naming_issues)
            
            # Complexity check
            if rules and rules.get("complexity_check", True):
                complexity_issues = await self._check_complexity(code, "python")
                warnings.extend(complexity_issues)
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "suggestions": suggestions
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Python validation failed: {str(e)}"],
                "warnings": warnings,
                "suggestions": suggestions
            }
    
    async def _validate_javascript(
        self,
        code: str,
        framework: Optional[str] = None,
        rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate JavaScript code"""
        errors = []
        warnings = []
        suggestions = []
        
        try:
            # Basic syntax check using Node.js
            syntax_valid = await self._check_js_syntax(code)
            if not syntax_valid:
                errors.append("JavaScript syntax error")
            
            # ESLint check (if available)
            if rules and rules.get("eslint_check", True):
                eslint_issues = await self._check_eslint(code)
                warnings.extend(eslint_issues)
            
            # Console statements check
            if rules and rules.get("console_check", True):
                console_issues = await self._check_console_statements(code)
                warnings.extend(console_issues)
            
            # Framework-specific checks
            if framework == "react":
                react_issues = await self._check_react_patterns(code)
                suggestions.extend(react_issues)
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "suggestions": suggestions
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"JavaScript validation failed: {str(e)}"],
                "warnings": warnings,
                "suggestions": suggestions
            }
    
    async def _validate_typescript(
        self,
        code: str,
        framework: Optional[str] = None,
        rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate TypeScript code"""
        errors = []
        warnings = []
        suggestions = []
        
        try:
            # TypeScript compilation check
            type_check = await self._check_typescript_types(code)
            if not type_check["valid"]:
                errors.extend(type_check["errors"])
            
            # ESLint check
            if rules and rules.get("eslint_check", True):
                eslint_issues = await self._check_eslint(code, "typescript")
                warnings.extend(eslint_issues)
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "suggestions": suggestions
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"TypeScript validation failed: {str(e)}"],
                "warnings": warnings,
                "suggestions": suggestions
            }
    
    async def _validate_html(
        self,
        code: str,
        framework: Optional[str] = None,
        rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate HTML code"""
        errors = []
        warnings = []
        suggestions = []
        
        try:
            # Basic HTML structure check
            html_issues = await self._check_html_structure(code)
            errors.extend(html_issues)
            
            # Accessibility check
            if rules and rules.get("accessibility_check", True):
                a11y_issues = await self._check_accessibility(code)
                warnings.extend(a11y_issues)
            
            # Semantic HTML check
            if rules and rules.get("semantic_check", True):
                semantic_issues = await self._check_semantic_html(code)
                suggestions.extend(semantic_issues)
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "suggestions": suggestions
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"HTML validation failed: {str(e)}"],
                "warnings": warnings,
                "suggestions": suggestions
            }
    
    async def _validate_css(
        self,
        code: str,
        framework: Optional[str] = None,
        rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate CSS code"""
        errors = []
        warnings = []
        suggestions = []
        
        try:
            # CSS syntax check
            css_issues = await self._check_css_syntax(code)
            errors.extend(css_issues)
            
            # Browser compatibility check
            if rules and rules.get("browser_compatibility", True):
                compatibility_issues = await self._check_css_compatibility(code)
                warnings.extend(compatibility_issues)
            
            # Performance check
            if rules and rules.get("performance_check", True):
                performance_issues = await self._check_css_performance(code)
                suggestions.extend(performance_issues)
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "suggestions": suggestions
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"CSS validation failed: {str(e)}"],
                "warnings": warnings,
                "suggestions": suggestions
            }
    
    async def _validate_json(
        self,
        code: str,
        framework: Optional[str] = None,
        rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate JSON code"""
        errors = []
        warnings = []
        suggestions = []
        
        try:
            import json
            json.loads(code)
            
            return {
                "valid": True,
                "errors": errors,
                "warnings": warnings,
                "suggestions": suggestions
            }
            
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "errors": [f"JSON syntax error: {str(e)}"],
                "warnings": warnings,
                "suggestions": suggestions
            }
    
    # Helper methods
    
    def _get_language_from_path(self, file_path: str) -> str:
        """Get language from file path"""
        extension = Path(file_path).suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.html': 'html',
            '.htm': 'html',
            '.css': 'css',
            '.json': 'json'
        }
        
        return language_map.get(extension, 'text')
    
    async def _check_pep8(self, code: str) -> List[str]:
        """Check PEP 8 style issues"""
        issues = []
        
        # Basic PEP 8 checks
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Line length
            if len(line) > 79:
                issues.append(f"Line {i}: Line too long ({len(line)} > 79)")
            
            # Trailing whitespace
            if line.rstrip() != line:
                issues.append(f"Line {i}: Trailing whitespace")
        
        return issues
    
    async def _check_imports(self, code: str) -> List[str]:
        """Check import issues"""
        issues = []
        
        # Check for unused imports (basic check)
        lines = code.split('\n')
        import_lines = [line for line in lines if line.strip().startswith('import') or line.strip().startswith('from')]
        
        for import_line in import_lines:
            if 'import' in import_line:
                module = import_line.split('import')[1].strip().split()[0]
                if module not in code.replace(import_line, ''):
                    issues.append(f"Potentially unused import: {module}")
        
        return issues
    
    async def _check_python_naming(self, code: str) -> List[str]:
        """Check Python naming conventions"""
        suggestions = []
        
        # Check for function and variable naming
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for camelCase (should be snake_case)
            if re.search(r'\b[a-z][a-zA-Z]*[A-Z][a-zA-Z]*\b', line):
                suggestions.append(f"Line {i}: Consider using snake_case instead of camelCase")
        
        return suggestions
    
    async def _check_complexity(self, code: str, language: str) -> List[str]:
        """Check code complexity"""
        issues = []
        
        # Basic complexity check
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        if len(non_empty_lines) > 50:
            issues.append("Function/class might be too long (>50 lines)")
        
        # Check for nested structures
        max_indent = 0
        for line in lines:
            indent = len(line) - len(line.lstrip())
            max_indent = max(max_indent, indent)
        
        if max_indent > 12:  # More than 3 levels of nesting
            issues.append("Code has deep nesting, consider refactoring")
        
        return issues
    
    async def _check_js_syntax(self, code: str) -> bool:
        """Check JavaScript syntax using Node.js"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            result = subprocess.run(
                ['node', '--check', temp_file],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            os.unlink(temp_file)
            return result.returncode == 0
            
        except Exception:
            return False
    
    async def _check_eslint(self, code: str, language: str = "javascript") -> List[str]:
        """Check ESLint issues"""
        issues = []
        
        # Basic ESLint-style checks
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for console statements
            if 'console.' in line and not line.strip().startswith('//'):
                issues.append(f"Line {i}: Consider removing console statement")
            
            # Check for var usage
            if 'var ' in line:
                issues.append(f"Line {i}: Consider using 'let' or 'const' instead of 'var'")
        
        return issues
    
    async def _check_console_statements(self, code: str) -> List[str]:
        """Check for console statements"""
        issues = []
        
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            if 'console.' in line and not line.strip().startswith('//'):
                issues.append(f"Line {i}: Console statement found - consider removing for production")
        
        return issues
    
    async def _check_react_patterns(self, code: str) -> List[str]:
        """Check React-specific patterns"""
        suggestions = []
        
        # Check for React best practices
        if 'componentDidMount' in code:
            suggestions.append("Consider using React hooks instead of class components")
        
        if 'this.state' in code:
            suggestions.append("Consider using useState hook instead of this.state")
        
        return suggestions
    
    async def _check_typescript_types(self, code: str) -> Dict[str, Any]:
        """Check TypeScript type issues"""
        # This would require TypeScript compiler
        # For now, return basic validation
        return {
            "valid": True,
            "errors": []
        }
    
    async def _check_html_structure(self, code: str) -> List[str]:
        """Check HTML structure"""
        issues = []
        
        # Check for basic HTML structure
        if '<html>' not in code.lower():
            issues.append("Missing <html> tag")
        
        if '<head>' not in code.lower():
            issues.append("Missing <head> tag")
        
        if '<body>' not in code.lower():
            issues.append("Missing <body> tag")
        
        return issues
    
    async def _check_accessibility(self, code: str) -> List[str]:
        """Check accessibility issues"""
        issues = []
        
        # Basic accessibility checks
        if '<img' in code and 'alt=' not in code:
            issues.append("Images should have alt attributes")
        
        if '<button' in code and 'aria-label' not in code:
            issues.append("Buttons should have accessible labels")
        
        return issues
    
    async def _check_semantic_html(self, code: str) -> List[str]:
        """Check semantic HTML usage"""
        suggestions = []
        
        # Check for semantic HTML elements
        if '<div>' in code and '<section>' not in code:
            suggestions.append("Consider using semantic HTML elements like <section>, <article>, <nav>")
        
        return suggestions
    
    async def _check_css_syntax(self, code: str) -> List[str]:
        """Check CSS syntax"""
        issues = []
        
        # Basic CSS syntax checks
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            if '{' in line and '}' not in line:
                # Check if closing brace is in next few lines
                next_lines = lines[i:i+5]
                if not any('}' in next_line for next_line in next_lines):
                    issues.append(f"Line {i}: Missing closing brace")
        
        return issues
    
    async def _check_css_compatibility(self, code: str) -> List[str]:
        """Check CSS browser compatibility"""
        issues = []
        
        # Check for vendor prefixes
        if 'transform' in code and '-webkit-transform' not in code:
            issues.append("Consider adding vendor prefixes for better browser compatibility")
        
        return issues
    
    async def _check_css_performance(self, code: str) -> List[str]:
        """Check CSS performance issues"""
        suggestions = []
        
        # Check for performance issues
        if '@import' in code:
            suggestions.append("Consider using <link> tags instead of @import for better performance")
        
        return suggestions
    
    async def _calculate_complexity_score(self, code: str, language: str) -> float:
        """Calculate complexity score"""
        try:
            lines = code.split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            
            # Simple complexity calculation
            complexity = len(non_empty_lines) / 100.0  # Normalize to 0-1
            
            # Penalize for long lines
            long_lines = sum(1 for line in lines if len(line) > 100)
            complexity += long_lines * 0.1
            
            return max(0.0, min(1.0, 1.0 - complexity))
            
        except Exception:
            return 0.5
