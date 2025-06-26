"""Basic Open Agent Tools.

An open foundational toolkit providing essential components for building AI agents
with minimal dependencies for local (non-HTTP/API) actions.
"""

from typing import List

__version__ = "0.6.1"

# Modular structure
from . import data, exceptions, file_system, text, types

# Helper functions for tool management
from .helpers import (
    get_tool_info,
    list_all_available_tools,
    load_all_data_tools,
    load_all_filesystem_tools,
    load_all_read_only_tools,
    load_all_text_tools,
    load_data_archive_tools,
    load_data_binary_tools,
    load_data_config_tools,
    load_data_csv_tools,
    load_data_json_tools,
    load_data_object_tools,
    load_data_structure_tools,
    load_data_transformation_tools,
    load_data_validation_tools,
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
    "data",
    # Future modules (uncomment when implemented)
    # "system",
    # "network",
    # "crypto",
    # "utilities",
    # Common infrastructure
    "exceptions",
    "types",
    # Helper functions
    "load_all_filesystem_tools",
    "load_all_text_tools",
    "load_all_data_tools",
    "load_all_read_only_tools",
    "load_data_json_tools",
    "load_data_csv_tools",
    "load_data_structure_tools",
    "load_data_validation_tools",
    "load_data_transformation_tools",
    "load_data_object_tools",
    "load_data_config_tools",
    "load_data_binary_tools",
    "load_data_archive_tools",
    "merge_tool_lists",
    "get_tool_info",
    "list_all_available_tools",
]
