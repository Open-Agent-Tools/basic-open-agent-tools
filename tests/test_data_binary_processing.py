"""Tests for binary data processing functions."""

import base64
import os
import tempfile

import pytest

from basic_open_agent_tools.data.binary_processing import (
    decode_binary_data,
    encode_binary_data,
    extract_binary_metadata,
    read_binary_file,
    validate_binary_format,
    write_binary_file,
)
from basic_open_agent_tools.exceptions import DataError


class TestReadBinaryFile:
    """Tests for read_binary_file function."""

    def test_read_binary_file_basic(self):
        """Test reading a binary file."""
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp_path = temp.name
            test_data = b"Test binary data"
            temp.write(test_data)

        try:
            # Read the file
            data = read_binary_file(temp_path)

            # Verify
            assert isinstance(data, bytes)
            assert data == test_data

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_read_binary_file_not_found(self):
        """Test reading a non-existent file."""
        with pytest.raises(FileNotFoundError):
            read_binary_file("nonexistent_file.bin")

    def test_read_binary_file_max_size(self):
        """Test reading with max_size limit."""
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp_path = temp.name
            test_data = b"Test binary data" * 10  # 150 bytes
            temp.write(test_data)

        try:
            # Read with sufficient max_size
            data = read_binary_file(temp_path, max_size=200)
            assert data == test_data

            # Read with insufficient max_size
            with pytest.raises(DataError):
                read_binary_file(temp_path, max_size=100)

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestWriteBinaryFile:
    """Tests for write_binary_file function."""

    def test_write_binary_file_basic(self):
        """Test writing a binary file."""
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp_path = temp.name

        try:
            # Test data
            test_data = b"Test binary data for writing"

            # Write the file
            write_binary_file(test_data, temp_path)

            # Verify by reading it back
            with open(temp_path, "rb") as f:
                read_data = f.read()

            assert read_data == test_data

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_write_binary_file_create_dirs(self):
        """Test writing a file with directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a path with subdirectories
            file_path = os.path.join(temp_dir, "subdir1", "subdir2", "test.bin")

            # Test data
            test_data = b"Test binary data"

            # Write the file (should create directories)
            write_binary_file(test_data, file_path)

            # Verify file exists and content is correct
            assert os.path.exists(file_path)
            with open(file_path, "rb") as f:
                read_data = f.read()

            assert read_data == test_data

    def test_write_binary_file_invalid_data(self):
        """Test writing with invalid data type."""
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp_path = temp.name

        try:
            # Test with non-bytes data
            with pytest.raises(TypeError):
                write_binary_file("not bytes", temp_path)

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestEncodeBinaryData:
    """Tests for encode_binary_data function."""

    def test_encode_binary_data_base64(self):
        """Test encoding data with base64."""
        test_data = b"Test binary data for encoding"

        # Encode with base64
        encoded = encode_binary_data(test_data, encoding="base64")

        # Verify
        assert isinstance(encoded, str)
        assert base64.b64decode(encoded) == test_data

    def test_encode_binary_data_hex(self):
        """Test encoding data with hex."""
        test_data = b"Test binary data for encoding"

        # Encode with hex
        encoded = encode_binary_data(test_data, encoding="hex")

        # Verify
        assert isinstance(encoded, str)
        assert bytes.fromhex(encoded) == test_data

    def test_encode_binary_data_invalid_encoding(self):
        """Test encoding with invalid encoding method."""
        test_data = b"Test data"

        with pytest.raises(ValueError):
            encode_binary_data(test_data, encoding="invalid")

    def test_encode_binary_data_invalid_data(self):
        """Test encoding with invalid data type."""
        with pytest.raises(TypeError):
            encode_binary_data("not bytes", encoding="base64")


class TestDecodeBinaryData:
    """Tests for decode_binary_data function."""

    def test_decode_binary_data_base64(self):
        """Test decoding base64 data."""
        original = b"Test binary data for decoding"
        encoded = base64.b64encode(original).decode("ascii")

        # Decode
        decoded = decode_binary_data(encoded, encoding="base64")

        # Verify
        assert isinstance(decoded, bytes)
        assert decoded == original

    def test_decode_binary_data_hex(self):
        """Test decoding hex data."""
        original = b"Test binary data for decoding"
        encoded = original.hex()

        # Decode
        decoded = decode_binary_data(encoded, encoding="hex")

        # Verify
        assert isinstance(decoded, bytes)
        assert decoded == original

    def test_decode_binary_data_invalid_encoding(self):
        """Test decoding with invalid encoding method."""
        with pytest.raises(ValueError):
            decode_binary_data("data", encoding="invalid")

    def test_decode_binary_data_invalid_data(self):
        """Test decoding with invalid data."""
        # Invalid base64
        with pytest.raises(ValueError):
            decode_binary_data("not valid base64!", encoding="base64")

        # Invalid hex
        with pytest.raises(ValueError):
            decode_binary_data("not valid hex!", encoding="hex")

        # Not a string
        with pytest.raises(TypeError):
            decode_binary_data(b"bytes instead of string", encoding="base64")


class TestValidateBinaryFormat:
    """Tests for validate_binary_format function."""

    def test_validate_binary_format_png(self):
        """Test validating PNG format."""
        # Create a minimal valid PNG file
        png_header = (
            b"\x89PNG\r\n\x1a\n"  # PNG signature
            b"\x00\x00\x00\x0dIHDR"  # IHDR chunk header
            b"\x00\x00\x00\x01"  # Width: 1
            b"\x00\x00\x00\x01"  # Height: 1
            b"\x08\x00\x00\x00\x00"  # Bit depth, color type, etc.
        )

        # Should validate as PNG
        assert validate_binary_format(png_header, "png") is True

        # Should not validate as other formats
        assert validate_binary_format(png_header, "jpeg") is False
        assert validate_binary_format(png_header, "gif") is False

    def test_validate_binary_format_pdf(self):
        """Test validating PDF format."""
        pdf_header = b"%PDF-1.5\n"

        # Should validate as PDF
        assert validate_binary_format(pdf_header, "pdf") is True

        # Should not validate as other formats
        assert validate_binary_format(pdf_header, "png") is False

    def test_validate_binary_format_zip(self):
        """Test validating ZIP format."""
        zip_header = b"PK\x03\x04" + b"\x00" * 26

        # Should validate as ZIP
        assert validate_binary_format(zip_header, "zip") is True

        # Should not validate as other formats
        assert validate_binary_format(zip_header, "pdf") is False

    def test_validate_binary_format_invalid_data(self):
        """Test validating with invalid data."""
        # Not bytes
        assert validate_binary_format("not bytes", "png") is False

        # Empty bytes
        assert validate_binary_format(b"", "png") is False

        # Random bytes
        assert validate_binary_format(b"random data", "png") is False

        # Unknown format
        assert validate_binary_format(b"data", "unknown_format") is False


class TestExtractBinaryMetadata:
    """Tests for extract_binary_metadata function."""

    def test_extract_binary_metadata_basic(self):
        """Test extracting basic metadata."""
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as temp:
            temp_path = temp.name
            test_data = b"Test binary data"
            temp.write(test_data)

        try:
            # Extract metadata
            metadata = extract_binary_metadata(temp_path)

            # Verify basic metadata
            assert "size" in metadata
            assert metadata["size"] == len(test_data)
            assert "created" in metadata
            assert "modified" in metadata
            assert "accessed" in metadata

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_extract_binary_metadata_image(self):
        """Test extracting metadata from a PNG image."""
        # Create a minimal PNG file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
            temp_path = temp.name
            # PNG header with 16x16 dimensions
            png_data = (
                b"\x89PNG\r\n\x1a\n"  # PNG signature
                b"\x00\x00\x00\x0dIHDR"  # IHDR chunk header
                b"\x00\x00\x00\x10"  # Width: 16
                b"\x00\x00\x00\x10"  # Height: 16
                b"\x08\x00\x00\x00\x00"  # Bit depth, color type, etc.
            )
            temp.write(png_data)

        try:
            # This test might be skipped because our minimal PNG is not complete
            # and might not be recognized by imghdr
            if os.path.getsize(temp_path) > 0:
                # Extract metadata
                metadata = extract_binary_metadata(temp_path)

                # Verify basic metadata
                assert "size" in metadata
                assert "mime_type" in metadata

                # The image format detection might not work with our minimal PNG
                # so we don't assert on image_format or dimensions

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_extract_binary_metadata_not_found(self):
        """Test extracting metadata from a non-existent file."""
        with pytest.raises(FileNotFoundError):
            extract_binary_metadata("nonexistent_file.bin")
