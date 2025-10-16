"""PDF creation and authoring functions for AI agents.

This module provides functions for creating PDF documents from text content
using the reportlab library.
"""

import os

from ..decorators import strands_tool

try:
    from reportlab.lib.pagesizes import (
        letter,  # type: ignore[import-untyped, import-not-found]
    )
    from reportlab.lib.styles import (
        getSampleStyleSheet,  # type: ignore[import-untyped, import-not-found]
    )
    from reportlab.lib.units import (
        inch,  # type: ignore[import-untyped, import-not-found]
    )
    from reportlab.platypus import (  # type: ignore[import-untyped, import-not-found]
        Paragraph,
        SimpleDocTemplate,
        Spacer,
    )

    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


@strands_tool
def create_simple_pdf(file_path: str, content: str, skip_confirm: bool) -> str:
    """Create simple PDF from text content.

    This function creates a basic PDF document with the provided text content.
    The text will be formatted as a single paragraph.

    Args:
        file_path: Path where PDF will be created
        content: Text content to include in PDF
        skip_confirm: If False, raises error if file exists; if True, overwrites

    Returns:
        Success message with file path and size

    Raises:
        ImportError: If reportlab is not installed
        TypeError: If parameters are wrong type
        ValueError: If file exists and skip_confirm=False, or content is empty
        PermissionError: If directory is not writable

    Example:
        >>> msg = create_simple_pdf("/tmp/test.pdf", "Hello World", False)
        >>> "Created PDF" in msg
        True
    """
    if not HAS_REPORTLAB:
        raise ImportError(
            "reportlab is required for PDF creation. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(content, str):
        raise TypeError("content must be a string")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if not file_path.strip():
        raise ValueError("file_path cannot be empty")

    if not content.strip():
        raise ValueError("content cannot be empty")

    # Check if file exists
    if os.path.exists(file_path) and not skip_confirm:
        raise ValueError(
            f"File already exists: {file_path}. Set skip_confirm=True to overwrite."
        )

    # Check parent directory is writable
    parent_dir = os.path.dirname(file_path) or "."
    if not os.path.exists(parent_dir):
        raise FileNotFoundError(f"Parent directory does not exist: {parent_dir}")

    if not os.access(parent_dir, os.W_OK):
        raise PermissionError(f"Cannot write to directory: {parent_dir}")

    try:
        # Create PDF
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add content as paragraph
        para = Paragraph(content, styles["Normal"])
        story.append(para)

        doc.build(story)

        # Get file size
        file_size = os.path.getsize(file_path)
        return f"Created PDF {file_path} ({file_size} bytes)"

    except Exception as e:
        raise ValueError(f"Failed to create PDF: {e}")


@strands_tool
def create_pdf_from_text_list(
    file_path: str, paragraphs: list[str], skip_confirm: bool
) -> str:
    """Create PDF with multiple paragraphs.

    This function creates a PDF with multiple paragraphs, each separated
    by spacing. Each string in the list becomes a separate paragraph.

    Args:
        file_path: Path where PDF will be created
        paragraphs: List of text strings, one per paragraph
        skip_confirm: If False, raises error if file exists; if True, overwrites

    Returns:
        Success message with file path and paragraph count

    Raises:
        ImportError: If reportlab is not installed
        TypeError: If parameters are wrong type
        ValueError: If file exists and skip_confirm=False, or paragraphs is empty

    Example:
        >>> paragraphs = ["Introduction", "Body text", "Conclusion"]
        >>> msg = create_pdf_from_text_list("/tmp/test.pdf", paragraphs, False)
        >>> "3 paragraphs" in msg
        True
    """
    if not HAS_REPORTLAB:
        raise ImportError(
            "reportlab is required for PDF creation. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(paragraphs, list):
        raise TypeError("paragraphs must be a list")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if not file_path.strip():
        raise ValueError("file_path cannot be empty")

    if not paragraphs:
        raise ValueError("paragraphs cannot be empty")

    # Validate all paragraphs are strings
    for i, para in enumerate(paragraphs):
        if not isinstance(para, str):
            raise TypeError(f"Paragraph at index {i} must be a string")

    # Check if file exists
    if os.path.exists(file_path) and not skip_confirm:
        raise ValueError(
            f"File already exists: {file_path}. Set skip_confirm=True to overwrite."
        )

    # Check parent directory
    parent_dir = os.path.dirname(file_path) or "."
    if not os.path.exists(parent_dir):
        raise FileNotFoundError(f"Parent directory does not exist: {parent_dir}")

    if not os.access(parent_dir, os.W_OK):
        raise PermissionError(f"Cannot write to directory: {parent_dir}")

    try:
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add each paragraph with spacing
        for para_text in paragraphs:
            if para_text.strip():
                para = Paragraph(para_text, styles["Normal"])
                story.append(para)
                story.append(Spacer(1, 0.2 * inch))

        doc.build(story)

        return f"Created PDF {file_path} with {len(paragraphs)} paragraphs"

    except Exception as e:
        raise ValueError(f"Failed to create PDF: {e}")


@strands_tool
def create_pdf_with_title(
    file_path: str, title: str, content: str, skip_confirm: bool
) -> str:
    """Create PDF with title and content.

    This function creates a PDF document with a title followed by content.
    The title uses a larger, bold font style.

    Args:
        file_path: Path where PDF will be created
        title: Document title text
        content: Body content text
        skip_confirm: If False, raises error if file exists; if True, overwrites

    Returns:
        Success message with file path

    Raises:
        ImportError: If reportlab is not installed
        TypeError: If parameters are wrong type
        ValueError: If file exists and skip_confirm=False, or title/content empty

    Example:
        >>> msg = create_pdf_with_title("/tmp/test.pdf", "Report", "Content", False)
        >>> "Created PDF" in msg
        True
    """
    if not HAS_REPORTLAB:
        raise ImportError(
            "reportlab is required for PDF creation. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(title, str):
        raise TypeError("title must be a string")

    if not isinstance(content, str):
        raise TypeError("content must be a string")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if not file_path.strip():
        raise ValueError("file_path cannot be empty")

    if not title.strip():
        raise ValueError("title cannot be empty")

    if not content.strip():
        raise ValueError("content cannot be empty")

    # Check if file exists
    if os.path.exists(file_path) and not skip_confirm:
        raise ValueError(
            f"File already exists: {file_path}. Set skip_confirm=True to overwrite."
        )

    # Check parent directory
    parent_dir = os.path.dirname(file_path) or "."
    if not os.path.exists(parent_dir):
        raise FileNotFoundError(f"Parent directory does not exist: {parent_dir}")

    if not os.access(parent_dir, os.W_OK):
        raise PermissionError(f"Cannot write to directory: {parent_dir}")

    try:
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add title
        title_para = Paragraph(title, styles["Title"])
        story.append(title_para)
        story.append(Spacer(1, 0.3 * inch))

        # Add content
        content_para = Paragraph(content, styles["Normal"])
        story.append(content_para)

        doc.build(story)

        file_size = os.path.getsize(file_path)
        return f"Created PDF {file_path} ({file_size} bytes)"

    except Exception as e:
        raise ValueError(f"Failed to create PDF: {e}")


@strands_tool
def create_pdf_with_metadata(
    file_path: str, content: str, metadata: dict[str, str], skip_confirm: bool
) -> str:
    """Create PDF with custom metadata.

    This function creates a PDF with specified metadata fields including
    author, title, subject, and creator.

    Args:
        file_path: Path where PDF will be created
        content: Text content for PDF
        metadata: Dictionary with metadata fields (author, title, subject, creator)
        skip_confirm: If False, raises error if file exists; if True, overwrites

    Returns:
        Success message with file path

    Raises:
        ImportError: If reportlab is not installed
        TypeError: If parameters are wrong type
        ValueError: If file exists and skip_confirm=False

    Example:
        >>> meta = {"author": "John Doe", "title": "Report"}
        >>> msg = create_pdf_with_metadata("/tmp/test.pdf", "Content", meta, False)
        >>> "Created PDF" in msg
        True
    """
    if not HAS_REPORTLAB:
        raise ImportError(
            "reportlab is required for PDF creation. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(content, str):
        raise TypeError("content must be a string")

    if not isinstance(metadata, dict):
        raise TypeError("metadata must be a dictionary")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if not file_path.strip():
        raise ValueError("file_path cannot be empty")

    if not content.strip():
        raise ValueError("content cannot be empty")

    # Validate metadata values are strings
    for key, value in metadata.items():
        if not isinstance(key, str):
            raise TypeError(f"Metadata key must be string, got {type(key)}")
        if not isinstance(value, str):
            raise TypeError(f"Metadata value must be string, got {type(value)}")

    # Check if file exists
    if os.path.exists(file_path) and not skip_confirm:
        raise ValueError(
            f"File already exists: {file_path}. Set skip_confirm=True to overwrite."
        )

    # Check parent directory
    parent_dir = os.path.dirname(file_path) or "."
    if not os.path.exists(parent_dir):
        raise FileNotFoundError(f"Parent directory does not exist: {parent_dir}")

    if not os.access(parent_dir, os.W_OK):
        raise PermissionError(f"Cannot write to directory: {parent_dir}")

    try:
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            author=metadata.get("author", ""),
            title=metadata.get("title", ""),
            subject=metadata.get("subject", ""),
            creator=metadata.get("creator", ""),
        )

        styles = getSampleStyleSheet()
        story = []

        # Add content
        para = Paragraph(content, styles["Normal"])
        story.append(para)

        doc.build(story)

        file_size = os.path.getsize(file_path)
        return f"Created PDF {file_path} with metadata ({file_size} bytes)"

    except Exception as e:
        raise ValueError(f"Failed to create PDF: {e}")


@strands_tool
def create_multi_page_pdf(
    file_path: str, pages: list[dict[str, str]], skip_confirm: bool
) -> str:
    """Create PDF with multiple pages.

    This function creates a PDF with multiple pages. Each page can have
    a title and content. Page breaks are inserted between pages.

    Args:
        file_path: Path where PDF will be created
        pages: List of page dictionaries, each with 'title' and 'content' keys
        skip_confirm: If False, raises error if file exists; if True, overwrites

    Returns:
        Success message with file path and page count

    Raises:
        ImportError: If reportlab is not installed
        TypeError: If parameters are wrong type
        ValueError: If file exists and skip_confirm=False, or pages invalid

    Example:
        >>> pages = [
        ...     {"title": "Page 1", "content": "First page"},
        ...     {"title": "Page 2", "content": "Second page"}
        ... ]
        >>> msg = create_multi_page_pdf("/tmp/test.pdf", pages, False)
        >>> "2 pages" in msg
        True
    """
    if not HAS_REPORTLAB:
        raise ImportError(
            "reportlab is required for PDF creation. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(pages, list):
        raise TypeError("pages must be a list")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if not file_path.strip():
        raise ValueError("file_path cannot be empty")

    if not pages:
        raise ValueError("pages cannot be empty")

    # Validate pages structure
    for i, page in enumerate(pages):
        if not isinstance(page, dict):
            raise TypeError(f"Page at index {i} must be a dictionary")
        if "title" not in page or "content" not in page:
            raise ValueError(f"Page at index {i} must have 'title' and 'content' keys")
        if not isinstance(page["title"], str):
            raise TypeError(f"Page {i} title must be a string")
        if not isinstance(page["content"], str):
            raise TypeError(f"Page {i} content must be a string")

    # Check if file exists
    if os.path.exists(file_path) and not skip_confirm:
        raise ValueError(
            f"File already exists: {file_path}. Set skip_confirm=True to overwrite."
        )

    # Check parent directory
    parent_dir = os.path.dirname(file_path) or "."
    if not os.path.exists(parent_dir):
        raise FileNotFoundError(f"Parent directory does not exist: {parent_dir}")

    if not os.access(parent_dir, os.W_OK):
        raise PermissionError(f"Cannot write to directory: {parent_dir}")

    try:
        from reportlab.platypus import PageBreak  # type: ignore[import-untyped]

        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add each page
        for i, page in enumerate(pages):
            # Add title if provided
            if page["title"].strip():
                title_para = Paragraph(page["title"], styles["Heading1"])
                story.append(title_para)
                story.append(Spacer(1, 0.2 * inch))

            # Add content if provided
            if page["content"].strip():
                content_para = Paragraph(page["content"], styles["Normal"])
                story.append(content_para)

            # Add page break except for last page
            if i < len(pages) - 1:
                story.append(PageBreak())

        doc.build(story)

        return f"Created PDF {file_path} with {len(pages)} pages"

    except Exception as e:
        raise ValueError(f"Failed to create PDF: {e}")


@strands_tool
def text_to_pdf(
    text_content: str, output_path: str, font_size: int, skip_confirm: bool
) -> str:
    """Convert plain text to PDF with specified font size.

    This function creates a PDF from plain text content with custom
    font size. Preserves line breaks from the input text.

    Args:
        text_content: Plain text content to convert
        output_path: Path where PDF will be created
        font_size: Font size in points (e.g., 12)
        skip_confirm: If False, raises error if file exists; if True, overwrites

    Returns:
        Success message with file path

    Raises:
        ImportError: If reportlab is not installed
        TypeError: If parameters are wrong type
        ValueError: If file exists and skip_confirm=False, or invalid font_size

    Example:
        >>> msg = text_to_pdf("Hello\\nWorld", "/tmp/test.pdf", 12, False)
        >>> "Created PDF" in msg
        True
    """
    if not HAS_REPORTLAB:
        raise ImportError(
            "reportlab is required for PDF creation. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(text_content, str):
        raise TypeError("text_content must be a string")

    if not isinstance(output_path, str):
        raise TypeError("output_path must be a string")

    if not isinstance(font_size, int):
        raise TypeError("font_size must be an integer")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if not text_content.strip():
        raise ValueError("text_content cannot be empty")

    if not output_path.strip():
        raise ValueError("output_path cannot be empty")

    if font_size < 6 or font_size > 72:
        raise ValueError("font_size must be between 6 and 72")

    # Check if file exists
    if os.path.exists(output_path) and not skip_confirm:
        raise ValueError(
            f"File already exists: {output_path}. Set skip_confirm=True to overwrite."
        )

    # Check parent directory
    parent_dir = os.path.dirname(output_path) or "."
    if not os.path.exists(parent_dir):
        raise FileNotFoundError(f"Parent directory does not exist: {parent_dir}")

    if not os.access(parent_dir, os.W_OK):
        raise PermissionError(f"Cannot write to directory: {parent_dir}")

    try:
        from reportlab.lib.styles import ParagraphStyle  # type: ignore[import-untyped]

        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()

        # Create custom style with specified font size
        custom_style = ParagraphStyle(
            "CustomStyle",
            parent=styles["Normal"],
            fontSize=font_size,
            leading=font_size * 1.2,  # Line height
        )

        story = []

        # Split text into paragraphs and add to story
        paragraphs = text_content.split("\n")
        for para_text in paragraphs:
            if para_text.strip():
                para = Paragraph(para_text, custom_style)
                story.append(para)
                story.append(Spacer(1, 0.1 * inch))

        doc.build(story)

        file_size = os.path.getsize(output_path)
        return f"Created PDF {output_path} ({file_size} bytes)"

    except Exception as e:
        raise ValueError(f"Failed to create PDF: {e}")
