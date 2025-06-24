"""Tests for JSON processing tools."""

import pytest

from basic_open_agent_tools.data.json_tools import (
    compress_json_data,
    decompress_json_data,
    safe_json_deserialize,
    safe_json_serialize,
    validate_json_string,
)
from basic_open_agent_tools.exceptions import SerializationError


class TestSafeJsonSerialize:
    """Test safe_json_serialize function."""

    def test_serialize_dict(self):
        """Test serializing a dictionary."""
        data = {"name": "test", "value": 42}
        result = safe_json_serialize(data)
        assert result == '{"name": "test", "value": 42}'

    def test_serialize_list(self):
        """Test serializing a list."""
        data = [1, 2, 3]
        result = safe_json_serialize(data)
        assert result == "[1, 2, 3]"

    def test_serialize_with_indent(self):
        """Test serializing with indentation."""
        data = {"a": 1, "b": 2}
        result = safe_json_serialize(data, indent=2)
        expected = '{\n  "a": 1,\n  "b": 2\n}'
        assert result == expected

    def test_serialize_unicode(self):
        """Test serializing Unicode characters."""
        data = {"message": "Hello 世界"}
        result = safe_json_serialize(data)
        assert "世界" in result

    def test_serialize_none(self):
        """Test serializing None."""
        result = safe_json_serialize(None)
        assert result == "null"

    def test_serialize_invalid_indent_type(self):
        """Test with invalid indent type."""
        with pytest.raises(TypeError, match="indent must be an integer or None"):
            safe_json_serialize({"test": "data"}, indent="invalid")

    def test_serialize_non_serializable_object(self):
        """Test serializing non-serializable object."""

        class CustomClass:
            pass

        with pytest.raises(
            SerializationError, match="Failed to serialize data to JSON"
        ):
            safe_json_serialize({"obj": CustomClass()})


class TestSafeJsonDeserialize:
    """Test safe_json_deserialize function."""

    def test_deserialize_dict(self):
        """Test deserializing a dictionary."""
        json_str = '{"name": "test", "value": 42}'
        result = safe_json_deserialize(json_str)
        assert result == {"name": "test", "value": 42}

    def test_deserialize_list(self):
        """Test deserializing a list."""
        json_str = "[1, 2, 3]"
        result = safe_json_deserialize(json_str)
        assert result == [1, 2, 3]

    def test_deserialize_unicode(self):
        """Test deserializing Unicode characters."""
        json_str = '{"message": "Hello 世界"}'
        result = safe_json_deserialize(json_str)
        assert result == {"message": "Hello 世界"}

    def test_deserialize_null(self):
        """Test deserializing null."""
        result = safe_json_deserialize("null")
        assert result is None

    def test_deserialize_invalid_type(self):
        """Test with invalid input type."""
        with pytest.raises(TypeError, match="Input must be a string"):
            safe_json_deserialize({"invalid": "input"})

    def test_deserialize_invalid_json(self):
        """Test deserializing invalid JSON."""
        with pytest.raises(
            SerializationError, match="Failed to deserialize JSON string"
        ):
            safe_json_deserialize('{"invalid": }')

    def test_deserialize_empty_string(self):
        """Test deserializing empty string."""
        with pytest.raises(
            SerializationError, match="Failed to deserialize JSON string"
        ):
            safe_json_deserialize("")


class TestValidateJsonString:
    """Test validate_json_string function."""

    def test_validate_valid_json(self):
        """Test validating valid JSON."""
        assert validate_json_string('{"valid": true}') is True
        assert validate_json_string("[1, 2, 3]") is True
        assert validate_json_string('"string"') is True
        assert validate_json_string("null") is True

    def test_validate_invalid_json(self):
        """Test validating invalid JSON."""
        assert validate_json_string('{"invalid": }') is False
        assert validate_json_string("[1, 2,]") is False
        assert validate_json_string("undefined") is False
        assert validate_json_string("") is False

    def test_validate_non_string(self):
        """Test validating non-string input."""
        assert validate_json_string(None) is False
        assert validate_json_string(123) is False
        assert validate_json_string({"dict": "input"}) is False
        assert validate_json_string([1, 2, 3]) is False


class TestCompressJsonData:
    """Test compress_json_data function."""

    def test_compress_simple_data(self):
        """Test compressing simple data."""
        data = {"test": "data"}
        compressed = compress_json_data(data)
        assert isinstance(compressed, bytes)
        assert len(compressed) > 0

    def test_compress_large_data(self):
        """Test compressing larger data for better compression."""
        data = {"repeated": "data" * 100, "numbers": list(range(100))}
        compressed = compress_json_data(data)
        original_json = safe_json_serialize(data)

        # Compressed should be smaller than original for repetitive data
        assert len(compressed) < len(original_json.encode("utf-8"))

    def test_compress_unicode_data(self):
        """Test compressing Unicode data."""
        data = {"unicode": "Hello 世界", "emoji": "🚀"}
        compressed = compress_json_data(data)
        assert isinstance(compressed, bytes)

    def test_compress_non_serializable(self):
        """Test compressing non-serializable data."""

        class CustomClass:
            pass

        with pytest.raises(SerializationError, match="Failed to compress JSON data"):
            compress_json_data({"obj": CustomClass()})


class TestDecompressJsonData:
    """Test decompress_json_data function."""

    def test_decompress_simple_data(self):
        """Test decompressing simple data."""
        original = {"test": "data"}
        compressed = compress_json_data(original)
        decompressed = decompress_json_data(compressed)
        assert decompressed == original

    def test_decompress_complex_data(self):
        """Test decompressing complex data."""
        original = {
            "string": "Hello 世界",
            "number": 42,
            "list": [1, 2, 3],
            "nested": {"key": "value"},
            "null": None,
            "boolean": True,
        }
        compressed = compress_json_data(original)
        decompressed = decompress_json_data(compressed)
        assert decompressed == original

    def test_decompress_invalid_type(self):
        """Test decompressing invalid input type."""
        with pytest.raises(TypeError, match="Input must be bytes"):
            decompress_json_data("not bytes")

    def test_decompress_invalid_data(self):
        """Test decompressing invalid compressed data."""
        with pytest.raises(SerializationError, match="Failed to decompress JSON data"):
            decompress_json_data(b"invalid compressed data")

    def test_decompress_empty_bytes(self):
        """Test decompressing empty bytes."""
        with pytest.raises(SerializationError, match="Failed to decompress JSON data"):
            decompress_json_data(b"")


class TestRoundTripSerialization:
    """Test round-trip serialization scenarios."""

    def test_serialize_deserialize_roundtrip(self):
        """Test that serialize -> deserialize returns original data."""
        test_cases = [
            {"simple": "dict"},
            [1, 2, 3, "mixed", {"nested": "list"}],
            None,
            True,
            False,
            42,
            3.14,
            "string with unicode 世界",
            {"complex": {"nested": {"deeply": [1, 2, {"more": "nesting"}]}}},
        ]

        for original in test_cases:
            serialized = safe_json_serialize(original)
            deserialized = safe_json_deserialize(serialized)
            assert deserialized == original

    def test_compress_decompress_roundtrip(self):
        """Test that compress -> decompress returns original data."""
        test_cases = [
            {"simple": "dict"},
            [1, 2, 3, "mixed", {"nested": "list"}],
            {"large": "data" * 1000},  # Test compression benefits
            {"unicode": "世界 🌍 🚀"},
        ]

        for original in test_cases:
            compressed = compress_json_data(original)
            decompressed = decompress_json_data(compressed)
            assert decompressed == original
