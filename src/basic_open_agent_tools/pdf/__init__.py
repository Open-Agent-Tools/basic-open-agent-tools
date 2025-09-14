"""PDF processing tools."""

from .creator import merge_pdfs, text_to_pdf
from .reader import extract_text_from_pdf, get_pdf_info
from .manipulation import (
    split_pdf_by_pages, extract_pages_from_pdf,
    rotate_pdf_pages, add_watermark_to_pdf
)

__all__ = [
    # PDF reading
    "extract_text_from_pdf",
    "get_pdf_info",
    # PDF creation
    "text_to_pdf",
    "merge_pdfs",
    # PDF manipulation
    "split_pdf_by_pages",
    "extract_pages_from_pdf",
    "rotate_pdf_pages",
    "add_watermark_to_pdf",
]
