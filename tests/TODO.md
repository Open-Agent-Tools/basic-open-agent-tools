# Testing TODO - Basic Open Agent Tools

This document outlines the prioritized testing roadmap for the remaining modules in basic-open-agent-tools that need comprehensive test coverage.

## 📊 Current Status Overview

| Module | Functions | Current Coverage | Test Status | Priority |
|--------|-----------|------------------|-------------|----------|
| **file_system** | 20 | 87-100% | ✅ **COMPLETE** | - |
| **data** | 23 | 4-14% | ❌ **MISSING** | 🔴 **P1** |
| **text** | 10 | 9% | ❌ **MISSING** | 🔴 **P2** |
| **helpers** | 10 | 10% | ❌ **MISSING** | 🟡 **P3** |
| **exceptions** | 5 | 100%* | ❌ **MISSING** | 🟢 **P4** |
| **types** | 3 | 100%* | ❌ **MISSING** | 🟢 **P5** |

*Simple classes/definitions with inherent coverage

## 🎯 Priority 1: Data Module (CRITICAL)

**Status**: 🔴 **No tests exist** - 23 functions with 4-14% coverage  
**Complexity**: **High** - Complex business logic, file I/O, validation, serialization  
**Estimated Work**: 150-200 test cases needed

### Submodules to Test:

#### 1.1 `config_processing.py` (8 functions) - **Start Here**
- **Functions**: `read_yaml_file`, `write_yaml_file`, `read_toml_file`, `write_toml_file`, `read_ini_file`, `write_ini_file`, `validate_config_schema`, `merge_config_files`
- **Priority**: Highest - Complex file format handling
- **Test Requirements**:
  - File I/O operations with error handling
  - Multiple config format support (YAML, TOML, INI)
  - Schema validation logic
  - File merging algorithms
- **Estimated Tests**: 50-60 test cases

#### 1.2 `csv_tools.py` (7 functions)
- **Functions**: `read_csv_simple`, `write_csv_simple`, `csv_to_dict_list`, `dict_list_to_csv`, `detect_csv_delimiter`, `validate_csv_structure`, `clean_csv_data`
- **Test Requirements**:
  - CSV parsing with various delimiters
  - Data transformation logic
  - Error handling for malformed CSV
  - Large file processing
- **Estimated Tests**: 45-55 test cases

#### 1.3 `validation.py` (5 functions)
- **Functions**: `validate_schema_simple`, `check_required_fields`, `validate_data_types_simple`, `validate_range_simple`, `create_validation_report`
- **Test Requirements**:
  - Schema validation logic
  - Type checking algorithms
  - Range validation edge cases
  - Report generation
- **Estimated Tests**: 35-45 test cases

#### 1.4 `json_tools.py` (3 functions)
- **Functions**: `safe_json_serialize`, `safe_json_deserialize`, `validate_json_string`
- **Test Requirements**:
  - JSON serialization edge cases
  - Error handling for invalid JSON
  - Unicode and special character handling
- **Estimated Tests**: 25-35 test cases

### Implementation Order:
1. `config_processing.py` (highest complexity)
2. `csv_tools.py` (medium-high complexity)
3. `validation.py` (medium complexity)
4. `json_tools.py` (lower complexity)

---

## 🎯 Priority 2: Text Module (HIGH)

**Status**: 🔴 **No tests exist** - 10 functions with 9% coverage  
**Complexity**: **Medium-High** - String processing, regex, Unicode handling  
**Estimated Work**: 80-100 test cases needed

### Functions to Test:

#### 2.1 `text/processing.py` (10 functions)
- **Functions**: `clean_whitespace`, `normalize_line_endings`, `strip_html_tags`, `normalize_unicode`, `to_snake_case`, `to_camel_case`, `to_title_case`, `smart_split_lines`, `extract_sentences`, `join_with_oxford_comma`
- **Test Requirements**:
  - String transformation algorithms
  - Regular expression edge cases
  - Unicode normalization
  - HTML parsing and sanitization
  - Text formatting and case conversion
- **Estimated Tests**: 80-100 test cases

### Implementation Order:
1. String normalization and cleaning functions (4 functions)
2. Case conversion and formatting functions (4 functions)  
3. Text parsing and extraction functions (2 functions)

---

## 🎯 Priority 3: Helpers Module (MEDIUM)

**Status**: 🔴 **No tests exist** - 10 functions with 10% coverage  
**Complexity**: **Medium** - Tool management, dynamic loading, integration  
**Estimated Work**: 60-80 test cases needed

### Functions to Test:

#### 3.1 `helpers.py` (10 functions)
- **Functions**: `load_all_filesystem_tools`, `load_all_text_tools`, `load_all_data_tools`, `load_data_json_tools`, `load_data_csv_tools`, `load_data_validation_tools`, `load_data_config_tools`, `merge_tool_lists`, `get_tool_info`, `list_all_available_tools`
- **Test Requirements**:
  - Dynamic function loading and introspection
  - Tool list management and merging
  - Integration testing with actual modules
  - Error handling for missing modules
- **Estimated Tests**: 60-80 test cases

### Implementation Order:
1. Tool loading functions (7 functions)
2. Tool management and utility functions (3 functions)

---

## 🎯 Priority 4: Exceptions Module (LOW)

**Status**: 🔴 **No tests exist** - 5 exception classes with simple structure  
**Complexity**: **Low** - Exception class definitions and hierarchy  
**Estimated Work**: 20-30 test cases needed

### Classes to Test:

#### 4.1 `exceptions.py` (5 exception classes)
- **Classes**: `BasicAgentToolsError`, `FileSystemError`, `DataError`, `ValidationError`, `SerializationError`
- **Test Requirements**:
  - Exception instantiation and inheritance
  - Error message formatting
  - Exception chaining and context
- **Estimated Tests**: 20-30 test cases

---

## 🎯 Priority 5: Types Module (LOW)

**Status**: 🔴 **No tests exist** - 3 type definitions with minimal logic  
**Complexity**: **Low** - Type aliases and simple definitions  
**Estimated Work**: 10-15 test cases needed

### Types to Test:

#### 5.1 `types.py` (3 type definitions)
- **Types**: `PathLike`, `DataDict`, `ConfigDict` and related aliases
- **Test Requirements**:
  - Type validation and compatibility
  - Import and usage verification
- **Estimated Tests**: 10-15 test cases

---

## 📋 Implementation Guidelines

### Testing Standards
- **Coverage Target**: 70% minimum, 90%+ preferred (matching file_system module)
- **Quality Requirements**: 100% ruff compliance, full mypy type checking
- **Testing Strategy**: Dual approach (traditional unit tests + Google ADK agent evaluation)

### Required Files per Module
Following the established pattern from file_system module:

```
tests/{module}/
├── test_{module}.py                    # Traditional unit tests
├── test_{module}_agent/               # Agent evaluation tests
│   ├── __init__.py                    # Agent test package
│   ├── agent/                         # Agent implementation
│   │   ├── __init__.py               # Agent module exports
│   │   └── sample_agent.py           # Agent with tools
│   ├── test_config.json              # ADK evaluation criteria
│   ├── test_{module}_agent_evaluation.py  # Agent test runner
│   ├── {function}.test.json          # Individual tool tests (1 per function)
│   └── {module}_comprehensive.test.json   # Multi-tool workflow tests
```

### Quality Assurance Commands
Run before each module completion:
```bash
python3 -m ruff check tests/{module}/ --fix
python3 -m ruff format tests/{module}/
python3 -m mypy tests/{module}/ --ignore-missing-imports
python3 -m pytest tests/{module}/ --cov=src/basic_open_agent_tools/{module} --cov-report=term
```

## 🎯 Success Criteria

### Module Completion Requirements
1. ✅ **70%+ test coverage** for each module
2. ✅ **100% ruff compliance** across all test files
3. ✅ **Full mypy type checking** compatibility
4. ✅ **Dual testing strategy** implemented (traditional + agent evaluation)
5. ✅ **Google ADK compliance** for all agent tools
6. ✅ **Documentation updates** in tests/README.md

### Project Completion Goal
- **All 6 main modules** with comprehensive test coverage
- **300+ total test cases** across the entire toolkit
- **Production-ready toolkit** for both developers and AI agents
- **Reusable testing framework** for future module development

---

## 📝 Notes

- **Start with Data Module**: Highest impact, lowest current coverage
- **Follow Established Patterns**: Use file_system module tests as templates
- **Focus on Error Handling**: Critical for Google ADK compliance
- **Natural Language Agent Tests**: Human-like requests, not explicit function calls
- **Incremental Progress**: Complete one submodule before starting the next

This roadmap ensures systematic, high-quality test coverage for the entire basic-open-agent-tools project while maintaining consistency with established patterns and standards.