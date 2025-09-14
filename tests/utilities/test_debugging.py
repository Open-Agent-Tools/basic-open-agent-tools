"""Tests for debugging utilities."""

import sys

import pytest

from basic_open_agent_tools.exceptions import BasicAgentToolsError
from basic_open_agent_tools.utilities.debugging import (
    format_exception_details,
    get_call_stack_info,
    inspect_function_signature,
    trace_variable_changes,
    validate_function_call,
)


class TestInspectFunctionSignature:
    """Test cases for inspect_function_signature function."""

    def test_invalid_function_name_type(self):
        """Test with invalid function name type."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            inspect_function_signature(123)
        assert "Function name must be a non-empty string" in str(exc_info.value)

    def test_empty_function_name(self):
        """Test with empty function name."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            inspect_function_signature("")
        assert "Function name must be a non-empty string" in str(exc_info.value)

    def test_builtin_function_inspection(self):
        """Test inspecting a built-in function."""
        result = inspect_function_signature("print")

        assert result["function_name"] == "print"
        assert result["module_name"] == "current_scope"
        assert "args" in result["signature"]  # print has *args parameter
        assert result["parameter_count"] >= 1  # At least 'args' parameter
        assert result["inspection_status"] == "success"

    def test_nonexistent_function(self):
        """Test with nonexistent function name."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            inspect_function_signature("nonexistent_function_12345")
        assert "not found in current scope" in str(exc_info.value)

    def test_invalid_module_name(self):
        """Test with invalid module name type."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            inspect_function_signature("print", 123)
        assert "Module name must be a non-empty string" in str(exc_info.value)

    def test_custom_function_inspection(self):
        """Test inspecting a custom function."""

        def test_func(arg1: str, arg2: int = 10) -> str:
            """Test function docstring."""
            return f"{arg1}_{arg2}"

        # Add to current scope
        globals()["test_func"] = test_func

        result = inspect_function_signature("test_func")

        assert result["function_name"] == "test_func"
        assert result["parameter_count"] == 2
        assert result["docstring"] == "Test function docstring."
        assert "str" in result["return_annotation"]

        # Check parameter details
        params = result["parameters"]
        assert len(params) == 2
        assert params[0]["name"] == "arg1"
        assert not params[0]["has_default"]
        assert params[1]["name"] == "arg2"
        assert params[1]["has_default"]
        assert params[1]["default_value"] == "10"

        # Cleanup
        del globals()["test_func"]


class TestGetCallStackInfo:
    """Test cases for get_call_stack_info function."""

    def test_call_stack_structure(self):
        """Test call stack information structure."""

        def inner_function():
            return get_call_stack_info()

        def outer_function():
            return inner_function()

        result = outer_function()

        assert "stack_depth" in result
        assert "current_function" in result
        assert "current_file" in result
        assert "current_line" in result
        assert "call_stack" in result
        assert result["stack_retrieval_status"] == "success"

        # Check that stack contains our functions
        function_names = [frame["function_name"] for frame in result["call_stack"]]
        assert "inner_function" in function_names
        assert "outer_function" in function_names

    def test_call_stack_frame_structure(self):
        """Test individual frame structure."""
        result = get_call_stack_info()

        assert len(result["call_stack"]) > 0
        frame = result["call_stack"][0]

        required_keys = [
            "level",
            "filename",
            "function_name",
            "line_number",
            "code_context",
            "is_current_function",
        ]
        for key in required_keys:
            assert key in frame

        assert frame["is_current_function"] is True


class TestFormatExceptionDetails:
    """Test cases for format_exception_details function."""

    def test_no_exception_available(self):
        """Test when no exception information is available."""
        # Clear any existing exception
        sys.exc_clear() if hasattr(sys, "exc_clear") else None

        with pytest.raises(BasicAgentToolsError) as exc_info:
            format_exception_details()
        assert "No exception information available" in str(exc_info.value)

    def test_format_current_exception(self):
        """Test formatting current exception."""
        try:
            1 / 0
        except ZeroDivisionError:
            result = format_exception_details()

            assert result["exception_type"] == "ZeroDivisionError"
            assert "division by zero" in result["exception_message"].lower()
            assert result["has_traceback"] is True
            assert result["formatting_status"] == "success"
            assert len(result["traceback_lines"]) > 0
            assert len(result["frames"]) > 0

    def test_format_provided_exception_string(self):
        """Test formatting provided exception string."""
        exception_string = "Custom exception information"

        result = format_exception_details(exception_string)

        assert result["exception_source"] == "provided_string"
        assert result["exception_info"] == exception_string
        assert result["parsing_status"] == "string_provided_as_is"

    def test_invalid_exception_info_type(self):
        """Test with invalid exception info type."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            format_exception_details(123)
        assert "Exception info must be a string" in str(exc_info.value)


class TestValidateFunctionCall:
    """Test cases for validate_function_call function."""

    def test_invalid_function_name_type(self):
        """Test with invalid function name type."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            validate_function_call(123, {})
        assert "Function name must be a non-empty string" in str(exc_info.value)

    def test_invalid_arguments_type(self):
        """Test with invalid arguments type."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            validate_function_call("print", "not_a_dict")
        assert "Arguments must be a dictionary" in str(exc_info.value)

    def test_successful_validation(self):
        """Test successful function call validation."""
        arguments = {"sep": " ", "end": "\n"}

        result = validate_function_call("print", arguments)

        assert result["function_name"] == "print"
        assert result["is_valid"] is True
        assert result["can_call"] is True
        assert result["validation_status"] == "completed"
        assert "sep" in result["provided_arguments"]

    def test_missing_required_arguments(self):
        """Test validation with missing required arguments."""
        # Test with len() which requires one argument
        arguments = {}

        result = validate_function_call("len", arguments)

        assert result["is_valid"] is False
        assert result["can_call"] is False
        assert len(result["missing_required"]) > 0
        assert "binding_error" in result

    def test_extra_arguments(self):
        """Test validation with extra arguments."""
        arguments = {"value": "Hello", "extra_arg": "not_needed"}

        result = validate_function_call("print", arguments)

        # print() accepts **kwargs so this should still be valid
        assert "extra_arg" in result["provided_arguments"]

    def test_nonexistent_function(self):
        """Test validation of nonexistent function."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            validate_function_call("nonexistent_function_98765", {})
        assert "not found in current scope" in str(exc_info.value)


class TestTraceVariableChanges:
    """Test cases for trace_variable_changes function."""

    def test_invalid_variable_name_type(self):
        """Test with invalid variable name type."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            trace_variable_changes(123, 0, [])
        assert "Variable name must be a non-empty string" in str(exc_info.value)

    def test_invalid_operations_type(self):
        """Test with invalid operations type."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            trace_variable_changes("var", 0, "not_a_list")
        assert "Operations must be a list of strings" in str(exc_info.value)

    def test_invalid_variable_identifier(self):
        """Test with invalid Python identifier."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            trace_variable_changes("123invalid", 0, [])
        assert "is not a valid Python identifier" in str(exc_info.value)

    def test_successful_tracing(self):
        """Test successful variable tracing."""
        operations = [
            "counter = counter + 1",
            "counter = counter * 2",
            "counter = counter - 5",
        ]

        result = trace_variable_changes("counter", 0, operations)

        assert result["variable_name"] == "counter"
        assert result["initial_value"] == 0
        assert result["final_value"] == -3  # (0+1)*2-5 = -3
        assert result["operations_count"] == 3
        assert result["successful_operations"] == 3
        assert result["failed_operations"] == 0
        assert result["tracing_status"] == "completed"

        # Check trace steps
        steps = result["trace_steps"]
        assert len(steps) == 4  # Initial + 3 operations
        assert steps[0]["step"] == 0
        assert steps[0]["operation"] == "initialization"
        assert steps[0]["value"] == 0

    def test_dangerous_operation_blocking(self):
        """Test that dangerous operations are blocked."""
        operations = ["import os", "counter = 1"]

        with pytest.raises(BasicAgentToolsError) as exc_info:
            trace_variable_changes("counter", 0, operations)
        assert "potentially dangerous keyword" in str(exc_info.value)

    def test_operation_with_syntax_error(self):
        """Test handling of operations with syntax errors."""
        operations = [
            "counter = counter + 1",
            "counter = counter +",  # Syntax error
            "counter = counter * 2",
        ]

        result = trace_variable_changes("counter", 0, operations)

        assert result["successful_operations"] == 2  # First and third operations
        assert result["failed_operations"] == 1

        # Check that execution continued after error
        assert result["final_value"] == 2  # (0+1)*2 = 2

    def test_empty_operations_list(self):
        """Test with empty operations list."""
        result = trace_variable_changes("var", 42, [])

        assert result["initial_value"] == 42
        assert result["final_value"] == 42
        assert result["operations_count"] == 0
        assert result["successful_operations"] == 0
        assert result["failed_operations"] == 0

    def test_non_string_operation(self):
        """Test with non-string operation in list."""
        operations = ["counter = counter + 1", 123, "counter = counter * 2"]

        result = trace_variable_changes("counter", 0, operations)

        # Should handle the non-string operation gracefully
        assert result["failed_operations"] == 1
        assert result["successful_operations"] == 2
