"""Basic Open Agent Tools.

An open foundational toolkit providing essential components for building AI agents
with minimal dependencies for local (non-HTTP/API) actions.
"""

from typing import List

__version__ = "0.2.0"

# Modular structure
from . import exceptions, file_system, text, types

# Helper functions for tool management
from .helpers import (
    get_tool_info,
    list_all_available_tools,
    load_all_filesystem_tools,
    load_all_text_tools,
    merge_tool_lists,
)

# Future modules (placeholder imports for when modules are implemented)
# from . import system
# from . import network
# from . import data
# from . import crypto
# from . import utilities

__all__: List[str] = [
    # Implemented modules
    "file_system",
    "text",
    # Future modules (uncomment when implemented)
    # "system",
    # "network",
    # "data",
    # "crypto",
    # "utilities",
    # Common infrastructure
    "exceptions",
    "types",
    # Helper functions
    "load_all_filesystem_tools",
    "load_all_text_tools",
    "merge_tool_lists",
    "get_tool_info",
    "list_all_available_tools",
]
