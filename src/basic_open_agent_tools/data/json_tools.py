"""JSON processing utilities for AI agents."""

import json

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
