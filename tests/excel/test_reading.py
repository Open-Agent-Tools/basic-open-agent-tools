"""Tests for Excel reading functions."""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

from basic_open_agent_tools.excel import reading


class TestReadExcelSheet:
    """Tests for read_excel_sheet function."""

    def test_read_excel_sheet_returns_2d_list(self, tmp_path):
        """Test reading Excel sheet returns 2D list of strings."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            with patch.object(reading, "load_workbook") as mock_wb:
                # Setup mock
                mock_sheet = MagicMock()
                mock_sheet.iter_rows.return_value = [
                    ("Name", "Age"),
                    ("Alice", 30),
                    ("Bob", None),
                ]
                mock_wb.return_value.sheetnames = ["Sheet1"]
                mock_wb.return_value.__getitem__.return_value = mock_sheet
                mock_wb.return_value.close = Mock()

                # Create temp file
                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"fake excel content")

                # Call function
                result = reading.read_excel_sheet(str(test_file), "Sheet1")

                # Verify
                assert isinstance(result, list)
                assert len(result) == 3
                assert result[0] == ["Name", "Age"]
                assert result[1] == ["Alice", "30"]
                assert result[2] == ["Bob", ""]

    def test_read_excel_sheet_missing_openpyxl(self, tmp_path):
        """Test error when openpyxl not installed."""
        with patch.object(reading, "HAS_OPENPYXL", False):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(ImportError, match="openpyxl is required"):
                reading.read_excel_sheet(str(test_file), "Sheet1")

    def test_read_excel_sheet_type_validation(self, tmp_path):
        """Test parameter type validation."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(TypeError, match="file_path must be a string"):
                reading.read_excel_sheet(123, "Sheet1")

            with pytest.raises(TypeError, match="sheet_name must be a string"):
                reading.read_excel_sheet(str(test_file), 456)

    def test_read_excel_sheet_file_not_found(self):
        """Test error when file doesn't exist."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            with pytest.raises(FileNotFoundError, match="Excel file not found"):
                reading.read_excel_sheet("/nonexistent/file.xlsx", "Sheet1")

    def test_read_excel_sheet_file_too_large(self, tmp_path):
        """Test error when file exceeds size limit."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"x")

            with patch("os.path.getsize", return_value=101 * 1024 * 1024):
                with pytest.raises(ValueError, match="File too large"):
                    reading.read_excel_sheet(str(test_file), "Sheet1")

    def test_read_excel_sheet_sheet_not_found(self, tmp_path):
        """Test error when sheet doesn't exist."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            with patch.object(reading, "load_workbook") as mock_wb:
                mock_wb.return_value.sheetnames = ["Sheet1", "Sheet2"]

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                with pytest.raises(ValueError, match="Sheet 'NonExistent' not found"):
                    reading.read_excel_sheet(str(test_file), "NonExistent")


class TestGetExcelSheetNames:
    """Tests for get_excel_sheet_names function."""

    def test_get_excel_sheet_names_returns_list(self, tmp_path):
        """Test getting sheet names returns list."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            with patch.object(reading, "load_workbook") as mock_wb:
                mock_wb.return_value.sheetnames = ["Sheet1", "Sheet2", "Data"]
                mock_wb.return_value.close = Mock()

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = reading.get_excel_sheet_names(str(test_file))

                assert isinstance(result, list)
                assert result == ["Sheet1", "Sheet2", "Data"]

    def test_get_excel_sheet_names_missing_openpyxl(self, tmp_path):
        """Test error when openpyxl not installed."""
        with patch.object(reading, "HAS_OPENPYXL", False):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(ImportError, match="openpyxl is required"):
                reading.get_excel_sheet_names(str(test_file))


class TestReadExcelAsDicts:
    """Tests for read_excel_as_dicts function."""

    def test_read_excel_as_dicts_returns_list_of_dicts(self, tmp_path):
        """Test reading Excel as dictionaries."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            with patch.object(reading, "read_excel_sheet") as mock_read:
                mock_read.return_value = [
                    ["Name", "Age", "City"],
                    ["Alice", "30", "NYC"],
                    ["Bob", "25", "LA"],
                ]

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = reading.read_excel_as_dicts(str(test_file), "Sheet1", 1)

                assert isinstance(result, list)
                assert len(result) == 2
                assert result[0] == {"Name": "Alice", "Age": "30", "City": "NYC"}
                assert result[1] == {"Name": "Bob", "Age": "25", "City": "LA"}

    def test_read_excel_as_dicts_type_validation(self, tmp_path):
        """Test parameter type validation."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(TypeError, match="header_row must be an integer"):
                reading.read_excel_as_dicts(str(test_file), "Sheet1", "1")

    def test_read_excel_as_dicts_invalid_header_row(self, tmp_path):
        """Test error with invalid header row."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(ValueError, match="header_row must be >= 1"):
                reading.read_excel_as_dicts(str(test_file), "Sheet1", 0)


class TestGetExcelCellValue:
    """Tests for get_excel_cell_value function."""

    def test_get_excel_cell_value_returns_string(self, tmp_path):
        """Test getting cell value returns string."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            with patch.object(reading, "load_workbook") as mock_wb:
                mock_sheet = MagicMock()
                mock_cell = MagicMock()
                mock_cell.value = 42
                mock_sheet.__getitem__.return_value = mock_cell
                mock_wb.return_value.sheetnames = ["Sheet1"]
                mock_wb.return_value.__getitem__.return_value = mock_sheet
                mock_wb.return_value.close = Mock()

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = reading.get_excel_cell_value(str(test_file), "Sheet1", "B5")

                assert result == "42"

    def test_get_excel_cell_value_none_returns_empty(self, tmp_path):
        """Test None value returns empty string."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            with patch.object(reading, "load_workbook") as mock_wb:
                mock_sheet = MagicMock()
                mock_cell = MagicMock()
                mock_cell.value = None
                mock_sheet.__getitem__.return_value = mock_cell
                mock_wb.return_value.sheetnames = ["Sheet1"]
                mock_wb.return_value.__getitem__.return_value = mock_sheet
                mock_wb.return_value.close = Mock()

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = reading.get_excel_cell_value(str(test_file), "Sheet1", "A1")

                assert result == ""


class TestGetExcelCellRange:
    """Tests for get_excel_cell_range function."""

    def test_get_excel_cell_range_returns_2d_list(self, tmp_path):
        """Test getting cell range returns 2D list."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            with patch.object(reading, "load_workbook") as mock_wb:
                # Create mock cells
                mock_cell1 = Mock()
                mock_cell1.value = "Name"
                mock_cell2 = Mock()
                mock_cell2.value = "Age"
                mock_cell3 = Mock()
                mock_cell3.value = "Alice"
                mock_cell4 = Mock()
                mock_cell4.value = 30

                mock_sheet = MagicMock()
                mock_sheet.__getitem__.return_value = [
                    (mock_cell1, mock_cell2),
                    (mock_cell3, mock_cell4),
                ]
                mock_wb.return_value.sheetnames = ["Sheet1"]
                mock_wb.return_value.__getitem__.return_value = mock_sheet
                mock_wb.return_value.close = Mock()

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = reading.get_excel_cell_range(
                    str(test_file), "Sheet1", "A1", "B2"
                )

                assert isinstance(result, list)
                assert len(result) == 2
                assert result[0] == ["Name", "Age"]
                assert result[1] == ["Alice", "30"]


class TestSearchExcelText:
    """Tests for search_excel_text function."""

    def test_search_excel_text_case_sensitive(self, tmp_path):
        """Test text search with case sensitivity."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            with patch.object(reading, "load_workbook") as mock_wb:
                mock_cell1 = Mock()
                mock_cell1.value = "Python Developer"
                mock_cell1.coordinate = "B5"
                mock_cell2 = Mock()
                mock_cell2.value = "python beginner"
                mock_cell2.coordinate = "C10"

                mock_sheet = MagicMock()
                mock_sheet.iter_rows.return_value = [
                    (mock_cell1,),
                    (mock_cell2,),
                ]
                mock_wb.return_value.sheetnames = ["Sheet1"]
                mock_wb.return_value.__getitem__.return_value = mock_sheet
                mock_wb.return_value.close = Mock()

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = reading.search_excel_text(str(test_file), "Python", True)

                assert isinstance(result, list)
                assert len(result) == 1
                assert result[0]["value"] == "Python Developer"
                assert result[0]["cell_reference"] == "B5"

    def test_search_excel_text_case_insensitive(self, tmp_path):
        """Test text search without case sensitivity."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            with patch.object(reading, "load_workbook") as mock_wb:
                mock_cell1 = Mock()
                mock_cell1.value = "Python Developer"
                mock_cell1.coordinate = "B5"
                mock_cell2 = Mock()
                mock_cell2.value = "python beginner"
                mock_cell2.coordinate = "C10"

                mock_sheet = MagicMock()
                mock_sheet.iter_rows.return_value = [
                    (mock_cell1,),
                    (mock_cell2,),
                ]
                mock_wb.return_value.sheetnames = ["Sheet1"]
                mock_wb.return_value.__getitem__.return_value = mock_sheet
                mock_wb.return_value.close = Mock()

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = reading.search_excel_text(str(test_file), "python", False)

                assert len(result) == 2


class TestGetExcelMetadata:
    """Tests for get_excel_metadata function."""

    def test_get_excel_metadata_returns_dict(self, tmp_path):
        """Test getting metadata returns dictionary."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            with patch.object(reading, "load_workbook") as mock_wb:
                mock_props = Mock()
                mock_props.creator = "John Doe"
                mock_props.title = "Test Workbook"
                mock_props.subject = "Testing"
                mock_props.description = "Test Description"
                mock_props.keywords = "test, excel"
                mock_props.category = "Test Category"
                mock_props.lastModifiedBy = "Jane Doe"
                mock_props.created = "2024-01-01"
                mock_props.modified = "2024-01-02"

                mock_wb.return_value.properties = mock_props
                mock_wb.return_value.close = Mock()

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = reading.get_excel_metadata(str(test_file))

                assert isinstance(result, dict)
                assert result["creator"] == "John Doe"
                assert result["title"] == "Test Workbook"


class TestGetExcelInfo:
    """Tests for get_excel_info function."""

    def test_get_excel_info_returns_dict(self, tmp_path):
        """Test getting workbook info returns dictionary."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            with patch.object(reading, "load_workbook") as mock_wb:
                mock_sheet1 = MagicMock()
                mock_sheet1.max_row = 100
                mock_sheet1.max_column = 5

                mock_sheet2 = MagicMock()
                mock_sheet2.max_row = 50
                mock_sheet2.max_column = 3

                mock_wb.return_value.sheetnames = ["Sheet1", "Sheet2"]
                mock_wb.return_value.__getitem__.side_effect = [
                    mock_sheet1,
                    mock_sheet2,
                ]
                mock_wb.return_value.close = Mock()

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = reading.get_excel_info(str(test_file))

                assert isinstance(result, dict)
                assert result["sheet_count"] == 2
                assert "Sheet1" in result["sheet_names"]
                assert len(result["sheets"]) == 2


class TestGetSheetInfo:
    """Tests for get_sheet_info function."""

    def test_get_sheet_info_returns_dict(self, tmp_path):
        """Test getting sheet info returns dictionary."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            with patch.object(reading, "load_workbook") as mock_wb:
                mock_sheet = MagicMock()
                mock_sheet.max_row = 1000
                mock_sheet.max_column = 10

                mock_wb.return_value.sheetnames = ["Sheet1"]
                mock_wb.return_value.__getitem__.return_value = mock_sheet
                mock_wb.return_value.close = Mock()

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = reading.get_sheet_info(str(test_file), "Sheet1")

                assert isinstance(result, dict)
                assert result["row_count"] == "1000"
                assert result["column_count"] == "10"


class TestGetSheetSchema:
    """Tests for get_sheet_schema function."""

    def test_get_sheet_schema_infers_types(self, tmp_path):
        """Test schema inference for columns."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            with patch.object(reading, "load_workbook") as mock_wb:
                mock_sheet = MagicMock()
                mock_sheet.iter_rows.side_effect = [
                    [("Name", "Age", "Active")],  # First call for headers
                    [("Alice", 30, True), ("Bob", 25, False)],  # Second call for data
                ]

                mock_wb.return_value.sheetnames = ["Sheet1"]
                mock_wb.return_value.__getitem__.return_value = mock_sheet
                mock_wb.return_value.close = Mock()

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = reading.get_sheet_schema(str(test_file), "Sheet1", 100)

                assert isinstance(result, dict)
                assert result["Name"] == "string"
                assert result["Age"] == "integer"
                assert result["Active"] == "boolean"


class TestPreviewSheetRows:
    """Tests for preview_sheet_rows function."""

    def test_preview_sheet_rows_returns_list_of_dicts(self, tmp_path):
        """Test previewing rows returns list of dictionaries."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            with patch.object(reading, "load_workbook") as mock_wb:
                mock_sheet = MagicMock()
                mock_sheet.iter_rows.side_effect = [
                    [("Name", "Age")],
                    [("Alice", 30), ("Bob", 25)],
                ]

                mock_wb.return_value.sheetnames = ["Sheet1"]
                mock_wb.return_value.__getitem__.return_value = mock_sheet
                mock_wb.return_value.close = Mock()

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = reading.preview_sheet_rows(str(test_file), "Sheet1", 5)

                assert isinstance(result, list)
                assert len(result) == 2


class TestSelectSheetColumns:
    """Tests for select_sheet_columns function."""

    def test_select_sheet_columns_returns_subset(self, tmp_path):
        """Test selecting specific columns."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            with patch.object(reading, "load_workbook") as mock_wb:
                mock_sheet = MagicMock()
                mock_sheet.iter_rows.side_effect = [
                    [("Name", "Age", "City")],
                    [("Alice", 30, "NYC"), ("Bob", 25, "LA")],
                ]

                mock_wb.return_value.sheetnames = ["Sheet1"]
                mock_wb.return_value.__getitem__.return_value = mock_sheet
                mock_wb.return_value.close = Mock()

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = reading.select_sheet_columns(
                    str(test_file), "Sheet1", ["Name", "City"]
                )

                assert isinstance(result, list)
                assert len(result) == 2
                assert result[0] == {"Name": "Alice", "City": "NYC"}
                assert "Age" not in result[0]


class TestFilterSheetRows:
    """Tests for filter_sheet_rows function."""

    def test_filter_sheet_rows_equals_operator(self, tmp_path):
        """Test filtering rows with equals operator."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            with patch.object(reading, "_validate_excel_file"):
                with patch.object(reading, "_load_excel_sheet") as mock_load:
                    mock_wb = MagicMock()
                    mock_sheet = MagicMock()
                    mock_sheet.iter_rows.return_value = [
                        ("Alice", "30", "NYC"),
                        ("Bob", "30", "LA"),
                        ("Charlie", "25", "SF"),
                    ]

                    mock_load.return_value = (mock_wb, mock_sheet)

                    with patch.object(reading, "_get_sheet_headers") as mock_headers:
                        mock_headers.return_value = ["Name", "Age", "City"]

                        with patch.object(reading, "_row_to_dict") as mock_to_dict:
                            mock_to_dict.side_effect = [
                                {"Name": "Alice", "Age": "30", "City": "NYC"},
                                {"Name": "Bob", "Age": "30", "City": "LA"},
                            ]

                            result = reading.filter_sheet_rows(
                                "/tmp/test.xlsx", "Sheet1", "Age", "30", "equals"
                            )

                            assert len(result) == 2


class TestGetSheetRowRange:
    """Tests for get_sheet_row_range function."""

    def test_get_sheet_row_range_returns_range(self, tmp_path):
        """Test getting specific row range."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            with patch.object(reading, "load_workbook") as mock_wb:
                mock_sheet = MagicMock()
                mock_sheet.iter_rows.side_effect = [
                    [("Name", "Age")],
                    [
                        ("Alice", 30),
                        ("Bob", 25),
                        ("Charlie", 35),
                        ("Dana", 28),
                    ],
                ]

                mock_wb.return_value.sheetnames = ["Sheet1"]
                mock_wb.return_value.__getitem__.return_value = mock_sheet
                mock_wb.return_value.close = Mock()

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = reading.get_sheet_row_range(str(test_file), "Sheet1", 2, 3)

                assert isinstance(result, list)
                assert len(result) == 2  # Rows 2 and 3


class TestSampleSheetRows:
    """Tests for sample_sheet_rows function."""

    def test_sample_sheet_rows_first_method(self, tmp_path):
        """Test sampling first N rows."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            with patch.object(reading, "preview_sheet_rows") as mock_preview:
                mock_preview.return_value = [
                    {"Name": "Alice", "Age": "30"},
                    {"Name": "Bob", "Age": "25"},
                ]

                result = reading.sample_sheet_rows(
                    "/tmp/test.xlsx", "Sheet1", 2, "first"
                )

                assert len(result) == 2


class TestGetSheetColumnStats:
    """Tests for get_sheet_column_stats function."""

    def test_get_sheet_column_stats_returns_dict(self, tmp_path):
        """Test getting column statistics."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            with patch.object(reading, "load_workbook") as mock_wb:
                mock_sheet = MagicMock()
                mock_sheet.max_row = 1000
                mock_sheet.iter_rows.side_effect = [
                    [("Name", "Age", "City")],
                    [
                        ("Alice", 30, "NYC"),
                        ("Bob", 25, "LA"),
                        ("Charlie", 30, "NYC"),
                    ],
                ]

                mock_wb.return_value.sheetnames = ["Sheet1"]
                mock_wb.return_value.__getitem__.return_value = mock_sheet
                mock_wb.return_value.close = Mock()

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = reading.get_sheet_column_stats(
                    str(test_file), "Sheet1", "Age", 100
                )

                assert isinstance(result, dict)
                assert "total_rows" in result
                assert "unique_count" in result


class TestCountSheetRows:
    """Tests for count_sheet_rows function."""

    def test_count_sheet_rows_no_filter(self, tmp_path):
        """Test counting all rows."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            with patch.object(reading, "load_workbook") as mock_wb:
                mock_sheet = MagicMock()
                mock_sheet.max_row = 1001  # Including header

                mock_wb.return_value.sheetnames = ["Sheet1"]
                mock_wb.return_value.__getitem__.return_value = mock_sheet
                mock_wb.return_value.close = Mock()

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = reading.count_sheet_rows(str(test_file), "Sheet1", "", "")

                assert result == 1000  # Excluding header


class TestGetSheetValueCounts:
    """Tests for get_sheet_value_counts function."""

    def test_get_sheet_value_counts_returns_dict(self, tmp_path):
        """Test getting value frequency counts."""
        with patch.object(reading, "HAS_OPENPYXL", True):
            with patch.object(reading, "load_workbook") as mock_wb:
                mock_sheet = MagicMock()
                mock_sheet.iter_rows.side_effect = [
                    [("Name", "City")],
                    [
                        ("Alice", "NYC"),
                        ("Bob", "LA"),
                        ("Charlie", "NYC"),
                        ("Dana", "NYC"),
                        ("Eve", "SF"),
                    ],
                ]

                mock_wb.return_value.sheetnames = ["Sheet1"]
                mock_wb.return_value.__getitem__.return_value = mock_sheet
                mock_wb.return_value.close = Mock()

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = reading.get_sheet_value_counts(
                    str(test_file), "Sheet1", "City", 5
                )

                assert isinstance(result, dict)
                assert result["NYC"] == "3"
