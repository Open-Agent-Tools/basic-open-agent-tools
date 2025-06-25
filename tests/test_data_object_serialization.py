"""Tests for object serialization functions."""

import pickle
from datetime import datetime
from typing import Any, Dict

import pytest

from basic_open_agent_tools.data.object_serialization import (
    deserialize_object,
    sanitize_for_serialization,
    serialize_object,
    validate_pickle_safety,
)
from basic_open_agent_tools.exceptions import DataError


class TestSerializeObject:
    """Tests for serialize_object function."""

    def test_serialize_object_pickle(self):
        """Test serializing an object using pickle."""
        data = {"name": "test", "values": [1, 2, 3]}
        serialized = serialize_object(data, method="pickle")

        assert isinstance(serialized, bytes)
        # Verify we can deserialize it with pickle directly
        assert pickle.loads(serialized) == data

    def test_serialize_object_json(self):
        """Test serializing an object using JSON."""
        data = {"name": "test", "values": [1, 2, 3]}
        serialized = serialize_object(data, method="json")

        assert isinstance(serialized, bytes)
        # Verify it's valid JSON
        assert serialized.decode("utf-8")[0] == "{"

    def test_serialize_object_invalid_method(self):
        """Test serializing with an invalid method."""
        data = {"name": "test"}

        with pytest.raises(DataError):
            serialize_object(data, method="invalid")

    def test_serialize_object_not_serializable(self):
        """Test serializing an object that's not serializable."""
        # Create a circular reference that can't be serialized with JSON
        data: Dict[str, Any] = {"name": "test"}
        data["self"] = data

        with pytest.raises(TypeError):
            serialize_object(data, method="json")


class TestDeserializeObject:
    """Tests for deserialize_object function."""

    def test_deserialize_object_pickle(self):
        """Test deserializing an object using pickle."""
        original = {"name": "test", "values": [1, 2, 3]}
        serialized = serialize_object(original, method="pickle")

        deserialized = deserialize_object(serialized, method="pickle")
        assert deserialized == original

    def test_deserialize_object_json(self):
        """Test deserializing an object using JSON."""
        original = {"name": "test", "values": [1, 2, 3]}
        serialized = serialize_object(original, method="json")

        deserialized = deserialize_object(serialized, method="json")
        assert deserialized == original

    def test_deserialize_object_invalid_method(self):
        """Test deserializing with an invalid method."""
        data = b'{"name": "test"}'

        with pytest.raises(DataError):
            deserialize_object(data, method="invalid")

    def test_deserialize_object_invalid_data(self):
        """Test deserializing invalid data."""
        # Invalid JSON
        with pytest.raises(ValueError):
            deserialize_object(b'{"name": test}', method="json")

        # Invalid pickle
        with pytest.raises(ValueError):
            deserialize_object(b"not pickle data", method="pickle")

    def test_deserialize_object_not_bytes(self):
        """Test deserializing with non-bytes input."""
        with pytest.raises(TypeError):
            deserialize_object("not bytes", method="json")

    def test_deserialize_object_unsafe_pickle(self):
        """Test deserializing unsafe pickle data."""
        # Create pickle data with a dangerous pattern
        unsafe_data = pickle.dumps({"os": "command"})

        with pytest.raises(DataError):
            deserialize_object(unsafe_data, method="pickle")


class TestSanitizeForSerialization:
    """Tests for sanitize_for_serialization function."""

    def test_sanitize_basic_types(self):
        """Test sanitizing basic types."""
        assert sanitize_for_serialization(None) is None
        assert sanitize_for_serialization(True) is True
        assert sanitize_for_serialization(42) == 42
        assert sanitize_for_serialization(3.14) == 3.14
        assert sanitize_for_serialization("test") == "test"

    def test_sanitize_dict(self):
        """Test sanitizing a dictionary."""
        data = {"name": "test", "value": 42}
        assert sanitize_for_serialization(data) == data

    def test_sanitize_list(self):
        """Test sanitizing a list."""
        data = [1, 2, 3, "test"]
        assert sanitize_for_serialization(data) == data

    def test_sanitize_tuple(self):
        """Test sanitizing a tuple."""
        data = (1, 2, 3)
        assert sanitize_for_serialization(data) == [1, 2, 3]

    def test_sanitize_set(self):
        """Test sanitizing a set."""
        data = {1, 2, 3}
        assert set(sanitize_for_serialization(data)) == {1, 2, 3}

    def test_sanitize_nested_structure(self):
        """Test sanitizing a nested structure."""
        data = {
            "name": "test",
            "values": [1, 2, 3],
            "metadata": {"created": datetime(2023, 1, 1), "tags": {"tag1", "tag2"}},
        }

        sanitized = sanitize_for_serialization(data)

        # Check structure is preserved
        assert isinstance(sanitized, dict)
        assert isinstance(sanitized["values"], list)
        assert isinstance(sanitized["metadata"], dict)

        # Check non-serializable objects are converted to strings
        assert isinstance(sanitized["metadata"]["created"], str)
        # Check that it's a date string in the format YYYY-MM-DD
        assert "2023-01-01" in sanitized["metadata"]["created"]

        # Check sets are converted to lists
        assert isinstance(sanitized["metadata"]["tags"], list)
        assert set(sanitized["metadata"]["tags"]) == {"tag1", "tag2"}


class TestValidatePickleSafety:
    """Tests for validate_pickle_safety function."""

    def test_validate_safe_pickle(self):
        """Test validating safe pickle data."""
        safe_data = pickle.dumps({"name": "test", "values": [1, 2, 3]})
        assert validate_pickle_safety(safe_data) is True

    def test_validate_unsafe_pickle_os(self):
        """Test validating pickle data with os module reference."""
        unsafe_data = pickle.dumps({"module": "os", "command": "ls"})
        assert validate_pickle_safety(unsafe_data) is False

    def test_validate_unsafe_pickle_subprocess(self):
        """Test validating pickle data with subprocess reference."""
        unsafe_data = pickle.dumps({"module": "subprocess", "command": "ls"})
        assert validate_pickle_safety(unsafe_data) is False

    def test_validate_unsafe_pickle_eval(self):
        """Test validating pickle data with eval reference."""
        unsafe_data = pickle.dumps({"function": "eval", "code": "print('test')"})
        assert validate_pickle_safety(unsafe_data) is False

    def test_validate_not_bytes(self):
        """Test validating non-bytes input."""
        assert validate_pickle_safety("not bytes") is False

    def test_validate_large_pickle(self):
        """Test validating excessively large pickle data."""
        # Create a large list that exceeds the size limit when pickled
        large_data = pickle.dumps([0] * (11 * 1024 * 1024))  # Should exceed 10MB limit
        assert validate_pickle_safety(large_data) is False
