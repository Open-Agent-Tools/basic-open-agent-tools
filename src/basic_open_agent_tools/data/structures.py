"""Data structure manipulation utilities for AI agents."""

import re
from typing import Any, Dict, List, Tuple

from ..exceptions import DataError
from ..types import DataDict


def flatten_dict(data: DataDict, separator: str = ".") -> DataDict:
    """Flatten nested dictionaries into a single level.

    Args:
        data: Dictionary to flatten
        separator: String to separate nested keys

    Returns:
        Flattened dictionary with dot-separated keys

    Raises:
        TypeError: If arguments have wrong types
        DataError: If separator is empty or invalid

    Example:
        >>> data = {"a": {"b": {"c": 1}}, "d": 2}
        >>> flatten_dict(data)
        {"a.b.c": 1, "d": 2}
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")
    if not isinstance(separator, str):
        raise TypeError("separator must be a string")
    if not separator:
        raise DataError("separator cannot be empty")

    def _flatten(obj: Any, parent_key: str = "") -> DataDict:
        items: List[Tuple[str, Any]] = []
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_key = f"{parent_key}{separator}{key}" if parent_key else key
                if isinstance(value, dict):
                    items.extend(_flatten(value, new_key).items())
                else:
                    items.append((new_key, value))
        else:
            items.append((parent_key, obj))
        return dict(items)

    return _flatten(data)


def unflatten_dict(data: DataDict, separator: str = ".") -> DataDict:
    """Reconstruct nested dictionary from flattened structure.

    Args:
        data: Flattened dictionary to unflatten
        separator: String that separates nested keys

    Returns:
        Nested dictionary structure

    Raises:
        TypeError: If arguments have wrong types
        DataError: If separator is empty or invalid

    Example:
        >>> data = {"a.b.c": 1, "d": 2}
        >>> unflatten_dict(data)
        {"a": {"b": {"c": 1}}, "d": 2}
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")
    if not isinstance(separator, str):
        raise TypeError("separator must be a string")
    if not separator:
        raise DataError("separator cannot be empty")

    result: DataDict = {}
    for key, value in data.items():
        parts = key.split(separator)
        current = result

        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                # Handle conflict - existing value is not a dict
                current[part] = {}
            current = current[part]

        current[parts[-1]] = value

    return result


def get_nested_value(data: DataDict, key_path: str, default: Any = None) -> Any:
    """Safely access nested dictionary values using dot notation.

    Args:
        data: Dictionary to access
        key_path: Dot-separated path to the value
        default: Default value if key path not found

    Returns:
        Value at the key path or default

    Raises:
        TypeError: If arguments have wrong types

    Example:
        >>> data = {"a": {"b": {"c": 1}}}
        >>> get_nested_value(data, "a.b.c")
        1
        >>> get_nested_value(data, "a.b.x", "missing")
        "missing"
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")
    if not isinstance(key_path, str):
        raise TypeError("key_path must be a string")

    if not key_path:
        return data

    keys = key_path.split(".")
    current = data

    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default


def set_nested_value(data: DataDict, key_path: str, value: Any) -> DataDict:
    """Set nested dictionary value using dot notation (immutable).

    Args:
        data: Dictionary to update
        key_path: Dot-separated path to set
        value: Value to set at the path

    Returns:
        New dictionary with updated value

    Raises:
        TypeError: If arguments have wrong types
        DataError: If key_path is empty

    Example:
        >>> data = {"a": {"b": 1}}
        >>> set_nested_value(data, "a.c", 2)
        {"a": {"b": 1, "c": 2}}
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")
    if not isinstance(key_path, str):
        raise TypeError("key_path must be a string")
    if not key_path:
        raise DataError("key_path cannot be empty")

    import copy

    result = copy.deepcopy(data)
    keys = key_path.split(".")
    current = result

    # Navigate to the parent of the target key
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        elif not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]

    # Set the final value
    current[keys[-1]] = value
    return result


def merge_dicts(*dicts: DataDict, deep: bool = True) -> DataDict:
    """Deep merge multiple dictionaries.

    Args:
        *dicts: Dictionaries to merge
        deep: Whether to perform deep merge

    Returns:
        Merged dictionary

    Raises:
        TypeError: If arguments have wrong types

    Example:
        >>> dict1 = {"a": {"b": 1}, "c": 2}
        >>> dict2 = {"a": {"d": 3}, "e": 4}
        >>> merge_dicts(dict1, dict2)
        {"a": {"b": 1, "d": 3}, "c": 2, "e": 4}
    """
    if not all(isinstance(d, dict) for d in dicts):
        raise TypeError("All arguments must be dictionaries")
    if not isinstance(deep, bool):
        raise TypeError("deep must be a boolean")

    if not dicts:
        return {}

    import copy

    result = copy.deepcopy(dicts[0]) if deep else dicts[0].copy()

    for dictionary in dicts[1:]:
        if deep:
            _deep_merge(result, dictionary)
        else:
            result.update(dictionary)

    return result


def _deep_merge(target: dict, source: dict) -> None:
    """Helper function for deep merging dictionaries."""
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _deep_merge(target[key], value)
        else:
            target[key] = value


def compare_data_structures(data1: Any, data2: Any, ignore_order: bool = False) -> bool:
    """Compare two data structures for equality.

    Args:
        data1: First data structure
        data2: Second data structure
        ignore_order: Whether to ignore order in lists

    Returns:
        True if structures are equal

    Raises:
        TypeError: If ignore_order is not boolean

    Example:
        >>> compare_data_structures({"a": [1, 2]}, {"a": [2, 1]}, ignore_order=True)
        True
        >>> compare_data_structures({"a": [1, 2]}, {"a": [2, 1]})
        False
    """
    if not isinstance(ignore_order, bool):
        raise TypeError("ignore_order must be a boolean")

    if type(data1) is not type(data2):
        return False

    if isinstance(data1, dict):
        if data1.keys() != data2.keys():
            return False
        return all(
            compare_data_structures(data1[key], data2[key], ignore_order)
            for key in data1.keys()
        )
    elif isinstance(data1, list):
        if len(data1) != len(data2):
            return False
        if ignore_order:
            # Sort both lists for comparison (if elements are comparable)
            try:
                return sorted(data1) == sorted(data2)
            except TypeError:
                # If not sortable, check if all elements from data1 are in data2
                data2_copy = data2.copy()
                for item in data1:
                    try:
                        data2_copy.remove(item)
                    except ValueError:
                        return False
                return len(data2_copy) == 0
        else:
            return all(
                compare_data_structures(data1[i], data2[i], ignore_order)
                for i in range(len(data1))
            )
    else:
        return bool(data1 == data2)


def safe_get(data: DataDict, key: str, default: Any = None) -> Any:
    """Safely get value from dictionary with default.

    Args:
        data: Dictionary to access
        key: Key to retrieve
        default: Default value if key not found

    Returns:
        Value for key or default

    Raises:
        TypeError: If data is not a dictionary

    Example:
        >>> safe_get({"a": 1}, "a")
        1
        >>> safe_get({"a": 1}, "b", "missing")
        "missing"
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")
    return data.get(key, default)


def remove_empty_values(data: DataDict, recursive: bool = True) -> DataDict:
    """Remove empty values from dictionary.

    Args:
        data: Dictionary to clean
        recursive: Whether to recursively clean nested dictionaries

    Returns:
        Dictionary with empty values removed

    Raises:
        TypeError: If arguments have wrong types

    Example:
        >>> data = {"a": "", "b": {"c": None, "d": 1}, "e": []}
        >>> remove_empty_values(data)
        {"b": {"d": 1}}
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")
    if not isinstance(recursive, bool):
        raise TypeError("recursive must be a boolean")

    def _is_empty(value: Any) -> bool:
        return value is None or value == "" or value == [] or value == {}

    result = {}
    for key, value in data.items():
        if isinstance(value, dict) and recursive:
            cleaned = remove_empty_values(value, recursive)
            if cleaned:  # Only add if not empty after cleaning
                result[key] = cleaned
        elif not _is_empty(value):
            result[key] = value

    return result


def extract_keys(data: DataDict, key_pattern: str) -> List[str]:
    """Extract keys matching a pattern from dictionary.

    Args:
        data: Dictionary to search
        key_pattern: Regular expression pattern to match keys

    Returns:
        List of matching keys

    Raises:
        TypeError: If arguments have wrong types
        DataError: If pattern is invalid

    Example:
        >>> data = {"user_name": "Alice", "user_age": 25, "admin_role": "super"}
        >>> extract_keys(data, r"user_.*")
        ["user_name", "user_age"]
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")
    if not isinstance(key_pattern, str):
        raise TypeError("key_pattern must be a string")

    try:
        pattern = re.compile(key_pattern)
    except re.error as e:
        raise DataError(f"Invalid regular expression pattern: {e}")

    return [key for key in data.keys() if pattern.match(key)]


def rename_keys(data: DataDict, key_mapping: Dict[str, str]) -> DataDict:
    """Rename dictionary keys according to mapping.

    Args:
        data: Dictionary to rename keys in
        key_mapping: Mapping of old keys to new keys

    Returns:
        Dictionary with renamed keys

    Raises:
        TypeError: If arguments have wrong types

    Example:
        >>> data = {"old_name": "Alice", "old_age": 25}
        >>> mapping = {"old_name": "name", "old_age": "age"}
        >>> rename_keys(data, mapping)
        {"name": "Alice", "age": 25}
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")
    if not isinstance(key_mapping, dict):
        raise TypeError("key_mapping must be a dictionary")

    result = {}
    for key, value in data.items():
        new_key = key_mapping.get(key, key)
        result[new_key] = value

    return result
