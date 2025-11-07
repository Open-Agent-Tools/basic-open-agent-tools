"""Markdown parsing and extraction functions for AI agents.

This module provides functions for parsing and extracting data from
Markdown (.md) files using standard library only.
"""

import os
import re
from typing import Any

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


@strands_tool
def get_markdown_info(file_path: str) -> dict[str, str]:
    """Get Markdown file metadata without loading full content.

    Provides quick overview statistics without reading entire file content.

    Args:
        file_path: Path to Markdown file

    Returns:
        Dict with keys: file_size, line_count, heading_count, has_frontmatter,
        has_code_blocks, has_tables

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist

    Example:
        >>> info = get_markdown_info("/path/to/file.md")
        >>> info['line_count']
        '150'
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    try:
        file_size = os.path.getsize(file_path)
        line_count = 0
        heading_count = 0
        has_frontmatter = False
        has_code_blocks = False
        has_tables = False

        with open(file_path, encoding="utf-8") as f:
            first_line = True
            in_code_block = False

            for line in f:
                line_count += 1

                # Check for frontmatter
                if first_line and line.strip() == "---":
                    has_frontmatter = True
                first_line = False

                # Check for headings
                if re.match(r"^#{1,6}\s+", line):
                    heading_count += 1

                # Check for code blocks
                if line.strip().startswith("```"):
                    has_code_blocks = True
                    in_code_block = not in_code_block

                # Check for tables (if not in code block)
                if not in_code_block and "|" in line and line.count("|") >= 2:
                    has_tables = True

        return {
            "file_size": str(file_size),
            "line_count": str(line_count),
            "heading_count": str(heading_count),
            "has_frontmatter": str(has_frontmatter),
            "has_code_blocks": str(has_code_blocks),
            "has_tables": str(has_tables),
        }

    except Exception as e:
        raise ValueError(f"Failed to get Markdown info: {e}")


@strands_tool
def get_markdown_structure(file_path: str) -> list[dict[str, str]]:
    """Get hierarchical heading structure without loading content.

    Extracts only headings with their levels and line numbers for quick
    document navigation.

    Args:
        file_path: Path to Markdown file

    Returns:
        List of dicts with keys: level, text, line_number

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist

    Example:
        >>> structure = get_markdown_structure("/path/to/file.md")
        >>> structure[0]
        {'level': '1', 'text': 'Introduction', 'line_number': '5'}
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    try:
        headings = []
        line_number = 0

        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line_number += 1
                match = re.match(r"^(#{1,6})\s+(.+)$", line)
                if match:
                    level = str(len(match.group(1)))
                    text = match.group(2).strip()
                    headings.append(
                        {
                            "level": level,
                            "text": text,
                            "line_number": str(line_number),
                        }
                    )

        return headings

    except Exception as e:
        raise ValueError(f"Failed to get Markdown structure: {e}")


@strands_tool
def count_markdown_elements(file_path: str, element_type: str) -> int:
    """Count specific Markdown elements without loading full content.

    Efficiently counts elements by streaming through file.

    Args:
        file_path: Path to Markdown file
        element_type: Type to count ("headings", "links", "code_blocks", "tables", "lines")

    Returns:
        Count of specified elements

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If element_type is invalid

    Example:
        >>> count = count_markdown_elements("/path/to/file.md", "headings")
        >>> count
        15
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(element_type, str):
        raise TypeError("element_type must be a string")

    valid_types = ["headings", "links", "code_blocks", "tables", "lines"]
    if element_type not in valid_types:
        raise ValueError(f"element_type must be one of: {', '.join(valid_types)}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    try:
        count = 0

        with open(file_path, encoding="utf-8") as f:
            in_code_block = False

            for line in f:
                if element_type == "lines":
                    count += 1
                elif element_type == "headings":
                    if re.match(r"^#{1,6}\s+", line):
                        count += 1
                elif element_type == "links":
                    # Count inline links
                    pattern = r'\[([^\]]+)\]\(([^\s\)]+)(?:\s+"([^"]+)")?\)'
                    count += len(re.findall(pattern, line))
                elif element_type == "code_blocks":
                    if line.strip().startswith("```"):
                        if not in_code_block:
                            count += 1
                        in_code_block = not in_code_block
                elif element_type == "tables":
                    if not in_code_block and "|" in line and line.count("|") >= 2:
                        # Check if it's a separator line
                        if not re.match(r"^\|[\s\-:|\|]+\|$", line.strip()):
                            count += 1

        return count

    except Exception as e:
        raise ValueError(f"Failed to count Markdown elements: {e}")


@strands_tool
def get_markdown_section(file_path: str, heading_text: str) -> dict[str, str]:
    """Extract specific section by heading name without loading entire file.

    Streams through file to find matching heading and extract its content.

    Args:
        file_path: Path to Markdown file
        heading_text: Text of the heading to find (case-insensitive)

    Returns:
        Dict with keys: heading, level, content, line_start, line_end

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If heading not found

    Example:
        >>> section = get_markdown_section("/path/to/file.md", "Installation")
        >>> section['content']
        'Run pip install...'
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(heading_text, str):
        raise TypeError("heading_text must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    try:
        heading_text_lower = heading_text.lower()
        found_heading = False
        heading_level = 0
        line_start = 0
        line_number = 0
        content_lines = []

        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line_number += 1

                if not found_heading:
                    # Look for the target heading
                    match = re.match(r"^(#{1,6})\s+(.+)$", line)
                    if match and match.group(2).strip().lower() == heading_text_lower:
                        found_heading = True
                        heading_level = len(match.group(1))
                        line_start = line_number
                        continue
                else:
                    # Check if we've reached the next heading of same or higher level
                    match = re.match(r"^(#{1,6})\s+", line)
                    if match:
                        next_level = len(match.group(1))
                        if next_level <= heading_level:
                            # End of section
                            break

                    content_lines.append(line.rstrip())

        if not found_heading:
            raise ValueError(f"Heading '{heading_text}' not found in file")

        return {
            "heading": heading_text,
            "level": str(heading_level),
            "content": "\n".join(content_lines).strip(),
            "line_start": str(line_start),
            "line_end": str(line_number),
        }

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to get Markdown section: {e}")


@strands_tool
def search_markdown_headings(
    file_path: str, search_pattern: str
) -> list[dict[str, str]]:
    """Find headings matching pattern without loading full content.

    Uses case-insensitive substring matching on heading text.

    Args:
        file_path: Path to Markdown file
        search_pattern: Pattern to search for in heading text

    Returns:
        List of dicts with keys: level, text, line_number

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist

    Example:
        >>> headings = search_markdown_headings("/path/to/file.md", "install")
        >>> headings[0]['text']
        'Installation Guide'
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(search_pattern, str):
        raise TypeError("search_pattern must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    try:
        pattern_lower = search_pattern.lower()
        matching_headings = []
        line_number = 0

        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line_number += 1
                match = re.match(r"^(#{1,6})\s+(.+)$", line)
                if match:
                    heading_text = match.group(2).strip()
                    if pattern_lower in heading_text.lower():
                        level = str(len(match.group(1)))
                        matching_headings.append(
                            {
                                "level": level,
                                "text": heading_text,
                                "line_number": str(line_number),
                            }
                        )

        return matching_headings

    except Exception as e:
        raise ValueError(f"Failed to search Markdown headings: {e}")


@strands_tool
def preview_markdown_lines(file_path: str, num_lines: int) -> dict[str, str]:
    """Get first N lines of Markdown file for preview.

    Efficiently reads only the requested number of lines.

    Args:
        file_path: Path to Markdown file
        num_lines: Number of lines to read

    Returns:
        Dict with keys: content, total_lines_read, file_truncated

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If num_lines is negative

    Example:
        >>> preview = preview_markdown_lines("/path/to/file.md", 20)
        >>> preview['content']
        '# Title\\n\\nFirst paragraph...'
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(num_lines, int):
        raise TypeError("num_lines must be an integer")

    if num_lines < 0:
        raise ValueError("num_lines must be non-negative")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    try:
        lines_read = 0
        content_lines = []
        file_truncated = False

        with open(file_path, encoding="utf-8") as f:
            for line in f:
                if lines_read >= num_lines:
                    file_truncated = True
                    break
                content_lines.append(line.rstrip())
                lines_read += 1

        return {
            "content": "\n".join(content_lines),
            "total_lines_read": str(lines_read),
            "file_truncated": str(file_truncated),
        }

    except Exception as e:
        raise ValueError(f"Failed to preview Markdown lines: {e}")


@strands_tool
def get_markdown_toc(file_path: str, max_level: int) -> list[dict[str, str]]:
    """Generate table of contents from headings only.

    Creates TOC without loading full document content, optionally limiting
    depth to specified heading level.

    Args:
        file_path: Path to Markdown file
        max_level: Maximum heading level to include (1-6)

    Returns:
        List of dicts with keys: level, text, line_number, indent

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If max_level is invalid

    Example:
        >>> toc = get_markdown_toc("/path/to/file.md", 3)
        >>> toc[0]
        {'level': '1', 'text': 'Introduction', 'line_number': '5', 'indent': ''}
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(max_level, int):
        raise TypeError("max_level must be an integer")

    if max_level < 1 or max_level > 6:
        raise ValueError("max_level must be between 1 and 6")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    try:
        toc_entries = []
        line_number = 0

        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line_number += 1
                match = re.match(r"^(#{1,6})\s+(.+)$", line)
                if match:
                    level = len(match.group(1))
                    if level <= max_level:
                        text = match.group(2).strip()
                        indent = "  " * (level - 1)  # 2 spaces per level
                        toc_entries.append(
                            {
                                "level": str(level),
                                "text": text,
                                "line_number": str(line_number),
                                "indent": indent,
                            }
                        )

        return toc_entries

    except Exception as e:
        raise ValueError(f"Failed to generate Markdown TOC: {e}")


@strands_tool
def filter_headings_by_level(file_path: str, target_level: int) -> list[dict[str, str]]:
    """Get headings of specific level only without loading content.

    Efficiently extracts only headings at the specified level.

    Args:
        file_path: Path to Markdown file
        target_level: Heading level to filter (1-6)

    Returns:
        List of dicts with keys: level, text, line_number

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If target_level is invalid

    Example:
        >>> headings = filter_headings_by_level("/path/to/file.md", 2)
        >>> all(h['level'] == '2' for h in headings)
        True
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(target_level, int):
        raise TypeError("target_level must be an integer")

    if target_level < 1 or target_level > 6:
        raise ValueError("target_level must be between 1 and 6")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    try:
        filtered_headings = []
        line_number = 0

        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line_number += 1
                match = re.match(r"^(#{1,6})\s+(.+)$", line)
                if match:
                    level = len(match.group(1))
                    if level == target_level:
                        text = match.group(2).strip()
                        filtered_headings.append(
                            {
                                "level": str(level),
                                "text": text,
                                "line_number": str(line_number),
                            }
                        )

        return filtered_headings

    except Exception as e:
        raise ValueError(f"Failed to filter headings by level: {e}")


@strands_tool
def get_markdown_frontmatter(file_path: str) -> dict[str, str]:
    """Extract only frontmatter without loading document body.

    Reads only the frontmatter section at the beginning of the file.

    Args:
        file_path: Path to Markdown file

    Returns:
        Dict with frontmatter key-value pairs

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If no frontmatter found

    Example:
        >>> frontmatter = get_markdown_frontmatter("/path/to/file.md")
        >>> frontmatter['title']
        'My Document'
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    try:
        frontmatter: dict[str, str] = {}
        in_frontmatter = False
        first_line = True

        with open(file_path, encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()

                if first_line:
                    if stripped == "---":
                        in_frontmatter = True
                        first_line = False
                        continue
                    else:
                        raise ValueError(
                            "No frontmatter found (file doesn't start with ---)"
                        )

                first_line = False

                if in_frontmatter:
                    if stripped == "---":
                        # End of frontmatter
                        break

                    if ":" in line:
                        key, value = line.split(":", 1)
                        frontmatter[key.strip()] = value.strip()

        if not frontmatter:
            raise ValueError("No frontmatter found or frontmatter is empty")

        return frontmatter

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to extract frontmatter: {e}")


@strands_tool
def extract_markdown_section_range(
    file_path: str, start_heading: str, end_heading: str
) -> dict[str, str]:
    """Extract content between two headings without loading entire file.

    Efficiently extracts a range of content by streaming through file.

    Args:
        file_path: Path to Markdown file
        start_heading: Heading text where extraction starts (inclusive)
        end_heading: Heading text where extraction ends (exclusive)

    Returns:
        Dict with keys: content, line_start, line_end, sections_included

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If headings not found or in wrong order

    Example:
        >>> range_content = extract_markdown_section_range("/path/to/file.md", "Chapter 1", "Chapter 2")
        >>> range_content['sections_included']
        '5'
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(start_heading, str):
        raise TypeError("start_heading must be a string")

    if not isinstance(end_heading, str):
        raise TypeError("end_heading must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    try:
        start_lower = start_heading.lower()
        end_lower = end_heading.lower()
        in_range = False
        line_start = 0
        line_number = 0
        content_lines = []
        sections_included = 0

        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line_number += 1

                # Check for headings
                match = re.match(r"^#{1,6}\s+(.+)$", line)

                if match:
                    heading_text = match.group(1).strip().lower()

                    if not in_range and heading_text == start_lower:
                        # Start of range
                        in_range = True
                        line_start = line_number
                        content_lines.append(line.rstrip())
                        sections_included += 1
                        continue

                    if in_range and heading_text == end_lower:
                        # End of range (exclusive)
                        break

                    if in_range:
                        # Count subsections
                        sections_included += 1

                if in_range:
                    content_lines.append(line.rstrip())

        if not in_range:
            raise ValueError(f"Start heading '{start_heading}' not found in file")

        if line_number == 0:
            raise ValueError("File is empty")

        return {
            "content": "\n".join(content_lines).strip(),
            "line_start": str(line_start),
            "line_end": str(line_number),
            "sections_included": str(sections_included),
        }

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to extract section range: {e}")


# ===== Advanced Parsing Features (Issue #30) =====


@strands_tool
def parse_reference_links(file_path: str) -> list[dict[str, str]]:
    """Parse reference-style links from Markdown file.

    Reference-style links have two parts:
    - [link text][ref]
    - [ref]: http://url.com "optional title"

    Args:
        file_path: Path to Markdown file

    Returns:
        List of dicts with keys: ref, url, title, used_by

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or cannot be read

    Example:
        >>> parse_reference_links("doc.md")
        [{"ref": "1", "url": "http://example.com", "title": "Example", "used_by": "link text"}]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Find reference definitions: [ref]: url "title"
        ref_pattern = r'^\[([^\]]+)\]:\s+(\S+)(?:\s+"([^"]*)")?'
        references: dict[str, dict[str, Any]] = {}

        for match in re.finditer(ref_pattern, content, re.MULTILINE):
            ref_id = match.group(1)
            url = match.group(2)
            title = match.group(3) or ""
            references[ref_id] = {"url": url, "title": title, "used_by": []}

        # Find usage of references: [text][ref]
        usage_pattern = r"\[([^\]]+)\]\[([^\]]+)\]"

        for match in re.finditer(usage_pattern, content):
            text = match.group(1)
            ref_id = match.group(2)
            if ref_id in references:
                references[ref_id]["used_by"].append(text)

        # Convert to list format
        result = []
        for ref_id, data in references.items():
            result.append(
                {
                    "ref": ref_id,
                    "url": data["url"],
                    "title": data["title"],
                    "used_by": ", ".join(data["used_by"]) if data["used_by"] else "",
                }
            )

        return result

    except FileNotFoundError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse reference links: {e}")


@strands_tool
def parse_footnotes(file_path: str) -> list[dict[str, str]]:
    """Parse footnotes from Markdown file.

    Footnotes have two parts:
    - Text with footnote reference: text[^1]
    - Footnote definition: [^1]: footnote content

    Args:
        file_path: Path to Markdown file

    Returns:
        List of dicts with keys: id, content, location_line

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or cannot be read

    Example:
        >>> parse_footnotes("doc.md")
        [{"id": "1", "content": "This is a footnote.", "location_line": "42"}]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    try:
        footnotes = []

        with open(file_path, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                # Match footnote definition: [^id]: content
                match = re.match(r"^\[\^([^\]]+)\]:\s+(.+)$", line.strip())
                if match:
                    footnote_id = match.group(1)
                    content = match.group(2)
                    footnotes.append(
                        {
                            "id": footnote_id,
                            "content": content,
                            "location_line": str(line_num),
                        }
                    )

        return footnotes

    except FileNotFoundError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse footnotes: {e}")


@strands_tool
def parse_definition_lists(file_path: str) -> list[dict[str, str]]:
    """Parse definition lists from Markdown file.

    Definition lists format:
    Term
    : Definition

    Args:
        file_path: Path to Markdown file

    Returns:
        List of dicts with keys: term, definition, line_number

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or cannot be read

    Example:
        >>> parse_definition_lists("doc.md")
        [{"term": "Markdown", "definition": "A lightweight markup language", "line_number": "5"}]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    try:
        definitions = []
        current_term = ""
        term_line = 0

        with open(file_path, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                stripped = line.strip()

                # Check for definition marker
                if stripped.startswith(": "):
                    if current_term:
                        definition = stripped[2:].strip()  # Remove ": "
                        definitions.append(
                            {
                                "term": current_term,
                                "definition": definition,
                                "line_number": str(term_line),
                            }
                        )
                        current_term = ""
                elif stripped and not stripped.startswith(": "):
                    # This could be a term
                    current_term = stripped
                    term_line = line_num

        return definitions

    except FileNotFoundError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse definition lists: {e}")


@strands_tool
def parse_task_lists(file_path: str) -> list[dict[str, str]]:
    """Parse task lists with checkboxes from Markdown file.

    Task list format:
    - [ ] Unchecked task
    - [x] Checked task

    Args:
        file_path: Path to Markdown file

    Returns:
        List of dicts with keys: task, checked, line_number

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or cannot be read

    Example:
        >>> parse_task_lists("todo.md")
        [{"task": "Write documentation", "checked": "false", "line_number": "3"}]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    try:
        tasks = []

        with open(file_path, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                stripped = line.strip()

                # Match checked task
                checked_match = re.match(r"^-\s+\[x\]\s+(.+)$", stripped, re.IGNORECASE)
                if checked_match:
                    task_text = checked_match.group(1)
                    tasks.append(
                        {
                            "task": task_text,
                            "checked": "true",
                            "line_number": str(line_num),
                        }
                    )
                    continue

                # Match unchecked task
                unchecked_match = re.match(r"^-\s+\[\s\]\s+(.+)$", stripped)
                if unchecked_match:
                    task_text = unchecked_match.group(1)
                    tasks.append(
                        {
                            "task": task_text,
                            "checked": "false",
                            "line_number": str(line_num),
                        }
                    )

        return tasks

    except FileNotFoundError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse task lists: {e}")


@strands_tool
def extract_image_references(file_path: str) -> list[dict[str, str]]:
    """Extract image references from Markdown file.

    Supports both inline and reference-style images:
    - ![alt text](image.png "title")
    - ![alt text][ref]
      [ref]: image.png "title"

    Args:
        file_path: Path to Markdown file

    Returns:
        List of dicts with keys: alt_text, url, title, line_number

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or cannot be read

    Example:
        >>> extract_image_references("doc.md")
        [{"alt_text": "Logo", "url": "logo.png", "title": "Company Logo", "line_number": "10"}]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        images = []

        # Find reference definitions for images first
        ref_pattern = r'^\[([^\]]+)\]:\s+(\S+)(?:\s+"([^"]*)")?'
        image_refs = {}

        for match in re.finditer(ref_pattern, content, re.MULTILINE):
            ref_id = match.group(1)
            url = match.group(2)
            title = match.group(3) or ""
            # Only store if it looks like an image URL
            if any(
                url.lower().endswith(ext)
                for ext in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"]
            ):
                image_refs[ref_id] = {"url": url, "title": title}

        # Find inline images: ![alt](url "title")
        inline_pattern = r'!\[([^\]]*)\]\(([^\s\)]+)(?:\s+"([^"]*)")?\)'

        for line_num, line in enumerate(content.split("\n"), 1):
            for match in re.finditer(inline_pattern, line):
                alt_text = match.group(1)
                url = match.group(2)
                title = match.group(3) or ""
                images.append(
                    {
                        "alt_text": alt_text,
                        "url": url,
                        "title": title,
                        "line_number": str(line_num),
                    }
                )

        # Find reference-style images: ![alt][ref]
        ref_usage_pattern = r"!\[([^\]]*)\]\[([^\]]+)\]"

        for line_num, line in enumerate(content.split("\n"), 1):
            for match in re.finditer(ref_usage_pattern, line):
                alt_text = match.group(1)
                ref_id = match.group(2)
                if ref_id in image_refs:
                    images.append(
                        {
                            "alt_text": alt_text,
                            "url": image_refs[ref_id]["url"],
                            "title": image_refs[ref_id]["title"],
                            "line_number": str(line_num),
                        }
                    )

        return images

    except FileNotFoundError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to extract image references: {e}")
