"""
JSON Chunker
Handles large JSON data processing and chunking
"""

import json
import io
from typing import Dict, List, Optional, Any, Iterator, Union
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ChunkInfo:
    """Information about a data chunk"""
    chunk_id: str
    start_index: int
    end_index: int
    size: int
    metadata: Dict[str, Any]


class JSONChunker:
    """Handles JSON data chunking and processing"""
    
    def __init__(self, max_chunk_size: int = 1000, max_memory_size: int = 10 * 1024 * 1024):
        self.max_chunk_size = max_chunk_size
        self.max_memory_size = max_memory_size
    
    def chunk_json_data(
        self,
        data: Union[Dict, List, str],
        chunk_size: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Chunk JSON data into smaller pieces"""
        if chunk_size is None:
            chunk_size = self.max_chunk_size
        
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON string: {str(e)}")
        
        if isinstance(data, list):
            return self._chunk_list(data, chunk_size)
        elif isinstance(data, dict):
            return self._chunk_dict(data, chunk_size)
        else:
            # Single value
            return [{"data": data, "chunk_info": ChunkInfo("0", 0, 0, 1, {})}]
    
    def chunk_json_file(
        self,
        file_path: Union[str, Path],
        chunk_size: Optional[int] = None
    ) -> Iterator[Dict[str, Any]]:
        """Chunk JSON file into smaller pieces"""
        if chunk_size is None:
            chunk_size = self.max_chunk_size
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check file size
        file_size = file_path.stat().st_size
        if file_size > self.max_memory_size:
            return self._chunk_large_file(file_path, chunk_size)
        else:
            # Load entire file into memory
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            chunks = self.chunk_json_data(data, chunk_size)
            for chunk in chunks:
                yield chunk
    
    def chunk_json_stream(
        self,
        stream: io.TextIOBase,
        chunk_size: Optional[int] = None
    ) -> Iterator[Dict[str, Any]]:
        """Chunk JSON data from a stream"""
        if chunk_size is None:
            chunk_size = self.max_chunk_size
        
        # Try to parse as JSON first
        try:
            stream.seek(0)
            data = json.load(stream)
            chunks = self.chunk_json_data(data, chunk_size)
            for chunk in chunks:
                yield chunk
        except (json.JSONDecodeError, io.UnsupportedOperation):
            # Fall back to line-by-line processing
            yield from self._chunk_json_lines(stream, chunk_size)
    
    def merge_chunks(self, chunks: List[Dict[str, Any]]) -> Any:
        """Merge chunks back into original data structure"""
        if not chunks:
            return None
        
        # Check if chunks are from a list
        if all("chunk_info" in chunk for chunk in chunks):
            chunk_infos = [chunk["chunk_info"] for chunk in chunks]
            
            # Sort by start index
            sorted_chunks = sorted(zip(chunks, chunk_infos), key=lambda x: x[1].start_index)
            
            # Check if it's a list
            if all(info.start_index is not None for info in chunk_infos):
                # Reconstruct list
                result = []
                for chunk, info in sorted_chunks:
                    if "data" in chunk:
                        if isinstance(chunk["data"], list):
                            result.extend(chunk["data"])
                        else:
                            result.append(chunk["data"])
                return result
        
        # Check if chunks are from a dict
        if all("key" in chunk for chunk in chunks):
            # Reconstruct dict
            result = {}
            for chunk in chunks:
                if "key" in chunk and "value" in chunk:
                    result[chunk["key"]] = chunk["value"]
            return result
        
        # Fallback: return as list
        return [chunk.get("data", chunk) for chunk in chunks]
    
    def validate_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """Validate that chunks can be merged back"""
        if not chunks:
            return True
        
        # Check for required fields
        required_fields = ["chunk_info"]
        for chunk in chunks:
            for field in required_fields:
                if field not in chunk:
                    return False
        
        # Check chunk info consistency
        chunk_infos = [chunk["chunk_info"] for chunk in chunks]
        
        # Check for overlapping chunks
        sorted_infos = sorted(chunk_infos, key=lambda x: x.start_index)
        for i in range(len(sorted_infos) - 1):
            current = sorted_infos[i]
            next_info = sorted_infos[i + 1]
            
            if current.end_index > next_info.start_index:
                return False
        
        return True
    
    def get_chunk_statistics(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about chunks"""
        if not chunks:
            return {
                "total_chunks": 0,
                "total_size": 0,
                "average_size": 0,
                "min_size": 0,
                "max_size": 0
            }
        
        sizes = []
        total_size = 0
        
        for chunk in chunks:
            if "chunk_info" in chunk:
                size = chunk["chunk_info"].size
            else:
                size = len(str(chunk))
            
            sizes.append(size)
            total_size += size
        
        return {
            "total_chunks": len(chunks),
            "total_size": total_size,
            "average_size": total_size / len(chunks),
            "min_size": min(sizes),
            "max_size": max(sizes),
            "size_distribution": self._calculate_size_distribution(sizes)
        }
    
    def _chunk_list(self, data: List, chunk_size: int) -> List[Dict[str, Any]]:
        """Chunk a list into smaller pieces"""
        chunks = []
        
        for i in range(0, len(data), chunk_size):
            end_index = min(i + chunk_size, len(data))
            chunk_data = data[i:end_index]
            
            chunk_info = ChunkInfo(
                chunk_id=str(i // chunk_size),
                start_index=i,
                end_index=end_index,
                size=len(chunk_data),
                metadata={"type": "list_chunk"}
            )
            
            chunks.append({
                "data": chunk_data,
                "chunk_info": chunk_info
            })
        
        return chunks
    
    def _chunk_dict(self, data: Dict, chunk_size: int) -> List[Dict[str, Any]]:
        """Chunk a dictionary into smaller pieces"""
        chunks = []
        items = list(data.items())
        
        for i in range(0, len(items), chunk_size):
            end_index = min(i + chunk_size, len(items))
            chunk_items = items[i:end_index]
            
            chunk_data = dict(chunk_items)
            
            chunk_info = ChunkInfo(
                chunk_id=str(i // chunk_size),
                start_index=i,
                end_index=end_index,
                size=len(chunk_data),
                metadata={"type": "dict_chunk"}
            )
            
            chunks.append({
                "data": chunk_data,
                "chunk_info": chunk_info
            })
        
        return chunks
    
    def _chunk_large_file(
        self,
        file_path: Path,
        chunk_size: int
    ) -> Iterator[Dict[str, Any]]:
        """Chunk a large JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            # Try to determine if it's a JSON array or object
            first_char = f.read(1)
            f.seek(0)
            
            if first_char == '[':
                # JSON array - process line by line
                yield from self._chunk_json_array_file(f, chunk_size)
            elif first_char == '{':
                # JSON object - process key by key
                yield from self._chunk_json_object_file(f, chunk_size)
            else:
                raise ValueError("Unsupported JSON format")
    
    def _chunk_json_array_file(
        self,
        file: io.TextIOBase,
        chunk_size: int
    ) -> Iterator[Dict[str, Any]]:
        """Chunk a JSON array file"""
        chunk = []
        chunk_index = 0
        
        for line in file:
            line = line.strip()
            if not line:
                continue
            
            # Remove trailing comma
            if line.endswith(','):
                line = line[:-1]
            
            # Skip array brackets
            if line in ['[', ']']:
                continue
            
            try:
                item = json.loads(line)
                chunk.append(item)
                
                if len(chunk) >= chunk_size:
                    chunk_info = ChunkInfo(
                        chunk_id=str(chunk_index),
                        start_index=chunk_index * chunk_size,
                        end_index=(chunk_index + 1) * chunk_size,
                        size=len(chunk),
                        metadata={"type": "array_chunk"}
                    )
                    
                    yield {
                        "data": chunk,
                        "chunk_info": chunk_info
                    }
                    
                    chunk = []
                    chunk_index += 1
            
            except json.JSONDecodeError:
                # Skip invalid JSON lines
                continue
        
        # Yield remaining chunk
        if chunk:
            chunk_info = ChunkInfo(
                chunk_id=str(chunk_index),
                start_index=chunk_index * chunk_size,
                end_index=chunk_index * chunk_size + len(chunk),
                size=len(chunk),
                metadata={"type": "array_chunk"}
            )
            
            yield {
                "data": chunk,
                "chunk_info": chunk_info
            }
    
    def _chunk_json_object_file(
        self,
        file: io.TextIOBase,
        chunk_size: int
    ) -> Iterator[Dict[str, Any]]:
        """Chunk a JSON object file"""
        chunk = {}
        chunk_index = 0
        key_count = 0
        
        for line in file:
            line = line.strip()
            if not line:
                continue
            
            # Skip object braces
            if line in ['{', '}']:
                continue
            
            # Remove trailing comma
            if line.endswith(','):
                line = line[:-1]
            
            # Parse key-value pair
            if ':' in line:
                try:
                    key, value = line.split(':', 1)
                    key = key.strip().strip('"')
                    value = value.strip()
                    
                    # Try to parse value as JSON
                    try:
                        parsed_value = json.loads(value)
                    except json.JSONDecodeError:
                        parsed_value = value
                    
                    chunk[key] = parsed_value
                    key_count += 1
                    
                    if key_count >= chunk_size:
                        chunk_info = ChunkInfo(
                            chunk_id=str(chunk_index),
                            start_index=chunk_index * chunk_size,
                            end_index=(chunk_index + 1) * chunk_size,
                            size=len(chunk),
                            metadata={"type": "object_chunk"}
                        )
                        
                        yield {
                            "data": chunk,
                            "chunk_info": chunk_info
                        }
                        
                        chunk = {}
                        chunk_index += 1
                        key_count = 0
                
                except ValueError:
                    # Skip invalid key-value pairs
                    continue
        
        # Yield remaining chunk
        if chunk:
            chunk_info = ChunkInfo(
                chunk_id=str(chunk_index),
                start_index=chunk_index * chunk_size,
                end_index=chunk_index * chunk_size + len(chunk),
                size=len(chunk),
                metadata={"type": "object_chunk"}
            )
            
            yield {
                "data": chunk,
                "chunk_info": chunk_info
            }
    
    def _chunk_json_lines(
        self,
        stream: io.TextIOBase,
        chunk_size: int
    ) -> Iterator[Dict[str, Any]]:
        """Chunk JSON data from lines"""
        chunk = []
        chunk_index = 0
        
        for line in stream:
            line = line.strip()
            if not line:
                continue
            
            try:
                item = json.loads(line)
                chunk.append(item)
                
                if len(chunk) >= chunk_size:
                    chunk_info = ChunkInfo(
                        chunk_id=str(chunk_index),
                        start_index=chunk_index * chunk_size,
                        end_index=(chunk_index + 1) * chunk_size,
                        size=len(chunk),
                        metadata={"type": "line_chunk"}
                    )
                    
                    yield {
                        "data": chunk,
                        "chunk_info": chunk_info
                    }
                    
                    chunk = []
                    chunk_index += 1
            
            except json.JSONDecodeError:
                # Skip invalid JSON lines
                continue
        
        # Yield remaining chunk
        if chunk:
            chunk_info = ChunkInfo(
                chunk_id=str(chunk_index),
                start_index=chunk_index * chunk_size,
                end_index=chunk_index * chunk_size + len(chunk),
                size=len(chunk),
                metadata={"type": "line_chunk"}
            )
            
            yield {
                "data": chunk,
                "chunk_info": chunk_info
            }
    
    def _calculate_size_distribution(self, sizes: List[int]) -> Dict[str, int]:
        """Calculate size distribution of chunks"""
        if not sizes:
            return {}
        
        size_ranges = {
            "small": 0,    # < 100
            "medium": 0,   # 100-1000
            "large": 0,    # 1000-10000
            "xlarge": 0    # > 10000
        }
        
        for size in sizes:
            if size < 100:
                size_ranges["small"] += 1
            elif size < 1000:
                size_ranges["medium"] += 1
            elif size < 10000:
                size_ranges["large"] += 1
            else:
                size_ranges["xlarge"] += 1
        
        return size_ranges
