"""Tests for basic_open_agent_tools.data.json_tools module."""

import json

import pytest

from basic_open_agent_tools.data.json_tools import (
    safe_json_deserialize,
    safe_json_serialize,
    validate_json_string,
)
from basic_open_agent_tools.exceptions import SerializationError


class TestSafeJsonSerialize:
    """Test cases for safe_json_serialize function."""

    def test_basic_dict_serialization(self) -> None:
        """Test basic dictionary serialization."""
        data = {"name": "test", "value": 42, "active": True}
        result = safe_json_serialize(data, 0)

        parsed = json.loads(result)
        assert parsed == data
        assert isinstance(result, str)

    def test_compact_formatting(self) -> None:
        """Test compact formatting with indent=0."""
        data = {"a": 1, "b": 2}
        result = safe_json_serialize(data, 0)

        assert "\n" not in result
        assert "  " not in result
        assert result == '{"a": 1, "b": 2}' or result == '{"b": 2, "a": 1}'

    def test_indented_formatting(self) -> None:
        """Test indented formatting with indent > 0."""
        data = {"a": 1, "b": 2}
        result = safe_json_serialize(data, 2)

        assert "\n" in result
        assert "  " in result

        lines = result.split("\n")
        assert len(lines) >= 3

    def test_various_indent_values(self) -> None:
        """Test different indent values."""
        data = {"test": "value"}

        for indent in [0, 1, 2, 4, 8]:
            result = safe_json_serialize(data, indent)
            parsed = json.loads(result)
            assert parsed == data

    def test_nested_data_structures(self) -> None:
        """Test serialization of nested data structures."""
        data = {
            "user": {"name": "John", "details": {"age": 30, "scores": [95, 87, 92]}},
            "metadata": {"created": "2023-01-01", "tags": ["important", "user-data"]},
        }

        result = safe_json_serialize(data, 2)
        parsed = json.loads(result)
        assert parsed == data

    def test_unicode_handling(self) -> None:
        """Test Unicode character handling."""
        data = {"text": "Hello 世界", "emoji": "🎉🚀", "special": "café naïve résumé"}

        result = safe_json_serialize(data, 0)
        parsed = json.loads(result)
        assert parsed == data

        assert "世界" in result
        assert "🎉🚀" in result
        assert "café" in result

    def test_various_data_types(self) -> None:
        """Test serialization of various JSON-compatible data types."""
        data = {
            "string": "test",
            "integer": 42,
            "float": 3.14159,
            "boolean_true": True,
            "boolean_false": False,
            "null_value": None,
            "list": [1, 2, 3],
            "empty_list": [],
            "empty_dict": {},
        }

        result = safe_json_serialize(data, 0)
        parsed = json.loads(result)
        assert parsed == data

    def test_large_data_structure(self) -> None:
        """Test serialization of large data structures."""
        data = {
            "items": [{"id": i, "value": f"item_{i}"} for i in range(100)],
            "metadata": {"count": 100, "description": "Large test dataset"},
        }

        result = safe_json_serialize(data, 0)
        parsed = json.loads(result)
        assert parsed == data
        assert len(parsed["items"]) == 100

    def test_invalid_indent_type(self) -> None:
        """Test error handling for invalid indent type."""
        data = {"test": "value"}

        with pytest.raises(TypeError, match="indent must be an integer"):
            safe_json_serialize(data, "2")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="indent must be an integer"):
            safe_json_serialize(data, 2.5)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="indent must be an integer"):
            safe_json_serialize(data, None)  # type: ignore[arg-type]

    def test_non_serializable_data(self) -> None:
        """Test error handling for non-serializable data."""
        data = {"function": lambda x: x}  # type: ignore[dict-item]

        with pytest.raises(
            SerializationError, match="Failed to serialize data to JSON"
        ):
            safe_json_serialize(data, 0)

    def test_complex_object_error(self) -> None:
        """Test error handling for complex objects."""

        class CustomObject:
            def __init__(self) -> None:
                self.value = "test"

        data = {"object": CustomObject()}  # type: ignore[dict-item]

        with pytest.raises(
            SerializationError, match="Failed to serialize data to JSON"
        ):
            safe_json_serialize(data, 0)

    def test_empty_data_structures(self) -> None:
        """Test serialization of empty data structures."""
        result = safe_json_serialize({}, 0)
        assert result == "{}"

        data = {"empty_list": [], "empty_dict": {}, "empty_string": ""}
        result = safe_json_serialize(data, 0)
        parsed = json.loads(result)
        assert parsed == data


class TestSafeJsonDeserialize:
    """Test cases for safe_json_deserialize function."""

    def test_basic_dict_deserialization(self) -> None:
        """Test basic dictionary deserialization."""
        json_str = '{"name": "test", "value": 42, "active": true}'
        result = safe_json_deserialize(json_str)

        expected = {"name": "test", "value": 42, "active": True}
        assert result == expected
        assert isinstance(result, dict)

    def test_dict_return_type(self) -> None:
        """Test that dict input returns dict directly."""
        json_str = '{"key": "value"}'
        result = safe_json_deserialize(json_str)

        assert isinstance(result, dict)
        assert result == {"key": "value"}

    def test_list_wrapping(self) -> None:
        """Test that non-dict results are wrapped in dict."""
        json_str = "[1, 2, 3]"
        result = safe_json_deserialize(json_str)

        assert isinstance(result, dict)
        assert result == {"result": [1, 2, 3]}

    def test_string_wrapping(self) -> None:
        """Test that string results are wrapped in dict."""
        json_str = '"hello world"'
        result = safe_json_deserialize(json_str)

        assert isinstance(result, dict)
        assert result == {"result": "hello world"}

    def test_number_wrapping(self) -> None:
        """Test that number results are wrapped in dict."""
        json_str = "42"
        result = safe_json_deserialize(json_str)
        assert result == {"result": 42}

        json_str = "3.14159"
        result = safe_json_deserialize(json_str)
        assert result == {"result": 3.14159}

    def test_boolean_wrapping(self) -> None:
        """Test that boolean results are wrapped in dict."""
        json_str = "true"
        result = safe_json_deserialize(json_str)
        assert result == {"result": True}

        json_str = "false"
        result = safe_json_deserialize(json_str)
        assert result == {"result": False}

    def test_null_wrapping(self) -> None:
        """Test that null results are wrapped in dict."""
        json_str = "null"
        result = safe_json_deserialize(json_str)
        assert result == {"result": None}

    def test_nested_structures(self) -> None:
        """Test deserialization of nested data structures."""
        json_str = """
        {
            "user": {
                "name": "John",
                "details": {
                    "age": 30,
                    "scores": [95, 87, 92]
                }
            },
            "metadata": {
                "created": "2023-01-01",
                "tags": ["important", "user-data"]
            }
        }
        """

        result = safe_json_deserialize(json_str)

        assert isinstance(result, dict)
        assert "user" in result
        assert "metadata" in result
        assert result["user"]["name"] == "John"
        assert result["user"]["details"]["age"] == 30
        assert result["user"]["details"]["scores"] == [95, 87, 92]

    def test_unicode_handling(self) -> None:
        """Test Unicode character handling in deserialization."""
        json_str = (
            '{"text": "Hello 世界", "emoji": "🎉🚀", "special": "café naïve résumé"}'
        )
        result = safe_json_deserialize(json_str)

        assert result["text"] == "Hello 世界"
        assert result["emoji"] == "🎉🚀"
        assert result["special"] == "café naïve résumé"

    def test_various_json_formats(self) -> None:
        """Test various valid JSON format variations."""
        result = safe_json_deserialize('{"a":1,"b":2}')
        assert result == {"a": 1, "b": 2}

        result = safe_json_deserialize('{ "a" : 1 , "b" : 2 }')
        assert result == {"a": 1, "b": 2}

        json_str = """{
            "a": 1,
            "b": 2
        }"""
        result = safe_json_deserialize(json_str)
        assert result == {"a": 1, "b": 2}

    def test_empty_structures(self) -> None:
        """Test deserialization of empty structures."""
        result = safe_json_deserialize("{}")
        assert result == {}

        result = safe_json_deserialize("[]")
        assert result == {"result": []}

    def test_invalid_input_type(self) -> None:
        """Test error handling for invalid input types."""
        with pytest.raises(TypeError, match="Input must be a string"):
            safe_json_deserialize(42)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="Input must be a string"):
            safe_json_deserialize(["not", "a", "string"])  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="Input must be a string"):
            safe_json_deserialize(None)  # type: ignore[arg-type]

    def test_invalid_json_string(self) -> None:
        """Test error handling for invalid JSON strings."""
        invalid_json_cases = [
            '{"invalid": }',
            '{"unclosed": "string}',
            '{invalid: "no quotes"}',
            '{"trailing": "comma",}',
            "{",
            "[",
            '{"a": 1, "b":}',
            "",
            "not json at all",
        ]

        for invalid_json in invalid_json_cases:
            with pytest.raises(
                SerializationError, match="Failed to deserialize JSON string"
            ):
                safe_json_deserialize(invalid_json)

    def test_duplicate_keys_handling(self) -> None:
        """Test handling of duplicate keys in JSON (valid but worth testing)."""
        json_str = '{"duplicate": 1, "duplicate": 2}'
        result = safe_json_deserialize(json_str)
        assert result == {"duplicate": 2}

    def test_malformed_unicode(self) -> None:
        """Test handling of malformed Unicode sequences."""
        invalid_cases = [
            '{"bad_escape": "\\u"}',
            '{"bad_escape": "\\uGGGG"}',
        ]

        for invalid_case in invalid_cases:
            with pytest.raises(
                SerializationError, match="Failed to deserialize JSON string"
            ):
                safe_json_deserialize(invalid_case)


class TestValidateJsonString:
    """Test cases for validate_json_string function."""

    def test_valid_json_objects(self) -> None:
        """Test validation of valid JSON objects."""
        valid_cases = [
            "{}",
            '{"key": "value"}',
            '{"a": 1, "b": 2}',
            '{"nested": {"key": "value"}}',
            '{"array": [1, 2, 3]}',
            '{"mixed": {"num": 42, "arr": [1, 2], "bool": true}}',
        ]

        for valid_json in valid_cases:
            assert validate_json_string(valid_json) is True

    def test_valid_json_arrays(self) -> None:
        """Test validation of valid JSON arrays."""
        valid_cases = [
            "[]",
            "[1, 2, 3]",
            '["a", "b", "c"]',
            '[{"key": "value"}]',
            '[1, "two", true, null]',
            "[[1, 2], [3, 4]]",
        ]

        for valid_json in valid_cases:
            assert validate_json_string(valid_json) is True

    def test_valid_json_primitives(self) -> None:
        """Test validation of valid JSON primitive values."""
        valid_cases = [
            '"string"',
            "42",
            "3.14159",
            "true",
            "false",
            "null",
        ]

        for valid_json in valid_cases:
            assert validate_json_string(valid_json) is True

    def test_valid_json_with_unicode(self) -> None:
        """Test validation of JSON with Unicode characters."""
        valid_cases = [
            '{"text": "Hello 世界"}',
            '{"emoji": "🎉🚀"}',
            '{"special": "café naïve résumé"}',
            '["unicode", "世界", "🚀"]',
        ]

        for valid_json in valid_cases:
            assert validate_json_string(valid_json) is True

    def test_valid_json_formatting_variations(self) -> None:
        """Test validation of various JSON formatting styles."""
        valid_cases = [
            '{"a":1,"b":2}',
            '{ "a" : 1 , "b" : 2 }',
            '{\n  "a": 1,\n  "b": 2\n}',
            '{"a": 1, "b": 2}',
        ]

        for valid_json in valid_cases:
            assert validate_json_string(valid_json) is True

    def test_invalid_json_strings(self) -> None:
        """Test validation of invalid JSON strings."""
        invalid_cases = [
            '{"invalid": }',
            '{"unclosed": "string}',
            '{invalid: "no quotes"}',
            '{"trailing": "comma",}',
            "{",
            "[",
            '{"a": 1, "b":}',
            "",
            "not json at all",
            '{"bad_escape": "\\u"}',
            '{"bad_escape": "\\uGGGG"}',
            "undefined",
            "{a: 1}",
            "{'single': 'quotes'}",
        ]

        for invalid_json in invalid_cases:
            assert validate_json_string(invalid_json) is False

    def test_non_string_input(self) -> None:
        """Test validation behavior with non-string input."""
        non_string_cases = [
            42,
            3.14,
            True,
            False,
            None,
            [],
            {},
            {"key": "value"},
        ]

        for non_string in non_string_cases:
            assert validate_json_string(non_string) is False  # type: ignore[arg-type]

    def test_edge_cases(self) -> None:
        """Test validation of edge cases."""
        assert validate_json_string("999999999999999999999999999999999") is True

        long_string = '"' + "a" * 10000 + '"'
        assert validate_json_string(long_string) is True

        nested = '{"a": {"b": {"c": {"d": "value"}}}}'
        assert validate_json_string(nested) is True

        large_array = "[" + ",".join(str(i) for i in range(1000)) + "]"
        assert validate_json_string(large_array) is True


class TestJsonToolsIntegration:
    """Integration tests for JSON tools working together."""

    def test_serialize_deserialize_roundtrip(self) -> None:
        """Test that serialize -> deserialize maintains data integrity."""
        original_data = {
            "string": "test",
            "number": 42,
            "float": 3.14159,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "nested": {"key": "value", "array": ["a", "b", "c"]},
        }

        json_str = safe_json_serialize(original_data, 0)

        assert validate_json_string(json_str) is True

        result_data = safe_json_deserialize(json_str)

        assert result_data == original_data

    def test_validation_with_serialized_data(self) -> None:
        """Test that serialized data always passes validation."""
        test_cases = [
            {},
            {"simple": "value"},
            {"complex": {"nested": [1, 2, {"deep": True}]}},
            {"unicode": "世界 🚀 café"},
        ]

        for data in test_cases:
            json_str = safe_json_serialize(data, 2)
            assert validate_json_string(json_str) is True

    def test_error_consistency(self) -> None:
        """Test that invalid JSON fails consistently across functions."""
        invalid_json = '{"invalid": }'

        assert validate_json_string(invalid_json) is False

        with pytest.raises(SerializationError):
            safe_json_deserialize(invalid_json)

    def test_type_wrapping_consistency(self) -> None:
        """Test that non-dict deserialization wrapping works correctly."""
        test_cases = [
            ("[1, 2, 3]", {"result": [1, 2, 3]}),
            ('"string"', {"result": "string"}),
            ("42", {"result": 42}),
            ("true", {"result": True}),
            ("null", {"result": None}),
        ]

        for json_str, expected in test_cases:
            assert validate_json_string(json_str) is True

            result = safe_json_deserialize(json_str)
            assert result == expected
            assert isinstance(result, dict)
