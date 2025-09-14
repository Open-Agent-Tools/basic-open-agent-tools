"""Tests for basic_open_agent_tools.file_system.info module."""

import tempfile
from pathlib import Path

import pytest

from basic_open_agent_tools.exceptions import FileSystemError
from basic_open_agent_tools.file_system.info import (
    directory_exists,
    file_exists,
    get_file_info,
    get_file_size,
    is_empty_directory,
)


def can_create_symlinks() -> bool:
    """Check if we can create symbolic links on this system."""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            target = temp_path / "target"
            target.touch()
            link = temp_path / "link"
            link.symlink_to(target)
            return True
    except (OSError, NotImplementedError):
        return False


skip_if_no_symlinks = pytest.mark.skipif(
    not can_create_symlinks(), reason="Symlinks not supported or insufficient privileges"
)


class TestGetFileInfo:
    """Test cases for get_file_info function."""

    def test_get_file_info_basic(self, tmp_path: Path) -> None:
        """Test getting basic file information."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_content = "Hello, World!"
        test_file.write_text(test_content)

        result = get_file_info(str(test_file))

        # Verify file info structure
        assert isinstance(result, dict)
        assert "name" in result
        assert "size" in result
        assert "modified_time" in result
        assert "is_file" in result
        assert "is_directory" in result
        assert "is_symlink" in result
        assert "absolute_path" in result
        assert "parent" in result
        assert "suffix" in result
        assert "permissions" in result

    def test_get_file_info_file_properties(self, tmp_path: Path) -> None:
        """Test file-specific properties."""
        test_file = tmp_path / "example.txt"
        test_content = "Test content"
        test_file.write_text(test_content)

        result = get_file_info(str(test_file))

        # Check file properties
        assert result["name"] == "example.txt"
        assert result["size"] == len(test_content)
        assert result["is_file"] is True
        assert result["is_directory"] is False
        assert result["is_symlink"] is False
        assert result["suffix"] == ".txt"
        assert str(tmp_path) in result["absolute_path"]
        assert str(tmp_path) == result["parent"]
        assert isinstance(result["modified_time"], (int, float))
        assert len(result["permissions"]) == 3

    def test_get_directory_info(self, tmp_path: Path) -> None:
        """Test getting directory information."""
        test_dir = tmp_path / "test_directory"
        test_dir.mkdir()

        result = get_file_info(str(test_dir))

        # Check directory properties
        assert result["name"] == "test_directory"
        assert result["is_file"] is False
        assert result["is_directory"] is True
        assert result["is_symlink"] is False
        assert result["suffix"] == ""
        assert isinstance(result["size"], int)
        assert isinstance(result["modified_time"], (int, float))

    def test_get_file_info_with_suffix(self, tmp_path: Path) -> None:
        """Test file info with various suffixes."""
        test_cases = [
            ("file.py", ".py"),
            ("document.pdf", ".pdf"),
            ("archive.tar.gz", ".gz"),
            ("no_extension", ""),
        ]

        for filename, expected_suffix in test_cases:
            test_file = tmp_path / filename
            test_file.touch()

            result = get_file_info(str(test_file))
            assert result["suffix"] == expected_suffix

    def test_get_file_info_nonexistent_path(self) -> None:
        """Test getting info for nonexistent path."""
        with pytest.raises(FileSystemError, match="Path not found"):
            get_file_info("/nonexistent/path/file.txt")

    def test_get_file_info_invalid_path(self) -> None:
        """Test getting info for invalid path."""
        with pytest.raises(FileSystemError):
            get_file_info("")

    @skip_if_no_symlinks
    def test_get_file_info_symlink(self, tmp_path: Path) -> None:
        """Test getting info for symbolic link (follows symlink to target)."""
        # Create target file
        target_file = tmp_path / "target.txt"
        target_file.write_text("target content")

        # Create symlink
        symlink_file = tmp_path / "link.txt"
        symlink_file.symlink_to(target_file)

        result = get_file_info(str(symlink_file))

        # Note: get_file_info follows symlinks, so returns target info
        assert result["name"] == "target.txt"  # Target file name
        assert result["is_symlink"] is False  # Target is not a symlink
        assert result["is_file"] is True  # Target is a file
        assert result["is_directory"] is False
        assert result["size"] == len("target content")

    def test_get_file_info_large_file(self, tmp_path: Path) -> None:
        """Test getting info for larger file."""
        test_file = tmp_path / "large.txt"
        large_content = "x" * 10000
        test_file.write_text(large_content)

        result = get_file_info(str(test_file))

        assert result["size"] == 10000
        assert result["name"] == "large.txt"


class TestFileExists:
    """Test cases for file_exists function."""

    def test_file_exists_true(self, tmp_path: Path) -> None:
        """Test file_exists returns True for existing file."""
        test_file = tmp_path / "exists.txt"
        test_file.touch()

        assert file_exists(str(test_file)) is True

    def test_file_exists_false_nonexistent(self) -> None:
        """Test file_exists returns False for nonexistent file."""
        assert file_exists("/nonexistent/file.txt") is False

    def test_file_exists_false_directory(self, tmp_path: Path) -> None:
        """Test file_exists returns False for directory."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        assert file_exists(str(test_dir)) is False

    def test_file_exists_empty_path(self) -> None:
        """Test file_exists returns False for empty path."""
        assert file_exists("") is False

    @skip_if_no_symlinks
    def test_file_exists_symlink_to_file(self, tmp_path: Path) -> None:
        """Test file_exists returns True for symlink to file."""
        target_file = tmp_path / "target.txt"
        target_file.touch()

        symlink_file = tmp_path / "link.txt"
        symlink_file.symlink_to(target_file)

        assert file_exists(str(symlink_file)) is True

    @skip_if_no_symlinks
    def test_file_exists_broken_symlink(self, tmp_path: Path) -> None:
        """Test file_exists returns False for broken symlink."""
        nonexistent_target = tmp_path / "nonexistent.txt"

        symlink_file = tmp_path / "broken_link.txt"
        symlink_file.symlink_to(nonexistent_target)

        assert file_exists(str(symlink_file)) is False


class TestDirectoryExists:
    """Test cases for directory_exists function."""

    def test_directory_exists_true(self, tmp_path: Path) -> None:
        """Test directory_exists returns True for existing directory."""
        test_dir = tmp_path / "test_directory"
        test_dir.mkdir()

        assert directory_exists(str(test_dir)) is True

    def test_directory_exists_false_nonexistent(self) -> None:
        """Test directory_exists returns False for nonexistent directory."""
        assert directory_exists("/nonexistent/directory") is False

    def test_directory_exists_false_file(self, tmp_path: Path) -> None:
        """Test directory_exists returns False for file."""
        test_file = tmp_path / "test.txt"
        test_file.touch()

        assert directory_exists(str(test_file)) is False

    def test_directory_exists_empty_path(self) -> None:
        """Test directory_exists returns False for empty path."""
        assert directory_exists("") is False

    def test_directory_exists_current_directory(self) -> None:
        """Test directory_exists returns True for current directory."""
        assert directory_exists(".") is True

    def test_directory_exists_parent_directory(self) -> None:
        """Test directory_exists returns True for parent directory."""
        assert directory_exists("..") is True

    @skip_if_no_symlinks
    def test_directory_exists_symlink_to_directory(self, tmp_path: Path) -> None:
        """Test directory_exists returns True for symlink to directory."""
        target_dir = tmp_path / "target_dir"
        target_dir.mkdir()

        symlink_dir = tmp_path / "link_dir"
        symlink_dir.symlink_to(target_dir)

        assert directory_exists(str(symlink_dir)) is True


class TestGetFileSize:
    """Test cases for get_file_size function."""

    def test_get_file_size_empty_file(self, tmp_path: Path) -> None:
        """Test getting size of empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.touch()

        size = get_file_size(str(test_file))
        assert size == 0

    def test_get_file_size_with_content(self, tmp_path: Path) -> None:
        """Test getting size of file with content."""
        test_file = tmp_path / "content.txt"
        content = "Hello, World!"
        test_file.write_text(content)

        size = get_file_size(str(test_file))
        assert size == len(content)

    def test_get_file_size_large_file(self, tmp_path: Path) -> None:
        """Test getting size of large file."""
        test_file = tmp_path / "large.txt"
        content = "x" * 50000
        test_file.write_text(content)

        size = get_file_size(str(test_file))
        assert size == 50000

    def test_get_file_size_binary_file(self, tmp_path: Path) -> None:
        """Test getting size of binary file."""
        test_file = tmp_path / "binary.bin"
        binary_data = b"\x00\x01\x02\x03" * 1000
        test_file.write_bytes(binary_data)

        size = get_file_size(str(test_file))
        assert size == len(binary_data)

    def test_get_file_size_nonexistent_file(self) -> None:
        """Test getting size of nonexistent file raises error."""
        with pytest.raises(FileSystemError, match="File not found"):
            get_file_size("/nonexistent/file.txt")

    def test_get_file_size_directory(self, tmp_path: Path) -> None:
        """Test getting size of directory raises error."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        with pytest.raises(FileSystemError, match="File not found"):
            get_file_size(str(test_dir))

    def test_get_file_size_invalid_path(self) -> None:
        """Test getting size with invalid path."""
        with pytest.raises(FileSystemError):
            get_file_size("")


class TestIsEmptyDirectory:
    """Test cases for is_empty_directory function."""

    def test_is_empty_directory_true(self, tmp_path: Path) -> None:
        """Test is_empty_directory returns True for empty directory."""
        test_dir = tmp_path / "empty_dir"
        test_dir.mkdir()

        assert is_empty_directory(str(test_dir)) is True

    def test_is_empty_directory_false_with_files(self, tmp_path: Path) -> None:
        """Test is_empty_directory returns False for directory with files."""
        test_dir = tmp_path / "dir_with_files"
        test_dir.mkdir()

        # Add a file
        (test_dir / "file.txt").touch()

        assert is_empty_directory(str(test_dir)) is False

    def test_is_empty_directory_false_with_subdirectories(self, tmp_path: Path) -> None:
        """Test is_empty_directory returns False for directory with subdirectories."""
        test_dir = tmp_path / "dir_with_subdirs"
        test_dir.mkdir()

        # Add a subdirectory
        (test_dir / "subdir").mkdir()

        assert is_empty_directory(str(test_dir)) is False

    def test_is_empty_directory_false_with_hidden_files(self, tmp_path: Path) -> None:
        """Test is_empty_directory returns False for directory with hidden files."""
        test_dir = tmp_path / "dir_with_hidden"
        test_dir.mkdir()

        # Add a hidden file
        (test_dir / ".hidden").touch()

        assert is_empty_directory(str(test_dir)) is False

    def test_is_empty_directory_nonexistent(self) -> None:
        """Test is_empty_directory raises error for nonexistent directory."""
        with pytest.raises(FileSystemError, match="Directory not found"):
            is_empty_directory("/nonexistent/directory")

    def test_is_empty_directory_file(self, tmp_path: Path) -> None:
        """Test is_empty_directory raises error for file."""
        test_file = tmp_path / "test.txt"
        test_file.touch()

        with pytest.raises(FileSystemError, match="Directory not found"):
            is_empty_directory(str(test_file))

    def test_is_empty_directory_invalid_path(self) -> None:
        """Test is_empty_directory with invalid path."""
        with pytest.raises(FileSystemError):
            is_empty_directory("")

    def test_is_empty_directory_with_multiple_items(self, tmp_path: Path) -> None:
        """Test is_empty_directory with multiple files and directories."""
        test_dir = tmp_path / "mixed_dir"
        test_dir.mkdir()

        # Add multiple items
        (test_dir / "file1.txt").touch()
        (test_dir / "file2.txt").touch()
        (test_dir / "subdir1").mkdir()
        (test_dir / "subdir2").mkdir()

        assert is_empty_directory(str(test_dir)) is False


# Integration tests
class TestInfoIntegration:
    """Integration tests for info functions."""

    def test_file_workflow(self, tmp_path: Path) -> None:
        """Test complete file information workflow."""
        test_file = tmp_path / "workflow.txt"
        content = "Integration test content"
        test_file.write_text(content)

        # Test all functions work together
        assert file_exists(str(test_file)) is True
        assert directory_exists(str(test_file)) is False

        size = get_file_size(str(test_file))
        assert size == len(content)

        info = get_file_info(str(test_file))
        assert info["size"] == size
        assert info["is_file"] is True
        assert info["name"] == "workflow.txt"

    def test_directory_workflow(self, tmp_path: Path) -> None:
        """Test complete directory information workflow."""
        test_dir = tmp_path / "workflow_dir"
        test_dir.mkdir()

        # Test with empty directory
        assert directory_exists(str(test_dir)) is True
        assert file_exists(str(test_dir)) is False
        assert is_empty_directory(str(test_dir)) is True

        info = get_file_info(str(test_dir))
        assert info["is_directory"] is True
        assert info["is_file"] is False
        assert info["name"] == "workflow_dir"

        # Add content and test again
        (test_dir / "file.txt").touch()
        assert is_empty_directory(str(test_dir)) is False

    def test_nonexistent_path_consistency(self) -> None:
        """Test all functions handle nonexistent paths consistently."""
        nonexistent = "/absolutely/nonexistent/path"

        # These should return False
        assert file_exists(nonexistent) is False
        assert directory_exists(nonexistent) is False

        # These should raise FileSystemError
        with pytest.raises(FileSystemError):
            get_file_info(nonexistent)

        with pytest.raises(FileSystemError):
            get_file_size(nonexistent)

        with pytest.raises(FileSystemError):
            is_empty_directory(nonexistent)

    @skip_if_no_symlinks
    def test_symlink_consistency(self, tmp_path: Path) -> None:
        """Test all functions handle symlinks consistently."""
        # Create target file
        target = tmp_path / "target.txt"
        target.write_text("target content")

        # Create symlink
        link = tmp_path / "link.txt"
        link.symlink_to(target)

        # Test consistency across functions (all follow symlinks)
        assert file_exists(str(link)) is True
        assert directory_exists(str(link)) is False

        size = get_file_size(str(link))
        info = get_file_info(str(link))

        assert info["size"] == size
        assert info["is_symlink"] is False  # Reports target, not symlink
        assert info["is_file"] is True
        assert size == len("target content")
