"""Tests for data structure manipulation tools."""

import pytest

from basic_open_agent_tools.data.structures import (
    compare_data_structures,
    extract_keys,
    flatten_dict_simple,
    get_nested_value_simple,
    merge_dicts_simple,
    remove_empty_values,
    rename_keys,
    safe_get,
    set_nested_value,
    unflatten_dict,
)
from basic_open_agent_tools.exceptions import DataError


class TestFlattenDict:
    """Test flatten_dict_simple function."""

    def test_flatten_simple_dict(self):
        """Test flattening a simple nested dictionary."""
        data = {"a": {"b": {"c": 1}}, "d": 2}
        result = flatten_dict_simple(data)
        expected = {"a.b.c": 1, "d": 2}
        assert result == expected

    def test_flatten_with_custom_separator(self):
        """Test flattening with custom separator."""
        data = {"a": {"b": 1}}
        result = flatten_dict_simple(data, separator="_")
        expected = {"a_b": 1}
        assert result == expected

    def test_flatten_empty_dict(self):
        """Test flattening empty dictionary."""
        result = flatten_dict_simple({})
        assert result == {}

    def test_flatten_single_level(self):
        """Test flattening single-level dictionary."""
        data = {"a": 1, "b": 2}
        result = flatten_dict_simple(data)
        assert result == data

    def test_flatten_mixed_types(self):
        """Test flattening with mixed value types."""
        data = {"a": {"b": [1, 2, 3]}, "c": "string", "d": {"e": None}}
        result = flatten_dict_simple(data)
        expected = {"a.b": [1, 2, 3], "c": "string", "d.e": None}
        assert result == expected

    def test_flatten_invalid_types(self):
        """Test with invalid argument types."""
        with pytest.raises(TypeError, match="data must be a dictionary"):
            flatten_dict_simple("not a dict")

        with pytest.raises(TypeError, match="separator must be a string"):
            flatten_dict_simple({"a": 1}, separator=123)

        with pytest.raises(DataError, match="separator cannot be empty"):
            flatten_dict_simple({"a": 1}, separator="")


class TestUnflattenDict:
    """Test unflatten_dict function."""

    def test_unflatten_simple_dict(self):
        """Test unflattening a simple flattened dictionary."""
        data = {"a.b.c": 1, "d": 2}
        result = unflatten_dict(data)
        expected = {"a": {"b": {"c": 1}}, "d": 2}
        assert result == expected

    def test_unflatten_with_custom_separator(self):
        """Test unflattening with custom separator."""
        data = {"a_b": 1}
        result = unflatten_dict(data, separator="_")
        expected = {"a": {"b": 1}}
        assert result == expected

    def test_unflatten_empty_dict(self):
        """Test unflattening empty dictionary."""
        result = unflatten_dict({})
        assert result == {}

    def test_unflatten_single_level(self):
        """Test unflattening single-level dictionary."""
        data = {"a": 1, "b": 2}
        result = unflatten_dict(data)
        assert result == data

    def test_unflatten_conflict_resolution(self):
        """Test handling conflicts when unflattening."""
        data = {"a": 1, "a.b": 2}
        result = unflatten_dict(data)
        # Later key should create nested structure
        expected = {"a": {"b": 2}}
        assert result == expected

    def test_unflatten_invalid_types(self):
        """Test with invalid argument types."""
        with pytest.raises(TypeError, match="data must be a dictionary"):
            unflatten_dict("not a dict")

        with pytest.raises(TypeError, match="separator must be a string"):
            unflatten_dict({"a": 1}, separator=123)

        with pytest.raises(DataError, match="separator cannot be empty"):
            unflatten_dict({"a": 1}, separator="")


class TestGetNestedValue:
    """Test get_nested_value_simple function."""

    def test_get_existing_nested_value(self):
        """Test getting existing nested value."""
        data = {"a": {"b": {"c": 1}}}
        result = get_nested_value_simple(data, "a.b.c")
        assert result == 1

    def test_get_nonexistent_nested_value(self):
        """Test getting non-existent nested value."""
        data = {"a": {"b": 1}}
        result = get_nested_value_simple(data, "a.b.c", default="missing")
        assert result == "missing"

    def test_get_top_level_value(self):
        """Test getting top-level value."""
        data = {"a": 1}
        result = get_nested_value_simple(data, "a")
        assert result == 1

    def test_get_empty_key_path(self):
        """Test getting with empty key path."""
        data = {"a": 1}
        result = get_nested_value_simple(data, "")
        assert result == data

    def test_get_invalid_types(self):
        """Test with invalid argument types."""
        with pytest.raises(TypeError, match="data must be a dictionary"):
            get_nested_value_simple("not a dict", "a.b")

        with pytest.raises(TypeError, match="key_path must be a string"):
            get_nested_value_simple({"a": 1}, 123)


class TestSetNestedValue:
    """Test set_nested_value function."""

    def test_set_nested_value_new_path(self):
        """Test setting value at new nested path."""
        data = {"a": {"b": 1}}
        result = set_nested_value(data, "a.c", 2)
        expected = {"a": {"b": 1, "c": 2}}
        assert result == expected
        # Original should be unchanged
        assert data == {"a": {"b": 1}}

    def test_set_nested_value_existing_path(self):
        """Test setting value at existing path."""
        data = {"a": {"b": 1}}
        result = set_nested_value(data, "a.b", 2)
        expected = {"a": {"b": 2}}
        assert result == expected

    def test_set_nested_value_deep_path(self):
        """Test setting value at deep new path."""
        data = {}
        result = set_nested_value(data, "a.b.c.d", "deep")
        expected = {"a": {"b": {"c": {"d": "deep"}}}}
        assert result == expected

    def test_set_nested_value_invalid_types(self):
        """Test with invalid argument types."""
        with pytest.raises(TypeError, match="data must be a dictionary"):
            set_nested_value("not a dict", "a.b", 1)

        with pytest.raises(TypeError, match="key_path must be a string"):
            set_nested_value({"a": 1}, 123, 1)

        with pytest.raises(DataError, match="key_path cannot be empty"):
            set_nested_value({"a": 1}, "", 1)


class TestMergeDicts:
    """Test merge_dicts_simple function."""

    def test_merge_simple_dicts(self):
        """Test merging simple dictionaries."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"c": 3, "d": 4}
        result = merge_dicts_simple([dict1, dict2])
        expected = {"a": 1, "b": 2, "c": 3, "d": 4}
        assert result == expected

    def test_merge_overlapping_dicts(self):
        """Test merging dictionaries with overlapping keys."""
        dict1 = {"a": 1, "b": {"x": 1}}
        dict2 = {"a": 2, "b": {"y": 2}}
        result = merge_dicts_simple(dict1, dict2, deep=True)
        expected = {"a": 2, "b": {"x": 1, "y": 2}}
        assert result == expected

    def test_merge_shallow(self):
        """Test shallow merge."""
        dict1 = {"a": {"x": 1}}
        dict2 = {"a": {"y": 2}}
        result = merge_dicts_simple(dict1, dict2, deep=False)
        expected = {"a": {"y": 2}}  # Shallow merge replaces entire value
        assert result == expected

    def test_merge_multiple_dicts(self):
        """Test merging multiple dictionaries."""
        dict1 = {"a": 1}
        dict2 = {"b": 2}
        dict3 = {"c": 3}
        result = merge_dicts_simple(dict1, dict2, dict3)
        expected = {"a": 1, "b": 2, "c": 3}
        assert result == expected

    def test_merge_empty_dicts(self):
        """Test merging empty dictionaries."""
        result = merge_dicts_simple()
        assert result == {}

        result = merge_dicts_simple({}, {"a": 1})
        assert result == {"a": 1}

    def test_merge_invalid_types(self):
        """Test with invalid argument types."""
        with pytest.raises(TypeError, match="All arguments must be dictionaries"):
            merge_dicts_simple({"a": 1}, "not a dict")

        with pytest.raises(TypeError, match="deep must be a boolean"):
            merge_dicts_simple({"a": 1}, {"b": 2}, deep="not bool")


class TestCompareDataStructures:
    """Test compare_data_structures function."""

    def test_compare_identical_structures(self):
        """Test comparing identical structures."""
        data1 = {"a": [1, 2, {"b": 3}]}
        data2 = {"a": [1, 2, {"b": 3}]}
        assert compare_data_structures(data1, data2) is True

    def test_compare_different_structures(self):
        """Test comparing different structures."""
        data1 = {"a": [1, 2]}
        data2 = {"a": [2, 1]}
        assert compare_data_structures(data1, data2) is False

    def test_compare_ignore_order(self):
        """Test comparing with order ignored."""
        data1 = {"a": [1, 2]}
        data2 = {"a": [2, 1]}
        assert compare_data_structures(data1, data2, ignore_order=True) is True

    def test_compare_different_types(self):
        """Test comparing different types."""
        assert compare_data_structures({"a": 1}, ["a", 1]) is False
        assert compare_data_structures(1, "1") is False

    def test_compare_complex_structures(self):
        """Test comparing complex nested structures."""
        data1 = {"users": [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]}
        data2 = {"users": [{"name": "Bob", "age": 30}, {"name": "Alice", "age": 25}]}
        assert compare_data_structures(data1, data2, ignore_order=True) is True

    def test_compare_invalid_types(self):
        """Test with invalid argument types."""
        with pytest.raises(TypeError, match="ignore_order must be a boolean"):
            compare_data_structures({"a": 1}, {"a": 1}, ignore_order="not bool")


class TestSafeGet:
    """Test safe_get function."""

    def test_safe_get_existing_key(self):
        """Test getting existing key."""
        data = {"a": 1, "b": 2}
        result = safe_get(data, "a")
        assert result == 1

    def test_safe_get_missing_key(self):
        """Test getting missing key with default."""
        data = {"a": 1}
        result = safe_get(data, "b", default="missing")
        assert result == "missing"

    def test_safe_get_missing_key_no_default(self):
        """Test getting missing key without default."""
        data = {"a": 1}
        result = safe_get(data, "b")
        assert result is None

    def test_safe_get_invalid_types(self):
        """Test with invalid argument types."""
        with pytest.raises(TypeError, match="data must be a dictionary"):
            safe_get("not a dict", "key")


class TestRemoveEmptyValues:
    """Test remove_empty_values function."""

    def test_remove_empty_values_simple(self):
        """Test removing empty values from simple dictionary."""
        data = {"a": "", "b": None, "c": 1, "d": []}
        result = remove_empty_values(data)
        expected = {"c": 1}
        assert result == expected

    def test_remove_empty_values_nested(self):
        """Test removing empty values from nested dictionary."""
        data = {"a": {"b": "", "c": 1}, "d": {"e": None}}
        result = remove_empty_values(data, recursive=True)
        expected = {"a": {"c": 1}}
        assert result == expected

    def test_remove_empty_values_non_recursive(self):
        """Test removing empty values without recursion."""
        data = {"a": {"b": ""}, "c": ""}
        result = remove_empty_values(data, recursive=False)
        expected = {"a": {"b": ""}}
        assert result == expected

    def test_remove_empty_values_invalid_types(self):
        """Test with invalid argument types."""
        with pytest.raises(TypeError, match="data must be a dictionary"):
            remove_empty_values("not a dict")

        with pytest.raises(TypeError, match="recursive must be a boolean"):
            remove_empty_values({"a": 1}, recursive="not bool")


class TestExtractKeys:
    """Test extract_keys function."""

    def test_extract_keys_simple_pattern(self):
        """Test extracting keys with simple pattern."""
        data = {"user_name": "Alice", "user_age": 25, "admin_role": "super"}
        result = extract_keys(data, r"user_.*")
        expected = ["user_name", "user_age"]
        assert sorted(result) == sorted(expected)

    def test_extract_keys_no_matches(self):
        """Test extracting keys with no matches."""
        data = {"a": 1, "b": 2}
        result = extract_keys(data, r"x_.*")
        assert result == []

    def test_extract_keys_all_match(self):
        """Test extracting keys where all match."""
        data = {"test_1": 1, "test_2": 2, "test_3": 3}
        result = extract_keys(data, r"test_.*")
        assert sorted(result) == ["test_1", "test_2", "test_3"]

    def test_extract_keys_invalid_pattern(self):
        """Test with invalid regex pattern."""
        data = {"a": 1}
        with pytest.raises(DataError, match="Invalid regular expression pattern"):
            extract_keys(data, r"[")

    def test_extract_keys_invalid_types(self):
        """Test with invalid argument types."""
        with pytest.raises(TypeError, match="data must be a dictionary"):
            extract_keys("not a dict", r".*")

        with pytest.raises(TypeError, match="key_pattern must be a string"):
            extract_keys({"a": 1}, 123)


class TestRenameKeys:
    """Test rename_keys function."""

    def test_rename_keys_simple(self):
        """Test renaming keys with simple mapping."""
        data = {"old_name": "Alice", "old_age": 25}
        mapping = {"old_name": "name", "old_age": "age"}
        result = rename_keys(data, mapping)
        expected = {"name": "Alice", "age": 25}
        assert result == expected

    def test_rename_keys_partial_mapping(self):
        """Test renaming with partial mapping."""
        data = {"a": 1, "b": 2, "c": 3}
        mapping = {"a": "x", "c": "z"}
        result = rename_keys(data, mapping)
        expected = {"x": 1, "b": 2, "z": 3}
        assert result == expected

    def test_rename_keys_empty_mapping(self):
        """Test renaming with empty mapping."""
        data = {"a": 1, "b": 2}
        result = rename_keys(data, {})
        assert result == data

    def test_rename_keys_invalid_types(self):
        """Test with invalid argument types."""
        with pytest.raises(TypeError, match="data must be a dictionary"):
            rename_keys("not a dict", {})

        with pytest.raises(TypeError, match="key_mapping must be a dictionary"):
            rename_keys({"a": 1}, "not a dict")


class TestRoundTripOperations:
    """Test round-trip operations."""

    def test_flatten_unflatten_roundtrip(self):
        """Test that flatten -> unflatten returns original."""
        original = {"a": {"b": {"c": 1}}, "d": 2, "e": {"f": 3}}
        flattened = flatten_dict_simple(original)
        result = unflatten_dict(flattened)
        assert result == original

    def test_set_get_nested_roundtrip(self):
        """Test that set_nested_value -> get_nested_value_simple works."""
        data = {"a": {"b": 1}}
        updated = set_nested_value(data, "a.c", 2)
        result = get_nested_value_simple(updated, "a.c")
        assert result == 2

    def test_merge_compare_operations(self):
        """Test merge and compare operations together."""
        dict1 = {"a": {"x": 1}}
        dict2 = {"a": {"y": 2}}
        merged = merge_dicts_simple(dict1, dict2)

        expected = {"a": {"x": 1, "y": 2}}
        assert compare_data_structures(merged, expected) is True
