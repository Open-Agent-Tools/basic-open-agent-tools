# Test Coverage TODO

This document outlines gaps in test coverage and areas that need additional testing in the basic-open-agent-tools project.

## Current Test Coverage Status (v0.6.1)

### ✅ Well-Tested Modules
- **Data Module**: 80%+ coverage with comprehensive tests for all simplified functions
- **File System Module**: Good coverage for core operations
- **Text Module**: Comprehensive test coverage
- **Helper Functions**: Tests for all tool loading functions including read-only helpers

### ✅ Recent Test Updates (v0.6.0-0.6.1)
- [x] Updated all data module tests for simplified function signatures
- [x] Fixed import references for `*_simple` function variants
- [x] Updated helper function tests for new function counts
- [x] Maintained test coverage during agent compatibility refactoring

## Missing Test Files

The following modules or files don't have dedicated test files:

- [ ] **exceptions.py**: Create tests for custom exception classes and their behavior
- [ ] **types.py**: Create tests for type definitions and any helper functions

## Modules with Limited Test Coverage

### File System Module

The current `test_file_system_tools.py` provides only basic coverage. Additional tests needed for:

- [ ] **info.py**: Comprehensive tests for all file information functions
- [ ] **operations.py**: Tests for all file operations beyond basic read/write
- [ ] **tree.py**: More extensive tests for directory tree functionality
- [ ] **validation.py**: Tests for path validation functions

### Data Module

While the data module has good test coverage with dedicated test files for each submodule, consider:

- [ ] **Edge cases**: Add more tests for edge cases and error handling
- [ ] **Integration tests**: Add tests that combine multiple data module functions
- [ ] **Performance tests**: Add tests for performance-critical operations

## Future Modules

As new modules are implemented (from their respective TODO.md files), tests should be created:

- [ ] **crypto module**: Create tests when implementation is added
- [ ] **network module**: Create tests when implementation is added
- [ ] **system module**: Create tests when implementation is added
- [ ] **utilities module**: Create tests when implementation is added

## Test Infrastructure Improvements

Consider the following improvements to the testing infrastructure:

- [x] **Test coverage reporting**: pytest-cov configured for HTML, XML, and terminal reporting
- [ ] **Property-based testing**: Consider adding property-based tests for data transformation functions
- [ ] **Parameterized tests**: Use parameterized tests for functions with multiple similar test cases
- [ ] **Agent Integration Tests**: Add tests specifically for agent framework integration scenarios
- [ ] **Performance Tests**: Add benchmarks for simplified vs complex function variants

## Agent Compatibility Testing

New testing priorities based on v0.6.0 agent compatibility improvements:

- [ ] **Function Signature Tests**: Verify all functions use only basic Python types
- [ ] **Import Tests**: Test individual function imports for agent framework scenarios
- [ ] **Type Annotation Tests**: Ensure no complex Union types or custom aliases remain
- [ ] **Helper Function Tests**: Verify all helper functions return correctly typed tool lists