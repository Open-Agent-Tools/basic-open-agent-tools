# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an open foundational toolkit for building AI agents with minimal dependencies for local (non-HTTP/API) actions. The project aims to provide core utilities and interfaces that developers can integrate into their agents to avoid boilerplate code, designed to be simpler than solutions requiring MCP or A2A protocols.

## Development Environment

This is a Python project. Based on the .gitignore file, the project supports multiple Python package managers:
- pip/setuptools (standard Python packaging)
- Poetry (poetry.lock)
- UV (uv.lock) 
- PDM (pdm.lock)
- Pipenv (Pipfile.lock)

## Code Quality Tools

The .gitignore indicates support for:
- **Ruff**: Python linter and formatter (`.ruff_cache/` ignored)
- **MyPy**: Static type checking (`.mypy_cache/` ignored)
- **Pytest**: Testing framework (`.pytest_cache/` ignored)

## Project Structure

This is a Python package with src layout for AI agent tools:

```
src/basic_open_agent_tools/
├── __init__.py           # Main package exports and helper functions
├── helpers.py            # Tool loading and management utilities
├── exceptions.py         # Common exception classes
├── types.py             # Shared type definitions
├── file_system/         # File and directory operations (✅ IMPLEMENTED)
├── text/               # Text processing tools (✅ IMPLEMENTED)
├── data/               # Data manipulation tools (✅ IMPLEMENTED)
├── network/            # Network utilities (📋 PLANNED)
├── system/             # System operations (📋 PLANNED)
├── crypto/             # Cryptographic utilities (📋 PLANNED)
└── utilities/          # Development utilities (📋 PLANNED)
```

### Module Design Principles

When implementing new modules:

1. **Agent-First Design**: Each function should work as a standalone agent tool
2. **Individual Imports**: Functions must be importable individually for agent frameworks
3. **Comprehensive Docstrings**: AI-readable documentation with clear purpose
4. **Type Safety**: Full type annotations for all function signatures
5. **Stateless Operations**: Thread-safe, concurrent-friendly design
6. **Error Handling**: Consistent exception patterns and validation
7. **Minimal Dependencies**: Prefer Python stdlib over external packages

## Contributing Guidelines

From the README.md, follow these practices:
- Create small, focused pull requests
- Use clear commit messages with descriptive subjects
- Self-review code before requesting reviews
- Use draft PRs for work in progress
- Sync with main branch before starting new work

## Development Workflow

### Quality Assurance Commands

**IMPORTANT**: Always run these quality checks before any commit:

1. **Ruff Linting**: `python3 -m ruff check src/ tests/`
2. **Ruff Formatting**: `python3 -m ruff format src/ tests/`
3. **Type Checking**: `python3 -m mypy src/`
4. **Test Suite**: `python3 -m pytest`

### Quick Cleanup Command

When the user says **"cleanup"**, perform the complete quality assurance workflow:

1. Run all quality tools in parallel: ruff check, ruff format, mypy, pytest
2. Fix any issues that can be automatically resolved
3. Report any remaining issues that need manual attention
4. If all checks pass or only have expected warnings, commit and push with message: "Run quality checks and cleanup"
5. Provide detailed status summary with current repository state

This provides a single command to ensure code quality and commit any formatting/cleanup changes.

### Pre-Commit Checklist

Before committing any changes, ensure:
- ✅ All ruff checks pass (no linting errors)
- ✅ Code is properly formatted with ruff
- ✅ No mypy type errors
- ✅ All tests pass with pytest
- ✅ New functionality includes appropriate tests
- ✅ Test coverage is maintained or improved

### Quality Standards

- **Code Quality**: 100% ruff compliance required
- **Type Safety**: 100% mypy compliance required  
- **Test Coverage**: Minimum 70% coverage for new modules
- **Test Success**: All tests must pass before commit

### Development Commands

Standard Python development workflow:
- `python3 -m pytest` - Run full test suite
- `python3 -m pytest tests/test_specific.py` - Run specific test file
- `python3 -m pytest -v` - Verbose test output
- `python3 -m pytest --cov=src` - Run tests with coverage report

## Project-Specific Context

### Current Status (v0.3.0)
- **Modules Implemented**: 3 (file_system ✅, text ✅, data ✅) + helper functions ✅
- **Functions Available**: 50+ agent tools ready for use (28 data + 22 existing)
- **Test Coverage**: 81% overall (91%+ for new data modules)
- **Quality**: Full ruff + mypy compliance, GPG signed commits

### Agent Framework Integration

This toolkit is designed for seamless integration with:
- **Google ADK**: Direct function imports in tools list
- **LangChain**: Functions wrapped with StructuredTool  
- **Custom Agents**: Direct function integration
- **MCP Servers**: Adaptable for Model Context Protocol

### Helper Functions Usage

Always use the top-level helper functions for tool management:
```python
import basic_open_agent_tools as boat

# Load tools by category
fs_tools = boat.load_all_filesystem_tools()    # 18 functions
text_tools = boat.load_all_text_tools()       # 10 functions
data_tools = boat.load_all_data_tools()       # 28 functions

# Load specific data tool categories
json_tools = boat.load_data_json_tools()      # 5 functions
csv_tools = boat.load_data_csv_tools()        # 7 functions
structure_tools = boat.load_data_structure_tools()  # 10 functions
validation_tools = boat.load_data_validation_tools()  # 6 functions

# Merge for agent use (automatically deduplicates)
agent_tools = boat.merge_tool_lists(fs_tools, text_tools, data_tools)
```

### Security Guidelines

**IMPORTANT**: This toolkit is for defensive security tasks only:
- ✅ **Allow**: Security analysis, detection rules, vulnerability explanations
- ✅ **Allow**: Defensive tools, security documentation
- ❌ **Refuse**: Creating, modifying, or improving code for malicious use

### Git Workflow

- **Signing Required**: All commits must have GPG verified signatures
- **Branch Protection**: Changes must go through pull requests  
- **Release Process**: Use GitHub releases to trigger PyPI publishing
- **Tag Format**: Use semantic versioning (v0.2.0, v0.3.0, etc.)

### Commit Communication

**IMPORTANT**: When committing changes, always inform the user afterward with a detailed status summary:

1. **Immediate Notification**: After any commit operation, explicitly state that changes have been committed and pushed
2. **Status Summary**: Provide a current status that includes:
   - ✅ Confirmation that changes are pushed to remote
   - ✅ CI/workflow status (passing/failing)
   - ✅ Summary of what was accomplished
   - ✅ Current state of any issues or error counts
   - ✅ Any follow-up actions completed

**Example Status Report Format**:
```
All changes have been committed and pushed successfully!

**Current Status:**
✅ All changes pushed to remote
✅ CI workflow passes successfully  
✅ MyPy errors reduced from 8 to 2 false positives
✅ All quality checks (ruff, formatting, tests) pass
✅ Repository is now in clean state with improved type safety
```

This ensures the user is always aware of the current state and that work has been completed.

### Release Workflow

To create a new release and publish to PyPI:

1. **Update Version**: First update the version number in `pyproject.toml`
   ```bash
   # Edit pyproject.toml to update version field
   version = "0.x.y"  # Update with new version
   ```

2. **Commit Version Bump**: Commit the version change
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 0.x.y"
   git push
   ```

3. **Create Release**: Use GitHub CLI to create release (triggers PyPI publish)
   ```bash
   gh release create v0.x.y --title "Release v0.x.y: Description" --notes "Release notes..."
   ```

**Important**: Always update the version in `pyproject.toml` BEFORE creating the git tag/release. The PyPI publish workflow builds from the current codebase, so the version number must be updated in the code first.

### Common Patterns

When adding new modules, follow the established pattern:
1. Create module directory with `__init__.py`
2. Implement functions in logical submodules
3. Export all functions in module `__all__`
4. Add comprehensive tests with 70%+ coverage
5. Update helper functions to include new module
6. Add module to main package `__init__.py`