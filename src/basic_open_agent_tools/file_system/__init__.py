"""File system tools for agent operations.

This module provides comprehensive file and directory operations organized into logical submodules:

- operations: Core file/directory operations (read, write, create, delete, copy, move)
- info: File information and existence checking
- tree: Directory tree listing functionality  
- validation: Path validation utilities

All functions are also available directly from this module for convenience.
"""

# Import all functions from submodules
from .operations import (
    read_file_to_string,
    write_file_from_string,
    append_to_file,
    list_directory_contents,
    create_directory,
    delete_file,
    delete_directory,
    move_file,
    copy_file,
)

from .info import (
    get_file_info,
    file_exists,
    directory_exists,
    get_file_size,
    is_empty_directory,
)

from .tree import (
    list_all_directory_contents,
    generate_directory_tree,
)

from .validation import (
    validate_path,
    validate_file_content,
)

# Re-export all functions at module level for convenience
__all__ = [
    # File operations
    "read_file_to_string",
    "write_file_from_string", 
    "append_to_file",
    
    # Directory operations
    "list_directory_contents",
    "create_directory",
    "delete_file",
    "delete_directory",
    "move_file",
    "copy_file",
    
    # Information and checking
    "get_file_info",
    "file_exists",
    "directory_exists", 
    "get_file_size",
    "is_empty_directory",
    
    # Tree operations
    "list_all_directory_contents",
    "generate_directory_tree",
    
    # Validation utilities
    "validate_path",
    "validate_file_content",
]
