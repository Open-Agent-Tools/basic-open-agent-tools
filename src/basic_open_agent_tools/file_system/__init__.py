"""File system tools for agent operations.

This module provides comprehensive file and directory operations organized into logical submodules:

- operations: Core file/directory operations (read, write, create, delete, copy, move)
- info: File information and existence checking
- tree: Directory tree listing functionality
- validation: Path validation utilities

All functions are also available directly from this module for convenience.
"""

# Import all functions from submodules
from .editor import (
    find_text_in_file,
    view_file_with_lines,
)
from .info import (
    directory_exists,
    file_exists,
    get_file_info,
    get_file_size,
    is_empty_directory,
)
from .operations import (
    append_to_file,
    copy_file,
    create_directory,
    delete_directory,
    delete_file,
    insert_at_line,
    list_directory_contents,
    move_file,
    read_file_to_string,
    replace_in_file,
    write_file_from_string,
)
from .tree import (
    generate_directory_tree,
    list_all_directory_contents,
)

# validation functions are internal utilities, not agent tools
# from .validation import (
#     validate_file_content,
#     validate_path,
# )

# Re-export all functions at module level for convenience
__all__ = [
    # File operations
    "read_file_to_string",
    "write_file_from_string",
    "append_to_file",
    "replace_in_file",
    "insert_at_line",
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
    # File editor tools (unique additions beyond basic file operations)
    "view_file_with_lines",  # View files with line numbers
    "find_text_in_file",  # Search/grep functionality
    # Note: Use write_file_from_string, replace_in_file, insert_at_line for create/edit operations
    # Note: validation utilities are internal, not exported as agent tools
]
