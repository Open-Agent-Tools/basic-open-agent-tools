"""Markdown generation and creation functions for AI agents.

This module provides functions for creating and generating Markdown (.md) files.
"""

import os

from ..decorators import strands_tool

# Maximum file size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024


@strands_tool
def create_markdown_from_text(file_path: str, content: str, skip_confirm: bool) -> str:
    """Create simple Markdown file from text content.

    Args:
        file_path: Path for new Markdown file
        content: Markdown content
        skip_confirm: If False, raises error if file exists; if True, overwrites

    Returns:
        Success message with file path

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If file exists and skip_confirm is False
        PermissionError: If lacking write permission

    Example:
        >>> msg = create_markdown_from_text("/tmp/doc.md", "# Hello\n\nWorld", True)
        >>> "Created" in msg
        True
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(content, str):
        raise TypeError("content must be a string")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    # Check if file exists
    if os.path.exists(file_path) and not skip_confirm:
        raise ValueError(
            f"File already exists: {file_path}. Set skip_confirm=True to overwrite."
        )

    # Check parent directory exists
    parent_dir = os.path.dirname(file_path)
    if parent_dir and not os.path.exists(parent_dir):
        raise ValueError(f"Parent directory does not exist: {parent_dir}")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Created Markdown file at {file_path}"

    except PermissionError:
        raise PermissionError(f"Permission denied writing to: {file_path}")
    except Exception as e:
        raise ValueError(f"Failed to create Markdown file: {e}")


@strands_tool
def create_markdown_with_frontmatter(
    file_path: str, frontmatter: dict[str, str], content: str, skip_confirm: bool
) -> str:
    """Create Markdown file with YAML frontmatter.

    Args:
        file_path: Path for new Markdown file
        frontmatter: Dictionary of frontmatter key-value pairs
        content: Markdown content (after frontmatter)
        skip_confirm: If False, raises error if file exists; if True, overwrites

    Returns:
        Success message with file path

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If file exists and skip_confirm is False, or frontmatter invalid
        PermissionError: If lacking write permission

    Example:
        >>> fm = {'title': 'My Post', 'date': '2024-01-01'}
        >>> msg = create_markdown_with_frontmatter("/tmp/post.md", fm, "Content", True)
        >>> "Created" in msg
        True
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(frontmatter, dict):
        raise TypeError("frontmatter must be a dict")

    if not isinstance(content, str):
        raise TypeError("content must be a string")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    # Validate frontmatter keys and values are strings
    for key, value in frontmatter.items():
        if not isinstance(key, str):
            raise TypeError("All frontmatter keys must be strings")
        if not isinstance(value, str):
            raise TypeError("All frontmatter values must be strings")

    # Build frontmatter section
    frontmatter_lines = ["---"]
    for key, value in frontmatter.items():
        frontmatter_lines.append(f"{key}: {value}")
    frontmatter_lines.append("---")
    frontmatter_lines.append("")  # Blank line after frontmatter

    full_content = "\n".join(frontmatter_lines) + content

    return create_markdown_from_text(file_path, full_content, skip_confirm)


@strands_tool
def create_markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    """Generate Markdown table string from headers and rows.

    Args:
        headers: List of header strings
        rows: 2D list of row data

    Returns:
        Markdown table as string

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If headers empty or rows have inconsistent columns

    Example:
        >>> headers = ['Name', 'Age']
        >>> rows = [['Alice', '30'], ['Bob', '25']]
        >>> table = create_markdown_table(headers, rows)
        >>> '| Name | Age |' in table
        True
    """
    if not isinstance(headers, list):
        raise TypeError("headers must be a list")

    if not isinstance(rows, list):
        raise TypeError("rows must be a list")

    if not headers:
        raise ValueError("headers must not be empty")

    for header in headers:
        if not isinstance(header, str):
            raise TypeError("all headers must be strings")

    for row in rows:
        if not isinstance(row, list):
            raise TypeError("each row must be a list")
        if len(row) != len(headers):
            raise ValueError(
                f"Row has {len(row)} cells but {len(headers)} headers provided"
            )
        for cell in row:
            if not isinstance(cell, str):
                raise TypeError("all cells must be strings")

    # Build table
    lines = []

    # Header row
    header_line = "| " + " | ".join(headers) + " |"
    lines.append(header_line)

    # Separator row
    separator = "| " + " | ".join(["---"] * len(headers)) + " |"
    lines.append(separator)

    # Data rows
    for row in rows:
        row_line = "| " + " | ".join(row) + " |"
        lines.append(row_line)

    return "\n".join(lines)


@strands_tool
def create_markdown_list(items: list[str], ordered: bool) -> str:
    """Generate Markdown list string from items.

    Args:
        items: List of item strings
        ordered: If True, creates numbered list; if False, creates bullet list

    Returns:
        Markdown list as string

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If items empty

    Example:
        >>> items = ['First', 'Second', 'Third']
        >>> bullet_list = create_markdown_list(items, False)
        >>> '- First' in bullet_list
        True
        >>> ordered_list = create_markdown_list(items, True)
        >>> '1. First' in ordered_list
        True
    """
    if not isinstance(items, list):
        raise TypeError("items must be a list")

    if not isinstance(ordered, bool):
        raise TypeError("ordered must be a boolean")

    if not items:
        raise ValueError("items must not be empty")

    for item in items:
        if not isinstance(item, str):
            raise TypeError("all items must be strings")

    lines = []
    for i, item in enumerate(items, 1):
        if ordered:
            lines.append(f"{i}. {item}")
        else:
            lines.append(f"- {item}")

    return "\n".join(lines)


@strands_tool
def append_to_markdown(file_path: str, content: str, skip_confirm: bool) -> str:
    """Append content to existing Markdown file.

    Args:
        file_path: Path to existing Markdown file
        content: Content to append
        skip_confirm: Required for consistency (always appends, no overwrite)

    Returns:
        Success message

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large
        PermissionError: If lacking write permission

    Example:
        >>> msg = append_to_markdown("/tmp/doc.md", "\\n## New Section", True)
        >>> "Appended" in msg
        True
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(content, str):
        raise TypeError("content must be a string")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    # Check file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(content)

        return f"Appended content to {file_path}"

    except PermissionError:
        raise PermissionError(f"Permission denied writing to: {file_path}")
    except Exception as e:
        raise ValueError(f"Failed to append to Markdown file: {e}")


@strands_tool
def markdown_to_html_string(markdown_text: str) -> str:
    """Convert Markdown string to HTML string.

    Basic conversion supporting common Markdown elements:
    - Headings (# to ######)
    - Bold (**text** or __text__)
    - Italic (*text* or _text_)
    - Links [text](url)
    - Code blocks (```language...```)
    - Inline code (`code`)
    - Paragraphs

    Args:
        markdown_text: Markdown content as string

    Returns:
        HTML content as string

    Raises:
        TypeError: If parameters are wrong type

    Example:
        >>> html = markdown_to_html_string("# Hello\\n\\nWorld")
        >>> '<h1>Hello</h1>' in html
        True
    """
    if not isinstance(markdown_text, str):
        raise TypeError("markdown_text must be a string")

    import html as html_module
    import re

    # Escape HTML entities first
    text = html_module.escape(markdown_text)

    # Convert headings
    for level in range(6, 0, -1):
        pattern = r"^" + "#" * level + r"\s+(.+)$"
        text = re.sub(pattern, rf"<h{level}>\1</h{level}>", text, flags=re.MULTILINE)

    # Convert code blocks (before inline code)
    def replace_code_block(match: re.Match[str]) -> str:
        code = match.group(2)
        # Unescape for code blocks
        code = html_module.unescape(code)
        code = html_module.escape(code)
        return f"<pre><code>{code}</code></pre>"

    text = re.sub(r"```\w*\n(.*?)```", replace_code_block, text, flags=re.DOTALL)

    # Convert inline code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    # Convert bold (before italic to handle ***)
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)

    # Convert italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"_(.+?)_", r"<em>\1</em>", text)

    # Convert links
    text = re.sub(r"\[([^\]]+)\]\(([^\)]+)\)", r'<a href="\2">\1</a>', text)

    # Convert paragraphs (split by double newline)
    paragraphs = text.split("\n\n")
    html_paragraphs = []
    for para in paragraphs:
        para = para.strip()
        if para:
            # Don't wrap if already has HTML tags
            if not para.startswith("<"):
                para = f"<p>{para}</p>"
            html_paragraphs.append(para)

    return "\n".join(html_paragraphs)
