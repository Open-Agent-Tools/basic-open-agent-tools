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
    count_markdown_elements,
    extract_image_references,
    extract_markdown_code_blocks,
    extract_markdown_headings,
    extract_markdown_links,
    extract_markdown_section_range,
    extract_markdown_tables,
    filter_headings_by_level,
    get_markdown_frontmatter,
    get_markdown_info,
    get_markdown_section,
    get_markdown_structure,
    get_markdown_toc,
    markdown_to_plain_text,
    parse_definition_lists,
    parse_footnotes,
    parse_markdown_to_dict,
    parse_reference_links,
    parse_task_lists,
    preview_markdown_lines,
    search_markdown_headings,
)

__all__: list[str] = [
    # Parsing functions (21 - includes 10 token-saving inspection tools + 5 advanced)
    "parse_markdown_to_dict",
    "extract_markdown_headings",
    "extract_markdown_links",
    "extract_markdown_code_blocks",
    "extract_markdown_tables",
    "markdown_to_plain_text",
    # Token-saving inspection tools
    "get_markdown_info",
    "get_markdown_structure",
    "count_markdown_elements",
    "get_markdown_section",
    "search_markdown_headings",
    "preview_markdown_lines",
    "get_markdown_toc",
    "filter_headings_by_level",
    "get_markdown_frontmatter",
    "extract_markdown_section_range",
    # Advanced parsing features (Issue #30)
    "parse_reference_links",
    "parse_footnotes",
    "parse_definition_lists",
    "parse_task_lists",
    "extract_image_references",
    # Generation functions (6)
    "create_markdown_from_text",
    "create_markdown_with_frontmatter",
    "create_markdown_table",
    "create_markdown_list",
    "append_to_markdown",
    "markdown_to_html_string",
]
