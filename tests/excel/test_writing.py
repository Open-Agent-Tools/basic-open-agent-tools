"""Tests for Excel writing functions."""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

from basic_open_agent_tools.excel import writing


class TestCreateSimpleExcel:
    """Tests for create_simple_excel function."""

    def test_create_simple_excel_success(self, tmp_path):
        """Test creating simple Excel file."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            with patch.object(writing, "Workbook") as mock_wb_class:
                mock_wb = MagicMock()
                mock_ws = MagicMock()
                mock_wb.active = mock_ws
                mock_wb.save = Mock()
                mock_wb.close = Mock()
                mock_wb_class.return_value = mock_wb

                test_file = tmp_path / "test.xlsx"
                data = [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]]

                result = writing.create_simple_excel(str(test_file), data, True)

                assert "Created Excel file" in result
                assert mock_ws.append.call_count == 3
                mock_wb.save.assert_called_once()

    def test_create_simple_excel_missing_openpyxl(self, tmp_path):
        """Test error when openpyxl not installed."""
        with patch.object(writing, "HAS_OPENPYXL", False):
            with pytest.raises(ImportError, match="openpyxl is required"):
                writing.create_simple_excel("/tmp/test.xlsx", [["data"]], True)

    def test_create_simple_excel_type_validation(self, tmp_path):
        """Test parameter type validation."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"

            with pytest.raises(TypeError, match="file_path must be a string"):
                writing.create_simple_excel(123, [["data"]], True)

            with pytest.raises(TypeError, match="data must be a list"):
                writing.create_simple_excel(str(test_file), "not a list", True)

            with pytest.raises(TypeError, match="skip_confirm must be a boolean"):
                writing.create_simple_excel(str(test_file), [["data"]], "yes")

    def test_create_simple_excel_empty_data(self, tmp_path):
        """Test error with empty data."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"

            with pytest.raises(ValueError, match="data must not be empty"):
                writing.create_simple_excel(str(test_file), [], True)

    def test_create_simple_excel_file_exists_without_confirm(self, tmp_path):
        """Test error when file exists and skip_confirm is False."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"existing content")

            with pytest.raises(ValueError, match="File already exists"):
                writing.create_simple_excel(str(test_file), [["data"]], False)

    def test_create_simple_excel_parent_directory_not_exists(self):
        """Test error when parent directory doesn't exist."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            with pytest.raises(ValueError, match="Parent directory does not exist"):
                writing.create_simple_excel(
                    "/nonexistent/dir/test.xlsx", [["data"]], True
                )


class TestCreateExcelWithHeaders:
    """Tests for create_excel_with_headers function."""

    def test_create_excel_with_headers_success(self, tmp_path):
        """Test creating Excel with headers."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            with patch.object(writing, "create_simple_excel") as mock_create:
                mock_create.return_value = "Created Excel file"

                test_file = tmp_path / "test.xlsx"
                headers = ["Name", "Age", "City"]
                data = [["Alice", "30", "NYC"], ["Bob", "25", "LA"]]

                result = writing.create_excel_with_headers(
                    str(test_file), headers, data, True
                )

                assert "Created Excel file" in result
                # Verify headers were combined with data
                call_args = mock_create.call_args[0]
                combined_data = call_args[1]
                assert combined_data[0] == headers
                assert len(combined_data) == 3

    def test_create_excel_with_headers_type_validation(self, tmp_path):
        """Test parameter type validation."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"

            with pytest.raises(TypeError, match="headers must be a list"):
                writing.create_excel_with_headers(
                    str(test_file), "not a list", [["data"]], True
                )

    def test_create_excel_with_headers_empty_headers(self, tmp_path):
        """Test error with empty headers."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"

            with pytest.raises(ValueError, match="headers must not be empty"):
                writing.create_excel_with_headers(str(test_file), [], [["data"]], True)


class TestCreateExcelFromDicts:
    """Tests for create_excel_from_dicts function."""

    def test_create_excel_from_dicts_success(self, tmp_path):
        """Test creating Excel from dictionaries."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            with patch.object(writing, "create_excel_with_headers") as mock_create:
                mock_create.return_value = "Created Excel file"

                test_file = tmp_path / "test.xlsx"
                data = [
                    {"Name": "Alice", "Age": "30", "City": "NYC"},
                    {"Name": "Bob", "Age": "25", "City": "LA"},
                ]

                result = writing.create_excel_from_dicts(str(test_file), data, True)

                assert "Created Excel file" in result
                # Verify headers and rows were extracted correctly
                call_args = mock_create.call_args[0]
                headers = call_args[1]
                assert "Name" in headers
                assert "Age" in headers
                assert "City" in headers

    def test_create_excel_from_dicts_type_validation(self, tmp_path):
        """Test parameter type validation."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"

            with pytest.raises(TypeError, match="data must be a list"):
                writing.create_excel_from_dicts(str(test_file), "not a list", True)

    def test_create_excel_from_dicts_empty_data(self, tmp_path):
        """Test error with empty data."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"

            with pytest.raises(ValueError, match="data must not be empty"):
                writing.create_excel_from_dicts(str(test_file), [], True)


class TestAddSheetToExcel:
    """Tests for add_sheet_to_excel function."""

    def test_add_sheet_to_excel_success(self, tmp_path):
        """Test adding sheet to existing Excel file."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            with patch.object(writing, "load_workbook") as mock_load:
                mock_wb = MagicMock()
                mock_ws = MagicMock()
                mock_wb.sheetnames = ["Sheet1"]
                mock_wb.create_sheet.return_value = mock_ws
                mock_wb.save = Mock()
                mock_wb.close = Mock()
                mock_load.return_value = mock_wb

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"existing content")

                data = [["Product", "Price"], ["Apple", "1.00"]]

                result = writing.add_sheet_to_excel(
                    str(test_file), "Products", data, True
                )

                assert "Added sheet" in result
                assert mock_ws.append.call_count == 2
                mock_wb.save.assert_called_once()

    def test_add_sheet_to_excel_file_not_found(self):
        """Test error when file doesn't exist."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            with pytest.raises(FileNotFoundError, match="Excel file not found"):
                writing.add_sheet_to_excel(
                    "/nonexistent/file.xlsx", "Sheet2", [["data"]], True
                )

    def test_add_sheet_to_excel_sheet_exists_without_confirm(self, tmp_path):
        """Test error when sheet exists and skip_confirm is False."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            with patch.object(writing, "load_workbook") as mock_load:
                mock_wb = MagicMock()
                mock_wb.sheetnames = ["Sheet1", "Products"]
                mock_load.return_value = mock_wb

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                with pytest.raises(ValueError, match="Sheet 'Products' already exists"):
                    writing.add_sheet_to_excel(
                        str(test_file), "Products", [["data"]], False
                    )


class TestAppendRowsToExcel:
    """Tests for append_rows_to_excel function."""

    def test_append_rows_to_excel_success(self, tmp_path):
        """Test appending rows to existing sheet."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            with patch.object(writing, "load_workbook") as mock_load:
                mock_wb = MagicMock()
                mock_ws = MagicMock()
                mock_wb.sheetnames = ["Sheet1"]
                mock_wb.__getitem__.return_value = mock_ws
                mock_wb.save = Mock()
                mock_wb.close = Mock()
                mock_load.return_value = mock_wb

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                rows = [["Charlie", "35", "SF"], ["Dana", "28", "LA"]]

                result = writing.append_rows_to_excel(
                    str(test_file), "Sheet1", rows, True
                )

                assert "Appended" in result
                assert mock_ws.append.call_count == 2
                mock_wb.save.assert_called_once()

    def test_append_rows_to_excel_sheet_not_found(self, tmp_path):
        """Test error when sheet doesn't exist."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            with patch.object(writing, "load_workbook") as mock_load:
                mock_wb = MagicMock()
                mock_wb.sheetnames = ["Sheet1"]
                mock_load.return_value = mock_wb

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                with pytest.raises(ValueError, match="Sheet 'NonExistent' not found"):
                    writing.append_rows_to_excel(
                        str(test_file), "NonExistent", [["data"]], True
                    )


class TestUpdateExcelCell:
    """Tests for update_excel_cell function."""

    def test_update_excel_cell_success(self, tmp_path):
        """Test updating single cell value."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            with patch.object(writing, "load_workbook") as mock_load:
                mock_wb = MagicMock()
                mock_ws = MagicMock()
                mock_wb.sheetnames = ["Sheet1"]
                mock_wb.__getitem__.return_value = mock_ws
                mock_wb.save = Mock()
                mock_wb.close = Mock()
                mock_load.return_value = mock_wb

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = writing.update_excel_cell(
                    str(test_file), "Sheet1", "B5", "Updated", True
                )

                assert "Updated cell" in result
                assert mock_ws.__setitem__.called
                mock_wb.save.assert_called_once()

    def test_update_excel_cell_type_validation(self, tmp_path):
        """Test parameter type validation."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(TypeError, match="cell_reference must be a string"):
                writing.update_excel_cell(str(test_file), "Sheet1", 123, "value", True)

            with pytest.raises(TypeError, match="value must be a string"):
                writing.update_excel_cell(str(test_file), "Sheet1", "B5", 456, True)


class TestDeleteExcelSheet:
    """Tests for delete_excel_sheet function."""

    def test_delete_excel_sheet_success(self, tmp_path):
        """Test deleting sheet from workbook."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            with patch.object(writing, "load_workbook") as mock_load:
                mock_wb = MagicMock()
                mock_wb.sheetnames = ["Sheet1", "OldSheet"]
                mock_wb.__delitem__ = Mock()
                mock_wb.save = Mock()
                mock_wb.close = Mock()
                mock_load.return_value = mock_wb

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = writing.delete_excel_sheet(str(test_file), "OldSheet", True)

                assert "Deleted sheet" in result
                mock_wb.__delitem__.assert_called_once_with("OldSheet")
                mock_wb.save.assert_called_once()

    def test_delete_excel_sheet_requires_confirmation(self, tmp_path):
        """Test error when skip_confirm is False."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(ValueError, match="Deletion requires confirmation"):
                writing.delete_excel_sheet(str(test_file), "Sheet1", False)

    def test_delete_excel_sheet_last_sheet_error(self, tmp_path):
        """Test error when deleting last sheet."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            with patch.object(writing, "load_workbook") as mock_load:
                mock_wb = MagicMock()
                mock_wb.sheetnames = ["OnlySheet"]
                mock_load.return_value = mock_wb

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                with pytest.raises(ValueError, match="Cannot delete the last sheet"):
                    writing.delete_excel_sheet(str(test_file), "OnlySheet", True)


class TestExcelToCSV:
    """Tests for excel_to_csv function."""

    def test_excel_to_csv_success(self, tmp_path):
        """Test exporting Excel sheet to CSV."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            with patch.object(writing, "load_workbook") as mock_load:
                mock_wb = MagicMock()
                mock_ws = MagicMock()
                mock_ws.iter_rows.return_value = [
                    ("Name", "Age"),
                    ("Alice", 30),
                    ("Bob", None),
                ]
                mock_wb.sheetnames = ["Sheet1"]
                mock_wb.__getitem__.return_value = mock_ws
                mock_wb.close = Mock()
                mock_load.return_value = mock_wb

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")
                output_file = tmp_path / "output.csv"

                result = writing.excel_to_csv(
                    str(test_file), "Sheet1", str(output_file), True
                )

                assert "Exported" in result
                assert output_file.exists()

    def test_excel_to_csv_file_exists_without_confirm(self, tmp_path):
        """Test error when CSV file exists and skip_confirm is False."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")
            output_file = tmp_path / "output.csv"
            output_file.write_bytes(b"existing csv content")

            with pytest.raises(ValueError, match="CSV file already exists"):
                writing.excel_to_csv(str(test_file), "Sheet1", str(output_file), False)

    def test_excel_to_csv_excel_file_not_found(self):
        """Test error when Excel file doesn't exist."""
        with patch.object(writing, "HAS_OPENPYXL", True):
            with pytest.raises(FileNotFoundError, match="Excel file not found"):
                writing.excel_to_csv(
                    "/nonexistent/file.xlsx", "Sheet1", "/tmp/output.csv", True
                )
