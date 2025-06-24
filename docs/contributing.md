# Contributing

Thank you for your interest in contributing to basic-open-agent-tools! This toolkit provides essential functions for AI agent frameworks, and this guide will help you get started with development.

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

## Project Structure

```
basic-open-agent-tools/
├── src/basic_open_agent_tools/    # Main package source
│   ├── __init__.py               # Package initialization
│   ├── exceptions.py             # Custom exceptions
│   ├── types.py                  # Type definitions
│   ├── file_system/              # File system tools (implemented)
│   │   ├── __init__.py
│   │   ├── operations.py         # Core file operations
│   │   ├── info.py              # File information utilities
│   │   ├── tree.py              # Directory tree operations
│   │   └── validation.py        # Path validation
│   ├── network/                  # Network tools (planned)
│   ├── text/                     # Text processing (planned)
│   ├── data/                     # Data utilities (planned)
│   ├── system/                   # System tools (planned)
│   ├── crypto/                   # Crypto utilities (planned)
│   └── utilities/                # Common utilities (planned)
├── tests/                        # Test suite
├── docs/                         # Documentation
├── .github/workflows/            # CI/CD pipelines
└── pyproject.toml               # Package configuration
```

## Agent Toolkit Design Philosophy

This project is specifically designed to provide **tool functions for AI agents**. Key principles:

### Function-First Design
- Each function is designed to work as an individual agent tool
- Functions have clear, descriptive names suitable for AI interpretation
- Parameters and return values are optimized for agent framework integration
- Comprehensive docstrings help AI understand function purpose and usage

### Agent Framework Integration
Functions are designed to work with various agent frameworks:
- **Google ADK** - Direct function imports in tools list
- **LangChain** - Functions can be wrapped with StructuredTool
- **Custom Agents** - Direct function integration
- **MCP Servers** - Adaptable for Model Context Protocol

### Import Patterns
- **Individual function imports** (preferred for agents)
- **Module imports** (for direct developer usage)
- **Clear separation** between agent tools and developer utilities

## Contributing Guidelines

### Code Style for Agent Tools

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write comprehensive docstrings for all public functions and classes
- Keep functions focused and single-purpose (optimal for agent tools)
- Use descriptive variable and function names that agents can understand
- Design function signatures to be clear for AI interpretation
- Ensure functions are stateless and thread-safe where possible

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

Each module should provide functions that work well as agent tools:
- **Clear, focused purpose** - Each function does one thing well
- **Agent-friendly names** - Descriptive function names that AI can understand
- **Comprehensive docstrings** - Help AI understand function purpose and usage
- **Type hints throughout** - Clear parameter and return types
- **Appropriate error handling** - Consistent exception patterns
- **Individual function exports** - Functions can be imported individually
- **Stateless design** - Functions don't rely on external state
- **Thread-safe operations** - Safe for concurrent agent usage

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
   - Add or update tests
   - Update documentation

3. **Test your changes:**
   ```bash
   pytest
   ruff check
   mypy src/basic_open_agent_tools
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