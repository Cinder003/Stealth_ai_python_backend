"""Input validation helpers"""

import re
import logging
from typing import List
from app.models.schemas import GenerateCodeRequest
from app.core.exceptions import ValidationException

logger = logging.getLogger(__name__)

# Patterns to detect potentially harmful content
DANGEROUS_PATTERNS = [
    r'rm\s+-rf',
    r'eval\s*\(',
    r'exec\s*\(',
    r'__import__',
    r'system\s*\(',
    r'subprocess',
]


def validate_code_request(request: GenerateCodeRequest) -> bool:
    """
    Validate code generation request
    
    Args:
        request: Code generation request
        
    Returns:
        True if valid
        
    Raises:
        ValidationException: If validation fails
    """
    # Check prompt length
    if len(request.prompt) < 10:
        raise ValidationException(
            "Prompt is too short. Please provide more details.",
            details={"min_length": 10, "actual_length": len(request.prompt)}
        )
    
    if len(request.prompt) > 10000:
        raise ValidationException(
            "Prompt is too long. Please shorten your request.",
            details={"max_length": 10000, "actual_length": len(request.prompt)}
        )
    
    # Check for dangerous patterns in prompt
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, request.prompt, re.IGNORECASE):
            logger.warning(f"Potentially dangerous pattern detected: {pattern}")
            raise ValidationException(
                "Your prompt contains potentially unsafe content.",
                details={"pattern": pattern}
            )
    
    logger.debug("Request validation passed")
    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path traversal attempts
    filename = filename.replace('..', '')
    filename = filename.replace('/', '_')
    filename = filename.replace('\\', '_')
    
    # Remove any non-alphanumeric characters except dots, hyphens, and underscores
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    return filename


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Validate file extension
    
    Args:
        filename: Filename to validate
        allowed_extensions: List of allowed extensions
        
    Returns:
        True if valid
    """
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    return ext in allowed_extensions


class ValidationHelper:
    """Helper class for validation operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_code_request(self, request: GenerateCodeRequest) -> bool:
        """Validate code generation request"""
        return validate_code_request(request)
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename"""
        return sanitize_filename(filename)
    
    def validate_file_extension(self, filename: str, allowed_extensions: List[str]) -> bool:
        """Validate file extension"""
        return validate_file_extension(filename, allowed_extensions)

