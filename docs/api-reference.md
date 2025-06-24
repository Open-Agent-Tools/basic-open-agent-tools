# API Reference

## File System Module

The `file_system` module provides comprehensive file and directory operations organized into logical submodules. **Functions are designed as tools for AI agents** and can be imported individually for agent framework integration.

### Import Options for Agent Integration

#### Individual Function Imports (Recommended for AI Agents)

```python
# Import specific functions to use as agent tools
from basic_open_agent_tools.file_system.operations import (
    read_file_to_string, write_file_from_string, append_to_file,
    create_directory, delete_file, move_file, copy_file
)
from basic_open_agent_tools.file_system.info import (
    file_exists, directory_exists, get_file_info, get_file_size
)

# Use in agent frameworks (Google ADK example)
tools = [read_file_to_string, write_file_from_string, file_exists, ...]
```

#### Module Import (For Direct Usage)

```python
# Main module import for direct developer usage
from basic_open_agent_tools import file_system

# Submodule imports for specific functionality
from basic_open_agent_tools.file_system.operations import read_file_to_string
from basic_open_agent_tools.file_system.info import get_file_info
from basic_open_agent_tools.file_system.tree import generate_directory_tree
from basic_open_agent_tools.file_system.validation import validate_path
```

## Core Operations (`operations`)

### File Operations

#### `read_file_to_string(file_path: str) -> str`
Load string from a text file.

**Parameters:**
- `file_path` (str): Path to the text file

**Returns:**
- str: The file content as a string with leading/trailing whitespace stripped

**Raises:**
- `FileSystemError`: If file doesn't exist or can't be read

**Example:**
```python
content = file_system.read_file_to_string("example.txt")
```

#### `write_file_from_string(file_path: str, content: str) -> bool`
Write string content to a text file.

**Parameters:**
- `file_path` (str): Path to the output file
- `content` (str): String content to write

**Returns:**
- bool: True if successful

**Raises:**
- `FileSystemError`: If write operation fails

**Example:**
```python
success = file_system.write_file_from_string("output.txt", "Hello World!")
```

#### `append_to_file(file_path: str, content: str) -> bool`
Append string content to a text file.

**Parameters:**
- `file_path` (str): Path to the file
- `content` (str): String content to append

**Returns:**
- bool: True if successful

**Raises:**
- `FileSystemError`: If append operation fails

### Directory Operations

#### `list_directory_contents(directory_path: str, include_hidden: bool = False) -> List[str]`
List contents of a directory.

**Parameters:**
- `directory_path` (str): Path to the directory
- `include_hidden` (bool): Whether to include hidden files/directories (default: False)

**Returns:**
- List[str]: Sorted list of file and directory names

**Raises:**
- `FileSystemError`: If directory doesn't exist or can't be read

#### `create_directory(directory_path: str) -> bool`
Create a directory and any necessary parent directories.

**Parameters:**
- `directory_path` (str): Path to the directory to create

**Returns:**
- bool: True if successful

**Raises:**
- `FileSystemError`: If directory creation fails

#### `delete_file(file_path: str) -> bool`
Delete a file.

**Parameters:**
- `file_path` (str): Path to the file to delete

**Returns:**
- bool: True if successful (including if file doesn't exist)

**Raises:**
- `FileSystemError`: If deletion fails

#### `delete_directory(directory_path: str, recursive: bool = False) -> bool`
Delete a directory.

**Parameters:**
- `directory_path` (str): Path to the directory to delete
- `recursive` (bool): If True, delete directory and all contents recursively

**Returns:**
- bool: True if successful (including if directory doesn't exist)

**Raises:**
- `FileSystemError`: If deletion fails

#### `move_file(source_path: str, destination_path: str) -> bool`
Move or rename a file or directory.

**Parameters:**
- `source_path` (str): Current path of the file/directory
- `destination_path` (str): New path for the file/directory

**Returns:**
- bool: True if successful

**Raises:**
- `FileSystemError`: If move operation fails

#### `copy_file(source_path: str, destination_path: str) -> bool`
Copy a file or directory.

**Parameters:**
- `source_path` (str): Path of the source file/directory
- `destination_path` (str): Path for the copied file/directory

**Returns:**
- bool: True if successful

**Raises:**
- `FileSystemError`: If copy operation fails

## File Information (`info`)

#### `get_file_info(file_path: str) -> Dict[str, Union[str, int, float, bool]]`
Get comprehensive information about a file or directory.

**Parameters:**
- `file_path` (str): Path to the file or directory

**Returns:**
- Dict: File information including size, modification time, permissions, etc.

**Raises:**
- `FileSystemError`: If file/directory doesn't exist or can't be accessed

#### `file_exists(file_path: str) -> bool`
Check if a file exists.

**Parameters:**
- `file_path` (str): Path to check

**Returns:**
- bool: True if file exists, False otherwise

#### `directory_exists(directory_path: str) -> bool`
Check if a directory exists.

**Parameters:**
- `directory_path` (str): Path to check

**Returns:**
- bool: True if directory exists, False otherwise

#### `get_file_size(file_path: str) -> int`
Get the size of a file in bytes.

**Parameters:**
- `file_path` (str): Path to the file

**Returns:**
- int: File size in bytes

**Raises:**
- `FileSystemError`: If file doesn't exist or can't be accessed

#### `is_empty_directory(directory_path: str) -> bool`
Check if a directory is empty.

**Parameters:**
- `directory_path` (str): Path to the directory

**Returns:**
- bool: True if directory is empty, False otherwise

**Raises:**
- `FileSystemError`: If directory doesn't exist or can't be accessed

## Directory Tree Operations (`tree`)

#### `list_all_directory_contents(directory_path: str, include_hidden: bool = False) -> List[str]`
Recursively list all files and directories.

**Parameters:**
- `directory_path` (str): Path to the directory
- `include_hidden` (bool): Whether to include hidden files/directories (default: False)

**Returns:**
- List[str]: List of all files and directories (with full paths)

**Raises:**
- `FileSystemError`: If directory doesn't exist or can't be accessed

#### `generate_directory_tree(directory_path: str, max_depth: int = None, include_hidden: bool = False) -> str`
Generate a visual directory tree representation.

**Parameters:**
- `directory_path` (str): Path to the directory
- `max_depth` (int, optional): Maximum depth to traverse (default: None for unlimited)
- `include_hidden` (bool): Whether to include hidden files/directories (default: False)

**Returns:**
- str: Visual tree representation of the directory structure

**Raises:**
- `FileSystemError`: If directory doesn't exist or can't be accessed

**Example:**
```python
tree = file_system.generate_directory_tree(".", max_depth=2)
print(tree)
```

## Path Validation (`validation`)

#### `validate_path(path: str, operation: str) -> Path`
Validate and convert a path string to a Path object.

**Parameters:**
- `path` (str): Path to validate
- `operation` (str): Description of the operation (for error messages)

**Returns:**
- Path: Validated Path object

**Raises:**
- `FileSystemError`: If path is invalid

#### `validate_file_content(content: str, operation: str) -> None`
Validate file content before operations.

**Parameters:**
- `content` (str): Content to validate
- `operation` (str): Description of the operation (for error messages)

**Raises:**
- `FileSystemError`: If content is invalid

## Exceptions

### `FileSystemError`
Base exception for all file system operations. Inherits from `BasicAgentToolsError`.

## Type Definitions

### `PathLike`
Type alias for `Union[str, Path]` - accepts both string paths and Path objects.

## Agent Integration Examples

### Google ADK Integration

```python
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from basic_open_agent_tools.file_system.operations import (
    read_file_to_string, write_file_from_string, create_directory
)

# Create agent with file system tools
agent = Agent(
    model=LiteLlm(model="anthropic/claude-3-5-haiku-20241022"),
    name="FileOps",
    tools=[read_file_to_string, write_file_from_string, create_directory],
)
```

### LangChain Integration

```python
from langchain.tools import StructuredTool
from basic_open_agent_tools.file_system.operations import read_file_to_string

# Wrap function as LangChain tool
read_tool = StructuredTool.from_function(
    func=read_file_to_string,
    name="read_file",
    description="Read contents of a text file"
)
```

### Custom Agent Integration

```python
# Direct function usage in custom agents
from basic_open_agent_tools.file_system.operations import write_file_from_string

class CustomAgent:
    def __init__(self):
        self.tools = {
            'write_file': write_file_from_string,
            # ... other tools
        }
    
    def execute_tool(self, tool_name, **kwargs):
        return self.tools[tool_name](**kwargs)
```

## Future Modules for Agent Toolkits

The following modules are planned to expand agent capabilities:

- `basic_open_agent_tools.http` - HTTP request utilities for web-enabled agents
- `basic_open_agent_tools.text` - Text processing and manipulation tools
- `basic_open_agent_tools.data` - Data parsing and conversion utilities
- `basic_open_agent_tools.system` - System information and process management tools
- `basic_open_agent_tools.crypto` - Cryptographic utilities for secure agents
- `basic_open_agent_tools.utilities` - Common helper functions and utilities

Each module will provide individual functions optimized for agent tool integration. See individual TODO.md files in each module directory for planned functionality.