"""Data validation utilities for AI agents."""

from typing import Dict, List

from ..exceptions import ValidationError


def validate_schema_simple(data: dict, schema: dict) -> bool:
    """Validate data against a JSON Schema-style schema.

    Args:
        data: Data to validate
        schema: Schema definition dictionary

    Returns:
        True if data matches schema

    Raises:
        ValidationError: If data doesn't match schema
        TypeError: If schema is not a dictionary

    Example:
        >>> schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        >>> validate_schema_simple({"name": "Alice"}, schema)
        True
    """
    if not isinstance(schema, dict):
        raise TypeError("schema must be a dictionary")

    try:
        _validate_against_schema(data, schema)
        return True
    except ValidationError:
        raise


def _validate_against_schema(data: dict, schema: dict) -> None:
    """Internal helper to validate data against schema."""
    schema_type = schema.get("type")

    if schema_type == "object":
        if not isinstance(data, dict):
            raise ValidationError(f"Expected object, got {type(data).__name__}")

        properties = schema.get("properties", {})
        required = schema.get("required", [])

        # Check required properties
        for prop in required:
            if prop not in data:
                raise ValidationError(f"Required property '{prop}' is missing")

        # Validate properties
        for prop, value in data.items():
            if prop in properties:
                # Only validate dict values recursively
                if isinstance(value, dict):
                    _validate_against_schema(value, properties[prop])

    elif schema_type == "array":
        # For dict-only validation, we can't handle arrays directly
        # This would need to be a dict with array-like structure
        raise ValidationError("Array validation not supported with dict-only input")


def check_required_fields(data: dict, required: List[str]) -> bool:
    """Check if all required fields are present in data.

    Args:
        data: Dictionary to check
        required: List of required field names

    Returns:
        True if all required fields are present

    Raises:
        ValidationError: If any required fields are missing
        TypeError: If data is not a dictionary or required is not a list

    Example:
        >>> check_required_fields({"name": "Alice", "age": 25}, ["name", "age"])
        True
        >>> check_required_fields({"name": "Alice"}, ["name", "age"])
        False
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")

    if not isinstance(required, list):
        raise TypeError("required must be a list")

    missing_fields = [field for field in required if field not in data]

    if missing_fields:
        raise ValidationError(f"Required fields are missing: {missing_fields}")

    return True


def validate_data_types_simple(data: dict, type_map: Dict[str, str]) -> bool:
    """Check that field types match expectations.

    Args:
        data: Dictionary to validate
        type_map: Mapping of field names to expected type names (as strings)

    Returns:
        True if all types match

    Raises:
        ValidationError: If any field has wrong type
        TypeError: If data is not a dictionary or type_map is not a dictionary

    Example:
        >>> data = {"name": "Alice", "age": 25}
        >>> type_map = {"name": "str", "age": "int"}
        >>> validate_data_types_simple(data, type_map)
        True
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")

    if not isinstance(type_map, dict):
        raise TypeError("type_map must be a dictionary")

    type_errors = []

    type_mapping = {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "list": list,
        "dict": dict,
    }

    for field, expected_type_name in type_map.items():
        if field in data:
            value = data[field]
            expected_type = type_mapping.get(expected_type_name)
            if expected_type and not isinstance(value, expected_type):
                actual_type = type(value).__name__
                type_errors.append(
                    f"Field '{field}': expected {expected_type_name}, got {actual_type}"
                )

    if type_errors:
        raise ValidationError(f"Type validation errors: {'; '.join(type_errors)}")

    return True


def validate_range_simple(
    value: float,
    min_val: float,
    max_val: float,
) -> bool:
    """Validate numeric value is within range.

    Args:
        value: Numeric value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        True if value is within range

    Raises:
        ValidationError: If value is outside the specified range
        TypeError: If value, min_val, or max_val are not numeric types

    Example:
        >>> validate_range_simple(5.0, 1.0, 10.0)
        True
        >>> validate_range_simple(15.0, 1.0, 10.0)
        False
    """
    if not isinstance(value, (int, float)):
        raise TypeError("value must be numeric")

    if not isinstance(min_val, (int, float)):
        raise TypeError("min_val must be numeric")

    if not isinstance(max_val, (int, float)):
        raise TypeError("max_val must be numeric")

    if value < min_val:
        raise ValidationError(f"Value {value} is below minimum {min_val}")

    if value > max_val:
        raise ValidationError(f"Value {value} is above maximum {max_val}")

    return True


def create_validation_report(data: dict, rules: dict) -> dict:
    """Create comprehensive validation report for data.

    Args:
        data: Dictionary to validate
        rules: Dictionary of validation rules

    Returns:
        Validation report with results and errors

    Raises:
        TypeError: If data is not a dictionary or rules is not a dictionary

    Example:
        >>> data = {"name": "Alice", "age": 25}
        >>> rules = {"required": ["name", "age"], "types": {"name": "str", "age": "int"}}
        >>> create_validation_report(data, rules)
        {"valid": True, "errors": [], "warnings": []}
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")

    if not isinstance(rules, dict):
        raise TypeError("rules must be a dictionary")

    errors = []
    warnings = []

    # Check required fields
    required_fields = rules.get("required", [])
    try:
        check_required_fields(data, required_fields)
    except ValidationError as e:
        errors.append(str(e))

    # Check data types
    type_map = rules.get("types", {})
    try:
        validate_data_types_simple(data, type_map)
    except ValidationError as e:
        errors.append(str(e))

    # Check ranges for numeric fields
    ranges = rules.get("ranges", {})
    for field, range_spec in ranges.items():
        if field in data:
            value = data[field]
            min_val = range_spec.get("min")
            max_val = range_spec.get("max")
            try:
                validate_range_simple(value, min_val, max_val)
            except (ValidationError, TypeError) as e:
                errors.append(f"Range validation failed for '{field}': {str(e)}")

    # Check custom patterns
    patterns = rules.get("patterns", {})
    for field, pattern in patterns.items():
        if field in data:
            import re

            value = str(data[field])
            try:
                if not re.match(pattern, value):
                    errors.append(f"Field '{field}' does not match pattern '{pattern}'")
            except re.error:
                warnings.append(f"Invalid regex pattern for field '{field}': {pattern}")

    # Check for unexpected fields
    allowed_fields = rules.get("allowed_fields")
    if allowed_fields:
        unexpected = set(data.keys()) - set(allowed_fields)
        if unexpected:
            warnings.append(f"Unexpected fields found: {list(unexpected)}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "fields_validated": len(data),
        "rules_applied": len([k for k in rules.keys() if rules[k]]),
    }


def check_required_fields_simple(data: dict, required: List[str]) -> bool:
    """Check if all required fields are present in data.

    This is an alias for check_required_fields for LLM agent compatibility.

    Args:
        data: Dictionary to check
        required: List of required field names

    Returns:
        True if all required fields are present

    Raises:
        ValidationError: If any required fields are missing
        TypeError: If data is not a dictionary or required is not a list

    Example:
        >>> check_required_fields_simple({"name": "Alice", "age": 25}, ["name", "age"])
        True
    """
    return check_required_fields(data, required)


def create_validation_report_simple(data: dict, rules: dict) -> dict:
    """Create simplified validation report for data.

    This is an alias for create_validation_report for LLM agent compatibility.

    Args:
        data: Dictionary to validate
        rules: Dictionary of validation rules

    Returns:
        Validation report with results and errors

    Example:
        >>> data = {"name": "Alice", "age": 25}
        >>> rules = {"required": ["name", "age"], "types": {"name": "str", "age": "int"}}
        >>> create_validation_report_simple(data, rules)
        {"valid": True, "errors": [], "warnings": []}
    """
    return create_validation_report(data, rules)
