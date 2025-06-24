"""Data validation utilities for AI agents."""

from typing import Any, Dict, List, Optional, Union

from ..exceptions import ValidationError
from ..types import DataDict, ValidationResult


def validate_schema(data: Any, schema: DataDict) -> bool:
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
        >>> validate_schema({"name": "Alice"}, schema)
        True
    """
    if not isinstance(schema, dict):
        raise TypeError("schema must be a dictionary")

    try:
        _validate_against_schema(data, schema)
        return True
    except ValidationError:
        raise


def _validate_against_schema(data: Any, schema: DataDict) -> None:
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


def check_required_fields(data: DataDict, required: List[str]) -> bool:
    """Ensure all required fields exist in data.

    Args:
        data: Dictionary to check
        required: List of required field names

    Returns:
        True if all required fields exist

    Raises:
        ValidationError: If any required field is missing
        TypeError: If arguments have wrong types

    Example:
        >>> check_required_fields({"name": "Alice", "age": 25}, ["name", "age"])
        True
        >>> check_required_fields({"name": "Alice"}, ["name", "age"])
        ValidationError: Required field 'age' is missing
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")
    if not isinstance(required, list):
        raise TypeError("required must be a list")

    missing_fields = [field for field in required if field not in data]

    if missing_fields:
        raise ValidationError(f"Required fields are missing: {missing_fields}")

    return True


def validate_data_types(data: DataDict, type_map: Dict[str, type]) -> bool:
    """Check that field types match expectations.

    Args:
        data: Dictionary to validate
        type_map: Mapping of field names to expected types

    Returns:
        True if all types match

    Raises:
        ValidationError: If any field has wrong type
        TypeError: If arguments have wrong types

    Example:
        >>> data = {"name": "Alice", "age": 25}
        >>> type_map = {"name": str, "age": int}
        >>> validate_data_types(data, type_map)
        True
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")
    if not isinstance(type_map, dict):
        raise TypeError("type_map must be a dictionary")

    type_errors = []

    for field, expected_type in type_map.items():
        if field in data:
            value = data[field]
            if not isinstance(value, expected_type):
                actual_type = type(value).__name__
                expected_name = expected_type.__name__
                type_errors.append(
                    f"Field '{field}': expected {expected_name}, got {actual_type}"
                )

    if type_errors:
        raise ValidationError(f"Type validation errors: {'; '.join(type_errors)}")

    return True


def validate_range(
    value: Union[int, float],
    min_val: Optional[Union[int, float]] = None,
    max_val: Optional[Union[int, float]] = None,
) -> bool:
    """Validate that numeric value is within specified range.

    Args:
        value: Numeric value to validate
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)

    Returns:
        True if value is within range

    Raises:
        ValidationError: If value is outside range
        TypeError: If arguments have wrong types

    Example:
        >>> validate_range(25, min_val=18, max_val=65)
        True
        >>> validate_range(10, min_val=18)
        ValidationError: Value 10 is below minimum 18
    """
    if not isinstance(value, (int, float)):
        raise TypeError("value must be numeric")
    if min_val is not None and not isinstance(min_val, (int, float)):
        raise TypeError("min_val must be numeric or None")
    if max_val is not None and not isinstance(max_val, (int, float)):
        raise TypeError("max_val must be numeric or None")

    if min_val is not None and value < min_val:
        raise ValidationError(f"Value {value} is below minimum {min_val}")

    if max_val is not None and value > max_val:
        raise ValidationError(f"Value {value} is above maximum {max_val}")

    return True


def aggregate_validation_errors(results: List[ValidationResult]) -> ValidationResult:
    """Combine multiple validation results into a single result.

    Args:
        results: List of validation result dictionaries

    Returns:
        Aggregated validation result

    Raises:
        TypeError: If results is not a list

    Example:
        >>> result1 = {"valid": False, "errors": ["Error 1"]}
        >>> result2 = {"valid": False, "errors": ["Error 2"]}
        >>> aggregate_validation_errors([result1, result2])
        {"valid": False, "errors": ["Error 1", "Error 2"]}
    """
    if not isinstance(results, list):
        raise TypeError("results must be a list")

    if not results:
        return {"valid": True, "errors": []}

    all_errors = []
    all_valid = True

    for result in results:
        if not isinstance(result, dict):
            continue  # type: ignore[unreachable]

        if not result.get("valid", True):
            all_valid = False

        errors = result.get("errors", [])
        if isinstance(errors, list):
            all_errors.extend(errors)
        elif isinstance(errors, str):
            all_errors.append(errors)

    return {
        "valid": all_valid,
        "errors": all_errors,
        "total_validations": len(results),
        "failed_validations": sum(1 for r in results if not r.get("valid", True)),
    }


def create_validation_report(data: DataDict, rules: DataDict) -> ValidationResult:
    """Generate detailed validation report for data according to rules.

    Args:
        data: Dictionary to validate
        rules: Validation rules dictionary

    Returns:
        Detailed validation result with errors and warnings

    Raises:
        TypeError: If arguments have wrong types

    Example:
        >>> data = {"name": "Alice", "age": 25}
        >>> rules = {"required": ["name", "age"], "types": {"name": str, "age": int}}
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
        validate_data_types(data, type_map)
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
                validate_range(value, min_val, max_val)
            except (ValidationError, TypeError) as e:
                errors.append(f"Range validation for '{field}': {e}")

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
