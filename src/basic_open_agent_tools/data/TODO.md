# Data Tools TODO

## Current Status (v0.6.1)

### ✅ Completed (v0.6.0-0.6.1)
- [x] **Agent-Friendly Type Signatures**: All complex functions replaced with `*_simple` variants
- [x] **Simplified CSV Tools**: `read_csv_simple`, `write_csv_simple` with basic types (str, dict, list)
- [x] **Simplified Structure Tools**: `flatten_dict_simple`, `merge_dicts_simple`, `get_nested_value_simple`
- [x] **Simplified Validation Tools**: `validate_schema_simple`, `validate_data_types_simple`, `validate_range_simple`
- [x] **Enhanced Transform Tools**: All transformation functions use basic Python types
- [x] **Updated Helper Functions**: All helpers updated for new simplified function names
- [x] **Type Safety**: Removed complex Union types and PathLike aliases for agent compatibility
- [x] **Comprehensive Testing**: Maintained 80%+ test coverage with simplified signatures

## Future Enhancements

- [ ] **Data Caching Tools** (`caching.py`)
  - Implement caching mechanisms for frequently accessed data
  - Support for memory and disk-based caching
  - Cache invalidation strategies
  - Thread-safe caching operations

- [ ] **Streaming Data Processing** (`streaming.py`)
  - Support for processing large files in chunks
  - Memory-efficient iterators for large datasets
  - Stream transformation utilities
  - Progress tracking for long-running operations

- [ ] **Performance Optimizations**
  - Memory-efficient variants for bulk operations
  - Parallel processing options for data transformation
  - Benchmarking utilities for data operations

- [ ] **Advanced Validation Features**
  - Custom validation rule creation
  - Validation pipelines
  - Enhanced error reporting and visualization

## Maintenance Tasks

- [ ] Add comprehensive benchmarks for all data operations
- [ ] Enhance documentation with more examples
- [x] Add type hints for all return values (completed v0.6.0)
- [x] Simplify type signatures for agent compatibility (completed v0.6.0)
- [ ] Create more comprehensive test cases
- [ ] Add performance comparison between simple and complex variants

## Design Considerations for Future Development
- ✅ **Agent-First Design**: All functions use basic Python types (str, dict, list, bool)
- ✅ **No Complex Types**: Eliminated Union types, PathLike, and custom type aliases
- ✅ **Individual Import Support**: Functions designed for agent framework tool loading
- Maintain backward compatibility with existing API
- Prioritize memory efficiency for large dataset operations
- Keep dependencies minimal
- Ensure all new features align with agent-centric design principles

## Agent Framework Integration Notes

As of v0.6.0, all data functions are optimized for AI agent frameworks:
- **Google ADK**: Direct function imports work without "signature too complex" errors
- **LangChain**: Functions can be wrapped with StructuredTool seamlessly
- **Custom Agents**: Simple type signatures ensure broad compatibility
- **Example**: `read_csv_simple(file_path: str) -> list` instead of complex Union types