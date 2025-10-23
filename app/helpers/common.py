"""
Common Utilities
Shared utility functions and helpers
"""

import os
import hashlib
import uuid
import json
import time
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timezone
from pathlib import Path
import logging


class CommonUtils:
    """Common utility functions"""
    
    @staticmethod
    def generate_uuid() -> str:
        """Generate a UUID string"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_short_id(length: int = 8) -> str:
        """Generate a short ID"""
        return uuid.uuid4().hex[:length]
    
    @staticmethod
    def generate_hash(data: str, algorithm: str = 'md5') -> str:
        """Generate hash of data"""
        if algorithm == 'md5':
            return hashlib.md5(data.encode()).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(data.encode()).hexdigest()
        elif algorithm == 'sha256':
            return hashlib.sha256(data.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    @staticmethod
    def get_timestamp() -> float:
        """Get current timestamp"""
        return time.time()
    
    @staticmethod
    def get_iso_timestamp() -> str:
        """Get current ISO timestamp"""
        return datetime.now(timezone.utc).isoformat()
    
    @staticmethod
    def format_timestamp(timestamp: float, format: str = '%Y-%m-%d %H:%M:%S') -> str:
        """Format timestamp to string"""
        return datetime.fromtimestamp(timestamp).strftime(format)
    
    @staticmethod
    def parse_timestamp(timestamp_str: str, format: str = '%Y-%m-%d %H:%M:%S') -> float:
        """Parse timestamp string to float"""
        return datetime.strptime(timestamp_str, format).timestamp()
    
    @staticmethod
    def safe_json_loads(data: str, default: Any = None) -> Any:
        """Safely parse JSON string"""
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return default
    
    @staticmethod
    def safe_json_dumps(data: Any, default: str = '{}') -> str:
        """Safely serialize data to JSON"""
        try:
            return json.dumps(data, default=str)
        except (TypeError, ValueError):
            return default
    
    @staticmethod
    def ensure_directory(path: str) -> bool:
        """Ensure directory exists"""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """Get file extension"""
        return Path(file_path).suffix.lower()
    
    @staticmethod
    def get_file_name(file_path: str) -> str:
        """Get file name without extension"""
        return Path(file_path).stem
    
    @staticmethod
    def is_file_exists(file_path: str) -> bool:
        """Check if file exists"""
        return os.path.isfile(file_path)
    
    @staticmethod
    def is_directory_exists(dir_path: str) -> bool:
        """Check if directory exists"""
        return os.path.isdir(dir_path)
    
    @staticmethod
    def get_relative_path(file_path: str, base_path: str) -> str:
        """Get relative path"""
        try:
            return os.path.relpath(file_path, base_path)
        except ValueError:
            return file_path
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """Normalize path"""
        return os.path.normpath(path)
    
    @staticmethod
    def join_paths(*paths: str) -> str:
        """Join paths"""
        return os.path.join(*paths)
    
    @staticmethod
    def split_path(path: str) -> tuple:
        """Split path into directory and filename"""
        return os.path.split(path)
    
    @staticmethod
    def get_directory_size(dir_path: str) -> int:
        """Get total size of directory"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(dir_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(file_path)
        except OSError:
            pass
        return total_size
    
    @staticmethod
    def clean_filename(filename: str) -> str:
        """Clean filename for safe usage"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        
        # Ensure filename is not empty
        if not filename:
            filename = 'unnamed'
        
        return filename
    
    @staticmethod
    def truncate_string(text: str, max_length: int, suffix: str = '...') -> str:
        """Truncate string to max length"""
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
        """Split list into chunks"""
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
    
    @staticmethod
    def flatten_list(lst: List[List[Any]]) -> List[Any]:
        """Flatten nested list"""
        result = []
        for item in lst:
            if isinstance(item, list):
                result.extend(item)
            else:
                result.append(item)
        return result
    
    @staticmethod
    def remove_duplicates(lst: List[Any]) -> List[Any]:
        """Remove duplicates from list while preserving order"""
        seen = set()
        result = []
        for item in lst:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result
    
    @staticmethod
    def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
        """Merge multiple dictionaries"""
        result = {}
        for d in dicts:
            result.update(d)
        return result
    
    @staticmethod
    def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = CommonUtils.deep_merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result
    
    @staticmethod
    def get_nested_value(data: Dict[str, Any], key_path: str, default: Any = None) -> Any:
        """Get nested value from dictionary using dot notation"""
        keys = key_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    @staticmethod
    def set_nested_value(data: Dict[str, Any], key_path: str, value: Any) -> None:
        """Set nested value in dictionary using dot notation"""
        keys = key_path.split('.')
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    @staticmethod
    def filter_dict(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
        """Filter dictionary to only include specified keys"""
        return {key: data[key] for key in keys if key in data}
    
    @staticmethod
    def exclude_dict(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
        """Filter dictionary to exclude specified keys"""
        return {key: value for key, value in data.items() if key not in keys}
    
    @staticmethod
    def convert_to_string(value: Any) -> str:
        """Convert value to string safely"""
        if value is None:
            return ''
        elif isinstance(value, str):
            return value
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, (list, dict)):
            return json.dumps(value, default=str)
        else:
            return str(value)
    
    @staticmethod
    def convert_to_bool(value: Any) -> bool:
        """Convert value to boolean"""
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        elif isinstance(value, (int, float)):
            return bool(value)
        else:
            return False
    
    @staticmethod
    def convert_to_int(value: Any, default: int = 0) -> int:
        """Convert value to integer"""
        try:
            if isinstance(value, int):
                return value
            elif isinstance(value, float):
                return int(value)
            elif isinstance(value, str):
                return int(float(value))
            else:
                return default
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def convert_to_float(value: Any, default: float = 0.0) -> float:
        """Convert value to float"""
        try:
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                return float(value)
            else:
                return default
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL"""
        import re
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def sanitize_html(html: str) -> str:
        """Sanitize HTML content"""
        import re
        # Remove script tags
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        # Remove style tags
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        # Remove javascript: protocols
        html = re.sub(r'javascript:', '', html, flags=re.IGNORECASE)
        return html
    
    @staticmethod
    def format_bytes(bytes_value: int) -> str:
        """Format bytes to human readable string"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds to human readable string"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f}h"
        else:
            days = seconds / 86400
            return f"{days:.1f}d"
    
    @staticmethod
    def get_memory_usage() -> Dict[str, int]:
        """Get current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                'rss': memory_info.rss,  # Resident Set Size
                'vms': memory_info.vms,  # Virtual Memory Size
                'percent': process.memory_percent()
            }
        except ImportError:
            return {'rss': 0, 'vms': 0, 'percent': 0}
    
    @staticmethod
    def get_cpu_usage() -> float:
        """Get current CPU usage"""
        try:
            import psutil
            return psutil.cpu_percent()
        except ImportError:
            return 0.0
    
    @staticmethod
    def get_disk_usage(path: str = '/') -> Dict[str, Any]:
        """Get disk usage for path"""
        try:
            import shutil
            total, used, free = shutil.disk_usage(path)
            return {
                'total': total,
                'used': used,
                'free': free,
                'percent': (used / total) * 100
            }
        except OSError:
            return {'total': 0, 'used': 0, 'free': 0, 'percent': 0}
    
    @staticmethod
    def create_logger(name: str, level: int = logging.INFO) -> logging.Logger:
        """Create a logger with standard configuration"""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    @staticmethod
    def measure_time(func: Callable) -> Callable:
        """Decorator to measure function execution time"""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f"{func.__name__} took {end_time - start_time:.4f} seconds")
            return result
        return wrapper
    
    @staticmethod
    def retry_on_exception(
        max_attempts: int = 3,
        delay: float = 1.0,
        exceptions: tuple = (Exception,)
    ):
        """Decorator to retry function on exception"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        if attempt == max_attempts - 1:
                            raise e
                        time.sleep(delay)
                return None
            return wrapper
        return decorator
    
    @staticmethod
    def cache_result(ttl: float = 300.0):
        """Decorator to cache function result with TTL"""
        cache = {}
        
        def decorator(func):
            def wrapper(*args, **kwargs):
                key = str(args) + str(kwargs)
                current_time = time.time()
                
                if key in cache:
                    result, timestamp = cache[key]
                    if current_time - timestamp < ttl:
                        return result
                
                result = func(*args, **kwargs)
                cache[key] = (result, current_time)
                return result
            return wrapper
        return decorator
