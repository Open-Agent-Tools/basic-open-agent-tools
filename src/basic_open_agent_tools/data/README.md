# Data Tools Status

## Overview
Data structure utilities, validation, and serialization tools for AI agents.

## Current Status
All planned data modules have been implemented and tested:
- ✅ Basic data structures and operations
- ✅ JSON and CSV processing
- ✅ Data validation and schema checking
- ✅ Object serialization and deserialization
- ✅ Configuration file processing (YAML, TOML, INI)
- ✅ Binary data handling and encoding
- ✅ Archive file creation and extraction

## Design Considerations for Agent Tools
- Memory efficiency for large datasets
- Functions designed as individual agent tools
- Type safety and validation
- Immutable data operations where possible
- Clear error messages and handling
- Performance considerations for bulk operations
- Security awareness for deserialization (especially pickle)
- Consistent API design across modules
- Functions suitable for agent framework integration
- Clear function signatures optimized for AI tool usage
- Avoid complex querying features (delegate to MCP servers)
- Focus on local data manipulation and validation
- Size limits to prevent memory exhaustion attacks
- Input sanitization for all transformation functions
- **Exclude visualization tools** (charts/graphs belong in separate visualization module)
- **Exclude Excel/spreadsheet processing** (complex dependencies, better suited for specialized tools)
- Prioritize text-based formats over binary formats where possible
- Support streaming/chunked processing for large files
- Provide both synchronous and memory-efficient variants for bulk operations

## Excluded from Data Module (Separate Module Considerations)
- **XML Processing** - Complex parsing, XPath, schema validation (heavy dependencies, specialized use cases)
- **Visualization Tools** - Charts, graphs, plots (should be in dedicated `visualization` module)
- **Excel/Spreadsheet Processing** - Complex .xlsx/.xls handling (requires heavy dependencies)
- **Machine Learning Data Prep** - Feature engineering, model-specific preprocessing (separate `ml` module)

## Function Signatures

### JSON Processing
- `safe_json_serialize(data: Union[dict, list, str, int, float, bool], indent: int) -> str`
- `safe_json_deserialize(json_str: str) -> Union[dict, list, str, int, float, bool, None]`
- `validate_json_string(json_str: str) -> bool`
- `compress_json_data(data: Union[dict, list, str, int, float, bool]) -> bytes`
- `decompress_json_data(compressed_data: bytes) -> Union[dict, list, str, int, float, bool, None]`

### CSV Processing
- `read_csv_simple(file_path: str, delimiter: str, headers: bool)`
- `write_csv_simple(data: list, file_path: str, delimiter: str, headers: bool)`
- `csv_to_dict_list(csv_data: str, delimiter: str)`
- `dict_list_to_csv(data: list, delimiter: str)`
- `detect_csv_delimiter(file_path: str, sample_size: int)`
- `validate_csv_structure(file_path: str, expected_columns: list)`
- `clean_csv_data(data: list, rules: dict)`


### Validation
- `validate_schema_simple(data: Union[dict, list, str, int, float, bool], schema: dict)`
- `check_required_fields(data: dict, required: List[str])`
- `validate_data_types_simple(data: dict, type_map: Dict[str, str])`
- `validate_range_simple(value: Union[int, float], min_val: Optional[Union[int, float]] = None, max_val: Optional[Union[int, float]] = None)`
- `create_validation_report(data: dict, rules: dict)`

### Configuration Processing
- `read_yaml_file(file_path: str)`
- `write_yaml_file(data: dict, file_path: str)`
- `read_toml_file(file_path: str)`
- `write_toml_file(data: dict, file_path: str)`
- `read_ini_file(file_path: str)`
- `write_ini_file(data: dict, file_path: str)`
- `validate_config_schema(config_data: dict, schema: dict)`
- `merge_config_files(config_paths: Union[str, List[str]], format_type: str)`
