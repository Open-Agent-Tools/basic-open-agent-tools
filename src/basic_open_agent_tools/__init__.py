"""Basic Open Agent Tools.

An open foundational toolkit providing essential components for building AI agents
with minimal dependencies for local (non-HTTP/API) actions.
"""

from typing import List

__version__ = "0.9.1"

# Modular structure
from . import data, datetime, exceptions, file_system, network, text, types, utilities

# Helper functions for tool management
from .helpers import (
    get_tool_info,
    list_all_available_tools,
    load_all_data_tools,
    load_all_datetime_tools,
    load_all_filesystem_tools,
    load_all_network_tools,
    load_all_text_tools,
    load_all_tools,
    load_all_utilities_tools,
    load_data_config_tools,
    load_data_csv_tools,
    load_data_json_tools,
    load_data_validation_tools,
    merge_tool_lists,
)

# Future modules (placeholder imports for when modules are implemented)
# from . import system
# from . import crypto

__all__: List[str] = [
    # Implemented modules
    "file_system",
    "text",
    "data",
    "datetime",
    "network",
    "utilities",
    # Future modules (uncomment when implemented)
    # "system",
    # "crypto",
    # Common infrastructure
    "exceptions",
    "types",
    # Helper functions
    "load_all_filesystem_tools",
    "load_all_text_tools",
    "load_all_data_tools",
    "load_all_datetime_tools",
    "load_all_network_tools",
    "load_all_utilities_tools",
    "load_all_tools",
    "load_data_json_tools",
    "load_data_csv_tools",
    "load_data_validation_tools",
    "load_data_config_tools",
    "merge_tool_lists",
    "get_tool_info",
    "list_all_available_tools",
]
