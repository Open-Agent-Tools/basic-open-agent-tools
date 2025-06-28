"""Tests for basic_open_agent_tools.text.processing module."""

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


class TestCleanWhitespace:
    """Test cases for clean_whitespace function."""

    def test_clean_basic_whitespace(self) -> None:
        """Test cleaning basic whitespace patterns."""
        assert clean_whitespace("hello world") == "hello world"
        assert clean_whitespace("  hello    world  ") == "hello world"
        assert clean_whitespace("hello\t\tworld") == "hello world"
        assert clean_whitespace("hello\n\nworld") == "hello world"

    def test_clean_mixed_whitespace(self) -> None:
        """Test cleaning mixed whitespace characters."""
        assert clean_whitespace("  hello\t\n  world  \r\n  ") == "hello world"
        assert clean_whitespace("a\r\n\t b\f\v c") == "a b c"
        assert (
            clean_whitespace("\u00a0hello\u2000world\u3000") == "hello world"
        )  # Unicode spaces

    def test_clean_empty_and_whitespace_only(self) -> None:
        """Test cleaning empty strings and whitespace-only strings."""
        assert clean_whitespace("") == ""
        assert clean_whitespace("   ") == ""
        assert clean_whitespace("\t\n\r") == ""
        assert clean_whitespace("\u00a0\u2000\u3000") == ""  # Unicode spaces only

    def test_clean_single_character(self) -> None:
        """Test cleaning single character strings."""
        assert clean_whitespace("a") == "a"
        assert clean_whitespace(" a ") == "a"
        assert clean_whitespace("\ta\n") == "a"

    def test_clean_no_whitespace(self) -> None:
        """Test strings with no whitespace to clean."""
        assert clean_whitespace("hello") == "hello"
        assert clean_whitespace("helloworld") == "helloworld"
        assert clean_whitespace("123") == "123"

    def test_clean_unicode_text(self) -> None:
        """Test cleaning text with Unicode characters."""
        assert clean_whitespace("  café  ") == "café"
        assert clean_whitespace("北京\t東京") == "北京 東京"
        assert clean_whitespace("  🚀  space  🌟  ") == "🚀 space 🌟"

    def test_clean_whitespace_invalid_input(self) -> None:
        """Test error handling for invalid input types."""
        with pytest.raises(TypeError, match="Input must be a string"):
            clean_whitespace(123)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="Input must be a string"):
            clean_whitespace(None)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="Input must be a string"):
            clean_whitespace(["hello", "world"])  # type: ignore[arg-type]


class TestNormalizeLineEndings:
    """Test cases for normalize_line_endings function."""

    def test_normalize_to_unix(self) -> None:
        """Test normalizing line endings to Unix style."""
        assert normalize_line_endings("line1\nline2", "unix") == "line1\nline2"
        assert normalize_line_endings("line1\r\nline2", "unix") == "line1\nline2"
        assert normalize_line_endings("line1\rline2", "unix") == "line1\nline2"
        assert (
            normalize_line_endings("line1\r\nline2\rline3\n", "unix")
            == "line1\nline2\nline3\n"
        )

    def test_normalize_to_windows(self) -> None:
        """Test normalizing line endings to Windows style."""
        assert normalize_line_endings("line1\nline2", "windows") == "line1\r\nline2"
        assert normalize_line_endings("line1\rline2", "windows") == "line1\r\nline2"
        assert (
            normalize_line_endings("line1\r\nline2\rline3\n", "windows")
            == "line1\r\nline2\r\nline3\r\n"
        )

    def test_normalize_to_mac(self) -> None:
        """Test normalizing line endings to Mac style."""
        assert normalize_line_endings("line1\nline2", "mac") == "line1\rline2"
        assert normalize_line_endings("line1\r\nline2", "mac") == "line1\rline2"
        assert (
            normalize_line_endings("line1\r\nline2\nline3", "mac")
            == "line1\rline2\rline3"
        )

    def test_normalize_mixed_line_endings(self) -> None:
        """Test normalizing text with mixed line ending styles."""
        mixed_text = "line1\r\nline2\rline3\nline4"
        assert (
            normalize_line_endings(mixed_text, "unix") == "line1\nline2\nline3\nline4"
        )
        assert (
            normalize_line_endings(mixed_text, "windows")
            == "line1\r\nline2\r\nline3\r\nline4"
        )
        assert normalize_line_endings(mixed_text, "mac") == "line1\rline2\rline3\rline4"

    def test_normalize_empty_string(self) -> None:
        """Test normalizing empty string."""
        assert normalize_line_endings("", "unix") == ""
        assert normalize_line_endings("", "windows") == ""
        assert normalize_line_endings("", "mac") == ""

    def test_normalize_no_line_endings(self) -> None:
        """Test normalizing text without line endings."""
        assert normalize_line_endings("hello world", "unix") == "hello world"
        assert normalize_line_endings("hello world", "windows") == "hello world"
        assert normalize_line_endings("hello world", "mac") == "hello world"

    def test_normalize_line_endings_invalid_style(self) -> None:
        """Test error handling for invalid line ending style."""
        with pytest.raises(ValueError, match="Unsupported line ending style"):
            normalize_line_endings("test", "invalid")

        with pytest.raises(ValueError, match="Unsupported line ending style"):
            normalize_line_endings("test", "linux")

    def test_normalize_line_endings_invalid_input(self) -> None:
        """Test error handling for invalid input types."""
        with pytest.raises(TypeError, match="Input must be a string"):
            normalize_line_endings(123, "unix")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="Input must be a string"):
            normalize_line_endings(None, "unix")  # type: ignore[arg-type]


class TestStripHtmlTags:
    """Test cases for strip_html_tags function."""

    def test_strip_basic_html_tags(self) -> None:
        """Test stripping basic HTML tags."""
        assert strip_html_tags("<p>Hello world</p>") == "Hello world"
        assert strip_html_tags("<div>Content</div>") == "Content"
        assert strip_html_tags("<span>Text</span>") == "Text"

    def test_strip_nested_html_tags(self) -> None:
        """Test stripping nested HTML tags."""
        assert strip_html_tags("<p>Hello <strong>world</strong>!</p>") == "Hello world!"
        assert (
            strip_html_tags("<div><p>Nested <em>text</em> here</p></div>")
            == "Nested text here"
        )
        assert (
            strip_html_tags("<ul><li>Item 1</li><li>Item 2</li></ul>")
            == "Item 1 Item 2"
        )

    def test_strip_html_with_attributes(self) -> None:
        """Test stripping HTML tags with attributes."""
        assert strip_html_tags('<p class="test">Hello</p>') == "Hello"
        assert (
            strip_html_tags('<a href="http://example.com" target="_blank">Link</a>')
            == "Link"
        )
        assert strip_html_tags('<img src="image.jpg" alt="Image" />') == ""

    def test_strip_html_preserve_spacing(self) -> None:
        """Test that HTML stripping preserves appropriate spacing."""
        assert strip_html_tags("<p>Hello</p> <p>world</p>") == "Hello world"
        assert strip_html_tags("Text<br>break") == "Text break"
        assert strip_html_tags("Before<div>middle</div>after") == "Before middle after"

    def test_strip_html_with_punctuation(self) -> None:
        """Test stripping HTML tags adjacent to punctuation."""
        assert strip_html_tags("Hello<strong>!</strong>") == "Hello!"
        assert strip_html_tags("Question<em>?</em>") == "Question?"
        assert strip_html_tags("End<span>.</span>") == "End."

    def test_strip_malformed_html(self) -> None:
        """Test stripping malformed HTML."""
        # Unclosed tags are not stripped (not valid HTML)
        assert (
            strip_html_tags("Hello <unclosed tag world") == "Hello <unclosed tag world"
        )
        assert (
            strip_html_tags("Text with > brackets < here")
            == "Text with > brackets < here"
        )
        # Empty tags result in empty string after whitespace cleaning
        result = strip_html_tags("<<>>")
        assert result == ">" or result.isspace()

    def test_strip_html_empty_and_whitespace(self) -> None:
        """Test stripping HTML from empty and whitespace strings."""
        assert strip_html_tags("") == ""
        assert strip_html_tags("<p></p>") == ""
        assert strip_html_tags("<div>   </div>") == ""
        assert strip_html_tags("   <span></span>   ") == ""

    def test_strip_html_unicode_content(self) -> None:
        """Test stripping HTML from Unicode content."""
        assert strip_html_tags("<p>Café</p>") == "Café"
        assert strip_html_tags("<div>北京</div>") == "北京"
        assert strip_html_tags("<span>🚀 Space</span>") == "🚀 Space"

    def test_strip_html_tags_invalid_input(self) -> None:
        """Test error handling for invalid input types."""
        with pytest.raises(TypeError, match="Input must be a string"):
            strip_html_tags(123)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="Input must be a string"):
            strip_html_tags(None)  # type: ignore[arg-type]


class TestNormalizeUnicode:
    """Test cases for normalize_unicode function."""

    def test_normalize_nfc(self) -> None:
        """Test Unicode normalization to NFC form."""
        # Test with decomposed characters
        decomposed = "café"  # 'e' + combining acute accent
        normalized = normalize_unicode(decomposed, "NFC")
        assert len(normalized) <= len(decomposed)
        assert normalized == "café"

    def test_normalize_nfd(self) -> None:
        """Test Unicode normalization to NFD form."""
        # Test with composed characters
        composed = "café"  # composed 'é'
        normalized = normalize_unicode(composed, "NFD")
        # NFD should decompose characters
        assert "café" in normalized or "cafe" in normalized

    def test_normalize_nfkc(self) -> None:
        """Test Unicode normalization to NFKC form."""
        # Test with compatibility characters
        text = "①②③"  # Circled numbers
        normalized = normalize_unicode(text, "NFKC")
        assert normalized == "123"

    def test_normalize_nfkd(self) -> None:
        """Test Unicode normalization to NFKD form."""
        # Test with compatibility characters and decomposition
        text = "ﬁ"  # fi ligature
        normalized = normalize_unicode(text, "NFKD")
        assert normalized == "fi"

    def test_normalize_ascii_text(self) -> None:
        """Test Unicode normalization with ASCII text."""
        text = "Hello World"
        for form in ["NFC", "NFD", "NFKC", "NFKD"]:
            assert normalize_unicode(text, form) == text

    def test_normalize_mixed_unicode(self) -> None:
        """Test Unicode normalization with mixed Unicode content."""
        text = "Café résumé naïve"
        for form in ["NFC", "NFD", "NFKC", "NFKD"]:
            normalized = normalize_unicode(text, form)
            assert isinstance(normalized, str)
            assert len(normalized) > 0

    def test_normalize_unicode_empty_string(self) -> None:
        """Test Unicode normalization with empty string."""
        for form in ["NFC", "NFD", "NFKC", "NFKD"]:
            assert normalize_unicode("", form) == ""

    def test_normalize_unicode_invalid_form(self) -> None:
        """Test error handling for invalid normalization form."""
        with pytest.raises(ValueError, match="Unsupported normalization form"):
            normalize_unicode("test", "INVALID")

        with pytest.raises(ValueError, match="Unsupported normalization form"):
            normalize_unicode("test", "nfc")  # Case sensitive

    def test_normalize_unicode_invalid_input(self) -> None:
        """Test error handling for invalid input types."""
        with pytest.raises(TypeError, match="Input must be a string"):
            normalize_unicode(123, "NFC")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="Input must be a string"):
            normalize_unicode(None, "NFC")  # type: ignore[arg-type]


class TestToSnakeCase:
    """Test cases for to_snake_case function."""

    def test_snake_case_camel_case_input(self) -> None:
        """Test converting camelCase to snake_case."""
        assert to_snake_case("helloWorld") == "hello_world"
        assert to_snake_case("camelCaseExample") == "camel_case_example"
        assert to_snake_case("XMLHttpRequest") == "xml_http_request"
        assert to_snake_case("iPhone") == "i_phone"

    def test_snake_case_pascal_case_input(self) -> None:
        """Test converting PascalCase to snake_case."""
        assert to_snake_case("HelloWorld") == "hello_world"
        assert to_snake_case("PascalCaseExample") == "pascal_case_example"
        assert to_snake_case("MyClass") == "my_class"

    def test_snake_case_spaces_and_hyphens(self) -> None:
        """Test converting spaced and hyphenated text to snake_case."""
        assert to_snake_case("hello world") == "hello_world"
        assert to_snake_case("hello-world") == "hello_world"
        assert to_snake_case("hello world test") == "hello_world_test"
        assert to_snake_case("multi-word-example") == "multi_word_example"

    def test_snake_case_mixed_delimiters(self) -> None:
        """Test converting text with mixed delimiters to snake_case."""
        assert to_snake_case("hello world-test_case") == "hello_world_test_case"
        assert to_snake_case("My Test-Class") == "my_test_class"
        assert to_snake_case("API_KEY value") == "api_key_value"

    def test_snake_case_numbers(self) -> None:
        """Test converting text with numbers to snake_case."""
        assert to_snake_case("version2") == "version2"
        assert to_snake_case("version2Update") == "version2_update"
        assert to_snake_case("HTML5Parser") == "html5_parser"
        assert to_snake_case("test123Case") == "test123_case"

    def test_snake_case_acronyms(self) -> None:
        """Test converting text with acronyms to snake_case."""
        assert to_snake_case("XMLParser") == "xml_parser"
        assert to_snake_case("HTTPSConnection") == "https_connection"
        assert to_snake_case("APIKey") == "api_key"
        assert to_snake_case("URLPath") == "url_path"

    def test_snake_case_already_snake_case(self) -> None:
        """Test converting already snake_case text."""
        assert to_snake_case("hello_world") == "hello_world"
        assert to_snake_case("snake_case_example") == "snake_case_example"
        assert to_snake_case("already_correct") == "already_correct"

    def test_snake_case_empty_and_single_char(self) -> None:
        """Test converting empty and single character strings."""
        assert to_snake_case("") == ""
        assert to_snake_case("a") == "a"
        assert to_snake_case("A") == "a"
        assert to_snake_case("1") == "1"

    def test_snake_case_special_characters(self) -> None:
        """Test converting text with special characters."""
        assert to_snake_case("hello@world") == "hello@world"
        assert to_snake_case("test.case") == "test.case"
        assert to_snake_case("my_file.txt") == "my_file.txt"

    def test_snake_case_invalid_input(self) -> None:
        """Test error handling for invalid input types."""
        with pytest.raises(TypeError, match="Input must be a string"):
            to_snake_case(123)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="Input must be a string"):
            to_snake_case(None)  # type: ignore[arg-type]


class TestToCamelCase:
    """Test cases for to_camel_case function."""

    def test_camel_case_snake_case_input(self) -> None:
        """Test converting snake_case to camelCase."""
        assert to_camel_case("hello_world", False) == "helloWorld"
        assert to_camel_case("snake_case_example", False) == "snakeCaseExample"
        assert to_camel_case("my_variable_name", False) == "myVariableName"

    def test_pascal_case_snake_case_input(self) -> None:
        """Test converting snake_case to PascalCase."""
        assert to_camel_case("hello_world", True) == "HelloWorld"
        assert to_camel_case("snake_case_example", True) == "SnakeCaseExample"
        assert to_camel_case("my_class_name", True) == "MyClassName"

    def test_camel_case_hyphenated_input(self) -> None:
        """Test converting hyphenated text to camelCase."""
        assert to_camel_case("hello-world", False) == "helloWorld"
        assert to_camel_case("kebab-case-example", False) == "kebabCaseExample"
        assert to_camel_case("multi-word-test", False) == "multiWordTest"

    def test_pascal_case_hyphenated_input(self) -> None:
        """Test converting hyphenated text to PascalCase."""
        assert to_camel_case("hello-world", True) == "HelloWorld"
        assert to_camel_case("kebab-case-example", True) == "KebabCaseExample"
        assert to_camel_case("multi-word-test", True) == "MultiWordTest"

    def test_camel_case_spaced_input(self) -> None:
        """Test converting spaced text to camelCase/PascalCase."""
        assert to_camel_case("hello world", False) == "helloWorld"
        assert to_camel_case("hello world", True) == "HelloWorld"
        assert to_camel_case("multi word example", False) == "multiWordExample"
        assert to_camel_case("multi word example", True) == "MultiWordExample"

    def test_camel_case_mixed_delimiters(self) -> None:
        """Test converting text with mixed delimiters."""
        assert to_camel_case("hello world-test_case", False) == "helloWorldTestCase"
        assert to_camel_case("hello world-test_case", True) == "HelloWorldTestCase"
        assert to_camel_case("my-test_variable name", False) == "myTestVariableName"

    def test_camel_case_already_camel_case(self) -> None:
        """Test converting already camelCase text."""
        assert (
            to_camel_case("helloWorld", False) == "helloworld"
        )  # Gets lowercased first
        assert to_camel_case("helloWorld", True) == "Helloworld"
        # Since it splits and processes, the original casing is lost

    def test_camel_case_empty_and_single_word(self) -> None:
        """Test converting empty and single word strings."""
        assert to_camel_case("", False) == ""
        assert to_camel_case("", True) == ""
        assert to_camel_case("hello", False) == "hello"
        assert to_camel_case("hello", True) == "Hello"
        assert to_camel_case("HELLO", False) == "hello"
        assert to_camel_case("HELLO", True) == "Hello"

    def test_camel_case_numbers(self) -> None:
        """Test converting text with numbers."""
        assert to_camel_case("version_2_update", False) == "version2Update"
        assert to_camel_case("version_2_update", True) == "Version2Update"
        assert to_camel_case("html5_parser", False) == "html5Parser"
        assert to_camel_case("html5_parser", True) == "Html5Parser"

    def test_camel_case_multiple_separators(self) -> None:
        """Test converting text with multiple consecutive separators."""
        assert to_camel_case("hello__world", False) == "helloWorld"
        assert to_camel_case("hello--world", False) == "helloWorld"
        assert to_camel_case("hello  world", False) == "helloWorld"
        assert to_camel_case("hello___world", True) == "HelloWorld"

    def test_camel_case_invalid_input(self) -> None:
        """Test error handling for invalid input types."""
        with pytest.raises(TypeError, match="Input must be a string"):
            to_camel_case(123, False)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="Input must be a string"):
            to_camel_case(None, False)  # type: ignore[arg-type]


class TestToTitleCase:
    """Test cases for to_title_case function."""

    def test_title_case_basic_words(self) -> None:
        """Test converting basic words to Title Case."""
        assert to_title_case("hello world") == "Hello World"
        assert to_title_case("the quick brown fox") == "The Quick Brown Fox"
        assert to_title_case("title case example") == "Title Case Example"

    def test_title_case_hyphenated_words(self) -> None:
        """Test converting hyphenated words to Title Case."""
        assert to_title_case("well-known") == "Well-Known"
        assert to_title_case("mother-in-law") == "Mother-In-Law"
        assert to_title_case("twenty-one") == "Twenty-One"

    def test_title_case_underscored_words(self) -> None:
        """Test converting underscored words to Title Case."""
        assert to_title_case("hello_world") == "Hello_World"
        assert to_title_case("snake_case_example") == "Snake_Case_Example"
        assert to_title_case("my_variable_name") == "My_Variable_Name"

    def test_title_case_mixed_separators(self) -> None:
        """Test converting text with mixed separators."""
        assert to_title_case("hello world-test_case") == "Hello World-Test_Case"
        assert to_title_case("multi-word_example text") == "Multi-Word_Example Text"

    def test_title_case_already_capitalized(self) -> None:
        """Test converting already capitalized text."""
        assert to_title_case("HELLO WORLD") == "Hello World"
        assert to_title_case("Hello World") == "Hello World"
        assert to_title_case("hELLo WoRLd") == "Hello World"

    def test_title_case_single_words(self) -> None:
        """Test converting single words."""
        assert to_title_case("hello") == "Hello"
        assert to_title_case("HELLO") == "Hello"
        assert to_title_case("hELLo") == "Hello"

    def test_title_case_empty_and_whitespace(self) -> None:
        """Test converting empty and whitespace strings."""
        assert to_title_case("") == ""
        assert to_title_case("   ") == "   "
        assert to_title_case("\t\n") == "\t\n"

    def test_title_case_numbers_and_special_chars(self) -> None:
        """Test converting text with numbers and special characters."""
        assert to_title_case("version 2.0") == "Version 2.0"
        assert to_title_case("chapter-1") == "Chapter-1"
        assert to_title_case("test@example.com") == "Test@example.com"

    def test_title_case_unicode_text(self) -> None:
        """Test converting Unicode text to Title Case."""
        assert to_title_case("café résumé") == "Café Résumé"
        assert to_title_case("北京 東京") == "北京 東京"
        assert to_title_case("naïve approach") == "Naïve Approach"

    def test_title_case_preserve_structure(self) -> None:
        """Test that Title Case preserves original structure."""
        assert to_title_case("a-b_c d") == "A-B_C D"
        assert (
            to_title_case("word1   word2") == "Word1   Word2"
        )  # Preserve multiple spaces
        assert to_title_case("test\tword") == "Test\tWord"  # Preserve tabs

    def test_title_case_invalid_input(self) -> None:
        """Test error handling for invalid input types."""
        with pytest.raises(TypeError, match="Input must be a string"):
            to_title_case(123)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="Input must be a string"):
            to_title_case(None)  # type: ignore[arg-type]


class TestSmartSplitLines:
    """Test cases for smart_split_lines function."""

    def test_split_lines_preserve_words(self) -> None:
        """Test splitting lines while preserving words."""
        text = "This is a long line that needs to be split"
        result = smart_split_lines(text, 20, True)
        assert len(result) > 1
        assert all(len(line) <= 20 for line in result)
        assert "".join(result).replace(" ", "") == text.replace(" ", "")

    def test_split_lines_character_based(self) -> None:
        """Test splitting lines based on character count."""
        text = "This is a long line that needs splitting"
        result = smart_split_lines(text, 10, False)
        assert len(result) == 4  # 40 chars / 10 = 4 lines
        assert all(len(line) <= 10 for line in result)
        assert "".join(result) == text

    def test_split_lines_exact_length(self) -> None:
        """Test splitting when text is exactly the max length."""
        text = "exact"
        result = smart_split_lines(text, 5, True)
        assert result == ["exact"]

        result = smart_split_lines(text, 5, False)
        assert result == ["exact"]

    def test_split_lines_shorter_than_max(self) -> None:
        """Test splitting when text is shorter than max length."""
        text = "short"
        result = smart_split_lines(text, 10, True)
        assert result == ["short"]

        result = smart_split_lines(text, 10, False)
        assert result == ["short"]

    def test_split_lines_single_character(self) -> None:
        """Test splitting with max_length of 1."""
        text = "hello"
        result = smart_split_lines(text, 1, False)
        assert result == ["h", "e", "l", "l", "o"]

        # With word preservation, might be different
        result = smart_split_lines(text, 1, True)
        assert len(result) >= 1

    def test_split_lines_empty_string(self) -> None:
        """Test splitting empty string."""
        result = smart_split_lines("", 10, True)
        assert result == []

        result = smart_split_lines("", 10, False)
        assert result == []

    def test_split_lines_whitespace_handling(self) -> None:
        """Test splitting with whitespace handling."""
        text = "hello    world"
        result = smart_split_lines(text, 10, True)
        # textwrap should normalize whitespace
        assert len(result) >= 1

    def test_split_lines_long_word(self) -> None:
        """Test splitting with words longer than max_length."""
        text = "supercalifragilisticexpialidocious"
        result = smart_split_lines(text, 10, True)
        # With preserve_words=True and break_long_words=False,
        # long words might exceed max_length
        assert len(result) >= 1

        result = smart_split_lines(text, 10, False)
        assert len(result) == 4  # 33 chars / 10 = 3.3 -> 4 lines
        assert all(len(line) <= 10 for line in result)

    def test_split_lines_multiple_lines(self) -> None:
        """Test splitting text that already has line breaks."""
        text = "Line 1\nLine 2 is longer than expected\nLine 3"
        result = smart_split_lines(text, 15, True)
        assert len(result) >= 3  # At least one per original line

    def test_split_lines_unicode_text(self) -> None:
        """Test splitting Unicode text."""
        text = "Café résumé naïve approach to the problem"
        result = smart_split_lines(text, 15, True)
        assert len(result) >= 2
        reconstructed = " ".join(result)
        # Account for potential whitespace normalization
        assert "Café" in reconstructed
        assert "résumé" in reconstructed

    def test_split_lines_invalid_max_length(self) -> None:
        """Test error handling for invalid max_length."""
        with pytest.raises(ValueError, match="max_length must be at least 1"):
            smart_split_lines("test", 0, True)

        with pytest.raises(ValueError, match="max_length must be at least 1"):
            smart_split_lines("test", -1, True)

    def test_split_lines_invalid_input(self) -> None:
        """Test error handling for invalid input types."""
        with pytest.raises(TypeError, match="Input must be a string"):
            smart_split_lines(123, 10, True)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="Input must be a string"):
            smart_split_lines(None, 10, True)  # type: ignore[arg-type]


class TestExtractSentences:
    """Test cases for extract_sentences function."""

    def test_extract_basic_sentences(self) -> None:
        """Test extracting basic sentences."""
        text = "Hello world. How are you? Fine!"
        result = extract_sentences(text)
        assert len(result) == 3
        assert "Hello world." in result
        assert "How are you?" in result
        assert "Fine!" in result

    def test_extract_sentences_with_spacing(self) -> None:
        """Test extracting sentences with various spacing."""
        text = "First sentence.  Second sentence!   Third sentence?"
        result = extract_sentences(text)
        assert len(result) == 3
        assert all(sentence.strip() for sentence in result)  # No empty sentences

    def test_extract_single_sentence(self) -> None:
        """Test extracting single sentence."""
        text = "This is a single sentence."
        result = extract_sentences(text)
        assert result == ["This is a single sentence."]

        text = "No punctuation"
        result = extract_sentences(text)
        assert result == ["No punctuation"]

    def test_extract_sentences_multiple_punctuation(self) -> None:
        """Test extracting sentences with multiple punctuation marks."""
        text = "What?!! Really... Yes!"
        result = extract_sentences(text)
        # The regex splits on punctuation, so this might create some empty results
        assert len(result) >= 2
        assert any("What" in sentence for sentence in result)
        assert any("Really" in sentence for sentence in result)

    def test_extract_sentences_no_punctuation(self) -> None:
        """Test extracting from text without sentence punctuation."""
        text = "This text has no sentence punctuation"
        result = extract_sentences(text)
        assert result == ["This text has no sentence punctuation"]

    def test_extract_sentences_empty_string(self) -> None:
        """Test extracting from empty string."""
        result = extract_sentences("")
        assert result == []

    def test_extract_sentences_whitespace_only(self) -> None:
        """Test extracting from whitespace-only string."""
        result = extract_sentences("   \t\n   ")
        assert result == []

    def test_extract_sentences_with_abbreviations(self) -> None:
        """Test extracting sentences with abbreviations."""
        text = "Mr. Smith went to Washington. He met Dr. Johnson."
        result = extract_sentences(text)
        # This simple regex will split on periods, so abbreviations might cause issues
        # The function may not handle abbreviations perfectly
        assert len(result) >= 2

    def test_extract_sentences_mixed_punctuation(self) -> None:
        """Test extracting sentences with mixed punctuation."""
        text = "Are you sure? Yes! Definitely. Maybe..."
        result = extract_sentences(text)
        assert len(result) >= 3
        assert any("Are you sure" in sentence for sentence in result)
        assert any("Yes" in sentence for sentence in result)

    def test_extract_sentences_unicode_text(self) -> None:
        """Test extracting sentences from Unicode text."""
        text = "Café is nice. 北京很大! ¿Cómo estás?"
        result = extract_sentences(text)
        assert len(result) == 3
        assert any("Café" in sentence for sentence in result)
        assert any("北京" in sentence for sentence in result)
        assert any("Cómo" in sentence for sentence in result)

    def test_extract_sentences_preserve_punctuation(self) -> None:
        """Test that sentence extraction preserves punctuation."""
        text = "Question? Statement. Exclamation!"
        result = extract_sentences(text)
        assert any(sentence.endswith("?") for sentence in result)
        assert any(sentence.endswith(".") for sentence in result)
        assert any(sentence.endswith("!") for sentence in result)

    def test_extract_sentences_invalid_input(self) -> None:
        """Test error handling for invalid input types."""
        with pytest.raises(TypeError, match="Input must be a string"):
            extract_sentences(123)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="Input must be a string"):
            extract_sentences(None)  # type: ignore[arg-type]


class TestJoinWithOxfordComma:
    """Test cases for join_with_oxford_comma function."""

    def test_join_empty_list(self) -> None:
        """Test joining empty list."""
        result = join_with_oxford_comma([], "and")
        assert result == ""

    def test_join_single_item(self) -> None:
        """Test joining single item."""
        result = join_with_oxford_comma(["apple"], "and")
        assert result == "apple"

        result = join_with_oxford_comma(["123"], "or")
        assert result == "123"

    def test_join_two_items(self) -> None:
        """Test joining two items."""
        result = join_with_oxford_comma(["apple", "banana"], "and")
        assert result == "apple and banana"

        result = join_with_oxford_comma(["cats", "dogs"], "or")
        assert result == "cats or dogs"

    def test_join_three_items(self) -> None:
        """Test joining three items with Oxford comma."""
        result = join_with_oxford_comma(["apples", "bananas", "oranges"], "and")
        assert result == "apples, bananas, and oranges"

        result = join_with_oxford_comma(["red", "green", "blue"], "or")
        assert result == "red, green, or blue"

    def test_join_four_items(self) -> None:
        """Test joining four items with Oxford comma."""
        result = join_with_oxford_comma(["Alice", "Bob", "Charlie", "Diana"], "and")
        assert result == "Alice, Bob, Charlie, and Diana"

        result = join_with_oxford_comma(["north", "south", "east", "west"], "or")
        assert result == "north, south, east, or west"

    def test_join_many_items(self) -> None:
        """Test joining many items."""
        items = ["one", "two", "three", "four", "five", "six"]
        result = join_with_oxford_comma(items, "and")
        assert result == "one, two, three, four, five, and six"
        assert result.count(",") == 5  # 5 commas total
        assert ", and " in result  # Oxford comma present

    def test_join_different_conjunctions(self) -> None:
        """Test joining with different conjunctions."""
        items = ["coffee", "tea", "water"]

        result = join_with_oxford_comma(items, "and")
        assert result == "coffee, tea, and water"

        result = join_with_oxford_comma(items, "or")
        assert result == "coffee, tea, or water"

        result = join_with_oxford_comma(items, "but not")
        assert result == "coffee, tea, but not water"

    def test_join_mixed_types(self) -> None:
        """Test joining items of mixed types (converted to strings)."""
        # Function expects List[str] so convert items to strings first
        items = ["text", "123", "True", "None"]
        result = join_with_oxford_comma(items, "and")
        assert "text" in result
        assert "123" in result
        assert "True" in result
        assert "None" in result

    def test_join_unicode_items(self) -> None:
        """Test joining Unicode items."""
        items = ["café", "résumé", "naïve"]
        result = join_with_oxford_comma(items, "et")
        assert result == "café, résumé, et naïve"

    def test_join_items_with_spaces(self) -> None:
        """Test joining items that contain spaces."""
        items = ["New York", "Los Angeles", "San Francisco"]
        result = join_with_oxford_comma(items, "and")
        assert result == "New York, Los Angeles, and San Francisco"

    def test_join_long_conjunction(self) -> None:
        """Test joining with longer conjunction phrases."""
        items = ["option A", "option B", "option C"]
        result = join_with_oxford_comma(items, "as well as")
        assert result == "option A, option B, as well as option C"

    def test_join_invalid_input_type(self) -> None:
        """Test error handling for invalid input types."""
        with pytest.raises(TypeError, match="Items must be a list"):
            join_with_oxford_comma("not a list", "and")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="Items must be a list"):
            join_with_oxford_comma(None, "and")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="Items must be a list"):
            join_with_oxford_comma(123, "and")  # type: ignore[arg-type]


class TestTextProcessingIntegration:
    """Integration tests for text processing functions working together."""

    def test_clean_and_normalize_workflow(self) -> None:
        """Test workflow combining cleaning and normalization."""
        # Raw HTML with mixed line endings and extra whitespace
        html_text = "<p>Hello   world!\r\n</p><div>How  are\tyou?</div>"

        # Step 1: Strip HTML
        no_html = strip_html_tags(html_text)

        # Step 2: Clean whitespace
        clean_text = clean_whitespace(no_html)

        # Step 3: Normalize line endings
        normalized = normalize_line_endings(clean_text, "unix")

        assert normalized == "Hello world! How are you?"

    def test_case_conversion_chain(self) -> None:
        """Test chaining case conversion functions."""
        original = "hello-world_example TEST"

        # Convert to snake_case
        snake = to_snake_case(original)
        assert snake == "hello_world_example_test"

        # Convert to camelCase
        camel = to_camel_case(snake, False)
        assert camel == "helloWorldExampleTest"

        # Convert to PascalCase
        pascal = to_camel_case(snake, True)
        assert pascal == "HelloWorldExampleTest"

        # Convert to Title Case (from snake_case)
        title = to_title_case(snake)
        assert title == "Hello_World_Example_Test"

    def test_text_splitting_and_joining(self) -> None:
        """Test splitting text and joining with Oxford comma."""
        long_text = "This is a very long sentence that needs to be split into smaller parts for better readability"

        # Split into lines
        lines = smart_split_lines(long_text, 25, True)
        assert len(lines) > 1

        # Join with Oxford comma
        joined = join_with_oxford_comma(lines, "and")
        assert ", and " in joined  # Oxford comma present

    def test_sentence_extraction_and_case_conversion(self) -> None:
        """Test extracting sentences and converting case."""
        text = "hello world. how are you? i am fine!"

        # Extract sentences
        sentences = extract_sentences(text)

        # Convert each sentence to title case
        title_sentences = [to_title_case(sentence) for sentence in sentences]

        # Join back together
        result = " ".join(title_sentences)

        assert "Hello World." in result
        assert "How Are You?" in result
        assert "I Am Fine!" in result

    def test_unicode_processing_workflow(self) -> None:
        """Test complete Unicode text processing workflow."""
        # Text with various Unicode normalization needs
        unicode_text = "<p>Café résumé</p>\r\n<div>naïve approach</div>"

        # Step 1: Strip HTML
        no_html = strip_html_tags(unicode_text)

        # Step 2: Normalize Unicode to NFC
        normalized_unicode = normalize_unicode(no_html, "NFC")

        # Step 3: Clean whitespace
        clean_text = clean_whitespace(normalized_unicode)

        # Step 4: Convert to title case
        final_text = to_title_case(clean_text)

        assert "Café Résumé" in final_text
        assert "Naïve Approach" in final_text

    def test_comprehensive_text_cleaning(self) -> None:
        """Test comprehensive text cleaning and formatting."""
        messy_text = """
        <html><body>
        <p>  hello    WORLD!!!  </p>
        <div>this-is_a    TEST</div>
        <span>café   résumé</span>
        </body></html>
        """

        # Complete cleaning workflow
        clean = strip_html_tags(messy_text)
        clean = clean_whitespace(clean)
        clean = normalize_unicode(clean, "NFC")
        clean = normalize_line_endings(clean, "unix")

        # Convert to snake_case for consistency
        snake_case = to_snake_case(clean)

        # Should be clean, normalized text
        assert "hello" in snake_case
        assert "world" in snake_case
        assert "test" in snake_case
        assert "café" in snake_case or "cafe" in snake_case
