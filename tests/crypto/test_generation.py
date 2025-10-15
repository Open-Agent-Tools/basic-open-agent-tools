"""Tests for generation utilities."""

import re
import uuid

import pytest

from basic_open_agent_tools.crypto.generation import (
    generate_random_bytes,
    generate_random_string,
    generate_uuid,
)
from basic_open_agent_tools.exceptions import BasicAgentToolsError


class TestGenerateUuid:
    """Test the generate_uuid function."""

    def test_invalid_version(self):
        """Test error handling for invalid UUID versions."""
        with pytest.raises(BasicAgentToolsError, match="Version must be 1 or 4"):
            generate_uuid(version=2)

        with pytest.raises(BasicAgentToolsError, match="Version must be 1 or 4"):
            generate_uuid(version=5)

        with pytest.raises(BasicAgentToolsError, match="Version must be 1 or 4"):
            generate_uuid(version="4")

    def test_successful_uuid4_generation(self):
        """Test successful UUID4 generation."""
        result = generate_uuid(version=4)

        assert result["uuid_version"] == 4
        assert result["uuid_type"] == "random"
        assert isinstance(result["uuid_string"], str)
        assert isinstance(result["uuid_hex"], str)
        assert result["uuid_bytes_length"] == 16
        assert result["uuid_string_length"] == 36  # Standard UUID string length

        # Verify UUID format
        uuid_pattern = (
            r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        )
        assert re.match(uuid_pattern, result["uuid_string"])

        # Verify hex format (no dashes)
        assert len(result["uuid_hex"]) == 32
        assert re.match(r"^[0-9a-f]{32}$", result["uuid_hex"])

    def test_successful_uuid1_generation(self):
        """Test successful UUID1 generation."""
        result = generate_uuid(version=1)

        assert result["uuid_version"] == 1
        assert result["uuid_type"] == "time-based (includes MAC address)"
        assert isinstance(result["uuid_string"], str)
        assert result["uuid_string_length"] == 36

        # Verify UUID format (UUID1 has version 1 in the version field)
        uuid_pattern = (
            r"^[0-9a-f]{8}-[0-9a-f]{4}-1[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        )
        assert re.match(uuid_pattern, result["uuid_string"])

    def test_version_4_is_random(self):
        """Test that version 4 produces random UUIDs."""
        result = generate_uuid(version=4)

        assert result["uuid_version"] == 4
        assert result["uuid_type"] == "random"

    def test_uuid_uniqueness(self):
        """Test that generated UUIDs are unique."""
        uuid1 = generate_uuid(version=4)
        uuid2 = generate_uuid(version=4)

        assert uuid1["uuid_string"] != uuid2["uuid_string"]
        assert uuid1["uuid_hex"] != uuid2["uuid_hex"]

    def test_uuid_parsing_compatibility(self):
        """Test that generated UUIDs can be parsed by standard UUID library."""
        result = generate_uuid(version=4)

        # Should be able to parse without error
        parsed_uuid = uuid.UUID(result["uuid_string"])
        assert str(parsed_uuid) == result["uuid_string"]
        assert parsed_uuid.hex == result["uuid_hex"]


class TestGenerateRandomString:
    """Test the generate_random_string function."""

    def test_invalid_length(self):
        """Test error handling for invalid length values."""
        with pytest.raises(
            BasicAgentToolsError, match="Length must be an integer between 1 and 1000"
        ):
            generate_random_string(length=0, character_set="alphanumeric")

        with pytest.raises(
            BasicAgentToolsError, match="Length must be an integer between 1 and 1000"
        ):
            generate_random_string(length=-1, character_set="alphanumeric")

        with pytest.raises(
            BasicAgentToolsError, match="Length must be an integer between 1 and 1000"
        ):
            generate_random_string(length=1001, character_set="alphanumeric")

        with pytest.raises(
            BasicAgentToolsError, match="Length must be an integer between 1 and 1000"
        ):
            generate_random_string(length="16", character_set="alphanumeric")

    def test_invalid_character_set(self):
        """Test error handling for invalid character set."""
        with pytest.raises(
            BasicAgentToolsError, match="Character set must be a string"
        ):
            generate_random_string(length=10, character_set=123)

        with pytest.raises(BasicAgentToolsError, match="Character set must be one of"):
            generate_random_string(length=10, character_set="invalid")

    def test_successful_alphanumeric_generation(self):
        """Test successful alphanumeric random string generation."""
        result = generate_random_string(length=20, character_set="alphanumeric")

        assert result["requested_length"] == 20
        assert result["actual_length"] == 20
        assert result["character_set"] == "alphanumeric"
        assert len(result["random_string"]) == 20

        # Verify only alphanumeric characters
        assert re.match(r"^[a-zA-Z0-9]+$", result["random_string"])

    def test_successful_letters_generation(self):
        """Test successful letters-only random string generation."""
        result = generate_random_string(length=15, character_set="letters")

        assert result["character_set"] == "letters"
        assert len(result["random_string"]) == 15

        # Verify only letters
        assert re.match(r"^[a-zA-Z]+$", result["random_string"])

    def test_successful_digits_generation(self):
        """Test successful digits-only random string generation."""
        result = generate_random_string(length=10, character_set="digits")

        assert result["character_set"] == "digits"
        assert len(result["random_string"]) == 10

        # Verify only digits
        assert re.match(r"^[0-9]+$", result["random_string"])

    def test_successful_ascii_generation(self):
        """Test successful ASCII random string generation."""
        result = generate_random_string(length=25, character_set="ascii")

        assert result["character_set"] == "ascii"
        assert len(result["random_string"]) == 25

        # Should contain letters, digits, and punctuation
        # Just verify it's ASCII printable
        assert all(ord(c) < 128 and ord(c) >= 32 for c in result["random_string"])

    def test_common_alphanumeric_generation(self):
        """Test common alphanumeric generation with standard length."""
        result = generate_random_string(length=16, character_set="alphanumeric")

        assert result["requested_length"] == 16
        assert result["actual_length"] == 16
        assert result["character_set"] == "alphanumeric"

    def test_character_set_size_calculation(self):
        """Test that character set size is calculated correctly."""
        result_alpha = generate_random_string(length=10, character_set="alphanumeric")
        result_letters = generate_random_string(length=10, character_set="letters")
        result_digits = generate_random_string(length=10, character_set="digits")

        assert result_alpha["character_set_size"] == 62  # 26+26+10
        assert result_letters["character_set_size"] == 52  # 26+26
        assert result_digits["character_set_size"] == 10  # 10

    def test_string_uniqueness(self):
        """Test that generated strings are unique."""
        result1 = generate_random_string(length=20, character_set="alphanumeric")
        result2 = generate_random_string(length=20, character_set="alphanumeric")

        assert result1["random_string"] != result2["random_string"]

    def test_case_insensitive_character_set(self):
        """Test that character set parameter is case-insensitive."""
        result_lower = generate_random_string(length=10, character_set="alphanumeric")
        result_upper = generate_random_string(length=10, character_set="ALPHANUMERIC")
        result_mixed = generate_random_string(length=10, character_set="AlPhAnUmErIc")

        assert result_lower["character_set"] == "alphanumeric"
        assert result_upper["character_set"] == "alphanumeric"
        assert result_mixed["character_set"] == "alphanumeric"


class TestGenerateRandomBytes:
    """Test the generate_random_bytes function."""

    def test_invalid_length(self):
        """Test error handling for invalid length values."""
        with pytest.raises(
            BasicAgentToolsError, match="Length must be an integer between 1 and 1000"
        ):
            generate_random_bytes(length=0, encoding="hex")

        with pytest.raises(
            BasicAgentToolsError, match="Length must be an integer between 1 and 1000"
        ):
            generate_random_bytes(length=-1, encoding="hex")

        with pytest.raises(
            BasicAgentToolsError, match="Length must be an integer between 1 and 1000"
        ):
            generate_random_bytes(length=1001, encoding="hex")

    def test_invalid_encoding(self):
        """Test error handling for invalid encoding."""
        with pytest.raises(BasicAgentToolsError, match="Encoding must be a string"):
            generate_random_bytes(length=16, encoding=123)

        with pytest.raises(
            BasicAgentToolsError, match="Encoding must be 'hex' or 'base64'"
        ):
            generate_random_bytes(length=16, encoding="invalid")

    def test_successful_hex_encoding(self):
        """Test successful random bytes generation with hex encoding."""
        result = generate_random_bytes(length=16, encoding="hex")

        assert result["random_bytes_length"] == 16
        assert result["encoding"] == "hex"
        assert result["encoded_length"] == 32  # 16 bytes = 32 hex chars
        assert result["entropy_bits"] == 128  # 16 * 8

        # Verify hex format
        assert re.match(r"^[0-9a-f]+$", result["encoded_data"])

    def test_successful_base64_encoding(self):
        """Test successful random bytes generation with base64 encoding."""
        result = generate_random_bytes(length=16, encoding="base64")

        assert result["random_bytes_length"] == 16
        assert result["encoding"] == "base64"
        assert result["entropy_bits"] == 128

        # Base64 encoding should produce valid base64
        import base64

        try:
            base64.b64decode(result["encoded_data"])
        except Exception:
            pytest.fail("Generated data is not valid base64")

    def test_common_hex_generation(self):
        """Test common hex generation with standard length."""
        result = generate_random_bytes(length=16, encoding="hex")

        assert result["random_bytes_length"] == 16
        assert result["encoding"] == "hex"

    def test_bytes_uniqueness(self):
        """Test that generated bytes are unique."""
        result1 = generate_random_bytes(length=32, encoding="hex")
        result2 = generate_random_bytes(length=32, encoding="hex")

        assert result1["encoded_data"] != result2["encoded_data"]

    def test_entropy_calculation(self):
        """Test that entropy is calculated correctly."""
        result8 = generate_random_bytes(length=8, encoding="hex")
        result16 = generate_random_bytes(length=16, encoding="hex")
        result32 = generate_random_bytes(length=32, encoding="hex")

        assert result8["entropy_bits"] == 64  # 8 * 8
        assert result16["entropy_bits"] == 128  # 16 * 8
        assert result32["entropy_bits"] == 256  # 32 * 8

    def test_case_insensitive_encoding(self):
        """Test that encoding parameter is case-insensitive."""
        result_lower = generate_random_bytes(length=16, encoding="hex")
        result_upper = generate_random_bytes(length=16, encoding="HEX")
        result_mixed = generate_random_bytes(length=16, encoding="HeX")

        assert result_lower["encoding"] == "hex"
        assert result_upper["encoding"] == "hex"
        assert result_mixed["encoding"] == "hex"

    def test_encoded_length_relationship(self):
        """Test the relationship between byte length and encoded length."""
        # Hex encoding: each byte becomes 2 hex characters
        hex_result = generate_random_bytes(length=20, encoding="hex")
        assert hex_result["encoded_length"] == 40

        # Base64 encoding: more complex relationship, but should be consistent
        b64_result = generate_random_bytes(length=21, encoding="base64")
        assert len(b64_result["encoded_data"]) == b64_result["encoded_length"]
