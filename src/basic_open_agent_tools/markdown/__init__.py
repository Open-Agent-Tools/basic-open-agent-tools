"""Markdown processing tools for AI agents.

This module provides Markdown (.md) operations including:
- Parsing and extracting structure, headings, links, code blocks, tables
- Generating Markdown files with frontmatter, tables, lists
- Converting between Markdown and other formats

All functions are designed for LLM agent compatibility with:
- JSON-serializable types only
- No default parameter values
- Consistent exception handling
- Comprehensive docstrings
- No external dependencies (stdlib only)
"""

# Generation functions
from .generation import (
    append_to_markdown,
    create_markdown_from_text,
    create_markdown_list,
    create_markdown_table,
    create_markdown_with_frontmatter,
    markdown_to_html_string,
)

# Parsing functions
from .parsing import (
    extract_markdown_code_blocks,
    extract_markdown_headings,
    extract_markdown_links,
    extract_markdown_tables,
    markdown_to_plain_text,
    parse_markdown_to_dict,
)

__all__: list[str] = [
    # Parsing functions (6)
    "parse_markdown_to_dict",
    "extract_markdown_headings",
    "extract_markdown_links",
    "extract_markdown_code_blocks",
    "extract_markdown_tables",
    "markdown_to_plain_text",
    # Generation functions (6)
    "create_markdown_from_text",
    "create_markdown_with_frontmatter",
    "create_markdown_table",
    "create_markdown_list",
    "append_to_markdown",
    "markdown_to_html_string",
]
