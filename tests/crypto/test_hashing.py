"""Tests for hashing utilities."""

import pytest
import tempfile
import os
from unittest.mock import patch, mock_open

from basic_open_agent_tools.crypto.hashing import (
    hash_md5,
    hash_sha256,
    hash_sha512,
    hash_file,
    verify_checksum,
)
from basic_open_agent_tools.exceptions import BasicAgentToolsError


class TestHashMd5:
    """Test the hash_md5 function."""

    def test_invalid_data_type(self):
        """Test error handling for invalid data types."""
        with pytest.raises(BasicAgentToolsError, match="Data must be a string"):
            hash_md5(123)

        with pytest.raises(BasicAgentToolsError, match="Data must be a string"):
            hash_md5(None)

    def test_successful_md5_hash(self):
        """Test successful MD5 hash generation."""
        result = hash_md5("hello world")

        assert result["algorithm"] == "md5"
        assert result["input_data"] == "hello world"
        assert result["input_length"] == 11
        assert result["hash_hex"] == "5eb63bbbe01eeed093cb22bb8f5acdc3"
        assert result["hash_length"] == 32

    def test_empty_string_hash(self):
        """Test MD5 hash of empty string."""
        result = hash_md5("")

        assert result["algorithm"] == "md5"
        assert result["input_data"] == ""
        assert result["input_length"] == 0
        assert result["hash_hex"] == "d41d8cd98f00b204e9800998ecf8427e"

    def test_unicode_string_hash(self):
        """Test MD5 hash of Unicode string."""
        unicode_string = "hello 🌍"
        result = hash_md5(unicode_string)

        assert result["algorithm"] == "md5"
        assert result["input_data"] == unicode_string
        assert len(result["hash_hex"]) == 32


class TestHashSha256:
    """Test the hash_sha256 function."""

    def test_invalid_data_type(self):
        """Test error handling for invalid data types."""
        with pytest.raises(BasicAgentToolsError, match="Data must be a string"):
            hash_sha256(123)

    def test_successful_sha256_hash(self):
        """Test successful SHA-256 hash generation."""
        result = hash_sha256("hello world")

        assert result["algorithm"] == "sha256"
        assert result["input_data"] == "hello world"
        assert result["input_length"] == 11
        assert result["hash_hex"] == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
        assert result["hash_length"] == 64

    def test_empty_string_hash(self):
        """Test SHA-256 hash of empty string."""
        result = hash_sha256("")

        assert result["algorithm"] == "sha256"
        assert result["hash_hex"] == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


class TestHashSha512:
    """Test the hash_sha512 function."""

    def test_invalid_data_type(self):
        """Test error handling for invalid data types."""
        with pytest.raises(BasicAgentToolsError, match="Data must be a string"):
            hash_sha512(None)

    def test_successful_sha512_hash(self):
        """Test successful SHA-512 hash generation."""
        result = hash_sha512("hello world")

        assert result["algorithm"] == "sha512"
        assert result["input_data"] == "hello world"
        assert result["input_length"] == 11
        expected_hash = "309ecc489c12d6eb4cc40f50c902f2b4d0ed77ee511a7c7a9bcd3ca86d4cd86f989dd35bc5ff499670da34255b45b0cfd830e81f605dcf7dc5542e93ae9cd76f"
        assert result["hash_hex"] == expected_hash
        assert result["hash_length"] == 128


class TestHashFile:
    """Test the hash_file function."""

    def test_invalid_file_path_type(self):
        """Test error handling for invalid file path types."""
        with pytest.raises(BasicAgentToolsError, match="File path must be a non-empty string"):
            hash_file("")

        with pytest.raises(BasicAgentToolsError, match="File path must be a non-empty string"):
            hash_file(None)

        with pytest.raises(BasicAgentToolsError, match="File path must be a non-empty string"):
            hash_file("   ")

    def test_invalid_algorithm(self):
        """Test error handling for invalid algorithm."""
        with pytest.raises(BasicAgentToolsError, match="Algorithm must be one of"):
            hash_file("/tmp/test.txt", algorithm="sha1")

        with pytest.raises(BasicAgentToolsError, match="Algorithm must be one of"):
            hash_file("/tmp/test.txt", algorithm="")

    def test_file_not_found(self):
        """Test error handling when file doesn't exist."""
        with pytest.raises(BasicAgentToolsError, match="File not found"):
            hash_file("/nonexistent/path/file.txt")

    def test_successful_file_hash_sha256(self):
        """Test successful file hashing with SHA-256."""
        test_content = "hello world\n"

        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(test_content.encode('utf-8'))
            temp_file_path = f.name

        try:
            result = hash_file(temp_file_path, algorithm="sha256")

            assert result["algorithm"] == "sha256"
            assert result["file_path"] == temp_file_path
            assert result["file_size_bytes"] == len(test_content.encode('utf-8'))
            assert len(result["hash_hex"]) == 64
            assert result["hash_length"] == 64

        finally:
            os.unlink(temp_file_path)

    def test_successful_file_hash_md5(self):
        """Test successful file hashing with MD5."""
        test_content = "test content"

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(test_content)
            temp_file_path = f.name

        try:
            result = hash_file(temp_file_path, algorithm="md5")

            assert result["algorithm"] == "md5"
            assert len(result["hash_hex"]) == 32

        finally:
            os.unlink(temp_file_path)

    def test_directory_instead_of_file(self):
        """Test error handling when path is a directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(BasicAgentToolsError, match="Path is not a file"):
                hash_file(temp_dir)

    def test_large_file_chunked_reading(self):
        """Test that large files are read in chunks."""
        # Create a file larger than typical chunk size
        large_content = "x" * (100 * 1024)  # 100KB

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(large_content)
            temp_file_path = f.name

        try:
            result = hash_file(temp_file_path, algorithm="sha256")

            assert result["file_size_bytes"] == len(large_content.encode('utf-8'))
            assert len(result["hash_hex"]) == 64

        finally:
            os.unlink(temp_file_path)


class TestVerifyChecksum:
    """Test the verify_checksum function."""

    def test_invalid_data_type(self):
        """Test error handling for invalid data types."""
        with pytest.raises(BasicAgentToolsError, match="Data must be a string"):
            verify_checksum(123, "abcdef123456")

    def test_invalid_expected_hash_type(self):
        """Test error handling for invalid expected hash types."""
        with pytest.raises(BasicAgentToolsError, match="Expected hash must be a non-empty string"):
            verify_checksum("test", "")

        with pytest.raises(BasicAgentToolsError, match="Expected hash must be a non-empty string"):
            verify_checksum("test", None)

    def test_invalid_algorithm(self):
        """Test error handling for invalid algorithm."""
        with pytest.raises(BasicAgentToolsError, match="Algorithm must be one of"):
            verify_checksum("test", "abcdef", algorithm="sha1")

    def test_invalid_hex_format(self):
        """Test error handling for invalid hex format in expected hash."""
        with pytest.raises(BasicAgentToolsError, match="Expected hash must be a valid hexadecimal string"):
            verify_checksum("test", "not_hex_format")

        with pytest.raises(BasicAgentToolsError, match="Expected hash must be a valid hexadecimal string"):
            verify_checksum("test", "gggggg")

    def test_successful_checksum_verification_valid(self):
        """Test successful checksum verification with valid hash."""
        data = "hello world"
        expected_hash = "5eb63bbbe01eeed093cb22bb8f5acdc3"  # MD5 of "hello world"

        result = verify_checksum(data, expected_hash, algorithm="md5")

        assert result["algorithm"] == "md5"
        assert result["data_length"] == 11
        assert result["expected_hash"] == expected_hash.lower()
        assert result["calculated_hash"] == expected_hash.lower()
        assert result["matches"] is True
        assert result["verification_result"] == "valid"

    def test_successful_checksum_verification_invalid(self):
        """Test successful checksum verification with invalid hash."""
        data = "hello world"
        wrong_hash = "0000000000000000000000000000000"  # Wrong MD5 hash

        result = verify_checksum(data, wrong_hash, algorithm="md5")

        assert result["matches"] is False
        assert result["verification_result"] == "invalid"
        assert result["expected_hash"] != result["calculated_hash"]

    def test_case_insensitive_hash_comparison(self):
        """Test that hash comparison is case-insensitive."""
        data = "hello world"
        uppercase_hash = "5EB63BBBE01EEED093CB22BB8F5ACDC3"  # MD5 in uppercase

        result = verify_checksum(data, uppercase_hash, algorithm="md5")

        assert result["matches"] is True
        assert result["expected_hash"] == uppercase_hash.lower()

    def test_sha256_verification(self):
        """Test checksum verification with SHA-256."""
        data = "test"
        expected_hash = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"

        result = verify_checksum(data, expected_hash, algorithm="sha256")

        assert result["algorithm"] == "sha256"
        assert result["matches"] is True

    def test_sha512_verification(self):
        """Test checksum verification with SHA-512."""
        data = "test"
        expected_hash = "ee26b0dd4af7e749aa1a8ee3c10ae9923f618980772e473f8819a5d4940e0db27ac185f8a0e1d5f84f88bc887fd67b143732c304cc5fa9ad8e6f57f50028a8ff"

        result = verify_checksum(data, expected_hash, algorithm="sha512")

        assert result["algorithm"] == "sha512"
        assert result["matches"] is True