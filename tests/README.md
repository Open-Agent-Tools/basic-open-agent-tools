# Testing Strategy Guide

This document provides comprehensive instructions for implementing the dual testing strategy used in `basic-open-agent-tools`: **Traditional Unit Tests** and **Agent Evaluation Tests**.

## Overview

Our testing approach ensures both code correctness and AI agent compatibility:

- **Traditional Unit Tests**: Comprehensive pytest-based tests for defensive programming
- **Agent Evaluation Tests**: Google ADK evaluation tests that validate functions work correctly when called by AI agents

## Directory Structure

```
tests/
├── README.md                    # This guide
├── __init__.py                  # Makes tests a package
├── {module_name}/               # Per-module test directory
│   ├── __init__.py             # Module test package
│   ├── test_{module}.py        # Traditional unit tests
│   └── test_{module}_agent/    # Agent evaluation tests
│       ├── __init__.py         # Agent test package
│       ├── agent/              # Agent implementation
│       │   ├── __init__.py     # Agent module exports
│       │   └── sample_agent.py # Agent with module tools
│       ├── test_{module}_agent_evaluation.py  # Agent test runner
│       ├── test_config.json                   # ADK evaluation criteria
│       └── list_available_tools.test.json     # Tool listing evaluation
```

## Example Implementation: CSV Tools Module

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

## Step-by-Step Implementation Guide

### Phase 1: Traditional Unit Tests

#### 1. Create Module Test File

**File**: `tests/{module}/test_{module}.py`

```python
"""Tests for basic_open_agent_tools.{module}.{submodule} module."""

import pytest
from pathlib import Path
from basic_open_agent_tools.exceptions import {ModuleError}
from basic_open_agent_tools.{module}.{submodule} import (
    function_one,
    function_two,
)

class TestFunctionOne:
    """Test cases for function_one."""
    
    def test_basic_functionality(self, tmp_path: Path) -> None:
        """Test basic function behavior."""
        # Setup test data
        test_input = "example"
        
        # Execute function
        result = function_one(test_input)
        
        # Verify results
        assert result == "expected_output"
        assert isinstance(result, str)
    
    def test_error_conditions(self) -> None:
        """Test error handling."""
        with pytest.raises({ModuleError}, match="expected error message"):
            function_one("invalid_input")
    
    def test_edge_cases(self) -> None:
        """Test edge cases and boundary conditions."""
        # Test empty input
        result = function_one("")
        assert result == "expected_empty_result"
        
        # Test maximum input
        large_input = "x" * 10000
        result = function_one(large_input)
        assert len(result) > 0

class TestFunctionTwo:
    """Test cases for function_two."""
    
    def test_parameter_combinations(self) -> None:
        """Test all parameter combinations."""
        # Test different parameter values
        test_cases = [
            ("input1", True, "expected1"),
            ("input2", False, "expected2"),
        ]
        
        for input_val, flag, expected in test_cases:
            result = function_two(input_val, flag)
            assert result == expected

# Integration tests
class TestModuleIntegration:
    """Integration tests for multiple functions."""
    
    def test_function_compatibility(self) -> None:
        """Test functions work together."""
        result_one = function_one("test")
        result_two = function_two(result_one, True)
        assert result_two is not None
```

#### 2. Test Coverage Requirements

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

### Phase 2: Agent Evaluation Tests

**Important**: Agent evaluation tests should only cover **public functions** that are intended for use by AI agents. Internal helper functions, private methods, and utility functions that are not exposed in the module's `__all__` list do not need agent evaluation tests.

#### 1. Create Agent Implementation

**File**: `tests/{module}/test_{module}_agent/agent/sample_agent.py`

```python
"""Agent module for {module} tools testing.

This module provides an AI agent that uses the basic_open_agent_tools
{module} functions for ADK evaluation testing.
"""

from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents import Agent

from basic_open_agent_tools.{module}.{submodule} import (
    function_one,
    function_two,
    function_three,
    # Import all public functions from the module
)

# Load environment variables for API keys
load_dotenv()  # From current working directory (when pytest runs from root)
project_root = Path(__file__).parent.parent.parent.parent.parent
load_dotenv(project_root / ".env")  # From project root

root_agent = Agent(
    name="{module}_agent",
    model="gemini-2.0-flash",
    description="Agent that can process {data_type} using the basic_open_agent_tools {module} utilities.",
    instruction="""You are a helpful agent that can work with {data_type}.

You have access to tools for reading, writing, parsing, validating, and processing {data_type}. 

Always provide clear output showing the processing results.""",
    tools=[
        function_one,
        function_two,
        function_three,
        # List all imported functions
    ],
)
```

**Example from working CSV agent:**
```python
from basic_open_agent_tools.data.csv_tools import (
    clean_csv_data,
    csv_to_dict_list,
    detect_csv_delimiter,
    dict_list_to_csv,
    read_csv_simple,
    validate_csv_structure,
    write_csv_simple,
)

root_agent = Agent(
    name="csv_tools_agent",
    model="gemini-2.0-flash",
    description="Agent that can process CSV files using the basic_open_agent_tools CSV utilities.",
    instruction="""You are a helpful agent that can work with CSV data.

You have access to tools for reading, writing, parsing, validating, and cleaning CSV files. You can detect delimiters, convert between formats, and process CSV data structures.

Always provide clear output showing the CSV processing results.""",
    tools=[
        read_csv_simple,
        write_csv_simple,
        csv_to_dict_list,
        dict_list_to_csv,
        detect_csv_delimiter,
        validate_csv_structure,
        clean_csv_data,
    ],
)
```

#### 2. Create Agent Module Exports

**File**: `tests/{module}/test_{module}_agent/agent/__init__.py`

```python
"""{Module} agent for ADK evaluation testing."""

from . import sample_agent as agent
```

#### 3. Create ADK Evaluation Configuration

**ADK Config File**: `tests/{module}/test_{module}_agent/test_config.json`

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 0.7,
    "response_match_score": 0.7
  }
}
```

This file configures the Google ADK evaluation criteria for agent testing.

#### 4. Create Tool Listing Test

**Tool Listing Test File**: `tests/{module}/test_{module}_agent/list_available_tools.test.json`

```json
{
  "eval_set_id": "list_available_tools_test_set",
  "name": "List Available Tools Test",
  "description": "Test case for listing available tools through agent interaction",
  "eval_cases": [
    {
      "eval_id": "list_available_tools_test",
      "conversation": [
        {
          "invocation_id": "list-tools-001",
          "user_content": {
            "parts": [
              {
                "text": "List all available tools alphabetically."
              }
            ],
            "role": "user"
          },
          "final_response": {
            "parts": [
              {
                "text": "    function_one,\n    function_two,\n    function_three,"
              }
            ],
            "role": "model"
          },
          "intermediate_data": {
            "tool_uses": [],
            "intermediate_responses": []
          }
        }
      ],
      "session_input": {
        "app_name": "{module}_agent",
        "user_id": "test_user",
        "state": {}
      }
    }
  ]
}
```

**Example from working CSV agent:**
```json
{
  "eval_set_id": "list_available_tools_test_set",
  "name": "List Available Tools Test", 
  "description": "Test case for listing available tools through agent interaction",
  "eval_cases": [
    {
      "eval_id": "list_available_tools_test",
      "conversation": [
        {
          "invocation_id": "list-tools-001",
          "user_content": {
            "parts": [
              {
                "text": "List all available tools alphabetically."
              }
            ],
            "role": "user"
          },
          "final_response": {
            "parts": [
              {
                "text": "    clean_csv_data,\n    csv_to_dict_list,\n    detect_csv_delimiter,\n    dict_list_to_csv,\n    read_csv_simple,\n    validate_csv_structure,\n    write_csv_simple,"
              }
            ],
            "role": "model"
          },
          "intermediate_data": {
            "tool_uses": [],
            "intermediate_responses": []
          }
        }
      ],
      "session_input": {
        "app_name": "csv_tools_agent",
        "user_id": "test_user",
        "state": {}
      }
    }
  ]
}
```

#### 5. Create Agent Evaluation Test Runner

**File**: `tests/{module}/test_{module}_agent/test_{module}_agent_evaluation.py`

```python
"""ADK evaluation tests for {module} agent tools.

This test suite validates that {module} functions work correctly
when called by AI agents in the Google ADK framework.
"""

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator


class Test{Module}AgentEvaluation:
    """Agent evaluation tests for {module} tools."""

    @pytest.mark.asyncio
    async def test_list_available_tools_agent(self):
        """Test agent listing available tools."""
        await AgentEvaluator.evaluate(
            agent_module="tests.{module}.test_{module}_agent.agent",
            eval_dataset_file_path_or_dir="tests/{module}/test_{module}_agent/list_available_tools.test.json",
        )
```

**Example from working CSV agent:**
```python
"""ADK evaluation tests for CSV tools agent.

This test suite validates that CSV tools functions work correctly
when called by AI agents in the Google ADK framework.
"""

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator


class TestCsvToolsAgentEvaluation:
    """Agent evaluation tests for CSV tools."""

    @pytest.mark.asyncio
    async def test_list_available_tools_agent(self):
        """Test agent listing available tools."""
        await AgentEvaluator.evaluate(
            agent_module="tests.data.test_csv_tools_agent.agent",
            eval_dataset_file_path_or_dir="tests/data/test_csv_tools_agent/list_available_tools.test.json",
        )
```

## Quality Assurance Workflow

### Pre-Implementation Checklist

Before writing tests:
- ✅ **Review function signatures**: Ensure Google ADK compliance
- ✅ **Identify test scenarios**: Map all parameter combinations
- ✅ **Plan error cases**: List all possible exceptions
- ✅ **Design edge cases**: Consider boundary conditions

### Required Files Checklist

Each agent test suite must include:
- ✅ **test_{module}.py**: Traditional unit tests with comprehensive coverage
- ✅ **test_{module}_agent/__init__.py**: Agent test package initialization
- ✅ **test_{module}_agent/agent/__init__.py**: Agent module exports
- ✅ **test_{module}_agent/agent/sample_agent.py**: Agent implementation with module tools
- ✅ **test_{module}_agent/test_config.json**: ADK evaluation criteria configuration
- ✅ **test_{module}_agent/test_{module}_agent_evaluation.py**: Agent test runner
- ✅ **test_{module}_agent/list_available_tools.test.json**: Tool listing evaluation test

**Simplified Approach**: Focus on tool listing capability rather than complex individual function tests or multi-tool workflows. This proven pattern works reliably with Google ADK evaluation framework.

### Development Workflow

#### 1. Run Quality Checks

**Always run before committing:**

```bash
# Lint and format
python3 -m ruff check tests/{module}/ --fix
python3 -m ruff format tests/{module}/

# Type checking
python3 -m mypy tests/{module}/ --ignore-missing-imports

# Run tests with coverage
python3 -m pytest tests/{module}/ --cov=src/basic_open_agent_tools/{module} --cov-report=term

# Validate JSON files
python3 -c "import json; [print(f'{f}: OK') for f in ['test1.json', 'test2.json'] if json.load(open(f))]"
```

#### 2. Test Traditional Units

```bash
# Run specific module tests
python3 -m pytest tests/{module}/test_{module}.py -v

# Check coverage
python3 -m pytest tests/{module}/test_{module}.py --cov=src/basic_open_agent_tools/{module} --cov-report=term
```

#### 3. Test Agent Evaluations

```bash
# Test agent import
python3 -c "from tests.{module}.test_{module}_agent.agent import agent; print('Agent OK:', agent.root_agent.name)"

# Run agent evaluations (requires API keys)
python3 -m pytest tests/{module}/test_{module}_agent/test_{module}_agent_evaluation.py -v
```

#### 4. Manual Agent Evaluation (Debugging)

For detailed debugging of agent responses, use the ADK CLI directly:

```bash
# Run manual evaluation with detailed output
PYTHONPATH=/Users/wes/Development/basic-open-agent-tools/src:/Users/wes/Development/basic-open-agent-tools:$PYTHONPATH adk eval \
    --config_file_path tests/{module}/test_{module}_agent/test_config.json \
    --print_detailed_results \
    tests/{module}/test_{module}_agent/agent \
    tests/{module}/test_{module}_agent/{test_file}.test.json

# Example for JSON tools:
PYTHONPATH=/Users/wes/Development/basic-open-agent-tools/src:/Users/wes/Development/basic-open-agent-tools:$PYTHONPATH adk eval \
    --config_file_path tests/data/test_json_tools_agent/test_config.json \
    --print_detailed_results \
    tests/data/test_json_tools_agent/agent \
    tests/data/test_json_tools_agent/list_available_tools.test.json
```

**Benefits of manual evaluation:**
- Shows exact agent responses vs expected responses
- Displays detailed evaluation metrics
- Reveals if agent fails to respond (final_response: null)
- Helpful for debugging response format mismatches
- Shows tool usage patterns

### Coverage Standards

**Traditional Tests:**
- **Code Coverage**: Minimum 70%, target 90%+
- **Function Coverage**: All exported functions tested
- **Parameter Coverage**: All parameter combinations
- **Error Coverage**: All exception paths
- **Edge Case Coverage**: Boundary conditions

**Agent Tests:**
- **Public Function Coverage**: Only functions in module's `__all__` list (not internal helpers)
- **Tool Coverage**: Each public function tested individually (1 test per tool)
- **Natural Language**: Human-like requests instead of explicit function calls
- **Workflow Coverage**: Comprehensive tests for multi-function scenarios
- **Error Recovery**: Invalid parameter handling in workflows

## Troubleshooting Common Issues

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'tests.module.agent'`

**Solution**: Check `__init__.py` files and import paths:
```python
# In agent/__init__.py
from . import sample_agent as agent  # Correct

# In test file
agent_module="tests.module.test_module_agent.agent"  # Points to directory
```

### JSON Validation Errors

**Problem**: Invalid JSON test files

**Solution**: Validate JSON syntax:
```bash
python3 -c "import json; json.load(open('test.json'))"
```

### Coverage Gaps

**Problem**: Missing test coverage for specific lines

**Solution**: Add targeted tests:
```python
def test_exception_handling(self):
    """Test specific exception path."""
    with pytest.raises(SpecificError):
        function_that_should_fail("bad_input")
```

### Agent Tool Loading

**Problem**: Agent doesn't recognize tools

**Solution**: Verify tool imports and agent configuration:
```python
# Check tools are imported correctly
from basic_open_agent_tools.module.submodule import function_name

# Verify agent has tools
tools=[function_one, function_two]  # List of actual function objects
```

## Best Practices

### Traditional Tests
- ✅ **One class per function** for organization
- ✅ **Descriptive test names** that explain what's being tested
- ✅ **Arrange-Act-Assert pattern** for clarity
- ✅ **Use fixtures** for common test data
- ✅ **Test edge cases** thoroughly
- ✅ **Mock external dependencies** when needed

### Agent Tests
- ✅ **Public functions only** - Test functions in module's `__all__` list, skip internal helpers
- ✅ **Natural language requests** in test scenarios (not explicit function calls)
- ✅ **One test per tool** to maintain simplicity
- ✅ **Realistic workflows** that agents would encounter  
- ✅ **Comprehensive tests** for multi-tool workflows
- ✅ **Expected outputs** that match function behavior
- ✅ **Proper JSON structure** following ADK standards

### File Organization
- ✅ **Consistent naming** across modules
- ✅ **Logical grouping** of related tests
- ✅ **Clear documentation** in test docstrings
- ✅ **Modular structure** for easy maintenance

## Integration with CI/CD

### GitHub Actions Integration

Add to `.github/workflows/test.yml`:

```yaml
- name: Run Traditional Tests
  run: |
    python -m pytest tests/ --cov=src/ --cov-report=xml

- name: Run Agent Evaluations
  env:
    GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
  run: |
    python -m pytest tests/ -k "agent_evaluation"
```

### Coverage Reporting

Configure coverage in `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "*/tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

This testing strategy ensures both code correctness and AI agent compatibility, providing comprehensive validation for all toolkit functions.
