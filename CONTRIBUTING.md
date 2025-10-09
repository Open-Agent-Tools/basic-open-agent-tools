# Contributing to Basic Open Agent Tools

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Style Guide](#style-guide)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/basic-open-agent-tools.git
   cd basic-open-agent-tools
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/Open-Agent-Tools/basic-open-agent-tools.git
   ```

## Development Setup

### Prerequisites

- Python 3.9 or higher
- pip or uv for package management

### Installation

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks** (optional but recommended):
   ```bash
   pre-commit install
   ```

## Making Changes

1. **Create a new branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the [Style Guide](#style-guide)

3. **Write or update tests** for your changes

4. **Run tests** to ensure everything works:
   ```bash
   pytest
   ```

5. **Run linters and formatters**:
   ```bash
   ruff check .
   ruff format .
   mypy src/
   ```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/basic_open_agent_tools

# Run specific test file
pytest tests/test_specific.py

# Run specific test
pytest tests/test_specific.py::test_function_name
```

### Test Organization

- Unit tests go in `tests/` directory
- Mirror the source structure in `src/basic_open_agent_tools/`
- Use descriptive test names: `test_<function>_<scenario>_<expected_result>`

### Writing Tests

- Test both success and failure cases
- Use fixtures for common test data
- Mock external dependencies
- Aim for high coverage but focus on meaningful tests

## Submitting Changes

### Before Submitting

- [ ] Tests pass locally
- [ ] Code follows style guide (ruff, mypy)
- [ ] Documentation is updated (if applicable)
- [ ] CHANGELOG.md is updated (if applicable)
- [ ] Commit messages are clear and descriptive

### Pull Request Process

1. **Push your changes** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub

3. **Fill out the PR template** with:
   - Clear description of changes
   - Related issue numbers
   - Testing performed
   - Breaking changes (if any)

4. **Wait for review**:
   - Address reviewer feedback
   - Keep PR up to date with main branch
   - Be patient and respectful

### Commit Message Guidelines

```
type(scope): brief description

Longer description if needed, explaining:
- Why the change is necessary
- How it addresses the issue
- Any side effects or considerations

Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build, dependencies, tooling

## Style Guide

### Python Code Style

- **Line length**: 88 characters (enforced by ruff)
- **Type hints**: Use type hints for all function parameters and return values
- **Docstrings**: Use Google-style docstrings

Example:
```python
def example_function(param: str, skip_confirm: bool) -> str:
    """Brief one-line description.

    Longer description if needed.

    Args:
        param: Description of param
        skip_confirm: If True, skip confirmation prompts

    Returns:
        Description of return value

    Raises:
        ValueError: When param is invalid
    """
    pass
```

### Code Organization

- One class per file (exceptions for small helper classes)
- Group imports: stdlib, third-party, local
- Keep functions focused and small
- Use meaningful variable names

### Documentation

- Update README.md for user-facing changes
- Update module-level READMEs in src/
- Add inline comments for complex logic
- Keep docs up to date with code changes

## Reporting Issues

### Bug Reports

Use the **Bug Report** template and include:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)
- Error messages and stack traces

### Feature Requests

Use the **Feature Request** template and include:
- Clear description of the feature
- Use case and motivation
- Proposed API or interface
- Alternatives considered

### Security Issues

**Do not** open public issues for security vulnerabilities. Instead:
- Use [GitHub Security Advisories](https://github.com/Open-Agent-Tools/basic-open-agent-tools/security/advisories/new)
- Or email the maintainers directly
- See [SECURITY.md](SECURITY.md) for details

## Questions?

- Open a [Discussion](https://github.com/Open-Agent-Tools/basic-open-agent-tools/discussions) for questions
- Check existing issues and discussions first
- Be respectful and patient

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Basic Open Agent Tools! 🎉
