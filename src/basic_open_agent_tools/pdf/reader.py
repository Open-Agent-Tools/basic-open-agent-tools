"""PDF reading and extraction tools."""

import os
from typing import Dict, List, Union

try:
    from strands import tool as strands_tool
except ImportError:

    def strands_tool(func):
        """Fallback decorator when strands is not available."""
        return func


# Try to import PDF processing library
try:
    import PyPDF2

    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

from ..exceptions import BasicAgentToolsError


@strands_tool
def extract_text_from_pdf(
    file_path: str, page_range: str = "all"
) -> Dict[str, Union[str, int, List[str]]]:
    """
    Extract text content from a PDF file.

    Args:
        file_path: Path to the PDF file
        page_range: Pages to extract ("all", "1", "1-3", "1,3,5")

    Returns:
        Dictionary with extracted text and metadata

    Raises:
        BasicAgentToolsError: If file is invalid or extraction fails
    """
    if not HAS_PYPDF2:
        raise BasicAgentToolsError(
            "PyPDF2 package required for PDF text extraction - install with: pip install PyPDF2"
        )

    if not isinstance(file_path, str) or not file_path.strip():
        raise BasicAgentToolsError("File path must be a non-empty string")

    if not isinstance(page_range, str):
        raise BasicAgentToolsError("Page range must be a string")

    file_path = file_path.strip()

    try:
        # Check if file exists
        if not os.path.exists(file_path):
            raise BasicAgentToolsError(f"PDF file not found: {file_path}")

        if not os.path.isfile(file_path):
            raise BasicAgentToolsError(f"Path is not a file: {file_path}")

        # Open and read PDF
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)

            # Parse page range
            if page_range.lower().strip() == "all":
                pages_to_extract = list(range(total_pages))
            else:
                pages_to_extract = _parse_page_range(page_range, total_pages)

            # Extract text from specified pages
            extracted_pages = []
            total_text = ""

            for page_num in pages_to_extract:
                if 0 <= page_num < total_pages:
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    extracted_pages.append(
                        {
                            "page_number": page_num + 1,  # 1-based for user display
                            "text": page_text,
                            "character_count": len(page_text),
                        }
                    )
                    total_text += page_text + "\n"

            return {
                "file_path": file_path,
                "total_pages": total_pages,
                "pages_extracted": len(extracted_pages),
                "page_range_requested": page_range,
                "total_text": total_text.strip(),
                "total_characters": len(total_text.strip()),
                "pages_detail": extracted_pages,
            }

    except FileNotFoundError:
        raise BasicAgentToolsError(f"PDF file not found: {file_path}")
    except PermissionError:
        raise BasicAgentToolsError(f"Permission denied accessing file: {file_path}")
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to extract text from PDF: {str(e)}")


@strands_tool
def get_pdf_info(file_path: str) -> Dict[str, Union[str, int, bool]]:
    """
    Get metadata and information about a PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        Dictionary with PDF information

    Raises:
        BasicAgentToolsError: If file is invalid or reading fails
    """
    if not HAS_PYPDF2:
        raise BasicAgentToolsError(
            "PyPDF2 package required for PDF information - install with: pip install PyPDF2"
        )

    if not isinstance(file_path, str) or not file_path.strip():
        raise BasicAgentToolsError("File path must be a non-empty string")

    file_path = file_path.strip()

    try:
        # Check if file exists
        if not os.path.exists(file_path):
            raise BasicAgentToolsError(f"PDF file not found: {file_path}")

        # Get file size
        file_size = os.path.getsize(file_path)

        # Open and analyze PDF
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)

            # Basic information
            total_pages = len(pdf_reader.pages)
            is_encrypted = pdf_reader.is_encrypted

            # Metadata (may not be available for all PDFs)
            metadata = pdf_reader.metadata

            result = {
                "file_path": file_path,
                "file_size_bytes": file_size,
                "total_pages": total_pages,
                "is_encrypted": is_encrypted,
                "has_metadata": metadata is not None,
            }

            # Extract metadata if available
            if metadata:
                # Common metadata fields
                metadata_fields = [
                    ("/Title", "title"),
                    ("/Author", "author"),
                    ("/Subject", "subject"),
                    ("/Creator", "creator"),
                    ("/Producer", "producer"),
                    ("/CreationDate", "creation_date"),
                    ("/ModDate", "modification_date"),
                ]

                for pdf_field, result_field in metadata_fields:
                    value = metadata.get(pdf_field, "")
                    if isinstance(value, str):
                        result[result_field] = value.strip()
                    else:
                        result[result_field] = str(value) if value else ""

            else:
                # Set empty metadata fields
                for _, field in [
                    ("/Title", "title"),
                    ("/Author", "author"),
                    ("/Subject", "subject"),
                    ("/Creator", "creator"),
                    ("/Producer", "producer"),
                    ("/CreationDate", "creation_date"),
                    ("/ModDate", "modification_date"),
                ]:
                    result[field] = ""

            return result

    except FileNotFoundError:
        raise BasicAgentToolsError(f"PDF file not found: {file_path}")
    except PermissionError:
        raise BasicAgentToolsError(f"Permission denied accessing file: {file_path}")
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to get PDF information: {str(e)}")


def _parse_page_range(page_range: str, total_pages: int) -> List[int]:
    """
    Parse page range string into list of 0-based page indices.

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
        parts = page_range.strip().split(",")

        for part in parts:
            part = part.strip()
            if "-" in part:
                # Range like "1-3"
                start, end = part.split("-", 1)
                start_page = int(start.strip()) - 1  # Convert to 0-based
                end_page = int(end.strip()) - 1  # Convert to 0-based

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
        return sorted(set(pages))

    except ValueError:
        raise BasicAgentToolsError(f"Invalid page range format: {page_range}")
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to parse page range: {str(e)}")
