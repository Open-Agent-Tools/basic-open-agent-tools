"""Helper functions for loading and managing tool collections."""

import inspect
from typing import Any, Callable, Union

from . import (
    archive,
    crypto,
    data,
    datetime,
    file_system,
    network,
    system,
    text,
    todo,
    utilities,
)
from . import logging as log_module


def load_all_filesystem_tools() -> list[Callable[..., Any]]:
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


def load_all_text_tools() -> list[Callable[..., Any]]:
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


def load_all_data_tools() -> list[Callable[..., Any]]:
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


def load_all_datetime_tools() -> list[Callable[..., Any]]:
    """Load all datetime tools as a list of callable functions.

    Returns:
        List of all datetime tool functions

    Example:
        >>> datetime_tools = load_all_datetime_tools()
        >>> len(datetime_tools) > 0
        True
    """
    tools = []

    # Get all functions from datetime module
    for name in datetime.__all__:
        func = getattr(datetime, name)
        if callable(func):
            tools.append(func)

    return tools


def load_all_network_tools() -> list[Callable[..., Any]]:
    """Load all network tools as a list of callable functions.

    Returns:
        List of all network tool functions

    Example:
        >>> network_tools = load_all_network_tools()
        >>> len(network_tools) > 0
        True
    """
    tools = []

    # Get all functions from network module
    for name in network.__all__:
        func = getattr(network, name)
        if callable(func):
            tools.append(func)

    return tools


def load_all_utilities_tools() -> list[Callable[..., Any]]:
    """Load all utilities tools as a list of callable functions.

    Returns:
        List of all utilities tool functions

    Example:
        >>> utilities_tools = load_all_utilities_tools()
        >>> len(utilities_tools) > 0
        True
    """
    tools = []

    # Get all functions from utilities module
    for name in utilities.__all__:
        func = getattr(utilities, name)
        if callable(func):
            tools.append(func)

    return tools


def load_all_system_tools() -> list[Callable[..., Any]]:
    """Load all system tools as a list of callable functions."""
    tools = []
    for name in system.__all__:
        func = getattr(system, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_crypto_tools() -> list[Callable[..., Any]]:
    """Load all crypto tools as a list of callable functions."""
    tools = []
    for name in crypto.__all__:
        func = getattr(crypto, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_archive_tools() -> list[Callable[..., Any]]:
    """Load all archive tools as a list of callable functions."""
    tools = []
    for name in archive.__all__:
        func = getattr(archive, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_logging_tools() -> list[Callable[..., Any]]:
    """Load all logging tools as a list of callable functions."""
    tools = []
    for name in log_module.__all__:
        func = getattr(log_module, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_todo_tools() -> list[Callable[..., Any]]:
    """Load all todo tools as a list of callable functions."""
    tools = []
    for name in todo.__all__:
        func = getattr(todo, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_tools() -> list[Callable[..., Any]]:
    """Load all tools from all modules as a single list of callable functions.

    This is a convenience function that loads and combines tools from all
    implemented modules.

    Returns:
        List of all tool functions from all modules (automatically deduplicated)

    Example:
        >>> all_tools = load_all_tools()
        >>> len(all_tools) >= 150  # Total with all new modules
        True
        >>> # Use with agent frameworks
        >>> agent = Agent(tools=load_all_tools())
    """
    return merge_tool_lists(
        load_all_filesystem_tools(),  # 18 functions
        load_all_text_tools(),  # 10 functions
        load_all_data_tools(),  # 23 functions
        load_all_datetime_tools(),  # 40 functions
        load_all_network_tools(),  # 3 functions
        load_all_utilities_tools(),  # 3 functions
        load_all_system_tools(),  # ~20 functions
        load_all_crypto_tools(),  # ~13 functions
        load_all_archive_tools(),  # 5 functions
        load_all_logging_tools(),  # 5 functions
        load_all_todo_tools(),  # 8 functions
    )


def load_data_json_tools() -> list[Callable[..., Any]]:
    """Load JSON processing tools as a list of callable functions.

    Returns:
        List of JSON processing tool functions

    Example:
        >>> json_tools = load_data_json_tools()
        >>> len(json_tools) == 3
        True
    """
    from .data import json_tools

    tools = []
    json_function_names = [
        "safe_json_serialize",
        "safe_json_deserialize",
        "validate_json_string",
    ]

    for name in json_function_names:
        func = getattr(json_tools, name)
        if callable(func):
            tools.append(func)

    return tools


def load_data_csv_tools() -> list[Callable[..., Any]]:
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


def load_data_validation_tools() -> list[Callable[..., Any]]:
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


def load_data_config_tools() -> list[Callable[..., Any]]:
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


def merge_tool_lists(
    *args: Union[list[Callable[..., Any]], Callable[..., Any]],
) -> list[Callable[..., Any]]:
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


def get_tool_info(tool: Callable[..., Any]) -> dict[str, Any]:
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


def list_all_available_tools() -> dict[str, list[dict[str, Any]]]:
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
        "datetime": [get_tool_info(tool) for tool in load_all_datetime_tools()],
    }
