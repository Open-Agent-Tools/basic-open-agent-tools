"""Object serialization tools for AI agents.

This module provides functions for serializing and deserializing Python objects,
with a focus on safety and compatibility.
"""

import json
import pickle
from typing import Any

from ..exceptions import DataError


def serialize_object(obj: Any, method: str) -> bytes:
    """Serialize a Python object to bytes using the specified method.

    Args:
        obj: The Python object to serialize
        method: Serialization method, either "pickle" or "json"

    Returns:
        Serialized object as bytes

    Raises:
        DataError: If the serialization method is not supported or serialization fails
        TypeError: If the object is not serializable with the chosen method

    Example:
        >>> data = {"name": "test", "values": [1, 2, 3]}
        >>> serialized = serialize_object(data, method="json")
        >>> isinstance(serialized, bytes)
        True
    """
    if method not in ("pickle", "json"):
        raise DataError(f"Unsupported serialization method: {method}")

    try:
        if method == "pickle":
            return pickle.dumps(obj)
        else:  # json
            json_str = json.dumps(obj)
            return json_str.encode("utf-8")
    except (TypeError, ValueError) as e:
        if method == "json":
            raise TypeError(f"Object is not JSON serializable: {str(e)}")
        else:
            raise TypeError(f"Object is not pickle serializable: {str(e)}")


def deserialize_object(data: bytes, method: str) -> Any:
    """Safely deserialize bytes back into a Python object.

    Args:
        data: The serialized data as bytes
        method: Deserialization method, either "pickle" or "json"

    Returns:
        Deserialized Python object

    Raises:
        DataError: If the deserialization method is not supported or deserialization fails
        ValueError: If the input data is not valid for the chosen method

    Example:
        >>> data = {"name": "test", "values": [1, 2, 3]}
        >>> serialized = serialize_object(data, method="json")
        >>> deserialized = deserialize_object(serialized, method="json")
        >>> deserialized == data
        True
    """
    if method not in ("pickle", "json"):
        raise DataError(f"Unsupported deserialization method: {method}")

    if not isinstance(data, bytes):
        raise TypeError("Input data must be bytes")

    try:
        if method == "pickle":
            # For pickle, we validate safety before deserializing
            if not validate_pickle_safety(data):
                raise DataError("Potentially unsafe pickle data detected")
            return pickle.loads(data)
        else:  # json
            json_str = data.decode("utf-8")
            return json.loads(json_str)
    except (pickle.UnpicklingError, json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ValueError(f"Failed to deserialize data using {method}: {str(e)}")


def sanitize_for_serialization(data: Any) -> Any:
    """Remove or replace non-serializable objects from a data structure.

    This function recursively processes dictionaries, lists, and tuples to ensure
    all contained objects are JSON-serializable. Non-serializable objects are
    converted to strings.

    Args:
        data: The data structure to sanitize

    Returns:
        A new data structure with all non-serializable objects converted to strings

    Example:
        >>> from datetime import datetime
        >>> data = {"date": datetime(2023, 1, 1), "values": [1, 2, 3]}
        >>> sanitized = sanitize_for_serialization(data)
        >>> json.dumps(sanitized)  # This will not raise an error
        '{"date": "datetime.datetime(2023, 1, 1, 0, 0)", "values": [1, 2, 3]}'
    """
    # Handle basic JSON-serializable types
    if data is None or isinstance(data, (bool, int, float, str)):
        return data

    # Handle dictionaries
    if isinstance(data, dict):
        return {
            sanitize_for_serialization(k): sanitize_for_serialization(v)
            for k, v in data.items()
        }

    # Handle lists and tuples
    if isinstance(data, (list, tuple)):
        return [sanitize_for_serialization(item) for item in data]

    # Handle sets by converting to list
    if isinstance(data, set):
        return [sanitize_for_serialization(item) for item in data]

    # For any other type, convert to string representation
    return str(data)


def validate_pickle_safety(data: Any) -> bool:
    """Check if pickle data is potentially safe to deserialize.

    This function performs basic safety checks on pickle data to reduce the risk
    of executing malicious code during unpickling. It's not a complete security
    solution but provides a basic level of protection.

    Args:
        data: The pickle data to validate

    Returns:
        True if the data passes basic safety checks, False otherwise

    Example:
        >>> safe_data = pickle.dumps({"name": "test"})
        >>> validate_pickle_safety(safe_data)
        True
        >>> validate_pickle_safety("not bytes")
        False
    """
    # Check that input is bytes
    if not isinstance(data, bytes):
        return False

    # Check for common dangerous patterns in the pickle data
    # This is a basic check and not comprehensive
    dangerous_patterns = [
        b"os",  # os module
        b"subprocess",  # subprocess module
        b"system",  # system calls
        b"eval",  # eval function
        b"exec",  # exec function
        b"__reduce__",  # reduce method often used in exploits
        b"__globals__",  # access to globals
        b"__builtins__",  # access to builtins
    ]

    for pattern in dangerous_patterns:
        if pattern in data:
            return False

    # Check for excessive size (potential DoS)
    if len(data) > 10 * 1024 * 1024:  # 10MB limit
        return False

    return True
