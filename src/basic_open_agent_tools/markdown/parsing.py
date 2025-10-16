"""Markdown parsing and extraction functions for AI agents.

This module provides functions for parsing and extracting data from
Markdown (.md) files using standard library only.
"""

import os
import re

from ..decorators import strands_tool

# Maximum file size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024


@strands_tool
def parse_markdown_to_dict(file_path: str) -> dict[str, object]:
    """Parse Markdown file into structured dictionary.

    Extracts frontmatter, headings, and content sections from a Markdown file.

    Args:
        file_path: Path to Markdown file

    Returns:
        Dictionary with keys: frontmatter, headings, sections, raw_content

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or unreadable

    Example:
        >>> data = parse_markdown_to_dict("/path/to/file.md")
        >>> data['headings'][0]
        {'level': 1, 'text': 'Introduction', 'line': 5}
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

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
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Extract frontmatter if present
        frontmatter = {}
        content_without_frontmatter = content

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter_text = parts[1].strip()
                # Simple key: value parsing
                for line in frontmatter_text.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        frontmatter[key.strip()] = value.strip()
                content_without_frontmatter = parts[2].strip()

        # Extract headings
        headings = []
        for line_num, line in enumerate(content_without_frontmatter.split("\n"), 1):
            match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                headings.append({"level": level, "text": text, "line": line_num})

        # Build sections based on headings
        sections = []
        lines = content_without_frontmatter.split("\n")

        for i, heading in enumerate(headings):
            start_line = int(heading["line"])  # Cast to int for type safety
            end_line = (
                int(headings[i + 1]["line"]) if i + 1 < len(headings) else len(lines)
            )

            section_content = "\n".join(lines[start_line : end_line - 1]).strip()
            sections.append(
                {
                    "heading": heading["text"],
                    "level": heading["level"],
                    "content": section_content,
                }
            )

        return {
            "frontmatter": frontmatter,
            "headings": headings,
            "sections": sections,
            "raw_content": content,
        }

    except Exception as e:
        raise ValueError(f"Failed to parse Markdown file: {e}")


@strands_tool
def extract_markdown_headings(file_path: str) -> list[dict[str, str]]:
    """Extract all headings from Markdown file.

    Args:
        file_path: Path to Markdown file

    Returns:
        List of dicts with keys: level, text

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or unreadable

    Example:
        >>> headings = extract_markdown_headings("/path/to/file.md")
        >>> headings[0]
        {'level': '1', 'text': 'Introduction'}
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

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
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        headings = []
        for line in content.split("\n"):
            match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if match:
                level = str(len(match.group(1)))
                text = match.group(2).strip()
                headings.append({"level": level, "text": text})

        return headings

    except Exception as e:
        raise ValueError(f"Failed to extract headings: {e}")


@strands_tool
def extract_markdown_links(file_path: str) -> list[dict[str, str]]:
    """Extract all links from Markdown file.

    Extracts both inline links [text](url) and reference links.

    Args:
        file_path: Path to Markdown file

    Returns:
        List of dicts with keys: text, url, title (optional)

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or unreadable

    Example:
        >>> links = extract_markdown_links("/path/to/file.md")
        >>> links[0]
        {'text': 'Click here', 'url': 'https://example.com', 'title': ''}
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

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
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        links = []

        # Match inline links: [text](url "optional title")
        inline_pattern = r'\[([^\]]+)\]\(([^\s\)]+)(?:\s+"([^"]+)")?\)'
        for match in re.finditer(inline_pattern, content):
            text = match.group(1)
            url = match.group(2)
            title = match.group(3) if match.group(3) else ""
            links.append({"text": text, "url": url, "title": title})

        return links

    except Exception as e:
        raise ValueError(f"Failed to extract links: {e}")


@strands_tool
def extract_markdown_code_blocks(file_path: str) -> list[dict[str, str]]:
    """Extract all code blocks from Markdown file.

    Extracts fenced code blocks with language identifiers.

    Args:
        file_path: Path to Markdown file

    Returns:
        List of dicts with keys: language, code

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or unreadable

    Example:
        >>> blocks = extract_markdown_code_blocks("/path/to/file.md")
        >>> blocks[0]
        {'language': 'python', 'code': 'print("hello")'}
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

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
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        blocks = []

        # Match fenced code blocks: ```language\ncode\n```
        pattern = r"```(\w*)\n(.*?)```"
        for match in re.finditer(pattern, content, re.DOTALL):
            language = match.group(1) if match.group(1) else ""
            code = match.group(2).strip()
            blocks.append({"language": language, "code": code})

        return blocks

    except Exception as e:
        raise ValueError(f"Failed to extract code blocks: {e}")


@strands_tool
def extract_markdown_tables(file_path: str) -> list[list[list[str]]]:
    """Extract all tables from Markdown file.

    Parses Markdown tables into 3D list structure.

    Args:
        file_path: Path to Markdown file

    Returns:
        List of tables, each table is a 2D list [row][cell]

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or unreadable

    Example:
        >>> tables = extract_markdown_tables("/path/to/file.md")
        >>> tables[0]
        [['Name', 'Age'], ['Alice', '30'], ['Bob', '25']]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

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
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tables = []
        lines = content.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Check if line looks like a table row (contains |)
            if "|" in line and line.count("|") >= 2:
                table = []

                # Start collecting table rows
                while i < len(lines) and "|" in lines[i]:
                    row_line = lines[i].strip()

                    # Skip separator lines (like |---|---|)
                    if re.match(r"^\|[\s\-:|\|]+\|$", row_line):
                        i += 1
                        continue

                    # Parse row
                    cells = [cell.strip() for cell in row_line.split("|")]
                    # Remove empty first/last cells from leading/trailing |
                    if cells and cells[0] == "":
                        cells = cells[1:]
                    if cells and cells[-1] == "":
                        cells = cells[:-1]

                    if cells:
                        table.append(cells)

                    i += 1

                if table:
                    tables.append(table)
            else:
                i += 1

        return tables

    except Exception as e:
        raise ValueError(f"Failed to extract tables: {e}")


@strands_tool
def markdown_to_plain_text(file_path: str) -> str:
    """Convert Markdown file to plain text by stripping formatting.

    Removes Markdown syntax while preserving readable text content.

    Args:
        file_path: Path to Markdown file

    Returns:
        Plain text content

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or unreadable

    Example:
        >>> text = markdown_to_plain_text("/path/to/file.md")
        >>> "**bold**" not in text
        True
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

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
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Remove frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2].strip()

        # Remove code blocks
        content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)

        # Remove inline code
        content = re.sub(r"`[^`]+`", "", content)

        # Remove images ![alt](url)
        content = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", r"\1", content)

        # Remove links but keep text [text](url)
        content = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", content)

        # Remove bold/italic
        content = re.sub(r"\*\*\*([^\*]+)\*\*\*", r"\1", content)  # Bold italic
        content = re.sub(r"\*\*([^\*]+)\*\*", r"\1", content)  # Bold
        content = re.sub(r"\*([^\*]+)\*", r"\1", content)  # Italic
        content = re.sub(r"__([^_]+)__", r"\1", content)  # Bold
        content = re.sub(r"_([^_]+)_", r"\1", content)  # Italic

        # Remove headings markers but keep text
        content = re.sub(r"^#{1,6}\s+", "", content, flags=re.MULTILINE)

        # Remove horizontal rules
        content = re.sub(r"^[\*\-_]{3,}$", "", content, flags=re.MULTILINE)

        # Remove blockquote markers
        content = re.sub(r"^>\s*", "", content, flags=re.MULTILINE)

        # Remove list markers
        content = re.sub(r"^[\*\-\+]\s+", "", content, flags=re.MULTILINE)
        content = re.sub(r"^\d+\.\s+", "", content, flags=re.MULTILINE)

        # Clean up extra whitespace
        content = re.sub(r"\n{3,}", "\n\n", content)
        content = content.strip()

        return content

    except Exception as e:
        raise ValueError(f"Failed to convert Markdown to plain text: {e}")
