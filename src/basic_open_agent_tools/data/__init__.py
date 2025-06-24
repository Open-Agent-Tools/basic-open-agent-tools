"""Data tools for AI agents.

This module provides data processing and manipulation tools organized into logical submodules:

- structures: Data structure manipulation and transformation
- json_tools: JSON serialization, compression, and validation
- csv_tools: CSV file processing, parsing, and cleaning
- validation: Data validation and schema checking
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
from .structures import (
    compare_data_structures,
    extract_keys,
    flatten_dict,
    get_nested_value,
    merge_dicts,
    remove_empty_values,
    rename_keys,
    safe_get,
    set_nested_value,
    unflatten_dict,
)
from .validation import (
    aggregate_validation_errors,
    check_required_fields,
    create_validation_report,
    validate_data_types,
    validate_range,
    validate_schema,
)

# Re-export all functions at module level for convenience
__all__: List[str] = [
    # Data structures
    "flatten_dict",
    "unflatten_dict",
    "get_nested_value",
    "set_nested_value",
    "merge_dicts",
    "compare_data_structures",
    "safe_get",
    "remove_empty_values",
    "extract_keys",
    "rename_keys",
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
    # Validation
    "validate_schema",
    "check_required_fields",
    "validate_data_types",
    "validate_range",
    "aggregate_validation_errors",
    "create_validation_report",
]
