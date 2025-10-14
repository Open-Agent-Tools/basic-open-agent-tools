"""PDF processing tools for AI agents.

This module provides comprehensive PDF operations including:
- Reading and extracting text from PDFs
- Creating new PDF documents
- Manipulating existing PDFs (merge, split, rotate, etc.)

All functions are designed for LLM agent compatibility with:
- JSON-serializable types only
- No default parameter values
- Consistent exception handling
- Comprehensive docstrings
"""

# Parsing functions
# Creation functions
from .creation import (
    create_multi_page_pdf,
    create_pdf_from_text_list,
    create_pdf_with_metadata,
    create_pdf_with_title,
    create_simple_pdf,
    text_to_pdf,
)

# Manipulation functions
from .manipulation import (
    add_page_numbers,
    extract_pdf_pages,
    merge_pdfs,
    remove_pdf_pages,
    rotate_pdf_pages,
    split_pdf,
    watermark_pdf,
)
from .parsing import (
    extract_pdf_pages_to_text,
    extract_text_from_page,
    extract_text_from_pdf,
    get_pdf_info,
    get_pdf_metadata,
    get_pdf_page_count,
    search_pdf_text,
)

__all__: list[str] = [
    # Parsing functions (7)
    "extract_text_from_pdf",
    "extract_text_from_page",
    "get_pdf_metadata",
    "get_pdf_page_count",
    "extract_pdf_pages_to_text",
    "search_pdf_text",
    "get_pdf_info",
    # Creation functions (6)
    "create_simple_pdf",
    "create_pdf_from_text_list",
    "create_pdf_with_title",
    "create_pdf_with_metadata",
    "create_multi_page_pdf",
    "text_to_pdf",
    # Manipulation functions (7)
    "merge_pdfs",
    "split_pdf",
    "extract_pdf_pages",
    "rotate_pdf_pages",
    "remove_pdf_pages",
    "add_page_numbers",
    "watermark_pdf",
]
