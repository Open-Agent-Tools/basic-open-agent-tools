# Data Tools TODO

## 🎉 Phase 1 Complete! 
**Status**: ✅ 28 functions implemented across 4 modules  
**Test Coverage**: 95%+ for new modules, 81% overall  
**Quality**: 100% ruff compliance, mypy compatible

## Overview
Data structure utilities, validation, and serialization tools for AI agents.

## Required Infrastructure Updates

### Exception Classes (add to `exceptions.py`)
- [x] `DataError(BasicAgentToolsError)` - Base exception for data operations ✅
- [x] `ValidationError(DataError)` - Data validation failures ✅
- [x] `SerializationError(DataError)` - Serialization/deserialization failures ✅

### Type Definitions (add to `types.py`)
- [x] `DataDict = Dict[str, Any]` - Standard data dictionary type ✅
- [x] `NestedData = Union[Dict, List, primitives]` - Nested data structure type ✅
- [x] `ValidationResult = Dict[str, Any]` - Validation result type ✅

### Helper Functions (add to `helpers.py`)
- [x] `load_all_data_tools()` - Load all data processing functions ✅
- [x] `load_data_structure_tools()` - Load data structure manipulation functions ✅
- [x] `load_data_validation_tools()` - Load validation functions ✅
- [x] `load_data_json_tools()` - Load JSON serialization functions ✅
- [x] `load_data_csv_tools()` - Load CSV processing functions ✅
- [ ] `load_data_object_tools()` - Load object serialization functions
- [ ] `load_data_config_tools()` - Load configuration file tools
- [ ] `load_data_transformation_tools()` - Load transformation functions
- [ ] `load_data_binary_tools()` - Load binary data handling functions
- [ ] `load_data_archive_tools()` - Load archive handling functions
- [ ] `load_data_caching_tools()` - Load caching functions
- [ ] `load_data_streaming_tools()` - Load streaming functions
- [ ] `load_data_database_tools()` - Load database processing functions

## Implementation Prioritization

### Phase 1: Foundation (MVP - COMPLETED ✅)
**Goal**: Core data manipulation for agent tools, zero external dependencies  
**Status**: ✅ COMPLETE - 28 functions implemented
**Dependencies**: None (pure Python stdlib)

#### Infrastructure ✅
- [x] Exception classes (`DataError`, `ValidationError`, `SerializationError`) ✅
- [x] Type definitions (`DataDict`, `NestedData`, `ValidationResult`) ✅

#### Core Modules ✅
1. [x] **Data Structures** (`structures.py`) - 10 functions ✅
  - Essential for all other modules, zero dependencies
  - `flatten_dict(data, separator=".")` - Flatten nested dictionaries ✅
  - `unflatten_dict(data, separator=".")` - Reconstruct nested structure ✅
  - `get_nested_value(data, key_path, default=None)` - Safe nested access ✅
  - `set_nested_value(data, key_path, value)` - Immutable nested updates ✅
  - `merge_dicts(*dicts, deep=True)` - Deep merge multiple dictionaries ✅
  - `compare_data_structures(data1, data2, ignore_order=False)` - Compare structures ✅
  - `safe_get(data, key, default=None)` - Safe dictionary access ✅
  - `remove_empty_values(data, recursive=True)` - Clean empty values ✅
  - `extract_keys(data, key_pattern)` - Extract keys matching pattern ✅
  - `rename_keys(data, key_mapping)` - Rename dictionary keys ✅

2. [x] **JSON Processing** (`json_tools.py`) - 5 functions ✅
  - Built into Python stdlib, critical for agent data exchange
  - `safe_json_serialize(data, indent=None)` - JSON serialization with error handling ✅
  - `safe_json_deserialize(json_str)` - Safe JSON deserialization ✅
  - `validate_json_string(json_str)` - Validate JSON before parsing ✅
  - `compress_json_data(data)` - Compress JSON for storage/transmission ✅
  - `decompress_json_data(compressed_data)` - Decompress JSON data ✅

3. [x] **CSV Processing** (`csv_tools.py`) - 7 functions ✅
  - Extremely common for agent data tasks, high ROI
  - `read_csv_file(file_path, delimiter=",", headers=True)` - Read CSV files ✅
  - `write_csv_file(data, file_path, delimiter=",", headers=True)` - Write CSV files ✅
  - `csv_to_dict_list(csv_data)` - Convert CSV to list of dictionaries ✅
  - `dict_list_to_csv(data)` - Convert dictionary list to CSV format ✅
  - `detect_csv_delimiter(file_path)` - Auto-detect CSV delimiter ✅
  - `validate_csv_structure(file_path, expected_columns)` - Validate CSV format ✅
  - `clean_csv_data(data, rules)` - Clean CSV data according to rules ✅

4. [x] **Basic Validation** (`validation.py`) - 6 functions ✅
  - Foundation for data integrity, supports other modules
  - `validate_schema(data, schema)` - JSON Schema-style validation ✅
  - `check_required_fields(data, required)` - Ensure required fields exist ✅
  - `validate_data_types(data, type_map)` - Check field types match expectations ✅
  - `validate_range(value, min_val=None, max_val=None)` - Numeric range validation ✅
  - `aggregate_validation_errors(results)` - Combine multiple validation results ✅
  - `create_validation_report(data, rules)` - Generate detailed validation report ✅

### Phase 2: Object Serialization & Advanced Processing (Next Priority)
**Goal**: Extended serialization and processing capabilities  
**Timeline**: 1-2 weeks, 4 functions  
**Dependencies**: None (pure Python stdlib)

1. [ ] **Object Serialization** (`object_serialization.py`) - 4 functions
  - Pickle in stdlib, security-aware implementation
  - `serialize_object(obj, method="pickle")` - Object serialization (pickle/json)
  - `deserialize_object(data, method="pickle")` - Safe object deserialization  
  - `sanitize_for_serialization(data)` - Remove non-serializable objects
  - `validate_pickle_safety(data)` - Check pickle data for safety

### Phase 3: Configuration & Transformation (Medium Impact)
**Goal**: Enhanced data manipulation capabilities  
**Timeline**: 2-3 weeks, 16 functions  
**Dependencies**: PyYAML, tomli (make optional)

6. [ ] **Configuration File Processing** (`config_processing.py`) - 8 functions
  - **⚠️ Requires external dependencies** (PyYAML, tomli)
  - Essential for agent configuration management
  - `read_yaml_file(file_path)` - Read YAML configuration files
  - `write_yaml_file(data, file_path)` - Write YAML configuration files
  - `read_toml_file(file_path)` - Read TOML configuration files
  - `write_toml_file(data, file_path)` - Write TOML configuration files
  - `read_ini_file(file_path)` - Read INI configuration files
  - `write_ini_file(data, file_path)` - Write INI configuration files
  - `validate_config_schema(config_data, schema)` - Validate config against schema
  - `merge_config_files(*config_paths)` - Merge multiple config files

7. [ ] **Data Transformation** (`transform.py`) - 8 functions
  - Builds on Phase 1 foundations, high utility for data cleaning
  - `transform_data(data, mapping)` - Apply transformation mapping
  - `rename_fields(data, field_mapping)` - Batch field renaming
  - `convert_data_types(data, type_conversions)` - Batch type conversion
  - `apply_data_transformations(data, transformations)` - Apply multiple transforms
  - `clean_data(data, rules)` - Apply data cleaning rules
  - `deduplicate_records(data, key_fields)` - Remove duplicate records
  - `normalize_data(data, normalization_rules)` - Normalize data values
  - `pivot_data(data, row_key, col_key, value_key)` - Pivot table transformation

### Phase 4: Advanced Features (Lower Priority)
**Goal**: Specialized capabilities for complex use cases  
**Timeline**: 2-3 weeks, 18 functions

8. [ ] **Binary Data Processing** (`binary_processing.py`) - 6 functions
9. [ ] **Archive Processing** (`archive_processing.py`) - 7 functions  
10. [ ] **Streaming** (`streaming.py`) - 5 functions

### Phase 5: Optional/Specialized (Future Consideration)
11. [ ] **Caching** (`caching.py`) - 7 functions
12. [ ] **Database Processing** (`database_processing.py`) - 6 functions

## Deferred Modules (Detailed Specifications)

### Binary Data Processing (Phase 4)
- `read_binary_file(file_path)` - Read binary files safely
- `write_binary_file(data, file_path)` - Write binary data to file
- `encode_binary_data(data, encoding="base64")` - Encode binary for transmission
- `decode_binary_data(encoded_data, encoding="base64")` - Decode binary data
- `validate_binary_format(data, expected_format)` - Validate binary file format
- `extract_binary_metadata(file_path)` - Extract metadata from binary files

### Archive Processing (Phase 4)
- `create_zip_archive(files, archive_path)` - Create ZIP archives
- `extract_zip_archive(archive_path, extract_to)` - Extract ZIP archives
- `list_archive_contents(archive_path)` - List files in archive
- `add_to_archive(archive_path, file_path, archive_name=None)` - Add files to archive
- `create_tar_archive(files, archive_path, compression=None)` - Create TAR archives
- `extract_tar_archive(archive_path, extract_to)` - Extract TAR archives
- `validate_archive_integrity(archive_path)` - Check archive integrity

### Streaming (Phase 4)
- `stream_process_file(file_path, chunk_size=8192)` - Process large files in chunks
- `batch_process_data(data, batch_size=1000, processor_func)` - Process data in batches
- `stream_csv_reader(file_path, chunk_size=1000)` - Stream CSV file processing
- `memory_efficient_merge(file_paths, output_path)` - Merge large files efficiently
- `create_data_pipeline(processors)` - Create data processing pipeline

### Caching (Phase 5)
- `create_memory_cache(max_size=128)` - Create in-memory cache
- `cache_get(cache, key, default=None)` - Retrieve cached value
- `cache_set(cache, key, value, ttl=None)` - Store value in cache
- `cache_delete(cache, key)` - Remove cached value
- `cache_clear(cache)` - Clear all cached values
- `cache_stats(cache)` - Get cache statistics
- `create_persistent_cache(cache_dir)` - Create file-based cache

### Database Processing (Phase 5)
- `create_sqlite_connection(db_path)` - Create SQLite database connection
- `execute_sqlite_query(connection, query, params=None)` - Execute SQL query
- `sqlite_table_to_dict_list(connection, table_name)` - Export table to list
- `dict_list_to_sqlite_table(data, connection, table_name)` - Import list to table
- `backup_sqlite_database(db_path, backup_path)` - Backup SQLite database
- `validate_sqlite_schema(connection, expected_schema)` - Validate database schema

## Implementation Strategy

### Immediate Actions (Week 1)
1. **Start with Phase 1 infrastructure** - exceptions, types
2. **Implement `structures.py` first** - most foundational  
3. **Focus on high-coverage testing** - match project's 98% standard

### Dependencies Strategy
- **Phase 1-2**: Zero external dependencies (pure stdlib)
- **Phase 3**: Make YAML/TOML optional with clear error messages
- **Phase 4+**: Consider each dependency carefully against project goals

### Success Metrics
- **Phase 1**: Enables basic agent data manipulation (MVP)
- **Phase 2**: Covers 80% of common agent data tasks  
- **Phase 3**: Full configuration and transformation capability
- Each phase should maintain 70%+ test coverage

### Helper Functions Rollout
- **Phase 1**: Add `load_data_structure_tools()`, `load_data_json_tools()`, `load_data_validation_tools()`
- **Phase 2**: Add `load_data_csv_tools()`, `load_data_object_tools()`
- **Later phases**: Add remaining helpers as modules are implemented

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
- **Advanced Database Features** - Complex ORM, migrations (better handled by MCP servers)
- **Real-time Data Processing** - Streaming analytics, event processing (separate `streaming` module)
- **Machine Learning Data Prep** - Feature engineering, model-specific preprocessing (separate `ml` module)