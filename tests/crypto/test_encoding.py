"""Tests for encoding utilities."""

import base64

import pytest

from basic_open_agent_tools.crypto.encoding import (
    base64_decode,
    base64_encode,
    hex_decode,
    hex_encode,
    url_decode,
    url_encode,
)
from basic_open_agent_tools.exceptions import BasicAgentToolsError


class TestBase64Encode:
    """Test the base64_encode function."""

    def test_invalid_data_type(self):
        """Test error handling for invalid data types."""
        with pytest.raises(BasicAgentToolsError, match="Data must be a string"):
            base64_encode(123)

        with pytest.raises(BasicAgentToolsError, match="Data must be a string"):
            base64_encode(None)

    def test_successful_base64_encoding(self):
        """Test successful Base64 encoding."""
        result = base64_encode("hello world")

        assert result["encoding"] == "base64"
        assert result["original_data"] == "hello world"
        assert result["original_length"] == 11
        assert result["encoded_data"] == "aGVsbG8gd29ybGQ="
        assert result["encoded_length"] == 16

    def test_empty_string_encoding(self):
        """Test Base64 encoding of empty string."""
        result = base64_encode("")

        assert result["original_data"] == ""
        assert result["original_length"] == 0
        assert result["encoded_data"] == ""
        assert result["encoded_length"] == 0

    def test_unicode_string_encoding(self):
        """Test Base64 encoding of Unicode string."""
        unicode_string = "hello 🌍"
        result = base64_encode(unicode_string)

        assert result["original_data"] == unicode_string
        assert len(result["encoded_data"]) > 0

        # Verify it can be decoded back
        decoded = base64.b64decode(result["encoded_data"]).decode("utf-8")
        assert decoded == unicode_string

    def test_special_characters_encoding(self):
        """Test Base64 encoding with special characters."""
        special_string = "!@#$%^&*()_+-=[]{}|;:',.<>?"
        result = base64_encode(special_string)

        assert result["original_data"] == special_string
        assert len(result["encoded_data"]) > 0


class TestBase64Decode:
    """Test the base64_decode function."""

    def test_invalid_data_type(self):
        """Test error handling for invalid data types."""
        with pytest.raises(BasicAgentToolsError, match="Encoded data must be a string"):
            base64_decode(123)

        with pytest.raises(BasicAgentToolsError, match="Encoded data must be a string"):
            base64_decode(None)

    def test_empty_encoded_data(self):
        """Test error handling for empty encoded data."""
        with pytest.raises(BasicAgentToolsError, match="Encoded data cannot be empty"):
            base64_decode("")

        with pytest.raises(BasicAgentToolsError, match="Encoded data cannot be empty"):
            base64_decode("   ")

    def test_successful_base64_decoding(self):
        """Test successful Base64 decoding."""
        result = base64_decode("aGVsbG8gd29ybGQ=")

        assert result["encoding"] == "base64"
        assert result["encoded_data"] == "aGVsbG8gd29ybGQ="
        assert result["encoded_length"] == 16
        assert result["decoded_data"] == "hello world"
        assert result["decoded_length"] == 11

    def test_invalid_base64_data(self):
        """Test error handling for invalid Base64 data."""
        with pytest.raises(BasicAgentToolsError, match="Failed to decode Base64 data"):
            base64_decode("invalid_base64!")

    def test_roundtrip_encoding_decoding(self):
        """Test that encoding and decoding are inverse operations."""
        original_data = "The quick brown fox jumps over the lazy dog"

        encoded_result = base64_encode(original_data)
        decoded_result = base64_decode(encoded_result["encoded_data"])

        assert decoded_result["decoded_data"] == original_data


class TestUrlEncode:
    """Test the url_encode function."""

    def test_invalid_data_type(self):
        """Test error handling for invalid data types."""
        with pytest.raises(BasicAgentToolsError, match="Data must be a string"):
            url_encode(123)

    def test_successful_url_encoding(self):
        """Test successful URL encoding."""
        result = url_encode("hello world")

        assert result["encoding"] == "url"
        assert result["original_data"] == "hello world"
        assert result["original_length"] == 11
        assert result["encoded_data"] == "hello%20world"
        assert result["encoded_length"] == 13

    def test_special_characters_url_encoding(self):
        """Test URL encoding with special characters."""
        special_string = "hello@example.com?param=value&other=123"
        result = url_encode(special_string)

        assert result["original_data"] == special_string
        assert "%40" in result["encoded_data"]  # @ encoded
        assert "%3F" in result["encoded_data"]  # ? encoded
        assert "%3D" in result["encoded_data"]  # = encoded
        assert "%26" in result["encoded_data"]  # & encoded

    def test_empty_string_url_encoding(self):
        """Test URL encoding of empty string."""
        result = url_encode("")

        assert result["original_data"] == ""
        assert result["encoded_data"] == ""


class TestUrlDecode:
    """Test the url_decode function."""

    def test_invalid_data_type(self):
        """Test error handling for invalid data types."""
        with pytest.raises(BasicAgentToolsError, match="Encoded data must be a string"):
            url_decode(123)

    def test_successful_url_decoding(self):
        """Test successful URL decoding."""
        result = url_decode("hello%20world")

        assert result["encoding"] == "url"
        assert result["encoded_data"] == "hello%20world"
        assert result["encoded_length"] == 13
        assert result["decoded_data"] == "hello world"
        assert result["decoded_length"] == 11

    def test_special_characters_url_decoding(self):
        """Test URL decoding with special characters."""
        encoded_string = "hello%40example.com%3Fparam%3Dvalue%26other%3D123"
        result = url_decode(encoded_string)

        expected = "hello@example.com?param=value&other=123"
        assert result["decoded_data"] == expected

    def test_roundtrip_url_encoding_decoding(self):
        """Test that URL encoding and decoding are inverse operations."""
        original_data = "hello world!@#$%^&*()"

        encoded_result = url_encode(original_data)
        decoded_result = url_decode(encoded_result["encoded_data"])

        assert decoded_result["decoded_data"] == original_data


class TestHexEncode:
    """Test the hex_encode function."""

    def test_invalid_data_type(self):
        """Test error handling for invalid data types."""
        with pytest.raises(BasicAgentToolsError, match="Data must be a string"):
            hex_encode(123)

    def test_successful_hex_encoding(self):
        """Test successful hex encoding."""
        result = hex_encode("hello")

        assert result["encoding"] == "hex"
        assert result["original_data"] == "hello"
        assert result["original_length"] == 5
        assert result["encoded_data"] == "68656c6c6f"
        assert result["encoded_length"] == 10

    def test_empty_string_hex_encoding(self):
        """Test hex encoding of empty string."""
        result = hex_encode("")

        assert result["original_data"] == ""
        assert result["encoded_data"] == ""

    def test_unicode_hex_encoding(self):
        """Test hex encoding of Unicode string."""
        unicode_string = "🌍"
        result = hex_encode(unicode_string)

        assert result["original_data"] == unicode_string
        assert len(result["encoded_data"]) > 0

        # Unicode characters should encode to multiple bytes
        assert len(result["encoded_data"]) > 2

    def test_special_characters_hex_encoding(self):
        """Test hex encoding with special characters."""
        special_string = "ABC123!@#"
        result = hex_encode(special_string)

        assert result["original_data"] == special_string
        assert len(result["encoded_data"]) == len(special_string.encode("utf-8")) * 2


class TestHexDecode:
    """Test the hex_decode function."""

    def test_invalid_data_type(self):
        """Test error handling for invalid data types."""
        with pytest.raises(BasicAgentToolsError, match="Encoded data must be a string"):
            hex_decode(123)

    def test_empty_encoded_data(self):
        """Test error handling for empty encoded data."""
        with pytest.raises(BasicAgentToolsError, match="Encoded data cannot be empty"):
            hex_decode("")

        with pytest.raises(BasicAgentToolsError, match="Encoded data cannot be empty"):
            hex_decode("   ")

    def test_successful_hex_decoding(self):
        """Test successful hex decoding."""
        result = hex_decode("68656c6c6f")

        assert result["encoding"] == "hex"
        assert result["encoded_data"] == "68656c6c6f"
        assert result["encoded_length"] == 10
        assert result["decoded_data"] == "hello"
        assert result["decoded_length"] == 5

    def test_odd_length_hex_string(self):
        """Test error handling for hex string with odd number of characters."""
        with pytest.raises(
            BasicAgentToolsError, match="Hex string must have even number of characters"
        ):
            hex_decode("68656c6c6")  # Missing last character

    def test_invalid_hex_characters(self):
        """Test error handling for invalid hex characters."""
        with pytest.raises(BasicAgentToolsError, match="Invalid hexadecimal string"):
            hex_decode("68656c6g6f")  # 'g' is not a valid hex character

    def test_invalid_utf8_sequence(self):
        """Test error handling for hex that doesn't decode to valid UTF-8."""
        # This hex sequence represents invalid UTF-8
        with pytest.raises(
            BasicAgentToolsError,
            match="Decoded bytes do not represent valid UTF-8 text",
        ):
            hex_decode("ff")  # 0xFF is not valid UTF-8

    def test_roundtrip_hex_encoding_decoding(self):
        """Test that hex encoding and decoding are inverse operations."""
        original_data = "The quick brown fox"

        encoded_result = hex_encode(original_data)
        decoded_result = hex_decode(encoded_result["encoded_data"])

        assert decoded_result["decoded_data"] == original_data

    def test_uppercase_hex_decoding(self):
        """Test hex decoding with uppercase characters."""
        result = hex_decode("48454C4C4F")  # "HELLO" in uppercase hex

        assert result["decoded_data"] == "HELLO"

    def test_mixed_case_hex_decoding(self):
        """Test hex decoding with mixed case characters."""
        result = hex_decode("48656C6c6F")  # Mixed case hex for "Hello"

        assert result["decoded_data"] == "Hello"
