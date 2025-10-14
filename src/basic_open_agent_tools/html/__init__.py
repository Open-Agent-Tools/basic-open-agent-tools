"""HTML processing tools for AI agents."""

from .generation import (
    append_to_html_body,
    create_html_list,
    create_html_table,
    create_html_with_head,
    create_simple_html,
    html_to_markdown_file,
    markdown_to_html_file,
    prettify_html,
    wrap_in_html_tag,
)
from .parsing import (
    extract_html_headings,
    extract_html_images,
    extract_html_links,
    extract_html_metadata,
    extract_html_tables,
    extract_html_text,
    html_to_plain_text,
    parse_html_to_dict,
)

__all__: list[str] = [
    # Parsing functions (8)
    "parse_html_to_dict",
    "extract_html_text",
    "extract_html_links",
    "extract_html_images",
    "extract_html_tables",
    "extract_html_headings",
    "extract_html_metadata",
    "html_to_plain_text",
    # Generation functions (9)
    "create_simple_html",
    "create_html_with_head",
    "create_html_table",
    "create_html_list",
    "wrap_in_html_tag",
    "append_to_html_body",
    "markdown_to_html_file",
    "html_to_markdown_file",
    "prettify_html",
]
