"""Tests for extended compression utilities."""

from unittest.mock import mock_open, patch

import pytest

from basic_open_agent_tools.archive.compression import (
    compress_file_bzip2,
    compress_file_gzip,
    compress_file_xz,
    decompress_file_gzip,
)
from basic_open_agent_tools.exceptions import BasicAgentToolsError


class TestCompressFileGzip:
    """Test cases for compress_file_gzip function."""

    def test_invalid_input_path_type(self):
        """Test with invalid input path type."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            compress_file_gzip(123, "output.txt.gz", False)  # type: ignore
        assert "Input path must be a non-empty string" in str(exc_info.value)

    def test_nonexistent_input_file(self):
        """Test with nonexistent input file."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            compress_file_gzip("nonexistent.txt", "output.txt.gz", False)
        assert "Input file not found" in str(exc_info.value)

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.path.getsize")
    @patch("gzip.open")
    @patch("builtins.open", new_callable=mock_open, read_data=b"test content")
    @patch("shutil.copyfileobj")
    def test_successful_gzip_compression(
        self, mock_copy, mock_file, mock_gzip, mock_getsize, mock_isfile, mock_exists
    ):
        """Test successful GZIP compression."""

        # Input exists, output doesn't exist
        def exists_side_effect(path):
            return path == "input.txt"

        mock_exists.side_effect = exists_side_effect
        mock_isfile.return_value = True
        mock_getsize.side_effect = [1000, 300]  # Input: 1000, Output: 300 bytes

        result = compress_file_gzip("input.txt", "output.txt.gz", False)

        # Function returns string description now
        assert isinstance(result, str)
        assert "output.txt.gz" in result
        assert "input.txt" in result
        assert "70.0%" in result

    @patch("os.path.exists")
    @patch("os.path.isfile")
    def test_input_not_file(self, mock_isfile, mock_exists):
        """Test with input path that's not a file."""
        mock_exists.return_value = True
        mock_isfile.return_value = False

        with pytest.raises(BasicAgentToolsError) as exc_info:
            compress_file_gzip("directory_path", "output.txt.gz", False)
        assert "Input path is not a file" in str(exc_info.value)


class TestDecompressFileGzip:
    """Test cases for decompress_file_gzip function."""

    def test_default_output_path_with_gz_extension(self):
        """Test decompression with explicit output path for .gz files."""
        with patch("os.path.exists", return_value=False):
            with pytest.raises(BasicAgentToolsError):
                # Will fail at exists check
                try:
                    decompress_file_gzip("test.txt.gz", "test.txt")
                except BasicAgentToolsError as e:
                    # Should fail because file doesn't exist
                    assert "not found" in str(e)
                    raise  # Re-raise so pytest.raises can catch it

    @patch("os.path.exists")
    @patch("os.path.getsize")
    @patch("gzip.open")
    @patch("builtins.open", new_callable=mock_open)
    @patch("shutil.copyfileobj")
    def test_successful_gzip_decompression(
        self, mock_copy, mock_file, mock_gzip, mock_getsize, mock_exists
    ):
        """Test successful GZIP decompression."""
        mock_exists.return_value = True
        mock_getsize.side_effect = [300, 1000]  # Compressed: 300, Decompressed: 1000

        result = decompress_file_gzip("input.txt.gz", "output.txt")

        assert result["input_path"] == "input.txt.gz"
        assert result["output_path"] == "output.txt"
        assert result["compressed_size_bytes"] == 300
        assert result["decompressed_size_bytes"] == 1000
        assert result["expansion_ratio"] == 3.33  # 1000/300 rounded
        assert result["decompression_type"] == "gzip"
        assert result["decompression_status"] == "success"


class TestCompressFileBzip2:
    """Test cases for compress_file_bzip2 function."""

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.path.getsize")
    @patch("bz2.BZ2File")
    @patch("builtins.open", new_callable=mock_open)
    @patch("shutil.copyfileobj")
    def test_successful_bzip2_compression(
        self, mock_copy, mock_file, mock_bz2, mock_getsize, mock_isfile, mock_exists
    ):
        """Test successful BZIP2 compression."""

        # Input exists, output doesn't exist
        def exists_side_effect(path):
            return path == "large_file.txt"

        mock_exists.side_effect = exists_side_effect
        mock_isfile.return_value = True
        mock_getsize.side_effect = [2000, 400]  # Better compression than gzip

        result = compress_file_bzip2("large_file.txt", "large_file.txt.bz2", False)

        # Function returns string description now
        assert isinstance(result, str)
        assert "large_file.txt.bz2" in result
        assert "large_file.txt" in result
        assert "80.0%" in result


class TestCompressFileXz:
    """Test cases for compress_file_xz function."""

    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.path.getsize")
    @patch("lzma.LZMAFile")
    @patch("builtins.open", new_callable=mock_open)
    @patch("shutil.copyfileobj")
    def test_successful_xz_compression(
        self, mock_copy, mock_file, mock_lzma, mock_getsize, mock_isfile, mock_exists
    ):
        """Test successful XZ compression."""

        # Input exists, output doesn't exist
        def exists_side_effect(path):
            return path == "huge_file.txt"

        mock_exists.side_effect = exists_side_effect
        mock_isfile.return_value = True
        mock_getsize.side_effect = [3000, 450]  # Best compression ratio

        result = compress_file_xz("huge_file.txt", "compressed.xz", False)

        # Function returns string description now
        assert isinstance(result, str)
        assert "compressed.xz" in result
        assert "huge_file.txt" in result
        assert "85.0%" in result
