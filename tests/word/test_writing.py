"""Tests for basic_open_agent_tools.word.writing module."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from basic_open_agent_tools.word.writing import (
    add_paragraph_to_docx,
    add_table_to_docx,
    create_docx_from_paragraphs,
    create_docx_from_template,
    create_docx_with_headings,
    create_docx_with_title,
    create_simple_docx,
    docx_to_text,
)


class TestCreateSimpleDocx:
    """Test cases for create_simple_docx function."""

    def test_create_simple_docx_basic(self, tmp_path: Path) -> None:
        """Test creating a simple Word document."""
        docx_file = tmp_path / "test.docx"

        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            mock_doc = Mock()
            mock_doc.add_paragraph = Mock()
            mock_doc.save = Mock()

            with patch(
                "basic_open_agent_tools.word.writing.Document",
                return_value=mock_doc,
                create=True,
            ):
                with patch("os.path.getsize", return_value=1024):
                    result = create_simple_docx(
                        str(docx_file), "Test content", skip_confirm=True
                    )

            # Verify document methods were called
            mock_doc.add_paragraph.assert_called_once_with("Test content")
            mock_doc.save.assert_called_once_with(str(docx_file))

        assert "Created Word document" in result
        assert str(docx_file) in result

    def test_create_simple_docx_unicode_content(self, tmp_path: Path) -> None:
        """Test creating document with Unicode content."""
        docx_file = tmp_path / "unicode.docx"
        unicode_content = "北京 東京 Москва 🚀"

        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            mock_doc = Mock()
            mock_doc.add_paragraph = Mock()
            mock_doc.save = Mock()

            with patch(
                "basic_open_agent_tools.word.writing.Document",
                return_value=mock_doc,
                create=True,
            ):
                with patch("os.path.getsize", return_value=2048):
                    result = create_simple_docx(
                        str(docx_file), unicode_content, skip_confirm=True
                    )

            mock_doc.add_paragraph.assert_called_once_with(unicode_content)

        assert "Created Word document" in result

    def test_create_simple_docx_python_docx_not_available(self) -> None:
        """Test error when python-docx is not installed."""
        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", False):
            with pytest.raises(ImportError, match="python-docx is required"):
                create_simple_docx("test.docx", "content", skip_confirm=True)

    def test_create_simple_docx_invalid_file_path_type(self) -> None:
        """Test error when file_path is not a string."""
        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            with pytest.raises(TypeError, match="file_path must be a string"):
                create_simple_docx(123, "content", skip_confirm=True)  # type: ignore[arg-type]

    def test_create_simple_docx_empty_file_path(self) -> None:
        """Test error when file_path is empty string."""
        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            with pytest.raises(ValueError, match="file_path cannot be empty"):
                create_simple_docx("", "content", skip_confirm=True)

    def test_create_simple_docx_invalid_content_type(self) -> None:
        """Test error when content is not a string."""
        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            with pytest.raises(TypeError, match="content must be a string"):
                create_simple_docx("test.docx", 123, skip_confirm=True)  # type: ignore[arg-type]


class TestCreateDocxFromParagraphs:
    """Test cases for create_docx_from_paragraphs function."""

    def test_create_from_paragraphs_basic(self, tmp_path: Path) -> None:
        """Test creating document from list of paragraphs."""
        docx_file = tmp_path / "test.docx"
        paragraphs = ["First paragraph", "Second paragraph", "Third paragraph"]

        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            mock_doc = Mock()
            mock_doc.add_paragraph = Mock()
            mock_doc.save = Mock()

            with patch(
                "basic_open_agent_tools.word.writing.Document",
                return_value=mock_doc,
                create=True,
            ):
                result = create_docx_from_paragraphs(
                    str(docx_file), paragraphs, skip_confirm=True
                )

            # Verify add_paragraph was called for each paragraph
            assert mock_doc.add_paragraph.call_count == 3
            mock_doc.save.assert_called_once()

        assert "Created Word document" in result
        assert "3 paragraphs" in result

    def test_create_from_paragraphs_empty_list(self, tmp_path: Path) -> None:
        """Test error with empty paragraph list."""
        docx_file = tmp_path / "empty.docx"

        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            with pytest.raises(ValueError, match="paragraphs cannot be empty"):
                create_docx_from_paragraphs(str(docx_file), [], skip_confirm=True)

    def test_create_from_paragraphs_invalid_type(self) -> None:
        """Test error when paragraphs is not a list."""
        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            with pytest.raises(TypeError, match="paragraphs must be a list"):
                create_docx_from_paragraphs(
                    "test.docx", "not a list", skip_confirm=True
                )  # type: ignore[arg-type]

    def test_create_from_paragraphs_python_docx_not_available(self) -> None:
        """Test error when python-docx is not installed."""
        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", False):
            with pytest.raises(ImportError, match="python-docx is required"):
                create_docx_from_paragraphs("test.docx", ["text"], skip_confirm=True)


class TestCreateDocxWithTitle:
    """Test cases for create_docx_with_title function."""

    def test_create_with_title_basic(self, tmp_path: Path) -> None:
        """Test creating document with title."""
        docx_file = tmp_path / "test.docx"

        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            mock_doc = Mock()
            mock_doc.add_heading = Mock()
            mock_doc.add_paragraph = Mock()
            mock_doc.save = Mock()

            with patch(
                "basic_open_agent_tools.word.writing.Document",
                return_value=mock_doc,
                create=True,
            ):
                with patch(
                    "basic_open_agent_tools.word.writing.os.path.getsize",
                    return_value=2048,
                ):
                    result = create_docx_with_title(
                        str(docx_file),
                        "Document Title",
                        "Document content",
                        skip_confirm=True,
                    )

            mock_doc.add_heading.assert_called_once_with("Document Title", level=1)
            mock_doc.add_paragraph.assert_called_once_with("Document content")
            mock_doc.save.assert_called_once()

        assert "Created Word document" in result

    def test_create_with_title_unicode(self, tmp_path: Path) -> None:
        """Test creating document with Unicode title and content."""
        docx_file = tmp_path / "unicode.docx"
        title = "文档标题"
        content = "内容 🚀"

        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            mock_doc = Mock()
            mock_doc.add_heading = Mock()
            mock_doc.add_paragraph = Mock()
            mock_doc.save = Mock()

            with patch(
                "basic_open_agent_tools.word.writing.Document",
                return_value=mock_doc,
                create=True,
            ):
                with patch(
                    "basic_open_agent_tools.word.writing.os.path.getsize",
                    return_value=3072,
                ):
                    result = create_docx_with_title(
                        str(docx_file), title, content, skip_confirm=True
                    )

            mock_doc.add_heading.assert_called_once_with(title, level=1)
            mock_doc.add_paragraph.assert_called_once_with(content)

        assert "Created Word document" in result

    def test_create_with_title_python_docx_not_available(self) -> None:
        """Test error when python-docx is not installed."""
        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", False):
            with pytest.raises(ImportError, match="python-docx is required"):
                create_docx_with_title(
                    "test.docx", "Title", "Content", skip_confirm=True
                )


class TestAddParagraphToDocx:
    """Test cases for add_paragraph_to_docx function."""

    def test_add_paragraph_to_existing_document(self, tmp_path: Path) -> None:
        """Test adding paragraph to existing document."""
        docx_file = tmp_path / "existing.docx"
        docx_file.touch()

        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            mock_doc = Mock()
            mock_doc.add_paragraph = Mock()
            mock_doc.save = Mock()

            with patch(
                "basic_open_agent_tools.word.writing.Document",
                return_value=mock_doc,
                create=True,
            ):
                result = add_paragraph_to_docx(
                    str(docx_file), "New paragraph", skip_confirm=True
                )

            mock_doc.add_paragraph.assert_called_once_with("New paragraph")
            mock_doc.save.assert_called_once_with(str(docx_file))

        assert "Added paragraph to" in result

    def test_add_paragraph_file_not_found(self) -> None:
        """Test error when document doesn't exist."""
        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            with pytest.raises(FileNotFoundError, match="File does not exist"):
                add_paragraph_to_docx(
                    "/nonexistent/file.docx", "paragraph", skip_confirm=False
                )

    def test_add_paragraph_python_docx_not_available(self) -> None:
        """Test error when python-docx is not installed."""
        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", False):
            with pytest.raises(ImportError, match="python-docx is required"):
                add_paragraph_to_docx("test.docx", "paragraph", skip_confirm=True)


class TestCreateDocxWithHeadings:
    """Test cases for create_docx_with_headings function."""

    def test_create_with_headings_basic(self, tmp_path: Path) -> None:
        """Test creating document with headings."""
        docx_file = tmp_path / "test.docx"
        sections = [
            {"heading": "Section 1", "level": "1", "content": "Content 1"},
            {"heading": "Section 2", "level": "2", "content": "Content 2"},
        ]

        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            mock_doc = Mock()
            mock_doc.add_heading = Mock()
            mock_doc.add_paragraph = Mock()
            mock_doc.save = Mock()

            with patch(
                "basic_open_agent_tools.word.writing.Document",
                return_value=mock_doc,
                create=True,
            ):
                result = create_docx_with_headings(
                    str(docx_file), sections, skip_confirm=True
                )

            # Verify headings and paragraphs were added
            assert mock_doc.add_heading.call_count == 2
            assert mock_doc.add_paragraph.call_count == 2
            mock_doc.save.assert_called_once()

        assert "Created Word document" in result
        assert "2 sections" in result

    def test_create_with_headings_empty_sections(self, tmp_path: Path) -> None:
        """Test error with empty sections list."""
        docx_file = tmp_path / "empty.docx"

        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            with pytest.raises(ValueError, match="sections cannot be empty"):
                create_docx_with_headings(str(docx_file), [], skip_confirm=True)

    def test_create_with_headings_invalid_sections_type(self) -> None:
        """Test error when sections is not a list."""
        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            with pytest.raises(TypeError, match="sections must be a list"):
                create_docx_with_headings("test.docx", "not a list", skip_confirm=True)  # type: ignore[arg-type]

    def test_create_with_headings_python_docx_not_available(self) -> None:
        """Test error when python-docx is not installed."""
        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", False):
            with pytest.raises(ImportError, match="python-docx is required"):
                create_docx_with_headings("test.docx", [], skip_confirm=True)


class TestAddTableToDocx:
    """Test cases for add_table_to_docx function."""

    def test_add_table_basic(self, tmp_path: Path) -> None:
        """Test adding table to document."""
        docx_file = tmp_path / "test.docx"
        docx_file.touch()

        table_data = [
            ["Header 1", "Header 2"],
            ["Row 1 Col 1", "Row 1 Col 2"],
            ["Row 2 Col 1", "Row 2 Col 2"],
        ]

        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            mock_doc = Mock()
            mock_table = Mock()
            mock_table.rows = []

            # Create mock rows and cells
            for _ in range(3):
                mock_row = Mock()
                mock_cell_1 = Mock()
                mock_cell_2 = Mock()
                mock_row.cells = [mock_cell_1, mock_cell_2]
                mock_table.rows.append(mock_row)

            mock_doc.add_table = Mock(return_value=mock_table)
            mock_doc.save = Mock()

            with patch(
                "basic_open_agent_tools.word.writing.Document",
                return_value=mock_doc,
                create=True,
            ):
                result = add_table_to_docx(
                    str(docx_file), table_data, skip_confirm=True
                )

            mock_doc.add_table.assert_called_once_with(rows=3, cols=2)
            mock_doc.save.assert_called_once()

        assert "Added 3x2 table" in result

    def test_add_table_empty_data(self, tmp_path: Path) -> None:
        """Test error when table data is empty."""
        docx_file = tmp_path / "test.docx"
        docx_file.touch()

        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            with pytest.raises(ValueError, match="table_data cannot be empty"):
                add_table_to_docx(str(docx_file), [], skip_confirm=True)

    def test_add_table_invalid_data_type(self, tmp_path: Path) -> None:
        """Test error when table_data is not a list."""
        docx_file = tmp_path / "test.docx"
        docx_file.touch()

        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            with pytest.raises(TypeError, match="table_data must be a list"):
                add_table_to_docx(str(docx_file), "not a list", skip_confirm=True)  # type: ignore[arg-type]

    def test_add_table_python_docx_not_available(self) -> None:
        """Test error when python-docx is not installed."""
        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", False):
            with pytest.raises(ImportError, match="python-docx is required"):
                add_table_to_docx("test.docx", [["data"]], skip_confirm=True)


class TestCreateDocxFromTemplate:
    """Test cases for create_docx_from_template function."""

    def test_create_from_template_basic(self, tmp_path: Path) -> None:
        """Test creating document from template."""
        template_file = tmp_path / "template.docx"
        template_file.touch()
        output_file = tmp_path / "output.docx"

        replacements = {"{{name}}": "John Doe", "{{date}}": "2024-01-01"}

        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            mock_doc = Mock()
            mock_para = Mock()
            mock_para.text = "Hello {{name}}, today is {{date}}"
            mock_run = Mock()
            mock_run.text = "Hello {{name}}, today is {{date}}"
            mock_para.runs = [mock_run]
            mock_doc.paragraphs = [mock_para]
            mock_doc.tables = []  # Empty tables list
            mock_doc.save = Mock()

            with patch(
                "basic_open_agent_tools.word.writing.Document",
                return_value=mock_doc,
                create=True,
            ):
                with patch(
                    "basic_open_agent_tools.word.writing.os.path.getsize",
                    return_value=4096,
                ):
                    result = create_docx_from_template(
                        str(template_file),
                        str(output_file),
                        replacements,
                        skip_confirm=True,
                    )

            mock_doc.save.assert_called_once_with(str(output_file))

        assert "Created document from template:" in result

    def test_create_from_template_file_not_found(self) -> None:
        """Test error when template doesn't exist."""
        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            with pytest.raises(FileNotFoundError, match="Template not found"):
                create_docx_from_template(
                    "/nonexistent/template.docx",
                    "output.docx",
                    {},
                    skip_confirm=True,
                )

    def test_create_from_template_invalid_replacements_type(
        self, tmp_path: Path
    ) -> None:
        """Test error when replacements is not a dict."""
        template_file = tmp_path / "template.docx"
        template_file.touch()

        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            with pytest.raises(TypeError, match="replacements must be a dict"):
                create_docx_from_template(
                    str(template_file),
                    "output.docx",
                    "not a dict",
                    skip_confirm=True,  # type: ignore[arg-type]
                )

    def test_create_from_template_python_docx_not_available(self) -> None:
        """Test error when python-docx is not installed."""
        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", False):
            with pytest.raises(ImportError, match="python-docx is required"):
                create_docx_from_template(
                    "template.docx", "output.docx", {}, skip_confirm=True
                )


class TestDocxToText:
    """Test cases for docx_to_text function."""

    def test_docx_to_text_basic(self, tmp_path: Path) -> None:
        """Test converting Word document to text file."""
        docx_file = tmp_path / "test.docx"
        docx_file.touch()
        text_file = tmp_path / "output.txt"

        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            mock_doc = Mock()
            mock_para1 = Mock()
            mock_para1.text = "First paragraph"
            mock_para2 = Mock()
            mock_para2.text = "Second paragraph"
            mock_doc.paragraphs = [mock_para1, mock_para2]

            with patch(
                "basic_open_agent_tools.word.writing.Document",
                return_value=mock_doc,
                create=True,
            ):
                with patch("builtins.open", create=True) as mock_open:
                    mock_file = Mock()
                    mock_open.return_value.__enter__.return_value = mock_file

                    with patch("os.path.getsize", return_value=512):
                        result = docx_to_text(
                            str(docx_file), str(text_file), skip_confirm=True
                        )

                    # Verify text file was written
                    mock_file.write.assert_called()

        assert "Converted" in result
        assert "to text file" in result

    def test_docx_to_text_file_not_found(self) -> None:
        """Test error when Word document doesn't exist."""
        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", True):
            with pytest.raises(FileNotFoundError, match="Input document not found"):
                docx_to_text("/nonexistent/file.docx", "output.txt", skip_confirm=True)

    def test_docx_to_text_python_docx_not_available(self) -> None:
        """Test error when python-docx is not installed."""
        with patch("basic_open_agent_tools.word.writing.HAS_PYTHON_DOCX", False):
            with pytest.raises(ImportError, match="python-docx is required"):
                docx_to_text("test.docx", "output.txt", skip_confirm=True)
