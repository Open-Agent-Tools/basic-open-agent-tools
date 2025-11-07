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
    return data["links"]  # type: ignore[return-value, no-any-return]


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
    return data["images"]  # type: ignore[return-value, no-any-return]


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
    return data["tables"]  # type: ignore[return-value, no-any-return]


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
    return data["headings"]  # type: ignore[return-value, no-any-return]


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
    return data["metadata"]  # type: ignore[return-value, no-any-return]


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


# ===== Token-Saving HTML Inspection Tools =====


class HTMLElementCounter(HTMLParser):
    """Parser to count specific elements without loading full content."""

    def __init__(self, target_tag: str) -> None:
        super().__init__()
        self.target_tag = target_tag.lower()
        self.count = 0

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, Union[str, None]]]
    ) -> None:
        """Count matching tags."""
        if tag.lower() == self.target_tag:
            self.count += 1


class HTMLTextExtractor(HTMLParser):
    """Parser to extract text from specific tags."""

    def __init__(self, target_tag: str, max_elements: int = -1) -> None:
        super().__init__()
        self.target_tag = target_tag.lower()
        self.max_elements = max_elements
        self.elements: list[str] = []
        self.current_text = ""
        self.in_target = False

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, Union[str, None]]]
    ) -> None:
        """Start capturing text if target tag."""
        if tag.lower() == self.target_tag:
            if self.max_elements == -1 or len(self.elements) < self.max_elements:
                self.in_target = True
                self.current_text = ""

    def handle_endtag(self, tag: str) -> None:
        """Stop capturing and store text."""
        if tag.lower() == self.target_tag and self.in_target:
            self.elements.append(self.current_text.strip())
            self.in_target = False

    def handle_data(self, data: str) -> None:
        """Capture text data."""
        if self.in_target:
            self.current_text += data


class HTMLStructureExtractor(HTMLParser):
    """Parser to extract DOM structure without content."""

    def __init__(self, max_depth: int = -1) -> None:
        super().__init__()
        self.max_depth = max_depth
        self.structure: list[dict[str, str]] = []
        self.depth = 0

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, Union[str, None]]]
    ) -> None:
        """Record tag structure."""
        if self.max_depth == -1 or self.depth < self.max_depth:
            attrs_str = " ".join(f"{k}={v}" for k, v in attrs if v)
            self.structure.append(
                {"tag": tag, "depth": str(self.depth), "attrs": attrs_str}
            )
        self.depth += 1

    def handle_endtag(self, tag: str) -> None:
        """Track depth."""
        self.depth = max(0, self.depth - 1)


class HTMLListExtractor(HTMLParser):
    """Parser to extract lists (ul/ol) as structured data."""

    def __init__(self) -> None:
        super().__init__()
        self.lists: list[dict[str, str]] = []
        self.current_list: list[str] = []
        self.current_item = ""
        self.in_list = False
        self.in_item = False
        self.list_type = ""

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, Union[str, None]]]
    ) -> None:
        """Track list and item tags."""
        if tag in ["ul", "ol"]:
            self.in_list = True
            self.list_type = tag
            self.current_list = []
        elif tag == "li" and self.in_list:
            self.in_item = True
            self.current_item = ""

    def handle_endtag(self, tag: str) -> None:
        """Close lists and items."""
        if tag in ["ul", "ol"] and self.in_list:
            if self.current_list:
                self.lists.append(
                    {"type": self.list_type, "items": str(self.current_list)}
                )
            self.in_list = False
        elif tag == "li" and self.in_item:
            self.current_list.append(self.current_item.strip())
            self.in_item = False

    def handle_data(self, data: str) -> None:
        """Capture list item text."""
        if self.in_item:
            self.current_item += data


class HTMLFormExtractor(HTMLParser):
    """Parser to extract form structures."""

    def __init__(self) -> None:
        super().__init__()
        self.forms: list[dict[str, str]] = []
        self.current_form: dict[str, str] = {}
        self.current_fields: list[str] = []
        self.in_form = False

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, Union[str, None]]]
    ) -> None:
        """Track form and input tags."""
        attrs_dict = dict(attrs)

        if tag == "form":
            self.in_form = True
            action = attrs_dict.get("action") or ""
            method = attrs_dict.get("method") or "get"
            self.current_form = {
                "action": action,
                "method": method,
            }
            self.current_fields = []
        elif tag in ["input", "textarea", "select"] and self.in_form:
            field_name = attrs_dict.get("name", "")
            field_type = attrs_dict.get("type", "text") if tag == "input" else tag
            if field_name:
                self.current_fields.append(f"{field_name} ({field_type})")

    def handle_endtag(self, tag: str) -> None:
        """Close form."""
        if tag == "form" and self.in_form:
            self.current_form["fields"] = ", ".join(self.current_fields)
            self.forms.append(self.current_form)
            self.in_form = False


class HTMLTextSearcher(HTMLParser):
    """Parser to find tags containing specific text."""

    def __init__(self, search_text: str) -> None:
        super().__init__()
        self.search_text = search_text.lower()
        self.matches: list[dict[str, str]] = []
        self.current_tag = ""
        self.current_text = ""

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, Union[str, None]]]
    ) -> None:
        """Track current tag."""
        self.current_tag = tag
        self.current_text = ""

    def handle_data(self, data: str) -> None:
        """Accumulate text."""
        self.current_text += data

    def handle_endtag(self, tag: str) -> None:
        """Check if text matches."""
        if self.search_text in self.current_text.lower():
            self.matches.append({"tag": tag, "text": self.current_text.strip()})


@strands_tool
def get_html_text_at_tag(file_path: str, tag_name: str) -> list[str]:
    """Extract text content from all occurrences of specific HTML tag.

    Parses HTML and returns text content from all matching tags without
    loading full document into memory. More efficient than full parse when
    you only need specific tag text.

    Args:
        file_path: Path to HTML file
        tag_name: HTML tag name to extract (e.g., "p", "div", "h1")

    Returns:
        List of text content from matching tags

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or cannot be parsed

    Example:
        >>> get_html_text_at_tag("page.html", "h1")
        ["Welcome to My Site", "About Us"]
        >>> get_html_text_at_tag("page.html", "p")
        ["First paragraph text", "Second paragraph text"]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(tag_name, str):
        raise TypeError("tag_name must be a string")

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

        parser = HTMLTextExtractor(tag_name)
        parser.feed(content)
        return parser.elements

    except Exception as e:
        raise ValueError(f"Failed to extract text from tag {tag_name}: {e}")


@strands_tool
def count_html_elements(file_path: str, tag_name: str) -> int:
    """Count occurrences of specific HTML tag without loading full content.

    Efficiently counts how many times a tag appears in HTML document without
    parsing full structure or loading content into memory.

    Args:
        file_path: Path to HTML file
        tag_name: HTML tag name to count (e.g., "div", "p", "img")

    Returns:
        Count of matching tags

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or cannot be parsed

    Example:
        >>> count_html_elements("page.html", "p")
        42
        >>> count_html_elements("page.html", "img")
        15
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(tag_name, str):
        raise TypeError("tag_name must be a string")

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

        parser = HTMLElementCounter(tag_name)
        parser.feed(content)
        return parser.count

    except Exception as e:
        raise ValueError(f"Failed to count elements {tag_name}: {e}")


@strands_tool
def get_html_structure(file_path: str, max_depth: int) -> list[dict[str, str]]:
    """Get DOM tree structure overview without loading text content.

    Returns hierarchical tag structure showing element types and nesting
    without actual content. Useful for understanding HTML organization.

    Args:
        file_path: Path to HTML file
        max_depth: Maximum nesting depth to traverse (-1 for unlimited)

    Returns:
        List of dictionaries with tag, depth, and attrs information

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or cannot be parsed

    Example:
        >>> get_html_structure("page.html", 2)
        [
            {"tag": "html", "depth": "0", "attrs": ""},
            {"tag": "head", "depth": "1", "attrs": ""},
            {"tag": "body", "depth": "1", "attrs": "class=main"}
        ]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(max_depth, int):
        raise TypeError("max_depth must be an integer")

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

        parser = HTMLStructureExtractor(max_depth)
        parser.feed(content)
        return parser.structure

    except Exception as e:
        raise ValueError(f"Failed to extract HTML structure: {e}")


@strands_tool
def search_html_text(file_path: str, search_pattern: str) -> list[dict[str, str]]:
    """Find HTML tags containing specific text pattern.

    Searches through HTML and returns tags whose text content matches the
    search pattern (case-insensitive substring match).

    Args:
        file_path: Path to HTML file
        search_pattern: Text pattern to search for

    Returns:
        List of dictionaries with tag and text for matching elements

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or cannot be parsed

    Example:
        >>> search_html_text("page.html", "contact")
        [
            {"tag": "h2", "text": "Contact Us"},
            {"tag": "p", "text": "Please contact us for more info"}
        ]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(search_pattern, str):
        raise TypeError("search_pattern must be a string")

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

        parser = HTMLTextSearcher(search_pattern)
        parser.feed(content)
        return parser.matches

    except Exception as e:
        raise ValueError(f"Failed to search HTML text: {e}")


@strands_tool
def extract_html_lists(file_path: str) -> list[dict[str, str]]:
    """Extract all lists (ul/ol) from HTML as structured data.

    Parses HTML and extracts all unordered and ordered lists with their items.
    More memory-efficient than full document parse when you only need lists.

    Args:
        file_path: Path to HTML file

    Returns:
        List of dictionaries with list type and items

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or cannot be parsed

    Example:
        >>> extract_html_lists("page.html")
        [
            {"type": "ul", "items": "['Item 1', 'Item 2', 'Item 3']"},
            {"type": "ol", "items": "['First', 'Second', 'Third']"}
        ]
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

        parser = HTMLListExtractor()
        parser.feed(content)
        return parser.lists

    except Exception as e:
        raise ValueError(f"Failed to extract HTML lists: {e}")


@strands_tool
def extract_html_forms(file_path: str) -> list[dict[str, str]]:
    """Extract form structures from HTML including fields and actions.

    Parses HTML and extracts form information including action URLs, methods,
    and field names. Useful for understanding form structure without full parse.

    Args:
        file_path: Path to HTML file

    Returns:
        List of dictionaries with form action, method, and fields

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or cannot be parsed

    Example:
        >>> extract_html_forms("page.html")
        [
            {
                "action": "/submit",
                "method": "post",
                "fields": "username (text), password (password), submit (submit)"
            }
        ]
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

        parser = HTMLFormExtractor()
        parser.feed(content)
        return parser.forms

    except Exception as e:
        raise ValueError(f"Failed to extract HTML forms: {e}")


@strands_tool
def preview_html_tags(file_path: str, tag_name: str, max_count: int) -> list[str]:
    """Get first N occurrences of specific HTML tag for preview.

    Extracts text from first N matching tags without processing entire
    document. Useful for sampling large HTML files.

    Args:
        file_path: Path to HTML file
        tag_name: HTML tag name to extract (e.g., "p", "div")
        max_count: Maximum number of tags to return

    Returns:
        List of text content from first max_count matching tags

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or cannot be parsed

    Example:
        >>> preview_html_tags("page.html", "p", 3)
        ["First paragraph", "Second paragraph", "Third paragraph"]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(tag_name, str):
        raise TypeError("tag_name must be a string")
    if not isinstance(max_count, int):
        raise TypeError("max_count must be an integer")

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

        parser = HTMLTextExtractor(tag_name, max_count)
        parser.feed(content)
        return parser.elements

    except Exception as e:
        raise ValueError(f"Failed to preview HTML tags: {e}")


@strands_tool
def get_html_title(file_path: str) -> str:
    """Extract HTML title without parsing full document.

    Efficiently extracts just the title tag content using regex pattern
    matching without full HTML parse.

    Args:
        file_path: Path to HTML file

    Returns:
        Title text, or empty string if no title found

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or cannot be read

    Example:
        >>> get_html_title("page.html")
        "Welcome to My Website"
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

        # Extract title using regex
        match = re.search(
            r"<title[^>]*>(.*?)</title>", content, re.IGNORECASE | re.DOTALL
        )
        if match:
            import html as html_module

            return html_module.unescape(match.group(1).strip())
        return ""

    except Exception as e:
        raise ValueError(f"Failed to extract HTML title: {e}")


@strands_tool
def get_html_tag_attributes(file_path: str, tag_name: str) -> list[dict[str, str]]:
    """Extract all attributes from occurrences of specific HTML tag.

    Parses HTML and returns attributes from all matching tags without
    loading full content. Useful for extracting metadata like hrefs, srcs, etc.

    Args:
        file_path: Path to HTML file
        tag_name: HTML tag name to extract attributes from

    Returns:
        List of dictionaries containing tag attributes

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or cannot be parsed

    Example:
        >>> get_html_tag_attributes("page.html", "a")
        [
            {"href": "/about", "class": "nav-link"},
            {"href": "/contact", "class": "nav-link"}
        ]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(tag_name, str):
        raise TypeError("tag_name must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"HTML file not found: {file_path}")

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    class AttributeExtractor(HTMLParser):
        """Extract attributes from specific tags."""

        def __init__(self, target: str) -> None:
            super().__init__()
            self.target = target.lower()
            self.results: list[dict[str, str]] = []

        def handle_starttag(
            self, tag: str, attrs: list[tuple[str, Union[str, None]]]
        ) -> None:
            """Collect attributes from matching tags."""
            if tag.lower() == self.target:
                attr_dict = {k: v or "" for k, v in attrs}
                self.results.append(attr_dict)

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        parser = AttributeExtractor(tag_name)
        parser.feed(content)
        return parser.results

    except Exception as e:
        raise ValueError(f"Failed to extract tag attributes: {e}")


@strands_tool
def get_html_element_count_by_type(file_path: str) -> dict[str, str]:
    """Count all HTML element types in document without loading content.

    Provides overview of document structure by counting occurrences of each
    tag type. Useful for understanding HTML composition.

    Args:
        file_path: Path to HTML file

    Returns:
        Dictionary mapping tag names to count strings

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or cannot be parsed

    Example:
        >>> get_html_element_count_by_type("page.html")
        {"div": "45", "p": "23", "a": "15", "img": "8"}
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

    class TagCounter(HTMLParser):
        """Count all tag types."""

        def __init__(self) -> None:
            super().__init__()
            self.counts: dict[str, int] = {}

        def handle_starttag(
            self, tag: str, attrs: list[tuple[str, Union[str, None]]]
        ) -> None:
            """Increment count for each tag."""
            self.counts[tag] = self.counts.get(tag, 0) + 1

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        parser = TagCounter()
        parser.feed(content)

        # Convert to string values for JSON serialization
        return {tag: str(count) for tag, count in parser.counts.items()}

    except Exception as e:
        raise ValueError(f"Failed to count HTML elements: {e}")
