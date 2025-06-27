# Contributing

Thank you for your interest in contributing to basic-open-agent-tools! This toolkit provides essential functions for AI agent frameworks, and this guide will help you get started with development.

## 🚀 **Quick Reference: Google AI Compatibility**

**✅ REQUIRED for all functions:**
- Use `List[Dict[str, str]]` instead of `list`
- No default parameters: `param: int = 0` ❌
- No Union types: `Union[str, int]` ❌
- JSON-serializable types only: `str`, `int`, `float`, `bool`, `dict`
- Comprehensive docstrings for LLM understanding

**🔍 Quick validation:**
```bash
rg "^def [a-zA-Z_][a-zA-Z0-9_]*\([^)]*: list[^\[]" src/ --type py  # Check untyped lists
rg "^def [a-zA-Z_][a-zA-Z0-9_]*\([^)]*=" src/ --type py            # Check defaults
```

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- pip or uv (recommended)

### Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Open-Agent-Tools/basic-open-agent-tools.git
   cd basic-open-agent-tools
   ```

2. **Create a virtual environment:**
   ```bash
   # Using venv
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Or using uv (recommended)
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   # Using pip
   pip install -e ".[dev]"

   # Or using uv
   uv pip install -e ".[dev]"
   ```


## 🏗️ Agent Toolkit Design Philosophy

This project is specifically designed to provide **tool functions for AI agents**. 

### Key Design Principles

- **Function-First Design:** Each function works as a standalone agent tool with clear signatures optimized for AI interpretation
- **Comprehensive Docstrings:** Help AI understand function purpose and usage
- **Stateless Operations:** Thread-safe and concurrent-friendly
- **Consistent Error Handling:** Predictable exception patterns
- **Type Safety:** Full type annotations for all functions
- **Minimal Dependencies:** Prefer Python standard library where possible

### Agent Framework Integration

The toolkit is designed to work with various agent frameworks:
- **Google ADK:** Direct function imports in tools list
- **LangChain:** Functions wrapped with StructuredTool
- **Custom Agents:** Direct function integration
- **MCP Servers:** Adaptable for Model Context Protocol

### Quality Standards

- **Testing:** Minimum 70% coverage target for new modules
- **Documentation:** Complete API reference and examples
- **Type Safety:** 100% mypy compliance
- **Code Quality:** All ruff checks passing
- **Agent Compatibility:** 100% Google AI Function Tool compliance

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/basic_open_agent_tools

# Run specific test file
pytest tests/test_file_system_tools.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code with ruff
ruff format

# Lint code
ruff check

# Fix auto-fixable issues
ruff check --fix

# Type checking with mypy
mypy src/basic_open_agent_tools
```

### Building the Package

```bash
# Build distribution packages
python -m build

# Install locally for testing
pip install -e .
```

## Contributing Guidelines

### Code Style for Agent Tools

- **Follow PEP 8** style guidelines
- **Type hints throughout** - Use type hints for all function parameters and return values
- **Comprehensive docstrings** - Help AI understand function purpose and usage
- **Clear, focused purpose** - Each function does one thing well (optimal for agent tools)
- **Agent-friendly names** - Descriptive function and variable names that AI can understand
- **Clear function signatures** - Design function signatures to be clear for AI interpretation
- **Stateless design** - Functions don't rely on external state
- **Thread-safe operations** - Safe for concurrent agent usage
- **Individual function exports** - Functions can be imported individually
- **Appropriate error handling** - Consistent exception patterns

### 🚨 **CRITICAL: Google AI Function Tool Requirements**

**ALL functions MUST follow these requirements for Google AI compatibility:**

#### ✅ **Required Function Signature Format**
```python
def process_data(data: List[Dict[str, str]], operation: str) -> dict:
    """Process data with specified operation.
    
    Detailed explanation for LLM understanding.
    
    Args:
        data: List of dictionaries to process
        operation: Type of operation to perform
        
    Returns:
        Dictionary with processing results
        
    Raises:
        ValueError: If operation is not supported
        TypeError: If data is not properly formatted
    """
    if not isinstance(data, list):
        raise TypeError("data must be a list")
    
    if operation not in ["clean", "validate", "transform"]:
        raise ValueError(f"Unsupported operation: {operation}")
    
    # Function implementation
    return {"status": "success", "processed_count": len(data)}
```

#### 📝 **Google AI Requirements**
1. **JSON-Serializable Types Only**: `str`, `int`, `float`, `bool`, `dict`
2. **Typed Lists Required**: Use `List[Dict[str, str]]`, `List[str]`, etc. - **NEVER** bare `list`
3. **No Default Parameters**: Never use default values (LLMs cannot interpret them)
4. **No Union Types**: Avoid `Union` types (create AnyOf constructs)
5. **No Any Types**: Never use `Any` in parameters
6. **No Bytes Parameters**: Not JSON-serializable
7. **Comprehensive Docstrings**: Essential for LLM understanding
8. **Consistent Error Handling**: Use clear exception patterns

#### ❌ **Prohibited Patterns**
```python
# ❌ WRONG - Will cause Google AI errors
def bad_function(
    data: list,                    # Missing items specification
    count: int = 0,               # Default parameter value
    mode: Union[str, int],        # Union type creates AnyOf
    content: Any,                 # Any type not allowed
    binary_data: bytes            # Bytes not JSON-serializable
) -> str:
    pass

# ✅ CORRECT - Google AI compatible
def good_function(
    data: List[Dict[str, str]],   # Properly typed list
    count: int,                   # Required parameter
    mode: str,                    # Single specific type
    content: dict                 # JSON-serializable type
) -> str:
    pass
```

#### 🔍 **Validation Commands**
Run these to check for compatibility issues:
```bash
# Check for untyped lists (will cause Google AI errors)
rg "^def [a-zA-Z_][a-zA-Z0-9_]*\([^)]*: list[^\[]" src/ --type py

# Check for prohibited Union types
rg "^def [a-zA-Z_][a-zA-Z0-9_]*\([^)]*Union\[" src/ --type py

# Check for prohibited Any types
rg "^def [a-zA-Z_][a-zA-Z0-9_]*\([^)]*: Any" src/ --type py

# Check for prohibited default values
rg "^def [a-zA-Z_][a-zA-Z0-9_]*\([^)]*=" src/ --type py
```

### Documentation

- Update documentation for any new features
- Include docstrings with parameters, return values, and examples
- Add usage examples to the docs/examples.md file
- Update API reference documentation

### Testing

- Write tests for all new functionality
- Maintain or improve test coverage
- Test both success and error cases
- Use descriptive test names

### Error Handling

- Use custom exceptions from `exceptions.py`
- Provide clear, actionable error messages
- Handle edge cases gracefully
- Document expected exceptions in docstrings

## Adding New Agent Tool Modules

### 1. Choose the Right Category

The project is organized into these categories:
- `file_system` - File and directory operations (implemented)
- `network` - Network utilities and validation (planned)
- `text` - Text processing and manipulation (planned)
- `data` - Data parsing and conversion (planned)
- `system` - System information and processes (planned)
- `crypto` - Cryptographic utilities (planned)
- `utilities` - Common helpers and utilities (planned)

### 2. Follow the Agent Tool Pattern

Each module should provide functions that work well as agent tools, following the code style guidelines above.

### 3. Agent Integration Testing

When adding new functions, test them with agent frameworks:
- Test individual function imports
- Verify function signatures work with agent tools
- Test error handling in agent contexts
- Ensure docstrings provide clear guidance for AI

### 4. Update Package Exports

When adding new modules:
1. Update `src/basic_open_agent_tools/__init__.py`
2. Add appropriate exports to module's `__init__.py`
3. Update documentation with agent usage examples
4. Add tests including agent integration patterns

## Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write code following the style guidelines
   - **Ensure Google AI compatibility** (see requirements above)
   - Add or update tests
   - Update documentation

3. **Test your changes:**
   ```bash
   # Run all quality checks
   pytest
   ruff check
   ruff format
   mypy src/basic_open_agent_tools
   
   # Validate Google AI compatibility
   rg "^def [a-zA-Z_][a-zA-Z0-9_]*\([^)]*: list[^\[]" src/ --type py
   rg "^def [a-zA-Z_][a-zA-Z0-9_]*\([^)]*=" src/ --type py
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```

5. **Push and create PR:**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a pull request on GitHub.

### PR Requirements

- [ ] All tests pass
- [ ] Code follows style guidelines (ruff, mypy)
- [ ] **Google AI compatibility verified** (no list/Union/Any/default parameters)
- [ ] Documentation is updated
- [ ] New functionality has tests
- [ ] PR description explains the changes

## Release Process

Releases are automated via GitHub Actions:

1. **Create a release:**
   - Tag format: `v1.2.3`
   - Follow semantic versioning
   - Include release notes

2. **Automatic publishing:**
   - GitHub Actions builds the package
   - Publishes to PyPI via Trusted Publishing
   - Creates GitHub release

## Troubleshooting Google AI Compatibility

### Common Error Messages

**Error:** `"missing field" in function declarations`
```
{"error": "400 INVALID_ARGUMENT. GenerateContentRequest.tools[0].function_declarations[4].parameters.properties[data].items: missing field."}
```

**Cause:** Untyped list parameters - Google AI requires list item specifications

**Fix:** Replace `data: list` with `data: List[Dict[str, str]]` or appropriate typing

**Error:** `"AnyOf is not supported"`
```
{"error": "AnyOf is not supported in function declaration schema for Google AI."}
```

**Cause:** Union types get converted to JSON Schema AnyOf constructs

**Fix:** Replace `Union[str, int]` with single specific type like `str`

**Error:** `"Failed to parse parameter"`
```
{"error": "Failed to parse the parameter data: bytes of function validate_binary_format"}
```

**Cause:** Non-JSON-serializable types (bytes, Any, complex types)

**Fix:** Use only JSON-serializable types (str, int, float, bool, dict, typed lists)

### Debugging Steps

1. **Run validation commands** to identify issues:
   ```bash
   rg "^def [a-zA-Z_][a-zA-Z0-9_]*\([^)]*: list[^\[]" src/ --type py
   ```

2. **Check function signatures** for compatibility:
   ```python
   import inspect
   import your_module
   
   # Check a specific function
   sig = inspect.signature(your_module.your_function)
   print(f"Function signature: {sig}")
   ```

3. **Test with agent tools** to verify compatibility:
   ```python
   import basic_open_agent_tools as boat
   
   # Load and test tools
   tools = boat.load_all_data_tools()
   print(f"Loaded {len(tools)} tools successfully")
   ```

## Getting Help

- **Issues:** Report bugs and request features via GitHub Issues
- **Discussions:** General questions and discussions on GitHub Discussions
- **Documentation:** Check the docs/ folder for detailed information

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment
- Follow the project's coding standards

Thank you for contributing to basic-open-agent-tools!
