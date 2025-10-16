"""HTML generation and creation functions for AI agents."""

import os
import re

from ..decorators import strands_tool

MAX_FILE_SIZE = 10 * 1024 * 1024


@strands_tool
def create_simple_html(
    file_path: str, title: str, content: str, skip_confirm: bool
) -> str:
    """Create simple HTML page.


    Args:
        file_path: Path for new HTML file
        title: Page title
        content: Body content (can include HTML tags)
        skip_confirm: If False, raises error if file exists

    Returns:
        Success message

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If file exists and skip_confirm is False

    Example:
        >>> msg = create_simple_html("/tmp/page.html", "Title", "<p>Content</p>", True)
        >>> "Created" in msg
        True
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(title, str):
        raise TypeError("title must be a string")
    if not isinstance(content, str):
        raise TypeError("content must be a string")
    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if os.path.exists(file_path) and not skip_confirm:
        raise ValueError(
            f"File already exists: {file_path}. Set skip_confirm=True to overwrite."
        )

    parent_dir = os.path.dirname(file_path)
    if parent_dir and not os.path.exists(parent_dir):
        raise ValueError(f"Parent directory does not exist: {parent_dir}")

    try:
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
</head>
<body>
{content}
</body>
</html>"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return f"Created HTML file at {file_path}"

    except PermissionError:
        raise PermissionError(f"Permission denied writing to: {file_path}")
    except Exception as e:
        raise ValueError(f"Failed to create HTML file: {e}")


@strands_tool
def create_html_with_head(
    file_path: str, head: dict[str, str], body: str, skip_confirm: bool
) -> str:
    """Create HTML with custom head tags.

    Args:
        file_path: Path for new HTML file
        head: Dict with 'title' and optional 'meta_*' keys
        body: Body content
        skip_confirm: If False, raises error if file exists

    Returns:
        Success message

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If file exists and skip_confirm is False or head invalid

    Example:
        >>> head = {'title': 'Page', 'meta_description': 'Desc'}
        >>> msg = create_html_with_head("/tmp/page.html", head, "<p>Content</p>", True)
        >>> "Created" in msg
        True
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(head, dict):
        raise TypeError("head must be a dict")
    if not isinstance(body, str):
        raise TypeError("body must be a string")
    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    title = head.get("title", "")
    if not title:
        raise ValueError("head must contain 'title' key")

    if os.path.exists(file_path) and not skip_confirm:
        raise ValueError(
            f"File already exists: {file_path}. Set skip_confirm=True to overwrite."
        )

    try:
        meta_tags = []
        for key, value in head.items():
            if key.startswith("meta_"):
                meta_name = key[5:]
                meta_tags.append(f'    <meta name="{meta_name}" content="{value}">')

        meta_section = "\n".join(meta_tags) if meta_tags else ""

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
{meta_section}
</head>
<body>
{body}
</body>
</html>"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return f"Created HTML file at {file_path}"

    except Exception as e:
        raise ValueError(f"Failed to create HTML file: {e}")


@strands_tool
def create_html_table(headers: list[str], rows: list[list[str]]) -> str:
    """Generate HTML table string.

    Args:
        headers: List of header strings
        rows: 2D list of row data

    Returns:
        HTML table as string

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If headers empty or rows have inconsistent columns

    Example:
        >>> table = create_html_table(['Name', 'Age'], [['Alice', '30']])
        >>> '<table>' in table
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

    lines = ["<table>", "  <thead>", "    <tr>"]
    for header in headers:
        lines.append(f"      <th>{header}</th>")
    lines.extend(["    </tr>", "  </thead>", "  <tbody>"])

    for row in rows:
        lines.append("    <tr>")
        for cell in row:
            lines.append(f"      <td>{cell}</td>")
        lines.append("    </tr>")

    lines.extend(["  </tbody>", "</table>"])
    return "\n".join(lines)


@strands_tool
def create_html_list(items: list[str], ordered: bool) -> str:
    """Generate HTML list string.

    Args:
        items: List of item strings
        ordered: If True, creates <ol>; if False, creates <ul>

    Returns:
        HTML list as string

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If items empty

    Example:
        >>> list_html = create_html_list(['First', 'Second'], False)
        >>> '<ul>' in list_html
        True
    """
    if not isinstance(items, list):
        raise TypeError("items must be a list")
    if not isinstance(ordered, bool):
        raise TypeError("ordered must be a boolean")
    if not items:
        raise ValueError("items must not be empty")

    tag = "ol" if ordered else "ul"
    lines = [f"<{tag}>"]
    for item in items:
        if not isinstance(item, str):
            raise TypeError("all items must be strings")
        lines.append(f"  <li>{item}</li>")
    lines.append(f"</{tag}>")

    return "\n".join(lines)


@strands_tool
def wrap_in_html_tag(content: str, tag: str, attributes: dict[str, str]) -> str:
    """Wrap content in HTML tag with attributes.

    Args:
        content: Content to wrap
        tag: Tag name (e.g., 'div', 'p', 'span')
        attributes: Dictionary of attribute name-value pairs

    Returns:
        HTML string with wrapped content

    Raises:
        TypeError: If parameters are wrong type

    Example:
        >>> html = wrap_in_html_tag('Text', 'div', {'class': 'container'})
        >>> html
        '<div class="container">Text</div>'
    """
    if not isinstance(content, str):
        raise TypeError("content must be a string")
    if not isinstance(tag, str):
        raise TypeError("tag must be a string")
    if not isinstance(attributes, dict):
        raise TypeError("attributes must be a dict")

    attrs = []
    for key, value in attributes.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError("all attribute keys and values must be strings")
        attrs.append(f'{key}="{value}"')

    attr_str = " " + " ".join(attrs) if attrs else ""
    return f"<{tag}{attr_str}>{content}</{tag}>"


@strands_tool
def append_to_html_body(file_path: str, content: str, skip_confirm: bool) -> str:
    """Append content to HTML body tag.

    Args:
        file_path: Path to existing HTML file
        content: Content to append
        skip_confirm: Required for consistency

    Returns:
        Success message

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or invalid HTML

    Example:
        >>> msg = append_to_html_body("/tmp/page.html", "<p>New</p>", True)
        >>> "Appended" in msg
        True
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(content, str):
        raise TypeError("content must be a string")
    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"HTML file not found: {file_path}")

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    try:
        with open(file_path, encoding="utf-8") as f:
            html_content = f.read()

        # Insert before closing body tag
        if "</body>" in html_content:
            html_content = html_content.replace("</body>", f"{content}\n</body>")
        else:
            # No closing body tag, append to end
            html_content += content

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return f"Appended content to {file_path}"

    except Exception as e:
        raise ValueError(f"Failed to append to HTML file: {e}")


@strands_tool
def markdown_to_html_file(md_path: str, html_path: str, skip_confirm: bool) -> str:
    """Convert Markdown file to HTML file.

    Uses basic Markdown to HTML conversion.

    Args:
        md_path: Path to Markdown file
        html_path: Path for output HTML file
        skip_confirm: If False, raises error if HTML file exists

    Returns:
        Success message

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If Markdown file doesn't exist
        ValueError: If HTML file exists and skip_confirm is False

    Example:
        >>> msg = markdown_to_html_file("/tmp/doc.md", "/tmp/doc.html", True)
        >>> "Converted" in msg
        True
    """
    if not isinstance(md_path, str):
        raise TypeError("md_path must be a string")
    if not isinstance(html_path, str):
        raise TypeError("html_path must be a string")
    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if not os.path.exists(md_path):
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    if os.path.exists(html_path) and not skip_confirm:
        raise ValueError(
            f"HTML file already exists: {html_path}. Set skip_confirm=True to overwrite."
        )

    try:
        # Import markdown module function
        from ..markdown.generation import markdown_to_html_string

        with open(md_path, encoding="utf-8") as f:
            md_content = f.read()

        # Extract title from first heading if present
        title_match = re.match(r"^#\s+(.+)$", md_content, re.MULTILINE)
        title = title_match.group(1) if title_match else "Document"

        html_body = markdown_to_html_string(md_content)

        return create_simple_html(html_path, title, html_body, skip_confirm)

    except Exception as e:
        raise ValueError(f"Failed to convert Markdown to HTML: {e}")


@strands_tool
def html_to_markdown_file(html_path: str, md_path: str, skip_confirm: bool) -> str:
    """Convert HTML file to Markdown file (basic conversion).

    Args:
        html_path: Path to HTML file
        md_path: Path for output Markdown file
        skip_confirm: If False, raises error if Markdown file exists

    Returns:
        Success message

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If HTML file doesn't exist
        ValueError: If Markdown file exists and skip_confirm is False

    Example:
        >>> msg = html_to_markdown_file("/tmp/page.html", "/tmp/page.md", True)
        >>> "Converted" in msg
        True
    """
    if not isinstance(html_path, str):
        raise TypeError("html_path must be a string")
    if not isinstance(md_path, str):
        raise TypeError("md_path must be a string")
    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if not os.path.exists(html_path):
        raise FileNotFoundError(f"HTML file not found: {html_path}")

    if os.path.exists(md_path) and not skip_confirm:
        raise ValueError(
            f"Markdown file already exists: {md_path}. Set skip_confirm=True to overwrite."
        )

    try:
        with open(html_path, encoding="utf-8") as f:
            html_content = f.read()

        # Basic HTML to Markdown conversion
        md_content = html_content

        # Convert headings
        for level in range(1, 7):
            md_content = re.sub(
                f"<h{level}[^>]*>(.*?)</h{level}>",
                lambda m, lvl=level: "#" * lvl + " " + m.group(1) + "\n\n",  # type: ignore[misc]
                md_content,
                flags=re.IGNORECASE | re.DOTALL,
            )

        # Convert paragraphs
        md_content = re.sub(
            r"<p[^>]*>(.*?)</p>",
            r"\1\n\n",
            md_content,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Convert bold
        md_content = re.sub(
            r"<(strong|b)[^>]*>(.*?)</\1>",
            r"**\2**",
            md_content,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Convert italic
        md_content = re.sub(
            r"<(em|i)[^>]*>(.*?)</\1>",
            r"*\2*",
            md_content,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Convert links
        md_content = re.sub(
            r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
            r"[\2](\1)",
            md_content,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Remove remaining tags
        md_content = re.sub(r"<[^>]+>", "", md_content)

        # Clean up whitespace
        md_content = re.sub(r"\n{3,}", "\n\n", md_content)
        md_content = md_content.strip()

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        return f"Converted HTML to Markdown: {html_path} -> {md_path}"

    except Exception as e:
        raise ValueError(f"Failed to convert HTML to Markdown: {e}")


@strands_tool
def prettify_html(file_path: str, skip_confirm: bool) -> str:
    """Format/indent HTML file for readability.

    Args:
        file_path: Path to HTML file
        skip_confirm: Required for consistency

    Returns:
        Success message

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large

    Example:
        >>> msg = prettify_html("/tmp/page.html", True)
        >>> "Prettified" in msg
        True
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"HTML file not found: {file_path}")

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Basic indentation (simplified)
        indent_level = 0
        lines = []
        for line in content.split(">"):
            line = line.strip()
            if not line:
                continue

            # Decrease indent for closing tags
            if line.startswith("</"):
                indent_level = max(0, indent_level - 1)

            lines.append("  " * indent_level + line + ">")

            # Increase indent for opening tags (not self-closing)
            if (
                line.startswith("<")
                and not line.startswith("</")
                and not line.endswith("/>")
                and line not in ["<!DOCTYPE html"]
            ):
                indent_level += 1

        formatted = "\n".join(lines)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(formatted)

        return f"Prettified HTML file: {file_path}"

    except Exception as e:
        raise ValueError(f"Failed to prettify HTML: {e}")
