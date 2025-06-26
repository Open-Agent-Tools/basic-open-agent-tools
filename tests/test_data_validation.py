"""Tests for data validation utilities."""

import pytest

from basic_open_agent_tools.data.validation import (
    check_required_fields,
    create_validation_report,
    validate_data_types_simple,
    validate_range_simple,
    validate_schema_simple,
)
from basic_open_agent_tools.exceptions import ValidationError


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

        # Valid array
        data = ["Alice", "Bob", "Charlie"]
        assert validate_schema_simple(data, schema) is True

        # Empty array is valid
        data = []
        assert validate_schema_simple(data, schema) is True

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

        # Wrong type
        with pytest.raises(ValidationError, match="Expected string, got int"):
            validate_schema_simple({"name": 123}, schema)

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
        assert validate_range_simple(25, min_val=18) is True
        assert validate_range_simple(100, min_val=18) is True

    def test_validate_range_simple_only_max(self):
        """Test validation with only maximum bound."""
        assert validate_range_simple(25, max_val=65) is True
        assert validate_range_simple(1, max_val=65) is True

    def test_validate_range_simple_no_bounds(self):
        """Test validation with no bounds."""
        assert validate_range_simple(25) is True
        assert validate_range_simple(-100) is True
        assert validate_range_simple(1000) is True

    def test_validate_range_simple_float_values(self):
        """Test validation with float values."""
        assert validate_range_simple(25.5, min_val=18.0, max_val=65.0) is True
        assert validate_range_simple(3.14, min_val=3, max_val=4) is True

    def test_validate_range_simple_below_minimum(self):
        """Test validation failure below minimum."""
        with pytest.raises(ValidationError, match="Value 10 is below minimum 18"):
            validate_range_simple(10, min_val=18)

    def test_validate_range_simple_above_maximum(self):
        """Test validation failure above maximum."""
        with pytest.raises(ValidationError, match="Value 70 is above maximum 65"):
            validate_range_simple(70, max_val=65)

    def test_validate_range_simple_invalid_types(self):
        """Test with invalid argument types."""
        with pytest.raises(TypeError, match="value must be numeric"):
            validate_range_simple("not numeric")

        with pytest.raises(TypeError, match="min_val must be numeric or None"):
            validate_range_simple(25, min_val="not numeric")

        with pytest.raises(TypeError, match="max_val must be numeric or None"):
            validate_range_simple(25, max_val="not numeric")


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
