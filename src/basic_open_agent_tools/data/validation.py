"""Data validation utilities for AI agents."""

from ..exceptions import ValidationError


def validate_schema_simple(data, schema: dict) -> bool:
    """Validate data against a JSON Schema-style schema.

    Args:
        data: Data to validate
        schema: Schema definition dictionary

    Returns:
        True if data matches schema

    Raises:
        ValidationError: If data doesn't match schema

    Example:
        >>> schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        >>> validate_schema_simple({"name": "Alice"}, schema)
        True
    """
    try:
        _validate_against_schema(data, schema)
        return True
    except ValidationError:
        raise


def _validate_against_schema(data, schema: dict) -> None:
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
                _validate_against_schema(value, properties[prop])

    elif schema_type == "array":
        if not isinstance(data, list):
            raise ValidationError(f"Expected array, got {type(data).__name__}")

        items_schema = schema.get("items")
        if items_schema:
            for i, item in enumerate(data):
                try:
                    _validate_against_schema(item, items_schema)
                except ValidationError as e:
                    raise ValidationError(f"Array item {i}: {e}")

    elif schema_type == "string":
        if not isinstance(data, str):
            raise ValidationError(f"Expected string, got {type(data).__name__}")

    elif schema_type == "number":
        if not isinstance(data, (int, float)):
            raise ValidationError(f"Expected number, got {type(data).__name__}")

    elif schema_type == "integer":
        if not isinstance(data, int):
            raise ValidationError(f"Expected integer, got {type(data).__name__}")

    elif schema_type == "boolean":
        if not isinstance(data, bool):
            raise ValidationError(f"Expected boolean, got {type(data).__name__}")

    elif schema_type == "null":
        if data is not None:
            raise ValidationError(f"Expected null, got {type(data).__name__}")


def check_required_fields(data: dict, required: list) -> bool:
    """Check if all required fields are present in data.

    Args:
        data: Dictionary to check
        required: List of required field names

    Returns:
        True if all required fields are present

    Raises:
        ValidationError: If any required fields are missing

    Example:
        >>> check_required_fields({"name": "Alice", "age": 25}, ["name", "age"])
        True
        >>> check_required_fields({"name": "Alice"}, ["name", "age"])
        False
    """
    missing_fields = [field for field in required if field not in data]

    if missing_fields:
        raise ValidationError(f"Required fields are missing: {missing_fields}")

    return True


def validate_data_types_simple(data: dict, type_map: dict) -> bool:
    """Check that field types match expectations.

    Args:
        data: Dictionary to validate
        type_map: Mapping of field names to expected type names (as strings)

    Returns:
        True if all types match

    Raises:
        ValidationError: If any field has wrong type

    Example:
        >>> data = {"name": "Alice", "age": 25}
        >>> type_map = {"name": "str", "age": "int"}
        >>> validate_data_types_simple(data, type_map)
        True
    """
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


def validate_range_simple(value, min_val=None, max_val=None) -> bool:
    """Validate numeric value is within range.

    Args:
        value: Numeric value to validate
        min_val: Minimum allowed value (optional)
        max_val: Maximum allowed value (optional)

    Returns:
        True if value is within range

    Example:
        >>> validate_range_simple(5, 1, 10)
        True
        >>> validate_range_simple(15, 1, 10)
        False
    """
    if not isinstance(value, (int, float)):
        return False

    if min_val is not None and value < min_val:
        return False

    if max_val is not None and value > max_val:
        return False

    return True


def create_validation_report(data: dict, rules: dict) -> dict:
    """Create comprehensive validation report for data.

    Args:
        data: Dictionary to validate
        rules: Dictionary of validation rules

    Returns:
        Validation report with results and errors

    Example:
        >>> data = {"name": "Alice", "age": 25}
        >>> rules = {"required": ["name", "age"], "types": {"name": "str", "age": "int"}}
        >>> create_validation_report(data, rules)
        {"valid": True, "errors": [], "warnings": []}
    """
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
            if not validate_range_simple(value, min_val, max_val):
                errors.append(
                    f"Range validation failed for '{field}': value {value} not in range [{min_val}, {max_val}]"
                )

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
