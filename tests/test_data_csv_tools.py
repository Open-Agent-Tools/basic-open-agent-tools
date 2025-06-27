"""Tests for CSV processing tools."""

import pytest

from basic_open_agent_tools.data.csv_tools import (
    clean_csv_data,
    csv_to_dict_list,
    detect_csv_delimiter,
    dict_list_to_csv,
    read_csv_simple,
    validate_csv_structure,
    write_csv_simple,
)
from basic_open_agent_tools.exceptions import DataError


class TestReadCsvSimple:
    """Test read_csv_simple function."""

    def test_read_simple_csv(self, tmp_path):
        """Test reading a simple CSV file."""
        csv_content = "name,age\nAlice,25\nBob,30"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        result = read_csv_simple(csv_file)
        expected = [{"name": "Alice", "age": "25"}, {"name": "Bob", "age": "30"}]
        assert result == expected

    def test_read_csv_without_headers(self, tmp_path):
        """Test reading CSV without headers."""
        csv_content = "Alice,25\nBob,30"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        result = read_csv_simple(csv_file, headers=False)
        expected = [{"col_0": "Alice", "col_1": "25"}, {"col_0": "Bob", "col_1": "30"}]
        assert result == expected

    def test_read_csv_custom_delimiter(self, tmp_path):
        """Test reading CSV with custom delimiter."""
        csv_content = "name;age\nAlice;25\nBob;30"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        result = read_csv_simple(csv_file, delimiter=";")
        expected = [{"name": "Alice", "age": "25"}, {"name": "Bob", "age": "30"}]
        assert result == expected

    def test_read_empty_csv(self, tmp_path):
        """Test reading empty CSV file."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        result = read_csv_simple(csv_file)
        assert result == []

    def test_read_csv_headers_only(self, tmp_path):
        """Test reading CSV with headers only."""
        csv_content = "name,age"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        result = read_csv_simple(csv_file)
        assert result == []

    def test_read_nonexistent_file(self, tmp_path):
        """Test reading non-existent file."""
        nonexistent = tmp_path / "nonexistent.csv"
        with pytest.raises(DataError, match="CSV file not found"):
            read_csv_simple(nonexistent)

    def test_read_csv_invalid_types(self):
        """Test with invalid argument types."""
        with pytest.raises(TypeError, match="file_path must be a string"):
            read_csv_simple(123)

        with pytest.raises(TypeError, match="delimiter must be a string"):
            read_csv_simple("test.csv", delimiter=123)

        with pytest.raises(TypeError, match="headers must be a boolean"):
            read_csv_simple("test.csv", headers="yes")


class TestWriteCsvFile:
    """Test write_csv_simple function."""

    def test_write_simple_csv(self, tmp_path):
        """Test writing a simple CSV file."""
        data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
        csv_file = tmp_path / "output.csv"

        write_csv_simple(data, csv_file)

        # Verify content
        content = csv_file.read_text()
        assert "name,age" in content
        assert "Alice,25" in content
        assert "Bob,30" in content

    def test_write_csv_without_headers(self, tmp_path):
        """Test writing CSV without headers."""
        data = [{"name": "Alice", "age": 25}]
        csv_file = tmp_path / "output.csv"

        write_csv_simple(data, csv_file, headers=False)

        content = csv_file.read_text()
        assert "name,age" not in content
        assert "Alice,25" in content

    def test_write_csv_custom_delimiter(self, tmp_path):
        """Test writing CSV with custom delimiter."""
        data = [{"name": "Alice", "age": 25}]
        csv_file = tmp_path / "output.csv"

        write_csv_simple(data, csv_file, delimiter=";")

        content = csv_file.read_text()
        assert "name;age" in content
        assert "Alice;25" in content

    def test_write_empty_data(self, tmp_path):
        """Test writing empty data."""
        csv_file = tmp_path / "empty.csv"
        write_csv_simple([], csv_file)

        assert csv_file.read_text() == ""

    def test_write_csv_mixed_fields(self, tmp_path):
        """Test writing CSV with mixed fields across rows."""
        data = [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "city": "NYC"},
            {"age": 30, "country": "USA"},
        ]
        csv_file = tmp_path / "output.csv"

        write_csv_simple(data, csv_file)

        # Should include all unique fields
        content = csv_file.read_text()
        assert "name" in content
        assert "age" in content
        assert "city" in content
        assert "country" in content

    def test_write_csv_invalid_types(self, tmp_path):
        """Test with invalid argument types."""
        csv_file = tmp_path / "test.csv"

        with pytest.raises(TypeError, match="data must be a list"):
            write_csv_simple("not a list", csv_file)

        with pytest.raises(TypeError, match="file_path must be a string"):
            write_csv_simple([], 123)

        with pytest.raises(TypeError, match="All items in data must be dictionaries"):
            write_csv_simple(["not", "dicts"], csv_file)


class TestCsvToDictList:
    """Test csv_to_dict_list function."""

    def test_convert_simple_csv(self):
        """Test converting simple CSV string."""
        csv_str = "name,age\nAlice,25\nBob,30"
        result = csv_to_dict_list(csv_str)
        expected = [{"name": "Alice", "age": "25"}, {"name": "Bob", "age": "30"}]
        assert result == expected

    def test_convert_custom_delimiter(self):
        """Test converting CSV with custom delimiter."""
        csv_str = "name;age\nAlice;25\nBob;30"
        result = csv_to_dict_list(csv_str, delimiter=";")
        expected = [{"name": "Alice", "age": "25"}, {"name": "Bob", "age": "30"}]
        assert result == expected

    def test_convert_empty_csv(self):
        """Test converting empty CSV."""
        result = csv_to_dict_list("")
        assert result == []

    def test_convert_headers_only(self):
        """Test converting CSV with headers only."""
        result = csv_to_dict_list("name,age")
        assert result == []

    def test_convert_invalid_types(self):
        """Test with invalid argument types."""
        with pytest.raises(TypeError, match="csv_data must be a string"):
            csv_to_dict_list(123)

        with pytest.raises(TypeError, match="delimiter must be a string"):
            csv_to_dict_list("name,age", delimiter=123)


class TestDictListToCsv:
    """Test dict_list_to_csv function."""

    def test_convert_simple_data(self):
        """Test converting simple data to CSV."""
        data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
        result = dict_list_to_csv(data)

        assert "name,age" in result
        assert "Alice,25" in result
        assert "Bob,30" in result

    def test_convert_custom_delimiter(self):
        """Test converting with custom delimiter."""
        data = [{"name": "Alice", "age": 25}]
        result = dict_list_to_csv(data, delimiter=";")

        assert "name;age" in result
        assert "Alice;25" in result

    def test_convert_empty_data(self):
        """Test converting empty data."""
        result = dict_list_to_csv([])
        assert result == ""

    def test_convert_mixed_fields(self):
        """Test converting data with mixed fields."""
        data = [{"name": "Alice", "age": 25}, {"name": "Bob", "city": "NYC"}]
        result = dict_list_to_csv(data)

        lines = result.strip().split("\n")
        header = lines[0]
        assert "name" in header
        assert "age" in header
        assert "city" in header

    def test_convert_invalid_types(self):
        """Test with invalid argument types."""
        with pytest.raises(TypeError, match="data must be a list"):
            dict_list_to_csv("not a list")

        with pytest.raises(TypeError, match="All items in data must be dictionaries"):
            dict_list_to_csv(["not", "dicts"])


class TestDetectCsvDelimiter:
    """Test detect_csv_delimiter function."""

    def test_detect_comma_delimiter(self, tmp_path):
        """Test detecting comma delimiter."""
        csv_content = "name,age\nAlice,25\nBob,30"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        result = detect_csv_delimiter(csv_file)
        assert result == ","

    def test_detect_semicolon_delimiter(self, tmp_path):
        """Test detecting semicolon delimiter."""
        csv_content = "name;age\nAlice;25\nBob;30"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        result = detect_csv_delimiter(csv_file)
        assert result == ";"

    def test_detect_tab_delimiter(self, tmp_path):
        """Test detecting tab delimiter."""
        csv_content = "name\tage\nAlice\t25\nBob\t30"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        result = detect_csv_delimiter(csv_file)
        assert result == "\t"

    def test_detect_custom_sample_size(self, tmp_path):
        """Test detection with custom sample size."""
        csv_content = "name,age\n" + "Alice,25\n" * 1000
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        result = detect_csv_delimiter(csv_file, sample_size=100)
        assert result == ","

    def test_detect_empty_file(self, tmp_path):
        """Test detecting delimiter in empty file."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        with pytest.raises(DataError, match="File is empty, cannot detect delimiter"):
            detect_csv_delimiter(csv_file)

    def test_detect_nonexistent_file(self, tmp_path):
        """Test detecting delimiter in non-existent file."""
        nonexistent = tmp_path / "nonexistent.csv"
        with pytest.raises(DataError, match="CSV file not found"):
            detect_csv_delimiter(nonexistent)

    def test_detect_invalid_types(self):
        """Test with invalid argument types."""
        with pytest.raises(TypeError, match="file_path must be a string"):
            detect_csv_delimiter(123)

        with pytest.raises(TypeError, match="sample_size must be a positive integer"):
            detect_csv_delimiter("test.csv", sample_size=0)


class TestValidateCsvStructure:
    """Test validate_csv_structure function."""

    def test_validate_valid_structure(self, tmp_path):
        """Test validating valid CSV structure."""
        csv_content = "name,age,email\nAlice,25,alice@example.com"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        result = validate_csv_structure(csv_file, ["name", "age"])
        assert result is True

    def test_validate_missing_columns(self, tmp_path):
        """Test validating CSV with missing expected columns."""
        csv_content = "name,age\nAlice,25"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        with pytest.raises(DataError, match="Missing expected columns"):
            validate_csv_structure(csv_file, ["name", "age", "email"])

    def test_validate_no_expected_columns(self, tmp_path):
        """Test validating without expected columns."""
        csv_content = "name,age\nAlice,25"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        result = validate_csv_structure(csv_file)
        assert result is True

    def test_validate_empty_file(self, tmp_path):
        """Test validating empty CSV file."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        result = validate_csv_structure(csv_file)
        assert result is True

    def test_validate_invalid_types(self):
        """Test with invalid argument types."""
        with pytest.raises(TypeError, match="file_path must be a string"):
            validate_csv_structure(123)

        with pytest.raises(TypeError, match="expected_columns must be a list or None"):
            validate_csv_structure("test.csv", "not a list")


class TestCleanCsvData:
    """Test clean_csv_data function."""

    def test_clean_default_rules(self):
        """Test cleaning with default rules."""
        data = [
            {"name": "  Alice  ", "age": "25", "score": ""},
            {"name": "Bob", "age": "N/A", "score": "95"},
        ]

        result = clean_csv_data(data)
        expected = [
            {"name": "Alice", "age": "25", "score": ""},
            {"name": "Bob", "age": None, "score": "95"},
        ]
        assert result == expected

    def test_clean_custom_rules(self):
        """Test cleaning with custom rules."""
        data = [
            {"name": "  Alice  ", "age": "", "score": "N/A"},
            {"name": "Bob", "age": "30", "score": "95"},
        ]

        rules = {
            "strip_whitespace": True,
            "remove_empty": True,
            "na_values": ["N/A", "", "null"],
        }

        result = clean_csv_data(data, rules)
        expected = [
            {"name": "Alice"},  # Empty values removed when remove_empty=True
            {"name": "Bob", "age": "30", "score": "95"},
        ]
        assert result == expected

    def test_clean_no_strip_whitespace(self):
        """Test cleaning without stripping whitespace."""
        data = [{"name": "  Alice  ", "age": "25"}]
        rules = {"strip_whitespace": False}

        result = clean_csv_data(data, rules)
        assert result[0]["name"] == "  Alice  "

    def test_clean_empty_data(self):
        """Test cleaning empty data."""
        result = clean_csv_data([])
        assert result == []

    def test_clean_invalid_types(self):
        """Test with invalid argument types."""
        with pytest.raises(TypeError, match="data must be a list"):
            clean_csv_data("not a list")

        with pytest.raises(TypeError, match="rules must be a dictionary or None"):
            clean_csv_data([], "not a dict")

    def test_clean_skip_non_dict_items(self):
        """Test cleaning skips non-dictionary items."""
        data = [
            {"name": "Alice", "age": "25"},
            "not a dict",
            {"name": "Bob", "age": "30"},
        ]

        result = clean_csv_data(data)
        assert len(result) == 2
        assert result[0]["name"] == "Alice"
        assert result[1]["name"] == "Bob"


class TestRoundTripCsvOperations:
    """Test round-trip CSV operations."""

    def test_write_read_roundtrip(self, tmp_path):
        """Test that write -> read returns original data."""
        original_data = [
            {"name": "Alice", "age": "25", "city": "NYC"},
            {"name": "Bob", "age": "30", "city": "LA"},
            {"name": "Charlie", "age": "35", "city": "Chicago"},
        ]

        csv_file = tmp_path / "roundtrip.csv"
        write_csv_simple(original_data, csv_file)
        read_data = read_csv_simple(csv_file)

        # Convert age back to string for comparison (CSV always returns strings)
        expected = []
        for item in original_data:
            expected.append({k: str(v) for k, v in item.items()})

        assert read_data == expected

    def test_dict_to_csv_to_dict_roundtrip(self):
        """Test that dict_list -> CSV string -> dict_list returns original."""
        original_data = [{"name": "Alice", "age": "25"}, {"name": "Bob", "age": "30"}]

        csv_string = dict_list_to_csv(original_data)
        converted_back = csv_to_dict_list(csv_string)

        assert converted_back == original_data
