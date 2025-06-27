"""Tests for CSV processing tools.

This module provides comprehensive tests for the CSV data processing toolkit functions,
including unit tests, integration tests, and Google AI compatibility verification.
"""

import inspect
import tempfile
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


class TestCsvFileOperations:
    """Test cases for CSV file read/write operations."""

    @pytest.fixture
    def temp_csv_files(self):
        """Create temporary CSV test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create various test CSV files
            files = {}

            # Simple CSV with headers
            simple_csv = temp_path / "simple.csv"
            simple_csv.write_text(
                "name,age,city\nAlice,25,NYC\nBob,30,LA\nCharlie,35,Chicago"
            )
            files["simple"] = str(simple_csv)

            # CSV without headers
            no_headers_csv = temp_path / "no_headers.csv"
            no_headers_csv.write_text("Alice,25,NYC\nBob,30,LA")
            files["no_headers"] = str(no_headers_csv)

            # CSV with semicolon delimiter
            semicolon_csv = temp_path / "semicolon.csv"
            semicolon_csv.write_text("name;age;city\nAlice;25;NYC\nBob;30;LA")
            files["semicolon"] = str(semicolon_csv)

            # CSV with tab delimiter
            tab_csv = temp_path / "tab.csv"
            tab_csv.write_text("name\tage\tcity\nAlice\t25\tNYC\nBob\t30\tLA")
            files["tab"] = str(tab_csv)

            # Empty CSV
            empty_csv = temp_path / "empty.csv"
            empty_csv.write_text("")
            files["empty"] = str(empty_csv)

            # Headers only CSV
            headers_only_csv = temp_path / "headers_only.csv"
            headers_only_csv.write_text("name,age,city")
            files["headers_only"] = str(headers_only_csv)

            # CSV with mixed fields
            mixed_csv = temp_path / "mixed.csv"
            mixed_csv.write_text("name,age\nAlice,25\nBob,30,extra")
            files["mixed"] = str(mixed_csv)

            yield files

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for output files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_read_csv_basic_functionality(self, temp_csv_files):
        """Test basic CSV reading functionality."""
        # Test reading simple CSV with headers
        result = read_csv_simple(temp_csv_files["simple"], ",", True)
        expected = [
            {"name": "Alice", "age": "25", "city": "NYC"},
            {"name": "Bob", "age": "30", "city": "LA"},
            {"name": "Charlie", "age": "35", "city": "Chicago"},
        ]
        assert result == expected

    def test_read_csv_without_headers(self, temp_csv_files):
        """Test reading CSV without headers."""
        result = read_csv_simple(temp_csv_files["no_headers"], ",", False)
        expected = [
            {"col_0": "Alice", "col_1": "25", "col_2": "NYC"},
            {"col_0": "Bob", "col_1": "30", "col_2": "LA"},
        ]
        assert result == expected

    def test_read_csv_custom_delimiters(self, temp_csv_files):
        """Test reading CSV with different delimiters."""
        # Test semicolon delimiter
        result = read_csv_simple(temp_csv_files["semicolon"], ";", True)
        expected = [
            {"name": "Alice", "age": "25", "city": "NYC"},
            {"name": "Bob", "age": "30", "city": "LA"},
        ]
        assert result == expected

        # Test tab delimiter
        result = read_csv_simple(temp_csv_files["tab"], "\t", True)
        expected = [
            {"name": "Alice", "age": "25", "city": "NYC"},
            {"name": "Bob", "age": "30", "city": "LA"},
        ]
        assert result == expected

    def test_read_csv_edge_cases(self, temp_csv_files):
        """Test reading CSV edge cases."""
        # Empty file
        result = read_csv_simple(temp_csv_files["empty"], ",", True)
        assert result == []

        # Headers only
        result = read_csv_simple(temp_csv_files["headers_only"], ",", True)
        assert result == []

    def test_read_csv_error_handling(self, temp_output_dir):
        """Test CSV reading error handling."""
        # Non-existent file
        nonexistent = str(temp_output_dir / "nonexistent.csv")
        with pytest.raises(DataError, match="CSV file not found"):
            read_csv_simple(nonexistent, ",", True)

    def test_write_csv_basic_functionality(self, temp_output_dir):
        """Test basic CSV writing functionality."""
        data = [
            {"name": "Alice", "age": "25", "city": "NYC"},
            {"name": "Bob", "age": "30", "city": "LA"},
        ]
        output_file = str(temp_output_dir / "output.csv")

        write_csv_simple(data, output_file, ",", True)

        # Verify content
        content = Path(output_file).read_text()
        assert "name,age,city" in content
        assert "Alice,25,NYC" in content
        assert "Bob,30,LA" in content

    def test_write_csv_without_headers(self, temp_output_dir):
        """Test writing CSV without headers."""
        data = [{"name": "Alice", "age": "25"}]
        output_file = str(temp_output_dir / "no_headers.csv")

        write_csv_simple(data, output_file, ",", False)

        content = Path(output_file).read_text()
        assert "name,age" not in content
        assert "Alice,25" in content

    def test_write_csv_custom_delimiters(self, temp_output_dir):
        """Test writing CSV with custom delimiters."""
        data = [{"name": "Alice", "age": "25"}]

        # Test semicolon delimiter
        output_file = str(temp_output_dir / "semicolon.csv")
        write_csv_simple(data, output_file, ";", True)

        content = Path(output_file).read_text()
        assert "name;age" in content
        assert "Alice;25" in content

    def test_write_csv_mixed_fields(self, temp_output_dir):
        """Test writing CSV with mixed fields across rows."""
        data = [
            {"name": "Alice", "age": "25"},
            {"name": "Bob", "city": "NYC"},
            {"age": "30", "country": "USA"},
        ]
        output_file = str(temp_output_dir / "mixed.csv")

        write_csv_simple(data, output_file, ",", True)

        content = Path(output_file).read_text()
        # Should include all unique fields
        assert "name" in content
        assert "age" in content
        assert "city" in content
        assert "country" in content

    def test_write_csv_empty_data(self, temp_output_dir):
        """Test writing empty data."""
        output_file = str(temp_output_dir / "empty.csv")
        write_csv_simple([], output_file, ",", True)

        assert Path(output_file).read_text() == ""


class TestCsvStringOperations:
    """Test cases for CSV string conversion operations."""

    def test_csv_to_dict_list_basic(self):
        """Test basic CSV string to dictionary list conversion."""
        csv_str = "name,age,city\nAlice,25,NYC\nBob,30,LA"
        result = csv_to_dict_list(csv_str, ",")
        expected = [
            {"name": "Alice", "age": "25", "city": "NYC"},
            {"name": "Bob", "age": "30", "city": "LA"},
        ]
        assert result == expected

    def test_csv_to_dict_list_custom_delimiter(self):
        """Test CSV string conversion with custom delimiter."""
        csv_str = "name;age\nAlice;25\nBob;30"
        result = csv_to_dict_list(csv_str, ";")
        expected = [{"name": "Alice", "age": "25"}, {"name": "Bob", "age": "30"}]
        assert result == expected

    def test_csv_to_dict_list_edge_cases(self):
        """Test CSV string conversion edge cases."""
        # Empty string
        assert csv_to_dict_list("", ",") == []

        # Headers only
        assert csv_to_dict_list("name,age", ",") == []

    def test_dict_list_to_csv_basic(self):
        """Test basic dictionary list to CSV string conversion."""
        data = [{"name": "Alice", "age": "25"}, {"name": "Bob", "age": "30"}]
        result = dict_list_to_csv(data, ",")

        assert "name,age" in result
        assert "Alice,25" in result
        assert "Bob,30" in result

    def test_dict_list_to_csv_custom_delimiter(self):
        """Test dictionary list to CSV with custom delimiter."""
        data = [{"name": "Alice", "age": "25"}]
        result = dict_list_to_csv(data, ";")

        assert "name;age" in result
        assert "Alice;25" in result

    def test_dict_list_to_csv_mixed_fields(self):
        """Test conversion with mixed fields across dictionaries."""
        data = [{"name": "Alice", "age": "25"}, {"name": "Bob", "city": "NYC"}]
        result = dict_list_to_csv(data, ",")

        lines = result.strip().split("\n")
        header = lines[0]
        assert "name" in header
        assert "age" in header
        assert "city" in header

    def test_dict_list_to_csv_empty_data(self):
        """Test converting empty data."""
        assert dict_list_to_csv([], ",") == ""


class TestCsvUtilities:
    """Test cases for CSV utility functions."""

    @pytest.fixture
    def temp_csv_files(self):
        """Create temporary CSV test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create various test CSV files
            files = {}

            # Simple CSV with headers
            simple_csv = temp_path / "simple.csv"
            simple_csv.write_text(
                "name,age,city\nAlice,25,NYC\nBob,30,LA\nCharlie,35,Chicago"
            )
            files["simple"] = str(simple_csv)

            # Empty CSV
            empty_csv = temp_path / "empty.csv"
            empty_csv.write_text("")
            files["empty"] = str(empty_csv)

            yield files

    @pytest.fixture
    def delimiter_test_files(self):
        """Create test files with different delimiters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            files = {}

            # Comma delimited
            comma_file = temp_path / "comma.csv"
            comma_file.write_text("name,age,city\nAlice,25,NYC\nBob,30,LA")
            files["comma"] = str(comma_file)

            # Semicolon delimited
            semicolon_file = temp_path / "semicolon.csv"
            semicolon_file.write_text("name;age;city\nAlice;25;NYC\nBob;30;LA")
            files["semicolon"] = str(semicolon_file)

            # Tab delimited
            tab_file = temp_path / "tab.csv"
            tab_file.write_text("name\tage\tcity\nAlice\t25\tNYC\nBob\t30\tLA")
            files["tab"] = str(tab_file)

            yield files

    def test_detect_csv_delimiter_basic(self, delimiter_test_files):
        """Test basic delimiter detection."""
        assert detect_csv_delimiter(delimiter_test_files["comma"], 1024) == ","
        assert detect_csv_delimiter(delimiter_test_files["semicolon"], 1024) == ";"
        assert detect_csv_delimiter(delimiter_test_files["tab"], 1024) == "\t"

    def test_detect_csv_delimiter_custom_sample_size(self, delimiter_test_files):
        """Test delimiter detection with custom sample size."""
        # Test with small sample size
        result = detect_csv_delimiter(delimiter_test_files["comma"], 50)
        assert result == ","

    def test_validate_csv_structure_valid(self, temp_csv_files):
        """Test CSV structure validation with valid files."""
        # Valid structure with expected columns
        result = validate_csv_structure(temp_csv_files["simple"], ["name", "age"])
        assert result is True

        # No expected columns specified
        result = validate_csv_structure(temp_csv_files["simple"], [])
        assert result is True

        # Empty file is considered valid
        result = validate_csv_structure(temp_csv_files["empty"], [])
        assert result is True

    def test_validate_csv_structure_invalid(self, temp_csv_files):
        """Test CSV structure validation with invalid files."""
        # Missing expected columns
        with pytest.raises(DataError, match="Missing expected columns"):
            validate_csv_structure(
                temp_csv_files["simple"], ["name", "age", "email", "phone"]
            )

    def test_clean_csv_data_basic(self):
        """Test basic CSV data cleaning."""
        data = [
            {"name": "  Alice  ", "age": "25", "score": ""},
            {"name": "Bob", "age": "N/A", "score": "95"},
        ]

        result = clean_csv_data(data, {})
        expected = [
            {"name": "Alice", "age": "25", "score": ""},
            {"name": "Bob", "age": "", "score": "95"},
        ]
        assert result == expected

    def test_clean_csv_data_custom_rules(self):
        """Test CSV cleaning with custom rules."""
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
            {"name": "Alice"},  # Empty values removed
            {"name": "Bob", "age": "30", "score": "95"},
        ]
        assert result == expected

    def test_clean_csv_data_no_strip(self):
        """Test cleaning without whitespace stripping."""
        data = [{"name": "  Alice  ", "age": "25"}]
        rules = {"strip_whitespace": False}

        result = clean_csv_data(data, rules)
        assert result[0]["name"] == "  Alice  "

    def test_clean_csv_data_skip_invalid(self):
        """Test cleaning skips non-dictionary items."""
        data = [
            {"name": "Alice", "age": "25"},
            "not a dict",
            {"name": "Bob", "age": "30"},
        ]

        result = clean_csv_data(data, {})
        assert len(result) == 2
        assert result[0]["name"] == "Alice"
        assert result[1]["name"] == "Bob"


class TestCsvCompatibility:
    """Test Google AI compatibility for CSV functions."""

    def test_function_signatures_compatibility(self):
        """Test that all CSV functions have Google AI compatible signatures."""
        functions_to_test = [
            read_csv_simple,
            write_csv_simple,
            csv_to_dict_list,
            dict_list_to_csv,
            detect_csv_delimiter,
            validate_csv_structure,
            clean_csv_data,
        ]

        for func in functions_to_test:
            sig = inspect.signature(func)

            # Check that no parameters have default values
            for param_name, param in sig.parameters.items():
                assert param.default == inspect.Parameter.empty, (
                    f"Function {func.__name__} parameter {param_name} has default value, "
                    "violating Google AI requirements"
                )

            # Check that return type is specified
            assert sig.return_annotation != inspect.Signature.empty, (
                f"Function {func.__name__} missing return type annotation"
            )

    def test_parameter_types_compatibility(self):
        """Test that parameter types are Google AI compatible."""
        # Test read_csv_simple
        sig = inspect.signature(read_csv_simple)
        params = sig.parameters

        assert params["file_path"].annotation is str
        assert params["delimiter"].annotation is str
        assert params["headers"].annotation is bool

        # Check return type is List[Dict[str, str]]
        return_annotation = sig.return_annotation
        assert hasattr(return_annotation, "__origin__")
        assert return_annotation.__origin__ is list

    def test_list_parameter_types(self):
        """Test that list parameters have proper typing."""
        # Test write_csv_simple - should have List[Dict[str, str]]
        sig = inspect.signature(write_csv_simple)
        data_param = sig.parameters["data"]

        # Should be a list type with Dict specification
        assert hasattr(data_param.annotation, "__origin__")
        assert data_param.annotation.__origin__ is list


class TestCsvIntegration:
    """Integration tests combining multiple CSV operations."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for output files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def integration_data(self):
        """Sample data for integration testing."""
        return [
            {
                "name": "Alice Johnson",
                "age": "25",
                "city": "New York",
                "salary": "75000",
            },
            {
                "name": "Bob Smith",
                "age": "30",
                "city": "Los Angeles",
                "salary": "85000",
            },
            {
                "name": "Charlie Brown",
                "age": "35",
                "city": "Chicago",
                "salary": "90000",
            },
            {"name": "Diana Prince", "age": "28", "city": "Seattle", "salary": "80000"},
        ]

    def test_complete_csv_workflow(self, integration_data, temp_output_dir):
        """Test complete CSV processing workflow."""
        # Step 1: Write data to CSV
        csv_file = str(temp_output_dir / "workflow.csv")
        write_csv_simple(integration_data, csv_file, ",", True)

        # Step 2: Read data back
        read_data = read_csv_simple(csv_file, ",", True)

        # Step 3: Validate structure
        result = validate_csv_structure(csv_file, ["name", "age", "city"])
        assert result is True

        # Step 4: Clean the data
        cleaned_data = clean_csv_data(read_data, {"strip_whitespace": True})

        # Step 5: Convert to CSV string and back
        csv_string = dict_list_to_csv(cleaned_data, ",")
        final_data = csv_to_dict_list(csv_string, ",")

        # Verify round-trip integrity
        assert len(final_data) == len(integration_data)
        assert final_data[0]["name"] == "Alice Johnson"
        assert final_data[0]["age"] == "25"

    def test_delimiter_detection_workflow(self, temp_output_dir):
        """Test workflow with automatic delimiter detection."""
        # Create files with different delimiters
        data = [{"name": "Alice", "age": "25"}, {"name": "Bob", "age": "30"}]

        # Test comma-separated
        comma_file = str(temp_output_dir / "comma.csv")
        write_csv_simple(data, comma_file, ",", True)
        detected_delimiter = detect_csv_delimiter(comma_file, 1024)
        assert detected_delimiter == ","

        # Read with detected delimiter
        read_data = read_csv_simple(comma_file, detected_delimiter, True)
        assert len(read_data) == 2
        assert read_data[0]["name"] == "Alice"

    def test_data_cleaning_pipeline(self, temp_output_dir):
        """Test data cleaning pipeline."""
        # Create messy data
        messy_data = [
            {"name": "  Alice  ", "age": "25", "score": "N/A", "status": ""},
            {"name": "Bob", "age": "null", "score": "95", "status": "active"},
            {"name": "  Charlie  ", "age": "35", "score": "", "status": "inactive"},
        ]

        # Write to file
        csv_file = str(temp_output_dir / "messy.csv")
        write_csv_simple(messy_data, csv_file, ",", True)

        # Read and clean
        read_data = read_csv_simple(csv_file, ",", True)

        # Apply comprehensive cleaning
        cleaning_rules = {
            "strip_whitespace": True,
            "remove_empty": True,
            "na_values": ["N/A", "null", ""],
        }

        cleaned_data = clean_csv_data(read_data, cleaning_rules)

        # Verify cleaning results
        assert len(cleaned_data) == 3
        assert cleaned_data[0]["name"] == "Alice"
        assert "score" not in cleaned_data[0]  # N/A values removed
        assert "age" not in cleaned_data[1]  # null converted to empty and then removed
        assert cleaned_data[2]["name"] == "Charlie"


class TestCsvErrorHandling:
    """Test error handling and edge cases for CSV functions."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for output files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_type_validation_errors(self):
        """Test type validation for all functions."""
        # read_csv_simple
        with pytest.raises(TypeError, match="file_path must be a string"):
            read_csv_simple(123, ",", True)

        with pytest.raises(TypeError, match="delimiter must be a string"):
            read_csv_simple("test.csv", 123, True)

        with pytest.raises(TypeError, match="headers must be a boolean"):
            read_csv_simple("test.csv", ",", "yes")

        # write_csv_simple
        with pytest.raises(TypeError, match="data must be a list"):
            write_csv_simple("not a list", "test.csv", ",", True)

        # csv_to_dict_list
        with pytest.raises(TypeError, match="csv_data must be a string"):
            csv_to_dict_list(123, ",")

        # dict_list_to_csv
        with pytest.raises(TypeError, match="data must be a list"):
            dict_list_to_csv("not a list", ",")

        # detect_csv_delimiter
        with pytest.raises(TypeError, match="file_path must be a string"):
            detect_csv_delimiter(123, 1024)

        with pytest.raises(TypeError, match="sample_size must be a positive integer"):
            detect_csv_delimiter("test.csv", 0)

        # validate_csv_structure
        with pytest.raises(TypeError, match="file_path must be a string"):
            validate_csv_structure(123, [])

        with pytest.raises(TypeError, match="expected_columns must be a list"):
            validate_csv_structure("test.csv", "not a list")

        # clean_csv_data
        with pytest.raises(TypeError, match="data must be a list"):
            clean_csv_data("not a list", {})

        with pytest.raises(TypeError, match="rules must be a dictionary"):
            clean_csv_data([], "not a dict")

    def test_file_operation_errors(self, temp_output_dir):
        """Test file operation error handling."""
        # Non-existent file
        nonexistent = str(temp_output_dir / "nonexistent.csv")

        with pytest.raises(DataError, match="CSV file not found"):
            read_csv_simple(nonexistent, ",", True)

        with pytest.raises(DataError, match="CSV file not found"):
            detect_csv_delimiter(nonexistent, 1024)

        # Empty file delimiter detection
        empty_file = temp_output_dir / "empty.csv"
        empty_file.write_text("")

        with pytest.raises(DataError, match="File is empty, cannot detect delimiter"):
            detect_csv_delimiter(str(empty_file), 1024)


class TestCsvRoundTrip:
    """Test round-trip operations to ensure data integrity."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for output files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_write_read_roundtrip(self, temp_output_dir):
        """Test that write -> read preserves data integrity."""
        original_data = [
            {"name": "Alice", "age": "25", "city": "NYC"},
            {"name": "Bob", "age": "30", "city": "LA"},
            {"name": "Charlie", "age": "35", "city": "Chicago"},
        ]

        csv_file = str(temp_output_dir / "roundtrip.csv")
        write_csv_simple(original_data, csv_file, ",", True)
        read_data = read_csv_simple(csv_file, ",", True)

        assert read_data == original_data

    def test_dict_to_csv_to_dict_roundtrip(self):
        """Test that dict_list -> CSV string -> dict_list preserves data."""
        original_data = [{"name": "Alice", "age": "25"}, {"name": "Bob", "age": "30"}]

        csv_string = dict_list_to_csv(original_data, ",")
        converted_back = csv_to_dict_list(csv_string, ",")

        assert converted_back == original_data

    def test_delimiter_preservation_roundtrip(self, temp_output_dir):
        """Test that custom delimiters are preserved in round-trip operations."""
        data = [{"name": "Alice", "age": "25"}]

        for delimiter in [",", ";", "\t"]:
            csv_file = str(temp_output_dir / f"delimiter_{ord(delimiter)}.csv")

            # Write with custom delimiter
            write_csv_simple(data, csv_file, delimiter, True)

            # Detect delimiter
            detected = detect_csv_delimiter(csv_file, 1024)
            assert detected == delimiter

            # Read with detected delimiter
            read_data = read_csv_simple(csv_file, detected, True)
            assert read_data == data
