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


@strands_tool
def update_json_value_at_path(
    file_path: str, json_path: str, new_value: str, skip_confirm: bool
) -> str:
    """Update single value at JSON path without loading entire structure.

    This function efficiently updates a specific value in a JSON file
    without requiring the entire structure to be loaded into context.

    Args:
        file_path: Path to JSON file
        json_path: Dot-notation path (e.g., "users.0.name")
        new_value: New value as string (will be parsed as JSON)
        skip_confirm: If False, requests confirmation for file modification

    Returns:
        Success message describing the update

    Raises:
        FileNotFoundError: If file does not exist
        SerializationError: If file contains invalid JSON or new_value is invalid JSON
        TypeError: If parameters are wrong type
        ValueError: If path not found

    Example:
        >>> result = update_json_value_at_path("/data/config.json", "timeout", "60", True)
        >>> result
        'Updated value at path "timeout" in /data/config.json'
    """
    from ..confirmation import check_user_confirmation

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(json_path, str):
        raise TypeError("json_path must be a string")

    if not isinstance(new_value, str):
        raise TypeError("new_value must be a string")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    # Read existing JSON
    data = read_json_file(file_path)

    # Parse new value as JSON
    try:
        parsed_value = json.loads(new_value)
    except json.JSONDecodeError as e:
        raise SerializationError(f"Invalid JSON in new_value: {e}")

    # Navigate to the path and update
    path_segments = _parse_json_path(json_path)
    if not path_segments:
        raise ValueError("json_path cannot be empty")

    # Navigate to parent
    current: Any = data
    for segment in path_segments[:-1]:
        if isinstance(current, dict):
            if segment not in current:
                raise ValueError(f"Path not found at segment: {segment}")
            current = current[segment]
        elif isinstance(current, list):
            try:
                index = int(segment)
                if index < 0 or index >= len(current):
                    raise ValueError(f"Index {index} out of range")
                current = current[index]
            except ValueError:
                raise ValueError(f"Invalid array index: {segment}")
        else:
            raise ValueError(f"Cannot navigate into {type(current).__name__}")

    # Update the final key/index
    final_segment = path_segments[-1]
    if isinstance(current, dict):
        if final_segment not in current:
            raise ValueError(f"Key '{final_segment}' not found")
        current[final_segment] = parsed_value
    elif isinstance(current, list):
        try:
            index = int(final_segment)
            if index < 0 or index >= len(current):
                raise ValueError(f"Index {index} out of range")
            current[index] = parsed_value
        except ValueError:
            raise ValueError(f"Invalid array index: {final_segment}")
    else:
        raise ValueError(f"Cannot update value in {type(current).__name__}")

    # Check confirmation
    check_user_confirmation(
        operation="update value in JSON file",
        target=file_path,
        skip_confirm=skip_confirm,
    )

    # Write back to file
    write_json_file(data, file_path, 2, True)

    logger.info(f"Updated value at path '{json_path}' in {file_path}")
    return f'Updated value at path "{json_path}" in {file_path}'


@strands_tool
def delete_json_key_at_path(file_path: str, json_path: str, skip_confirm: bool) -> str:
    """Remove specific key at JSON path without loading entire structure.

    This function efficiently deletes a key/index from a JSON file
    without requiring the entire structure to be loaded into context.

    Args:
        file_path: Path to JSON file
        json_path: Dot-notation path to key/index to delete (e.g., "users.0")
        skip_confirm: If False, requests confirmation for file modification

    Returns:
        Success message describing the deletion

    Raises:
        FileNotFoundError: If file does not exist
        SerializationError: If file contains invalid JSON
        TypeError: If parameters are wrong type
        ValueError: If path not found

    Example:
        >>> result = delete_json_key_at_path("/data/config.json", "deprecated_setting", True)
        >>> result
        'Deleted key at path "deprecated_setting" from /data/config.json'
    """
    from ..confirmation import check_user_confirmation

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(json_path, str):
        raise TypeError("json_path must be a string")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    # Read existing JSON
    data = read_json_file(file_path)

    # Navigate to the path and delete
    path_segments = _parse_json_path(json_path)
    if not path_segments:
        raise ValueError("json_path cannot be empty")

    # Navigate to parent
    current: Any = data
    for segment in path_segments[:-1]:
        if isinstance(current, dict):
            if segment not in current:
                raise ValueError(f"Path not found at segment: {segment}")
            current = current[segment]
        elif isinstance(current, list):
            try:
                index = int(segment)
                if index < 0 or index >= len(current):
                    raise ValueError(f"Index {index} out of range")
                current = current[index]
            except ValueError:
                raise ValueError(f"Invalid array index: {segment}")
        else:
            raise ValueError(f"Cannot navigate into {type(current).__name__}")

    # Delete the final key/index
    final_segment = path_segments[-1]
    if isinstance(current, dict):
        if final_segment not in current:
            raise ValueError(f"Key '{final_segment}' not found")
        del current[final_segment]
    elif isinstance(current, list):
        try:
            index = int(final_segment)
            if index < 0 or index >= len(current):
                raise ValueError(f"Index {index} out of range")
            del current[index]
        except ValueError:
            raise ValueError(f"Invalid array index: {final_segment}")
    else:
        raise ValueError(f"Cannot delete from {type(current).__name__}")

    # Check confirmation
    check_user_confirmation(
        operation="delete key from JSON file",
        target=file_path,
        skip_confirm=skip_confirm,
    )

    # Write back to file
    write_json_file(data, file_path, 2, True)

    logger.info(f"Deleted key at path '{json_path}' from {file_path}")
    return f'Deleted key at path "{json_path}" from {file_path}'


@strands_tool
def append_to_json_array(
    file_path: str, array_path: str, item: str, skip_confirm: bool
) -> str:
    """Add item to JSON array at path without loading entire structure.

    This function efficiently appends an item to an array in a JSON file
    without requiring the entire structure to be loaded into context.

    Args:
        file_path: Path to JSON file
        array_path: Dot-notation path to array (e.g., "users")
        item: Item to append as JSON string
        skip_confirm: If False, requests confirmation for file modification

    Returns:
        Success message describing the append operation

    Raises:
        FileNotFoundError: If file does not exist
        SerializationError: If file contains invalid JSON or item is invalid JSON
        TypeError: If parameters are wrong type
        ValueError: If path not found or target is not an array

    Example:
        >>> result = append_to_json_array("/data/users.json", "users", '{"name": "Alice"}', True)
        >>> result
        'Appended item to array at path "users" in /data/users.json'
    """
    from ..confirmation import check_user_confirmation

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(array_path, str):
        raise TypeError("array_path must be a string")

    if not isinstance(item, str):
        raise TypeError("item must be a string")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    # Read existing JSON
    data = read_json_file(file_path)

    # Parse item as JSON
    try:
        parsed_item = json.loads(item)
    except json.JSONDecodeError as e:
        raise SerializationError(f"Invalid JSON in item: {e}")

    # Navigate to the array
    if not array_path:
        # Root is the array
        if not isinstance(data, list):
            raise ValueError("Root element is not an array")
        data.append(parsed_item)
    else:
        path_segments = _parse_json_path(array_path)
        current: Any = data

        for segment in path_segments:
            if isinstance(current, dict):
                if segment not in current:
                    raise ValueError(f"Path not found at segment: {segment}")
                current = current[segment]
            elif isinstance(current, list):
                try:
                    index = int(segment)
                    if index < 0 or index >= len(current):
                        raise ValueError(f"Index {index} out of range")
                    current = current[index]
                except ValueError:
                    raise ValueError(f"Invalid array index: {segment}")
            else:
                raise ValueError(f"Cannot navigate into {type(current).__name__}")

        # Verify it's an array and append
        if not isinstance(current, list):
            raise ValueError(f"Target at path '{array_path}' is not an array")

        current.append(parsed_item)

    # Check confirmation
    check_user_confirmation(
        operation="append item to JSON array",
        target=file_path,
        skip_confirm=skip_confirm,
    )

    # Write back to file
    write_json_file(data, file_path, 2, True)

    logger.info(f"Appended item to array at path '{array_path}' in {file_path}")
    return f'Appended item to array at path "{array_path}" in {file_path}'


@strands_tool
def merge_json_objects(
    file_path: str, source_path: str, target_path: str, skip_confirm: bool
) -> str:
    """Deep merge two JSON objects without loading entire structure.

    This function efficiently merges two JSON objects in a file,
    with the source object's values taking precedence. Nested objects
    are merged recursively.

    Args:
        file_path: Path to JSON file
        source_path: Dot-notation path to source object
        target_path: Dot-notation path to target object (will receive merge)
        skip_confirm: If False, requests confirmation for file modification

    Returns:
        Success message describing the merge operation

    Raises:
        FileNotFoundError: If file does not exist
        SerializationError: If file contains invalid JSON
        TypeError: If parameters are wrong type or objects are not dicts
        ValueError: If paths not found

    Example:
        >>> result = merge_json_objects("/data/config.json", "defaults", "settings", True)
        >>> result
        'Merged object from "defaults" into "settings" in /data/config.json'
    """
    from ..confirmation import check_user_confirmation

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(source_path, str):
        raise TypeError("source_path must be a string")

    if not isinstance(target_path, str):
        raise TypeError("target_path must be a string")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    # Read existing JSON
    data = read_json_file(file_path)

    # Helper function for deep merge
    def deep_merge(source: dict[str, Any], target: dict[str, Any]) -> None:
        """Deep merge source into target."""
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                deep_merge(value, target[key])
            else:
                target[key] = value

    # Navigate to source object
    if not source_path:
        source_obj = data
    else:
        source_segments = _parse_json_path(source_path)
        current: Any = data
        for segment in source_segments:
            if isinstance(current, dict):
                if segment not in current:
                    raise ValueError(f"Source path not found at segment: {segment}")
                current = current[segment]
            elif isinstance(current, list):
                try:
                    index = int(segment)
                    if index < 0 or index >= len(current):
                        raise ValueError(f"Source index {index} out of range")
                    current = current[index]
                except ValueError:
                    raise ValueError(f"Invalid source array index: {segment}")
            else:
                raise ValueError(
                    f"Cannot navigate source into {type(current).__name__}"
                )
        source_obj = current

    # Navigate to target object
    if not target_path:
        target_obj = data
    else:
        target_segments = _parse_json_path(target_path)
        current = data
        for segment in target_segments:
            if isinstance(current, dict):
                if segment not in current:
                    raise ValueError(f"Target path not found at segment: {segment}")
                current = current[segment]
            elif isinstance(current, list):
                try:
                    index = int(segment)
                    if index < 0 or index >= len(current):
                        raise ValueError(f"Target index {index} out of range")
                    current = current[index]
                except ValueError:
                    raise ValueError(f"Invalid target array index: {segment}")
            else:
                raise ValueError(
                    f"Cannot navigate target into {type(current).__name__}"
                )
        target_obj = current

    # Verify both are dicts
    if not isinstance(source_obj, dict):
        raise TypeError(f"Source at '{source_path}' is not an object")

    if not isinstance(target_obj, dict):
        raise TypeError(f"Target at '{target_path}' is not an object")

    # Perform deep merge
    deep_merge(source_obj, target_obj)

    # Check confirmation
    check_user_confirmation(
        operation="merge JSON objects",
        target=file_path,
        skip_confirm=skip_confirm,
    )

    # Write back to file
    write_json_file(data, file_path, 2, True)

    logger.info(
        f"Merged object from '{source_path}' into '{target_path}' in {file_path}"
    )
    return f'Merged object from "{source_path}" into "{target_path}" in {file_path}'


@strands_tool
def sort_json_array(
    file_path: str, array_path: str, sort_key: str, reverse: bool, skip_confirm: bool
) -> str:
    """Sort JSON array by key without loading entire structure.

    This function efficiently sorts an array of objects in a JSON file
    by a specific key, without requiring the entire structure to be loaded.

    Args:
        file_path: Path to JSON file
        array_path: Dot-notation path to array to sort
        sort_key: Key to sort by (for arrays of objects) or empty for primitive arrays
        reverse: If True, sort in descending order
        skip_confirm: If False, requests confirmation for file modification

    Returns:
        Success message describing the sort operation

    Raises:
        FileNotFoundError: If file does not exist
        SerializationError: If file contains invalid JSON
        TypeError: If parameters are wrong type or target is not an array
        ValueError: If path not found or sort_key missing in objects

    Example:
        >>> result = sort_json_array("/data/users.json", "users", "age", False, True)
        >>> result
        'Sorted array at path "users" by key "age" in /data/users.json'
    """
    from ..confirmation import check_user_confirmation

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(array_path, str):
        raise TypeError("array_path must be a string")

    if not isinstance(sort_key, str):
        raise TypeError("sort_key must be a string")

    if not isinstance(reverse, bool):
        raise TypeError("reverse must be a boolean")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    # Read existing JSON
    data = read_json_file(file_path)

    # Navigate to the array
    if not array_path:
        target_array = data
    else:
        path_segments = _parse_json_path(array_path)
        current: Any = data
        for segment in path_segments:
            if isinstance(current, dict):
                if segment not in current:
                    raise ValueError(f"Path not found at segment: {segment}")
                current = current[segment]
            elif isinstance(current, list):
                try:
                    index = int(segment)
                    if index < 0 or index >= len(current):
                        raise ValueError(f"Index {index} out of range")
                    current = current[index]
                except ValueError:
                    raise ValueError(f"Invalid array index: {segment}")
            else:
                raise ValueError(f"Cannot navigate into {type(current).__name__}")
        target_array = current

    # Verify it's an array
    if not isinstance(target_array, list):
        raise TypeError(f"Target at path '{array_path}' is not an array")

    # Sort the array
    if sort_key:
        # Sort array of objects by key
        def get_sort_value(item: Any) -> Any:
            if not isinstance(item, dict):
                raise ValueError(
                    f"Cannot sort by key '{sort_key}' - array contains non-objects"
                )
            if sort_key not in item:
                raise ValueError(f"Sort key '{sort_key}' not found in array object")
            return item[sort_key]

        target_array.sort(key=get_sort_value, reverse=reverse)
    else:
        # Sort array of primitives
        target_array.sort(reverse=reverse)

    # Check confirmation
    check_user_confirmation(
        operation="sort JSON array",
        target=file_path,
        skip_confirm=skip_confirm,
    )

    # Write back to file
    write_json_file(data, file_path, 2, True)

    if sort_key:
        logger.info(
            f"Sorted array at path '{array_path}' by key '{sort_key}' in {file_path}"
        )
        return f'Sorted array at path "{array_path}" by key "{sort_key}" in {file_path}'
    else:
        logger.info(f"Sorted array at path '{array_path}' in {file_path}")
        return f'Sorted array at path "{array_path}" in {file_path}'


@strands_tool
def flatten_json_object(file_path: str, object_path: str) -> dict[str, str]:
    """Flatten nested JSON object to dot-notation keys without loading entire structure.

    This function efficiently flattens a nested JSON object into a flat
    dictionary with dot-notation keys, without requiring the entire structure
    to be loaded into context.

    Args:
        file_path: Path to JSON file
        object_path: Dot-notation path to object to flatten (empty for root)

    Returns:
        Flattened object as dict with dot-notation keys

    Raises:
        FileNotFoundError: If file does not exist
        SerializationError: If file contains invalid JSON
        TypeError: If parameters are wrong type or target is not an object
        ValueError: If path not found

    Example:
        >>> result = flatten_json_object("/data/config.json", "settings")
        >>> result
        {'database.host': 'localhost', 'database.port': '5432'}
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(object_path, str):
        raise TypeError("object_path must be a string")

    # Read existing JSON
    data = read_json_file(file_path)

    # Navigate to the object
    if not object_path:
        target_obj = data
    else:
        path_segments = _parse_json_path(object_path)
        current: Any = data
        for segment in path_segments:
            if isinstance(current, dict):
                if segment not in current:
                    raise ValueError(f"Path not found at segment: {segment}")
                current = current[segment]
            elif isinstance(current, list):
                try:
                    index = int(segment)
                    if index < 0 or index >= len(current):
                        raise ValueError(f"Index {index} out of range")
                    current = current[index]
                except ValueError:
                    raise ValueError(f"Invalid array index: {segment}")
            else:
                raise ValueError(f"Cannot navigate into {type(current).__name__}")
        target_obj = current

    # Verify it's an object
    if not isinstance(target_obj, dict):
        raise TypeError(f"Target at path '{object_path}' is not an object")

    # Flatten the object
    def flatten(obj: dict[str, Any], prefix: str = "") -> dict[str, str]:
        """Recursively flatten nested dict."""
        result: dict[str, str] = {}
        for key, value in obj.items():
            new_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                result.update(flatten(value, new_key))
            elif isinstance(value, list):
                # Convert arrays to indexed keys
                for i, item in enumerate(value):
                    indexed_key = f"{new_key}.{i}"
                    if isinstance(item, dict):
                        result.update(flatten(item, indexed_key))
                    else:
                        result[indexed_key] = (
                            json.dumps(item) if not isinstance(item, str) else item
                        )
            else:
                result[new_key] = (
                    json.dumps(value) if not isinstance(value, str) else value
                )
        return result

    flattened = flatten(target_obj)

    logger.info(f"Flattened object at path '{object_path}' from {file_path}")
    return flattened


@strands_tool
def unflatten_json_object(
    flattened_data: str, file_path: str, skip_confirm: bool
) -> str:
    """Unflatten dot-notation keys to nested JSON object and write to file.

    This function efficiently converts a flattened dictionary with dot-notation
    keys back into a nested JSON structure and writes it to a file.

    Args:
        flattened_data: JSON string of flattened object with dot-notation keys
        file_path: Path to write the unflattened JSON file
        skip_confirm: If False, requests confirmation for file modification

    Returns:
        Success message describing the unflatten operation

    Raises:
        SerializationError: If flattened_data is invalid JSON
        TypeError: If parameters are wrong type or flattened_data is not an object
        ValueError: If dot-notation keys are invalid

    Example:
        >>> result = unflatten_json_object('{"db.host": "localhost", "db.port": "5432"}', "/data/config.json", True)
        >>> result
        'Unflattened object written to /data/config.json'
    """
    from ..confirmation import check_user_confirmation

    if not isinstance(flattened_data, str):
        raise TypeError("flattened_data must be a string")

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    # Parse flattened data
    try:
        flattened = json.loads(flattened_data)
    except json.JSONDecodeError as e:
        raise SerializationError(f"Invalid JSON in flattened_data: {e}")

    if not isinstance(flattened, dict):
        raise TypeError("flattened_data must be a JSON object")

    # Unflatten the object
    result: dict[str, Any] = {}
    for key, value in flattened.items():
        parts = key.split(".")
        current: Any = result

        # Navigate/create nested structure
        for i, part in enumerate(parts[:-1]):
            # Check if next part is numeric (array index)
            next_part = parts[i + 1]
            is_array = next_part.isdigit()

            if part not in current:
                current[part] = [] if is_array else {}
            elif is_array and not isinstance(current[part], list):
                raise ValueError(f"Conflicting types at key '{part}': expected array")
            elif not is_array and not isinstance(current[part], dict):
                raise ValueError(f"Conflicting types at key '{part}': expected object")

            current = current[part]

        # Set the final value
        final_key = parts[-1]
        if final_key.isdigit():
            # Array index
            index = int(final_key)
            if not isinstance(current, list):
                raise ValueError(f"Expected array but got {type(current).__name__}")
            # Extend array if necessary
            while len(current) <= index:
                current.append(None)
            # Try to parse value as JSON
            try:
                current[index] = json.loads(value) if isinstance(value, str) else value
            except json.JSONDecodeError:
                current[index] = value
        else:
            # Object key
            if not isinstance(current, dict):
                raise ValueError(f"Expected object but got {type(current).__name__}")
            # Try to parse value as JSON
            try:
                current[final_key] = (
                    json.loads(value) if isinstance(value, str) else value
                )
            except json.JSONDecodeError:
                current[final_key] = value

    # Check confirmation
    check_user_confirmation(
        operation="write unflattened JSON object",
        target=file_path,
        skip_confirm=skip_confirm,
    )

    # Write to file
    write_json_file(result, file_path, 2, True)

    logger.info(f"Unflattened object written to {file_path}")
    return f"Unflattened object written to {file_path}"


@strands_tool
def transform_json_values(
    file_path: str, path_filter: str, transform_type: str, skip_confirm: bool
) -> str:
    """Transform values in JSON structure without loading entire structure.

    This function efficiently applies transformations to values in a JSON file
    that match a specific path pattern.

    Args:
        file_path: Path to JSON file
        path_filter: Path pattern to match (supports wildcards: "*" for any key, "#" for array index)
        transform_type: Type of transformation ("uppercase", "lowercase", "trim", "string")
        skip_confirm: If False, requests confirmation for file modification

    Returns:
        Success message describing the transformation

    Raises:
        FileNotFoundError: If file does not exist
        SerializationError: If file contains invalid JSON
        TypeError: If parameters are wrong type
        ValueError: If transform_type is not supported

    Example:
        >>> result = transform_json_values("/data/users.json", "users.*.name", "uppercase", True)
        >>> result
        'Transformed 5 values matching "users.*.name" in /data/users.json'
    """
    from ..confirmation import check_user_confirmation

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(path_filter, str):
        raise TypeError("path_filter must be a string")

    if not isinstance(transform_type, str):
        raise TypeError("transform_type must be a string")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    valid_transforms = ["uppercase", "lowercase", "trim", "string"]
    if transform_type not in valid_transforms:
        raise ValueError(
            f"transform_type must be one of: {', '.join(valid_transforms)}"
        )

    # Read existing JSON
    data = read_json_file(file_path)

    transform_count = 0

    # Apply transformation recursively
    def apply_transform(obj: Any, current_path: str) -> None:
        nonlocal transform_count

        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{current_path}.{key}" if current_path else key
                if _path_matches_filter(new_path, path_filter):
                    # Transform this value
                    if transform_type == "uppercase" and isinstance(value, str):
                        obj[key] = value.upper()
                        transform_count += 1
                    elif transform_type == "lowercase" and isinstance(value, str):
                        obj[key] = value.lower()
                        transform_count += 1
                    elif transform_type == "trim" and isinstance(value, str):
                        obj[key] = value.strip()
                        transform_count += 1
                    elif transform_type == "string":
                        obj[key] = str(value)
                        transform_count += 1
                else:
                    # Recurse into nested structures
                    apply_transform(value, new_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{current_path}.{i}" if current_path else str(i)
                if _path_matches_filter(new_path, path_filter):
                    # Transform this value
                    if transform_type == "uppercase" and isinstance(item, str):
                        obj[i] = item.upper()
                        transform_count += 1
                    elif transform_type == "lowercase" and isinstance(item, str):
                        obj[i] = item.lower()
                        transform_count += 1
                    elif transform_type == "trim" and isinstance(item, str):
                        obj[i] = item.strip()
                        transform_count += 1
                    elif transform_type == "string":
                        obj[i] = str(item)
                        transform_count += 1
                else:
                    # Recurse into nested structures
                    apply_transform(item, new_path)

    def _path_matches_filter(path: str, filter_pattern: str) -> bool:
        """Check if path matches filter pattern with wildcards."""
        path_parts = path.split(".")
        filter_parts = filter_pattern.split(".")

        if len(path_parts) != len(filter_parts):
            return False

        for path_part, filter_part in zip(path_parts, filter_parts):
            if filter_part == "*":
                continue  # Wildcard matches any key
            elif filter_part == "#":
                if not path_part.isdigit():
                    return False  # # should match array indices
            elif path_part != filter_part:
                return False

        return True

    apply_transform(data, "")

    # Check confirmation
    check_user_confirmation(
        operation="transform JSON values",
        target=file_path,
        skip_confirm=skip_confirm,
    )

    # Write back to file
    write_json_file(data, file_path, 2, True)

    logger.info(
        f"Transformed {transform_count} values matching '{path_filter}' in {file_path}"
    )
    return (
        f'Transformed {transform_count} values matching "{path_filter}" in {file_path}'
    )


@strands_tool
def deduplicate_json_array(
    file_path: str, array_path: str, unique_key: str, skip_confirm: bool
) -> str:
    """Remove duplicate objects from JSON array without loading entire structure.

    This function efficiently removes duplicates from an array in a JSON file,
    preserving the first occurrence of each unique value.

    Args:
        file_path: Path to JSON file
        array_path: Dot-notation path to array to deduplicate
        unique_key: Key to use for uniqueness (empty for primitive arrays)
        skip_confirm: If False, requests confirmation for file modification

    Returns:
        Success message describing the deduplication

    Raises:
        FileNotFoundError: If file does not exist
        SerializationError: If file contains invalid JSON
        TypeError: If parameters are wrong type or target is not an array
        ValueError: If path not found or unique_key missing in objects

    Example:
        >>> result = deduplicate_json_array("/data/users.json", "users", "email", True)
        >>> result
        'Removed 3 duplicates from array at path "users" in /data/users.json'
    """
    from ..confirmation import check_user_confirmation

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(array_path, str):
        raise TypeError("array_path must be a string")

    if not isinstance(unique_key, str):
        raise TypeError("unique_key must be a string")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    # Read existing JSON
    data = read_json_file(file_path)

    # Navigate to the array
    if not array_path:
        target_array = data
    else:
        path_segments = _parse_json_path(array_path)
        current: Any = data
        for segment in path_segments:
            if isinstance(current, dict):
                if segment not in current:
                    raise ValueError(f"Path not found at segment: {segment}")
                current = current[segment]
            elif isinstance(current, list):
                try:
                    index = int(segment)
                    if index < 0 or index >= len(current):
                        raise ValueError(f"Index {index} out of range")
                    current = current[index]
                except ValueError:
                    raise ValueError(f"Invalid array index: {segment}")
            else:
                raise ValueError(f"Cannot navigate into {type(current).__name__}")
        target_array = current

    # Verify it's an array
    if not isinstance(target_array, list):
        raise TypeError(f"Target at path '{array_path}' is not an array")

    original_length = len(target_array)

    # Deduplicate the array
    if unique_key:
        # Deduplicate array of objects by key
        seen = set()
        deduped = []
        for item in target_array:
            if not isinstance(item, dict):
                raise ValueError(
                    f"Cannot deduplicate by key '{unique_key}' - array contains non-objects"
                )
            if unique_key not in item:
                raise ValueError(f"Unique key '{unique_key}' not found in array object")

            # Convert value to string for hashing
            value = json.dumps(item[unique_key], sort_keys=True)
            if value not in seen:
                seen.add(value)
                deduped.append(item)

        # Replace array contents
        target_array.clear()
        target_array.extend(deduped)
    else:
        # Deduplicate array of primitives
        seen = set()
        deduped = []
        for item in target_array:
            # Convert to string for hashing
            value = json.dumps(item, sort_keys=True)
            if value not in seen:
                seen.add(value)
                deduped.append(item)

        # Replace array contents
        target_array.clear()
        target_array.extend(deduped)

    removed_count = original_length - len(target_array)

    # Check confirmation
    check_user_confirmation(
        operation="deduplicate JSON array",
        target=file_path,
        skip_confirm=skip_confirm,
    )

    # Write back to file
    write_json_file(data, file_path, 2, True)

    logger.info(
        f"Removed {removed_count} duplicates from array at path '{array_path}' in {file_path}"
    )
    return f'Removed {removed_count} duplicates from array at path "{array_path}" in {file_path}'
