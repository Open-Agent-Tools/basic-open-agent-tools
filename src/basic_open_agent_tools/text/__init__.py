"""Text tools for AI agents.

This module provides text processing and manipulation tools organized into logical submodules:

- processing: Core text cleaning, normalization, and formatting
"""

from .processing import (
    clean_whitespace,
    extract_sentences,
    join_with_oxford_comma,
    normalize_line_endings,
    normalize_unicode,
    smart_split_lines,
    strip_html_tags,
    to_camel_case,
    to_snake_case,
    to_title_case,
)

__all__: list[str] = [
    "clean_whitespace",
    "normalize_line_endings",
    "strip_html_tags",
    "normalize_unicode",
    "to_snake_case",
    "to_camel_case",
    "to_title_case",
    "smart_split_lines",
    "extract_sentences",
    "join_with_oxford_comma",
]
