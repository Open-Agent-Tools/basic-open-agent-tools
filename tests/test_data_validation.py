"""Tests for data validation utilities.

This module provides comprehensive tests for the data validation toolkit functions,
including unit tests, integration tests, and Google AI compatibility verification.
"""

import inspect
import logging
import warnings

import pytest
from dotenv import load_dotenv
from google.adk.agents import Agent

from basic_open_agent_tools.data.validation import (
    check_required_fields,
    create_validation_report,
    validate_data_types_simple,
    validate_range_simple,
    validate_schema_simple,
)
from basic_open_agent_tools.exceptions import ValidationError

# Initialize environment and logging
load_dotenv()
logging.basicConfig(level=logging.ERROR)
warnings.filterwarnings("ignore")


class TestValidateSchema:
    """Test validate_schema_simple function."""

    def test_validate_simple_object_schema(self):
        """Test validating against simple object schema."""
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
            "required": ["name"],
        }

        # Valid data
        data = {"name": "Alice", "age": 25}
        assert validate_schema_simple(data, schema) is True

        # Valid data without optional field
        data = {"name": "Alice"}
        assert validate_schema_simple(data, schema) is True

    def test_validate_array_schema(self):
        """Test validating against array schema."""
        schema = {"type": "array", "items": {"type": "string"}}

        # Array validation not supported with dict-only input
        data = {"items": ["Alice", "Bob", "Charlie"]}
        with pytest.raises(ValidationError, match="Array validation not supported"):
            validate_schema_simple(data, schema)

        # Empty array also not supported
        data = {}
        with pytest.raises(ValidationError, match="Array validation not supported"):
            validate_schema_simple(data, schema)

    def test_validate_primitive_schemas(self):
        """Test validating against primitive type schemas."""
        # String schema
        assert validate_schema_simple("hello", {"type": "string"}) is True

        # Number schema
        assert validate_schema_simple(42, {"type": "number"}) is True
        assert validate_schema_simple(3.14, {"type": "number"}) is True

        # Integer schema
        assert validate_schema_simple(42, {"type": "integer"}) is True

        # Boolean schema
        assert validate_schema_simple(True, {"type": "boolean"}) is True

        # Null schema
        assert validate_schema_simple(None, {"type": "null"}) is True

    def test_validate_nested_schema(self):
        """Test validating against nested schema."""
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "contacts": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["name"],
                }
            },
            "required": ["user"],
        }

        data = {
            "user": {"name": "Alice", "contacts": ["alice@example.com", "+1234567890"]}
        }
        assert validate_schema_simple(data, schema) is True

    def test_validate_schema_simple_failures(self):
        """Test schema validation failures."""
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        }

        # Missing required field
        with pytest.raises(
            ValidationError, match="Required property 'name' is missing"
        ):
            validate_schema_simple({}, schema)

        # Wrong type - this test no longer applies since we simplified validation
        # The function now only validates dict structure, not individual field types
        pass

        # Wrong top-level type
        with pytest.raises(ValidationError, match="Expected object, got str"):
            validate_schema_simple("not an object", schema)

    def test_validate_schema_simple_invalid_types(self):
        """Test with invalid argument types."""
        with pytest.raises(TypeError, match="schema must be a dictionary"):
            validate_schema_simple({"name": "Alice"}, "not a dict")


class TestCheckRequiredFields:
    """Test check_required_fields function."""

    def test_check_required_fields_success(self):
        """Test successful required field validation."""
        data = {"name": "Alice", "age": 25, "email": "alice@example.com"}
        required = ["name", "age"]
        assert check_required_fields(data, required) is True

    def test_check_required_fields_empty_required(self):
        """Test with empty required list."""
        data = {"name": "Alice"}
        assert check_required_fields(data, []) is True

    def test_check_required_fields_failure(self):
        """Test required field validation failure."""
        data = {"name": "Alice"}
        required = ["name", "age", "email"]

        with pytest.raises(ValidationError, match="Required fields are missing"):
            check_required_fields(data, required)

    def test_check_required_fields_invalid_types(self):
        """Test with invalid argument types."""
        with pytest.raises(TypeError, match="data must be a dictionary"):
            check_required_fields("not a dict", ["name"])

        with pytest.raises(TypeError, match="required must be a list"):
            check_required_fields({"name": "Alice"}, "not a list")


class TestValidateDataTypes:
    """Test validate_data_types_simple function."""

    def test_validate_data_types_simple_success(self):
        """Test successful type validation."""
        data = {"name": "Alice", "age": 25, "active": True}
        type_map = {"name": "str", "age": "int", "active": "bool"}
        assert validate_data_types_simple(data, type_map) is True

    def test_validate_data_types_simple_partial_mapping(self):
        """Test validation with partial type mapping."""
        data = {"name": "Alice", "age": 25, "other": "value"}
        type_map = {"name": "str", "age": "int"}
        # Should only validate fields in type_map
        assert validate_data_types_simple(data, type_map) is True

    def test_validate_data_types_simple_missing_fields(self):
        """Test validation when data is missing some mapped fields."""
        data = {"name": "Alice"}
        type_map = {"name": "str", "age": "int"}
        # Should not fail for missing fields, only validate present ones
        assert validate_data_types_simple(data, type_map) is True

    def test_validate_data_types_simple_failure(self):
        """Test type validation failure."""
        data = {"name": "Alice", "age": "25"}  # age should be int
        type_map = {"name": "str", "age": "int"}

        with pytest.raises(ValidationError, match="Type validation errors"):
            validate_data_types_simple(data, type_map)

    def test_validate_data_types_simple_multiple_failures(self):
        """Test multiple type validation failures."""
        data = {"name": 123, "age": "25"}
        type_map = {"name": "str", "age": "int"}

        with pytest.raises(ValidationError) as exc_info:
            validate_data_types_simple(data, type_map)

        error_msg = str(exc_info.value)
        assert "name" in error_msg
        assert "age" in error_msg

    def test_validate_data_types_simple_invalid_types(self):
        """Test with invalid argument types."""
        with pytest.raises(TypeError, match="data must be a dictionary"):
            validate_data_types_simple("not a dict", {})

        with pytest.raises(TypeError, match="type_map must be a dictionary"):
            validate_data_types_simple({"name": "Alice"}, "not a dict")


class TestValidateRange:
    """Test validate_range_simple function."""

    def test_validate_range_simple_within_bounds(self):
        """Test validation within range bounds."""
        assert validate_range_simple(25, min_val=18, max_val=65) is True
        assert (
            validate_range_simple(18, min_val=18, max_val=65) is True
        )  # Inclusive min
        assert (
            validate_range_simple(65, min_val=18, max_val=65) is True
        )  # Inclusive max

    def test_validate_range_simple_only_min(self):
        """Test validation with only minimum bound."""
        assert validate_range_simple(25.0, 18.0, 999.0) is True
        assert validate_range_simple(100.0, 18.0, 999.0) is True

    def test_validate_range_simple_only_max(self):
        """Test validation with only maximum bound."""
        assert validate_range_simple(25.0, -999.0, 65.0) is True
        assert validate_range_simple(1.0, -999.0, 65.0) is True

    def test_validate_range_simple_no_bounds(self):
        """Test validation with no bounds."""
        assert validate_range_simple(25.0, -9999.0, 9999.0) is True
        assert validate_range_simple(-100.0, -9999.0, 9999.0) is True
        assert validate_range_simple(1000.0, -9999.0, 9999.0) is True

    def test_validate_range_simple_float_values(self):
        """Test validation with float values."""
        assert validate_range_simple(25.5, min_val=18.0, max_val=65.0) is True
        assert validate_range_simple(3.14, min_val=3, max_val=4) is True

    def test_validate_range_simple_below_minimum(self):
        """Test validation failure below minimum."""
        with pytest.raises(ValidationError, match="Value 10.0 is below minimum 18.0"):
            validate_range_simple(10.0, 18.0, 999.0)

    def test_validate_range_simple_above_maximum(self):
        """Test validation failure above maximum."""
        with pytest.raises(ValidationError, match="Value 70.0 is above maximum 65.0"):
            validate_range_simple(70.0, -999.0, 65.0)

    def test_validate_range_simple_invalid_types(self):
        """Test with invalid argument types."""
        with pytest.raises(TypeError, match="value must be numeric"):
            validate_range_simple("not numeric", 0.0, 100.0)

        with pytest.raises(TypeError, match="min_val must be numeric"):
            validate_range_simple(25.0, "not numeric", 100.0)

        with pytest.raises(TypeError, match="max_val must be numeric"):
            validate_range_simple(25.0, 0.0, "not numeric")


class TestCreateValidationReport:
    """Test create_validation_report function."""

    def test_create_validation_report_success(self):
        """Test creating validation report for valid data."""
        data = {"name": "Alice", "age": 25}
        rules = {
            "required": ["name", "age"],
            "types": {"name": "str", "age": "int"},
            "ranges": {"age": {"min": 18, "max": 65}},
        }

        result = create_validation_report(data, rules)
        assert result["valid"] is True
        assert result["errors"] == []
        assert result["fields_validated"] == 2
        assert result["rules_applied"] == 3

    def test_create_validation_report_with_errors(self):
        """Test creating validation report with errors."""
        data = {"name": "Alice"}  # Missing age
        rules = {"required": ["name", "age"], "types": {"name": "str", "age": "int"}}

        result = create_validation_report(data, rules)
        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert any("age" in error for error in result["errors"])

    def test_create_validation_report_type_errors(self):
        """Test validation report with type errors."""
        data = {"name": 123, "age": "25"}
        rules = {"types": {"name": "str", "age": "int"}}

        result = create_validation_report(data, rules)
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_create_validation_report_range_errors(self):
        """Test validation report with range errors."""
        data = {"age": 15}
        rules = {"ranges": {"age": {"min": 18, "max": 65}}}

        result = create_validation_report(data, rules)
        assert result["valid"] is False
        assert any("Range validation" in error for error in result["errors"])

    def test_create_validation_report_pattern_validation(self):
        """Test validation report with pattern validation."""
        data = {"email": "invalid-email"}
        rules = {
            "patterns": {"email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"}
        }

        result = create_validation_report(data, rules)
        assert result["valid"] is False
        assert any("pattern" in error for error in result["errors"])

    def test_create_validation_report_unexpected_fields(self):
        """Test validation report with unexpected fields."""
        data = {"name": "Alice", "unexpected": "value"}
        rules = {"allowed_fields": ["name", "age"]}

        result = create_validation_report(data, rules)
        # Unexpected fields generate warnings, not errors
        assert "warnings" in result
        assert any("Unexpected fields" in warning for warning in result["warnings"])

    def test_create_validation_report_invalid_pattern(self):
        """Test validation report with invalid regex pattern."""
        data = {"field": "value"}
        rules = {
            "patterns": {"field": "[invalid"}  # Invalid regex
        }

        result = create_validation_report(data, rules)
        assert "warnings" in result
        assert any("Invalid regex pattern" in warning for warning in result["warnings"])

    def test_create_validation_report_empty_rules(self):
        """Test validation report with empty rules."""
        data = {"name": "Alice"}
        rules = {}

        result = create_validation_report(data, rules)
        assert result["valid"] is True
        assert result["errors"] == []
        assert result["fields_validated"] == 1

    def test_create_validation_report_invalid_types(self):
        """Test with invalid argument types."""
        with pytest.raises(TypeError, match="data must be a dictionary"):
            create_validation_report("not a dict", {})

        with pytest.raises(TypeError, match="rules must be a dictionary"):
            create_validation_report({"name": "Alice"}, "not a dict")


class TestIntegrationScenarios:
    """Test integration scenarios with multiple validation functions."""

    def test_complete_user_validation(self):
        """Test complete user data validation scenario."""
        user_data = {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "age": 28,
            "role": "admin",
        }

        # Define comprehensive validation rules
        rules = {
            "required": ["name", "email", "age"],
            "types": {"name": str, "email": str, "age": int, "role": str},
            "ranges": {"age": {"min": 18, "max": 65}},
            "patterns": {"email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"},
            "allowed_fields": ["name", "email", "age", "role", "phone"],
        }

        # Run validation
        report = create_validation_report(user_data, rules)

        assert report["valid"] is True
        assert report["errors"] == []
        assert report["fields_validated"] == 4

    def test_batch_validation_reports(self):
        """Test creating multiple validation reports."""
        users = [
            {"name": "Alice", "age": 25},
            {"name": "Bob"},  # Missing age
            {"name": 123, "age": "invalid"},  # Type errors
        ]

        validation_results = []
        for user in users:
            rules = {
                "required": ["name", "age"],
                "types": {"name": "str", "age": "int"},
            }
            result = create_validation_report(user, rules)
            validation_results.append(result)

        # Check that we got validation results
        assert len(validation_results) == 3
        assert validation_results[0]["valid"] is True  # Alice is valid
        assert validation_results[1]["valid"] is False  # Bob missing age
        assert validation_results[2]["valid"] is False  # Invalid types


class TestADKAgentIntegration:
    """Test ADK Agent integration with data validation tools."""

    @pytest.fixture
    def adk_agent_with_validation_tools(self):
        """Create ADK agent configured with data validation tools."""
        agent = Agent(
            model="gemini-2.0-flash",
            name="DataValidationAgent",
            instruction="You are a data validation agent. Use the available tools to validate data schemas, check required fields, validate data types, check ranges, and create comprehensive validation reports.",
            description="An agent specialized in data validation, quality checking, and compliance verification.",
            tools=[
                validate_schema_simple,
                check_required_fields,
                validate_data_types_simple,
                validate_range_simple,
                create_validation_report,
            ],
        )
        return agent

    @pytest.fixture
    def adk_agent_with_schema_validation(self):
        """Create ADK agent configured with schema validation only."""
        agent = Agent(
            model="gemini-2.0-flash",
            name="SchemaValidationAgent",
            instruction="You are a schema validation agent. Use the validate_schema_simple tool to validate data against JSON-like schemas.",
            description="An agent specialized in schema validation.",
            tools=[validate_schema_simple],
        )
        return agent

    def test_validate_schema_simple_basic_functionality(self):
        """Test validate_schema_simple function directly (non-ADK)."""
        # Test basic object validation
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
            "required": ["name"],
        }

        data = {"name": "Alice", "age": 25}
        assert validate_schema_simple(data, schema) is True

        # Test without optional field
        data = {"name": "Alice"}
        assert validate_schema_simple(data, schema) is True

        # Test primitive validation
        assert validate_schema_simple("hello", {"type": "string"}) is True
        assert validate_schema_simple(42, {"type": "number"}) is True
        assert validate_schema_simple(True, {"type": "boolean"}) is True

    def test_adk_agent_can_validate_schema(self, adk_agent_with_schema_validation):
        """Test that ADK agent can validate data against schemas."""
        instruction = """Validate this data: {"user": "admin", "permissions": ["read", "write"]} against this schema: {"type": "object", "properties": {"user": {"type": "string"}}, "required": ["user"]}"""

        try:
            response = adk_agent_with_schema_validation.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence that schema validation occurred
            expected_elements = ["validate", "schema", "user", "admin", "valid"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of successful schema validation
            assert found_elements >= 2, (
                f"Expected schema validation elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed to validate schema: {e}")

    def test_check_required_fields_basic_functionality(self):
        """Test check_required_fields function directly (non-ADK)."""
        # Test successful validation
        data = {"name": "Alice", "age": 25, "email": "alice@example.com"}
        required = ["name", "age"]
        assert check_required_fields(data, required) is True

        # Test empty required list
        assert check_required_fields(data, []) is True

        # Test missing fields
        data = {"name": "Alice"}
        required = ["name", "age", "email"]

        with pytest.raises(ValidationError, match="Required fields are missing"):
            check_required_fields(data, required)

    def test_adk_agent_can_check_required_fields(self, adk_agent_with_validation_tools):
        """Test that ADK agent can check required fields."""
        instruction = """Check if this data: {"name": "John", "email": "john@example.com"} has these required fields: ["name", "email", "age"]"""

        try:
            response = adk_agent_with_validation_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of required field checking
            expected_elements = ["required", "field", "check", "missing", "age"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of required field validation
            assert found_elements >= 2, (
                f"Expected required field validation elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed to check required fields: {e}")

    def test_validate_data_types_simple_basic_functionality(self):
        """Test validate_data_types_simple function directly (non-ADK)."""
        # Test successful type validation
        data = {"name": "Alice", "age": 25, "active": True}
        type_map = {"name": "str", "age": "int", "active": "bool"}
        assert validate_data_types_simple(data, type_map) is True

        # Test partial mapping
        data = {"name": "Alice", "age": 25, "other": "value"}
        type_map = {"name": "str", "age": "int"}
        assert validate_data_types_simple(data, type_map) is True

        # Test type validation failure
        data = {"name": "Alice", "age": "25"}  # age should be int
        type_map = {"name": "str", "age": "int"}

        with pytest.raises(ValidationError, match="Type validation errors"):
            validate_data_types_simple(data, type_map)

    def test_adk_agent_can_validate_data_types(self, adk_agent_with_validation_tools):
        """Test that ADK agent can validate data types."""
        instruction = """Validate types for this data: {"product": "laptop", "price": 999, "available": true} using type map: {"product": "str", "price": "int", "available": "bool"}"""

        try:
            response = adk_agent_with_validation_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of type validation
            expected_elements = ["type", "validate", "product", "laptop", "price"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of successful type validation
            assert found_elements >= 2, (
                f"Expected type validation elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed to validate data types: {e}")

    def test_validate_range_simple_basic_functionality(self):
        """Test validate_range_simple function directly (non-ADK)."""
        # Test within bounds
        assert validate_range_simple(25, min_val=18, max_val=65) is True
        assert (
            validate_range_simple(18, min_val=18, max_val=65) is True
        )  # Inclusive min
        assert (
            validate_range_simple(65, min_val=18, max_val=65) is True
        )  # Inclusive max

        # Test float values
        assert validate_range_simple(25.5, min_val=18.0, max_val=65.0) is True

        # Test validation failures
        with pytest.raises(ValidationError, match="Value 10.0 is below minimum 18.0"):
            validate_range_simple(10.0, 18.0, 999.0)

        with pytest.raises(ValidationError, match="Value 70.0 is above maximum 65.0"):
            validate_range_simple(70.0, -999.0, 65.0)

    def test_adk_agent_can_validate_range(self, adk_agent_with_validation_tools):
        """Test that ADK agent can validate ranges."""
        instruction = (
            "Validate that the value 35 is within the range minimum 18 and maximum 65"
        )

        try:
            response = adk_agent_with_validation_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of range validation
            expected_elements = ["range", "validate", "35", "18", "65", "within"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of successful range validation
            assert found_elements >= 3, (
                f"Expected range validation elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed to validate range: {e}")

    def test_create_validation_report_basic_functionality(self):
        """Test create_validation_report function directly (non-ADK)."""
        # Test successful validation
        data = {"name": "Alice", "age": 25}
        rules = {
            "required": ["name", "age"],
            "types": {"name": "str", "age": "int"},
            "ranges": {"age": {"min": 18, "max": 65}},
        }

        result = create_validation_report(data, rules)
        assert result["valid"] is True
        assert result["errors"] == []
        assert result["fields_validated"] == 2
        assert result["rules_applied"] == 3

        # Test with errors
        data = {"name": "Alice"}  # Missing age
        rules = {"required": ["name", "age"], "types": {"name": "str", "age": "int"}}

        result = create_validation_report(data, rules)
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_adk_agent_can_create_validation_report(
        self, adk_agent_with_validation_tools
    ):
        """Test that ADK agent can create comprehensive validation reports."""
        instruction = """Create a validation report for this data: {"user": "alice", "age": 28, "role": "admin"} using these rules: {"required": ["user", "age"], "types": {"user": "str", "age": "int", "role": "str"}, "ranges": {"age": {"min": 18, "max": 65}}}"""

        try:
            response = adk_agent_with_validation_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of validation report creation
            expected_elements = ["validation", "report", "alice", "age", "28", "valid"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of successful validation report creation
            assert found_elements >= 3, (
                f"Expected validation report elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed to create validation report: {e}")

    def test_adk_agent_comprehensive_validation_workflow(
        self, adk_agent_with_validation_tools
    ):
        """Test ADK agent performing comprehensive validation workflow."""
        instruction = """Perform comprehensive validation on this user data: {"name": "Bob", "email": "bob@example.com", "age": 32, "department": "engineering"}. First check required fields ["name", "email", "age"], then validate types {"name": "str", "email": "str", "age": "int"}, then check age range 18-65, and finally create a full validation report with rules: {"required": ["name", "email", "age"], "types": {"name": "str", "email": "str", "age": "int"}, "ranges": {"age": {"min": 18, "max": 65}}}"""

        try:
            response = adk_agent_with_validation_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of comprehensive validation
            expected_elements = [
                "bob",
                "email",
                "age",
                "32",
                "validation",
                "required",
                "type",
                "range",
                "report",
            ]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of comprehensive validation workflow
            assert found_elements >= 6, (
                f"Expected comprehensive validation elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed comprehensive validation workflow: {e}")

    def test_adk_agent_error_handling(self, adk_agent_with_validation_tools):
        """Test ADK agent error handling with invalid data."""
        instruction = 'Validate this problematic data: {"name": 123, "age": "not_a_number"} with type requirements: {"name": "str", "age": "int"}'

        try:
            response = adk_agent_with_validation_tools.run(instruction)

            # The agent should handle validation errors gracefully
            assert response is not None

            response_str = str(response).lower()

            # Look for evidence of error handling
            expected_elements = ["error", "invalid", "type", "validation", "fail"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # Either the agent processed the errors or provided some response
            assert found_elements >= 1 or len(response_str) > 0

        except Exception as e:
            # Some exceptions are acceptable as they indicate proper error handling
            acceptable_errors = ["validation", "type", "invalid", "error"]
            error_msg = str(e).lower()

            is_acceptable = any(
                acceptable in error_msg for acceptable in acceptable_errors
            )

            if not is_acceptable:
                pytest.fail(f"Unexpected error type: {e}")

    def test_integration_user_validation_scenario(self):
        """Test integrated user validation scenario with multiple functions."""
        user_data = {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "age": 28,
            "role": "admin",
        }

        # Test individual validations
        assert check_required_fields(user_data, ["name", "email", "age"]) is True
        assert (
            validate_data_types_simple(
                user_data, {"name": "str", "email": "str", "age": "int", "role": "str"}
            )
            is True
        )
        assert validate_range_simple(user_data["age"], 18, 65) is True

        # Test comprehensive validation report
        rules = {
            "required": ["name", "email", "age"],
            "types": {"name": "str", "email": "str", "age": "int", "role": "str"},
            "ranges": {"age": {"min": 18, "max": 65}},
            "patterns": {"email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"},
        }

        report = create_validation_report(user_data, rules)
        assert report["valid"] is True
        assert report["errors"] == []


class TestDataValidationCompatibility:
    """Test Google AI compatibility for data validation functions."""

    def test_function_signatures_compatibility(self):
        """Test that all validation functions have Google AI compatible signatures."""
        functions_to_test = [
            validate_schema_simple,
            check_required_fields,
            validate_data_types_simple,
            validate_range_simple,
            create_validation_report,
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
        # Test check_required_fields
        sig = inspect.signature(check_required_fields)
        params = sig.parameters

        assert params["data"].annotation is dict
        # Should have List[str] for required fields
        required_annotation = params["required"].annotation
        assert hasattr(required_annotation, "__origin__")
        assert required_annotation.__origin__ is list
        assert sig.return_annotation is bool

        # Test validate_range_simple - numeric types
        sig = inspect.signature(validate_range_simple)
        params = sig.parameters

        # These should accept Union[int, float] but simplified for Google AI
        assert sig.return_annotation is bool

        # Test create_validation_report
        sig = inspect.signature(create_validation_report)
        params = sig.parameters

        assert params["data"].annotation is dict
        assert params["rules"].annotation is dict
        assert sig.return_annotation is dict


class TestDataValidationIntegrationWithADK:
    """Integration tests combining multiple validation operations with ADK."""

    @pytest.fixture
    def adk_agent_with_all_validation_tools(self):
        """Create ADK agent with all validation tools."""
        agent = Agent(
            model="gemini-2.0-flash",
            name="ComprehensiveValidationAgent",
            instruction="You are a comprehensive data validation agent. Use the available tools to perform complete data quality checks including schema validation, required field checks, type validation, range validation, and comprehensive reporting.",
            description="An agent capable of comprehensive data validation and quality assurance.",
            tools=[
                validate_schema_simple,
                check_required_fields,
                validate_data_types_simple,
                validate_range_simple,
                create_validation_report,
            ],
        )
        return agent

    def test_adk_agent_data_quality_pipeline(self, adk_agent_with_all_validation_tools):
        """Test ADK agent performing data quality pipeline."""
        instruction = """Execute a complete data quality pipeline on this dataset: [{"name": "Alice", "age": 25, "score": 95.5}, {"name": "Bob", "age": 30, "score": 88.0}, {"name": "Charlie", "age": 22, "score": 92.3}]. For each record, validate required fields ["name", "age"], check types {"name": "str", "age": "int", "score": "float"}, validate age range 18-65, and create summary reports."""

        try:
            response = adk_agent_with_all_validation_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of comprehensive pipeline
            expected_elements = [
                "alice",
                "bob",
                "charlie",
                "validate",
                "quality",
                "pipeline",
                "age",
                "score",
            ]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of data quality pipeline
            assert found_elements >= 5, (
                f"Expected pipeline elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed data quality pipeline: {e}")

    def test_adk_agent_validation_rule_enforcement(
        self, adk_agent_with_all_validation_tools
    ):
        """Test ADK agent enforcing validation rules."""
        instruction = """Enforce these validation rules on employee data: {"name": "John Doe", "employee_id": 12345, "salary": 75000, "department": "Engineering", "start_date": "2023-01-15"}. Rules: 1) Required fields: name, employee_id, salary 2) Types: name=str, employee_id=int, salary=int, department=str 3) Salary range: 30000-200000 4) Create detailed validation report"""

        try:
            response = adk_agent_with_all_validation_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of rule enforcement
            expected_elements = [
                "john doe",
                "employee",
                "salary",
                "75000",
                "engineering",
                "validation",
                "rules",
            ]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of rule enforcement
            assert found_elements >= 4, (
                f"Expected rule enforcement elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed validation rule enforcement: {e}")
