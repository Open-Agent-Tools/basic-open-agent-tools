"""HTML parsing and extraction functions for AI agents.

This module provides functions for parsing and extracting data from HTML files
using Python standard library only.
"""

import os
import re
from html.parser import HTMLParser
from typing import Union

from ..decorators import strands_tool

# Maximum file size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024


class HTMLStructureParser(HTMLParser):
    """Parser to extract structured data from HTML."""

    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.headings: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.images: list[dict[str, str]] = []
        self.tables: list[list[list[str]]] = []
        self.metadata: dict[str, str] = {}
        self.text_parts: list[str] = []

        self._current_tag = ""
        self._current_table: list[list[str]] = []
        self._current_row: list[str] = []
        self._current_cell = ""
        self._in_title = False
        self._in_table = False
        self._in_row = False
        self._in_cell = False

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, Union[str, None]]]
    ) -> None:
        """Handle opening tags."""
        self._current_tag = tag
        attrs_dict = dict(attrs)

        if tag == "title":
            self._in_title = True
        elif tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            pass  # Will capture text in handle_data
        elif tag == "a":
            href = attrs_dict.get("href", "")
            self.links.append({"href": href or "", "text": ""})
        elif tag == "img":
            src = attrs_dict.get("src", "")
            alt = attrs_dict.get("alt", "")
            self.images.append({"src": src or "", "alt": alt or ""})
        elif tag == "meta":
            name = attrs_dict.get("name", "")
            content = attrs_dict.get("content", "")
            if name and content:
                self.metadata[name] = content
        elif tag == "table":
            self._in_table = True
            self._current_table = []
        elif tag == "tr" and self._in_table:
            self._in_row = True
            self._current_row = []
        elif tag in ["td", "th"] and self._in_row:
            self._in_cell = True
            self._current_cell = ""

    def handle_endtag(self, tag: str) -> None:
        """Handle closing tags."""
        if tag == "title":
            self._in_title = False
        elif tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            pass  # Headings captured in handle_data
        elif tag == "table":
            if self._current_table:
                self.tables.append(self._current_table)
            self._in_table = False
        elif tag == "tr" and self._in_row:
            if self._current_row:
                self._current_table.append(self._current_row)
            self._in_row = False
        elif tag in ["td", "th"] and self._in_cell:
            self._current_row.append(self._current_cell.strip())
            self._in_cell = False

    def handle_data(self, data: str) -> None:
        """Handle text data."""
        text = data.strip()
        if not text:
            return

        if self._in_title:
            self.title += text
        elif self._current_tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            level = self._current_tag[1]
            self.headings.append({"level": level, "text": text})
        elif self._current_tag == "a" and self.links:
            self.links[-1]["text"] = text
        elif self._in_cell:
            self._current_cell += text + " "
        else:
            self.text_parts.append(text)


@strands_tool
def parse_html_to_dict(file_path: str) -> dict[str, object]:
    """Parse HTML file into structured dictionary.

    Args:
        file_path: Path to HTML file

    Returns:
        Dictionary with keys: title, headings, links, images, tables, metadata, text

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or unreadable

    Example:
        >>> data = parse_html_to_dict("/path/to/file.html")
        >>> data['title']
        'Page Title'
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

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

        parser = HTMLStructureParser()
        parser.feed(content)

        return {
            "title": parser.title,
            "headings": parser.headings,
            "links": parser.links,
            "images": parser.images,
            "tables": parser.tables,
            "metadata": parser.metadata,
            "text": " ".join(parser.text_parts),
        }

    except Exception as e:
        raise ValueError(f"Failed to parse HTML file: {e}")


@strands_tool
def extract_html_text(file_path: str) -> str:
    """Extract all text content from HTML file.

    Args:
        file_path: Path to HTML file

    Returns:
        Plain text content

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or unreadable

    Example:
        >>> text = extract_html_text("/path/to/file.html")
        >>> len(text) > 0
        True
    """
    data = parse_html_to_dict(file_path)
    return str(data["text"])


@strands_tool
def extract_html_links(file_path: str) -> list[dict[str, str]]:
    """Extract all links from HTML file.

    Args:
        file_path: Path to HTML file

    Returns:
        List of dicts with keys: href, text

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or unreadable

    Example:
        >>> links = extract_html_links("/path/to/file.html")
        >>> links[0]['href']
        'https://example.com'
    """
    data = parse_html_to_dict(file_path)
    return data["links"]  # type: ignore[return-value]


@strands_tool
def extract_html_images(file_path: str) -> list[dict[str, str]]:
    """Extract all image sources from HTML file.

    Args:
        file_path: Path to HTML file

    Returns:
        List of dicts with keys: src, alt

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or unreadable

    Example:
        >>> images = extract_html_images("/path/to/file.html")
        >>> images[0]['src']
        '/images/photo.jpg'
    """
    data = parse_html_to_dict(file_path)
    return data["images"]  # type: ignore[return-value]


@strands_tool
def extract_html_tables(file_path: str) -> list[list[list[str]]]:
    """Extract all tables from HTML file.

    Args:
        file_path: Path to HTML file

    Returns:
        List of tables, each table is a 2D list [row][cell]

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or unreadable

    Example:
        >>> tables = extract_html_tables("/path/to/file.html")
        >>> tables[0][0]
        ['Header1', 'Header2']
    """
    data = parse_html_to_dict(file_path)
    return data["tables"]  # type: ignore[return-value]


@strands_tool
def extract_html_headings(file_path: str) -> list[dict[str, str]]:
    """Extract all headings (h1-h6) from HTML file.

    Args:
        file_path: Path to HTML file

    Returns:
        List of dicts with keys: level, text

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or unreadable

    Example:
        >>> headings = extract_html_headings("/path/to/file.html")
        >>> headings[0]
        {'level': '1', 'text': 'Main Title'}
    """
    data = parse_html_to_dict(file_path)
    return data["headings"]  # type: ignore[return-value]


@strands_tool
def extract_html_metadata(file_path: str) -> dict[str, str]:
    """Extract metadata from HTML meta tags.

    Args:
        file_path: Path to HTML file

    Returns:
        Dictionary of meta tag name-content pairs

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or unreadable

    Example:
        >>> metadata = extract_html_metadata("/path/to/file.html")
        >>> metadata['description']
        'Page description'
    """
    data = parse_html_to_dict(file_path)
    return data["metadata"]  # type: ignore[return-value]


@strands_tool
def html_to_plain_text(file_path: str) -> str:
    """Convert HTML file to plain text by stripping tags.

    Args:
        file_path: Path to HTML file

    Returns:
        Plain text content

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or unreadable

    Example:
        >>> text = html_to_plain_text("/path/to/file.html")
        >>> '<div>' not in text
        True
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

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

        # Remove script and style tags with content
        content = re.sub(
            r"<script[^>]*>.*?</script>", "", content, flags=re.DOTALL | re.IGNORECASE
        )
        content = re.sub(
            r"<style[^>]*>.*?</style>", "", content, flags=re.DOTALL | re.IGNORECASE
        )

        # Remove all HTML tags
        content = re.sub(r"<[^>]+>", "", content)

        # Decode HTML entities
        import html as html_module

        content = html_module.unescape(content)

        # Clean up whitespace
        content = re.sub(r"\s+", " ", content)
        content = content.strip()

        return content

    except Exception as e:
        raise ValueError(f"Failed to convert HTML to plain text: {e}")
