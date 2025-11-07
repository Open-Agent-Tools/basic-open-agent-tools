"""PDF parsing and text extraction functions for AI agents.

This module provides functions for reading PDF files, extracting text content,
metadata, and searching within PDFs.
"""

import os

from ..decorators import strands_tool

try:
    from PyPDF2 import PdfReader  # type: ignore[import-untyped, import-not-found]

    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False


# Maximum file size to prevent memory exhaustion (100MB default)
MAX_PDF_FILE_SIZE = 100 * 1024 * 1024


@strands_tool
def extract_text_from_pdf(file_path: str) -> str:
    """Extract all text content from PDF file.

    This function reads a PDF file and extracts all text from every page,
    concatenating it into a single string. Requires PyPDF2 to be installed.

    Args:
        file_path: Path to PDF file to read

    Returns:
        Extracted text content from all pages concatenated together

    Raises:
        ImportError: If PyPDF2 is not installed
        FileNotFoundError: If file does not exist
        ValueError: If file is too large or not a valid PDF
        PermissionError: If file cannot be read
        TypeError: If file_path is not a string

    Example:
        >>> text = extract_text_from_pdf("/data/document.pdf")
        >>> "Introduction" in text
        True
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF operations. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not file_path.strip():
        raise ValueError("file_path cannot be empty")

    # Validate file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size > MAX_PDF_FILE_SIZE:
        raise ValueError(
            f"PDF file too large: {file_size} bytes "
            f"(maximum: {MAX_PDF_FILE_SIZE} bytes)"
        )

    # Check read permission
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Cannot read PDF file: {file_path}")

    try:
        reader = PdfReader(file_path)

        # Extract text from all pages
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        return "\n".join(text_parts)

    except Exception as e:
        raise ValueError(f"Failed to read PDF file {file_path}: {e}")


@strands_tool
def extract_text_from_page(file_path: str, page_number: int) -> str:
    """Extract text content from specific PDF page.

    This function extracts text from a single page in the PDF document.
    Pages are 0-indexed (first page is 0).

    Args:
        file_path: Path to PDF file to read
        page_number: Page number to extract (0-indexed)

    Returns:
        Extracted text content from the specified page

    Raises:
        ImportError: If PyPDF2 is not installed
        FileNotFoundError: If file does not exist
        ValueError: If page_number is invalid or file is malformed
        TypeError: If parameters are wrong type

    Example:
        >>> text = extract_text_from_page("/data/document.pdf", 0)
        >>> len(text) > 0
        True
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF operations. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(page_number, int):
        raise TypeError("page_number must be an integer")

    if page_number < 0:
        raise ValueError("page_number must be non-negative")

    # Validate file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size > MAX_PDF_FILE_SIZE:
        raise ValueError(
            f"PDF file too large: {file_size} bytes "
            f"(maximum: {MAX_PDF_FILE_SIZE} bytes)"
        )

    try:
        reader = PdfReader(file_path)

        if page_number >= len(reader.pages):
            raise ValueError(
                f"Page number {page_number} out of range "
                f"(PDF has {len(reader.pages)} pages)"
            )

        page = reader.pages[page_number]
        text = page.extract_text()

        return text if text else ""

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to extract text from page {page_number}: {e}")


@strands_tool
def get_pdf_metadata(file_path: str) -> dict[str, str]:
    """Extract metadata from PDF file.

    This function reads PDF metadata including author, title, subject,
    creator, producer, creation date, and modification date.

    Args:
        file_path: Path to PDF file to read

    Returns:
        Dictionary with metadata fields (all values are strings):
        - author: Document author
        - title: Document title
        - subject: Document subject
        - creator: Application that created the document
        - producer: PDF producer application
        - creation_date: Creation date/time
        - modification_date: Last modification date/time

    Raises:
        ImportError: If PyPDF2 is not installed
        FileNotFoundError: If file does not exist
        ValueError: If file is malformed
        TypeError: If file_path is not a string

    Example:
        >>> metadata = get_pdf_metadata("/data/document.pdf")
        >>> "author" in metadata
        True
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF operations. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not file_path.strip():
        raise ValueError("file_path cannot be empty")

    # Validate file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        reader = PdfReader(file_path)
        metadata = reader.metadata

        result: dict[str, str] = {
            "author": "",
            "title": "",
            "subject": "",
            "creator": "",
            "producer": "",
            "creation_date": "",
            "modification_date": "",
        }

        if metadata:
            # PyPDF2 metadata keys start with /
            result["author"] = str(metadata.get("/Author", ""))
            result["title"] = str(metadata.get("/Title", ""))
            result["subject"] = str(metadata.get("/Subject", ""))
            result["creator"] = str(metadata.get("/Creator", ""))
            result["producer"] = str(metadata.get("/Producer", ""))
            result["creation_date"] = str(metadata.get("/CreationDate", ""))
            result["modification_date"] = str(metadata.get("/ModDate", ""))

        return result

    except Exception as e:
        raise ValueError(f"Failed to extract metadata from {file_path}: {e}")


@strands_tool
def get_pdf_page_count(file_path: str) -> int:
    """Get total number of pages in PDF file.

    This function returns the page count of a PDF document.

    Args:
        file_path: Path to PDF file to read

    Returns:
        Number of pages in the PDF

    Raises:
        ImportError: If PyPDF2 is not installed
        FileNotFoundError: If file does not exist
        ValueError: If file is malformed
        TypeError: If file_path is not a string

    Example:
        >>> count = get_pdf_page_count("/data/document.pdf")
        >>> count > 0
        True
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF operations. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not file_path.strip():
        raise ValueError("file_path cannot be empty")

    # Validate file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        reader = PdfReader(file_path)
        return len(reader.pages)

    except Exception as e:
        raise ValueError(f"Failed to read PDF file {file_path}: {e}")


@strands_tool
def extract_pdf_pages_to_text(
    file_path: str, start_page: int, end_page: int
) -> list[str]:
    """Extract text from range of PDF pages.

    This function extracts text from a range of pages (inclusive).
    Pages are 0-indexed. Returns a list with one string per page.

    Args:
        file_path: Path to PDF file to read
        start_page: First page to extract (0-indexed, inclusive)
        end_page: Last page to extract (0-indexed, inclusive)

    Returns:
        List of text strings, one per page in the range

    Raises:
        ImportError: If PyPDF2 is not installed
        FileNotFoundError: If file does not exist
        ValueError: If page range is invalid or file is malformed
        TypeError: If parameters are wrong type

    Example:
        >>> texts = extract_pdf_pages_to_text("/data/document.pdf", 0, 2)
        >>> len(texts) == 3
        True
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF operations. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(start_page, int):
        raise TypeError("start_page must be an integer")

    if not isinstance(end_page, int):
        raise TypeError("end_page must be an integer")

    if start_page < 0:
        raise ValueError("start_page must be non-negative")

    if end_page < start_page:
        raise ValueError("end_page must be >= start_page")

    # Validate file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        reader = PdfReader(file_path)

        if end_page >= len(reader.pages):
            raise ValueError(
                f"end_page {end_page} out of range (PDF has {len(reader.pages)} pages)"
            )

        texts = []
        for page_num in range(start_page, end_page + 1):
            page = reader.pages[page_num]
            text = page.extract_text()
            texts.append(text if text else "")

        return texts

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to extract text from page range: {e}")


@strands_tool
def search_pdf_text(
    file_path: str, search_term: str, case_sensitive: bool
) -> list[dict[str, object]]:
    """Search for text in PDF and return matches with page numbers.

    This function searches all pages for the specified text and returns
    matches with context. Each match includes page number and surrounding text.

    Args:
        file_path: Path to PDF file to search
        search_term: Text to search for
        case_sensitive: Whether search should be case-sensitive

    Returns:
        List of match dictionaries, each containing:
        - page_number: Page where match was found (int, 0-indexed)
        - match_text: The matched text (str)
        - context: Surrounding text (str, up to 100 chars before/after)

    Raises:
        ImportError: If PyPDF2 is not installed
        FileNotFoundError: If file does not exist
        ValueError: If search_term is empty or file is malformed
        TypeError: If parameters are wrong type

    Example:
        >>> matches = search_pdf_text("/data/document.pdf", "Python", False)
        >>> len(matches) > 0
        True
        >>> matches[0]["page_number"] >= 0
        True
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF operations. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(search_term, str):
        raise TypeError("search_term must be a string")

    if not isinstance(case_sensitive, bool):
        raise TypeError("case_sensitive must be a boolean")

    if not search_term.strip():
        raise ValueError("search_term cannot be empty")

    # Validate file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        reader = PdfReader(file_path)
        matches: list[dict[str, object]] = []

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue

            # Prepare text for searching
            search_text = text if case_sensitive else text.lower()
            search_for = search_term if case_sensitive else search_term.lower()

            # Find all occurrences
            start = 0
            while True:
                pos = search_text.find(search_for, start)
                if pos == -1:
                    break

                # Extract context (100 chars before and after)
                context_start = max(0, pos - 100)
                context_end = min(len(text), pos + len(search_term) + 100)
                context = text[context_start:context_end]

                matches.append(
                    {
                        "page_number": page_num,
                        "match_text": text[pos : pos + len(search_term)],
                        "context": context,
                    }
                )

                start = pos + 1

        return matches

    except Exception as e:
        raise ValueError(f"Failed to search PDF file {file_path}: {e}")


@strands_tool
def get_pdf_info(file_path: str) -> dict[str, object]:
    """Get comprehensive information about PDF file.

    This function returns detailed information about the PDF including
    page count, file size, metadata, and encryption status.

    Args:
        file_path: Path to PDF file to analyze

    Returns:
        Dictionary with PDF information:
        - page_count: Number of pages (int)
        - file_size_bytes: File size in bytes (int)
        - encrypted: Whether PDF is encrypted (bool)
        - metadata: Dictionary of metadata fields (dict[str, str])

    Raises:
        ImportError: If PyPDF2 is not installed
        FileNotFoundError: If file does not exist
        ValueError: If file is malformed
        TypeError: If file_path is not a string

    Example:
        >>> info = get_pdf_info("/data/document.pdf")
        >>> info["page_count"] > 0
        True
        >>> isinstance(info["encrypted"], bool)
        True
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF operations. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not file_path.strip():
        raise ValueError("file_path cannot be empty")

    # Validate file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        reader = PdfReader(file_path)
        file_size = os.path.getsize(file_path)

        # Get metadata
        metadata_dict: dict[str, str] = {
            "author": "",
            "title": "",
            "subject": "",
            "creator": "",
            "producer": "",
            "creation_date": "",
            "modification_date": "",
        }

        if reader.metadata:
            metadata_dict["author"] = str(reader.metadata.get("/Author", ""))
            metadata_dict["title"] = str(reader.metadata.get("/Title", ""))
            metadata_dict["subject"] = str(reader.metadata.get("/Subject", ""))
            metadata_dict["creator"] = str(reader.metadata.get("/Creator", ""))
            metadata_dict["producer"] = str(reader.metadata.get("/Producer", ""))
            metadata_dict["creation_date"] = str(
                reader.metadata.get("/CreationDate", "")
            )
            metadata_dict["modification_date"] = str(
                reader.metadata.get("/ModDate", "")
            )

        return {
            "page_count": len(reader.pages),
            "file_size_bytes": file_size,
            "encrypted": reader.is_encrypted,
            "metadata": metadata_dict,
        }

    except Exception as e:
        raise ValueError(f"Failed to get PDF info from {file_path}: {e}")


@strands_tool
def preview_pdf_pages(file_path: str, num_pages: int) -> list[str]:
    """Get first N pages of PDF for preview without loading entire document.

    Extracts text from only the first few pages for quick preview.

    Args:
        file_path: Path to PDF file
        num_pages: Number of pages to preview from start

    Returns:
        List of text strings, one per page

    Raises:
        ImportError: If PyPDF2 is not installed
        FileNotFoundError: If file does not exist
        ValueError: If num_pages is negative or file is malformed
        TypeError: If parameters are wrong type

    Example:
        >>> pages = preview_pdf_pages("/data/document.pdf", 3)
        >>> len(pages) <= 3
        True
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF operations. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(num_pages, int):
        raise TypeError("num_pages must be an integer")

    if num_pages < 0:
        raise ValueError("num_pages must be non-negative")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)
        pages_to_read = min(num_pages, total_pages)

        texts = []
        for page_num in range(pages_to_read):
            page = reader.pages[page_num]
            text = page.extract_text()
            texts.append(text if text else "")

        return texts

    except Exception as e:
        raise ValueError(f"Failed to preview PDF pages: {e}")


@strands_tool
def sample_pdf_pages(
    file_path: str, sample_size: int, method: str
) -> list[dict[str, str]]:
    """Get representative sample of PDF pages without loading all pages.

    Samples pages using specified method for efficient document exploration.

    Args:
        file_path: Path to PDF file
        sample_size: Number of pages to sample
        method: Sampling method ("first", "random", "systematic")

    Returns:
        List of dicts with keys: page_number, text

    Raises:
        ImportError: If PyPDF2 is not installed
        FileNotFoundError: If file does not exist
        ValueError: If parameters invalid or file is malformed
        TypeError: If parameters are wrong type

    Example:
        >>> samples = sample_pdf_pages("/data/document.pdf", 5, "systematic")
        >>> len(samples) <= 5
        True
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF operations. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(sample_size, int):
        raise TypeError("sample_size must be an integer")

    if not isinstance(method, str):
        raise TypeError("method must be a string")

    if sample_size < 0:
        raise ValueError("sample_size must be non-negative")

    valid_methods = ["first", "random", "systematic"]
    if method not in valid_methods:
        raise ValueError(f"method must be one of: {', '.join(valid_methods)}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)

        if sample_size >= total_pages:
            # Return all pages if sample size >= total
            page_indices = list(range(total_pages))
        elif method == "first":
            page_indices = list(range(sample_size))
        elif method == "random":
            import random

            page_indices = sorted(random.sample(range(total_pages), sample_size))
        elif method == "systematic":
            # Evenly spaced pages
            step = total_pages / sample_size
            page_indices = [int(i * step) for i in range(sample_size)]
        else:
            page_indices = []

        samples = []
        for page_num in page_indices:
            page = reader.pages[page_num]
            text = page.extract_text()
            samples.append({"page_number": str(page_num), "text": text if text else ""})

        return samples

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to sample PDF pages: {e}")


@strands_tool
def get_pdf_page_sizes(file_path: str) -> list[dict[str, str]]:
    """Get dimensions of all PDF pages without loading text content.

    Extracts page dimensions efficiently without text extraction.

    Args:
        file_path: Path to PDF file

    Returns:
        List of dicts with keys: page_number, width, height (in points)

    Raises:
        ImportError: If PyPDF2 is not installed
        FileNotFoundError: If file does not exist
        ValueError: If file is malformed
        TypeError: If file_path is not a string

    Example:
        >>> sizes = get_pdf_page_sizes("/data/document.pdf")
        >>> sizes[0]['width']
        '612.0'
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF operations. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        reader = PdfReader(file_path)
        sizes = []

        for page_num, page in enumerate(reader.pages):
            mediabox = page.mediabox
            width = float(mediabox.width)
            height = float(mediabox.height)

            sizes.append(
                {
                    "page_number": str(page_num),
                    "width": str(width),
                    "height": str(height),
                }
            )

        return sizes

    except Exception as e:
        raise ValueError(f"Failed to get PDF page sizes: {e}")


@strands_tool
def get_pdf_outline(file_path: str) -> list[dict[str, str]]:
    """Extract PDF outline/bookmarks (table of contents) without loading text.

    Gets document structure via bookmarks/outline for navigation.

    Args:
        file_path: Path to PDF file

    Returns:
        List of dicts with keys: title, page_number, level

    Raises:
        ImportError: If PyPDF2 is not installed
        FileNotFoundError: If file does not exist
        ValueError: If file is malformed
        TypeError: If file_path is not a string

    Example:
        >>> outline = get_pdf_outline("/data/document.pdf")
        >>> outline[0]['title']
        'Chapter 1'
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF operations. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        reader = PdfReader(file_path)
        outline_items = []

        def extract_outline(items: list, level: int = 0) -> None:
            """Recursively extract outline items."""
            for item in items:
                if isinstance(item, list):
                    extract_outline(item, level + 1)
                else:
                    title = str(item.get("/Title", "Untitled"))
                    # Try to get page number
                    page_num = "unknown"
                    if "/Page" in item:
                        try:
                            page = item["/Page"]
                            if hasattr(page, "page_number"):
                                page_num = str(page.page_number)
                        except Exception:
                            pass

                    outline_items.append(
                        {
                            "title": title,
                            "page_number": page_num,
                            "level": str(level),
                        }
                    )

                    # Check for children
                    if hasattr(item, "children") and item.children:
                        extract_outline(item.children, level + 1)

        if reader.outline:
            extract_outline(reader.outline)

        return outline_items

    except Exception as e:
        raise ValueError(f"Failed to extract PDF outline: {e}")


@strands_tool
def count_pdf_text_occurrences(
    file_path: str, search_term: str, case_sensitive: bool
) -> dict[str, str]:
    """Count occurrences of text across PDF without loading all text.

    Counts matches efficiently by processing pages one at a time.

    Args:
        file_path: Path to PDF file
        search_term: Text to search for
        case_sensitive: Whether search should be case-sensitive

    Returns:
        Dict with keys: total_count, pages_with_matches

    Raises:
        ImportError: If PyPDF2 is not installed
        FileNotFoundError: If file does not exist
        ValueError: If search_term is empty or file is malformed
        TypeError: If parameters are wrong type

    Example:
        >>> result = count_pdf_text_occurrences("/data/document.pdf", "Python", False)
        >>> int(result['total_count']) >= 0
        True
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF operations. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(search_term, str):
        raise TypeError("search_term must be a string")

    if not isinstance(case_sensitive, bool):
        raise TypeError("case_sensitive must be a boolean")

    if not search_term.strip():
        raise ValueError("search_term cannot be empty")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        reader = PdfReader(file_path)
        total_count = 0
        pages_with_matches = 0

        search_for = search_term if case_sensitive else search_term.lower()

        for page in reader.pages:
            text = page.extract_text()
            if not text:
                continue

            search_text = text if case_sensitive else text.lower()
            page_count = search_text.count(search_for)

            if page_count > 0:
                total_count += page_count
                pages_with_matches += 1

        return {
            "total_count": str(total_count),
            "pages_with_matches": str(pages_with_matches),
        }

    except Exception as e:
        raise ValueError(f"Failed to count text occurrences: {e}")


@strands_tool
def get_pdf_page_stats(file_path: str, page_number: int) -> dict[str, str]:
    """Get statistics for specific PDF page without loading full document.

    Extracts stats for single page efficiently.

    Args:
        file_path: Path to PDF file
        page_number: Page number to analyze (0-indexed)

    Returns:
        Dict with keys: page_number, char_count, word_count, line_count

    Raises:
        ImportError: If PyPDF2 is not installed
        FileNotFoundError: If file does not exist
        ValueError: If page_number invalid or file is malformed
        TypeError: If parameters are wrong type

    Example:
        >>> stats = get_pdf_page_stats("/data/document.pdf", 0)
        >>> int(stats['word_count']) >= 0
        True
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF operations. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(page_number, int):
        raise TypeError("page_number must be an integer")

    if page_number < 0:
        raise ValueError("page_number must be non-negative")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        reader = PdfReader(file_path)

        if page_number >= len(reader.pages):
            raise ValueError(
                f"Page number {page_number} out of range (PDF has {len(reader.pages)} pages)"
            )

        page = reader.pages[page_number]
        text = page.extract_text()

        if not text:
            return {
                "page_number": str(page_number),
                "char_count": "0",
                "word_count": "0",
                "line_count": "0",
            }

        char_count = len(text)
        word_count = len(text.split())
        line_count = len(text.split("\n"))

        return {
            "page_number": str(page_number),
            "char_count": str(char_count),
            "word_count": str(word_count),
            "line_count": str(line_count),
        }

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to get page stats: {e}")


@strands_tool
def extract_pdf_page_snippets(
    file_path: str, page_number: int, snippet_length: int
) -> list[str]:
    """Extract small text snippets from PDF page for preview.

    Gets first N characters from page without loading full document.

    Args:
        file_path: Path to PDF file
        page_number: Page number to extract from (0-indexed)
        snippet_length: Maximum characters to extract

    Returns:
        List with single snippet string (truncated if longer than snippet_length)

    Raises:
        ImportError: If PyPDF2 is not installed
        FileNotFoundError: If file does not exist
        ValueError: If parameters invalid or file is malformed
        TypeError: If parameters are wrong type

    Example:
        >>> snippets = extract_pdf_page_snippets("/data/document.pdf", 0, 100)
        >>> len(snippets[0]) <= 100
        True
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF operations. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(page_number, int):
        raise TypeError("page_number must be an integer")

    if not isinstance(snippet_length, int):
        raise TypeError("snippet_length must be an integer")

    if page_number < 0:
        raise ValueError("page_number must be non-negative")

    if snippet_length < 0:
        raise ValueError("snippet_length must be non-negative")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        reader = PdfReader(file_path)

        if page_number >= len(reader.pages):
            raise ValueError(
                f"Page number {page_number} out of range (PDF has {len(reader.pages)} pages)"
            )

        page = reader.pages[page_number]
        text = page.extract_text()

        if not text:
            return [""]

        snippet = text[:snippet_length]
        if len(text) > snippet_length:
            snippet += "..."

        return [snippet]

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to extract page snippet: {e}")


@strands_tool
def filter_pdf_pages_by_text(
    file_path: str, search_term: str, case_sensitive: bool
) -> list[int]:
    """Find page numbers containing text without loading all page content.

    Efficiently identifies pages with matching text.

    Args:
        file_path: Path to PDF file
        search_term: Text to search for
        case_sensitive: Whether search should be case-sensitive

    Returns:
        List of page numbers (0-indexed) containing the search term

    Raises:
        ImportError: If PyPDF2 is not installed
        FileNotFoundError: If file does not exist
        ValueError: If search_term is empty or file is malformed
        TypeError: If parameters are wrong type

    Example:
        >>> pages = filter_pdf_pages_by_text("/data/document.pdf", "Python", False)
        >>> all(isinstance(p, int) for p in pages)
        True
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF operations. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(search_term, str):
        raise TypeError("search_term must be a string")

    if not isinstance(case_sensitive, bool):
        raise TypeError("case_sensitive must be a boolean")

    if not search_term.strip():
        raise ValueError("search_term cannot be empty")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        reader = PdfReader(file_path)
        matching_pages = []

        search_for = search_term if case_sensitive else search_term.lower()

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue

            search_text = text if case_sensitive else text.lower()
            if search_for in search_text:
                matching_pages.append(page_num)

        return matching_pages

    except Exception as e:
        raise ValueError(f"Failed to filter PDF pages: {e}")


@strands_tool
def get_pdf_text_length(file_path: str) -> dict[str, str]:
    """Get total text length across all pages without loading all text.

    Calculates length by processing pages one at a time.

    Args:
        file_path: Path to PDF file

    Returns:
        Dict with keys: total_chars, total_words, total_pages

    Raises:
        ImportError: If PyPDF2 is not installed
        FileNotFoundError: If file does not exist
        ValueError: If file is malformed
        TypeError: If file_path is not a string

    Example:
        >>> result = get_pdf_text_length("/data/document.pdf")
        >>> int(result['total_chars']) >= 0
        True
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF operations. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        reader = PdfReader(file_path)
        total_chars = 0
        total_words = 0

        for page in reader.pages:
            text = page.extract_text()
            if text:
                total_chars += len(text)
                total_words += len(text.split())

        return {
            "total_chars": str(total_chars),
            "total_words": str(total_words),
            "total_pages": str(len(reader.pages)),
        }

    except Exception as e:
        raise ValueError(f"Failed to get PDF text length: {e}")


@strands_tool
def check_pdf_has_text(file_path: str) -> dict[str, str]:
    """Check if PDF has extractable text vs image-only without loading all pages.

    Samples pages to determine if text is extractable.

    Args:
        file_path: Path to PDF file

    Returns:
        Dict with keys: has_text, pages_checked, pages_with_text

    Raises:
        ImportError: If PyPDF2 is not installed
        FileNotFoundError: If file does not exist
        ValueError: If file is malformed
        TypeError: If file_path is not a string

    Example:
        >>> result = check_pdf_has_text("/data/document.pdf")
        >>> result['has_text'] in ['True', 'False']
        True
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF operations. "
            "Install with: pip install basic-open-agent-tools[pdf]"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)

        # Check first 5 pages or all pages if less than 5
        pages_to_check = min(5, total_pages)
        pages_with_text = 0

        for page_num in range(pages_to_check):
            page = reader.pages[page_num]
            text = page.extract_text()
            if text and text.strip():
                pages_with_text += 1

        has_text = pages_with_text > 0

        return {
            "has_text": str(has_text),
            "pages_checked": str(pages_to_check),
            "pages_with_text": str(pages_with_text),
        }

    except Exception as e:
        raise ValueError(f"Failed to check PDF text: {e}")
