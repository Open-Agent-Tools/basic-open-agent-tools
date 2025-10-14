"""Word document processing tools for AI agents.

This module provides comprehensive Word (.docx) operations including:
- Reading and extracting text, tables, and metadata
- Creating new Word documents
- Modifying existing documents
- Applying styles and formatting

All functions are designed for LLM agent compatibility with:
- JSON-serializable types only
- No default parameter values
- Consistent exception handling
- Comprehensive docstrings
"""

# Reading functions
from .reading import (
    extract_text_from_docx,
    get_docx_info,
    get_docx_metadata,
    get_docx_paragraphs,
    get_docx_tables,
    search_docx_text,
)

# Styling functions
from .styles import (
    add_page_break,
    apply_bold_to_paragraph,
    apply_heading_style,
    set_paragraph_alignment,
)

# Writing functions
from .writing import (
    add_paragraph_to_docx,
    add_table_to_docx,
    create_docx_from_paragraphs,
    create_docx_from_template,
    create_docx_with_headings,
    create_docx_with_title,
    create_simple_docx,
    docx_to_text,
)

__all__: list[str] = [
    # Reading functions (6)
    "extract_text_from_docx",
    "get_docx_paragraphs",
    "get_docx_tables",
    "get_docx_metadata",
    "search_docx_text",
    "get_docx_info",
    # Writing functions (8)
    "create_simple_docx",
    "create_docx_from_paragraphs",
    "create_docx_with_title",
    "add_paragraph_to_docx",
    "create_docx_with_headings",
    "add_table_to_docx",
    "create_docx_from_template",
    "docx_to_text",
    # Styling functions (4)
    "apply_heading_style",
    "apply_bold_to_paragraph",
    "set_paragraph_alignment",
    "add_page_break",
]
