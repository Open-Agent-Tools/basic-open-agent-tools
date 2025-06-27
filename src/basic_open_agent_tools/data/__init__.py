"""Data tools for AI agents.

This module provides data processing and manipulation tools organized into logical submodules:

- structures: Data structure manipulation and transformation
- json_tools: JSON serialization, compression, and validation
- csv_tools: CSV file processing, parsing, and cleaning
- validation: Data validation and schema checking
- transform: Data transformation, cleaning, and normalization
- object_serialization: Object serialization and deserialization
- config_processing: Configuration file processing (YAML, TOML, INI)
- archive_processing: Archive file creation and extraction (ZIP, TAR)
"""

from typing import List

# Import all functions from submodules
from .archive_processing import (
    add_to_archive,
    create_tar_archive,
    create_zip_archive,
    extract_tar_archive,
    extract_zip_archive,
    list_archive_contents,
    validate_archive_integrity,
)
from .config_processing import (
    merge_config_files,
    read_ini_file,
    read_toml_file,
    read_yaml_file,
    validate_config_schema,
    write_ini_file,
    write_toml_file,
    write_yaml_file,
)
from .csv_tools import (
    clean_csv_data,
    csv_to_dict_list,
    detect_csv_delimiter,
    dict_list_to_csv,
    read_csv_simple,
    validate_csv_structure,
    write_csv_simple,
)
from .json_tools import (
    compress_json_data,
    decompress_json_data,
    safe_json_deserialize,
    safe_json_serialize,
    validate_json_string,
)
from .object_serialization import (
    deserialize_object,
    sanitize_for_serialization,
    serialize_object,
    validate_pickle_safety,
)
from .structures import (
    compare_data_structures,
    extract_keys,
    flatten_dict_simple,
    get_nested_value_simple,
    merge_dicts_simple,
    remove_empty_values,
    rename_keys,
    safe_get,
    set_nested_value,
    unflatten_dict,
)
from .transform import (
    clean_data,
    convert_data_types,
    deduplicate_records,
    normalize_data,
    pivot_data,
    rename_fields,
    transform_data,
)
from .validation import (
    check_required_fields,
    create_validation_report,
    validate_data_types_simple,
    validate_range_simple,
    validate_schema_simple,
)

# Re-export all functions at module level for convenience
__all__: List[str] = [
    # Data structures
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
    # JSON processing
    "safe_json_serialize",
    "safe_json_deserialize",
    "validate_json_string",
    "compress_json_data",
    "decompress_json_data",
    # CSV processing
    "read_csv_simple",
    "write_csv_simple",
    "csv_to_dict_list",
    "dict_list_to_csv",
    "detect_csv_delimiter",
    "validate_csv_structure",
    "clean_csv_data",
    # Data transformation
    "transform_data",
    "rename_fields",
    "convert_data_types",
    "clean_data",
    "deduplicate_records",
    "normalize_data",
    "pivot_data",
    # Validation
    "validate_schema_simple",
    "check_required_fields",
    "validate_data_types_simple",
    "validate_range_simple",
    "create_validation_report",
    # Object serialization
    "serialize_object",
    "deserialize_object",
    "sanitize_for_serialization",
    "validate_pickle_safety",
    # Configuration processing
    "read_yaml_file",
    "write_yaml_file",
    "read_toml_file",
    "write_toml_file",
    "read_ini_file",
    "write_ini_file",
    "validate_config_schema",
    "merge_config_files",
    # Archive processing
    "create_zip_archive",
    "extract_zip_archive",
    "list_archive_contents",
    "add_to_archive",
    "create_tar_archive",
    "extract_tar_archive",
    "validate_archive_integrity",
]
