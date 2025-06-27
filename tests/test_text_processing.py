"""Tests for text processing module."""

import pytest

from basic_open_agent_tools.text.processing import (
    clean_whitespace,
    extract_sentences,
    join_with_oxford_comma,
    normalize_line_endings,
    normalize_unicode,
    smart_split_lines,
    strip_html_tags,
    to_camel_case,
    to_snake_case,
    to_title_case,
)


class TestTextProcessing:
    """Test cases for text processing functions."""

    def test_clean_whitespace(self):
        """Test whitespace cleaning functionality."""
        # Basic whitespace cleaning
        assert clean_whitespace("  hello    world  ") == "hello world"

        # Mixed whitespace types
        assert clean_whitespace("hello\t\n\r world") == "hello world"

        # Empty string
        assert clean_whitespace("") == ""

        # Only whitespace
        assert clean_whitespace("   \t\n  ") == ""

        # Already clean
        assert clean_whitespace("hello world") == "hello world"

        # Type error
        with pytest.raises(TypeError):
            clean_whitespace(123)

    def test_normalize_line_endings(self):
        """Test line ending normalization."""
        # Unix style (default)
        assert (
            normalize_line_endings("line1\r\nline2\rline3\n", "unix")
            == "line1\nline2\nline3\n"
        )

        # Windows style
        assert normalize_line_endings("line1\nline2", "windows") == "line1\r\nline2"

        # Mac style
        assert normalize_line_endings("line1\nline2", "mac") == "line1\rline2"

        # Invalid style
        with pytest.raises(ValueError):
            normalize_line_endings("text", "invalid")

        # Type error
        with pytest.raises(TypeError):
            normalize_line_endings(123, "unix")

    def test_strip_html_tags(self):
        """Test HTML tag removal."""
        # Basic tags
        assert strip_html_tags("<p>Hello world</p>") == "Hello world"

        # Nested tags
        assert (
            strip_html_tags("<div><p>Hello <strong>world</strong>!</p></div>")
            == "Hello world!"
        )

        # Self-closing tags
        assert strip_html_tags("Line 1<br/>Line 2") == "Line 1 Line 2"

        # No tags
        assert strip_html_tags("Plain text") == "Plain text"

        # Empty string
        assert strip_html_tags("") == ""

        # Type error
        with pytest.raises(TypeError):
            strip_html_tags(123)

    def test_normalize_unicode(self):
        """Test Unicode normalization."""
        # Basic normalization (this test might be system-dependent)
        text = "café"
        result = normalize_unicode(text)
        assert isinstance(result, str)
        assert "é" in result or "e" in result  # Handle different Unicode forms

        # Different forms
        for form in ["NFC", "NFD", "NFKC", "NFKD"]:
            result = normalize_unicode("test", form)
            assert result == "test"

        # Invalid form
        with pytest.raises(ValueError):
            normalize_unicode("text", "INVALID")

        # Type error
        with pytest.raises(TypeError):
            normalize_unicode(123)

    def test_to_snake_case(self):
        """Test snake_case conversion."""
        # CamelCase
        assert to_snake_case("HelloWorld") == "hello_world"

        # PascalCase
        assert to_snake_case("XMLHttpRequest") == "xml_http_request"

        # Spaces
        assert to_snake_case("hello world") == "hello_world"

        # Hyphens
        assert to_snake_case("hello-world") == "hello_world"

        # Mixed
        assert to_snake_case("XMLHttp-Request Test") == "xml_http_request_test"

        # Already snake_case
        assert to_snake_case("hello_world") == "hello_world"

        # Empty string
        assert to_snake_case("") == ""

        # Type error
        with pytest.raises(TypeError):
            to_snake_case(123)

    def test_to_camel_case(self):
        """Test camelCase conversion."""
        # Snake case
        assert to_camel_case("hello_world", False) == "helloWorld"

        # Spaces
        assert to_camel_case("hello world", False) == "helloWorld"

        # Hyphens
        assert to_camel_case("hello-world", False) == "helloWorld"

        # PascalCase mode
        assert to_camel_case("hello_world", upper_first=True) == "HelloWorld"

        # Single word
        assert to_camel_case("hello", False) == "hello"
        assert to_camel_case("hello", upper_first=True) == "Hello"

        # Empty string
        assert to_camel_case("", False) == ""

        # Type error
        with pytest.raises(TypeError):
            to_camel_case(123, False)

    def test_to_title_case(self):
        """Test Title Case conversion."""
        # Basic conversion
        assert to_title_case("hello world") == "Hello World"

        # Mixed delimiters
        assert to_title_case("hello-world_test") == "Hello-World_Test"

        # Already title case
        assert to_title_case("Hello World") == "Hello World"

        # Single word
        assert to_title_case("hello") == "Hello"

        # Empty string
        assert to_title_case("") == ""

        # Type error
        with pytest.raises(TypeError):
            to_title_case(123)

    def test_smart_split_lines(self):
        """Test smart line splitting."""
        # Word-preserving split
        text = "This is a long line that needs splitting"
        result = smart_split_lines(text, 15, True)
        assert all(len(line) <= 15 for line in result)
        assert " ".join(result) == text

        # Character-based split
        result = smart_split_lines("abcdefghij", 3, False)
        assert result == ["abc", "def", "ghi", "j"]

        # Short text
        assert smart_split_lines("short", 10, True) == ["short"]

        # Empty string
        assert smart_split_lines("", 10, True) == []

        # Invalid max_length
        with pytest.raises(ValueError):
            smart_split_lines("text", 0, True)

        # Type error
        with pytest.raises(TypeError):
            smart_split_lines(123, 10, True)

    def test_extract_sentences(self):
        """Test sentence extraction."""
        # Basic sentences
        text = "Hello world. How are you? Fine!"
        result = extract_sentences(text)
        assert len(result) == 3
        assert "Hello world." in result
        assert "How are you?" in result
        assert "Fine!" in result

        # Single sentence
        assert extract_sentences("Hello world") == ["Hello world"]

        # No punctuation
        assert extract_sentences("Hello world") == ["Hello world"]

        # Empty string
        assert extract_sentences("") == []

        # Multiple punctuation
        result = extract_sentences("What?! Really...")
        assert len(result) >= 1

        # Type error
        with pytest.raises(TypeError):
            extract_sentences(123)

    def test_join_with_oxford_comma(self):
        """Test Oxford comma joining."""
        # Three items
        items = ["apples", "bananas", "oranges"]
        assert join_with_oxford_comma(items, "and") == "apples, bananas, and oranges"

        # Two items
        items = ["apples", "bananas"]
        assert join_with_oxford_comma(items, "and") == "apples and bananas"

        # One item
        assert join_with_oxford_comma(["apples"], "and") == "apples"

        # Empty list
        assert join_with_oxford_comma([], "and") == ""

        # Custom conjunction
        items = ["A", "B", "C"]
        assert join_with_oxford_comma(items, "or") == "A, B, or C"

        # Type error
        with pytest.raises(TypeError):
            join_with_oxford_comma("not a list", "and")


class TestTextProcessingIntegration:
    """Integration tests combining multiple text processing functions."""

    def test_clean_and_normalize_workflow(self):
        """Test combining cleaning and normalization functions."""
        messy_text = "  <p>Hello    World!</p>\r\n\t  "

        # Clean HTML and whitespace
        cleaned = strip_html_tags(messy_text)
        normalized = clean_whitespace(cleaned)

        assert normalized == "Hello World!"

    def test_case_conversion_roundtrip(self):
        """Test converting between different case styles."""
        original = "hello_world_test"

        # snake -> camel -> snake
        camel = to_camel_case(original, False)
        back_to_snake = to_snake_case(camel)

        assert back_to_snake == original

    def test_text_splitting_and_joining(self):
        """Test splitting text and joining results."""
        original = "The quick brown fox jumps over the lazy dog"

        # Split into lines
        lines = smart_split_lines(original, 15, True)

        # Join back together
        rejoined = " ".join(lines)

        assert rejoined == original
