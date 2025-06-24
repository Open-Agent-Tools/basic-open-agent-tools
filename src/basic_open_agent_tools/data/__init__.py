"""Data tools for AI agents.

This module provides data processing and manipulation tools organized into logical submodules:

- json_tools: JSON serialization, compression, and validation
- csv_tools: CSV file processing, parsing, and cleaning
"""

from typing import List

# Import all functions from submodules
from .csv_tools import (
    clean_csv_data,
    csv_to_dict_list,
    detect_csv_delimiter,
    dict_list_to_csv,
    read_csv_file,
    validate_csv_structure,
    write_csv_file,
)
from .json_tools import (
    compress_json_data,
    decompress_json_data,
    safe_json_deserialize,
    safe_json_serialize,
    validate_json_string,
)

# Re-export all functions at module level for convenience
__all__: List[str] = [
    # JSON processing
    "safe_json_serialize",
    "safe_json_deserialize",
    "validate_json_string",
    "compress_json_data",
    "decompress_json_data",
    # CSV processing
    "read_csv_file",
    "write_csv_file",
    "csv_to_dict_list",
    "dict_list_to_csv",
    "detect_csv_delimiter",
    "validate_csv_structure",
    "clean_csv_data",
]
