"""Core text processing utilities for AI agents."""

import re
import textwrap
import unicodedata
from typing import List, Literal, Match


def clean_whitespace(text: str) -> str:
    """Clean and normalize whitespace in text.

    Args:
        text: Input text to clean

    Returns:
        Text with normalized whitespace (single spaces, no leading/trailing)

    Example:
        >>> clean_whitespace("  hello    world  \\n\\t  ")
        "hello world"
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")

    # Replace all whitespace sequences with single spaces
    cleaned = re.sub(r"\s+", " ", text)
    # Strip leading and trailing whitespace
    return cleaned.strip()


def normalize_line_endings(text: str, style: str = "unix") -> str:
    """Normalize line endings in text.

    Args:
        text: Input text to normalize
        style: Line ending style ("unix", "windows", "mac")

    Returns:
        Text with normalized line endings

    Raises:
        ValueError: If style is not supported

    Example:
        >>> normalize_line_endings("line1\\r\\nline2\\rline3\\n", "unix")
        "line1\\nline2\\nline3\\n"
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")

    line_endings = {"unix": "\n", "windows": "\r\n", "mac": "\r"}

    if style not in line_endings:
        raise ValueError(f"Unsupported line ending style: {style}")

    # Normalize all line endings to Unix first
    normalized = re.sub(r"\r\n|\r|\n", "\n", text)

    # Convert to target style if not unix
    if style != "unix":
        normalized = normalized.replace("\n", line_endings[style])

    return normalized


def strip_html_tags(text: str) -> str:
    """Remove HTML tags from text.

    Args:
        text: Input text containing HTML tags

    Returns:
        Text with HTML tags removed

    Example:
        >>> strip_html_tags("<p>Hello <strong>world</strong>!</p>")
        "Hello world!"
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")

    # Remove HTML tags - be smart about spacing to avoid extra spaces around punctuation
    # First pass: remove tags that are followed by punctuation without adding space
    cleaned = re.sub(r"<[^>]+>(?=[^\w\s])", "", text)
    # Second pass: remove remaining tags with space replacement
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    # Clean up extra whitespace that might result from tag removal
    return clean_whitespace(cleaned)


def normalize_unicode(
    text: str, form: Literal["NFC", "NFD", "NFKC", "NFKD"] = "NFC"
) -> str:
    """Normalize Unicode text.

    Args:
        text: Input text to normalize
        form: Unicode normalization form ("NFC", "NFD", "NFKC", "NFKD")

    Returns:
        Unicode-normalized text

    Raises:
        ValueError: If normalization form is not supported

    Example:
        >>> normalize_unicode("café")  # Handles composed/decomposed characters
        "café"
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")

    valid_forms = ["NFC", "NFD", "NFKC", "NFKD"]
    if form not in valid_forms:
        raise ValueError(f"Unsupported normalization form: {form}")

    return unicodedata.normalize(form, text)


def to_snake_case(text: str) -> str:
    """Convert text to snake_case.

    Args:
        text: Input text to convert

    Returns:
        Text converted to snake_case

    Example:
        >>> to_snake_case("HelloWorld")
        "hello_world"
        >>> to_snake_case("hello-world test")
        "hello_world_test"
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")

    # Replace spaces and hyphens with underscores
    text = re.sub(r"[-\s]+", "_", text)
    # Handle sequences of uppercase letters (e.g., XMLHttp -> XML_Http)
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", text)
    # Insert underscore before uppercase letters that follow lowercase letters
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)
    # Convert to lowercase
    return text.lower()


def to_camel_case(text: str, upper_first: bool = False) -> str:
    """Convert text to camelCase or PascalCase.

    Args:
        text: Input text to convert
        upper_first: If True, use PascalCase (first letter uppercase)

    Returns:
        Text converted to camelCase or PascalCase

    Example:
        >>> to_camel_case("hello_world")
        "helloWorld"
        >>> to_camel_case("hello-world", upper_first=True)
        "HelloWorld"
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")

    # Split on common delimiters
    words = re.split(r"[-_\s]+", text.lower())
    # Filter out empty strings
    words = [word for word in words if word]

    if not words:
        return ""

    if upper_first:
        # PascalCase - capitalize all words
        return "".join(word.capitalize() for word in words)
    else:
        # camelCase - first word lowercase, rest capitalized
        return words[0] + "".join(word.capitalize() for word in words[1:])


def to_title_case(text: str) -> str:
    """Convert text to Title Case.

    Args:
        text: Input text to convert

    Returns:
        Text converted to Title Case

    Example:
        >>> to_title_case("hello world")
        "Hello World"
        >>> to_title_case("the-quick_brown fox")
        "The Quick Brown Fox"
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")

    # Split on common delimiters but preserve the structure
    def capitalize_word(match: Match[str]) -> str:
        word = match.group(0)
        return word.capitalize()

    # Split on word separators (spaces, hyphens, underscores) but preserve them
    parts = re.split(r"([\s\-_]+)", text)  # Split on whitespace, hyphens, underscores
    result = []
    for part in parts:
        if part and not re.match(r"^[\s\-_]+$", part):  # If it's not just separators
            result.append(part.capitalize())
        else:  # If it's separators or empty, keep as-is
            result.append(part)
    return "".join(result)


def smart_split_lines(
    text: str, max_length: int, preserve_words: bool = True
) -> List[str]:
    """Split text into lines with maximum length.

    Args:
        text: Input text to split
        max_length: Maximum characters per line
        preserve_words: If True, avoid breaking words

    Returns:
        List of text lines

    Raises:
        ValueError: If max_length is less than 1

    Example:
        >>> smart_split_lines("This is a long line that needs splitting", 10)
        ["This is a", "long line", "that needs", "splitting"]
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")

    if max_length < 1:
        raise ValueError("max_length must be at least 1")

    if preserve_words:
        # Use textwrap for word-preserving splits
        wrapper = textwrap.TextWrapper(
            width=max_length,
            break_long_words=False,
            break_on_hyphens=True,
            expand_tabs=True,
            replace_whitespace=True,
            drop_whitespace=True,
        )
        return wrapper.wrap(text)
    else:
        # Simple character-based splitting
        lines = []
        for i in range(0, len(text), max_length):
            lines.append(text[i : i + max_length])
        return lines


def extract_sentences(text: str) -> List[str]:
    """Extract sentences from text using simple rules.

    Args:
        text: Input text to extract sentences from

    Returns:
        List of sentences

    Example:
        >>> extract_sentences("Hello world. How are you? Fine!")
        ["Hello world.", "How are you?", "Fine!"]
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")

    # Simple sentence boundary detection
    # Split on . ? ! followed by whitespace or end of string
    sentences = re.split(r"[.!?]+(?:\s+|$)", text)

    # Filter out empty sentences and restore punctuation
    result = []
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if sentence:
            # Find the punctuation that was used to split
            if i < len(sentences) - 1:  # Not the last sentence
                # Look for the punctuation in the original text
                start_pos = text.find(sentence)
                end_pos = start_pos + len(sentence)
                if end_pos < len(text) and text[end_pos] in ".!?":
                    sentence += text[end_pos]
            result.append(sentence)

    return result


def join_with_oxford_comma(items: List[str], conjunction: str = "and") -> str:
    """Join a list of items with Oxford comma.

    Args:
        items: List of items to join
        conjunction: Word to use before the last item

    Returns:
        Items joined with Oxford comma

    Example:
        >>> join_with_oxford_comma(["apples", "bananas", "oranges"])
        "apples, bananas, and oranges"
        >>> join_with_oxford_comma(["Alice", "Bob"], "or")
        "Alice or Bob"
    """
    if not isinstance(items, list):
        raise TypeError("Items must be a list")

    if not items:
        return ""

    if len(items) == 1:
        return str(items[0])

    if len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"

    # Three or more items - use Oxford comma
    return f"{', '.join(items[:-1])}, {conjunction} {items[-1]}"
