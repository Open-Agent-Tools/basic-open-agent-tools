"""Helper functions for loading and managing tool collections."""

import inspect
from typing import Any, Callable, Dict, List, Union

from . import data, file_system, text


def load_all_filesystem_tools() -> List[Callable[..., Any]]:
    """Load all file system tools as a list of callable functions.

    Returns:
        List of all file system tool functions

    Example:
        >>> fs_tools = load_all_filesystem_tools()
        >>> len(fs_tools) > 0
        True
    """
    tools = []

    # Get all functions from file_system module
    for name in file_system.__all__:
        func = getattr(file_system, name)
        if callable(func):
            tools.append(func)

    return tools


def load_all_text_tools() -> List[Callable[..., Any]]:
    """Load all text processing tools as a list of callable functions.

    Returns:
        List of all text processing tool functions

    Example:
        >>> text_tools = load_all_text_tools()
        >>> len(text_tools) > 0
        True
    """
    tools = []

    # Get all functions from text module
    for name in text.__all__:
        func = getattr(text, name)
        if callable(func):
            tools.append(func)

    return tools


def load_all_data_tools() -> List[Callable[..., Any]]:
    """Load all data processing tools as a list of callable functions.

    Returns:
        List of all data processing tool functions

    Example:
        >>> data_tools = load_all_data_tools()
        >>> len(data_tools) > 0
        True
    """
    tools = []

    # Get all functions from data module
    for name in data.__all__:
        func = getattr(data, name)
        if callable(func):
            tools.append(func)

    return tools


def load_data_json_tools() -> List[Callable[..., Any]]:
    """Load JSON processing tools as a list of callable functions.

    Returns:
        List of JSON processing tool functions

    Example:
        >>> json_tools = load_data_json_tools()
        >>> len(json_tools) == 5
        True
    """
    from .data import json_tools

    tools = []
    json_function_names = [
        "safe_json_serialize",
        "safe_json_deserialize",
        "validate_json_string",
        "compress_json_data",
        "decompress_json_data",
    ]

    for name in json_function_names:
        func = getattr(json_tools, name)
        if callable(func):
            tools.append(func)

    return tools


def load_data_csv_tools() -> List[Callable[..., Any]]:
    """Load CSV processing tools as a list of callable functions.

    Returns:
        List of CSV processing tool functions

    Example:
        >>> csv_tools = load_data_csv_tools()
        >>> len(csv_tools) == 7
        True
    """
    from .data import csv_tools

    tools = []
    csv_function_names = [
        "read_csv_simple",
        "write_csv_simple",
        "csv_to_dict_list",
        "dict_list_to_csv",
        "detect_csv_delimiter",
        "validate_csv_structure",
        "clean_csv_data",
    ]

    for name in csv_function_names:
        func = getattr(csv_tools, name)
        if callable(func):
            tools.append(func)

    return tools


def load_data_structure_tools() -> List[Callable[..., Any]]:
    """Load data structure manipulation tools as a list of callable functions.

    Returns:
        List of data structure tool functions

    Example:
        >>> structure_tools = load_data_structure_tools()
        >>> len(structure_tools) == 10
        True
    """
    from .data import structures

    tools = []
    structure_function_names = [
        "flatten_dict_simple",
        "unflatten_dict",
        "get_nested_value_simple",
        "set_nested_value",
        "merge_dicts_simple",
        "compare_data_structures",
        "safe_get",
        "remove_empty_values",
        "extract_keys",
        "rename_keys",
    ]

    for name in structure_function_names:
        func = getattr(structures, name)
        if callable(func):
            tools.append(func)

    return tools


def load_data_validation_tools() -> List[Callable[..., Any]]:
    """Load data validation tools as a list of callable functions.

    Returns:
        List of data validation tool functions

    Example:
        >>> validation_tools = load_data_validation_tools()
        >>> len(validation_tools) == 5
        True
    """
    from .data import validation

    tools = []
    validation_function_names = [
        "validate_schema_simple",
        "check_required_fields",
        "validate_data_types_simple",
        "validate_range_simple",
        "create_validation_report",
    ]

    for name in validation_function_names:
        func = getattr(validation, name)
        if callable(func):
            tools.append(func)

    return tools


def load_data_transformation_tools() -> List[Callable[..., Any]]:
    """Load data transformation tools as a list of callable functions.

    Returns:
        List of data transformation tool functions

    Example:
        >>> transform_tools = load_data_transformation_tools()
        >>> len(transform_tools) == 7
        True
    """
    from .data import transform

    tools = []
    transform_function_names = [
        "transform_data",
        "rename_fields",
        "convert_data_types",
        "clean_data",
        "deduplicate_records",
        "normalize_data",
        "pivot_data",
    ]

    for name in transform_function_names:
        func = getattr(transform, name)
        if callable(func):
            tools.append(func)

    return tools


def load_data_object_tools() -> List[Callable[..., Any]]:
    """Load object serialization tools as a list of callable functions.

    Returns:
        List of object serialization tool functions

    Example:
        >>> object_tools = load_data_object_tools()
        >>> len(object_tools) == 4
        True
    """
    from .data import object_serialization

    tools = []
    object_function_names = [
        "serialize_object",
        "deserialize_object",
        "sanitize_for_serialization",
        "validate_pickle_safety",
    ]

    for name in object_function_names:
        func = getattr(object_serialization, name)
        if callable(func):
            tools.append(func)

    return tools


def load_data_config_tools() -> List[Callable[..., Any]]:
    """Load configuration file processing tools as a list of callable functions.

    Returns:
        List of configuration file processing tool functions

    Example:
        >>> config_tools = load_data_config_tools()
        >>> len(config_tools) == 8
        True
    """
    from .data import config_processing

    tools = []
    config_function_names = [
        "read_yaml_file",
        "write_yaml_file",
        "read_toml_file",
        "write_toml_file",
        "read_ini_file",
        "write_ini_file",
        "validate_config_schema",
        "merge_config_files",
    ]

    for name in config_function_names:
        func = getattr(config_processing, name)
        if callable(func):
            tools.append(func)

    return tools




def load_data_archive_tools() -> List[Callable[..., Any]]:
    """Load archive processing tools as a list of callable functions.

    Returns:
        List of archive processing tool functions

    Example:
        >>> archive_tools = load_data_archive_tools()
        >>> len(archive_tools) == 7
        True
    """
    from .data import archive_processing

    tools = []
    archive_function_names = [
        "create_zip_archive",
        "extract_zip_archive",
        "list_archive_contents",
        "add_to_archive",
        "create_tar_archive",
        "extract_tar_archive",
        "validate_archive_integrity",
    ]

    for name in archive_function_names:
        func = getattr(archive_processing, name)
        if callable(func):
            tools.append(func)

    return tools


def merge_tool_lists(
    *args: Union[List[Callable[..., Any]], Callable[..., Any]],
) -> List[Callable[..., Any]]:
    """Merge multiple tool lists and individual functions into a single list.

    This function automatically deduplicates tools based on their function name and module.
    If the same function appears multiple times, only the first occurrence is kept.

    Args:
        *args: Tool lists (List[Callable]) and/or individual functions (Callable)

    Returns:
        Combined list of all tools with duplicates removed

    Raises:
        TypeError: If any argument is not a list of callables or a callable

    Example:
        >>> def custom_tool(x): return x
        >>> fs_tools = load_all_filesystem_tools()
        >>> text_tools = load_all_text_tools()
        >>> all_tools = merge_tool_lists(fs_tools, text_tools, custom_tool)
        >>> custom_tool in all_tools
        True
    """
    merged = []
    seen = set()  # Track (name, module) tuples to detect duplicates

    for arg in args:
        if callable(arg):
            # Single function
            func_key = (arg.__name__, getattr(arg, "__module__", ""))
            if func_key not in seen:
                merged.append(arg)
                seen.add(func_key)
        elif isinstance(arg, list):
            # List of functions
            for item in arg:
                if not callable(item):
                    raise TypeError(
                        f"All items in tool lists must be callable, got {type(item)}"
                    )
                func_key = (item.__name__, getattr(item, "__module__", ""))
                if func_key not in seen:
                    merged.append(item)
                    seen.add(func_key)
        else:
            raise TypeError(
                f"Arguments must be callable or list of callables, got {type(arg)}"
            )

    return merged


def get_tool_info(tool: Callable[..., Any]) -> Dict[str, Any]:
    """Get information about a tool function.

    Args:
        tool: The tool function to inspect

    Returns:
        Dictionary containing tool information (name, docstring, signature)

    Example:
        >>> from basic_open_agent_tools.text import clean_whitespace
        >>> info = get_tool_info(clean_whitespace)
        >>> info['name']
        'clean_whitespace'
    """
    if not callable(tool):
        raise TypeError("Tool must be callable")

    sig = inspect.signature(tool)

    return {
        "name": tool.__name__,
        "docstring": tool.__doc__ or "",
        "signature": str(sig),
        "module": getattr(tool, "__module__", "unknown"),
        "parameters": list(sig.parameters.keys()),
    }


def load_all_read_only_tools() -> List[Callable[..., Any]]:
    """Load all read-only tools (non-destructive operations) from all modules.

    This function returns tools that only read, analyze, validate, or transform data
    without modifying files, creating new files, or performing destructive operations.
    Perfect for agents that need to analyze and process information safely.

    Returns:
        List of all read-only tool functions from file_system, data, and text modules

    Example:
        >>> read_only_tools = load_all_read_only_tools()
        >>> len(read_only_tools) > 45  # Should have 45+ read-only tools
        True
    """
    tools = []

    # File System Read-Only Tools (11 tools)
    fs_read_only = [
        "file_exists",
        "directory_exists",
        "get_file_info",
        "get_file_size",
        "is_empty_directory",
        "read_file_to_string",
        "list_directory_contents",
        "list_all_directory_contents",
        "generate_directory_tree",
        "validate_path",
        "validate_file_content",
    ]

    for name in fs_read_only:
        func = getattr(file_system, name)
        if callable(func):
            tools.append(func)

    # Text Processing Tools (10 tools - ALL are read-only)
    tools.extend(load_all_text_tools())

    # Data Read-Only Tools (31 tools)
    from .data import (
        archive_processing,
        config_processing,
        csv_tools,
        json_tools,
        object_serialization,
        structures,
        transform,
        validation,
    )

    # JSON read-only tools (2)
    data_json_read_only = ["safe_json_deserialize", "validate_json_string"]
    for name in data_json_read_only:
        func = getattr(json_tools, name)
        if callable(func):
            tools.append(func)

    # CSV read-only tools (4)
    data_csv_read_only = [
        "read_csv_simple",
        "csv_to_dict_list",
        "detect_csv_delimiter",
        "validate_csv_structure",
    ]
    for name in data_csv_read_only:
        func = getattr(csv_tools, name)
        if callable(func):
            tools.append(func)

    # Config read-only tools (4)
    data_config_read_only = [
        "read_yaml_file",
        "read_toml_file",
        "read_ini_file",
        "validate_config_schema",
    ]
    for name in data_config_read_only:
        func = getattr(config_processing, name)
        if callable(func):
            tools.append(func)


    # Archive read-only tools (2)
    data_archive_read_only = ["list_archive_contents", "validate_archive_integrity"]
    for name in data_archive_read_only:
        func = getattr(archive_processing, name)
        if callable(func):
            tools.append(func)

    # Structure read-only tools (8)
    data_structure_read_only = [
        "flatten_dict_simple",
        "unflatten_dict",
        "get_nested_value_simple",
        "merge_dicts_simple",
        "compare_data_structures",
        "safe_get",
        "remove_empty_values",
        "extract_keys",
    ]
    for name in data_structure_read_only:
        func = getattr(structures, name)
        if callable(func):
            tools.append(func)

    # Validation tools (5 - ALL are read-only)
    data_validation_read_only = [
        "validate_schema_simple",
        "check_required_fields",
        "validate_data_types_simple",
        "validate_range_simple",
        "create_validation_report",
    ]
    for name in data_validation_read_only:
        func = getattr(validation, name)
        if callable(func):
            tools.append(func)

    # Object serialization read-only tools (2)
    data_object_read_only = ["sanitize_for_serialization", "validate_pickle_safety"]
    for name in data_object_read_only:
        func = getattr(object_serialization, name)
        if callable(func):
            tools.append(func)

    # Transform read-only tools (4 - analysis/cleaning without modification)
    data_transform_read_only = [
        "clean_data",
        "deduplicate_records",
        "normalize_data",
        "convert_data_types",
    ]
    for name in data_transform_read_only:
        func = getattr(transform, name)
        if callable(func):
            tools.append(func)

    return tools


def list_all_available_tools() -> Dict[str, List[Dict[str, Any]]]:
    """List all available tools organized by category.

    Returns:
        Dictionary with tool categories as keys and lists of tool info as values

    Example:
        >>> tools = list_all_available_tools()
        >>> 'file_system' in tools
        True
        >>> 'text' in tools
        True
    """
    return {
        "file_system": [get_tool_info(tool) for tool in load_all_filesystem_tools()],
        "text": [get_tool_info(tool) for tool in load_all_text_tools()],
        "data": [get_tool_info(tool) for tool in load_all_data_tools()],
        "read_only": [get_tool_info(tool) for tool in load_all_read_only_tools()],
    }
