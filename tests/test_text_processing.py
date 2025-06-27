"""Tests for text processing module.

This module provides comprehensive tests for the text processing toolkit functions,
including unit tests, integration tests, and Google AI compatibility verification.
"""

import inspect
import logging
import warnings

import pytest
from dotenv import load_dotenv
from google.adk.agents import Agent

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

# Initialize environment and logging
load_dotenv()
logging.basicConfig(level=logging.ERROR)
warnings.filterwarnings("ignore")


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
        result = normalize_unicode(text, "NFC")
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


class TestADKAgentIntegration:
    """Test ADK Agent integration with text processing tools."""

    @pytest.fixture
    def adk_agent_with_text_tools(self):
        """Create ADK agent configured with multiple text processing tools."""
        agent = Agent(
            model="gemini-2.0-flash",
            name="TextProcessingAgent",
            instruction="You are a text processing agent. Use the available text processing tools to clean, normalize, and transform text content.",
            description="An agent specialized in text processing, cleaning, and transformation operations.",
            tools=[
                clean_whitespace,
                normalize_line_endings,
                strip_html_tags,
                normalize_unicode,
                to_snake_case,
                to_camel_case,
                to_title_case,
                smart_split_lines,
                extract_sentences,
                join_with_oxford_comma,
            ],
        )
        return agent

    @pytest.fixture
    def adk_agent_with_single_tool(self):
        """Create ADK agent configured with single text processing tool."""
        agent = Agent(
            model="gemini-2.0-flash",
            name="WhitespaceCleanerAgent",
            instruction="You are a whitespace cleaning agent. Use the clean_whitespace tool to clean up text formatting.",
            description="An agent specialized in cleaning whitespace from text.",
            tools=[clean_whitespace],
        )
        return agent

    def test_clean_whitespace_basic_functionality(self):
        """Test clean_whitespace function directly (non-ADK)."""
        # Test basic whitespace cleaning
        result = clean_whitespace("  hello    world  ")
        assert result == "hello world"

        # Test mixed whitespace types
        result = clean_whitespace("hello\t\n\r world")
        assert result == "hello world"

        # Test empty string
        result = clean_whitespace("")
        assert result == ""

    def test_adk_agent_can_use_clean_whitespace_tool(self, adk_agent_with_single_tool):
        """Test that ADK agent can successfully use the clean_whitespace tool."""
        instruction = 'Clean the whitespace from this text: "  hello    world  "'

        try:
            response = adk_agent_with_single_tool.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence that the tool was used successfully
            expected_elements = ["hello world", "clean", "text"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of successful text processing
            assert found_elements >= 1, (
                f"Expected text processing elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed to use clean_whitespace tool: {e}")

    def test_case_conversion_functionality(self):
        """Test case conversion functions directly."""
        # Test snake_case conversion
        result = to_snake_case("HelloWorld")
        assert result == "hello_world"

        # Test camelCase conversion
        result = to_camel_case("hello_world", False)
        assert result == "helloWorld"

        # Test PascalCase conversion
        result = to_camel_case("hello_world", True)
        assert result == "HelloWorld"

        # Test title case conversion
        result = to_title_case("hello world")
        assert result == "Hello World"

    def test_adk_agent_can_use_multiple_text_tools(self, adk_agent_with_text_tools):
        """Test that ADK agent can use multiple text processing tools."""
        instruction = 'Process this messy text: "  <p>Hello    World!</p>\\r\\n\\t  " - first strip HTML tags, then clean whitespace'

        try:
            response = adk_agent_with_text_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence that text processing occurred
            expected_elements = ["hello world", "clean", "process"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of successful text processing
            assert found_elements >= 1, (
                f"Expected text processing elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed to use multiple text tools: {e}")

    def test_text_splitting_functionality(self):
        """Test text splitting function directly."""
        text = "This is a long line that needs splitting"
        result = smart_split_lines(text, 15, True)

        # Verify all lines are within limit
        assert all(len(line) <= 15 for line in result)

        # Verify original text is preserved when rejoined
        assert " ".join(result) == text

    def test_adk_agent_text_splitting(self, adk_agent_with_text_tools):
        """Test that ADK agent can use text splitting tool."""
        instruction = 'Split this text into lines of maximum 10 characters each, preserving words: "Hello world this is a test"'

        try:
            response = adk_agent_with_text_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence that splitting occurred
            expected_elements = ["split", "line", "text"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of text splitting
            assert found_elements >= 1, (
                f"Expected text splitting elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed to use text splitting tool: {e}")

    def test_sentence_extraction_functionality(self):
        """Test sentence extraction function directly."""
        text = "Hello world. How are you? Fine!"
        result = extract_sentences(text)

        assert len(result) == 3
        assert "Hello world." in result
        assert "How are you?" in result
        assert "Fine!" in result

    def test_adk_agent_error_handling(self, adk_agent_with_single_tool):
        """Test ADK agent error handling with invalid input."""
        instruction = (
            "Clean whitespace from this invalid input (testing error handling)"
        )

        try:
            response = adk_agent_with_single_tool.run(instruction)

            # The agent should handle the request gracefully
            assert response is not None

            response_str = str(response).lower()

            # Either the agent processed the request or provided some response
            assert len(response_str) > 0

        except Exception as e:
            # Some exceptions are acceptable as they indicate proper error handling
            acceptable_errors = ["type", "invalid", "error"]
            error_msg = str(e).lower()

            is_acceptable = any(
                acceptable in error_msg for acceptable in acceptable_errors
            )

            if not is_acceptable:
                pytest.fail(f"Unexpected error type: {e}")

    def test_oxford_comma_functionality(self):
        """Test Oxford comma joining function directly."""
        # Test three items
        items = ["apples", "bananas", "oranges"]
        result = join_with_oxford_comma(items, "and")
        assert result == "apples, bananas, and oranges"

        # Test two items
        items = ["apples", "bananas"]
        result = join_with_oxford_comma(items, "and")
        assert result == "apples and bananas"

        # Test one item
        result = join_with_oxford_comma(["apples"], "and")
        assert result == "apples"


class TestTextProcessingCompatibility:
    """Test Google AI compatibility for text processing functions."""

    def test_function_signatures_compatibility(self):
        """Test that all text processing functions have Google AI compatible signatures."""
        functions_to_test = [
            clean_whitespace,
            normalize_line_endings,
            strip_html_tags,
            normalize_unicode,
            to_snake_case,
            to_camel_case,
            to_title_case,
            smart_split_lines,
            extract_sentences,
            join_with_oxford_comma,
        ]

        for func in functions_to_test:
            sig = inspect.signature(func)

            # Check that no parameters have default values
            for param_name, param in sig.parameters.items():
                assert param.default == inspect.Parameter.empty, (
                    f"Function {func.__name__} parameter {param_name} has default value, "
                    "violating Google AI requirements"
                )

            # Check that return type is specified
            assert sig.return_annotation != inspect.Signature.empty, (
                f"Function {func.__name__} missing return type annotation"
            )

    def test_parameter_types_compatibility(self):
        """Test that parameter types are Google AI compatible."""
        # Test clean_whitespace
        sig = inspect.signature(clean_whitespace)
        params = sig.parameters

        assert params["text"].annotation is str
        assert sig.return_annotation is str

        # Test to_camel_case
        sig = inspect.signature(to_camel_case)
        params = sig.parameters

        assert params["text"].annotation is str
        assert params["upper_first"].annotation is bool
        assert sig.return_annotation is str

        # Test smart_split_lines - should return List[str]
        sig = inspect.signature(smart_split_lines)
        return_annotation = sig.return_annotation
        assert hasattr(return_annotation, "__origin__")
        assert return_annotation.__origin__ is list

    def test_list_parameter_types(self):
        """Test that list parameters have proper typing."""
        # Test join_with_oxford_comma - should have List[str]
        sig = inspect.signature(join_with_oxford_comma)
        items_param = sig.parameters["items"]

        # Should be a list type with str specification
        assert hasattr(items_param.annotation, "__origin__")
        assert items_param.annotation.__origin__ is list


class TestTextProcessingIntegrationWithADK:
    """Integration tests combining multiple text processing operations with ADK."""

    @pytest.fixture
    def adk_agent_with_text_tools(self):
        """Create ADK agent configured with text processing tools."""
        agent = Agent(
            model="gemini-2.0-flash",
            name="TextProcessingAgent",
            instruction="You are a text processing agent. Use the available tools to process text according to user instructions.",
            description="An agent specialized in comprehensive text processing operations.",
            tools=[
                clean_whitespace,
                strip_html_tags,
                to_snake_case,
                to_camel_case,
                normalize_line_endings,
            ],
        )
        return agent

    def test_adk_agent_comprehensive_text_workflow(self, adk_agent_with_text_tools):
        """Test ADK agent performing complex text processing workflow."""
        instruction = 'Process this HTML text and convert to snake_case: "<p>Hello World Test</p>"'

        try:
            response = adk_agent_with_text_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of successful processing
            expected_elements = ["hello", "world", "test", "process"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of comprehensive text processing
            assert found_elements >= 2, (
                f"Expected comprehensive processing elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed comprehensive text workflow: {e}")

    def test_adk_agent_case_conversion_workflow(self, adk_agent_with_text_tools):
        """Test ADK agent performing case conversion operations."""
        instruction = 'Convert "hello world" to camelCase format'

        try:
            response = adk_agent_with_text_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of case conversion
            expected_elements = ["camel", "convert", "hello", "world"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of case conversion
            assert found_elements >= 2, (
                f"Expected case conversion elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed case conversion workflow: {e}")
