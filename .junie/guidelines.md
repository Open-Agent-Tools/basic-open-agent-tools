# Project Guidelines for Junie

## Project Overview and Intent

basic-open-agent-tools is a toolkit providing essential functions for AI agent frameworks. It offers core utilities that developers can integrate into their agents to avoid boilerplate code, designed to be simpler than solutions requiring MCP or A2A protocols.

## Project Structure

The project is organized into these categories:

- `file_system` - File and directory operations (implemented)
- `text` - Text processing and manipulation (implemented)
- `data` - Data parsing and conversion (implemented)
- `network` - Network utilities and validation (planned)
- `system` - System information and processes (planned)
- `crypto` - Cryptographic utilities (planned)
- `utilities` - Common helpers and utilities (planned)

## Development Environment

This Python project supports multiple package managers:
- pip/setuptools (standard)
- Poetry (poetry.lock)
- UV (uv.lock)
- PDM (pdm.lock)
- Pipenv (Pipfile.lock)

## Design Principles and Coding Standards

This project follows these key principles:

- **Function-First Design**: Each function works as a standalone agent tool with clear signatures
- **Type Safety**: Full type annotations for all functions
- **Comprehensive Docstrings**: Help AI understand function purpose and usage
- **Stateless Operations**: Thread-safe and concurrent-friendly
- **Consistent Error Handling**: Predictable exception patterns
- **Minimal Dependencies**: Prefer Python standard library where possible

When making changes, ensure:
- **PEP 8** style guidelines are followed
- **Agent-friendly names** are used (descriptive function and variable names)
- **Individual function exports** are maintained (functions can be imported individually)

## Code Quality Requirements

Before submitting changes, run:

```bash
# Format and lint code
ruff format
ruff check

# Type checking
mypy src/basic_open_agent_tools
```

## Testing Requirements

Junie should verify solutions with tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/basic_open_agent_tools
```

The project has a minimum 70% coverage target for new modules.

## Building the Project

If needed, build the project using:

```bash
# Build distribution packages
python -m build

# Install locally for testing
pip install -e .
```

## Integration and Usage

### Agent Framework Integration

This toolkit integrates seamlessly with:
- **Google ADK**: Direct function imports in tools list
- **LangChain**: Functions wrapped with StructuredTool
- **Custom Agents**: Direct function integration
- **MCP Servers**: Adaptable for Model Context Protocol

### Helper Functions Usage

Always use the top-level helper functions:

```python
import basic_open_agent_tools as boat

# Load tools by category
fs_tools = boat.load_all_filesystem_tools()    # 18 functions
text_tools = boat.load_all_text_tools()        # 10 functions
data_tools = boat.load_all_data_tools()        # 28 functions

# Load specific data tool categories
json_tools = boat.load_data_json_tools()       # 5 functions
csv_tools = boat.load_data_csv_tools()         # 7 functions

# Merge for agent use (automatically deduplicates)
agent_tools = boat.merge_tool_lists(fs_tools, text_tools, data_tools)
```

## Security Guidelines

**IMPORTANT**: This toolkit is for defensive security tasks only:
- ✅ **Allow**: Security analysis, detection rules, vulnerability explanations
- ✅ **Allow**: Defensive tools, security documentation
- ❌ **Refuse**: Creating, modifying, or improving code for malicious use

## Development Patterns

When adding new modules, follow this pattern:
1. Create module directory with `__init__.py`
2. Implement functions in logical submodules
3. Export all functions in module `__all__`
4. Add comprehensive tests with 70%+ coverage
5. Update helper functions to include new module
6. Add module to main package `__init__.py`
