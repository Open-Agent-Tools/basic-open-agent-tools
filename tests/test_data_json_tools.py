"""Tests for JSON processing tools.

This module provides comprehensive tests for the JSON processing toolkit functions,
including unit tests, integration tests, and Google AI compatibility verification.
"""

import inspect
import logging
import warnings

import pytest
from dotenv import load_dotenv
from google.adk.agents import Agent

from basic_open_agent_tools.data.json_tools import (
    safe_json_deserialize,
    safe_json_serialize,
    validate_json_string,
)
from basic_open_agent_tools.exceptions import SerializationError

# Initialize environment and logging
load_dotenv()
logging.basicConfig(level=logging.ERROR)
warnings.filterwarnings("ignore")


class TestSafeJsonSerialize:
    """Test safe_json_serialize function."""

    def test_serialize_dict(self):
        """Test serializing a dictionary."""
        data = {"name": "test", "value": 42}
        result = safe_json_serialize(data, 0)
        assert result == '{"name": "test", "value": 42}'

    def test_serialize_list(self):
        """Test serializing a list."""
        data = [1, 2, 3]
        result = safe_json_serialize(data, 0)
        assert result == "[1, 2, 3]"

    def test_serialize_with_indent(self):
        """Test serializing with indentation."""
        data = {"a": 1, "b": 2}
        result = safe_json_serialize(data, indent=2)
        expected = '{\n  "a": 1,\n  "b": 2\n}'
        assert result == expected

    def test_serialize_unicode(self):
        """Test serializing Unicode characters."""
        data = {"message": "Hello 世界"}
        result = safe_json_serialize(data, 0)
        assert "世界" in result

    def test_serialize_none(self):
        """Test serializing None."""
        result = safe_json_serialize(None, 0)
        assert result == "null"

    def test_serialize_invalid_indent_type(self):
        """Test with invalid indent type."""
        with pytest.raises(TypeError, match="indent must be an integer"):
            safe_json_serialize({"test": "data"}, indent="invalid")

    def test_serialize_non_serializable_object(self):
        """Test serializing non-serializable object."""

        class CustomClass:
            pass

        with pytest.raises(
            SerializationError, match="Failed to serialize data to JSON"
        ):
            safe_json_serialize({"obj": CustomClass()}, 0)


class TestSafeJsonDeserialize:
    """Test safe_json_deserialize function."""

    def test_deserialize_dict(self):
        """Test deserializing a dictionary."""
        json_str = '{"name": "test", "value": 42}'
        result = safe_json_deserialize(json_str)
        assert result == {"name": "test", "value": 42}

    def test_deserialize_list(self):
        """Test deserializing a list."""
        json_str = "[1, 2, 3]"
        result = safe_json_deserialize(json_str)
        assert result == {"result": [1, 2, 3]}

    def test_deserialize_unicode(self):
        """Test deserializing Unicode characters."""
        json_str = '{"message": "Hello 世界"}'
        result = safe_json_deserialize(json_str)
        assert result == {"message": "Hello 世界"}

    def test_deserialize_null(self):
        """Test deserializing null."""
        result = safe_json_deserialize("null")
        assert result == {"result": None}

    def test_deserialize_invalid_type(self):
        """Test with invalid input type."""
        with pytest.raises(TypeError, match="Input must be a string"):
            safe_json_deserialize({"invalid": "input"})

    def test_deserialize_invalid_json(self):
        """Test deserializing invalid JSON."""
        with pytest.raises(
            SerializationError, match="Failed to deserialize JSON string"
        ):
            safe_json_deserialize('{"invalid": }')

    def test_deserialize_empty_string(self):
        """Test deserializing empty string."""
        with pytest.raises(
            SerializationError, match="Failed to deserialize JSON string"
        ):
            safe_json_deserialize("")


class TestValidateJsonString:
    """Test validate_json_string function."""

    def test_validate_valid_json(self):
        """Test validating valid JSON."""
        assert validate_json_string('{"valid": true}') is True
        assert validate_json_string("[1, 2, 3]") is True
        assert validate_json_string('"string"') is True
        assert validate_json_string("null") is True

    def test_validate_invalid_json(self):
        """Test validating invalid JSON."""
        assert validate_json_string('{"invalid": }') is False
        assert validate_json_string("[1, 2,]") is False
        assert validate_json_string("undefined") is False
        assert validate_json_string("") is False

    def test_validate_non_string(self):
        """Test validating non-string input."""
        assert validate_json_string(None) is False
        assert validate_json_string(123) is False
        assert validate_json_string({"dict": "input"}) is False
        assert validate_json_string([1, 2, 3]) is False


class TestRoundTripSerialization:
    """Test round-trip serialization scenarios."""

    def test_serialize_deserialize_roundtrip(self):
        """Test that serialize -> deserialize returns original data."""
        # Only test dict types since function now requires dict input
        test_cases = [
            {"simple": "dict"},
            {"complex": {"nested": {"deeply": [1, 2, {"more": "nesting"}]}}},
            {"unicode": "string with unicode 世界"},
            {"numbers": {"int": 42, "float": 3.14}},
            {"booleans": {"true": True, "false": False}},
            {"null_value": None},
        ]

        for original in test_cases:
            serialized = safe_json_serialize(original, 0)
            deserialized = safe_json_deserialize(serialized)
            assert deserialized == original


class TestADKAgentIntegration:
    """Test ADK Agent integration with JSON processing tools."""

    @pytest.fixture
    def adk_agent_with_json_tools(self):
        """Create ADK agent configured with JSON processing tools."""
        agent = Agent(
            model="gemini-2.0-flash",
            name="JsonProcessingAgent",
            instruction="You are a JSON processing agent. Use the available tools to serialize, deserialize, and validate JSON data.",
            description="An agent specialized in JSON data processing, validation, and transformation.",
            tools=[
                safe_json_serialize,
                safe_json_deserialize,
                validate_json_string,
            ],
        )
        return agent

    @pytest.fixture
    def adk_agent_with_validation_tool(self):
        """Create ADK agent configured with JSON validation tool only."""
        agent = Agent(
            model="gemini-2.0-flash",
            name="JsonValidationAgent",
            instruction="You are a JSON validation agent. Use the validate_json_string tool to check if JSON strings are valid.",
            description="An agent specialized in JSON validation.",
            tools=[validate_json_string],
        )
        return agent

    def test_safe_json_serialize_basic_functionality(self):
        """Test safe_json_serialize function directly (non-ADK)."""
        # Test basic serialization
        data = {"name": "test", "value": 42}
        result = safe_json_serialize(data, 0)
        assert result == '{"name": "test", "value": 42}'

        # Test with indentation
        result = safe_json_serialize(data, 2)
        assert '"name": "test"' in result
        assert '"value": 42' in result

        # Test list serialization
        list_data = {"items": [1, 2, 3]}
        result = safe_json_serialize(list_data, 0)
        assert '"items": [1, 2, 3]' in result

    def test_adk_agent_can_serialize_json(self, adk_agent_with_json_tools):
        """Test that ADK agent can successfully serialize JSON data."""
        instruction = (
            'Serialize this data to JSON: {"name": "Alice", "age": 30} with indent 0'
        )

        try:
            response = adk_agent_with_json_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence that serialization occurred
            expected_elements = ["alice", "serialize", "json", "30"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of successful JSON serialization
            assert found_elements >= 2, (
                f"Expected JSON serialization elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed to serialize JSON: {e}")

    def test_safe_json_deserialize_basic_functionality(self):
        """Test safe_json_deserialize function directly (non-ADK)."""
        # Test basic deserialization
        json_str = '{"name": "test", "value": 42}'
        result = safe_json_deserialize(json_str)
        assert result == {"name": "test", "value": 42}

        # Test list deserialization (wrapped in result key)
        json_str = "[1, 2, 3]"
        result = safe_json_deserialize(json_str)
        assert result == {"result": [1, 2, 3]}

        # Test null deserialization
        result = safe_json_deserialize("null")
        assert result == {"result": None}

    def test_adk_agent_can_deserialize_json(self, adk_agent_with_json_tools):
        """Test that ADK agent can successfully deserialize JSON strings."""
        instruction = (
            'Deserialize this JSON string: \'{"product": "laptop", "price": 999}\''
        )

        try:
            response = adk_agent_with_json_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence that deserialization occurred
            expected_elements = ["laptop", "deserialize", "json", "999", "product"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of successful JSON deserialization
            assert found_elements >= 2, (
                f"Expected JSON deserialization elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed to deserialize JSON: {e}")

    def test_validate_json_string_basic_functionality(self):
        """Test validate_json_string function directly (non-ADK)."""
        # Test valid JSON
        assert validate_json_string('{"valid": true}') is True
        assert validate_json_string("[1, 2, 3]") is True
        assert validate_json_string('"string"') is True
        assert validate_json_string("null") is True

        # Test invalid JSON
        assert validate_json_string('{"invalid": }') is False
        assert validate_json_string("[1, 2,]") is False
        assert validate_json_string("undefined") is False
        assert validate_json_string("") is False

    def test_adk_agent_can_validate_json_string(self, adk_agent_with_validation_tool):
        """Test that ADK agent can validate JSON strings."""
        instruction = 'Validate this JSON string: \'{"user": "admin", "permissions": ["read", "write"]}\''

        try:
            response = adk_agent_with_validation_tool.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence that validation occurred
            expected_elements = ["valid", "json", "validate", "user", "admin"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of successful JSON validation
            assert found_elements >= 2, (
                f"Expected JSON validation elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed to validate JSON string: {e}")

    def test_adk_agent_can_handle_invalid_json_validation(
        self, adk_agent_with_validation_tool
    ):
        """Test that ADK agent can handle invalid JSON during validation."""
        instruction = "Validate this invalid JSON string: '{\"invalid\": }'"

        try:
            response = adk_agent_with_validation_tool.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence that validation occurred and found it invalid
            expected_elements = ["invalid", "json", "validate", "false", "not valid"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence that the JSON was identified as invalid
            assert found_elements >= 2, (
                f"Expected invalid JSON identification not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed to handle invalid JSON validation: {e}")

    def test_adk_agent_comprehensive_json_workflow(self, adk_agent_with_json_tools):
        """Test ADK agent performing comprehensive JSON processing workflow."""
        instruction = 'Take this data: {"items": ["apple", "banana"], "count": 2}, serialize it with indent 2, then deserialize it back'

        try:
            response = adk_agent_with_json_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of comprehensive JSON processing
            expected_elements = [
                "serialize",
                "deserialize",
                "apple",
                "banana",
                "count",
                "2",
            ]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of comprehensive JSON processing
            assert found_elements >= 4, (
                f"Expected comprehensive JSON processing elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed comprehensive JSON workflow: {e}")

    def test_adk_agent_error_handling(self, adk_agent_with_json_tools):
        """Test ADK agent error handling with invalid data."""
        instruction = "Serialize this invalid data structure (testing error handling)"

        try:
            response = adk_agent_with_json_tools.run(instruction)

            # The agent should handle the request gracefully
            assert response is not None

            response_str = str(response).lower()

            # Either the agent processed the request or provided some response
            assert len(response_str) > 0

        except Exception as e:
            # Some exceptions are acceptable as they indicate proper error handling
            acceptable_errors = ["type", "invalid", "error", "serialization"]
            error_msg = str(e).lower()

            is_acceptable = any(
                acceptable in error_msg for acceptable in acceptable_errors
            )

            if not is_acceptable:
                pytest.fail(f"Unexpected error type: {e}")

    def test_json_roundtrip_functionality(self):
        """Test JSON roundtrip processing functionality."""
        # Test data that should survive serialization/deserialization
        test_data = {
            "simple": "value",
            "nested": {"key": "value", "number": 42},
            "array": [1, 2, "three"],
            "boolean": True,
            "null_value": None,
        }

        # Serialize then deserialize
        serialized = safe_json_serialize(test_data, 0)
        deserialized = safe_json_deserialize(serialized)

        # Should get back the original data
        assert deserialized == test_data


class TestJsonProcessingCompatibility:
    """Test Google AI compatibility for JSON processing functions."""

    def test_function_signatures_compatibility(self):
        """Test that all JSON functions have Google AI compatible signatures."""
        functions_to_test = [
            safe_json_serialize,
            safe_json_deserialize,
            validate_json_string,
        ]

        for func in functions_to_test:
            sig = inspect.signature(func)

            # Check that no parameters have default values
            for param_name, param in sig.parameters.items():
                assert param.default == inspect.Parameter.empty, (
                    f"Function {func.__name__} parameter {param_name} has default value, "
                    "violating Google AI requirements"
                )

            # Check that return type is specified
            assert sig.return_annotation != inspect.Signature.empty, (
                f"Function {func.__name__} missing return type annotation"
            )

    def test_parameter_types_compatibility(self):
        """Test that parameter types are Google AI compatible."""
        # Test safe_json_serialize
        sig = inspect.signature(safe_json_serialize)
        params = sig.parameters

        assert params["data"].annotation is dict
        assert params["indent"].annotation is int
        assert sig.return_annotation is str

        # Test safe_json_deserialize
        sig = inspect.signature(safe_json_deserialize)
        params = sig.parameters

        assert params["json_string"].annotation is str
        assert sig.return_annotation is dict

        # Test validate_json_string
        sig = inspect.signature(validate_json_string)
        params = sig.parameters

        # This function accepts any type for validation purposes
        assert sig.return_annotation is bool


class TestJsonProcessingIntegrationWithADK:
    """Integration tests combining multiple JSON processing operations with ADK."""

    @pytest.fixture
    def adk_agent_with_all_json_tools(self):
        """Create ADK agent with all JSON processing tools."""
        agent = Agent(
            model="gemini-2.0-flash",
            name="ComprehensiveJsonAgent",
            instruction="You are a comprehensive JSON processing agent. Use the available tools to perform complex JSON operations including serialization, deserialization, and validation.",
            description="An agent capable of comprehensive JSON data processing and validation.",
            tools=[
                safe_json_serialize,
                safe_json_deserialize,
                validate_json_string,
            ],
        )
        return agent

    def test_adk_agent_data_transformation_workflow(
        self, adk_agent_with_all_json_tools
    ):
        """Test ADK agent performing data transformation workflow."""
        instruction = """Process this workflow: 1) Validate JSON string '{"config": {"debug": true, "version": "1.0"}}', 2) If valid, deserialize it, 3) Serialize it back with indent 2"""

        try:
            response = adk_agent_with_all_json_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of complete workflow
            expected_elements = [
                "validate",
                "deserialize",
                "serialize",
                "config",
                "debug",
                "version",
            ]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of complete workflow
            assert found_elements >= 4, (
                f"Expected workflow elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed data transformation workflow: {e}")

    def test_adk_agent_json_quality_check_workflow(self, adk_agent_with_all_json_tools):
        """Test ADK agent performing JSON quality check workflow."""
        instruction = """Check the quality of these JSON strings: 1) '{"valid": "json"}' 2) '{"invalid": }' 3) '[1, 2, 3]' - validate each and report which ones are valid"""

        try:
            response = adk_agent_with_all_json_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of quality checking
            expected_elements = ["valid", "invalid", "json", "check", "validate"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of JSON quality checking
            assert found_elements >= 3, (
                f"Expected quality check elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed JSON quality check workflow: {e}")
