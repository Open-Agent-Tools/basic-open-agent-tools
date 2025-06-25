"""Data transformation tools for AI agents.

This module provides functions for transforming, cleaning, and manipulating
structured data like dictionaries and lists of records.
"""

import copy
from collections import defaultdict
from typing import Any, Callable, Dict, List, TypeVar, Union

from ..exceptions import DataError

T = TypeVar("T")
DataRecord = Dict[str, Any]
DataList = List[DataRecord]
TransformationFunc = Callable[[Any], Any]
TransformationMap = Dict[str, Union[str, TransformationFunc]]


def transform_data(data: DataList, mapping: TransformationMap) -> DataList:
    """Apply a transformation mapping to a list of data records.

    This function applies a set of transformations to each record in a list.
    The mapping can specify both field renaming and value transformations.

    Args:
        data: List of dictionary records to transform
        mapping: Dictionary mapping source fields to either:
            - A string (for simple field renaming)
            - A function (to transform the field's value)

    Returns:
        New list of transformed records

    Raises:
        DataError: If the input data is not a list of dictionaries

    Example:
        >>> data = [{"name": "John Doe", "age": "42"}]
        >>> mapping = {"name": "full_name", "age": lambda x: int(x)}
        >>> transform_data(data, mapping)
        [{"full_name": "John Doe", "age": 42}]
    """
    if not isinstance(data, list):
        raise DataError("Input data must be a list of records")

    result = []

    for record in data:
        if not isinstance(record, dict):
            raise DataError("Each record must be a dictionary")

        new_record = copy.deepcopy(record)

        for src_field, transform in mapping.items():
            if src_field not in record:
                continue

            value = record[src_field]

            if isinstance(transform, str):
                # Simple field renaming
                new_record[transform] = value
                if transform != src_field:
                    del new_record[src_field]
            elif callable(transform):
                # Value transformation
                new_record[src_field] = transform(value)
            else:
                raise DataError(
                    f"Invalid transformation for field '{src_field}': must be string or callable"
                )

        result.append(new_record)

    return result


def rename_fields(data: DataList, field_mapping: Dict[str, str]) -> DataList:
    """Rename fields in a list of data records.

    Args:
        data: List of dictionary records
        field_mapping: Dictionary mapping old field names to new field names

    Returns:
        New list of records with renamed fields

    Raises:
        DataError: If the input data is not a list of dictionaries

    Example:
        >>> data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
        >>> rename_fields(data, {"name": "full_name", "age": "years"})
        [{"full_name": "John", "years": 30}, {"full_name": "Jane", "years": 25}]
    """
    if not isinstance(data, list):
        raise DataError("Input data must be a list of records")

    result = []

    for record in data:
        if not isinstance(record, dict):
            raise DataError("Each record must be a dictionary")

        new_record = copy.deepcopy(record)

        for old_field, new_field in field_mapping.items():
            if old_field in new_record:
                new_record[new_field] = new_record[old_field]
                if old_field != new_field:
                    del new_record[old_field]

        result.append(new_record)

    return result


def convert_data_types(
    data: DataList, type_conversions: Dict[str, Callable[[Any], Any]]
) -> DataList:
    """Convert field values to specified types in a list of data records.

    Args:
        data: List of dictionary records
        type_conversions: Dictionary mapping field names to conversion functions

    Returns:
        New list of records with converted field values

    Raises:
        DataError: If the input data is not a list of dictionaries
        ValueError: If a conversion function fails

    Example:
        >>> data = [{"id": "1", "amount": "42.5", "active": "true"}]
        >>> conversions = {
        ...     "id": int,
        ...     "amount": float,
        ...     "active": lambda x: x.lower() == "true"
        ... }
        >>> convert_data_types(data, conversions)
        [{"id": 1, "amount": 42.5, "active": True}]
    """
    if not isinstance(data, list):
        raise DataError("Input data must be a list of records")

    result = []

    for record in data:
        if not isinstance(record, dict):
            raise DataError("Each record must be a dictionary")

        new_record = copy.deepcopy(record)

        for field, converter in type_conversions.items():
            if field in new_record and new_record[field] is not None:
                try:
                    new_record[field] = converter(new_record[field])
                except Exception as e:
                    raise ValueError(
                        f"Failed to convert field '{field}' with value '{new_record[field]}': {str(e)}"
                    )

        result.append(new_record)

    return result


def apply_data_transformations(
    data: DataList, transformations: List[Callable[[DataList], DataList]]
) -> DataList:
    """Apply multiple transformation functions to data in sequence.

    Args:
        data: List of dictionary records
        transformations: List of transformation functions to apply in order

    Returns:
        Transformed data after applying all transformations

    Raises:
        DataError: If any transformation doesn't return a list of dictionaries

    Example:
        >>> data = [{"name": "John Doe", "age": "42"}]
        >>> def clean_names(d):
        ...     return [{"name": r["name"].upper(), **{k:v for k,v in r.items() if k != "name"}} for r in d]
        >>> def convert_ages(d):
        ...     return [{**r, "age": int(r["age"])} for r in d]
        >>> apply_data_transformations(data, [clean_names, convert_ages])
        [{"name": "JOHN DOE", "age": 42}]
    """
    if not isinstance(data, list):
        raise DataError("Input data must be a list of records")

    result = copy.deepcopy(data)

    for transform_func in transformations:
        if not callable(transform_func):
            raise DataError("Each transformation must be a callable function")

        result = transform_func(result)

        if not isinstance(result, list):
            raise DataError("Each transformation must return a list of records")

        if result and not all(isinstance(r, dict) for r in result):
            raise DataError(
                "Each transformation must return a list of dictionary records"
            )

    return result


def clean_data(
    data: DataList, rules: Dict[str, List[Callable[[Any], Any]]]
) -> DataList:
    """Apply cleaning rules to data fields.

    Args:
        data: List of dictionary records
        rules: Dictionary mapping field names to lists of cleaning functions

    Returns:
        New list of records with cleaned field values

    Raises:
        DataError: If the input data is not a list of dictionaries

    Example:
        >>> data = [{"name": "  John  ", "email": "JOHN@example.com"}]
        >>> rules = {
        ...     "name": [str.strip, str.title],
        ...     "email": [str.lower]
        ... }
        >>> clean_data(data, rules)
        [{"name": "John", "email": "john@example.com"}]
    """
    if not isinstance(data, list):
        raise DataError("Input data must be a list of records")

    result = []

    for record in data:
        if not isinstance(record, dict):
            raise DataError("Each record must be a dictionary")

        new_record = copy.deepcopy(record)

        for field, cleaners in rules.items():
            if field in new_record and new_record[field] is not None:
                value = new_record[field]

                for cleaner in cleaners:
                    if not callable(cleaner):
                        raise DataError(
                            f"Cleaning rule for field '{field}' must be callable"
                        )

                    try:
                        value = cleaner(value)
                    except Exception as e:
                        raise DataError(
                            f"Failed to apply cleaner to field '{field}': {str(e)}"
                        )

                new_record[field] = value

        result.append(new_record)

    return result


def deduplicate_records(data: DataList, key_fields: List[str]) -> DataList:
    """Remove duplicate records based on specified key fields.

    Args:
        data: List of dictionary records
        key_fields: List of field names that form a unique key

    Returns:
        New list with duplicates removed (keeping first occurrence)

    Raises:
        DataError: If the input data is not a list of dictionaries

    Example:
        >>> data = [
        ...     {"id": 1, "name": "John", "dept": "HR"},
        ...     {"id": 2, "name": "Jane", "dept": "IT"},
        ...     {"id": 1, "name": "John", "dept": "Sales"}
        ... ]
        >>> deduplicate_records(data, ["id"])
        [{"id": 1, "name": "John", "dept": "HR"}, {"id": 2, "name": "Jane", "dept": "IT"}]
    """
    if not isinstance(data, list):
        raise DataError("Input data must be a list of records")

    if not key_fields:
        raise DataError("At least one key field must be specified")

    result = []
    seen_keys = set()

    for record in data:
        if not isinstance(record, dict):
            raise DataError("Each record must be a dictionary")

        # Create a tuple of the key field values
        try:
            key_values = tuple(record[field] for field in key_fields)
        except KeyError as e:
            raise DataError(f"Key field {str(e)} not found in record")

        # Only add the record if we haven't seen this key before
        if key_values not in seen_keys:
            seen_keys.add(key_values)
            result.append(copy.deepcopy(record))

    return result


def normalize_data(
    data: DataList, normalization_rules: Dict[str, Callable[[Any], Any]]
) -> DataList:
    """Normalize data values according to specified rules.

    Args:
        data: List of dictionary records
        normalization_rules: Dictionary mapping field names to normalization functions

    Returns:
        New list of records with normalized field values

    Raises:
        DataError: If the input data is not a list of dictionaries

    Example:
        >>> data = [{"temp_f": 98.6}, {"temp_f": 100.4}]
        >>> rules = {"temp_f": lambda f: (f - 32) * 5/9}
        >>> normalize_data(data, rules)
        [{"temp_f": 37.0}, {"temp_f": 38.0}]
    """
    if not isinstance(data, list):
        raise DataError("Input data must be a list of records")

    result = []

    for record in data:
        if not isinstance(record, dict):
            raise DataError("Each record must be a dictionary")

        new_record = copy.deepcopy(record)

        for field, normalizer in normalization_rules.items():
            if field in new_record and new_record[field] is not None:
                try:
                    new_record[field] = normalizer(new_record[field])
                except Exception as e:
                    raise DataError(f"Failed to normalize field '{field}': {str(e)}")

        result.append(new_record)

    return result


def pivot_data(
    data: DataList, row_key: str, col_key: str, value_key: str
) -> Dict[Any, Dict[Any, Any]]:
    """Transform a list of records into a pivot table structure.

    Args:
        data: List of dictionary records
        row_key: Field name to use for row identifiers
        col_key: Field name to use for column identifiers
        value_key: Field name containing the values to pivot

    Returns:
        Nested dictionary with row_key values as outer keys and col_key values as inner keys

    Raises:
        DataError: If the input data is not a list of dictionaries or required keys are missing

    Example:
        >>> data = [
        ...     {"product": "Apple", "region": "East", "sales": 100},
        ...     {"product": "Apple", "region": "West", "sales": 150},
        ...     {"product": "Banana", "region": "East", "sales": 200},
        ...     {"product": "Banana", "region": "West", "sales": 250}
        ... ]
        >>> pivot_data(data, "product", "region", "sales")
        {
            "Apple": {"East": 100, "West": 150},
            "Banana": {"East": 200, "West": 250}
        }
    """
    if not isinstance(data, list):
        raise DataError("Input data must be a list of records")

    result: Dict[Any, Dict[Any, Any]] = defaultdict(dict)

    for record in data:
        if not isinstance(record, dict):
            raise DataError("Each record must be a dictionary")

        try:
            row = record[row_key]
            col = record[col_key]
            value = record[value_key]
        except KeyError as e:
            raise DataError(f"Required key {str(e)} not found in record")

        result[row][col] = value

    # Convert defaultdict to regular dict
    return {k: dict(v) for k, v in result.items()}
