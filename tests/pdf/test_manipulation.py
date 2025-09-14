"""Tests for PDF manipulation functions."""

import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open
import pytest
from basic_open_agent_tools.pdf.manipulation import (
    split_pdf_by_pages,
    extract_pages_from_pdf,
    rotate_pdf_pages,
    add_watermark_to_pdf
)
from basic_open_agent_tools.exceptions import BasicAgentToolsError


class TestSplitPdfByPages:
    """Test cases for split_pdf_by_pages function."""

    def test_invalid_input_path_type(self):
        """Test with invalid input path type."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            split_pdf_by_pages(123, 5)
        assert "Input path must be a non-empty string" in str(exc_info.value)

    def test_invalid_pages_per_file(self):
        """Test with invalid pages per file value."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            split_pdf_by_pages("test.pdf", 0)
        assert "Pages per file must be a positive integer" in str(exc_info.value)

    def test_nonexistent_file(self):
        """Test with nonexistent input file."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            split_pdf_by_pages("nonexistent.pdf", 5)
        assert "Input PDF not found" in str(exc_info.value)

    @patch('basic_open_agent_tools.pdf.manipulation.HAS_PYPDF2', False)
    def test_missing_pypdf2_dependency(self):
        """Test error when PyPDF2 is not available."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            split_pdf_by_pages("test.pdf", 5)
        assert "PyPDF2 package required" in str(exc_info.value)

    @patch('basic_open_agent_tools.pdf.manipulation.HAS_PYPDF2', True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('basic_open_agent_tools.pdf.manipulation.PyPDF2')
    def test_successful_split(self, mock_pypdf2, mock_exists, mock_file):
        """Test successful PDF splitting."""
        mock_exists.return_value = True

        # Mock PDF reader with 10 pages
        mock_reader = MagicMock()
        mock_reader.pages = [MagicMock() for _ in range(10)]
        mock_pypdf2.PdfReader.return_value = mock_reader

        # Mock PDF writer
        mock_writer = MagicMock()
        mock_pypdf2.PdfWriter.return_value = mock_writer

        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = os.path.join(temp_dir, "input.pdf")

            result = split_pdf_by_pages(input_path, 3)

            assert result["total_pages"] == 10
            assert result["pages_per_file"] == 3
            assert result["files_created"] == 4  # 3+3+3+1 pages
            assert result["split_status"] == "success"
            assert len(result["output_files"]) == 4

    @patch('basic_open_agent_tools.pdf.manipulation.HAS_PYPDF2', True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('basic_open_agent_tools.pdf.manipulation.PyPDF2')
    def test_empty_pdf(self, mock_pypdf2, mock_exists, mock_file):
        """Test splitting PDF with no pages."""
        mock_exists.return_value = True

        mock_reader = MagicMock()
        mock_reader.pages = []  # Empty PDF
        mock_pypdf2.PdfReader.return_value = mock_reader

        with pytest.raises(BasicAgentToolsError) as exc_info:
            split_pdf_by_pages("empty.pdf", 5)
        assert "PDF contains no pages" in str(exc_info.value)


class TestExtractPagesFromPdf:
    """Test cases for extract_pages_from_pdf function."""

    def test_invalid_page_range_type(self):
        """Test with invalid page range type."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            extract_pages_from_pdf("test.pdf", 123, "output.pdf")
        assert "Page range must be a non-empty string" in str(exc_info.value)

    @patch('basic_open_agent_tools.pdf.manipulation.HAS_PYPDF2', True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('basic_open_agent_tools.pdf.manipulation.PyPDF2')
    def test_successful_page_extraction(self, mock_pypdf2, mock_getsize, mock_exists, mock_file):
        """Test successful page extraction."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024

        # Mock PDF reader with 10 pages
        mock_reader = MagicMock()
        mock_reader.pages = [MagicMock() for _ in range(10)]
        mock_pypdf2.PdfReader.return_value = mock_reader

        mock_writer = MagicMock()
        mock_pypdf2.PdfWriter.return_value = mock_writer

        result = extract_pages_from_pdf("input.pdf", "1-3,5", "output.pdf")

        assert result["total_pages_in_input"] == 10
        assert result["pages_extracted"] == 4  # Pages 1,2,3,5
        assert result["page_range_requested"] == "1-3,5"
        assert result["output_file_size_bytes"] == 1024
        assert result["extraction_status"] == "success"

    @patch('basic_open_agent_tools.pdf.manipulation.HAS_PYPDF2', True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('basic_open_agent_tools.pdf.manipulation.PyPDF2')
    def test_extract_all_pages(self, mock_pypdf2, mock_getsize, mock_exists, mock_file):
        """Test extracting all pages."""
        mock_exists.return_value = True
        mock_getsize.return_value = 2048

        mock_reader = MagicMock()
        mock_reader.pages = [MagicMock() for _ in range(5)]
        mock_pypdf2.PdfReader.return_value = mock_reader

        mock_writer = MagicMock()
        mock_pypdf2.PdfWriter.return_value = mock_writer

        result = extract_pages_from_pdf("input.pdf", "all", "output.pdf")

        assert result["pages_extracted"] == 5


class TestRotatePdfPages:
    """Test cases for rotate_pdf_pages function."""

    def test_invalid_rotation_angle(self):
        """Test with invalid rotation angle."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            rotate_pdf_pages("test.pdf", 45)
        assert "Rotation angle must be one of" in str(exc_info.value)

    @patch('basic_open_agent_tools.pdf.manipulation.HAS_PYPDF2', True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('basic_open_agent_tools.pdf.manipulation.PyPDF2')
    def test_successful_rotation(self, mock_pypdf2, mock_getsize, mock_exists, mock_file):
        """Test successful page rotation."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1500

        # Mock PDF reader and pages
        mock_pages = []
        for _ in range(5):
            mock_page = MagicMock()
            mock_page.rotate.return_value = mock_page
            mock_pages.append(mock_page)

        mock_reader = MagicMock()
        mock_reader.pages = mock_pages
        mock_pypdf2.PdfReader.return_value = mock_reader

        mock_writer = MagicMock()
        mock_pypdf2.PdfWriter.return_value = mock_writer

        result = rotate_pdf_pages("input.pdf", 90, "1-3")

        assert result["total_pages"] == 5
        assert result["pages_rotated"] == 3
        assert result["rotation_angle"] == 90
        assert result["page_range"] == "1-3"
        assert result["rotation_status"] == "success"

        # Verify rotation was called on the correct pages
        mock_pages[0].rotate.assert_called_once_with(90)
        mock_pages[1].rotate.assert_called_once_with(90)
        mock_pages[2].rotate.assert_called_once_with(90)
        mock_pages[3].rotate.assert_not_called()
        mock_pages[4].rotate.assert_not_called()


class TestAddWatermarkToPdf:
    """Test cases for add_watermark_to_pdf function."""

    def test_missing_dependencies(self):
        """Test error when required dependencies are missing."""
        with patch('basic_open_agent_tools.pdf.manipulation.HAS_REPORTLAB', False):
            with pytest.raises(BasicAgentToolsError) as exc_info:
                add_watermark_to_pdf("test.pdf", "WATERMARK")
            assert "Both reportlab and PyPDF2 packages required" in str(exc_info.value)

    def test_invalid_opacity(self):
        """Test with invalid opacity value."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            add_watermark_to_pdf("test.pdf", "WATERMARK", opacity=1.5)
        assert "Opacity must be a number between 0.0 and 1.0" in str(exc_info.value)

    def test_empty_watermark_text(self):
        """Test with empty watermark text."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            add_watermark_to_pdf("test.pdf", "")
        assert "Watermark text must be a non-empty string" in str(exc_info.value)

    @patch('basic_open_agent_tools.pdf.manipulation.HAS_REPORTLAB', True)
    @patch('basic_open_agent_tools.pdf.manipulation.HAS_PYPDF2', True)
    @patch('tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('os.unlink')
    @patch('basic_open_agent_tools.pdf.manipulation.canvas')
    @patch('basic_open_agent_tools.pdf.manipulation.PyPDF2')
    def test_successful_watermarking(self, mock_pypdf2, mock_canvas, mock_unlink,
                                   mock_getsize, mock_exists, mock_file, mock_temp):
        """Test successful watermark addition."""
        mock_exists.return_value = True
        mock_getsize.return_value = 2048

        # Mock temporary file
        mock_temp_file = MagicMock()
        mock_temp_file.name = "temp_watermark.pdf"
        mock_temp.__enter__.return_value = mock_temp_file

        # Mock canvas
        mock_canvas_instance = MagicMock()
        mock_canvas.Canvas.return_value = mock_canvas_instance

        # Mock PDF components
        mock_pages = [MagicMock() for _ in range(3)]
        mock_reader = MagicMock()
        mock_reader.pages = mock_pages
        mock_pypdf2.PdfReader.return_value = mock_reader

        mock_watermark_page = MagicMock()
        mock_watermark_reader = MagicMock()
        mock_watermark_reader.pages = [mock_watermark_page]

        mock_writer = MagicMock()
        mock_pypdf2.PdfWriter.return_value = mock_writer

        # Configure PdfReader to return different instances
        mock_pypdf2.PdfReader.side_effect = [mock_reader, mock_watermark_reader]

        result = add_watermark_to_pdf("input.pdf", "CONFIDENTIAL", "output.pdf", 0.5)

        assert result["watermark_text"] == "CONFIDENTIAL"
        assert result["pages_watermarked"] == 3
        assert result["opacity"] == 0.5
        assert result["watermarking_status"] == "success"

        # Verify watermark creation
        mock_canvas.Canvas.assert_called_once()
        mock_canvas_instance.drawCentredText.assert_called_once()

        # Verify page merging
        for page in mock_pages:
            page.merge_page.assert_called_once_with(mock_watermark_page)