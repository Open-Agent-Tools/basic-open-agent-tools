"""Helper functions for loading and managing tool collections."""

import inspect
from typing import Any, Callable, Dict, List, Union

from . import file_system, text


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


def merge_tool_lists(
    *args: Union[List[Callable[..., Any]], Callable[..., Any]],
) -> List[Callable[..., Any]]:
    """Merge multiple tool lists and individual functions into a single list.

    Args:
        *args: Tool lists (List[Callable]) and/or individual functions (Callable)

    Returns:
        Combined list of all tools

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

    for arg in args:
        if callable(arg):
            # Single function
            merged.append(arg)
        elif isinstance(arg, list):
            # List of functions
            for item in arg:
                if not callable(item):
                    raise TypeError(
                        f"All items in tool lists must be callable, got {type(item)}"
                    )
                merged.append(item)
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
    }
