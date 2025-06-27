"""Data transformation tools for AI agents."""

from typing import Any, Callable, Dict, List, Optional, Union

from ..exceptions import DataError


def transform_data(
    data: List[Dict[str, Any]], mapping: Dict[str, Union[str, Callable[[Any], Any]]]
) -> List[Dict[str, Any]]:
    """Apply a transformation mapping to a list of data records.

    Args:
        data: List of dictionary records to transform
        mapping: Dictionary mapping source fields to new field names or transformation functions

    Returns:
        Transformed list of dictionaries

    Raises:
        DataError: If data is not a list, mapping is not a dictionary,
                  or a mapping value is neither a string nor a callable

    Example:
        >>> data = [{"name": "John Doe", "age": "42"}]
        >>> mapping = {"name": "full_name", "age": lambda x: int(x)}
        >>> transform_data(data, mapping)
        [{"full_name": "John Doe", "age": 42}]
    """
    if not isinstance(data, list):
        raise DataError("Data must be a list of dictionaries")
    if not isinstance(mapping, dict):
        raise DataError("Mapping must be a dictionary")

    transformed_data = []

    for record in data:
        if not isinstance(record, dict):
            raise DataError(f"Expected dictionary, got {type(record).__name__}")

        transformed_record = {}

        for source_field, transform in mapping.items():
            if source_field in record:
                value = record[source_field]

                if callable(transform):
                    try:
                        transformed_record[source_field] = transform(value)
                    except Exception as e:
                        raise DataError(
                            f"Error transforming field '{source_field}': {e}"
                        )
                elif isinstance(transform, str):
                    transformed_record[transform] = value
                else:
                    raise DataError(
                        f"Invalid transform for field '{source_field}': must be string or callable"
                    )

        # Include fields not in mapping as-is
        for field, value in record.items():
            if field not in mapping and field not in transformed_record:
                transformed_record[field] = value

        transformed_data.append(transformed_record)

    return transformed_data


def rename_fields(
    data: List[Dict[str, Any]], field_mapping: Dict[str, str]
) -> List[Dict[str, Any]]:
    """Rename fields in a list of dictionaries.

    Args:
        data: List of dictionaries
        field_mapping: Mapping of old field names to new field names

    Returns:
        List with renamed fields

    Raises:
        DataError: If data is not a list, field_mapping is not a dictionary, or a record is not a dictionary

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

    for i, record in enumerate(data):
        if not isinstance(record, dict):
            raise DataError(
                f"Record at index {i} is not a dictionary: {type(record).__name__}"
            )

        renamed_record = {}
        for field, value in record.items():
            new_field = field_mapping.get(field, field)
            renamed_record[new_field] = value

        renamed_data.append(renamed_record)

    return renamed_data


def convert_data_types(
    data: List[Dict[str, Any]], type_mapping: Dict[str, Callable[[Any], Any]]
) -> List[Dict[str, Any]]:
    """Convert data types for specified fields.

    Args:
        data: List of dictionaries
        type_mapping: Mapping of field names to type conversion functions

    Returns:
        List with converted data types

    Raises:
        DataError: If data is not a list or type_mapping is not a dictionary
        ValueError: If a conversion function raises a ValueError

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
            raise DataError(f"Expected dictionary, got {type(record).__name__}")

        converted_record = record.copy()

        for field, type_func in type_mapping.items():
            if field in converted_record and converted_record[field] is not None:
                # Let ValueError propagate to the caller
                converted_record[field] = type_func(converted_record[field])

        converted_data.append(converted_record)

    return converted_data


def clean_data(
    data: List[Dict[str, Any]], rules: Dict[str, List[Callable[[Any], Any]]]
) -> List[Dict[str, Any]]:
    """Clean data according to specified rules.

    Args:
        data: List of dictionaries to clean
        rules: Dictionary mapping field names to lists of cleaning functions

    Returns:
        Cleaned data

    Raises:
        DataError: If data is not a list, rules is not a dictionary,
                  a cleaner is not callable, or a cleaner raises an error

    Example:
        >>> data = [{"name": "  John  ", "email": "JOHN@example.com"}]
        >>> rules = {"name": [str.strip, str.title], "email": [str.lower]}
        >>> clean_data(data, rules)
        [{"name": "John", "email": "john@example.com"}]
    """
    if not isinstance(data, list):
        raise DataError("Data must be a list")

    if not isinstance(rules, dict):
        raise DataError("Rules must be a dictionary")

    cleaned_data = []

    for record in data:
        if not isinstance(record, dict):
            raise DataError(f"Expected dictionary, got {type(record).__name__}")

        cleaned_record = record.copy()

        for field, cleaners in rules.items():
            if field in cleaned_record:
                value = cleaned_record[field]

                if not isinstance(cleaners, list):
                    raise DataError(f"Cleaners for field '{field}' must be a list")

                for cleaner in cleaners:
                    if not callable(cleaner):
                        raise DataError(
                            f"Cleaner for field '{field}' is not callable: {cleaner}"
                        )

                    try:
                        value = cleaner(value)
                    except Exception as e:
                        raise DataError(
                            f"Error applying cleaner to field '{field}': {e}"
                        )

                cleaned_record[field] = value

        cleaned_data.append(cleaned_record)

    return cleaned_data


def deduplicate_records(
    data: List[Dict[str, Any]], key_fields: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Remove duplicate records from a list.

    Args:
        data: List of dictionaries
        key_fields: List of fields to use for deduplication (None for all fields)

    Returns:
        List with duplicates removed

    Raises:
        DataError: If data is not a list, key_fields is empty, or a record is missing a key field

    Example:
        >>> data = [{"name": "Alice", "age": 25}, {"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
        >>> deduplicate_records(data)
        [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
    """
    if not isinstance(data, list):
        raise DataError("Data must be a list")

    if key_fields is not None and not key_fields:
        raise DataError("key_fields cannot be empty")

    seen = set()
    deduplicated_data = []

    for i, record in enumerate(data):
        if not isinstance(record, dict):
            raise DataError(
                f"Record at index {i} is not a dictionary: {type(record).__name__}"
            )

        # Create a key based on specified fields or all fields
        if key_fields:
            # Check if all key fields are present in the record
            missing_fields = [field for field in key_fields if field not in record]
            if missing_fields:
                raise DataError(
                    f"Record at index {i} is missing key fields: {missing_fields}"
                )

            key_values = tuple(record[field] for field in key_fields)
        else:
            key_values = tuple(sorted(record.items()))

        if key_values not in seen:
            seen.add(key_values)
            deduplicated_data.append(record)

    return deduplicated_data


def normalize_data(
    data: List[Dict[str, Any]], rules: Dict[str, Callable[[Any], Any]]
) -> List[Dict[str, Any]]:
    """Apply normalization functions to data fields.

    Args:
        data: List of dictionaries
        rules: Dictionary mapping field names to normalization functions

    Returns:
        List with normalized values

    Raises:
        DataError: If data is not a list, rules is not a dictionary, or a normalizer raises an error

    Example:
        >>> data = [{"temp_f": 98.6}, {"temp_f": 100.4}]
        >>> rules = {"temp_f": lambda f: round((f - 32) * 5 / 9, 1)}
        >>> normalize_data(data, rules)
        [{"temp_f": 37.0}, {"temp_f": 38.0}]
    """
    if not isinstance(data, list):
        raise DataError("Data must be a list")

    if not isinstance(rules, dict):
        raise DataError("Rules must be a dictionary")

    normalized_data = []

    for i, record in enumerate(data):
        if not isinstance(record, dict):
            raise DataError(
                f"Record at index {i} is not a dictionary: {type(record).__name__}"
            )

        normalized_record = record.copy()

        for field, normalizer in rules.items():
            if field in normalized_record:
                value = normalized_record[field]

                if not callable(normalizer):
                    raise DataError(f"Normalizer for field '{field}' is not callable")

                try:
                    normalized_record[field] = normalizer(value)
                except Exception as e:
                    raise DataError(f"Error normalizing field '{field}': {e}")

        normalized_data.append(normalized_record)

    return normalized_data


def pivot_data(
    data: List[Dict[str, Any]], index_field: str, column_field: str, value_field: str
) -> Dict[Any, Dict[Any, Any]]:
    """Pivot data from long format to wide format.

    Args:
        data: List of dictionaries in long format
        index_field: Field to use as row index
        column_field: Field to use as column headers
        value_field: Field containing values to pivot

    Returns:
        Dictionary with pivoted data

    Raises:
        DataError: If data is not a list or if any record is missing required fields

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

    pivoted: Dict[Any, Dict[Any, Any]] = {}

    for i, record in enumerate(data):
        if not isinstance(record, dict):
            raise DataError(
                f"Record at index {i} is not a dictionary: {type(record).__name__}"
            )

        if (
            index_field not in record
            or column_field not in record
            or value_field not in record
        ):
            missing_fields = []
            if index_field not in record:
                missing_fields.append(index_field)
            if column_field not in record:
                missing_fields.append(column_field)
            if value_field not in record:
                missing_fields.append(value_field)
            raise DataError(
                f"Record at index {i} is missing required fields: {missing_fields}"
            )

        index_val = record[index_field]
        column_val = record[column_field]
        value_val = record[value_field]

        if index_val not in pivoted:
            pivoted[index_val] = {}

        pivoted[index_val][column_val] = value_val

    return pivoted


def transform_data_simple(
    data: List[Dict[str, Any]], mapping: Dict[str, str]
) -> List[Dict[str, Any]]:
    """Apply a simple transformation mapping to a list of data records.

    This is a simplified version of transform_data for LLM agent compatibility.
    Only supports field renaming (no transformation functions).

    Args:
        data: List of dictionary records to transform
        mapping: Dictionary mapping source fields to new field names

    Returns:
        Transformed list of dictionaries

    Raises:
        DataError: If data is not a list or mapping is not a dictionary

    Example:
        >>> data = [{"name": "John Doe", "age": "42"}]
        >>> mapping = {"name": "full_name", "age": "user_age"}
        >>> transform_data_simple(data, mapping)
        [{"full_name": "John Doe", "user_age": "42"}]
    """
    if not isinstance(data, list):
        raise DataError("Data must be a list of dictionaries")
    if not isinstance(mapping, dict):
        raise DataError("Mapping must be a dictionary")

    transformed_data = []

    for record in data:
        if not isinstance(record, dict):
            raise DataError(f"Expected dictionary, got {type(record).__name__}")

        transformed_record = {}

        for source_field, new_field in mapping.items():
            if source_field in record:
                if not isinstance(new_field, str):
                    raise DataError(
                        f"Invalid mapping for field '{source_field}': must be string"
                    )
                transformed_record[new_field] = record[source_field]

        # Include fields not in mapping as-is
        for field, value in record.items():
            if field not in mapping and field not in transformed_record:
                transformed_record[field] = value

        transformed_data.append(transformed_record)

    return transformed_data


def rename_fields_simple(
    data: List[Dict[str, Any]], field_mapping: Dict[str, str]
) -> List[Dict[str, Any]]:
    """Rename fields in a list of dictionaries.

    This is an alias for transform_data_simple for LLM agent compatibility.

    Args:
        data: List of dictionaries
        field_mapping: Mapping of old field names to new field names

    Returns:
        List with renamed fields

    Example:
        >>> data = [{"first": "Alice", "last": "Smith"}]
        >>> rename_fields_simple(data, {"first": "first_name", "last": "last_name"})
        [{"first_name": "Alice", "last_name": "Smith"}]
    """
    return transform_data_simple(data, field_mapping)


def convert_data_types_simple(
    data: List[Dict[str, Any]], type_mapping: Dict[str, str]
) -> List[Dict[str, Any]]:
    """Convert data types for specified fields using string type names.

    This is a simplified version of convert_data_types for LLM agent compatibility.

    Args:
        data: List of dictionaries
        type_mapping: Mapping of field names to type names as strings ("int", "float", "str", "bool")

    Returns:
        List with converted data types

    Raises:
        DataError: If data is not a list, type_mapping is not a dictionary, or type name is invalid

    Example:
        >>> data = [{"age": "25", "score": "95.5"}]
        >>> convert_data_types_simple(data, {"age": "int", "score": "float"})
        [{"age": 25, "score": 95.5}]
    """
    if not isinstance(data, list):
        raise DataError("Data must be a list")
    if not isinstance(type_mapping, dict):
        raise DataError("Type mapping must be a dictionary")

    converted_data = []

    type_functions: Dict[str, Callable[[Any], Any]] = {
        "str": str,
        "int": int,
        "float": float,
        "bool": lambda x: bool(x)
        if x in (0, 1)
        else x.lower() in ("true", "yes", "1")
        if isinstance(x, str)
        else bool(x),
    }

    for i, record in enumerate(data):
        if not isinstance(record, dict):
            raise DataError(
                f"Record at index {i} is not a dictionary: {type(record).__name__}"
            )

        converted_record = record.copy()

        for field, type_name in type_mapping.items():
            if field in converted_record and converted_record[field] is not None:
                if type_name not in type_functions:
                    raise DataError(
                        f"Invalid type name: {type_name}. Must be one of: str, int, float, bool"
                    )

                try:
                    converted_record[field] = type_functions[type_name](
                        converted_record[field]
                    )
                except ValueError as e:
                    raise DataError(
                        f"Error converting field '{field}' to {type_name}: {e}"
                    )

        converted_data.append(converted_record)

    return converted_data


def clean_data_simple(
    data: List[Dict[str, Any]], rules: Dict[str, str]
) -> List[Dict[str, Any]]:
    """Clean data according to simple string-based rules.

    This is a simplified version of clean_data for LLM agent compatibility.

    Args:
        data: List of dictionaries to clean
        rules: Dictionary mapping field names to cleaning operations ("strip", "lower", "upper", "title")

    Returns:
        Cleaned data

    Raises:
        DataError: If data is not a list, rules is not a dictionary, or rule is invalid

    Example:
        >>> data = [{"name": "  John  ", "email": "JOHN@example.com"}]
        >>> rules = {"name": "strip", "email": "lower"}
        >>> clean_data_simple(data, rules)
        [{"name": "John", "email": "john@example.com"}]
    """
    if not isinstance(data, list):
        raise DataError("Data must be a list")
    if not isinstance(rules, dict):
        raise DataError("Rules must be a dictionary")

    cleaned_data = []

    cleaning_functions: Dict[str, Callable[[str], str]] = {
        "strip": str.strip,
        "lower": str.lower,
        "upper": str.upper,
        "title": str.title,
        "capitalize": str.capitalize,
    }

    for i, record in enumerate(data):
        if not isinstance(record, dict):
            raise DataError(
                f"Record at index {i} is not a dictionary: {type(record).__name__}"
            )

        cleaned_record = record.copy()

        for field, rule in rules.items():
            if field in cleaned_record and cleaned_record[field] is not None:
                if not isinstance(rule, str):
                    raise DataError(f"Rule for field '{field}' must be a string")

                if rule not in cleaning_functions:
                    raise DataError(
                        f"Invalid cleaning rule: {rule}. Must be one of: {', '.join(cleaning_functions.keys())}"
                    )

                try:
                    value = str(cleaned_record[field])
                    cleaned_record[field] = cleaning_functions[rule](value)
                except Exception as e:
                    raise DataError(
                        f"Error applying rule '{rule}' to field '{field}': {e}"
                    )

        cleaned_data.append(cleaned_record)

    return cleaned_data


def deduplicate_records_simple(
    data: List[Dict[str, Any]], key_fields: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Remove duplicate records from a list.

    This is a simplified version of deduplicate_records for LLM agent compatibility.

    Args:
        data: List of dictionaries
        key_fields: List of fields to use for deduplication (None for all fields)

    Returns:
        List with duplicates removed

    Raises:
        DataError: If data is not a list

    Example:
        >>> data = [{"name": "Alice", "age": 25}, {"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
        >>> deduplicate_records_simple(data, ["name"])
        [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
    """
    if not isinstance(data, list):
        raise DataError("Data must be a list")

    # If no key fields specified, use all fields
    if key_fields is None:
        return deduplicate_records(data)

    seen = set()
    deduplicated_data = []

    for i, record in enumerate(data):
        if not isinstance(record, dict):
            raise DataError(
                f"Record at index {i} is not a dictionary: {type(record).__name__}"
            )

        # Create a key based on specified fields
        key_values = tuple(str(record.get(field, "")) for field in key_fields)

        if key_values not in seen:
            seen.add(key_values)
            deduplicated_data.append(record)

    return deduplicated_data
