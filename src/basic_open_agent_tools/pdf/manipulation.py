"""PDF manipulation and editing functions for AI agents.

This module provides functions for merging, splitting, rotating, and otherwise
manipulating existing PDF files.
"""

import os

from ..decorators import strands_tool

try:
    from PyPDF2 import (  # type: ignore[import-untyped, import-not-found]
        PdfReader,
        PdfWriter,
    )

    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    from reportlab.lib.pagesizes import (
        letter,  # type: ignore[import-untyped, import-not-found]
    )
    from reportlab.lib.units import (
        inch,  # type: ignore[import-untyped, import-not-found]
    )
    from reportlab.pdfgen import (
        canvas,  # type: ignore[import-untyped, import-not-found]
    )

    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


# Maximum file size for safety
MAX_PDF_FILE_SIZE = 100 * 1024 * 1024


@strands_tool
def merge_pdfs(input_paths: list[str], output_path: str, skip_confirm: bool) -> str:
    """Merge multiple PDF files into one.

    This function combines multiple PDF files into a single output file,
    preserving the order of input files.

    Args:
        input_paths: List of paths to PDF files to merge
        output_path: Path where merged PDF will be created
        skip_confirm: If False, raises error if file exists; if True, overwrites

    Returns:
        Success message with output path and total page count

    Raises:
        ImportError: If PyPDF2 is not installed
        TypeError: If parameters are wrong type
        ValueError: If input_paths is empty, files don't exist, or output exists
        FileNotFoundError: If any input file doesn't exist

    Example:
        >>> msg = merge_pdfs(["/tmp/a.pdf", "/tmp/b.pdf"], "/tmp/merged.pdf", False)
        >>> "Merged" in msg
        True
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF manipulation. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(input_paths, list):
        raise TypeError("input_paths must be a list")

    if not isinstance(output_path, str):
        raise TypeError("output_path must be a string")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if not input_paths:
        raise ValueError("input_paths cannot be empty")

    if not output_path.strip():
        raise ValueError("output_path cannot be empty")

    # Validate all input paths are strings
    for i, path in enumerate(input_paths):
        if not isinstance(path, str):
            raise TypeError(f"Input path at index {i} must be a string")

    # Check all input files exist
    for path in input_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Input PDF not found: {path}")

    # Check if output exists
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
        writer = PdfWriter()
        total_pages = 0

        # Add all pages from each input PDF
        for input_path in input_paths:
            reader = PdfReader(input_path)
            for page in reader.pages:
                writer.add_page(page)
                total_pages += 1

        # Write merged PDF
        with open(output_path, "wb") as output_file:
            writer.write(output_file)

        return f"Merged {len(input_paths)} PDFs into {output_path} ({total_pages} total pages)"

    except Exception as e:
        raise ValueError(f"Failed to merge PDFs: {e}")


@strands_tool
def split_pdf(input_path: str, output_dir: str, skip_confirm: bool) -> str:
    """Split PDF into individual page files.

    This function splits a PDF into separate files, one per page.
    Output files are named as: page_001.pdf, page_002.pdf, etc.

    Args:
        input_path: Path to PDF file to split
        output_dir: Directory where page files will be created
        skip_confirm: If False, raises error if output files exist; if True, overwrites

    Returns:
        Success message with output directory and page count

    Raises:
        ImportError: If PyPDF2 is not installed
        TypeError: If parameters are wrong type
        ValueError: If input doesn't exist or output files exist
        FileNotFoundError: If input file or output directory doesn't exist

    Example:
        >>> msg = split_pdf("/tmp/document.pdf", "/tmp/pages", False)
        >>> "Split" in msg
        True
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF manipulation. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(input_path, str):
        raise TypeError("input_path must be a string")

    if not isinstance(output_dir, str):
        raise TypeError("output_dir must be a string")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if not input_path.strip():
        raise ValueError("input_path cannot be empty")

    if not output_dir.strip():
        raise ValueError("output_dir cannot be empty")

    # Check input file exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input PDF not found: {input_path}")

    # Check output directory exists
    if not os.path.exists(output_dir):
        raise FileNotFoundError(f"Output directory does not exist: {output_dir}")

    if not os.access(output_dir, os.W_OK):
        raise PermissionError(f"Cannot write to directory: {output_dir}")

    try:
        reader = PdfReader(input_path)
        page_count = len(reader.pages)

        # Check if any output files would exist
        if not skip_confirm:
            for i in range(page_count):
                output_file = os.path.join(output_dir, f"page_{i + 1:03d}.pdf")
                if os.path.exists(output_file):
                    raise ValueError(
                        f"Output file already exists: {output_file}. "
                        "Set skip_confirm=True to overwrite."
                    )

        # Split into individual pages
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)

            output_file = os.path.join(output_dir, f"page_{i + 1:03d}.pdf")
            with open(output_file, "wb") as f:
                writer.write(f)

        return f"Split {input_path} into {page_count} pages in {output_dir}"

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to split PDF: {e}")


@strands_tool
def extract_pdf_pages(
    input_path: str, output_path: str, page_numbers: list[int], skip_confirm: bool
) -> str:
    """Extract specific pages to new PDF.

    This function creates a new PDF containing only the specified pages
    from the input PDF. Pages are 0-indexed.

    Args:
        input_path: Path to source PDF file
        output_path: Path where extracted PDF will be created
        page_numbers: List of page numbers to extract (0-indexed)
        skip_confirm: If False, raises error if file exists; if True, overwrites

    Returns:
        Success message with output path and extracted page count

    Raises:
        ImportError: If PyPDF2 is not installed
        TypeError: If parameters are wrong type
        ValueError: If page numbers invalid or output exists
        FileNotFoundError: If input file doesn't exist

    Example:
        >>> msg = extract_pdf_pages("/tmp/doc.pdf", "/tmp/extract.pdf", [0, 2], False)
        >>> "Extracted 2 pages" in msg
        True
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF manipulation. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(input_path, str):
        raise TypeError("input_path must be a string")

    if not isinstance(output_path, str):
        raise TypeError("output_path must be a string")

    if not isinstance(page_numbers, list):
        raise TypeError("page_numbers must be a list")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if not input_path.strip():
        raise ValueError("input_path cannot be empty")

    if not output_path.strip():
        raise ValueError("output_path cannot be empty")

    if not page_numbers:
        raise ValueError("page_numbers cannot be empty")

    # Validate all page numbers are integers
    for i, page_num in enumerate(page_numbers):
        if not isinstance(page_num, int):
            raise TypeError(f"Page number at index {i} must be an integer")
        if page_num < 0:
            raise ValueError(f"Page number at index {i} must be non-negative")

    # Check input file exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input PDF not found: {input_path}")

    # Check if output exists
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
        reader = PdfReader(input_path)
        writer = PdfWriter()

        # Validate page numbers are in range
        for page_num in page_numbers:
            if page_num >= len(reader.pages):
                raise ValueError(
                    f"Page number {page_num} out of range "
                    f"(PDF has {len(reader.pages)} pages)"
                )

        # Extract specified pages
        for page_num in page_numbers:
            writer.add_page(reader.pages[page_num])

        # Write output
        with open(output_path, "wb") as output_file:
            writer.write(output_file)

        return f"Extracted {len(page_numbers)} pages to {output_path}"

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to extract pages: {e}")


@strands_tool
def rotate_pdf_pages(
    input_path: str,
    output_path: str,
    rotation: int,
    page_numbers: list[int],
    skip_confirm: bool,
) -> str:
    """Rotate specified pages in PDF.

    This function rotates specified pages by the given angle.
    Valid rotation values are 90, 180, and 270 (clockwise).

    Args:
        input_path: Path to source PDF file
        output_path: Path where rotated PDF will be created
        rotation: Rotation angle (90, 180, or 270 degrees clockwise)
        page_numbers: List of page numbers to rotate (0-indexed)
        skip_confirm: If False, raises error if file exists; if True, overwrites

    Returns:
        Success message with output path and rotated page count

    Raises:
        ImportError: If PyPDF2 is not installed
        TypeError: If parameters are wrong type
        ValueError: If rotation invalid, page numbers invalid, or output exists

    Example:
        >>> msg = rotate_pdf_pages("/tmp/doc.pdf", "/tmp/rotated.pdf", 90, [0], False)
        >>> "Rotated 1 pages" in msg
        True
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF manipulation. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(input_path, str):
        raise TypeError("input_path must be a string")

    if not isinstance(output_path, str):
        raise TypeError("output_path must be a string")

    if not isinstance(rotation, int):
        raise TypeError("rotation must be an integer")

    if not isinstance(page_numbers, list):
        raise TypeError("page_numbers must be a list")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if rotation not in [90, 180, 270]:
        raise ValueError("rotation must be 90, 180, or 270")

    if not page_numbers:
        raise ValueError("page_numbers cannot be empty")

    # Validate page numbers
    for i, page_num in enumerate(page_numbers):
        if not isinstance(page_num, int):
            raise TypeError(f"Page number at index {i} must be an integer")
        if page_num < 0:
            raise ValueError(f"Page number at index {i} must be non-negative")

    # Check input file exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input PDF not found: {input_path}")

    # Check if output exists
    if os.path.exists(output_path) and not skip_confirm:
        raise ValueError(
            f"File already exists: {output_path}. Set skip_confirm=True to overwrite."
        )

    # Check parent directory
    parent_dir = os.path.dirname(output_path) or "."
    if not os.path.exists(parent_dir):
        raise FileNotFoundError(f"Parent directory does not exist: {parent_dir}")

    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()

        # Validate page numbers
        for page_num in page_numbers:
            if page_num >= len(reader.pages):
                raise ValueError(
                    f"Page number {page_num} out of range "
                    f"(PDF has {len(reader.pages)} pages)"
                )

        # Process all pages
        pages_to_rotate = set(page_numbers)
        for i, page in enumerate(reader.pages):
            if i in pages_to_rotate:
                # Rotate this page
                page.rotate(rotation)
            writer.add_page(page)

        # Write output
        with open(output_path, "wb") as output_file:
            writer.write(output_file)

        return f"Rotated {len(page_numbers)} pages in {output_path}"

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to rotate pages: {e}")


@strands_tool
def remove_pdf_pages(
    input_path: str, output_path: str, page_numbers: list[int], skip_confirm: bool
) -> str:
    """Remove specific pages from PDF.

    This function creates a new PDF with specified pages removed.
    Pages are 0-indexed.

    Args:
        input_path: Path to source PDF file
        output_path: Path where modified PDF will be created
        page_numbers: List of page numbers to remove (0-indexed)
        skip_confirm: If False, raises error if file exists; if True, overwrites

    Returns:
        Success message with output path and remaining page count

    Raises:
        ImportError: If PyPDF2 is not installed
        TypeError: If parameters are wrong type
        ValueError: If page numbers invalid or output exists
        FileNotFoundError: If input file doesn't exist

    Example:
        >>> msg = remove_pdf_pages("/tmp/doc.pdf", "/tmp/trimmed.pdf", [0, 2], False)
        >>> "Removed 2 pages" in msg
        True
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF manipulation. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(input_path, str):
        raise TypeError("input_path must be a string")

    if not isinstance(output_path, str):
        raise TypeError("output_path must be a string")

    if not isinstance(page_numbers, list):
        raise TypeError("page_numbers must be a list")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if not page_numbers:
        raise ValueError("page_numbers cannot be empty")

    # Validate page numbers
    for i, page_num in enumerate(page_numbers):
        if not isinstance(page_num, int):
            raise TypeError(f"Page number at index {i} must be an integer")
        if page_num < 0:
            raise ValueError(f"Page number at index {i} must be non-negative")

    # Check input file exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input PDF not found: {input_path}")

    # Check if output exists
    if os.path.exists(output_path) and not skip_confirm:
        raise ValueError(
            f"File already exists: {output_path}. Set skip_confirm=True to overwrite."
        )

    # Check parent directory
    parent_dir = os.path.dirname(output_path) or "."
    if not os.path.exists(parent_dir):
        raise FileNotFoundError(f"Parent directory does not exist: {parent_dir}")

    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()

        # Validate page numbers
        for page_num in page_numbers:
            if page_num >= len(reader.pages):
                raise ValueError(
                    f"Page number {page_num} out of range "
                    f"(PDF has {len(reader.pages)} pages)"
                )

        # Add all pages except removed ones
        pages_to_remove = set(page_numbers)
        for i, page in enumerate(reader.pages):
            if i not in pages_to_remove:
                writer.add_page(page)

        # Write output
        with open(output_path, "wb") as output_file:
            writer.write(output_file)

        remaining = len(reader.pages) - len(page_numbers)
        return f"Removed {len(page_numbers)} pages, {remaining} pages remain in {output_path}"

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to remove pages: {e}")


@strands_tool
def add_page_numbers(input_path: str, output_path: str, skip_confirm: bool) -> str:
    """Add page numbers to PDF.

    This function adds page numbers to the bottom center of each page.
    Page numbers are formatted as "Page X of Y".

    Args:
        input_path: Path to source PDF file
        output_path: Path where numbered PDF will be created
        skip_confirm: If False, raises error if file exists; if True, overwrites

    Returns:
        Success message with output path and page count

    Raises:
        ImportError: If PyPDF2 or reportlab is not installed
        TypeError: If parameters are wrong type
        ValueError: If output exists
        FileNotFoundError: If input file doesn't exist

    Example:
        >>> msg = add_page_numbers("/tmp/doc.pdf", "/tmp/numbered.pdf", False)
        >>> "Added page numbers" in msg
        True
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF manipulation. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not HAS_REPORTLAB:
        raise ImportError(
            "reportlab is required for PDF manipulation. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(input_path, str):
        raise TypeError("input_path must be a string")

    if not isinstance(output_path, str):
        raise TypeError("output_path must be a string")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    # Check input file exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input PDF not found: {input_path}")

    # Check if output exists
    if os.path.exists(output_path) and not skip_confirm:
        raise ValueError(
            f"File already exists: {output_path}. Set skip_confirm=True to overwrite."
        )

    # Check parent directory
    parent_dir = os.path.dirname(output_path) or "."
    if not os.path.exists(parent_dir):
        raise FileNotFoundError(f"Parent directory does not exist: {parent_dir}")

    try:
        import io

        reader = PdfReader(input_path)
        writer = PdfWriter()
        total_pages = len(reader.pages)

        for i, page in enumerate(reader.pages):
            # Create page number overlay
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)

            # Add page number at bottom center
            page_text = f"Page {i + 1} of {total_pages}"
            can.drawCentredString(letter[0] / 2, 0.5 * inch, page_text)
            can.save()

            # Merge overlay with original page
            packet.seek(0)
            overlay = PdfReader(packet)
            page.merge_page(overlay.pages[0])
            writer.add_page(page)

        # Write output
        with open(output_path, "wb") as output_file:
            writer.write(output_file)

        return f"Added page numbers to {total_pages} pages in {output_path}"

    except Exception as e:
        raise ValueError(f"Failed to add page numbers: {e}")


@strands_tool
def watermark_pdf(
    input_path: str, output_path: str, watermark_text: str, skip_confirm: bool
) -> str:
    """Add text watermark to all PDF pages.

    This function adds a diagonal text watermark across all pages.
    The watermark is semi-transparent and centered on each page.

    Args:
        input_path: Path to source PDF file
        output_path: Path where watermarked PDF will be created
        watermark_text: Text to use as watermark
        skip_confirm: If False, raises error if file exists; if True, overwrites

    Returns:
        Success message with output path and page count

    Raises:
        ImportError: If PyPDF2 or reportlab is not installed
        TypeError: If parameters are wrong type
        ValueError: If watermark_text empty or output exists
        FileNotFoundError: If input file doesn't exist

    Example:
        >>> msg = watermark_pdf("/tmp/doc.pdf", "/tmp/marked.pdf", "DRAFT", False)
        >>> "watermark" in msg
        True
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF manipulation. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not HAS_REPORTLAB:
        raise ImportError(
            "reportlab is required for PDF manipulation. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(input_path, str):
        raise TypeError("input_path must be a string")

    if not isinstance(output_path, str):
        raise TypeError("output_path must be a string")

    if not isinstance(watermark_text, str):
        raise TypeError("watermark_text must be a string")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if not watermark_text.strip():
        raise ValueError("watermark_text cannot be empty")

    # Check input file exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input PDF not found: {input_path}")

    # Check if output exists
    if os.path.exists(output_path) and not skip_confirm:
        raise ValueError(
            f"File already exists: {output_path}. Set skip_confirm=True to overwrite."
        )

    # Check parent directory
    parent_dir = os.path.dirname(output_path) or "."
    if not os.path.exists(parent_dir):
        raise FileNotFoundError(f"Parent directory does not exist: {parent_dir}")

    try:
        import io

        from reportlab.lib.colors import grey  # type: ignore[import-untyped]

        reader = PdfReader(input_path)
        writer = PdfWriter()

        for page in reader.pages:
            # Create watermark overlay
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)

            # Set watermark properties
            can.setFont("Helvetica-Bold", 60)
            can.setFillColor(grey, alpha=0.3)

            # Draw watermark diagonally across page
            can.saveState()
            can.translate(letter[0] / 2, letter[1] / 2)
            can.rotate(45)
            can.drawCentredString(0, 0, watermark_text)
            can.restoreState()

            can.save()

            # Merge watermark with page
            packet.seek(0)
            overlay = PdfReader(packet)
            page.merge_page(overlay.pages[0])
            writer.add_page(page)

        # Write output
        with open(output_path, "wb") as output_file:
            writer.write(output_file)

        return f"Added watermark to {len(reader.pages)} pages in {output_path}"

    except Exception as e:
        raise ValueError(f"Failed to add watermark: {e}")
