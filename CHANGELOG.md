# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Smart Confirmation System**: 3-mode hybrid confirmation for write/delete operations
  - **Bypass Mode**: `skip_confirm=True` or `BYPASS_TOOL_CONSENT=true` environment variable proceeds immediately
  - **Interactive Mode**: TTY-enabled terminals with `skip_confirm=False` prompt user with `y/n` confirmation
  - **Agent Mode**: Non-TTY environments with `skip_confirm=False` raise `CONFIRMATION_REQUIRED` error with instructions
- **New Module**: `confirmation.py` - Centralized confirmation handling with context-aware behavior
- **Environment Variable**: `BYPASS_TOOL_CONSENT` for CI/CD and automation workflows

### Changed
- **Confirmation Behavior**: All functions with `skip_confirm` now use intelligent 3-mode confirmation system
  - File operations: `write_file_from_string`, `create_directory`, `delete_file`, `delete_directory`, `move_file`, `copy_file`, `file_editor`
  - Data operations: `write_csv_simple`, `write_ini_file`, `write_yaml_file`, `write_toml_file`
  - Archive operations: `create_zip`, `extract_zip`, `compress_files`, `create_tar`, `compress_file_gzip`, `compress_file_bzip2`, `compress_file_xz`
  - TODO operations: `delete_task`
- **User Experience**: Interactive terminal users get confirmation prompts instead of errors
- **Agent Integration**: LLM agents receive instructive error messages to guide user permission workflow
- **Documentation**: Enhanced README, getting-started.md, api-reference.md, faq.md, and CLAUDE.md with confirmation system details

### Fixed
- **Agent UX**: Resolved issue where agents couldn't provide user feedback loop for confirmations
- **Type Safety**: Added explicit type casts for mypy compliance in file_system/editor.py

## [0.13.1] - 2025-10-14

### Removed
- **Code Analysis Module** - Migrated to [coding-open-agent-tools](https://github.com/open-agent-tools/coding-open-agent-tools) (15 functions)
- **Git Tools Module** - Migrated to coding-open-agent-tools (9 functions)
- **Profiling Module** - Migrated to coding-open-agent-tools (8 functions)
- **Static Analysis Module** - Migrated to coding-open-agent-tools (7 functions)

### Changed
- **Function Count**: Reduced from 190+ to 151 functions (focused on foundational tools)
- **Module Count**: Reduced from 15 to 11 modules (removed coding-specific modules)
- **Package Scope**: Refocused on foundational, non-coding-specific agent tools

### Migration Guide
The removed modules are now available in the **coding-open-agent-tools** package:
```bash
pip install coding-open-agent-tools
```

These modules were development/coding-specific and better suited for a specialized package. Users who need these capabilities should install coding-open-agent-tools alongside this package.

## [0.13.0] - 2025-10-14

### Note
**This version contained modules that were not properly exported in the package API.** Version 0.13.1 removes these modules as they have been migrated to coding-open-agent-tools.

### Added (Not Actually Available)
- Code Analysis Module (15 functions) - **Migrated to coding-open-agent-tools in v0.13.1**
- Profiling Module (8 functions) - **Migrated to coding-open-agent-tools in v0.13.1**
- Static Analysis Module (7 functions) - **Migrated to coding-open-agent-tools in v0.13.1**
- Git Tools Module (9 functions) - **Migrated to coding-open-agent-tools in v0.13.1**

### Added
- **Code Analysis Module** (15 functions): AST parsing, complexity analysis, import management, secret detection
  - `parse_python_ast`, `extract_functions`, `extract_classes`, `extract_imports`
  - `calculate_complexity`, `calculate_function_complexity`, `get_code_metrics`, `identify_complex_functions`
  - `find_unused_imports`, `organize_imports`, `validate_import_order`
  - `scan_for_secrets`, `scan_directory_for_secrets`, `validate_secret_patterns`
- **Profiling Module** (8 functions): Performance and memory profiling, benchmarking
  - `profile_function`, `profile_script`, `get_hotspots`
  - `measure_memory_usage`, `detect_memory_leaks`, `get_memory_snapshot`
  - `benchmark_execution`, `compare_implementations`
- **Static Analysis Module** (7 functions): Tool output parsing and issue analysis
  - `parse_ruff_json`, `parse_mypy_json`, `parse_pytest_json`, `summarize_static_analysis`
  - `filter_issues_by_severity`, `group_issues_by_file`, `prioritize_issues`
- **Git Tools Module** (9 functions): Read-only git repository operations
  - `get_git_status`, `get_current_branch`, `get_git_diff`
  - `get_git_log`, `get_git_blame`, `get_file_history`, `get_file_at_commit`
  - `list_branches`, `get_branch_info`

### Changed
- **Test Coverage**: Improved to 87% average across new modules (148 new tests)
- **Function Count**: Increased from 150+ to 190+ total agent tools
- **Module Count**: Expanded from 11 to 15 modules

### Fixed
- **Test Compatibility**: Updated archive compression tests for new skip_confirm parameter behavior
- **Type Validation**: Fixed encoding functions to validate types before logging operations

## [0.11.1] - 2024-09-26

### Added
- **Enhanced User Feedback Loops**: All file and data manipulation tools now provide detailed feedback messages
- **Permission System**: Added `force` parameter to prevent accidental overwrites across all write operations
- **Detailed Operation Reports**: Functions now return descriptive strings instead of simple boolean values
- **Consistent Response Patterns**: Unified feedback approach across all modules following the file_editor pattern

### Enhanced Functions
- **File System**: `write_file_from_string`, `copy_file`, `delete_file`, `move_file` now include detailed feedback
- **Data Tools**: `write_csv_simple`, `write_yaml_to_file`, `write_toml_to_file`, `write_ini_to_file` with operation summaries
- **Archive Tools**: `create_tar_archive`, `create_zip_archive` with compression statistics
- **Todo Tools**: `write_todo_to_file` with protection mechanisms and clear confirmations

### Changed
- **Agent Framework Compatibility**: All functions maintain Google ADK compliance while providing richer feedback
- **Function Signatures**: Added required `force` parameter to destructive operations for safety
- **Return Values**: Enhanced from boolean/None returns to detailed string descriptions for better agent understanding

### Fixed
- **Package Build Process**: Ensured all enhancements are properly included in published packages
- **Test Agent Compatibility**: Updated test agents to handle new function signatures
- **Import Errors**: Resolved import issues in evaluation tests

## [0.9.1] - 2024-09-14

### Added
- **Strands Agents Integration**: Native `@strands_tool` decorator support across all modules
- **Enhanced Documentation**: Comprehensive README files for all 12 modules
- **Web-Ready Links**: GitHub Pages compatible documentation links
- **Quality Improvements**: Comprehensive code cleanup and linting fixes

### Changed
- **Python Version Requirement**: Updated minimum Python version from 3.8 to 3.9
- **Type Signatures**: Improved type hints consistency across all modules
- **Documentation Structure**: Updated all module READMEs with comprehensive examples

### Fixed
- **Type Checking**: Resolved all mypy type checking issues
- **Code Quality**: Fixed all ruff linting issues
- **Test Coverage**: Enhanced test coverage across new modules

## [0.9.0] - 2024-07-08

### Added
- **6 New Modules**: Major toolkit expansion with comprehensive new functionality
  - **Archive Tools** (9 functions): ZIP, TAR, GZIP, BZIP2, XZ compression and extraction
  - **Crypto Tools** (14 functions): Hashing, encoding, UUID generation (non-security critical)
  - **Logging Tools** (5 functions): Structured logging and log rotation
  - **Monitoring Tools** (8 functions): File watching, health checks, performance profiling
  - **PDF Tools** (8 functions): PDF reading, creation, manipulation, watermarking
  - **System Tools** (19 functions): Cross-platform shell, process management, system info
- **Network Tools** (4 functions): HTTP client, DNS resolution, port checking
- **Utilities Tools** (8 functions): Timing controls, debugging utilities
- **Dependency Groups**: Optional dependency management with `[system]`, `[pdf]`, `[all]` groups
- **166 Total Functions**: Complete toolkit with comprehensive local operations

### Changed
- **Module Organization**: Restructured from 4 modules to 12 specialized modules
- **Agent Framework Support**: Enhanced compatibility with Google ADK, LangChain, Strands
- **Function Signatures**: Agent-friendly type signatures across all new modules
- **Error Handling**: Consistent error handling patterns across all modules

### Performance
- **Optimized Dependencies**: Optional dependencies reduce installation size
- **Improved Loading**: Modular tool loading with category-specific helpers
- **Memory Efficiency**: Optimized memory usage in file and system operations

## [0.8.2] - 2024-06-27

### Added
- **DateTime Module** (40 functions): Comprehensive date and time operations
  - Current date/time operations with timezone support
  - Date arithmetic and range generation
  - Business day calculations and validation
  - Format conversion and validation tools
  - Quarter and period calculations
- **Enhanced Testing**: Comprehensive test coverage for datetime operations
- **Documentation**: Complete datetime module documentation

### Changed
- **Function Count**: Expanded from ~70 to 110+ total functions
- **Module Structure**: Enhanced datetime module with 6 sub-modules
- **Type Safety**: Improved type annotations for datetime operations

### Fixed
- **Timezone Handling**: Robust timezone-aware datetime operations
- **Date Validation**: Enhanced date format validation and error handling

## [0.8.1] - 2024-06-15

### Added
- **Agent-Friendly Design**: Function signatures optimized for AI agent frameworks
- **Google ADK Compatibility**: Full compatibility with Google Agent Development Kit
- **Helper Functions**: Tool loading utilities (`load_all_tools()`, `merge_tool_lists()`)
- **Comprehensive Testing**: 74% test coverage with extensive test suite

### Changed
- **Type Signatures**: Simplified types to prevent "signature too complex" errors
- **Function Names**: Standardized naming conventions across all modules
- **Error Handling**: Consistent exception patterns with `BasicAgentToolsError`

### Fixed
- **Import Issues**: Resolved circular import problems
- **Type Checking**: Fixed mypy compatibility issues
- **Agent Integration**: Smooth integration with major agent frameworks

## [0.8.0] - 2024-05-20

### Added
- **Data Processing Module** (23 functions): JSON, CSV, YAML, TOML, INI processing
  - Safe JSON serialization and validation
  - CSV reading, writing, and cleaning operations
  - Configuration file processing (YAML, TOML, INI)
  - Data validation and schema checking tools
- **Enhanced File System**: Additional file operations and path validation
- **Text Processing**: Expanded text manipulation capabilities

### Changed
- **Module Architecture**: Cleaner separation between data types
- **Function Organization**: Logical grouping of related functions
- **Documentation**: Improved docstrings for LLM understanding

### Security
- **Input Validation**: Enhanced input sanitization across all modules
- **Path Safety**: Improved path traversal protection
- **Error Messages**: Safe error reporting without information disclosure

## [0.7.x] - 2024-04-15

### Added
- **Core Modules**: Initial implementation of file_system and text modules
- **Basic Operations**: File CRUD operations and text processing utilities
- **Foundation**: Base architecture for agent tool integration

### Changed
- **Initial Structure**: Established module organization patterns
- **Function Design**: Basic agent-compatible function signatures

## [Pre-0.7.0] - Legacy Versions

### Note
Legacy versions (< 0.7.0) are no longer supported. Please upgrade to the latest version for security updates and new features.

---

## Migration Guides

### Upgrading to 0.9.x from 0.8.x

**Breaking Changes:**
- **Python 3.9+ Required**: Update your Python version if using 3.8
- **New Modules**: 6 new modules with optional dependencies
- **Function Locations**: Some utility functions moved to dedicated modules

**Migration Steps:**
1. Update Python to 3.9+
2. Install with optional dependencies: `pip install basic-open-agent-tools[all]`
3. Update imports for moved functions (see module READMEs)
4. Test agent integrations with new module structure

### Upgrading to 0.8.x from 0.7.x

**Breaking Changes:**
- **Helper Functions**: New tool loading patterns
- **Function Names**: Some functions renamed for consistency
- **Type Signatures**: Enhanced type annotations

**Migration Steps:**
1. Replace direct imports with helper functions
2. Update function names (see individual module READMEs)
3. Update type annotations in your code

---

## Development

### Contributing
See [CONTRIBUTING.md](docs/contributing.md) for development setup and guidelines.

### Releases
- **Major versions** (x.0.0): Significant new features or breaking changes
- **Minor versions** (0.x.0): New features, modules, or substantial enhancements
- **Patch versions** (0.0.x): Bug fixes, documentation updates, minor improvements

### Support Policy
- **Current version (0.9.x)**: Full support with new features and bug fixes
- **Previous version (0.8.x)**: Security updates and critical bug fixes
- **Legacy versions (< 0.8.x)**: No longer supported

For security vulnerabilities, see [SECURITY.md](SECURITY.md).