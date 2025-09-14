# Archive Tools

## Overview
Complete archive and compression utilities for AI agents supporting ZIP, TAR, GZIP, BZIP2, and XZ formats with detailed analytics.

## Current Status
**✅ FULLY IMPLEMENTED MODULE** - 9 functions available

## Current Features
- ✅ **ZIP Operations**: create_zip, extract_zip, compress_files
- ✅ **TAR Operations**: create_tar, extract_tar
- ✅ **GZIP Compression**: compress_file_gzip, decompress_file_gzip
- ✅ **BZIP2 Compression**: compress_file_bzip2
- ✅ **XZ/LZMA Compression**: compress_file_xz

## Function Reference

### ZIP Operations
```python
create_zip(source_paths: List[str], output_path: str)
extract_zip(zip_path: str, extract_to: str)
compress_files(file_paths: List[str], output_path: str)  # Alias for create_zip
```

### TAR Operations
```python
create_tar(source_paths: List[str], output_path: str)
extract_tar(tar_path: str, extract_to: str)
```

### Individual File Compression
```python
# GZIP compression/decompression
compress_file_gzip(input_path: str, output_path: str = None)
decompress_file_gzip(input_path: str, output_path: str = None)

# BZIP2 compression
compress_file_bzip2(input_path: str, output_path: str = None)

# XZ/LZMA compression
compress_file_xz(input_path: str, output_path: str = None)
```

## Key Features

### Compression Analytics
All compression functions return detailed metrics:
- **Compression ratio**: Output size / input size
- **Space saved**: Input size - output size in bytes
- **Compression percentage**: (1 - ratio) × 100
- **Processing statistics**: File counts, sizes, timing

### Multiple Format Support
- **ZIP**: Directory and multi-file archives with deflate compression
- **TAR**: Uncompressed archive format for file collections
- **GZIP**: Single-file compression with good speed/ratio balance
- **BZIP2**: Higher compression ratio, slower processing
- **XZ/LZMA**: Best compression ratio, modern algorithm

### Agent-Friendly Design
- Simple type signatures (str, int, List, Dict)
- Comprehensive error handling
- Detailed return dictionaries
- Cross-platform compatibility

## Usage Examples

### Basic Compression Comparison
```python
# Compare compression methods on the same file
file = "large_document.txt"

gzip_result = compress_file_gzip(file)
bzip2_result = compress_file_bzip2(file)
xz_result = compress_file_xz(file)

print(f"GZIP: {gzip_result['compression_percent']:.1f}% reduction")
print(f"BZIP2: {bzip2_result['compression_percent']:.1f}% reduction")
print(f"XZ: {xz_result['compression_percent']:.1f}% reduction")
```

### Archive Management
```python
# Create archive of project files
project_files = ["src/", "docs/", "README.md", "LICENSE"]
zip_result = create_zip(project_files, "project_backup.zip")

print(f"Archived {zip_result['files_added']} files")
print(f"Archive size: {zip_result['file_size_bytes']} bytes")

# Extract to new location
extract_result = extract_zip("project_backup.zip", "restore/")
print(f"Extracted {extract_result['files_extracted']} files")
```

## Agent Integration

### Google ADK
```python
import basic_open_agent_tools as boat
archive_tools = boat.load_all_archive_tools()
agent = Agent(tools=archive_tools)
```

### Strands Agents
```python
from basic_open_agent_tools.archive import compress_file_gzip
# Automatically compatible with @strands_tool decorator
```

## Performance Notes
- **GZIP**: Fast compression, good for frequent operations
- **BZIP2**: Better compression, slower processing
- **XZ**: Best compression, slowest processing
- **ZIP**: Good for multiple files with directory structure
- **TAR**: Fast for archiving without compression

## Dependencies
All compression functions use Python standard library modules (gzip, bz2, lzma, zipfile, tarfile) - no additional dependencies required.

## Testing
Comprehensive tests cover compression accuracy, error handling, file format compatibility, and cross-platform behavior.