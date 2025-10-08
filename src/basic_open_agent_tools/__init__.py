"""Basic Open Agent Tools.

An open foundational toolkit providing essential components for building AI agents
with minimal dependencies for local (non-HTTP/API) actions.
"""

__version__ = "0.12.0"

# Modular structure
from . import (
    archive,
    crypto,
    data,
    datetime,
    exceptions,
    file_system,
    network,
    system,
    text,
    todo,
    types,
    utilities,
)
from . import (
    logging as log_module,
)

# Helper functions for tool management
from .helpers import (
    get_tool_info,
    list_all_available_tools,
    load_all_archive_tools,
    load_all_crypto_tools,
    load_all_data_tools,
    load_all_datetime_tools,
    load_all_filesystem_tools,
    load_all_logging_tools,
    load_all_network_tools,
    load_all_system_tools,
    load_all_text_tools,
    load_all_todo_tools,
    load_all_tools,
    load_all_utilities_tools,
    load_data_config_tools,
    load_data_csv_tools,
    load_data_json_tools,
    load_data_validation_tools,
    merge_tool_lists,
)

__all__: list[str] = [
    # All implemented modules
    "archive",
    "crypto",
    "data",
    "datetime",
    "file_system",
    "log_module",
    "network",
    "system",
    "text",
    "todo",
    "utilities",
    # Common infrastructure
    "exceptions",
    "types",
    # Helper functions
    "load_all_archive_tools",
    "load_all_crypto_tools",
    "load_all_data_tools",
    "load_all_datetime_tools",
    "load_all_filesystem_tools",
    "load_all_logging_tools",
    "load_all_network_tools",
    "load_all_system_tools",
    "load_all_text_tools",
    "load_all_todo_tools",
    "load_all_tools",
    "load_all_utilities_tools",
    "load_data_config_tools",
    "load_data_csv_tools",
    "load_data_json_tools",
    "load_data_validation_tools",
    "merge_tool_lists",
    "get_tool_info",
    "list_all_available_tools",
]
