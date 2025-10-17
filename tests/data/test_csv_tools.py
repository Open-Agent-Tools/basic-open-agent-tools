"""Tests for basic_open_agent_tools.data.csv_tools module."""

from pathlib import Path

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
    """Test cases for read_csv_simple function."""

    def test_read_csv_with_headers(self, tmp_path: Path) -> None:
        """Test reading CSV file with headers."""
        csv_file = tmp_path / "test.csv"
        csv_content = "name,age,city\nAlice,25,NYC\nBob,30,LA"
        csv_file.write_text(csv_content, encoding="utf-8")

        result = read_csv_simple(str(csv_file), ",", True)

        expected = [
            {"name": "Alice", "age": "25", "city": "NYC"},
            {"name": "Bob", "age": "30", "city": "LA"},
        ]
        assert result == expected

    def test_read_csv_without_headers(self, tmp_path: Path) -> None:
        """Test reading CSV file without headers."""
        csv_file = tmp_path / "test.csv"
        csv_content = "Alice,25,NYC\nBob,30,LA"
        csv_file.write_text(csv_content, encoding="utf-8")

        result = read_csv_simple(str(csv_file), ",", False)

        expected = [
            {"col_0": "Alice", "col_1": "25", "col_2": "NYC"},
            {"col_0": "Bob", "col_1": "30", "col_2": "LA"},
        ]
        assert result == expected

    def test_read_csv_with_different_delimiter(self, tmp_path: Path) -> None:
        """Test reading CSV with different delimiter."""
        csv_file = tmp_path / "test.csv"
        csv_content = "name;age;city\nAlice;25;NYC\nBob;30;LA"
        csv_file.write_text(csv_content, encoding="utf-8")

        result = read_csv_simple(str(csv_file), ";", True)

        expected = [
            {"name": "Alice", "age": "25", "city": "NYC"},
            {"name": "Bob", "age": "30", "city": "LA"},
        ]
        assert result == expected

    def test_read_empty_csv_file(self, tmp_path: Path) -> None:
        """Test reading empty CSV file."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("", encoding="utf-8")

        result = read_csv_simple(str(csv_file), ",", True)
        assert result == []

        result = read_csv_simple(str(csv_file), ",", False)
        assert result == []

    def test_read_csv_with_only_headers(self, tmp_path: Path) -> None:
        """Test reading CSV with only header row."""
        csv_file = tmp_path / "headers_only.csv"
        csv_content = "name,age,city"
        csv_file.write_text(csv_content, encoding="utf-8")

        result = read_csv_simple(str(csv_file), ",", True)
        assert result == []

    def test_read_csv_with_unicode(self, tmp_path: Path) -> None:
        """Test reading CSV with Unicode characters."""
        csv_file = tmp_path / "unicode.csv"
        csv_content = "name,city\nAlice,北京\nBob,Москва\nCarlos,São Paulo"
        csv_file.write_text(csv_content, encoding="utf-8")

        result = read_csv_simple(str(csv_file), ",", True)

        expected = [
            {"name": "Alice", "city": "北京"},
            {"name": "Bob", "city": "Москва"},
            {"name": "Carlos", "city": "São Paulo"},
        ]
        assert result == expected

    def test_read_csv_with_quoted_fields(self, tmp_path: Path) -> None:
        """Test reading CSV with quoted fields containing commas."""
        csv_file = tmp_path / "quoted.csv"
        csv_content = (
            'name,description\nAlice,"Engineer, Software"\nBob,"Manager, Sales"'
        )
        csv_file.write_text(csv_content, encoding="utf-8")

        result = read_csv_simple(str(csv_file), ",", True)

        expected = [
            {"name": "Alice", "description": "Engineer, Software"},
            {"name": "Bob", "description": "Manager, Sales"},
        ]
        assert result == expected

    def test_read_csv_file_not_found(self) -> None:
        """Test error handling when CSV file doesn't exist."""
        with pytest.raises(DataError, match="CSV file not found"):
            read_csv_simple("nonexistent.csv", ",", True)

    def test_read_csv_invalid_file_path_type(self) -> None:
        """Test error handling for invalid file_path type."""
        with pytest.raises(TypeError, match="file_path must be a string"):
            read_csv_simple(123, ",", True)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="file_path must be a string"):
            read_csv_simple(None, ",", True)  # type: ignore[arg-type]

    def test_read_csv_invalid_delimiter_type(self, tmp_path: Path) -> None:
        """Test error handling for invalid delimiter type."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,age\nAlice,25", encoding="utf-8")

        with pytest.raises(TypeError, match="delimiter must be a string"):
            read_csv_simple(str(csv_file), 123, True)  # type: ignore[arg-type]

    def test_read_csv_invalid_headers_type(self, tmp_path: Path) -> None:
        """Test error handling for invalid headers type."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,age\nAlice,25", encoding="utf-8")

        with pytest.raises(TypeError, match="headers must be a boolean"):
            read_csv_simple(str(csv_file), ",", "yes")  # type: ignore[arg-type]

    def test_read_csv_malformed_data(self, tmp_path: Path) -> None:
        """Test reading CSV with unusual but valid data."""
        csv_file = tmp_path / "unusual.csv"
        # Create a file with unmatched quotes (Python CSV reader handles this)
        csv_content = 'name,age\n"Alice,25\nBob,30'
        csv_file.write_text(csv_content, encoding="utf-8")

        # This should work because Python's CSV reader is lenient
        result = read_csv_simple(str(csv_file), ",", True)
        assert len(result) == 1  # CSV reader treats this as one record
        assert "name" in result[0]
        assert "age" in result[0]


class TestWriteCsvSimple:
    """Test cases for write_csv_simple function."""

    def test_write_csv_with_headers(self, tmp_path: Path) -> None:
        """Test writing CSV file with headers."""
        data = [
            {"name": "Alice", "age": "25", "city": "NYC"},
            {"name": "Bob", "age": "30", "city": "LA"},
        ]
        csv_file = tmp_path / "output.csv"

        write_csv_simple(data, str(csv_file), ",", True, skip_confirm=True)

        # Read back and verify
        content = csv_file.read_text(encoding="utf-8")
        lines = content.strip().split("\n")
        assert lines[0] == "name,age,city"
        assert "Alice,25,NYC" in lines
        assert "Bob,30,LA" in lines

    def test_write_csv_without_headers(self, tmp_path: Path) -> None:
        """Test writing CSV file without headers."""
        data = [
            {"name": "Alice", "age": "25"},
            {"name": "Bob", "age": "30"},
        ]
        csv_file = tmp_path / "output.csv"

        write_csv_simple(data, str(csv_file), ",", False, skip_confirm=True)

        # Read back and verify
        content = csv_file.read_text(encoding="utf-8")
        lines = content.strip().split("\n")
        assert "Alice,25" in lines
        assert "Bob,30" in lines
        # Should not contain header line
        assert "name,age" not in lines

    def test_write_csv_with_different_delimiter(self, tmp_path: Path) -> None:
        """Test writing CSV with different delimiter."""
        data = [{"name": "Alice", "age": "25"}]
        csv_file = tmp_path / "output.csv"

        write_csv_simple(data, str(csv_file), ";", True, skip_confirm=True)

        content = csv_file.read_text(encoding="utf-8")
        assert "name;age" in content
        assert "Alice;25" in content

    def test_write_empty_data(self, tmp_path: Path) -> None:
        """Test writing empty data."""
        data = []
        csv_file = tmp_path / "empty.csv"

        write_csv_simple(data, str(csv_file), ",", True, skip_confirm=True)

        content = csv_file.read_text(encoding="utf-8")
        assert content == ""

    def test_write_csv_with_unicode(self, tmp_path: Path) -> None:
        """Test writing CSV with Unicode characters."""
        data = [
            {"name": "Alice", "city": "北京"},
            {"name": "Bob", "city": "Москва"},
        ]
        csv_file = tmp_path / "unicode.csv"

        write_csv_simple(data, str(csv_file), ",", True, skip_confirm=True)

        content = csv_file.read_text(encoding="utf-8")
        assert "北京" in content
        assert "Москва" in content

    def test_write_csv_with_mixed_keys(self, tmp_path: Path) -> None:
        """Test writing CSV with dictionaries having different keys."""
        data = [
            {"name": "Alice", "age": "25"},
            {"name": "Bob", "city": "LA"},
            {"age": "35", "country": "USA"},
        ]
        csv_file = tmp_path / "mixed.csv"

        write_csv_simple(data, str(csv_file), ",", True, skip_confirm=True)

        # Read back to verify all keys are included
        result = read_csv_simple(str(csv_file), ",", True)
        assert len(result) == 3
        # All unique keys should be present as columns
        all_keys = set()
        for row in result:
            all_keys.update(row.keys())
        assert "name" in all_keys
        assert "age" in all_keys
        assert "city" in all_keys
        assert "country" in all_keys

    def test_write_csv_invalid_data_type(self, tmp_path: Path) -> None:
        """Test error handling for invalid data type."""
        csv_file = tmp_path / "output.csv"

        with pytest.raises(TypeError, match="data must be a list"):
            write_csv_simple(
                {"not": "list"}, str(csv_file), ",", True, skip_confirm=True
            )  # type: ignore[arg-type]

    def test_write_csv_invalid_file_path_type(self) -> None:
        """Test error handling for invalid file_path type."""
        data = [{"name": "Alice"}]

        with pytest.raises(TypeError, match="file_path must be a string"):
            write_csv_simple(data, 123, ",", True, skip_confirm=True)  # type: ignore[arg-type]

    def test_write_csv_invalid_data_items(self, tmp_path: Path) -> None:
        """Test error handling for invalid data items."""
        data = [{"name": "Alice"}, "not a dict", {"age": "25"}]  # type: ignore[list-item]
        csv_file = tmp_path / "output.csv"

        with pytest.raises(TypeError, match="All items in data must be dictionaries"):
            write_csv_simple(data, str(csv_file), ",", True, skip_confirm=True)

    def test_write_csv_permission_error(self, tmp_path: Path) -> None:
        """Test error handling for file permission issues."""
        data = [{"name": "Alice"}]
        # Try to write to a directory (should fail)
        invalid_path = tmp_path / "directory_not_file"
        invalid_path.mkdir()

        with pytest.raises(DataError, match="Failed to write CSV file"):
            write_csv_simple(data, str(invalid_path), ",", True, skip_confirm=True)


class TestCsvToDictList:
    """Test cases for csv_to_dict_list function."""

    def test_csv_string_to_dict_list(self) -> None:
        """Test converting CSV string to dictionary list."""
        csv_data = "name,age,city\nAlice,25,NYC\nBob,30,LA"

        result = csv_to_dict_list(csv_data, ",")

        expected = [
            {"name": "Alice", "age": "25", "city": "NYC"},
            {"name": "Bob", "age": "30", "city": "LA"},
        ]
        assert result == expected

    def test_csv_string_with_different_delimiter(self) -> None:
        """Test CSV string with different delimiter."""
        csv_data = "name;age;city\nAlice;25;NYC\nBob;30;LA"

        result = csv_to_dict_list(csv_data, ";")

        expected = [
            {"name": "Alice", "age": "25", "city": "NYC"},
            {"name": "Bob", "age": "30", "city": "LA"},
        ]
        assert result == expected

    def test_csv_string_empty(self) -> None:
        """Test converting empty CSV string."""
        result = csv_to_dict_list("", ",")
        assert result == []

    def test_csv_string_headers_only(self) -> None:
        """Test CSV string with only headers."""
        csv_data = "name,age,city"

        result = csv_to_dict_list(csv_data, ",")
        assert result == []

    def test_csv_string_with_unicode(self) -> None:
        """Test CSV string with Unicode characters."""
        csv_data = "name,city\nAlice,北京\nBob,Москва"

        result = csv_to_dict_list(csv_data, ",")

        expected = [
            {"name": "Alice", "city": "北京"},
            {"name": "Bob", "city": "Москва"},
        ]
        assert result == expected

    def test_csv_string_with_quoted_fields(self) -> None:
        """Test CSV string with quoted fields."""
        csv_data = 'name,description\nAlice,"Engineer, Software"\nBob,"Manager, Sales"'

        result = csv_to_dict_list(csv_data, ",")

        expected = [
            {"name": "Alice", "description": "Engineer, Software"},
            {"name": "Bob", "description": "Manager, Sales"},
        ]
        assert result == expected

    def test_csv_string_invalid_type(self) -> None:
        """Test error handling for invalid csv_data type."""
        with pytest.raises(TypeError, match="csv_data must be a string"):
            csv_to_dict_list(123, ",")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="csv_data must be a string"):
            csv_to_dict_list(None, ",")  # type: ignore[arg-type]

    def test_csv_string_invalid_delimiter_type(self) -> None:
        """Test error handling for invalid delimiter type."""
        with pytest.raises(TypeError, match="delimiter must be a string"):
            csv_to_dict_list("name,age\nAlice,25", 123)  # type: ignore[arg-type]

    def test_csv_string_malformed_data(self) -> None:
        """Test parsing CSV string with unusual but valid data."""
        unusual_csv = 'name,age\n"Alice,25\nBob,30'

        # This should work because Python's CSV reader is lenient
        result = csv_to_dict_list(unusual_csv, ",")
        assert len(result) == 1  # CSV reader treats this as one record
        assert "name" in result[0]
        assert "age" in result[0]


class TestDictListToCsv:
    """Test cases for dict_list_to_csv function."""

    def test_dict_list_to_csv_string(self) -> None:
        """Test converting dictionary list to CSV string."""
        data = [
            {"name": "Alice", "age": "25", "city": "NYC"},
            {"name": "Bob", "age": "30", "city": "LA"},
        ]

        result = dict_list_to_csv(data, ",")

        # Parse result back to verify
        lines = [line.strip() for line in result.strip().split("\n")]
        assert (
            "name,age,city" in lines or "name,city,age" in lines
        )  # Header order may vary
        assert "Alice,25,NYC" in result or "Alice,NYC,25" in result
        assert "Bob,30,LA" in result or "Bob,LA,30" in result

    def test_dict_list_to_csv_with_delimiter(self) -> None:
        """Test CSV conversion with different delimiter."""
        data = [{"name": "Alice", "age": "25"}]

        result = dict_list_to_csv(data, ";")

        assert "name;age" in result or "age;name" in result
        assert "Alice;25" in result or "25;Alice" in result

    def test_dict_list_to_csv_empty_data(self) -> None:
        """Test converting empty data."""
        result = dict_list_to_csv([], ",")
        assert result == ""

    def test_dict_list_to_csv_with_unicode(self) -> None:
        """Test CSV conversion with Unicode characters."""
        data = [
            {"name": "Alice", "city": "北京"},
            {"name": "Bob", "city": "Москва"},
        ]

        result = dict_list_to_csv(data, ",")

        assert "北京" in result
        assert "Москва" in result

    def test_dict_list_to_csv_mixed_keys(self) -> None:
        """Test CSV conversion with mixed dictionary keys."""
        data = [
            {"name": "Alice", "age": "25"},
            {"name": "Bob", "city": "LA"},
            {"age": "35", "country": "USA"},
        ]

        result = dict_list_to_csv(data, ",")

        # All keys should be included as columns
        assert "name" in result
        assert "age" in result
        assert "city" in result
        assert "country" in result

    def test_dict_list_to_csv_invalid_data_type(self) -> None:
        """Test error handling for invalid data type."""
        with pytest.raises(TypeError, match="data must be a list"):
            dict_list_to_csv({"not": "list"}, ",")  # type: ignore[arg-type]

    def test_dict_list_to_csv_invalid_data_items(self) -> None:
        """Test error handling for invalid data items."""
        data = [{"name": "Alice"}, "not a dict"]  # type: ignore[list-item]

        with pytest.raises(TypeError, match="All items in data must be dictionaries"):
            dict_list_to_csv(data, ",")


class TestDetectCsvDelimiter:
    """Test cases for detect_csv_delimiter function."""

    def test_detect_comma_delimiter(self, tmp_path: Path) -> None:
        """Test detecting comma delimiter."""
        csv_file = tmp_path / "comma.csv"
        csv_content = "name,age,city\nAlice,25,NYC\nBob,30,LA"
        csv_file.write_text(csv_content, encoding="utf-8")

        result = detect_csv_delimiter(str(csv_file), 1000)
        assert result == ","

    def test_detect_semicolon_delimiter(self, tmp_path: Path) -> None:
        """Test detecting semicolon delimiter."""
        csv_file = tmp_path / "semicolon.csv"
        csv_content = "name;age;city\nAlice;25;NYC\nBob;30;LA"
        csv_file.write_text(csv_content, encoding="utf-8")

        result = detect_csv_delimiter(str(csv_file), 1000)
        assert result == ";"

    def test_detect_tab_delimiter(self, tmp_path: Path) -> None:
        """Test detecting tab delimiter."""
        csv_file = tmp_path / "tab.csv"
        csv_content = "name\tage\tcity\nAlice\t25\tNYC\nBob\t30\tLA"
        csv_file.write_text(csv_content, encoding="utf-8")

        result = detect_csv_delimiter(str(csv_file), 1000)
        assert result == "\t"

    def test_detect_pipe_delimiter(self, tmp_path: Path) -> None:
        """Test detecting pipe delimiter."""
        csv_file = tmp_path / "pipe.csv"
        csv_content = "name|age|city\nAlice|25|NYC\nBob|30|LA"
        csv_file.write_text(csv_content, encoding="utf-8")

        result = detect_csv_delimiter(str(csv_file), 1000)
        assert result == "|"

    def test_detect_delimiter_with_sample_size(self, tmp_path: Path) -> None:
        """Test delimiter detection with limited sample size."""
        csv_file = tmp_path / "large.csv"
        csv_content = "name,age,city\n" + "Alice,25,NYC\n" * 1000 + "Bob,30,LA"
        csv_file.write_text(csv_content, encoding="utf-8")

        result = detect_csv_delimiter(str(csv_file), 50)  # Small sample
        assert result == ","

    def test_detect_delimiter_file_not_found(self) -> None:
        """Test error handling when file doesn't exist."""
        with pytest.raises(DataError, match="CSV file not found"):
            detect_csv_delimiter("nonexistent.csv", 1000)

    def test_detect_delimiter_empty_file(self, tmp_path: Path) -> None:
        """Test error handling for empty file."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("", encoding="utf-8")

        with pytest.raises(DataError, match="File is empty, cannot detect delimiter"):
            detect_csv_delimiter(str(csv_file), 1000)

    def test_detect_delimiter_invalid_file_path_type(self) -> None:
        """Test error handling for invalid file_path type."""
        with pytest.raises(TypeError, match="file_path must be a string"):
            detect_csv_delimiter(123, 1000)  # type: ignore[arg-type]

    def test_detect_delimiter_invalid_sample_size_type(self, tmp_path: Path) -> None:
        """Test error handling for invalid sample_size type."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,age\nAlice,25", encoding="utf-8")

        with pytest.raises(TypeError, match="sample_size must be a positive integer"):
            detect_csv_delimiter(str(csv_file), "1000")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="sample_size must be a positive integer"):
            detect_csv_delimiter(str(csv_file), 0)

        with pytest.raises(TypeError, match="sample_size must be a positive integer"):
            detect_csv_delimiter(str(csv_file), -10)


class TestValidateCsvStructure:
    """Test cases for validate_csv_structure function."""

    def test_validate_csv_structure_valid(self, tmp_path: Path) -> None:
        """Test validation of valid CSV structure."""
        csv_file = tmp_path / "valid.csv"
        csv_content = (
            "name,age,email\nAlice,25,alice@example.com\nBob,30,bob@example.com"
        )
        csv_file.write_text(csv_content, encoding="utf-8")

        result = validate_csv_structure(str(csv_file), ["name", "age", "email"])
        assert result is True

    def test_validate_csv_structure_subset_columns(self, tmp_path: Path) -> None:
        """Test validation when expected columns are subset of actual."""
        csv_file = tmp_path / "extra_columns.csv"
        csv_content = "name,age,email,city\nAlice,25,alice@example.com,NYC\nBob,30,bob@example.com,LA"
        csv_file.write_text(csv_content, encoding="utf-8")

        result = validate_csv_structure(str(csv_file), ["name", "age"])
        assert result is True

    def test_validate_csv_structure_missing_columns(self, tmp_path: Path) -> None:
        """Test validation failure when columns are missing."""
        csv_file = tmp_path / "missing_columns.csv"
        csv_content = "name,age\nAlice,25\nBob,30"
        csv_file.write_text(csv_content, encoding="utf-8")

        with pytest.raises(DataError, match="Missing expected columns"):
            validate_csv_structure(str(csv_file), ["name", "age", "email"])

    def test_validate_csv_structure_empty_file(self, tmp_path: Path) -> None:
        """Test validation of empty file."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("", encoding="utf-8")

        result = validate_csv_structure(str(csv_file), ["name", "age"])
        assert result is True  # Empty file is considered valid

    def test_validate_csv_structure_no_expected_columns(self, tmp_path: Path) -> None:
        """Test validation with no expected columns."""
        csv_file = tmp_path / "any.csv"
        csv_content = "col1,col2\nvalue1,value2"
        csv_file.write_text(csv_content, encoding="utf-8")

        result = validate_csv_structure(str(csv_file), [])
        assert result is True

    def test_validate_csv_structure_file_not_found(self) -> None:
        """Test error handling when file doesn't exist."""
        with pytest.raises(DataError, match="CSV file not found"):
            validate_csv_structure("nonexistent.csv", ["name"])

    def test_validate_csv_structure_invalid_file_path_type(self) -> None:
        """Test error handling for invalid file_path type."""
        with pytest.raises(TypeError, match="file_path must be a string"):
            validate_csv_structure(123, ["name"])  # type: ignore[arg-type]

    def test_validate_csv_structure_invalid_expected_columns_type(
        self, tmp_path: Path
    ) -> None:
        """Test error handling for invalid expected_columns type."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,age\nAlice,25", encoding="utf-8")

        with pytest.raises(TypeError, match="expected_columns must be a list"):
            validate_csv_structure(str(csv_file), "name,age")  # type: ignore[arg-type]

    def test_validate_csv_structure_malformed_file(self, tmp_path: Path) -> None:
        """Test validation of unusual but valid CSV file."""
        csv_file = tmp_path / "unusual.csv"
        csv_content = 'name,age\n"Alice,25\nBob,30'  # Python CSV reader handles this
        csv_file.write_text(csv_content, encoding="utf-8")

        # This should succeed because Python's CSV reader is lenient
        result = validate_csv_structure(str(csv_file), ["name", "age"])
        assert result is True


class TestCleanCsvData:
    """Test cases for clean_csv_data function."""

    def test_clean_csv_data_strip_whitespace(self) -> None:
        """Test cleaning CSV data by stripping whitespace."""
        data = [
            {"name": "  Alice  ", "age": " 25 ", "city": "NYC  "},
            {"name": "Bob ", "age": "30", "city": "  LA"},
        ]
        rules = {"strip_whitespace": True}

        result = clean_csv_data(data, rules)

        expected = [
            {"name": "Alice", "age": "25", "city": "NYC"},
            {"name": "Bob", "age": "30", "city": "LA"},
        ]
        assert result == expected

    def test_clean_csv_data_remove_empty(self) -> None:
        """Test cleaning CSV data by removing empty fields."""
        data = [
            {"name": "Alice", "age": "", "city": "NYC"},
            {"name": "", "age": "30", "city": "LA"},
        ]
        rules = {"remove_empty": True, "strip_whitespace": False}

        result = clean_csv_data(data, rules)

        expected = [
            {"name": "Alice", "city": "NYC"},
            {"age": "30", "city": "LA"},
        ]
        assert result == expected

    def test_clean_csv_data_handle_na_values(self) -> None:
        """Test cleaning CSV data by handling NA values."""
        data = [
            {"name": "Alice", "age": "N/A", "score": "95"},
            {"name": "Bob", "age": "30", "score": "NULL"},
        ]
        rules = {"na_values": ["N/A", "NULL"], "strip_whitespace": False}

        result = clean_csv_data(data, rules)

        expected = [
            {"name": "Alice", "age": "", "score": "95"},
            {"name": "Bob", "age": "30", "score": ""},
        ]
        assert result == expected

    def test_clean_csv_data_comprehensive_cleaning(self) -> None:
        """Test comprehensive CSV data cleaning."""
        data = [
            {"name": "  Alice  ", "age": "", "score": "N/A", "city": "NYC"},
            {"name": "Bob", "age": " null ", "score": "85", "city": ""},
        ]
        rules = {
            "strip_whitespace": True,
            "remove_empty": True,
            "na_values": ["N/A", "null"],
        }

        result = clean_csv_data(data, rules)

        expected = [
            {"name": "Alice", "city": "NYC"},
            {"name": "Bob", "score": "85"},
        ]
        assert result == expected

    def test_clean_csv_data_default_rules(self) -> None:
        """Test cleaning with default rules."""
        data = [
            {"name": "  Alice  ", "age": "N/A", "score": "null"},
            {"name": "Bob", "age": "30", "score": "85"},
        ]
        rules = {}  # Use all defaults

        result = clean_csv_data(data, rules)

        # Default rules: strip_whitespace=True, remove_empty=False, na_values includes N/A and null
        expected = [
            {"name": "Alice", "age": "", "score": ""},
            {"name": "Bob", "age": "30", "score": "85"},
        ]
        assert result == expected

    def test_clean_csv_data_custom_na_values(self) -> None:
        """Test cleaning with custom NA values."""
        data = [
            {"status": "MISSING", "value": "UNKNOWN", "score": "95"},
            {"status": "OK", "value": "42", "score": "MISSING"},
        ]
        rules = {
            "na_values": ["MISSING", "UNKNOWN"],
            "strip_whitespace": False,
        }

        result = clean_csv_data(data, rules)

        expected = [
            {"status": "", "value": "", "score": "95"},
            {"status": "OK", "value": "42", "score": ""},
        ]
        assert result == expected

    def test_clean_csv_data_mixed_types(self) -> None:
        """Test cleaning data with mixed value types."""
        data = [
            {"name": "Alice", "age": 25, "score": None, "active": True},
            {"name": "  Bob  ", "age": "N/A", "score": 95.5, "active": False},
        ]
        rules = {"strip_whitespace": True, "na_values": ["N/A"]}

        result = clean_csv_data(data, rules)

        expected = [
            {"name": "Alice", "age": "25", "score": "", "active": "True"},
            {"name": "Bob", "age": "", "score": "95.5", "active": "False"},
        ]
        assert result == expected

    def test_clean_csv_data_empty_data(self) -> None:
        """Test cleaning empty data."""
        result = clean_csv_data([], {"strip_whitespace": True})
        assert result == []

    def test_clean_csv_data_non_dict_items(self) -> None:
        """Test cleaning data with non-dictionary items."""
        data = [
            {"name": "Alice", "age": "25"},
            "not a dict",  # type: ignore[list-item]
            {"name": "Bob", "age": "30"},
        ]
        rules = {"strip_whitespace": True}

        result = clean_csv_data(data, rules)

        # Non-dict items should be skipped
        expected = [
            {"name": "Alice", "age": "25"},
            {"name": "Bob", "age": "30"},
        ]
        assert result == expected

    def test_clean_csv_data_invalid_data_type(self) -> None:
        """Test error handling for invalid data type."""
        with pytest.raises(TypeError, match="data must be a list"):
            clean_csv_data({"not": "list"}, {})  # type: ignore[arg-type]

    def test_clean_csv_data_invalid_rules_type(self) -> None:
        """Test error handling for invalid rules type."""
        data = [{"name": "Alice"}]

        with pytest.raises(TypeError, match="rules must be a dictionary"):
            clean_csv_data(data, "not dict")  # type: ignore[arg-type]

    def test_clean_csv_data_merge_rules(self) -> None:
        """Test that provided rules merge with defaults correctly."""
        data = [{"name": "  Alice  ", "age": "N/A"}]
        rules = {"remove_empty": True}  # Only specify one rule

        result = clean_csv_data(data, rules)

        # Should still apply default strip_whitespace and na_values
        expected = [{"name": "Alice"}]  # N/A converted to empty, then removed
        assert result == expected


# Integration tests
class TestCsvToolsIntegration:
    """Integration tests for CSV tools working together."""

    def test_complete_csv_workflow(self, tmp_path: Path) -> None:
        """Test complete CSV processing workflow."""
        # Step 1: Create test data
        original_data = [
            {"name": "Alice", "age": "25", "city": "NYC"},
            {"name": "Bob", "age": "30", "city": "LA"},
        ]

        # Step 2: Write to file
        csv_file = tmp_path / "workflow.csv"
        write_csv_simple(original_data, str(csv_file), ",", True, skip_confirm=True)

        # Step 3: Detect delimiter
        detected_delimiter = detect_csv_delimiter(str(csv_file), 1000)
        assert detected_delimiter == ","

        # Step 4: Validate structure
        is_valid = validate_csv_structure(str(csv_file), ["name", "age"])
        assert is_valid is True

        # Step 5: Read back
        read_data = read_csv_simple(str(csv_file), detected_delimiter, True)
        assert read_data == original_data

        # Step 6: Convert to string and back
        csv_string = dict_list_to_csv(read_data, detected_delimiter)
        dict_data = csv_to_dict_list(csv_string, detected_delimiter)
        assert dict_data == original_data

    def test_csv_cleaning_workflow(self) -> None:
        """Test CSV data cleaning workflow."""
        # Step 1: Create messy data
        messy_data = [
            {"name": "  Alice  ", "age": "", "score": "N/A"},
            {"name": "Bob", "age": " 30 ", "score": "95"},
            {"name": "", "age": "25", "score": "null"},
        ]

        # Step 2: Clean the data
        clean_rules = {
            "strip_whitespace": True,
            "remove_empty": True,
            "na_values": ["N/A", "null"],
        }
        cleaned_data = clean_csv_data(messy_data, clean_rules)

        # Step 3: Verify cleaning results
        expected = [
            {"name": "Alice"},
            {"name": "Bob", "age": "30", "score": "95"},
            {"age": "25"},
        ]
        assert cleaned_data == expected

        # Step 4: Convert cleaned data to CSV string
        csv_string = dict_list_to_csv(cleaned_data, ",")
        assert "Alice" in csv_string
        assert "Bob,30,95" in csv_string or "30,Bob,95" in csv_string

    def test_error_consistency_across_functions(self, tmp_path: Path) -> None:
        """Test that functions handle unusual but valid CSV consistently."""
        # Create unusual but valid CSV file
        csv_file = tmp_path / "unusual.csv"
        csv_content = 'name,age\n"Alice,25\nBob,30'  # Python CSV reader handles this
        csv_file.write_text(csv_content, encoding="utf-8")

        # All functions should handle this consistently (not raise errors)
        data = read_csv_simple(str(csv_file), ",", True)
        assert len(data) == 1  # CSV reader treats this as one record

        result = validate_csv_structure(str(csv_file), ["name", "age"])
        assert result is True

    def test_unicode_consistency_across_functions(self, tmp_path: Path) -> None:
        """Test Unicode handling consistency across all functions."""
        unicode_data = [
            {"name": "Alice", "city": "北京"},
            {"name": "José", "city": "São Paulo"},
            {"name": "Владимир", "city": "Москва"},
        ]

        # Step 1: Write Unicode data
        csv_file = tmp_path / "unicode.csv"
        write_csv_simple(unicode_data, str(csv_file), ",", True, skip_confirm=True)

        # Step 2: Read back
        read_data = read_csv_simple(str(csv_file), ",", True)
        assert read_data == unicode_data

        # Step 3: Convert to string and back
        csv_string = dict_list_to_csv(unicode_data, ",")
        dict_data = csv_to_dict_list(csv_string, ",")
        assert dict_data == unicode_data

        # Step 4: Detect delimiter (should work with Unicode)
        delimiter = detect_csv_delimiter(str(csv_file), 1000)
        assert delimiter == ","
