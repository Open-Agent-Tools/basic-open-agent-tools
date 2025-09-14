"""PDF creation and manipulation tools."""

import os
from typing import Dict, List, Union

try:
    from strands import tool as strands_tool
except ImportError:
    def strands_tool(func):
        """Fallback decorator when strands is not available."""
        return func

# Try to import PDF processing libraries
try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

from ..exceptions import BasicAgentToolsError


@strands_tool
def text_to_pdf(
    text: str,
    output_path: str,
    page_size: str = "letter",
    font_size: int = 12,
    margin_inches: float = 1.0
) -> Dict[str, Union[str, int, float]]:
    """
    Convert text to a PDF file.

    Args:
        text: Text content to convert
        output_path: Path for the output PDF file
        page_size: Page size ("letter", "a4")
        font_size: Font size in points (8-72)
        margin_inches: Margin size in inches (0.5-2.0)

    Returns:
        Dictionary with creation results

    Raises:
        BasicAgentToolsError: If parameters are invalid or creation fails
    """
    if not HAS_REPORTLAB:
        raise BasicAgentToolsError("reportlab package required for PDF creation - install with: pip install reportlab")

    if not isinstance(text, str):
        raise BasicAgentToolsError("Text must be a string")

    if not isinstance(output_path, str) or not output_path.strip():
        raise BasicAgentToolsError("Output path must be a non-empty string")

    if not isinstance(page_size, str) or page_size.lower() not in ["letter", "a4"]:
        raise BasicAgentToolsError("Page size must be 'letter' or 'a4'")

    if not isinstance(font_size, int) or font_size < 8 or font_size > 72:
        raise BasicAgentToolsError("Font size must be an integer between 8 and 72")

    if not isinstance(margin_inches, (int, float)) or margin_inches < 0.5 or margin_inches > 2.0:
        raise BasicAgentToolsError("Margin must be a number between 0.5 and 2.0 inches")

    output_path = output_path.strip()

    try:
        # Set up page size
        if page_size.lower() == "letter":
            page_width, page_height = letter
        else:  # a4
            page_width, page_height = A4

        margin = margin_inches * inch
        text_width = page_width - (2 * margin)
        text_height = page_height - (2 * margin)

        # Create PDF
        c = canvas.Canvas(output_path, pagesize=(page_width, page_height))
        c.setFont("Helvetica", font_size)

        # Calculate line height and lines per page
        line_height = font_size * 1.2  # 120% of font size
        lines_per_page = int(text_height / line_height)

        # Split text into lines
        lines = text.split('\n')

        # Handle text wrapping for long lines
        wrapped_lines = []
        chars_per_line = int(text_width / (font_size * 0.6))  # Approximate

        for line in lines:
            if len(line) <= chars_per_line:
                wrapped_lines.append(line)
            else:
                # Simple word wrapping
                words = line.split(' ')
                current_line = ""
                for word in words:
                    if len(current_line + " " + word) <= chars_per_line:
                        current_line = current_line + " " + word if current_line else word
                    else:
                        if current_line:
                            wrapped_lines.append(current_line)
                        current_line = word
                if current_line:
                    wrapped_lines.append(current_line)

        # Write text to PDF
        page_count = 0
        line_count = 0

        for i, line in enumerate(wrapped_lines):
            if line_count == 0:
                # Start new page
                page_count += 1
                y_position = page_height - margin - line_height

            # Write line
            c.drawString(margin, y_position, line)
            y_position -= line_height
            line_count += 1

            # Check if we need a new page
            if line_count >= lines_per_page or i == len(wrapped_lines) - 1:
                c.showPage()
                line_count = 0

        # Save the PDF
        c.save()

        # Get file size
        file_size = os.path.getsize(output_path)

        return {
            "output_path": output_path,
            "text_length": len(text),
            "lines_count": len(wrapped_lines),
            "pages_created": page_count,
            "page_size": page_size.lower(),
            "font_size": font_size,
            "margin_inches": margin_inches,
            "file_size_bytes": file_size,
            "creation_status": "success"
        }

    except Exception as e:
        raise BasicAgentToolsError(f"Failed to create PDF from text: {str(e)}")


@strands_tool
def merge_pdfs(input_paths: List[str], output_path: str) -> Dict[str, Union[str, int, List[str]]]:
    """
    Merge multiple PDF files into a single PDF.

    Args:
        input_paths: List of paths to PDF files to merge
        output_path: Path for the output merged PDF file

    Returns:
        Dictionary with merge results

    Raises:
        BasicAgentToolsError: If parameters are invalid or merge fails
    """
    if not HAS_PYPDF2:
        raise BasicAgentToolsError("PyPDF2 package required for PDF merging - install with: pip install PyPDF2")

    if not isinstance(input_paths, list) or len(input_paths) < 2:
        raise BasicAgentToolsError("Input paths must be a list with at least 2 PDF files")

    if not isinstance(output_path, str) or not output_path.strip():
        raise BasicAgentToolsError("Output path must be a non-empty string")

    output_path = output_path.strip()

    try:
        # Validate input files
        validated_paths = []
        total_input_pages = 0

        for path in input_paths:
            if not isinstance(path, str) or not path.strip():
                raise BasicAgentToolsError("All input paths must be non-empty strings")

            path = path.strip()

            if not os.path.exists(path):
                raise BasicAgentToolsError(f"Input PDF file not found: {path}")

            if not os.path.isfile(path):
                raise BasicAgentToolsError(f"Input path is not a file: {path}")

            # Test if file is a valid PDF by trying to read it
            with open(path, 'rb') as file:
                try:
                    reader = PyPDF2.PdfReader(file)
                    page_count = len(reader.pages)
                    total_input_pages += page_count
                    validated_paths.append(path)
                except Exception:
                    raise BasicAgentToolsError(f"Invalid or corrupted PDF file: {path}")

        # Create PDF merger
        merger = PyPDF2.PdfMerger()

        # Add all PDFs to merger
        for path in validated_paths:
            with open(path, 'rb') as file:
                merger.append(file)

        # Write merged PDF
        with open(output_path, 'wb') as output_file:
            merger.write(output_file)

        merger.close()

        # Get output file size
        output_size = os.path.getsize(output_path)

        # Calculate input file sizes
        input_sizes = [os.path.getsize(path) for path in validated_paths]
        total_input_size = sum(input_sizes)

        return {
            "output_path": output_path,
            "input_files_count": len(validated_paths),
            "input_files": validated_paths,
            "total_input_pages": total_input_pages,
            "total_input_size_bytes": total_input_size,
            "output_size_bytes": output_size,
            "compression_ratio": output_size / total_input_size if total_input_size > 0 else 1.0,
            "merge_status": "success"
        }

    except FileNotFoundError as e:
        raise BasicAgentToolsError(f"File not found: {str(e)}")
    except PermissionError as e:
        raise BasicAgentToolsError(f"Permission denied: {str(e)}")
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to merge PDFs: {str(e)}")
