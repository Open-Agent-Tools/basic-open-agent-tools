"""Data transformation tools for AI agents."""

import copy

from ..exceptions import DataError


def transform_data(data: list, mapping: dict) -> list:
    """Apply a transformation mapping to a list of data records.

    Args:
        data: List of dictionary records to transform
        mapping: Dictionary mapping source fields to new field names

    Returns:
        Transformed list of dictionaries

    Example:
        >>> data = [{"old_name": "Alice", "old_age": 25}]
        >>> mapping = {"old_name": "name", "old_age": "age"}
        >>> transform_data(data, mapping)
        [{"name": "Alice", "age": 25}]
    """
    if not isinstance(data, list):
        raise DataError("Data must be a list of dictionaries")
    if not isinstance(mapping, dict):
        raise DataError("Mapping must be a dictionary")

    transformed_data = []

    for record in data:
        if not isinstance(record, dict):
            continue

        transformed_record = {}

        for source_field, target_field in mapping.items():
            if source_field in record:
                transformed_record[target_field] = record[source_field]

        # Include fields not in mapping as-is
        for field, value in record.items():
            if field not in mapping and field not in transformed_record:
                transformed_record[field] = value

        transformed_data.append(transformed_record)

    return transformed_data


def rename_fields(data: list, field_mapping: dict) -> list:
    """Rename fields in a list of dictionaries.

    Args:
        data: List of dictionaries
        field_mapping: Mapping of old field names to new field names

    Returns:
        List with renamed fields

    Example:
        >>> data = [{"first": "Alice", "last": "Smith"}]
        >>> rename_fields(data, {"first": "first_name", "last": "last_name"})
        [{"first_name": "Alice", "last_name": "Smith"}]
    """
    if not isinstance(data, list):
        raise DataError("Data must be a list")
    if not isinstance(field_mapping, dict):
        raise DataError("Field mapping must be a dictionary")

    renamed_data = []

    for record in data:
        if not isinstance(record, dict):
            continue

        renamed_record = {}
        for field, value in record.items():
            new_field = field_mapping.get(field, field)
            renamed_record[new_field] = value

        renamed_data.append(renamed_record)

    return renamed_data


def convert_data_types(data: list, type_mapping: dict) -> list:
    """Convert data types for specified fields.

    Args:
        data: List of dictionaries
        type_mapping: Mapping of field names to type conversion functions

    Returns:
        List with converted data types

    Example:
        >>> data = [{"age": "25", "score": "95.5"}]
        >>> convert_data_types(data, {"age": int, "score": float})
        [{"age": 25, "score": 95.5}]
    """
    if not isinstance(data, list):
        raise DataError("Data must be a list")
    if not isinstance(type_mapping, dict):
        raise DataError("Type mapping must be a dictionary")

    converted_data = []

    for record in data:
        if not isinstance(record, dict):
            continue

        converted_record = record.copy()

        for field, type_func in type_mapping.items():
            if field in converted_record:
                try:
                    converted_record[field] = type_func(converted_record[field])
                except (ValueError, TypeError) as e:
                    raise DataError(f"Failed to convert field '{field}': {e}")

        converted_data.append(converted_record)

    return converted_data


def clean_data(data: list, rules: dict = None) -> list:
    """Clean data according to specified rules.

    Args:
        data: List of dictionaries to clean
        rules: Dictionary of cleaning rules

    Returns:
        Cleaned data

    Example:
        >>> data = [{"name": "  Alice  ", "age": None, "city": ""}]
        >>> clean_data(data, {"strip_whitespace": True, "remove_nulls": True})
        [{"name": "Alice"}]
    """
    if not isinstance(data, list):
        raise DataError("Data must be a list")

    # Default rules
    default_rules = {
        "strip_whitespace": True,
        "remove_nulls": False,
        "remove_empty_strings": False,
        "remove_empty_lists": False,
    }

    if rules:
        default_rules.update(rules)

    cleaned_data = []

    for record in data:
        if not isinstance(record, dict):
            continue

        cleaned_record = {}

        for field, value in record.items():
            # Strip whitespace from strings
            if default_rules.get("strip_whitespace") and isinstance(value, str):
                value = value.strip()

            # Remove null values
            if default_rules.get("remove_nulls") and value is None:
                continue

            # Remove empty strings
            if default_rules.get("remove_empty_strings") and value == "":
                continue

            # Remove empty lists
            if default_rules.get("remove_empty_lists") and value == []:
                continue

            cleaned_record[field] = value

        cleaned_data.append(cleaned_record)

    return cleaned_data


def deduplicate_records(data: list, key_fields: list = None) -> list:
    """Remove duplicate records from a list.

    Args:
        data: List of dictionaries
        key_fields: List of fields to use for deduplication (None for all fields)

    Returns:
        List with duplicates removed

    Example:
        >>> data = [{"name": "Alice", "age": 25}, {"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
        >>> deduplicate_records(data)
        [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
    """
    if not isinstance(data, list):
        raise DataError("Data must be a list")

    seen = set()
    deduplicated_data = []

    for record in data:
        if not isinstance(record, dict):
            continue

        # Create a key based on specified fields or all fields
        if key_fields:
            key_values = tuple(record.get(field) for field in key_fields)
        else:
            key_values = tuple(sorted(record.items()))

        if key_values not in seen:
            seen.add(key_values)
            deduplicated_data.append(record)

    return deduplicated_data


def normalize_data(
    data: list, field: str, min_val: float = 0.0, max_val: float = 1.0
) -> list:
    """Normalize numeric values in a field to a specified range.

    Args:
        data: List of dictionaries
        field: Field name to normalize
        min_val: Minimum value for normalization
        max_val: Maximum value for normalization

    Returns:
        List with normalized values

    Example:
        >>> data = [{"score": 80}, {"score": 90}, {"score": 100}]
        >>> normalize_data(data, "score", 0, 1)
        [{"score": 0.0}, {"score": 0.5}, {"score": 1.0}]
    """
    if not isinstance(data, list):
        raise DataError("Data must be a list")

    # Find min and max values in the field
    values = []
    for record in data:
        if isinstance(record, dict) and field in record:
            value = record[field]
            if isinstance(value, (int, float)):
                values.append(value)

    if not values:
        return data

    data_min = min(values)
    data_max = max(values)
    data_range = data_max - data_min

    if data_range == 0:
        # All values are the same
        normalized_data = copy.deepcopy(data)
        for record in normalized_data:
            if isinstance(record, dict) and field in record:
                record[field] = min_val
        return normalized_data

    # Normalize the data
    normalized_data = copy.deepcopy(data)
    for record in normalized_data:
        if isinstance(record, dict) and field in record:
            value = record[field]
            if isinstance(value, (int, float)):
                normalized_value = min_val + (value - data_min) / data_range * (
                    max_val - min_val
                )
                record[field] = normalized_value

    return normalized_data


def pivot_data(
    data: list, index_field: str, column_field: str, value_field: str
) -> dict:
    """Pivot data from long format to wide format.

    Args:
        data: List of dictionaries in long format
        index_field: Field to use as row index
        column_field: Field to use as column headers
        value_field: Field containing values to pivot

    Returns:
        Dictionary with pivoted data

    Example:
        >>> data = [
        ...     {"name": "Alice", "metric": "age", "value": 25},
        ...     {"name": "Alice", "metric": "score", "value": 95},
        ...     {"name": "Bob", "metric": "age", "value": 30}
        ... ]
        >>> pivot_data(data, "name", "metric", "value")
        {"Alice": {"age": 25, "score": 95}, "Bob": {"age": 30}}
    """
    if not isinstance(data, list):
        raise DataError("Data must be a list")

    pivoted = {}

    for record in data:
        if not isinstance(record, dict):
            continue

        if (
            index_field not in record
            or column_field not in record
            or value_field not in record
        ):
            continue

        index_val = record[index_field]
        column_val = record[column_field]
        value_val = record[value_field]

        if index_val not in pivoted:
            pivoted[index_val] = {}

        pivoted[index_val][column_val] = value_val

    return pivoted
