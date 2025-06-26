"""Tests for data transformation functions."""

import pytest

from basic_open_agent_tools.data.transform import (
    clean_data,
    convert_data_types,
    deduplicate_records,
    normalize_data,
    pivot_data,
    rename_fields,
    transform_data,
)
from basic_open_agent_tools.exceptions import DataError


class TestTransformData:
    """Tests for transform_data function."""

    def test_transform_data_basic(self):
        """Test basic transformation with field renaming and value conversion."""
        data = [{"name": "John Doe", "age": "42"}]
        mapping = {"name": "full_name", "age": lambda x: int(x)}

        result = transform_data(data, mapping)

        assert result[0]["full_name"] == "John Doe"
        assert result[0]["age"] == 42
        assert "name" not in result[0]

    def test_transform_data_missing_field(self):
        """Test transformation with missing field."""
        data = [{"name": "John Doe"}]
        mapping = {"name": "full_name", "age": lambda x: int(x)}

        result = transform_data(data, mapping)

        assert result[0]["full_name"] == "John Doe"
        assert "age" not in result[0]

    def test_transform_data_invalid_input(self):
        """Test transformation with invalid input."""
        with pytest.raises(DataError):
            transform_data("not a list", {})

        with pytest.raises(DataError):
            transform_data([1, 2, 3], {})

    def test_transform_data_invalid_transform(self):
        """Test transformation with invalid transformation."""
        data = [{"name": "John Doe"}]
        mapping = {"name": 123}  # Not a string or callable

        with pytest.raises(DataError):
            transform_data(data, mapping)


class TestRenameFields:
    """Tests for rename_fields function."""

    def test_rename_fields_basic(self):
        """Test basic field renaming."""
        data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
        field_mapping = {"name": "full_name", "age": "years"}

        result = rename_fields(data, field_mapping)

        assert result[0]["full_name"] == "John"
        assert result[0]["years"] == 30
        assert "name" not in result[0]
        assert "age" not in result[0]

    def test_rename_fields_missing_field(self):
        """Test renaming with missing field."""
        data = [{"name": "John"}]
        field_mapping = {"name": "full_name", "age": "years"}

        result = rename_fields(data, field_mapping)

        assert result[0]["full_name"] == "John"
        assert "years" not in result[0]

    def test_rename_fields_invalid_input(self):
        """Test renaming with invalid input."""
        with pytest.raises(DataError):
            rename_fields("not a list", {})

        with pytest.raises(DataError):
            rename_fields([1, 2, 3], {})


class TestConvertDataTypes:
    """Tests for convert_data_types function."""

    def test_convert_data_types_basic(self):
        """Test basic type conversion."""
        data = [{"id": "1", "amount": "42.5", "active": "true"}]
        conversions = {
            "id": int,
            "amount": float,
            "active": lambda x: x.lower() == "true",
        }

        result = convert_data_types(data, conversions)

        assert result[0]["id"] == 1
        assert result[0]["amount"] == 42.5
        assert result[0]["active"] is True

    def test_convert_data_types_missing_field(self):
        """Test conversion with missing field."""
        data = [{"id": "1"}]
        conversions = {"id": int, "amount": float}

        result = convert_data_types(data, conversions)

        assert result[0]["id"] == 1
        assert "amount" not in result[0]

    def test_convert_data_types_none_value(self):
        """Test conversion with None value."""
        data = [{"id": "1", "amount": None}]
        conversions = {"id": int, "amount": float}

        result = convert_data_types(data, conversions)

        assert result[0]["id"] == 1
        assert result[0]["amount"] is None

    def test_convert_data_types_conversion_error(self):
        """Test conversion with error."""
        data = [{"id": "not an int"}]
        conversions = {"id": int}

        with pytest.raises(ValueError):
            convert_data_types(data, conversions)


class TestCleanData:
    """Tests for clean_data function."""

    def test_clean_data_basic(self):
        """Test basic data cleaning."""
        data = [{"name": "  John  ", "email": "JOHN@example.com"}]
        rules = {"name": [str.strip, str.title], "email": [str.lower]}

        result = clean_data(data, rules)

        assert result[0]["name"] == "John"
        assert result[0]["email"] == "john@example.com"

    def test_clean_data_missing_field(self):
        """Test cleaning with missing field."""
        data = [{"name": "John"}]
        rules = {"name": [str.strip], "email": [str.lower]}

        result = clean_data(data, rules)

        assert result[0]["name"] == "John"
        assert "email" not in result[0]

    def test_clean_data_invalid_cleaner(self):
        """Test with invalid cleaner."""
        data = [{"name": "John"}]
        rules = {"name": ["not a function"]}

        with pytest.raises(DataError):
            clean_data(data, rules)

    def test_clean_data_cleaner_error(self):
        """Test with cleaner that raises an error."""
        data = [{"name": 123}]  # Not a string
        rules = {"name": [str.strip]}

        with pytest.raises(DataError):
            clean_data(data, rules)


class TestDeduplicateRecords:
    """Tests for deduplicate_records function."""

    def test_deduplicate_records_basic(self):
        """Test basic deduplication."""
        data = [
            {"id": 1, "name": "John", "dept": "HR"},
            {"id": 2, "name": "Jane", "dept": "IT"},
            {"id": 1, "name": "John", "dept": "Sales"},
        ]

        result = deduplicate_records(data, ["id"])

        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["dept"] == "HR"  # First occurrence kept
        assert result[1]["id"] == 2

    def test_deduplicate_records_multiple_keys(self):
        """Test deduplication with multiple key fields."""
        data = [
            {"id": 1, "name": "John", "dept": "HR"},
            {"id": 2, "name": "Jane", "dept": "IT"},
            {"id": 1, "name": "Jane", "dept": "Sales"},
        ]

        result = deduplicate_records(data, ["id", "name"])

        assert len(result) == 3  # All records have unique (id, name) combinations

    def test_deduplicate_records_missing_key(self):
        """Test deduplication with missing key field."""
        data = [{"id": 1}, {"name": "John"}]

        with pytest.raises(DataError):
            deduplicate_records(data, ["id", "name"])

    def test_deduplicate_records_no_keys(self):
        """Test deduplication with no key fields."""
        data = [{"id": 1}]

        with pytest.raises(DataError):
            deduplicate_records(data, [])


class TestNormalizeData:
    """Tests for normalize_data function."""

    def test_normalize_data_basic(self):
        """Test basic data normalization."""
        data = [{"temp_f": 98.6}, {"temp_f": 100.4}]
        rules = {"temp_f": lambda f: round((f - 32) * 5 / 9, 1)}

        result = normalize_data(data, rules)

        assert result[0]["temp_f"] == 37.0
        assert result[1]["temp_f"] == 38.0

    def test_normalize_data_missing_field(self):
        """Test normalization with missing field."""
        data = [{"temp_f": 98.6}, {"humidity": 50}]
        rules = {"temp_f": lambda f: (f - 32) * 5 / 9}

        result = normalize_data(data, rules)

        assert result[0]["temp_f"] == 37.0
        assert "temp_f" not in result[1]
        assert result[1]["humidity"] == 50

    def test_normalize_data_normalizer_error(self):
        """Test with normalizer that raises an error."""
        data = [{"value": "not a number"}]
        rules = {"value": lambda x: 1 / int(x)}  # Will raise ValueError

        with pytest.raises(DataError):
            normalize_data(data, rules)


class TestPivotData:
    """Tests for pivot_data function."""

    def test_pivot_data_basic(self):
        """Test basic pivot operation."""
        data = [
            {"product": "Apple", "region": "East", "sales": 100},
            {"product": "Apple", "region": "West", "sales": 150},
            {"product": "Banana", "region": "East", "sales": 200},
            {"product": "Banana", "region": "West", "sales": 250},
        ]

        result = pivot_data(data, "product", "region", "sales")

        assert result["Apple"]["East"] == 100
        assert result["Apple"]["West"] == 150
        assert result["Banana"]["East"] == 200
        assert result["Banana"]["West"] == 250

    def test_pivot_data_missing_key(self):
        """Test pivot with missing key."""
        data = [
            {"product": "Apple", "region": "East", "sales": 100},
            {"product": "Banana", "sales": 200},  # Missing region
        ]

        with pytest.raises(DataError):
            pivot_data(data, "product", "region", "sales")

    def test_pivot_data_overwrite(self):
        """Test pivot with duplicate keys (last value wins)."""
        data = [
            {"product": "Apple", "region": "East", "sales": 100},
            {"product": "Apple", "region": "East", "sales": 200},  # Duplicate keys
        ]

        result = pivot_data(data, "product", "region", "sales")

        assert result["Apple"]["East"] == 200  # Last value wins
