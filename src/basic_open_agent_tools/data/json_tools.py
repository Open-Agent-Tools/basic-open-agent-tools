"""JSON processing utilities for AI agents."""

import json
from typing import Any, Union

from .._logging import get_logger
from ..decorators import strands_tool
from ..exceptions import SerializationError

logger = get_logger("data.json_tools")


@strands_tool
def safe_json_serialize(data: dict, indent: int) -> str:
    """Safely serialize data to JSON string with error handling.

    Args:
        data: Data to serialize to JSON (accepts any serializable type)
        indent: Number of spaces for indentation (0 for compact)

    Returns:
        JSON string representation of the data

    Raises:
        SerializationError: If data cannot be serialized to JSON
        TypeError: If data contains non-serializable objects

    Example:
        >>> safe_json_serialize({"name": "test", "value": 42})
        '{"name": "test", "value": 42}'
        >>> safe_json_serialize({"a": 1, "b": 2}, indent=2)
        '{\\n  "a": 1,\\n  "b": 2\\n}'
    """
    data_type = type(data).__name__
    logger.debug(f"Serializing {data_type} to JSON (indent={indent})")

    if not isinstance(indent, int):
        raise TypeError("indent must be an integer")

    try:
        # Use None for compact format when indent is 0
        actual_indent = None if indent == 0 else indent
        result = json.dumps(data, indent=actual_indent, ensure_ascii=False)
        logger.debug(f"JSON serialized: {len(result)} characters")
        return result
    except (TypeError, ValueError) as e:
        logger.error(f"JSON serialization error: {e}")
        raise SerializationError(f"Failed to serialize data to JSON: {e}")


@strands_tool
def safe_json_deserialize(json_str: str) -> dict:
    """Safely deserialize JSON string to Python object with error handling.

    Args:
        json_str: JSON string to deserialize

    Returns:
        Deserialized Python object

    Raises:
        SerializationError: If JSON string cannot be parsed
        TypeError: If input is not a string

    Example:
        >>> safe_json_deserialize('{"name": "test", "value": 42}')
        {'name': 'test', 'value': 42}
        >>> safe_json_deserialize('[1, 2, 3]')
        [1, 2, 3]
    """
    if not isinstance(json_str, str):
        raise TypeError("Input must be a string")

    logger.debug(f"Deserializing JSON string ({len(json_str)} characters)")

    try:
        result = json.loads(json_str)
        # Always return dict for agent compatibility
        if isinstance(result, dict):
            final_result = result
        else:
            # Wrap non-dict results in a dict for consistency
            final_result = {"result": result}

        logger.debug(
            f"JSON deserialized: {type(final_result).__name__} with {len(final_result)} keys"
        )
        return final_result
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"JSON deserialization error: {e}")
        raise SerializationError(f"Failed to deserialize JSON string: {e}")


@strands_tool
def validate_json_string(json_str: str) -> bool:
    """Validate JSON string without deserializing.

    Args:
        json_str: JSON string to validate

    Returns:
        True if valid JSON, False otherwise

    Example:
        >>> validate_json_string('{"valid": true}')
        True
        >>> validate_json_string('{"invalid": }')
        False
    """
    if not isinstance(json_str, str):
        logger.debug("[DATA] JSON validation failed: not a string")  # type: ignore[unreachable]
        return False  # False positive - mypy thinks isinstance always narrows, but runtime can differ

    logger.debug(f"Validating JSON string ({len(json_str)} characters)")

    try:
        json.loads(json_str)
        logger.debug("[DATA] JSON validation: valid")
        return True
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"JSON validation failed: {e}")
        return False


@strands_tool
def read_json_file(file_path: str) -> dict:
    """Read JSON data from file.

    This function loads JSON from a file and returns it as a dictionary.
    For large files, consider using get_json_value_at_path or other
    selective functions to reduce token usage.

    Args:
        file_path: Path to the JSON file as a string

    Returns:
        Dictionary containing the JSON data

    Raises:
        TypeError: If file_path is not a string
        SerializationError: If file cannot be read or contains invalid JSON

    Example:
        >>> read_json_file("config.json")
        {'name': 'app', 'version': '1.0', 'settings': {...}}
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    logger.info(f"Reading JSON file: {file_path}")

    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        # Ensure we return a dict
        if isinstance(data, dict):
            result = data
        else:
            result = {"data": data}

        logger.info(f"JSON file loaded: {type(data).__name__}")
        return result
    except FileNotFoundError:
        logger.debug(f"JSON file not found: {file_path}")
        raise SerializationError(f"JSON file not found: {file_path}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        raise SerializationError(f"Invalid JSON in file {file_path}: {e}")
    except OSError as e:
        logger.error(f"File read error: {e}")
        raise SerializationError(f"Failed to read JSON file {file_path}: {e}")


@strands_tool
def write_json_file(data: dict, file_path: str, indent: int, skip_confirm: bool) -> str:
    """Write JSON data to file with permission checking.

    Args:
        data: Dictionary to write as JSON
        file_path: Path where JSON file will be created as a string
        indent: Number of spaces for indentation (0 for compact)
        skip_confirm: If True, skip confirmation and overwrite existing files

    Returns:
        String describing the operation result

    Raises:
        TypeError: If parameters are not the correct types
        SerializationError: If data cannot be serialized or file cannot be written

    Example:
        >>> data = {'name': 'test', 'value': 42}
        >>> write_json_file(data, "output.json", 2, skip_confirm=True)
        "Created JSON file output.json (85 bytes)"
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dict")

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(indent, int):
        raise TypeError("indent must be an integer")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    import os

    from ..confirmation import check_user_confirmation

    file_existed = os.path.exists(file_path)

    logger.info(f"Writing JSON file: {file_path} (indent={indent})")

    if file_existed:
        # Check user confirmation
        key_count = len(data.keys())
        preview = f"Writing JSON with {key_count} top-level keys"
        confirmed, decline_reason = check_user_confirmation(
            operation="overwrite existing JSON file",
            target=file_path,
            skip_confirm=skip_confirm,
            preview_info=preview,
        )

        if not confirmed:
            reason_msg = f" (reason: {decline_reason})" if decline_reason else ""
            logger.debug(f"JSON write cancelled by user: {file_path}{reason_msg}")
            return f"Operation cancelled by user{reason_msg}: {file_path}"

    try:
        # Serialize to JSON
        actual_indent = None if indent == 0 else indent
        json_str = json.dumps(data, indent=actual_indent, ensure_ascii=False)

        # Write to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json_str)

        # Get file size
        file_size = os.path.getsize(file_path)
        action = "Overwrote" if file_existed else "Created"

        result = f"{action} JSON file {file_path} ({file_size} bytes)"
        logger.info(f"JSON written successfully: {file_size} bytes ({action.lower()})")
        return result
    except (TypeError, ValueError) as e:
        logger.error(f"JSON serialization error: {e}")
        raise SerializationError(f"Failed to serialize data to JSON: {e}")
    except OSError as e:
        logger.error(f"File write error: {e}")
        raise SerializationError(f"Failed to write JSON file {file_path}: {e}")


def _parse_json_path(path: str) -> list[str]:
    """Parse a simple JSON path into segments.

    Supports dot notation: "users.0.name" → ["users", "0", "name"]
    """
    if not path or path == ".":
        return []
    return path.split(".")


def _navigate_json_path(data: dict, path_segments: list[str]) -> dict:
    """Navigate to a location in JSON data using path segments.

    Returns a dict with either 'value' or 'error' key.
    """
    current: Any = data

    for segment in path_segments:
        if isinstance(current, dict):
            if segment not in current:
                return {"error": f"Key '{segment}' not found"}
            current = current[segment]
        elif isinstance(current, list):
            try:
                index = int(segment)
                if index < 0 or index >= len(current):
                    return {"error": f"Index {index} out of range"}
                current = current[index]
            except ValueError:
                return {"error": f"Invalid array index: '{segment}'"}
        else:
            return {"error": f"Cannot navigate into {type(current).__name__}"}

    return {"value": current}


@strands_tool
def get_json_value_at_path(data: dict, json_path: str) -> dict:
    """Extract value at JSON path without loading entire structure.

    This function uses dot notation to navigate nested JSON structures
    and return only the requested value, saving tokens.

    Path notation:
    - "key" - access object key
    - "0" - access array index
    - "users.0.name" - nested access

    Args:
        data: JSON data as dictionary
        json_path: Dot-notation path (e.g., "users.0.name")

    Returns:
        Dictionary with either 'value' key (success) or 'error' key (failure)

    Raises:
        TypeError: If parameters are not the correct types

    Example:
        >>> data = {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}
        >>> get_json_value_at_path(data, "users.0.name")
        {'value': 'Alice'}
        >>> get_json_value_at_path(data, "users.5.name")
        {'error': 'Index 5 out of range'}
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dict")

    if not isinstance(json_path, str):
        raise TypeError("json_path must be a string")

    logger.info(f"Getting JSON value at path: {json_path}")

    path_segments = _parse_json_path(json_path)
    result = _navigate_json_path(data, path_segments)

    if "value" in result:
        # Convert value to serializable form
        value = result["value"]
        if isinstance(value, (dict, list, str, int, float, bool, type(None))):
            final_result = {"value": value}
        else:
            final_result = {"value": str(value)}

        logger.info(f"JSON value retrieved at path: {type(value).__name__}")
        return final_result
    else:
        logger.debug(f"JSON path error: {result['error']}")
        return result


@strands_tool
def get_json_keys(data: dict, path: str) -> list[str]:
    """Get keys at JSON path without loading values.

    This function inspects JSON structure without retrieving data values,
    making it token-efficient for understanding large JSON structures.

    Args:
        data: JSON data as dictionary
        path: Dot-notation path to object (empty string for root)

    Returns:
        List of keys at the specified path

    Raises:
        TypeError: If parameters are not the correct types
        SerializationError: If path doesn't lead to an object/array

    Example:
        >>> data = {'users': [{'name': 'Alice', 'age': 25}], 'count': 1}
        >>> get_json_keys(data, "")
        ['users', 'count']
        >>> get_json_keys(data, "users.0")
        ['name', 'age']
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dict")

    if not isinstance(path, str):
        raise TypeError("path must be a string")

    logger.info(f"Getting JSON keys at path: '{path}'")

    if not path:
        # Root level
        keys = list(data.keys())
        logger.info(f"JSON keys retrieved: {len(keys)} keys")
        return keys

    # Navigate to path
    path_segments = _parse_json_path(path)
    nav_result = _navigate_json_path(data, path_segments)

    if "error" in nav_result:
        logger.debug(f"JSON path error: {nav_result['error']}")
        raise SerializationError(f"Path error: {nav_result['error']}")

    value = nav_result["value"]

    if isinstance(value, dict):
        keys = list(value.keys())
        logger.info(f"JSON keys retrieved: {len(keys)} keys")
        return keys
    elif isinstance(value, list):
        # Return indices as strings for arrays
        keys = [str(i) for i in range(len(value))]
        logger.info(f"JSON array indices retrieved: {len(keys)} items")
        return keys
    else:
        raise SerializationError(
            f"Path '{path}' leads to {type(value).__name__}, not object/array"
        )


@strands_tool
def filter_json_array(
    data: dict, array_path: str, key: str, value: str, operator: str
) -> list[dict]:
    """Filter JSON array elements by criteria.

    This function reduces token usage by loading only array elements
    that match specific criteria, similar to filter_csv_rows.

    Supported operators:
    - "equals": Exact match
    - "contains": Value contains search string
    - "startswith": Value starts with search string
    - "endswith": Value ends with search string
    - "greater_than": Numeric comparison (value > search)
    - "less_than": Numeric comparison (value < search)

    Args:
        data: JSON data as dictionary
        array_path: Dot-notation path to array
        key: Key to filter on within array elements
        value: Value to compare against
        operator: Comparison operator

    Returns:
        List of matching array elements as dictionaries

    Raises:
        TypeError: If parameters are not the correct types
        SerializationError: If path doesn't lead to an array or operator is invalid

    Example:
        >>> data = {'users': [{'name': 'Alice', 'age': '25'}, {'name': 'Bob', 'age': '30'}]}
        >>> filter_json_array(data, "users", "name", "Alice", "equals")
        [{'name': 'Alice', 'age': '25'}]
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dict")

    if not isinstance(array_path, str):
        raise TypeError("array_path must be a string")

    if not isinstance(key, str):
        raise TypeError("key must be a string")

    if not isinstance(value, str):
        raise TypeError("value must be a string")

    if not isinstance(operator, str):
        raise TypeError("operator must be a string")

    valid_operators = [
        "equals",
        "contains",
        "startswith",
        "endswith",
        "greater_than",
        "less_than",
    ]
    if operator not in valid_operators:
        raise SerializationError(
            f"Invalid operator: {operator}. Valid: {valid_operators}"
        )

    logger.info(
        f"Filtering JSON array at '{array_path}' WHERE {key} {operator} '{value}'"
    )

    # Navigate to array
    path_segments = _parse_json_path(array_path) if array_path else []
    nav_result = _navigate_json_path(data, path_segments)

    if "error" in nav_result:
        raise SerializationError(f"Path error: {nav_result['error']}")

    array = nav_result["value"]

    if not isinstance(array, list):
        raise SerializationError(
            f"Path '{array_path}' leads to {type(array).__name__}, not array"
        )

    # Filter array
    result: list[dict] = []
    for item in array:
        if not isinstance(item, dict):
            continue

        if key not in item:
            continue

        item_value = str(item[key])

        matches = False
        if operator == "equals":
            matches = item_value == value
        elif operator == "contains":
            matches = value in item_value
        elif operator == "startswith":
            matches = item_value.startswith(value)
        elif operator == "endswith":
            matches = item_value.endswith(value)
        elif operator == "greater_than":
            try:
                matches = float(item_value) > float(value)
            except ValueError:
                matches = False
        elif operator == "less_than":
            try:
                matches = float(item_value) < float(value)
            except ValueError:
                matches = False

        if matches:
            result.append(item)

    logger.info(f"JSON array filtered: {len(result)} matching items")
    return result


@strands_tool
def select_json_keys(data: dict, keys: list[str]) -> dict:
    """Select only specific keys from JSON object, discarding others.

    This function reduces token usage by loading only requested keys
    from large JSON objects, similar to select_csv_columns.

    Args:
        data: JSON data as dictionary
        keys: List of keys to select

    Returns:
        Dictionary containing only the selected keys

    Raises:
        TypeError: If parameters are not the correct types

    Example:
        >>> data = {'name': 'Alice', 'age': 25, 'email': 'a@b.com', 'phone': '123', 'address': '...'}
        >>> select_json_keys(data, ["name", "email"])
        {'name': 'Alice', 'email': 'a@b.com'}
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dict")

    if not isinstance(keys, list):
        raise TypeError("keys must be a list")

    logger.info(f"Selecting {len(keys)} keys from JSON object")

    result = {key: data[key] for key in keys if key in data}

    logger.info(f"JSON keys selected: {len(result)} keys")
    return result


@strands_tool
def slice_json_array(data: dict, array_path: str, start: int, end: int) -> list[dict]:
    """Get slice of JSON array for pagination.

    This function enables efficient pagination through large JSON arrays
    by loading only the requested range, similar to get_csv_row_range.

    Args:
        data: JSON data as dictionary
        array_path: Dot-notation path to array
        start: Starting index (0-based, inclusive)
        end: Ending index (0-based, exclusive)

    Returns:
        List of array elements in the specified range

    Raises:
        TypeError: If parameters are not the correct types
        SerializationError: If path doesn't lead to an array or indices are invalid

    Example:
        >>> data = {'items': [{'id': i} for i in range(100)]}
        >>> slice_json_array(data, "items", 10, 20)
        [{'id': 10}, {'id': 11}, ..., {'id': 19}]
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dict")

    if not isinstance(array_path, str):
        raise TypeError("array_path must be a string")

    if not isinstance(start, int) or start < 0:
        raise TypeError("start must be a non-negative integer")

    if not isinstance(end, int) or end < 0:
        raise TypeError("end must be a non-negative integer")

    if end <= start:
        raise SerializationError("end must be greater than start")

    logger.info(f"Slicing JSON array at '{array_path}' [{start}:{end}]")

    # Navigate to array
    path_segments = _parse_json_path(array_path) if array_path else []
    nav_result = _navigate_json_path(data, path_segments)

    if "error" in nav_result:
        raise SerializationError(f"Path error: {nav_result['error']}")

    array = nav_result["value"]

    if not isinstance(array, list):
        raise SerializationError(
            f"Path '{array_path}' leads to {type(array).__name__}, not array"
        )

    # Slice array
    result_slice = array[start:end]

    # Convert to list of dicts
    result: list[dict] = []
    for item in result_slice:
        if isinstance(item, dict):
            result.append(item)
        else:
            result.append({"value": item})

    logger.info(f"JSON array sliced: {len(result)} items")
    return result


@strands_tool
def get_json_structure(data: dict, max_depth: int) -> dict[str, str]:
    """Get JSON structure/schema without values.

    This function provides a token-efficient way to understand JSON
    structure by returning type information instead of actual data.

    Args:
        data: JSON data as dictionary
        max_depth: Maximum depth to traverse (prevents infinite recursion)

    Returns:
        Dictionary mapping paths to type information

    Raises:
        TypeError: If parameters are not the correct types

    Example:
        >>> data = {'name': 'Alice', 'age': 25, 'tags': ['a', 'b'], 'meta': {'key': 'val'}}
        >>> get_json_structure(data, 2)
        {
            'name': 'string',
            'age': 'integer',
            'tags': 'array[2]',
            'meta': 'object',
            'meta.key': 'string'
        }
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dict")

    if not isinstance(max_depth, int) or max_depth < 0:
        raise TypeError("max_depth must be a non-negative integer")

    logger.info(f"Getting JSON structure (max_depth={max_depth})")

    def get_type_name(value: Union[dict, list, str, int, float, bool, None]) -> str:
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            return f"array[{len(value)}]"
        elif isinstance(value, dict):
            return "object"
        else:  # value is None
            return "null"

    def traverse(
        obj: Union[dict, list, str, int, float, bool, None],
        path: str,
        depth: int,
        result: dict[str, str],
    ) -> None:
        if depth > max_depth:
            return

        if isinstance(obj, dict):
            if path:
                result[path] = "object"
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                result[new_path] = get_type_name(value)
                if isinstance(value, (dict, list)) and depth < max_depth:
                    traverse(value, new_path, depth + 1, result)
        elif isinstance(obj, list):
            if path:
                result[path] = f"array[{len(obj)}]"
            # Sample first item if exists
            if obj and depth < max_depth:
                traverse(obj[0], f"{path}.0", depth + 1, result)

    structure: dict[str, str] = {}
    traverse(data, "", 0, structure)

    logger.info(f"JSON structure retrieved: {len(structure)} paths")
    return structure


@strands_tool
def count_json_items(data: dict, path: str) -> int:
    """Count items in JSON array or object keys.

    This function efficiently counts items without loading data values,
    enabling agents to understand data size before processing.

    Args:
        data: JSON data as dictionary
        path: Dot-notation path to array/object (empty string for root)

    Returns:
        Number of items (array length or object key count)

    Raises:
        TypeError: If parameters are not the correct types
        SerializationError: If path doesn't lead to array/object

    Example:
        >>> data = {'users': [1, 2, 3], 'config': {'a': 1, 'b': 2}}
        >>> count_json_items(data, "users")
        3
        >>> count_json_items(data, "config")
        2
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dict")

    if not isinstance(path, str):
        raise TypeError("path must be a string")

    logger.info(f"Counting JSON items at path: '{path}'")

    if not path:
        # Root level
        count = len(data)
        logger.info(f"JSON item count: {count}")
        return count

    # Navigate to path
    path_segments = _parse_json_path(path)
    nav_result = _navigate_json_path(data, path_segments)

    if "error" in nav_result:
        raise SerializationError(f"Path error: {nav_result['error']}")

    value = nav_result["value"]

    if isinstance(value, (dict, list)):
        count = len(value)
        logger.info(f"JSON item count: {count}")
        return count
    else:
        raise SerializationError(
            f"Path '{path}' leads to {type(value).__name__}, not array/object"
        )


@strands_tool
def search_json_keys(data: dict, key_pattern: str) -> list[str]:
    """Find all paths containing keys matching pattern.

    This function helps discover JSON structure by searching for
    keys that match a pattern (case-insensitive substring match).

    Args:
        data: JSON data as dictionary
        key_pattern: Pattern to search for in keys (case-insensitive)

    Returns:
        List of paths where matching keys were found

    Raises:
        TypeError: If parameters are not the correct types

    Example:
        >>> data = {'user_name': 'Alice', 'user_age': 25, 'config': {'user_id': 1}}
        >>> search_json_keys(data, "user")
        ['user_name', 'user_age', 'config.user_id']
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dict")

    if not isinstance(key_pattern, str):
        raise TypeError("key_pattern must be a string")

    logger.info(f"Searching JSON keys for pattern: '{key_pattern}'")

    pattern_lower = key_pattern.lower()
    matching_paths: list[str] = []

    def search(obj: Union[dict, list, str, int, float, bool, None], path: str) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                if pattern_lower in key.lower():
                    matching_paths.append(new_path)
                # Recurse into nested structures
                if isinstance(value, (dict, list)):
                    search(value, new_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, (dict, list)):
                    search(item, f"{path}.{i}")

    search(data, "")

    logger.info(f"JSON key search complete: {len(matching_paths)} matches")
    return matching_paths
