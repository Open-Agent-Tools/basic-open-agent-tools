"""Text tools for AI agents.

This module provides text processing and manipulation tools organized into logical submodules:

- processing: Core text cleaning, normalization, and formatting
"""

from typing import List

# Import all functions from submodules
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

# Re-export all functions at module level for convenience
__all__: List[str] = [
    # Text cleaning and normalization
    "clean_whitespace",
    "normalize_line_endings",
    "strip_html_tags",
    "normalize_unicode",
    # Case conversion
    "to_snake_case",
    "to_camel_case",
    "to_title_case",
    # Text splitting and manipulation
    "smart_split_lines",
    "extract_sentences",
    "join_with_oxford_comma",
]
