"""Tests for basic_open_agent_tools.data.validation module."""

import pytest

from basic_open_agent_tools.data.validation import (
    check_required_fields,
    check_required_fields_simple,
    create_validation_report,
    create_validation_report_simple,
    validate_data_types_simple,
    validate_range_simple,
    validate_schema_simple,
)
from basic_open_agent_tools.exceptions import ValidationError


class TestValidateSchemaSimple:
    """Test cases for validate_schema_simple function."""

    def test_valid_object_schema(self) -> None:
        """Test validation of valid object against schema."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"},
            },
        }
        data = {"name": "Alice", "age": 30}

        result = validate_schema_simple(data, schema)
        assert result is True

    def test_simple_object_schema(self) -> None:
        """Test validation with minimal schema."""
        schema = {"type": "object"}
        data = {"any": "value"}

        result = validate_schema_simple(data, schema)
        assert result is True

    def test_schema_with_required_fields(self) -> None:
        """Test schema validation with required fields."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
            },
            "required": ["name", "email"],
        }
        data = {"name": "Alice", "email": "alice@example.com"}

        result = validate_schema_simple(data, schema)
        assert result is True

    def test_nested_object_schema(self) -> None:
        """Test validation of nested objects."""
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "details": {
                            "type": "object",
                            "properties": {"age": {"type": "number"}},
                        },
                    },
                },
            },
        }
        data = {
            "user": {
                "name": "Alice",
                "details": {"age": 30},
            }
        }

        result = validate_schema_simple(data, schema)
        assert result is True

    def test_invalid_schema_type_error(self) -> None:
        """Test error handling for invalid schema type."""
        with pytest.raises(TypeError, match="schema_definition must be a dictionary"):
            validate_schema_simple({"data": "value"}, "invalid_schema")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="schema_definition must be a dictionary"):
            validate_schema_simple({"data": "value"}, ["not", "dict"])  # type: ignore[arg-type]

    def test_data_type_mismatch(self) -> None:
        """Test validation failure when data type doesn't match schema."""
        schema = {"type": "object"}

        # Non-dict data should fail for object schema
        with pytest.raises(ValidationError, match="Expected object, got"):
            validate_schema_simple(["not", "a", "dict"], schema)  # type: ignore[arg-type]

        with pytest.raises(ValidationError, match="Expected object, got"):
            validate_schema_simple("string", schema)  # type: ignore[arg-type]

    def test_missing_required_fields(self) -> None:
        """Test validation failure for missing required fields."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
            },
            "required": ["name", "email"],
        }

        # Missing email field
        with pytest.raises(
            ValidationError, match="Required property 'email' is missing"
        ):
            validate_schema_simple({"name": "Alice"}, schema)

        # Missing both fields
        with pytest.raises(
            ValidationError, match="Required property 'name' is missing"
        ):
            validate_schema_simple({}, schema)

    def test_array_schema_not_supported(self) -> None:
        """Test that array schemas are not supported."""
        schema = {"type": "array"}
        data = {"key": "value"}

        with pytest.raises(ValidationError, match="Array validation not supported"):
            validate_schema_simple(data, schema)

    def test_empty_schema(self) -> None:
        """Test validation with empty schema."""
        schema = {}
        data = {"any": "data"}

        # Empty schema should pass (no validation rules)
        result = validate_schema_simple(data, schema)
        assert result is True

    def test_schema_without_type(self) -> None:
        """Test schema without type specification."""
        schema = {"properties": {"name": {"type": "string"}}}
        data = {"name": "Alice"}

        # Schema without type should pass (no type validation)
        result = validate_schema_simple(data, schema)
        assert result is True

    def test_extra_properties_allowed(self) -> None:
        """Test that extra properties not in schema are allowed."""
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
        }
        data = {"name": "Alice", "extra": "allowed"}

        result = validate_schema_simple(data, schema)
        assert result is True


class TestCheckRequiredFields:
    """Test cases for check_required_fields function."""

    def test_all_required_fields_present(self) -> None:
        """Test when all required fields are present."""
        data = {"name": "Alice", "age": 30, "email": "alice@example.com"}
        required = ["name", "age"]

        result = check_required_fields(data, required)
        assert result is True

    def test_empty_required_list(self) -> None:
        """Test with empty required fields list."""
        data = {"name": "Alice"}
        required = []

        result = check_required_fields(data, required)
        assert result is True

    def test_empty_data_empty_required(self) -> None:
        """Test with empty data and empty required fields."""
        data = {}
        required = []

        result = check_required_fields(data, required)
        assert result is True

    def test_single_missing_field(self) -> None:
        """Test when single required field is missing."""
        data = {"name": "Alice"}
        required = ["name", "age"]

        with pytest.raises(
            ValidationError, match="Required fields are missing: \\['age'\\]"
        ):
            check_required_fields(data, required)

    def test_multiple_missing_fields(self) -> None:
        """Test when multiple required fields are missing."""
        data = {"name": "Alice"}
        required = ["name", "age", "email", "phone"]

        with pytest.raises(
            ValidationError,
            match="Required fields are missing: \\['age', 'email', 'phone'\\]",
        ):
            check_required_fields(data, required)

    def test_all_fields_missing(self) -> None:
        """Test when all required fields are missing."""
        data = {"other": "value"}
        required = ["name", "age"]

        with pytest.raises(
            ValidationError, match="Required fields are missing: \\['name', 'age'\\]"
        ):
            check_required_fields(data, required)

    def test_invalid_data_type(self) -> None:
        """Test error handling for invalid data type."""
        required = ["name"]

        with pytest.raises(TypeError, match="data must be a dictionary"):
            check_required_fields(["not", "dict"], required)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="data must be a dictionary"):
            check_required_fields("string", required)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="data must be a dictionary"):
            check_required_fields(None, required)  # type: ignore[arg-type]

    def test_invalid_required_type(self) -> None:
        """Test error handling for invalid required type."""
        data = {"name": "Alice"}

        with pytest.raises(TypeError, match="required must be a list"):
            check_required_fields(data, {"not": "list"})  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="required must be a list"):
            check_required_fields(data, "string")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="required must be a list"):
            check_required_fields(data, None)  # type: ignore[arg-type]

    def test_field_values_with_various_types(self) -> None:
        """Test that field values can be any type."""
        data = {
            "string": "value",
            "number": 42,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
        }
        required = ["string", "number", "boolean", "null", "list", "dict"]

        result = check_required_fields(data, required)
        assert result is True


class TestValidateDataTypesSimple:
    """Test cases for validate_data_types_simple function."""

    def test_all_types_match(self) -> None:
        """Test when all field types match expectations."""
        data = {
            "name": "Alice",
            "age": 30,
            "height": 5.6,
            "active": True,
            "tags": ["user", "premium"],
            "metadata": {"created": "2023-01-01"},
        }
        type_map = {
            "name": "str",
            "age": "int",
            "height": "float",
            "active": "bool",
            "tags": "list",
            "metadata": "dict",
        }

        result = validate_data_types_simple(data, type_map)
        assert result is True

    def test_partial_type_validation(self) -> None:
        """Test validation when only some fields are in type_map."""
        data = {"name": "Alice", "age": 30, "extra": "ignored"}
        type_map = {"name": "str", "age": "int"}

        result = validate_data_types_simple(data, type_map)
        assert result is True

    def test_empty_type_map(self) -> None:
        """Test with empty type map."""
        data = {"any": "data"}
        type_map = {}

        result = validate_data_types_simple(data, type_map)
        assert result is True

    def test_field_not_in_data(self) -> None:
        """Test when type_map has fields not in data."""
        data = {"name": "Alice"}
        type_map = {"name": "str", "missing_field": "int"}

        # Should not fail for missing fields (only validates present fields)
        result = validate_data_types_simple(data, type_map)
        assert result is True

    def test_single_type_mismatch(self) -> None:
        """Test when single field type doesn't match."""
        data = {"name": "Alice", "age": "30"}  # age is string, not int
        type_map = {"name": "str", "age": "int"}

        with pytest.raises(
            ValidationError,
            match="Type validation errors: Field 'age': expected int, got str",
        ):
            validate_data_types_simple(data, type_map)

    def test_multiple_type_mismatches(self) -> None:
        """Test when multiple field types don't match."""
        data = {"name": 123, "age": "30", "active": "true"}
        type_map = {"name": "str", "age": "int", "active": "bool"}

        with pytest.raises(ValidationError) as exc_info:
            validate_data_types_simple(data, type_map)

        error_msg = str(exc_info.value)
        assert "Field 'name': expected str, got int" in error_msg
        assert "Field 'age': expected int, got str" in error_msg
        assert "Field 'active': expected bool, got str" in error_msg

    def test_invalid_type_name(self) -> None:
        """Test behavior with invalid type name in type_map."""
        data = {"field": "value"}
        type_map = {"field": "invalid_type"}

        # Should not fail when type name is not in type_mapping
        result = validate_data_types_simple(data, type_map)
        assert result is True

    def test_numeric_type_variations(self) -> None:
        """Test numeric type validation variations."""
        # int can be validated as float (Python int is instance of numbers)
        data = {"value": 42}
        type_map = {"value": "int"}

        result = validate_data_types_simple(data, type_map)
        assert result is True

    def test_invalid_data_type(self) -> None:
        """Test error handling for invalid data type."""
        type_map = {"field": "str"}

        with pytest.raises(TypeError, match="data must be a dictionary"):
            validate_data_types_simple(["not", "dict"], type_map)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="data must be a dictionary"):
            validate_data_types_simple("string", type_map)  # type: ignore[arg-type]

    def test_invalid_type_map_type(self) -> None:
        """Test error handling for invalid type_map type."""
        data = {"field": "value"}

        with pytest.raises(TypeError, match="type_map must be a dictionary"):
            validate_data_types_simple(data, ["not", "dict"])  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="type_map must be a dictionary"):
            validate_data_types_simple(data, "string")  # type: ignore[arg-type]

    def test_supported_type_names(self) -> None:
        """Test all supported type names."""
        data = {
            "str_field": "string",
            "int_field": 42,
            "float_field": 3.14,
            "bool_field": True,
            "list_field": [1, 2, 3],
            "dict_field": {"key": "value"},
        }
        type_map = {
            "str_field": "str",
            "int_field": "int",
            "float_field": "float",
            "bool_field": "bool",
            "list_field": "list",
            "dict_field": "dict",
        }

        result = validate_data_types_simple(data, type_map)
        assert result is True


class TestValidateRangeSimple:
    """Test cases for validate_range_simple function."""

    def test_value_within_range(self) -> None:
        """Test when value is within the specified range."""
        assert validate_range_simple(5.0, 1.0, 10.0) is True
        assert validate_range_simple(1.0, 1.0, 10.0) is True  # Boundary: min
        assert validate_range_simple(10.0, 1.0, 10.0) is True  # Boundary: max
        assert validate_range_simple(5.5, 1.0, 10.0) is True  # Float

    def test_integer_values(self) -> None:
        """Test range validation with integer values."""
        assert validate_range_simple(5, 1, 10) is True
        assert validate_range_simple(1, 1, 10) is True
        assert validate_range_simple(10, 1, 10) is True

    def test_mixed_int_float_values(self) -> None:
        """Test range validation with mixed int/float values."""
        assert validate_range_simple(5, 1.0, 10.0) is True
        assert validate_range_simple(5.0, 1, 10) is True
        assert validate_range_simple(5.5, 1, 10.0) is True

    def test_negative_ranges(self) -> None:
        """Test range validation with negative values."""
        assert validate_range_simple(-5.0, -10.0, -1.0) is True
        assert validate_range_simple(0.0, -10.0, 10.0) is True
        assert validate_range_simple(-1.0, -10.0, 10.0) is True

    def test_value_below_minimum(self) -> None:
        """Test when value is below minimum."""
        with pytest.raises(ValidationError, match="Value 0.5 is below minimum 1.0"):
            validate_range_simple(0.5, 1.0, 10.0)

        with pytest.raises(ValidationError, match="Value -5 is below minimum 0"):
            validate_range_simple(-5, 0, 10)

    def test_value_above_maximum(self) -> None:
        """Test when value is above maximum."""
        with pytest.raises(ValidationError, match="Value 15.0 is above maximum 10.0"):
            validate_range_simple(15.0, 1.0, 10.0)

        with pytest.raises(ValidationError, match="Value 100 is above maximum 50"):
            validate_range_simple(100, 1, 50)

    def test_invalid_value_type(self) -> None:
        """Test error handling for invalid value type."""
        with pytest.raises(TypeError, match="value must be numeric"):
            validate_range_simple("5", 1.0, 10.0)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="value must be numeric"):
            validate_range_simple(None, 1.0, 10.0)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="value must be numeric"):
            validate_range_simple([5], 1.0, 10.0)  # type: ignore[arg-type]

    def test_invalid_min_val_type(self) -> None:
        """Test error handling for invalid min_val type."""
        with pytest.raises(TypeError, match="min_val must be numeric"):
            validate_range_simple(5.0, "1", 10.0)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="min_val must be numeric"):
            validate_range_simple(5.0, None, 10.0)  # type: ignore[arg-type]

    def test_invalid_max_val_type(self) -> None:
        """Test error handling for invalid max_val type."""
        with pytest.raises(TypeError, match="max_val must be numeric"):
            validate_range_simple(5.0, 1.0, "10")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="max_val must be numeric"):
            validate_range_simple(5.0, 1.0, None)  # type: ignore[arg-type]

    def test_edge_case_equal_min_max(self) -> None:
        """Test when min and max are equal."""
        assert validate_range_simple(5.0, 5.0, 5.0) is True

        with pytest.raises(ValidationError, match="Value 4.0 is below minimum 5.0"):
            validate_range_simple(4.0, 5.0, 5.0)

        with pytest.raises(ValidationError, match="Value 6.0 is above maximum 5.0"):
            validate_range_simple(6.0, 5.0, 5.0)

    def test_very_large_numbers(self) -> None:
        """Test with very large numbers."""
        large_num = 1e10
        assert validate_range_simple(large_num, 0, 2e10) is True

    def test_very_small_numbers(self) -> None:
        """Test with very small numbers."""
        small_num = 1e-10
        assert validate_range_simple(small_num, 0, 1e-5) is True


class TestCreateValidationReport:
    """Test cases for create_validation_report function."""

    def test_valid_data_simple_rules(self) -> None:
        """Test validation report for valid data with simple rules."""
        data = {"name": "Alice", "age": 30}
        rules = {
            "required": ["name", "age"],
            "types": {"name": "str", "age": "int"},
        }

        result = create_validation_report(data, rules)

        assert result["valid"] is True
        assert result["errors"] == []
        assert result["warnings"] == []
        assert result["fields_validated"] == 2
        assert result["rules_applied"] == 2

    def test_invalid_data_missing_required(self) -> None:
        """Test validation report for data missing required fields."""
        data = {"name": "Alice"}
        rules = {
            "required": ["name", "age", "email"],
            "types": {"name": "str"},
        }

        result = create_validation_report(data, rules)

        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert "Required fields are missing: ['age', 'email']" in result["errors"][0]
        assert result["warnings"] == []

    def test_invalid_data_wrong_types(self) -> None:
        """Test validation report for data with wrong types."""
        data = {"name": 123, "age": "thirty"}
        rules = {
            "required": ["name", "age"],
            "types": {"name": "str", "age": "int"},
        }

        result = create_validation_report(data, rules)

        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert "Type validation errors" in result["errors"][0]
        assert "expected str, got int" in result["errors"][0]
        assert "expected int, got str" in result["errors"][0]

    def test_range_validation_success(self) -> None:
        """Test validation report with successful range validation."""
        data = {"score": 85.5, "rating": 4}
        rules = {
            "types": {"score": "float", "rating": "int"},
            "ranges": {
                "score": {"min": 0, "max": 100},
                "rating": {"min": 1, "max": 5},
            },
        }

        result = create_validation_report(data, rules)

        assert result["valid"] is True
        assert result["errors"] == []
        assert result["warnings"] == []

    def test_range_validation_failure(self) -> None:
        """Test validation report with range validation failures."""
        data = {"score": 105, "rating": 0}
        rules = {
            "ranges": {
                "score": {"min": 0, "max": 100},
                "rating": {"min": 1, "max": 5},
            },
        }

        result = create_validation_report(data, rules)

        assert result["valid"] is False
        assert len(result["errors"]) == 2
        assert any(
            "score" in error and "above maximum" in error for error in result["errors"]
        )
        assert any(
            "rating" in error and "below minimum" in error for error in result["errors"]
        )

    def test_pattern_validation_success(self) -> None:
        """Test validation report with successful pattern validation."""
        data = {"email": "alice@example.com", "phone": "123-456-7890"}
        rules = {
            "patterns": {
                "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                "phone": r"^\d{3}-\d{3}-\d{4}$",
            },
        }

        result = create_validation_report(data, rules)

        assert result["valid"] is True
        assert result["errors"] == []

    def test_pattern_validation_failure(self) -> None:
        """Test validation report with pattern validation failures."""
        data = {"email": "invalid-email", "phone": "123456"}
        rules = {
            "patterns": {
                "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                "phone": r"^\d{3}-\d{3}-\d{4}$",
            },
        }

        result = create_validation_report(data, rules)

        assert result["valid"] is False
        assert len(result["errors"]) == 2
        assert any(
            "email" in error and "does not match pattern" in error
            for error in result["errors"]
        )
        assert any(
            "phone" in error and "does not match pattern" in error
            for error in result["errors"]
        )

    def test_invalid_pattern_warning(self) -> None:
        """Test validation report with invalid regex pattern."""
        data = {"field": "value"}
        rules = {
            "patterns": {
                "field": "[invalid_regex",  # Invalid regex
            },
        }

        result = create_validation_report(data, rules)

        assert result["valid"] is True  # Should still be valid despite warning
        assert result["errors"] == []
        assert len(result["warnings"]) == 1
        assert "Invalid regex pattern" in result["warnings"][0]

    def test_unexpected_fields_warning(self) -> None:
        """Test validation report with unexpected fields."""
        data = {"name": "Alice", "unexpected1": "value", "unexpected2": 123}
        rules = {
            "allowed_fields": ["name", "age"],
            "required": ["name"],
        }

        result = create_validation_report(data, rules)

        assert result["valid"] is True  # Warnings don't make it invalid
        assert result["errors"] == []
        assert len(result["warnings"]) == 1
        assert "Unexpected fields found" in result["warnings"][0]
        assert "unexpected1" in result["warnings"][0]
        assert "unexpected2" in result["warnings"][0]

    def test_comprehensive_validation_report(self) -> None:
        """Test comprehensive validation with multiple rule types."""
        data = {
            "name": "Alice",
            "age": 25,
            "email": "alice@example.com",
            "score": 95.5,
            "phone": "123-456-7890",
            "extra": "unexpected",
        }
        rules = {
            "required": ["name", "age", "email"],
            "types": {"name": "str", "age": "int", "email": "str", "score": "float"},
            "ranges": {"age": {"min": 18, "max": 65}, "score": {"min": 0, "max": 100}},
            "patterns": {
                "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                "phone": r"^\d{3}-\d{3}-\d{4}$",
            },
            "allowed_fields": ["name", "age", "email", "score", "phone"],
        }

        result = create_validation_report(data, rules)

        assert result["valid"] is True
        assert result["errors"] == []
        assert len(result["warnings"]) == 1  # Unexpected field warning
        assert result["fields_validated"] == 6
        assert result["rules_applied"] == 5

    def test_empty_data_empty_rules(self) -> None:
        """Test validation report with empty data and rules."""
        data = {}
        rules = {}

        result = create_validation_report(data, rules)

        assert result["valid"] is True
        assert result["errors"] == []
        assert result["warnings"] == []
        assert result["fields_validated"] == 0
        assert result["rules_applied"] == 0

    def test_invalid_data_type(self) -> None:
        """Test error handling for invalid data type."""
        rules = {"required": ["name"]}

        with pytest.raises(TypeError, match="data must be a dictionary"):
            create_validation_report(["not", "dict"], rules)  # type: ignore[arg-type]

    def test_invalid_rules_type(self) -> None:
        """Test error handling for invalid rules type."""
        data = {"name": "Alice"}

        with pytest.raises(TypeError, match="rules must be a dictionary"):
            create_validation_report(data, ["not", "dict"])  # type: ignore[arg-type]

    def test_range_validation_missing_field(self) -> None:
        """Test range validation when field is missing from data."""
        data = {"name": "Alice"}
        rules = {
            "ranges": {"missing_field": {"min": 0, "max": 100}},
        }

        result = create_validation_report(data, rules)

        # Should not fail for missing fields in range validation
        assert result["valid"] is True
        assert result["errors"] == []

    def test_pattern_validation_missing_field(self) -> None:
        """Test pattern validation when field is missing from data."""
        data = {"name": "Alice"}
        rules = {
            "patterns": {"missing_field": r"^\d+$"},
        }

        result = create_validation_report(data, rules)

        # Should not fail for missing fields in pattern validation
        assert result["valid"] is True
        assert result["errors"] == []


class TestAliaseFunctions:
    """Test cases for alias functions."""

    def test_check_required_fields_simple_alias(self) -> None:
        """Test that check_required_fields_simple is an alias."""
        data = {"name": "Alice", "age": 30}
        required = ["name", "age"]

        # Should behave identically to check_required_fields
        result1 = check_required_fields(data, required)
        result2 = check_required_fields_simple(data, required)

        assert result1 == result2 is True

        # Should raise same errors
        with pytest.raises(ValidationError):
            check_required_fields_simple({"name": "Alice"}, ["name", "missing"])

    def test_create_validation_report_simple_alias(self) -> None:
        """Test that create_validation_report_simple is an alias."""
        data = {"name": "Alice", "age": 30}
        rules = {"required": ["name"], "types": {"age": "int"}}

        # Should behave identically to create_validation_report
        result1 = create_validation_report(data, rules)
        result2 = create_validation_report_simple(data, rules)

        assert result1 == result2
        assert result1["valid"] is True


# Integration tests
class TestValidationIntegration:
    """Integration tests for validation functions working together."""

    def test_complete_user_validation_workflow(self) -> None:
        """Test complete user validation workflow."""
        # Valid user data
        user_data = {
            "name": "Alice Johnson",
            "age": 28,
            "email": "alice@company.com",
            "score": 85.5,
        }

        # Step 1: Check required fields
        required_fields = ["name", "age", "email"]
        assert check_required_fields(user_data, required_fields) is True

        # Step 2: Validate data types
        type_map = {"name": "str", "age": "int", "email": "str", "score": "float"}
        assert validate_data_types_simple(user_data, type_map) is True

        # Step 3: Validate ranges
        assert validate_range_simple(user_data["age"], 18, 65) is True
        assert validate_range_simple(user_data["score"], 0, 100) is True

        # Step 4: Schema validation
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"},
                "email": {"type": "string"},
            },
            "required": ["name", "age", "email"],
        }
        assert validate_schema_simple(user_data, schema) is True

        # Step 5: Comprehensive report
        rules = {
            "required": required_fields,
            "types": type_map,
            "ranges": {"age": {"min": 18, "max": 65}, "score": {"min": 0, "max": 100}},
            "patterns": {"email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"},
        }
        report = create_validation_report(user_data, rules)
        assert report["valid"] is True

    def test_validation_error_propagation(self) -> None:
        """Test that validation errors are properly propagated."""
        invalid_data = {"name": 123}  # Wrong type

        # Individual function should raise
        with pytest.raises(ValidationError):
            validate_data_types_simple(invalid_data, {"name": "str"})

        # Report should capture the error
        rules = {"types": {"name": "str"}}
        report = create_validation_report(invalid_data, rules)
        assert report["valid"] is False
        assert len(report["errors"]) == 1

    def test_partial_validation_success(self) -> None:
        """Test partial validation where some rules pass and others fail."""
        data = {"name": "Alice", "age": "not_a_number", "score": 150}
        rules = {
            "required": ["name"],  # This should pass
            "types": {"name": "str", "age": "int"},  # name passes, age fails
            "ranges": {"score": {"min": 0, "max": 100}},  # This should fail
        }

        report = create_validation_report(data, rules)
        assert report["valid"] is False
        assert len(report["errors"]) == 2  # Type error + range error
        assert report["fields_validated"] == 3
