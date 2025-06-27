"""JSON processing utilities for AI agents."""

import json

from ..exceptions import SerializationError


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
    if not isinstance(indent, int):
        raise TypeError("indent must be an integer")

    try:
        # Use None for compact format when indent is 0
        actual_indent = None if indent == 0 else indent
        return json.dumps(data, indent=actual_indent, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        raise SerializationError(f"Failed to serialize data to JSON: {e}")


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

    try:
        result = json.loads(json_str)
        # Always return dict for agent compatibility
        if isinstance(result, dict):
            return result
        else:
            # Wrap non-dict results in a dict for consistency
            return {"result": result}
    except (json.JSONDecodeError, ValueError) as e:
        raise SerializationError(f"Failed to deserialize JSON string: {e}")


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
        return False  # type: ignore[unreachable]

    try:
        json.loads(json_str)
        return True
    except (json.JSONDecodeError, ValueError):
        return False
