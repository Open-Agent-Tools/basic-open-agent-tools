"""Advanced PDF manipulation tools."""

import os
from typing import Dict, List, Union, Optional

try:
    from strands import tool as strands_tool
except ImportError:
    def strands_tool(func):
        """Fallback decorator when strands is not available."""
        return func

# Try to import PDF processing libraries
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.pdfgen import canvas
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

from ..exceptions import BasicAgentToolsError


@strands_tool
def split_pdf_by_pages(input_path: str, pages_per_file: int, output_prefix: str = None) -> Dict[str, Union[str, int, List[str]]]:
    """
    Split a PDF into multiple smaller PDFs based on page count.

    Args:
        input_path: Path to input PDF
        pages_per_file: Number of pages per output file
        output_prefix: Prefix for output files (defaults to input filename)

    Returns:
        Dictionary with split results

    Raises:
        BasicAgentToolsError: If splitting fails
    """
    if not HAS_PYPDF2:
        raise BasicAgentToolsError("PyPDF2 package required for PDF splitting - install with: pip install PyPDF2")

    if not isinstance(input_path, str) or not input_path.strip():
        raise BasicAgentToolsError("Input path must be a non-empty string")

    if not isinstance(pages_per_file, int) or pages_per_file < 1:
        raise BasicAgentToolsError("Pages per file must be a positive integer")

    input_path = input_path.strip()

    if not os.path.exists(input_path):
        raise BasicAgentToolsError(f"Input PDF not found: {input_path}")

    try:
        # Determine output prefix
        if output_prefix is None:
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_dir = os.path.dirname(input_path)
            output_prefix = os.path.join(output_dir, base_name)

        output_files = []

        with open(input_path, 'rb') as input_file:
            pdf_reader = PyPDF2.PdfReader(input_file)
            total_pages = len(pdf_reader.pages)

            if total_pages == 0:
                raise BasicAgentToolsError("PDF contains no pages")

            files_created = 0
            current_page = 0

            while current_page < total_pages:
                # Create a new PDF writer for this chunk
                pdf_writer = PyPDF2.PdfWriter()

                # Add pages to this chunk
                pages_in_chunk = 0
                while current_page < total_pages and pages_in_chunk < pages_per_file:
                    pdf_writer.add_page(pdf_reader.pages[current_page])
                    current_page += 1
                    pages_in_chunk += 1

                # Write the chunk to file
                output_filename = f"{output_prefix}_part_{files_created + 1:03d}.pdf"
                with open(output_filename, 'wb') as output_file:
                    pdf_writer.write(output_file)

                output_files.append(output_filename)
                files_created += 1

        return {
            "input_path": input_path,
            "total_pages": total_pages,
            "pages_per_file": pages_per_file,
            "files_created": files_created,
            "output_files": output_files,
            "split_status": "success"
        }

    except Exception as e:
        raise BasicAgentToolsError(f"Failed to split PDF: {str(e)}")


@strands_tool
def extract_pages_from_pdf(input_path: str, page_range: str, output_path: str) -> Dict[str, Union[str, int]]:
    """
    Extract specific pages from a PDF to create a new PDF.

    Args:
        input_path: Path to input PDF
        page_range: Page range (e.g., "1-5", "1,3,5", "all")
        output_path: Path for extracted pages PDF

    Returns:
        Dictionary with extraction results

    Raises:
        BasicAgentToolsError: If extraction fails
    """
    if not HAS_PYPDF2:
        raise BasicAgentToolsError("PyPDF2 package required for PDF page extraction - install with: pip install PyPDF2")

    if not isinstance(input_path, str) or not input_path.strip():
        raise BasicAgentToolsError("Input path must be a non-empty string")

    if not isinstance(page_range, str) or not page_range.strip():
        raise BasicAgentToolsError("Page range must be a non-empty string")

    if not isinstance(output_path, str) or not output_path.strip():
        raise BasicAgentToolsError("Output path must be a non-empty string")

    input_path = input_path.strip()
    output_path = output_path.strip()
    page_range = page_range.strip()

    if not os.path.exists(input_path):
        raise BasicAgentToolsError(f"Input PDF not found: {input_path}")

    try:
        with open(input_path, 'rb') as input_file:
            pdf_reader = PyPDF2.PdfReader(input_file)
            total_pages = len(pdf_reader.pages)

            # Parse page range
            if page_range.lower() == "all":
                pages_to_extract = list(range(total_pages))
            else:
                pages_to_extract = _parse_page_range_for_manipulation(page_range, total_pages)

            # Create new PDF with extracted pages
            pdf_writer = PyPDF2.PdfWriter()

            for page_index in pages_to_extract:
                if 0 <= page_index < total_pages:
                    pdf_writer.add_page(pdf_reader.pages[page_index])

            # Write extracted pages
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)

            output_size = os.path.getsize(output_path)

        return {
            "input_path": input_path,
            "output_path": output_path,
            "total_pages_in_input": total_pages,
            "pages_extracted": len(pages_to_extract),
            "page_range_requested": page_range,
            "output_file_size_bytes": output_size,
            "extraction_status": "success"
        }

    except Exception as e:
        raise BasicAgentToolsError(f"Failed to extract pages from PDF: {str(e)}")


@strands_tool
def rotate_pdf_pages(input_path: str, rotation_angle: int, page_range: str = "all", output_path: str = None) -> Dict[str, Union[str, int]]:
    """
    Rotate pages in a PDF document.

    Args:
        input_path: Path to input PDF
        rotation_angle: Rotation angle (90, 180, 270, -90, -180, -270)
        page_range: Pages to rotate (defaults to "all")
        output_path: Path for rotated PDF (defaults to input_rotated.pdf)

    Returns:
        Dictionary with rotation results

    Raises:
        BasicAgentToolsError: If rotation fails
    """
    if not HAS_PYPDF2:
        raise BasicAgentToolsError("PyPDF2 package required for PDF rotation - install with: pip install PyPDF2")

    if not isinstance(input_path, str) or not input_path.strip():
        raise BasicAgentToolsError("Input path must be a non-empty string")

    if not isinstance(rotation_angle, int) or rotation_angle not in [90, 180, 270, -90, -180, -270]:
        raise BasicAgentToolsError("Rotation angle must be one of: 90, 180, 270, -90, -180, -270")

    input_path = input_path.strip()

    if not os.path.exists(input_path):
        raise BasicAgentToolsError(f"Input PDF not found: {input_path}")

    if output_path is None:
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}_rotated.pdf"
    elif not isinstance(output_path, str) or not output_path.strip():
        raise BasicAgentToolsError("Output path must be a non-empty string")
    else:
        output_path = output_path.strip()

    try:
        with open(input_path, 'rb') as input_file:
            pdf_reader = PyPDF2.PdfReader(input_file)
            total_pages = len(pdf_reader.pages)

            # Parse page range
            if page_range.lower().strip() == "all":
                pages_to_rotate = list(range(total_pages))
            else:
                pages_to_rotate = _parse_page_range_for_manipulation(page_range, total_pages)

            # Create new PDF with rotated pages
            pdf_writer = PyPDF2.PdfWriter()

            for i in range(total_pages):
                page = pdf_reader.pages[i]
                if i in pages_to_rotate:
                    page = page.rotate(rotation_angle)
                pdf_writer.add_page(page)

            # Write rotated PDF
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)

            output_size = os.path.getsize(output_path)

        return {
            "input_path": input_path,
            "output_path": output_path,
            "total_pages": total_pages,
            "pages_rotated": len(pages_to_rotate),
            "rotation_angle": rotation_angle,
            "page_range": page_range,
            "output_file_size_bytes": output_size,
            "rotation_status": "success"
        }

    except Exception as e:
        raise BasicAgentToolsError(f"Failed to rotate PDF pages: {str(e)}")


@strands_tool
def add_watermark_to_pdf(input_path: str, watermark_text: str, output_path: str = None, opacity: float = 0.3) -> Dict[str, Union[str, int, float]]:
    """
    Add a text watermark to all pages of a PDF.

    Args:
        input_path: Path to input PDF
        watermark_text: Text to use as watermark
        output_path: Path for watermarked PDF (defaults to input_watermarked.pdf)
        opacity: Watermark opacity (0.0 to 1.0)

    Returns:
        Dictionary with watermarking results

    Raises:
        BasicAgentToolsError: If watermarking fails
    """
    if not HAS_REPORTLAB or not HAS_PYPDF2:
        raise BasicAgentToolsError("Both reportlab and PyPDF2 packages required for watermarking - install with: pip install reportlab PyPDF2")

    if not isinstance(input_path, str) or not input_path.strip():
        raise BasicAgentToolsError("Input path must be a non-empty string")

    if not isinstance(watermark_text, str) or not watermark_text.strip():
        raise BasicAgentToolsError("Watermark text must be a non-empty string")

    if not isinstance(opacity, (int, float)) or opacity < 0.0 or opacity > 1.0:
        raise BasicAgentToolsError("Opacity must be a number between 0.0 and 1.0")

    input_path = input_path.strip()
    watermark_text = watermark_text.strip()

    if not os.path.exists(input_path):
        raise BasicAgentToolsError(f"Input PDF not found: {input_path}")

    if output_path is None:
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}_watermarked.pdf"
    elif not isinstance(output_path, str) or not output_path.strip():
        raise BasicAgentToolsError("Output path must be a non-empty string")
    else:
        output_path = output_path.strip()

    try:
        import tempfile
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter

        # Create temporary watermark PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            watermark_path = temp_file.name

        # Create watermark PDF
        c = canvas.Canvas(watermark_path, pagesize=letter)
        width, height = letter

        # Set watermark properties
        c.setFillColorRGB(0.5, 0.5, 0.5)  # Gray color
        c.setFont("Helvetica-Bold", 50)

        # Add diagonal watermark text
        c.saveState()
        c.translate(width/2, height/2)
        c.rotate(45)  # Diagonal angle
        c.drawCentredText(0, 0, watermark_text)
        c.restoreState()
        c.showPage()
        c.save()

        # Apply watermark to input PDF
        with open(input_path, 'rb') as input_file:
            with open(watermark_path, 'rb') as watermark_file:
                pdf_reader = PyPDF2.PdfReader(input_file)
                watermark_reader = PyPDF2.PdfReader(watermark_file)
                pdf_writer = PyPDF2.PdfWriter()

                watermark_page = watermark_reader.pages[0]

                pages_watermarked = 0
                for page in pdf_reader.pages:
                    # Merge watermark with each page
                    page.merge_page(watermark_page)
                    pdf_writer.add_page(page)
                    pages_watermarked += 1

                # Write watermarked PDF
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)

        # Clean up temporary file
        try:
            os.unlink(watermark_path)
        except:
            pass  # Best effort cleanup

        output_size = os.path.getsize(output_path)

        return {
            "input_path": input_path,
            "output_path": output_path,
            "watermark_text": watermark_text,
            "pages_watermarked": pages_watermarked,
            "opacity": opacity,
            "output_file_size_bytes": output_size,
            "watermarking_status": "success"
        }

    except Exception as e:
        # Clean up on error
        try:
            os.unlink(watermark_path)
        except:
            pass
        raise BasicAgentToolsError(f"Failed to add watermark to PDF: {str(e)}")


def _parse_page_range_for_manipulation(page_range: str, total_pages: int) -> List[int]:
    """
    Parse page range string into list of 0-based page indices for PDF manipulation.

    Args:
        page_range: Range specification like "1", "1-3", "1,3,5"
        total_pages: Total number of pages in document

    Returns:
        List of 0-based page indices

    Raises:
        BasicAgentToolsError: If range is invalid
    """
    try:
        pages = []
        parts = page_range.strip().split(',')

        for part in parts:
            part = part.strip()
            if '-' in part:
                # Range like "1-3"
                start, end = part.split('-', 1)
                start_page = int(start.strip()) - 1  # Convert to 0-based
                end_page = int(end.strip()) - 1      # Convert to 0-based

                if start_page < 0 or end_page >= total_pages or start_page > end_page:
                    raise BasicAgentToolsError(f"Invalid page range: {part}")

                pages.extend(range(start_page, end_page + 1))
            else:
                # Single page
                page_num = int(part) - 1  # Convert to 0-based
                if page_num < 0 or page_num >= total_pages:
                    raise BasicAgentToolsError(f"Invalid page number: {int(part)}")
                pages.append(page_num)

        # Remove duplicates and sort
        return sorted(list(set(pages)))

    except ValueError:
        raise BasicAgentToolsError(f"Invalid page range format: {page_range}")
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to parse page range: {str(e)}")