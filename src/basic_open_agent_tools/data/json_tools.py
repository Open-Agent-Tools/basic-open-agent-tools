"""JSON processing utilities for AI agents."""

import json
from typing import Any, Callable

try:
    from strands import tool as strands_tool
except ImportError:
    # Create a no-op decorator if strands is not installed
    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]  # type: ignore
        return func


from ..exceptions import SerializationError


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
    print(f"[DATA] Serializing {data_type} to JSON (indent={indent})")

    if not isinstance(indent, int):
        raise TypeError("indent must be an integer")

    try:
        # Use None for compact format when indent is 0
        actual_indent = None if indent == 0 else indent
        result = json.dumps(data, indent=actual_indent, ensure_ascii=False)
        print(f"[DATA] JSON serialized: {len(result)} characters")
        return result
    except (TypeError, ValueError) as e:
        print(f"[DATA] JSON serialization error: {e}")
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
    print(f"[DATA] Deserializing JSON string ({len(json_str)} characters)")

    if not isinstance(json_str, str):
        raise TypeError("Input must be a string")

    try:
        result = json.loads(json_str)
        # Always return dict for agent compatibility
        if isinstance(result, dict):
            final_result = result
        else:
            # Wrap non-dict results in a dict for consistency
            final_result = {"result": result}

        print(f"[DATA] JSON deserialized: {type(final_result).__name__} with {len(final_result)} keys")
        return final_result
    except (json.JSONDecodeError, ValueError) as e:
        print(f"[DATA] JSON deserialization error: {e}")
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
    print(f"[DATA] Validating JSON string ({len(json_str)} characters)")

    if not isinstance(json_str, str):
        print("[DATA] JSON validation failed: not a string")
        return False  # type: ignore[unreachable]

    try:
        json.loads(json_str)
        print("[DATA] JSON validation: valid")
        return True
    except (json.JSONDecodeError, ValueError) as e:
        print(f"[DATA] JSON validation failed: {e}")
        return False
