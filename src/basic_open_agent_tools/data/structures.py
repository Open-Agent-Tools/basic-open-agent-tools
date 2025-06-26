"""Data structure manipulation utilities for AI agents."""

import re

from ..exceptions import DataError


def flatten_dict_simple(data: dict, separator: str = ".") -> dict:
    """Flatten nested dictionaries into a single level.

    Args:
        data: Dictionary to flatten
        separator: String to separate nested keys

    Returns:
        Flattened dictionary with dot-separated keys

    Example:
        >>> data = {"a": {"b": {"c": 1}}, "d": 2}
        >>> flatten_dict_simple(data)
        {"a.b.c": 1, "d": 2}
    """

    def _flatten(obj, parent_key=""):
        items = []
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


def unflatten_dict(data: dict, separator: str = ".") -> dict:
    """Reconstruct nested dictionary from flattened structure.

    Args:
        data: Flattened dictionary to unflatten
        separator: String that separates nested keys

    Returns:
        Nested dictionary structure

    Example:
        >>> data = {"a.b.c": 1, "d": 2}
        >>> unflatten_dict(data)
        {"a": {"b": {"c": 1}}, "d": 2}
    """
    result = {}
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


def get_nested_value_simple(data: dict, key_path: str, default=None):
    """Safely access nested dictionary values using dot notation.

    Args:
        data: Dictionary to access
        key_path: Dot-separated path to the value
        default: Default value if key path not found

    Returns:
        Value at the key path or default

    Example:
        >>> data = {"a": {"b": {"c": 1}}}
        >>> get_nested_value_simple(data, "a.b.c")
        1
        >>> get_nested_value_simple(data, "a.b.x", "missing")
        "missing"
    """
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


def set_nested_value(data: dict, key_path: str, value) -> dict:
    """Set nested dictionary value using dot notation (immutable).

    Args:
        data: Dictionary to update
        key_path: Dot-separated path to set
        value: Value to set at the path

    Returns:
        New dictionary with updated value

    Example:
        >>> data = {"a": {"b": 1}}
        >>> set_nested_value(data, "a.c", 2)
        {"a": {"b": 1, "c": 2}}
    """
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


def merge_dicts_simple(dicts: list, deep: bool = True) -> dict:
    """Deep merge multiple dictionaries.

    Args:
        dicts: List of dictionaries to merge
        deep: Whether to perform deep merge

    Returns:
        Merged dictionary

    Example:
        >>> dict1 = {"a": {"b": 1}, "c": 2}
        >>> dict2 = {"a": {"d": 3}, "e": 4}
        >>> merge_dicts_simple([dict1, dict2])
        {"a": {"b": 1, "d": 3}, "c": 2, "e": 4}
    """
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


def compare_data_structures(data1, data2, ignore_order: bool = False) -> bool:
    """Compare two data structures for equality.

    Args:
        data1: First data structure
        data2: Second data structure
        ignore_order: Whether to ignore order in lists

    Returns:
        True if structures are equal

    Example:
        >>> compare_data_structures({"a": [1, 2]}, {"a": [2, 1]}, ignore_order=True)
        True
        >>> compare_data_structures({"a": [1, 2]}, {"a": [2, 1]})
        False
    """
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


def safe_get(data: dict, key: str, default=None):
    """Safely get value from dictionary with default.

    Args:
        data: Dictionary to access
        key: Key to retrieve
        default: Default value if key not found

    Returns:
        Value for key or default

    Example:
        >>> safe_get({"a": 1}, "a")
        1
        >>> safe_get({"a": 1}, "b", "missing")
        "missing"
    """
    return data.get(key, default)


def remove_empty_values(data: dict, recursive: bool = True) -> dict:
    """Remove empty values from dictionary.

    Args:
        data: Dictionary to clean
        recursive: Whether to recursively clean nested dictionaries

    Returns:
        Dictionary with empty values removed

    Example:
        >>> data = {"a": "", "b": {"c": None, "d": 1}, "e": []}
        >>> remove_empty_values(data)
        {"b": {"d": 1}}
    """

    def _is_empty(value):
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


def extract_keys(data: dict, key_pattern: str) -> list:
    """Extract keys matching a pattern from dictionary.

    Args:
        data: Dictionary to search
        key_pattern: Regular expression pattern to match keys

    Returns:
        List of matching keys

    Example:
        >>> data = {"user_name": "Alice", "user_age": 25, "admin_role": "super"}
        >>> extract_keys(data, r"user_.*")
        ["user_name", "user_age"]
    """
    try:
        pattern = re.compile(key_pattern)
    except re.error as e:
        raise DataError(f"Invalid regular expression pattern: {e}")

    return [key for key in data.keys() if pattern.match(key)]


def rename_keys(data: dict, key_mapping: dict) -> dict:
    """Rename dictionary keys according to mapping.

    Args:
        data: Dictionary to rename keys in
        key_mapping: Mapping of old keys to new keys

    Returns:
        Dictionary with renamed keys

    Example:
        >>> data = {"old_name": "Alice", "old_age": 25}
        >>> mapping = {"old_name": "name", "old_age": "age"}
        >>> rename_keys(data, mapping)
        {"name": "Alice", "age": 25}
    """
    result = {}
    for key, value in data.items():
        new_key = key_mapping.get(key, key)
        result[new_key] = value

    return result
