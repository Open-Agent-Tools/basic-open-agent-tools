# File System Tools Status

## Overview
File system operations, directory management, and file manipulation tools for AI agents.

## Current Status
All planned file system modules have been implemented and tested:
- ✅ File and directory information gathering
- ✅ Basic file operations (read, write, append)
- ✅ Directory operations (create, list, delete)
- ✅ File system navigation and tree generation
- ✅ File validation and path handling
- ✅ Advanced file operations (move, copy, replace, insert)

## Design Considerations for Agent Tools
- Cross-platform compatibility (Windows, macOS, Linux)
- Functions designed as individual agent tools
- Path validation and security checks
- Clear error messages and handling
- Memory-efficient file operations
- Safe file manipulation with backup strategies
- Consistent API design across modules
- Functions suitable for agent framework integration
- Clear function signatures optimized for AI tool usage
- Security-conscious file operations with path traversal protection
- Size limits to prevent resource exhaustion
- **Focus on local file system operations only** (no network file systems)
- **Exclude binary file processing** (images, videos, etc. - use specialized tools)
- Support both absolute and relative path handling
- Atomic operations where possible to prevent corruption
- Comprehensive error reporting for debugging

## Excluded from File System Module (Separate Module Considerations)
- **Binary File Processing** - Image, video, audio manipulation (should be in dedicated modules)
- **Archive/Compression** - ZIP, TAR, GZIP handling (complex operations, better in data module)
- **File Watching/Monitoring** - Real-time file system events (requires event loops, system-specific)
- **Network File Systems** - FTP, SFTP, cloud storage access (networking concerns, credentials)

## Function Signatures

### File Information
- `get_file_info(file_path: str) -> dict` - Get comprehensive file metadata
- `file_exists(file_path: str) -> bool` - Check if file exists
- `directory_exists(directory_path: str) -> bool` - Check if directory exists
- `get_file_size(file_path: str) -> int` - Get file size in bytes
- `is_empty_directory(directory_path: str) -> bool` - Check if directory is empty

### File Operations
- `read_file_to_string(file_path: str) -> str` - Read entire file as string
- `write_file_from_string(file_path: str, content: str) -> bool` - Write string to file
- `append_to_file(file_path: str, content: str) -> bool` - Append content to file
- `delete_file(file_path: str) -> bool` - Delete a file
- `move_file(source_path: str, destination_path: str) -> bool` - Move/rename file
- `copy_file(source_path: str, destination_path: str) -> bool` - Copy file to new location
- `replace_in_file(file_path: str, old_text: str, new_text: str, count: int) -> bool` - Replace text in file
- `insert_at_line(file_path: str, line_number: int, content: str) -> bool` - Insert content at specific line

### Directory Operations
- `list_directory_contents(directory_path: str, include_hidden: bool) -> List[str]` - List directory contents
- `create_directory(directory_path: str) -> bool` - Create directory (with parents)
- `delete_directory(directory_path: str, recursive: bool) -> bool` - Delete directory
- `list_all_directory_contents(directory_path: str) -> str` - Get detailed directory listing
- `generate_directory_tree(directory_path: str, max_depth: int, include_files: bool) -> str` - Generate tree structure

### Path Validation
- `validate_path(path: str, operation: str) -> Path` - Validate and resolve file paths
- `validate_file_content(content: str, operation: str) -> None` - Validate file content

## Security Features
- Path traversal protection (prevents `../` attacks)
- File size limits for read operations
- Content validation for write operations
- Permission checking before operations
- Safe error handling without path disclosure

## Performance Considerations
- Memory-efficient streaming for large files
- Atomic operations for file safety
- Minimal system calls for directory traversal
- Optimized path handling with pathlib

## Agent Integration
Compatible with:
- **Google ADK**: Direct function imports as tools
- **LangChain**: Wrappable with StructuredTool
- **Strands Agents**: Native @strands_tool decorator support
- **Custom Agents**: Simple function-based API

## Example Usage

```python
import basic_open_agent_tools as boat

# Load file system tools
fs_tools = boat.load_all_filesystem_tools()

# Individual function usage
from basic_open_agent_tools.file_system import read_file_to_string, write_file_from_string

# Read a configuration file
config_content = read_file_to_string("config.txt")

# Write processed data
success = write_file_from_string("output.txt", processed_data)
```

## Module Structure
- **info.py** - File and directory information functions (5 functions)
- **operations.py** - Core file and directory operations (11 functions)
- **tree.py** - Directory tree and listing functions (2 functions) 
- **validation.py** - Path and content validation utilities (internal use, not exported as agent tools)

**Total Functions**: 18 agent-ready tools with Google ADK compatibility