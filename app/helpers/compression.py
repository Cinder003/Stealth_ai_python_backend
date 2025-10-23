"""
Compression Helper
Handles file compression and decompression operations
"""

import os
import zipfile
import tarfile
import gzip
import shutil
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class CompressionFormat(Enum):
    """Compression format enumeration"""
    ZIP = "zip"
    TAR = "tar"
    TAR_GZ = "tar.gz"
    TAR_BZ2 = "tar.bz2"
    GZIP = "gz"
    BZIP2 = "bz2"


@dataclass
class CompressionResult:
    """Result of compression operation"""
    success: bool
    archive_path: str
    original_size: int
    compressed_size: int
    compression_ratio: float
    files_compressed: int
    errors: List[str]
    warnings: List[str]


class CompressionHelper:
    """Handles file compression and decompression"""
    
    def __init__(self):
        self.supported_formats = {
            CompressionFormat.ZIP: self._compress_zip,
            CompressionFormat.TAR: self._compress_tar,
            CompressionFormat.TAR_GZ: self._compress_tar_gz,
            CompressionFormat.TAR_BZ2: self._compress_tar_bz2,
            CompressionFormat.GZIP: self._compress_gzip,
            CompressionFormat.BZIP2: self._compress_bzip2
        }
        
        self.decompression_formats = {
            CompressionFormat.ZIP: self._decompress_zip,
            CompressionFormat.TAR: self._decompress_tar,
            CompressionFormat.TAR_GZ: self._decompress_tar_gz,
            CompressionFormat.TAR_BZ2: self._decompress_tar_bz2,
            CompressionFormat.GZIP: self._decompress_gzip,
            CompressionFormat.BZIP2: self._decompress_bzip2
        }
    
    def compress_files(
        self,
        file_paths: List[str],
        output_path: str,
        format: CompressionFormat = CompressionFormat.ZIP,
        compression_level: int = 6,
        include_base_dir: bool = False
    ) -> CompressionResult:
        """Compress multiple files into an archive"""
        try:
            # Validate input files
            valid_files = []
            total_size = 0
            
            for file_path in file_paths:
                if os.path.exists(file_path):
                    valid_files.append(file_path)
                    total_size += os.path.getsize(file_path)
                else:
                    return CompressionResult(
                        success=False,
                        archive_path="",
                        original_size=0,
                        compressed_size=0,
                        compression_ratio=0.0,
                        files_compressed=0,
                        errors=[f"File not found: {file_path}"],
                        warnings=[]
                    )
            
            if not valid_files:
                return CompressionResult(
                    success=False,
                    archive_path="",
                    original_size=0,
                    compressed_size=0,
                    compression_ratio=0.0,
                    files_compressed=0,
                    errors=["No valid files to compress"],
                    warnings=[]
                )
            
            # Get compression function
            compress_func = self.supported_formats.get(format)
            if not compress_func:
                return CompressionResult(
                    success=False,
                    archive_path="",
                    original_size=total_size,
                    compressed_size=0,
                    compression_ratio=0.0,
                    files_compressed=0,
                    errors=[f"Unsupported compression format: {format}"],
                    warnings=[]
                )
            
            # Compress files
            result = compress_func(valid_files, output_path, compression_level, include_base_dir)
            
            return result
            
        except Exception as e:
            return CompressionResult(
                success=False,
                archive_path="",
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                files_compressed=0,
                errors=[f"Compression failed: {str(e)}"],
                warnings=[]
            )
    
    def compress_directory(
        self,
        directory_path: str,
        output_path: str,
        format: CompressionFormat = CompressionFormat.ZIP,
        compression_level: int = 6,
        exclude_patterns: Optional[List[str]] = None
    ) -> CompressionResult:
        """Compress a directory into an archive"""
        try:
            directory_path = Path(directory_path)
            if not directory_path.exists() or not directory_path.is_dir():
                return CompressionResult(
                    success=False,
                    archive_path="",
                    original_size=0,
                    compressed_size=0,
                    compression_ratio=0.0,
                    files_compressed=0,
                    errors=[f"Directory not found: {directory_path}"],
                    warnings=[]
                )
            
            # Get all files in directory
            all_files = []
            total_size = 0
            
            for file_path in directory_path.rglob('*'):
                if file_path.is_file():
                    # Check exclude patterns
                    if exclude_patterns:
                        should_exclude = False
                        for pattern in exclude_patterns:
                            if pattern in str(file_path):
                                should_exclude = True
                                break
                        
                        if should_exclude:
                            continue
                    
                    all_files.append(str(file_path))
                    total_size += file_path.stat().st_size
            
            if not all_files:
                return CompressionResult(
                    success=False,
                    archive_path="",
                    original_size=0,
                    compressed_size=0,
                    compression_ratio=0.0,
                    files_compressed=0,
                    errors=["No files found in directory"],
                    warnings=[]
                )
            
            # Compress files
            return self.compress_files(all_files, output_path, format, compression_level, True)
            
        except Exception as e:
            return CompressionResult(
                success=False,
                archive_path="",
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                files_compressed=0,
                errors=[f"Directory compression failed: {str(e)}"],
                warnings=[]
            )
    
    def decompress_archive(
        self,
        archive_path: str,
        extract_path: str,
        format: Optional[CompressionFormat] = None
    ) -> CompressionResult:
        """Decompress an archive"""
        try:
            if not os.path.exists(archive_path):
                return CompressionResult(
                    success=False,
                    archive_path=archive_path,
                    original_size=0,
                    compressed_size=0,
                    compression_ratio=0.0,
                    files_compressed=0,
                    errors=[f"Archive not found: {archive_path}"],
                    warnings=[]
                )
            
            # Auto-detect format if not specified
            if format is None:
                format = self._detect_compression_format(archive_path)
            
            if format is None:
                return CompressionResult(
                    success=False,
                    archive_path=archive_path,
                    original_size=0,
                    compressed_size=0,
                    compression_ratio=0.0,
                    files_compressed=0,
                    errors=["Could not detect compression format"],
                    warnings=[]
                )
            
            # Get decompression function
            decompress_func = self.decompression_formats.get(format)
            if not decompress_func:
                return CompressionResult(
                    success=False,
                    archive_path=archive_path,
                    original_size=0,
                    compressed_size=0,
                    compression_ratio=0.0,
                    files_compressed=0,
                    errors=[f"Unsupported decompression format: {format}"],
                    warnings=[]
                )
            
            # Decompress archive
            result = decompress_func(archive_path, extract_path)
            
            return result
            
        except Exception as e:
            return CompressionResult(
                success=False,
                archive_path=archive_path,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                files_compressed=0,
                errors=[f"Decompression failed: {str(e)}"],
                warnings=[]
            )
    
    def get_archive_info(self, archive_path: str) -> Dict[str, Any]:
        """Get information about an archive"""
        try:
            if not os.path.exists(archive_path):
                return {"error": f"Archive not found: {archive_path}"}
            
            format = self._detect_compression_format(archive_path)
            if format is None:
                return {"error": "Could not detect compression format"}
            
            if format == CompressionFormat.ZIP:
                return self._get_zip_info(archive_path)
            elif format in [CompressionFormat.TAR, CompressionFormat.TAR_GZ, CompressionFormat.TAR_BZ2]:
                return self._get_tar_info(archive_path)
            else:
                return {"error": f"Info not supported for format: {format}"}
            
        except Exception as e:
            return {"error": f"Failed to get archive info: {str(e)}"}
    
    def _compress_zip(
        self,
        file_paths: List[str],
        output_path: str,
        compression_level: int,
        include_base_dir: bool
    ) -> CompressionResult:
        """Compress files into ZIP archive"""
        try:
            original_size = sum(os.path.getsize(f) for f in file_paths)
            
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zipf:
                for file_path in file_paths:
                    if include_base_dir:
                        arcname = os.path.basename(file_path)
                    else:
                        arcname = file_path
                    
                    zipf.write(file_path, arcname)
            
            compressed_size = os.path.getsize(output_path)
            compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            
            return CompressionResult(
                success=True,
                archive_path=output_path,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                files_compressed=len(file_paths),
                errors=[],
                warnings=[]
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                archive_path=output_path,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                files_compressed=0,
                errors=[f"ZIP compression failed: {str(e)}"],
                warnings=[]
            )
    
    def _compress_tar(
        self,
        file_paths: List[str],
        output_path: str,
        compression_level: int,
        include_base_dir: bool
    ) -> CompressionResult:
        """Compress files into TAR archive"""
        try:
            original_size = sum(os.path.getsize(f) for f in file_paths)
            
            with tarfile.open(output_path, 'w') as tar:
                for file_path in file_paths:
                    if include_base_dir:
                        arcname = os.path.basename(file_path)
                    else:
                        arcname = file_path
                    
                    tar.add(file_path, arcname=arcname)
            
            compressed_size = os.path.getsize(output_path)
            compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            
            return CompressionResult(
                success=True,
                archive_path=output_path,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                files_compressed=len(file_paths),
                errors=[],
                warnings=[]
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                archive_path=output_path,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                files_compressed=0,
                errors=[f"TAR compression failed: {str(e)}"],
                warnings=[]
            )
    
    def _compress_tar_gz(
        self,
        file_paths: List[str],
        output_path: str,
        compression_level: int,
        include_base_dir: bool
    ) -> CompressionResult:
        """Compress files into TAR.GZ archive"""
        try:
            original_size = sum(os.path.getsize(f) for f in file_paths)
            
            with tarfile.open(output_path, 'w:gz', compresslevel=compression_level) as tar:
                for file_path in file_paths:
                    if include_base_dir:
                        arcname = os.path.basename(file_path)
                    else:
                        arcname = file_path
                    
                    tar.add(file_path, arcname=arcname)
            
            compressed_size = os.path.getsize(output_path)
            compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            
            return CompressionResult(
                success=True,
                archive_path=output_path,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                files_compressed=len(file_paths),
                errors=[],
                warnings=[]
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                archive_path=output_path,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                files_compressed=0,
                errors=[f"TAR.GZ compression failed: {str(e)}"],
                warnings=[]
            )
    
    def _compress_tar_bz2(
        self,
        file_paths: List[str],
        output_path: str,
        compression_level: int,
        include_base_dir: bool
    ) -> CompressionResult:
        """Compress files into TAR.BZ2 archive"""
        try:
            original_size = sum(os.path.getsize(f) for f in file_paths)
            
            with tarfile.open(output_path, 'w:bz2', compresslevel=compression_level) as tar:
                for file_path in file_paths:
                    if include_base_dir:
                        arcname = os.path.basename(file_path)
                    else:
                        arcname = file_path
                    
                    tar.add(file_path, arcname=arcname)
            
            compressed_size = os.path.getsize(output_path)
            compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            
            return CompressionResult(
                success=True,
                archive_path=output_path,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                files_compressed=len(file_paths),
                errors=[],
                warnings=[]
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                archive_path=output_path,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                files_compressed=0,
                errors=[f"TAR.BZ2 compression failed: {str(e)}"],
                warnings=[]
            )
    
    def _compress_gzip(
        self,
        file_paths: List[str],
        output_path: str,
        compression_level: int,
        include_base_dir: bool
    ) -> CompressionResult:
        """Compress files using GZIP"""
        try:
            if len(file_paths) > 1:
                return CompressionResult(
                    success=False,
                    archive_path=output_path,
                    original_size=0,
                    compressed_size=0,
                    compression_ratio=0.0,
                    files_compressed=0,
                    errors=["GZIP can only compress single files"],
                    warnings=[]
                )
            
            file_path = file_paths[0]
            original_size = os.path.getsize(file_path)
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(output_path, 'wb', compresslevel=compression_level) as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            compressed_size = os.path.getsize(output_path)
            compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            
            return CompressionResult(
                success=True,
                archive_path=output_path,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                files_compressed=1,
                errors=[],
                warnings=[]
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                archive_path=output_path,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                files_compressed=0,
                errors=[f"GZIP compression failed: {str(e)}"],
                warnings=[]
            )
    
    def _compress_bzip2(
        self,
        file_paths: List[str],
        output_path: str,
        compression_level: int,
        include_base_dir: bool
    ) -> CompressionResult:
        """Compress files using BZIP2"""
        try:
            if len(file_paths) > 1:
                return CompressionResult(
                    success=False,
                    archive_path=output_path,
                    original_size=0,
                    compressed_size=0,
                    compression_ratio=0.0,
                    files_compressed=0,
                    errors=["BZIP2 can only compress single files"],
                    warnings=[]
                )
            
            file_path = file_paths[0]
            original_size = os.path.getsize(file_path)
            
            import bz2
            
            with open(file_path, 'rb') as f_in:
                with bz2.open(output_path, 'wb', compresslevel=compression_level) as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            compressed_size = os.path.getsize(output_path)
            compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            
            return CompressionResult(
                success=True,
                archive_path=output_path,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                files_compressed=1,
                errors=[],
                warnings=[]
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                archive_path=output_path,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                files_compressed=0,
                errors=[f"BZIP2 compression failed: {str(e)}"],
                warnings=[]
            )
    
    def _decompress_zip(self, archive_path: str, extract_path: str) -> CompressionResult:
        """Decompress ZIP archive"""
        try:
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                zipf.extractall(extract_path)
                file_list = zipf.namelist()
            
            return CompressionResult(
                success=True,
                archive_path=archive_path,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                files_compressed=len(file_list),
                errors=[],
                warnings=[]
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                archive_path=archive_path,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                files_compressed=0,
                errors=[f"ZIP decompression failed: {str(e)}"],
                warnings=[]
            )
    
    def _decompress_tar(self, archive_path: str, extract_path: str) -> CompressionResult:
        """Decompress TAR archive"""
        try:
            with tarfile.open(archive_path, 'r') as tar:
                tar.extractall(extract_path)
                file_list = tar.getnames()
            
            return CompressionResult(
                success=True,
                archive_path=archive_path,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                files_compressed=len(file_list),
                errors=[],
                warnings=[]
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                archive_path=archive_path,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                files_compressed=0,
                errors=[f"TAR decompression failed: {str(e)}"],
                warnings=[]
            )
    
    def _decompress_tar_gz(self, archive_path: str, extract_path: str) -> CompressionResult:
        """Decompress TAR.GZ archive"""
        try:
            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(extract_path)
                file_list = tar.getnames()
            
            return CompressionResult(
                success=True,
                archive_path=archive_path,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                files_compressed=len(file_list),
                errors=[],
                warnings=[]
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                archive_path=archive_path,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                files_compressed=0,
                errors=[f"TAR.GZ decompression failed: {str(e)}"],
                warnings=[]
            )
    
    def _decompress_tar_bz2(self, archive_path: str, extract_path: str) -> CompressionResult:
        """Decompress TAR.BZ2 archive"""
        try:
            with tarfile.open(archive_path, 'r:bz2') as tar:
                tar.extractall(extract_path)
                file_list = tar.getnames()
            
            return CompressionResult(
                success=True,
                archive_path=archive_path,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                files_compressed=len(file_list),
                errors=[],
                warnings=[]
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                archive_path=archive_path,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                files_compressed=0,
                errors=[f"TAR.BZ2 decompression failed: {str(e)}"],
                warnings=[]
            )
    
    def _decompress_gzip(self, archive_path: str, extract_path: str) -> CompressionResult:
        """Decompress GZIP archive"""
        try:
            import gzip
            
            # Create output directory if it doesn't exist
            os.makedirs(extract_path, exist_ok=True)
            
            # Determine output filename
            output_filename = os.path.basename(archive_path)
            if output_filename.endswith('.gz'):
                output_filename = output_filename[:-3]
            
            output_path = os.path.join(extract_path, output_filename)
            
            with gzip.open(archive_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            return CompressionResult(
                success=True,
                archive_path=archive_path,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                files_compressed=1,
                errors=[],
                warnings=[]
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                archive_path=archive_path,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                files_compressed=0,
                errors=[f"GZIP decompression failed: {str(e)}"],
                warnings=[]
            )
    
    def _decompress_bzip2(self, archive_path: str, extract_path: str) -> CompressionResult:
        """Decompress BZIP2 archive"""
        try:
            import bz2
            
            # Create output directory if it doesn't exist
            os.makedirs(extract_path, exist_ok=True)
            
            # Determine output filename
            output_filename = os.path.basename(archive_path)
            if output_filename.endswith('.bz2'):
                output_filename = output_filename[:-4]
            
            output_path = os.path.join(extract_path, output_filename)
            
            with bz2.open(archive_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            return CompressionResult(
                success=True,
                archive_path=archive_path,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                files_compressed=1,
                errors=[],
                warnings=[]
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                archive_path=archive_path,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                files_compressed=0,
                errors=[f"BZIP2 decompression failed: {str(e)}"],
                warnings=[]
            )
    
    def _detect_compression_format(self, archive_path: str) -> Optional[CompressionFormat]:
        """Detect compression format from file extension"""
        extension = os.path.splitext(archive_path)[1].lower()
        
        format_map = {
            '.zip': CompressionFormat.ZIP,
            '.tar': CompressionFormat.TAR,
            '.tar.gz': CompressionFormat.TAR_GZ,
            '.tgz': CompressionFormat.TAR_GZ,
            '.tar.bz2': CompressionFormat.TAR_BZ2,
            '.tbz2': CompressionFormat.TAR_BZ2,
            '.gz': CompressionFormat.GZIP,
            '.bz2': CompressionFormat.BZIP2
        }
        
        return format_map.get(extension)
    
    def _get_zip_info(self, archive_path: str) -> Dict[str, Any]:
        """Get information about ZIP archive"""
        try:
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                file_list = zipf.namelist()
                total_size = sum(info.file_size for info in zipf.infolist())
                compressed_size = sum(info.compress_size for info in zipf.infolist())
                
                return {
                    "format": "ZIP",
                    "files": len(file_list),
                    "total_size": total_size,
                    "compressed_size": compressed_size,
                    "compression_ratio": (1 - compressed_size / total_size) * 100 if total_size > 0 else 0,
                    "file_list": file_list
                }
        except Exception as e:
            return {"error": f"Failed to get ZIP info: {str(e)}"}
    
    def _get_tar_info(self, archive_path: str) -> Dict[str, Any]:
        """Get information about TAR archive"""
        try:
            with tarfile.open(archive_path, 'r') as tar:
                file_list = tar.getnames()
                total_size = sum(member.size for member in tar.getmembers() if member.isfile())
                
                return {
                    "format": "TAR",
                    "files": len(file_list),
                    "total_size": total_size,
                    "compressed_size": os.path.getsize(archive_path),
                    "compression_ratio": (1 - os.path.getsize(archive_path) / total_size) * 100 if total_size > 0 else 0,
                    "file_list": file_list
                }
        except Exception as e:
            return {"error": f"Failed to get TAR info: {str(e)}"}
