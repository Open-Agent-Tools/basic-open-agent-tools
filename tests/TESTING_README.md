# Testing Guide

This project uses traditional unit tests and agent evaluation tests. This guide provides commands for running tests and implementing the testing strategy.

## Quick Command Reference

```bash
# Run all tests
python3 -m pytest tests/ -v

# Fast tests only (skip agent evaluations)
python3 -m pytest tests/ -v -m "not agent_evaluation"

# Agent tests only (requires GOOGLE_API_KEY)
python3 -m pytest tests/ -v -m "agent_evaluation"

# Run with coverage
python3 -m pytest tests/ --cov=src/basic_open_agent_tools --cov-report=term-missing

# Quality checks
python3 -m ruff check src/ tests/ --fix
python3 -m ruff format src/ tests/
python3 -m mypy src/
```

## Test Types

**Traditional Unit Tests**: Fast tests of individual functions (no API calls)
- Location: `tests/*/test_*.py`
- Coverage: 96% code coverage

**Agent Evaluation Tests**: Test AI agent compatibility (requires Google API key)
- Location: `tests/*/*_agent_evaluation.py` 
- Requirements: `GOOGLE_API_KEY` environment variable
- Behavior: Sequential execution with rate limiting

## Directory Structure

```
tests/
├── {module}/
│   ├── test_{module}.py              # Traditional unit tests
│   └── test_{module}_agent/          # Agent evaluation tests
│       ├── agent/sample_agent.py     # Agent implementation
│       ├── test_{module}_agent_evaluation.py
│       ├── test_config.json
│       └── list_available_tools.test.json
```

## Environment Setup

**Traditional Tests**: No setup required

**Agent Tests**: Set Google API key and ensure quota
```bash
export GOOGLE_API_KEY="your-api-key-here"
```
Free tier: 15 requests/minute. Tests run sequentially with 2-second delays to prevent quota issues.

## Implementation Guide

### Example Implementation: CSV Tools Module

The CSV tools module demonstrates the simplified agent evaluation strategy:

```
tests/data/
├── test_csv_tools.py            # Traditional unit tests
└── test_csv_tools_agent/        # Agent evaluation suite
    ├── agent/
    │   ├── __init__.py          # Exports agent
    │   └── sample_agent.py      # CSV tools agent
    ├── test_csv_tools_agent_evaluation.py  # Agent test runner
    ├── test_config.json                     # ADK evaluation criteria
    └── list_available_tools.test.json       # Tool listing test
```

**Key Features:**
- **Simple Setup**: Agent loads module tools directly
- **Single Evaluation**: Only tests tool listing capability
- **Native Response**: Agent responds without calling helper functions
- **Working Pattern**: Proven to work with Google ADK evaluation framework

### Implementation Overview

#### Traditional Unit Tests

Create `tests/{module}/test_{module}.py` with:
- Test classes for each function
- Basic functionality, error handling, edge cases
- Parameter combinations and integration tests
- Use pytest fixtures and descriptive test names

#### Test Coverage Requirements

Ensure comprehensive coverage for each function:

**Required Test Categories:**
- ✅ **Basic functionality**: Happy path scenarios
- ✅ **Parameter validation**: All parameter combinations
- ✅ **Error handling**: All exception paths
- ✅ **Edge cases**: Empty inputs, large inputs, boundary values
- ✅ **Type safety**: Input/output type validation
- ✅ **Integration**: Functions working together

**Coverage Standards:**
- **Minimum**: 70% code coverage per module
- **Target**: 90%+ code coverage
- **Google ADK Compliance**: All functions use JSON-serializable types

#### Agent Evaluation Tests

**Focus**: Test only public functions (in module's `__all__` list)

Required files for each module:
1. `agent/sample_agent.py` - Agent with module tools
2. `test_config.json` - ADK evaluation criteria (0.7 scores)
3. `list_available_tools.test.json` - Tool listing test case
4. `test_{module}_agent_evaluation.py` - Test runner

**Key Pattern**: Test tool listing capability rather than complex workflows. This proven pattern works reliably with Google ADK evaluation framework.

## Quality Assurance

### Pre-Implementation Checklist
- Review function signatures for Google ADK compliance
- Identify test scenarios and parameter combinations
- Plan error cases and edge cases

### Required Files
- `test_{module}.py` - Traditional unit tests
- `test_{module}_agent/` directory with agent files
- Focus on tool listing capability for reliable ADK evaluation

### Development Workflow

1. **Quality Checks**: Run ruff, mypy, and pytest before commits
2. **Test Modules**: Test specific modules with coverage reports  
3. **Agent Tests**: Verify agent imports and run evaluations
4. **Debug**: Use ADK CLI for detailed troubleshooting:
   ```bash
   PYTHONPATH=src:.:$PYTHONPATH adk eval \
     --config_file_path tests/{module}/test_{module}_agent/test_config.json \
     --print_detailed_results \
     tests/{module}/test_{module}_agent/agent \
     tests/{module}/test_{module}_agent/list_available_tools.test.json
   ```

## Troubleshooting

- **API Quota Exceeded**: Run `python3 -m pytest tests/ -v -m "not agent_evaluation"`
- **Missing API Key**: Set `GOOGLE_API_KEY` or skip agent tests  
- **Import Errors**: Check `__init__.py` files and module paths
- **JSON Errors**: Validate with `python3 -c "import json; json.load(open('file.json'))"`
- **Coverage Gaps**: Add targeted tests for missing exception paths

## Coverage Standards

- **Traditional Tests**: Minimum 70% code coverage, test all exported functions
- **Agent Tests**: Test only public functions in module's `__all__` list

## Best Practices

- **Traditional Tests**: One class per function, descriptive names, test edge cases
- **Agent Tests**: Use natural language requests, focus on tool listing capability
- **Organization**: Consistent naming, clear documentation, modular structure