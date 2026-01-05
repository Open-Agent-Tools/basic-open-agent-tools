"""Tests for Excel formatting functions."""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

from basic_open_agent_tools.excel import formatting


class TestApplyExcelBold:
    """Tests for apply_excel_bold function."""

    def test_apply_excel_bold_success(self, tmp_path):
        """Test applying bold formatting to cell range."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            with patch.object(formatting, "load_workbook") as mock_load:
                with patch.object(formatting, "Font") as mock_font:
                    mock_wb = MagicMock()
                    mock_ws = MagicMock()
                    mock_cell = MagicMock()
                    mock_ws.__getitem__.return_value = [(mock_cell,)]
                    mock_wb.sheetnames = ["Sheet1"]
                    mock_wb.__getitem__.return_value = mock_ws
                    mock_wb.save = Mock()
                    mock_wb.close = Mock()
                    mock_load.return_value = mock_wb

                    test_file = tmp_path / "test.xlsx"
                    test_file.write_bytes(b"content")

                    result = formatting.apply_excel_bold(
                        str(test_file), "Sheet1", "A1:A10", True
                    )

                    assert "Applied bold" in result
                    mock_wb.save.assert_called_once()
                    mock_font.assert_called_with(bold=True)

    def test_apply_excel_bold_missing_openpyxl(self, tmp_path):
        """Test error when openpyxl not installed."""
        with patch.object(formatting, "HAS_OPENPYXL", False):
            with pytest.raises(ImportError, match="openpyxl is required"):
                formatting.apply_excel_bold("/tmp/test.xlsx", "Sheet1", "A1", True)

    def test_apply_excel_bold_type_validation(self, tmp_path):
        """Test parameter type validation."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(TypeError, match="file_path must be a string"):
                formatting.apply_excel_bold(123, "Sheet1", "A1", True)

            with pytest.raises(TypeError, match="sheet_name must be a string"):
                formatting.apply_excel_bold(str(test_file), 456, "A1", True)

            with pytest.raises(TypeError, match="cell_range must be a string"):
                formatting.apply_excel_bold(str(test_file), "Sheet1", 789, True)


class TestApplyExcelFontSize:
    """Tests for apply_excel_font_size function."""

    def test_apply_excel_font_size_success(self, tmp_path):
        """Test setting font size for cell range."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            with patch.object(formatting, "load_workbook") as mock_load:
                with patch.object(formatting, "Font") as mock_font:
                    mock_wb = MagicMock()
                    mock_ws = MagicMock()
                    mock_cell = MagicMock()
                    mock_ws.__getitem__.return_value = [(mock_cell,)]
                    mock_wb.sheetnames = ["Sheet1"]
                    mock_wb.__getitem__.return_value = mock_ws
                    mock_wb.save = Mock()
                    mock_wb.close = Mock()
                    mock_load.return_value = mock_wb

                    test_file = tmp_path / "test.xlsx"
                    test_file.write_bytes(b"content")

                    result = formatting.apply_excel_font_size(
                        str(test_file), "Sheet1", "A1", 14, True
                    )

                    assert "Set font size" in result
                    mock_wb.save.assert_called_once()
                    mock_font.assert_called_with(size=14)

    def test_apply_excel_font_size_type_validation(self, tmp_path):
        """Test parameter type validation."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(TypeError, match="font_size must be an integer"):
                formatting.apply_excel_font_size(
                    str(test_file), "Sheet1", "A1", "14", True
                )

    def test_apply_excel_font_size_invalid_range(self, tmp_path):
        """Test error with invalid font size range."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(ValueError, match="font_size must be between 1 and 409"):
                formatting.apply_excel_font_size(
                    str(test_file), "Sheet1", "A1", 0, True
                )

            with pytest.raises(ValueError, match="font_size must be between 1 and 409"):
                formatting.apply_excel_font_size(
                    str(test_file), "Sheet1", "A1", 500, True
                )


class TestApplyExcelAlignment:
    """Tests for apply_excel_alignment function."""

    def test_apply_excel_alignment_success(self, tmp_path):
        """Test setting cell alignment."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            with patch.object(formatting, "load_workbook") as mock_load:
                with patch.object(formatting, "Alignment") as mock_align:
                    mock_wb = MagicMock()
                    mock_ws = MagicMock()
                    mock_cell = MagicMock()
                    mock_ws.__getitem__.return_value = [(mock_cell,)]
                    mock_wb.sheetnames = ["Sheet1"]
                    mock_wb.__getitem__.return_value = mock_ws
                    mock_wb.save = Mock()
                    mock_wb.close = Mock()
                    mock_load.return_value = mock_wb

                    test_file = tmp_path / "test.xlsx"
                    test_file.write_bytes(b"content")

                    result = formatting.apply_excel_alignment(
                        str(test_file), "Sheet1", "A1", "center", "center", True
                    )

                    assert "Set alignment" in result
                    mock_wb.save.assert_called_once()
                    mock_align.assert_called_with(
                        horizontal="center", vertical="center"
                    )

    def test_apply_excel_alignment_invalid_horizontal(self, tmp_path):
        """Test error with invalid horizontal alignment."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(ValueError, match="horizontal must be one of"):
                formatting.apply_excel_alignment(
                    str(test_file), "Sheet1", "A1", "invalid", "center", True
                )

    def test_apply_excel_alignment_invalid_vertical(self, tmp_path):
        """Test error with invalid vertical alignment."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(ValueError, match="vertical must be one of"):
                formatting.apply_excel_alignment(
                    str(test_file), "Sheet1", "A1", "center", "invalid", True
                )


class TestSetExcelColumnWidth:
    """Tests for set_excel_column_width function."""

    def test_set_excel_column_width_success(self, tmp_path):
        """Test setting column width."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            with patch.object(formatting, "load_workbook") as mock_load:
                mock_wb = MagicMock()
                mock_ws = MagicMock()
                mock_col_dim = MagicMock()
                mock_ws.column_dimensions = {"A": mock_col_dim}
                mock_wb.sheetnames = ["Sheet1"]
                mock_wb.__getitem__.return_value = mock_ws
                mock_wb.save = Mock()
                mock_wb.close = Mock()
                mock_load.return_value = mock_wb

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = formatting.set_excel_column_width(
                    str(test_file), "Sheet1", "A", 20, True
                )

                assert "Set column width" in result
                assert mock_col_dim.width == 20
                mock_wb.save.assert_called_once()

    def test_set_excel_column_width_type_validation(self, tmp_path):
        """Test parameter type validation."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(TypeError, match="column_letter must be a string"):
                formatting.set_excel_column_width(str(test_file), "Sheet1", 1, 20, True)

            with pytest.raises(TypeError, match="width must be an integer"):
                formatting.set_excel_column_width(
                    str(test_file), "Sheet1", "A", "20", True
                )

    def test_set_excel_column_width_invalid_range(self, tmp_path):
        """Test error with invalid width range."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(ValueError, match="width must be between 0 and 255"):
                formatting.set_excel_column_width(
                    str(test_file), "Sheet1", "A", -1, True
                )

    def test_set_excel_column_width_invalid_letter(self, tmp_path):
        """Test error with invalid column letter."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(ValueError, match="Invalid column letter"):
                formatting.set_excel_column_width(
                    str(test_file), "Sheet1", "123", 20, True
                )


class TestSetExcelRowHeight:
    """Tests for set_excel_row_height function."""

    def test_set_excel_row_height_success(self, tmp_path):
        """Test setting row height."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            with patch.object(formatting, "load_workbook") as mock_load:
                mock_wb = MagicMock()
                mock_ws = MagicMock()
                mock_row_dim = MagicMock()
                mock_ws.row_dimensions = {1: mock_row_dim}
                mock_wb.sheetnames = ["Sheet1"]
                mock_wb.__getitem__.return_value = mock_ws
                mock_wb.save = Mock()
                mock_wb.close = Mock()
                mock_load.return_value = mock_wb

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = formatting.set_excel_row_height(
                    str(test_file), "Sheet1", 1, 30, True
                )

                assert "Set row height" in result
                assert mock_row_dim.height == 30
                mock_wb.save.assert_called_once()

    def test_set_excel_row_height_type_validation(self, tmp_path):
        """Test parameter type validation."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(TypeError, match="row_number must be an integer"):
                formatting.set_excel_row_height(str(test_file), "Sheet1", "1", 30, True)

            with pytest.raises(TypeError, match="height must be an integer"):
                formatting.set_excel_row_height(str(test_file), "Sheet1", 1, "30", True)

    def test_set_excel_row_height_invalid_row_number(self, tmp_path):
        """Test error with invalid row number."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(ValueError, match="row_number must be >= 1"):
                formatting.set_excel_row_height(str(test_file), "Sheet1", 0, 30, True)

    def test_set_excel_row_height_invalid_range(self, tmp_path):
        """Test error with invalid height range."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(ValueError, match="height must be between 0 and 409"):
                formatting.set_excel_row_height(str(test_file), "Sheet1", 1, 500, True)


class TestApplyExcelCellColor:
    """Tests for apply_excel_cell_color function."""

    def test_apply_excel_cell_color_success(self, tmp_path):
        """Test applying background color to cells."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            with patch.object(formatting, "load_workbook") as mock_load:
                with patch.object(formatting, "PatternFill") as mock_fill:
                    mock_wb = MagicMock()
                    mock_ws = MagicMock()
                    mock_cell = MagicMock()
                    mock_ws.__getitem__.return_value = [(mock_cell,)]
                    mock_wb.sheetnames = ["Sheet1"]
                    mock_wb.__getitem__.return_value = mock_ws
                    mock_wb.save = Mock()
                    mock_wb.close = Mock()
                    mock_load.return_value = mock_wb

                    test_file = tmp_path / "test.xlsx"
                    test_file.write_bytes(b"content")

                    result = formatting.apply_excel_cell_color(
                        str(test_file), "Sheet1", "A1", "FFFF00", True
                    )

                    assert "Applied color" in result
                    mock_wb.save.assert_called_once()
                    mock_fill.assert_called()

    def test_apply_excel_cell_color_type_validation(self, tmp_path):
        """Test parameter type validation."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(TypeError, match="color_hex must be a string"):
                formatting.apply_excel_cell_color(
                    str(test_file), "Sheet1", "A1", 123456, True
                )

    def test_apply_excel_cell_color_invalid_hex(self, tmp_path):
        """Test error with invalid hex color."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(ValueError, match="color_hex must be 6 hex digits"):
                formatting.apply_excel_cell_color(
                    str(test_file), "Sheet1", "A1", "ZZZ", True
                )

            with pytest.raises(ValueError, match="color_hex must be 6 hex digits"):
                formatting.apply_excel_cell_color(
                    str(test_file), "Sheet1", "A1", "#FFFF00", True
                )


class TestFreezeExcelPanes:
    """Tests for freeze_excel_panes function."""

    def test_freeze_excel_panes_success(self, tmp_path):
        """Test freezing panes at specified cell."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            with patch.object(formatting, "load_workbook") as mock_load:
                mock_wb = MagicMock()
                mock_ws = MagicMock()
                mock_wb.sheetnames = ["Sheet1"]
                mock_wb.__getitem__.return_value = mock_ws
                mock_wb.save = Mock()
                mock_wb.close = Mock()
                mock_load.return_value = mock_wb

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = formatting.freeze_excel_panes(
                    str(test_file), "Sheet1", "B2", True
                )

                assert "Froze panes" in result
                assert mock_ws.freeze_panes == "B2"
                mock_wb.save.assert_called_once()

    def test_freeze_excel_panes_type_validation(self, tmp_path):
        """Test parameter type validation."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(TypeError, match="cell_reference must be a string"):
                formatting.freeze_excel_panes(str(test_file), "Sheet1", 123, True)


class TestAddExcelFormula:
    """Tests for add_excel_formula function."""

    def test_add_excel_formula_success(self, tmp_path):
        """Test adding formula to cell."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            with patch.object(formatting, "load_workbook") as mock_load:
                mock_wb = MagicMock()
                mock_ws = MagicMock()
                mock_wb.sheetnames = ["Sheet1"]
                mock_wb.__getitem__.return_value = mock_ws
                mock_wb.save = Mock()
                mock_wb.close = Mock()
                mock_load.return_value = mock_wb

                test_file = tmp_path / "test.xlsx"
                test_file.write_bytes(b"content")

                result = formatting.add_excel_formula(
                    str(test_file), "Sheet1", "C1", "=SUM(A1:A10)", True
                )

                assert "Added formula" in result
                mock_ws.__setitem__.assert_called_with("C1", "=SUM(A1:A10)")
                mock_wb.save.assert_called_once()

    def test_add_excel_formula_type_validation(self, tmp_path):
        """Test parameter type validation."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(TypeError, match="formula must be a string"):
                formatting.add_excel_formula(str(test_file), "Sheet1", "C1", 123, True)

    def test_add_excel_formula_invalid_formula(self, tmp_path):
        """Test error with formula not starting with =."""
        with patch.object(formatting, "HAS_OPENPYXL", True):
            test_file = tmp_path / "test.xlsx"
            test_file.write_bytes(b"content")

            with pytest.raises(ValueError, match="Formula must start with '='"):
                formatting.add_excel_formula(
                    str(test_file), "Sheet1", "C1", "SUM(A1:A10)", True
                )
