"""Code Extraction Service - Extract code blocks from LLM responses"""

import re
import logging
from typing import List, Dict, Tuple, Optional
from app.core.exceptions import CodeExtractionException
from app.models.domain import GeneratedFile

logger = logging.getLogger(__name__)


class CodeExtractionService:
    """Service to extract code blocks from LLM text responses"""
    
    # Regex patterns for code block extraction
    MARKDOWN_CODE_BLOCK = re.compile(
        r'```(?P<language>\w+)?\s*\n(?P<code>.*?)```',
        re.DOTALL | re.MULTILINE
    )
    
    FILE_PATH_PATTERN = re.compile(
        r'(?:File|Path|Create file):\s*`?([a-zA-Z0-9_/\-\.]+)`?',
        re.IGNORECASE
    )
    
    def extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """
        Extract all code blocks from markdown text
        
        Args:
            text: Raw text from LLM response
            
        Returns:
            List of dicts with 'language' and 'code' keys
        """
        blocks = []
        
        for match in self.MARKDOWN_CODE_BLOCK.finditer(text):
            language = match.group('language') or 'text'
            code = match.group('code').strip()
            
            blocks.append({
                'language': language.lower(),
                'code': code
            })
        
        logger.info(f"Extracted {len(blocks)} code blocks")
        return blocks
    
    def extract_file_path(self, context: str) -> Optional[str]:
        """
        Extract file path from surrounding context
        
        Args:
            context: Text around the code block
            
        Returns:
            File path if found
        """
        match = self.FILE_PATH_PATTERN.search(context)
        if match:
            return match.group(1)
        return None
    
    def infer_file_path(
        self,
        code: str,
        language: str,
        index: int = 0
    ) -> str:
        """
        Infer file path from code content and language
        
        Args:
            code: Code content
            language: Programming language
            index: Index of the file
            
        Returns:
            Inferred file path
        """
        # Try to find component/class name in code
        component_name = self._extract_component_name(code, language)
        
        # Map language to file extension
        ext_map = {
            'javascript': 'js',
            'jsx': 'jsx',
            'typescript': 'ts',
            'tsx': 'tsx',
            'python': 'py',
            'html': 'html',
            'css': 'css',
            'json': 'json',
            'yaml': 'yaml',
            'yml': 'yml',
            'markdown': 'md',
            'md': 'md',
            'sql': 'sql',
            'sh': 'sh',
            'bash': 'sh',
        }
        
        extension = ext_map.get(language.lower(), 'txt')
        
        if component_name:
            return f"src/{component_name}.{extension}"
        else:
            return f"src/file_{index + 1}.{extension}"
    
    def _extract_component_name(self, code: str, language: str) -> Optional[str]:
        """Extract component/class/function name from code"""
        
        # React component
        if language in ['jsx', 'tsx', 'javascript', 'typescript']:
            # Function component: export default function ComponentName
            match = re.search(r'(?:export\s+default\s+)?(?:function|const)\s+([A-Z][a-zA-Z0-9]*)', code)
            if match:
                return match.group(1)
            
            # Class component: class ComponentName
            match = re.search(r'class\s+([A-Z][a-zA-Z0-9]*)', code)
            if match:
                return match.group(1)
        
        # Python class/function
        elif language == 'python':
            match = re.search(r'class\s+([A-Z][a-zA-Z0-9]*)', code)
            if match:
                return match.group(1)
            match = re.search(r'def\s+([a-z_][a-zA-Z0-9_]*)', code)
            if match:
                return match.group(1)
        
        return None
    
    def extract_files_from_response(
        self,
        response_text: str,
        default_framework: str = "react"
    ) -> List[GeneratedFile]:
        """
        Extract all files from LLM response
        
        Args:
            response_text: Raw LLM response
            default_framework: Default framework for language detection
            
        Returns:
            List of GeneratedFile objects
        """
        try:
            files = []
            code_blocks = self.extract_code_blocks(response_text)
            
            if not code_blocks:
                logger.warning("No code blocks found in response")
                raise CodeExtractionException(
                    "No code blocks found in LLM response",
                    details={"response_length": len(response_text)}
                )
            
            for i, block in enumerate(code_blocks):
                language = block['language']
                code = block['code']
                
                # Try to extract file path from context
                # For now, use inference
                file_path = self.infer_file_path(code, language, i)
                
                file = GeneratedFile(
                    path=file_path,
                    content=code,
                    language=language
                )
                
                files.append(file)
            
            logger.info(f"Extracted {len(files)} files from response")
            return files
            
        except Exception as e:
            logger.exception(f"Error extracting files: {e}")
            raise CodeExtractionException(
                f"Failed to extract files: {str(e)}",
                details={"error": str(e)}
            )
    
    def parse_structured_response(self, response_text: str) -> List[GeneratedFile]:
        """
        Parse structured response with explicit file paths
        
        Expected format:
        File: path/to/file.ext
        ```language
        code here
        ```
        
        Args:
            response_text: Raw LLM response
            
        Returns:
            List of GeneratedFile objects
        """
        files = []
        lines = response_text.split('\n')
        
        current_file_path = None
        current_code_blocks = []
        in_code_block = False
        current_language = None
        current_code = []
        
        for line in lines:
            # Check for file path declaration
            file_match = self.FILE_PATH_PATTERN.search(line)
            if file_match:
                current_file_path = file_match.group(1)
                continue
            
            # Check for code block start
            if line.strip().startswith('```'):
                if not in_code_block:
                    # Start of code block
                    in_code_block = True
                    lang_match = re.search(r'```(\w+)', line)
                    current_language = lang_match.group(1) if lang_match else 'text'
                    current_code = []
                else:
                    # End of code block
                    in_code_block = False
                    code_content = '\n'.join(current_code)
                    
                    if current_file_path:
                        files.append(GeneratedFile(
                            path=current_file_path,
                            content=code_content,
                            language=current_language
                        ))
                        current_file_path = None
                continue
            
            # Accumulate code lines
            if in_code_block:
                current_code.append(line)
        
        if files:
            logger.info(f"Parsed {len(files)} files with explicit paths")
            return files
        
        # Fall back to simple extraction
        return self.extract_files_from_response(response_text)


# Singleton instance
_code_extraction_service: Optional[CodeExtractionService] = None


def get_code_extraction_service() -> CodeExtractionService:
    """Get or create code extraction service singleton"""
    global _code_extraction_service
    if _code_extraction_service is None:
        _code_extraction_service = CodeExtractionService()
    return _code_extraction_service

