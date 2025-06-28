"""Tests for basic_open_agent_tools.file_system.validation module."""

from pathlib import Path
from unittest.mock import patch

import pytest

from basic_open_agent_tools.exceptions import FileSystemError
from basic_open_agent_tools.file_system.validation import (
    validate_file_content,
    validate_path,
)


class TestValidatePath:
    """Test cases for validate_path function."""

    def test_validate_valid_absolute_path(self, tmp_path: Path) -> None:
        """Test validating a valid absolute path."""
        test_path = str(tmp_path / "test.txt")

        result = validate_path(test_path, "test operation")

        assert isinstance(result, Path)
        assert result.is_absolute()
        assert result.name == "test.txt"

    def test_validate_valid_relative_path(self) -> None:
        """Test validating a valid relative path."""
        test_path = "relative/path/test.txt"

        result = validate_path(test_path, "test operation")

        assert isinstance(result, Path)
        assert result.is_absolute()  # resolve() makes it absolute
        assert result.name == "test.txt"

    def test_validate_existing_file_path(self, tmp_path: Path) -> None:
        """Test validating a path to an existing file."""
        test_file = tmp_path / "existing.txt"
        test_file.write_text("content")

        result = validate_path(str(test_file), "read")

        assert isinstance(result, Path)
        assert result.exists()
        assert result.is_file()

    def test_validate_existing_directory_path(self, tmp_path: Path) -> None:
        """Test validating a path to an existing directory."""
        test_dir = tmp_path / "existing_dir"
        test_dir.mkdir()

        result = validate_path(str(test_dir), "list")

        assert isinstance(result, Path)
        assert result.exists()
        assert result.is_dir()

    def test_validate_nonexistent_path(self, tmp_path: Path) -> None:
        """Test validating a path that doesn't exist."""
        test_path = str(tmp_path / "nonexistent.txt")

        result = validate_path(test_path, "create")

        assert isinstance(result, Path)
        assert not result.exists()  # Path validation doesn't require existence

    def test_validate_empty_string_path(self) -> None:
        """Test validating an empty string path."""
        with pytest.raises(FileSystemError, match="Invalid path for test operation"):
            validate_path("", "test operation")

    def test_validate_none_path(self) -> None:
        """Test validating None as path."""
        with pytest.raises(FileSystemError, match="Invalid path for test operation"):
            validate_path(None, "test operation")

    def test_validate_non_string_path(self) -> None:
        """Test validating non-string path."""
        with pytest.raises(FileSystemError, match="Invalid path for test operation"):
            validate_path(123, "test operation")

    def test_validate_whitespace_only_path(self) -> None:
        """Test validating whitespace-only path."""
        result = validate_path("   ", "test operation")

        assert isinstance(result, Path)
        # Whitespace path is technically valid, just unusual

    def test_validate_path_with_special_characters(self, tmp_path: Path) -> None:
        """Test validating path with special characters."""
        test_path = str(tmp_path / "file with spaces & symbols!.txt")

        result = validate_path(test_path, "create")

        assert isinstance(result, Path)
        assert result.name == "file with spaces & symbols!.txt"

    def test_validate_very_long_path(self, tmp_path: Path) -> None:
        """Test validating a very long path."""
        long_name = "a" * 100
        test_path = str(tmp_path / f"{long_name}.txt")

        result = validate_path(test_path, "create")

        assert isinstance(result, Path)
        assert result.name == f"{long_name}.txt"

    def test_validate_path_resolution(self, tmp_path: Path) -> None:
        """Test that path resolution works correctly."""
        # Create a path with .. components
        test_subdir = tmp_path / "subdir"
        test_subdir.mkdir()
        test_path = str(test_subdir / ".." / "test.txt")

        result = validate_path(test_path, "create")

        assert isinstance(result, Path)
        assert result.parent == tmp_path  # Should resolve .. correctly

    def test_validate_path_os_error(self) -> None:
        """Test handling of OSError during path resolution."""
        with patch("pathlib.Path.resolve", side_effect=OSError("Path error")):
            with pytest.raises(
                FileSystemError, match="Invalid path for test operation"
            ):
                validate_path("test/path", "test operation")

    def test_validate_path_value_error(self) -> None:
        """Test handling of ValueError during path resolution."""
        with patch("pathlib.Path.resolve", side_effect=ValueError("Invalid path")):
            with pytest.raises(
                FileSystemError, match="Invalid path for test operation"
            ):
                validate_path("test/path", "test operation")

    def test_validate_operation_in_error_message(self) -> None:
        """Test that operation name appears in error messages."""
        with pytest.raises(FileSystemError, match="Invalid path for custom operation"):
            validate_path("", "custom operation")

    def test_validate_path_symlink_resolution(self, tmp_path: Path) -> None:
        """Test that symlinks are resolved correctly."""
        # Create a file and a symlink to it
        target_file = tmp_path / "target.txt"
        target_file.write_text("content")

        symlink_file = tmp_path / "symlink.txt"
        symlink_file.symlink_to(target_file)

        result = validate_path(str(symlink_file), "read")

        assert isinstance(result, Path)
        # The resolved path should point to the target
        assert result == target_file.resolve()

    def test_validate_current_directory_path(self) -> None:
        """Test validating current directory path."""
        result = validate_path(".", "list")

        assert isinstance(result, Path)
        assert result.is_absolute()
        assert result.exists()


class TestValidateFileContent:
    """Test cases for validate_file_content function."""

    def test_validate_valid_string_content(self) -> None:
        """Test validating valid string content."""
        content = "This is valid content"

        # Should not raise any exception
        validate_file_content(content, "write")

    def test_validate_empty_string_content(self) -> None:
        """Test validating empty string content."""
        content = ""

        # Should not raise any exception - empty strings are valid
        validate_file_content(content, "write")

    def test_validate_multiline_string_content(self) -> None:
        """Test validating multiline string content."""
        content = "Line 1\nLine 2\nLine 3"

        # Should not raise any exception
        validate_file_content(content, "write")

    def test_validate_unicode_string_content(self) -> None:
        """Test validating Unicode string content."""
        content = "Hello 世界! 🌍 Здравствуй мир!"

        # Should not raise any exception
        validate_file_content(content, "write")

    def test_validate_string_with_special_characters(self) -> None:
        """Test validating string with special characters."""
        content = "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"

        # Should not raise any exception
        validate_file_content(content, "write")

    def test_validate_very_long_string_content(self) -> None:
        """Test validating very long string content."""
        content = "a" * 10000

        # Should not raise any exception
        validate_file_content(content, "write")

    def test_validate_whitespace_only_content(self) -> None:
        """Test validating whitespace-only content."""
        content = "   \n\t  \r\n  "

        # Should not raise any exception
        validate_file_content(content, "write")

    def test_validate_none_content(self) -> None:
        """Test validating None as content."""
        with pytest.raises(FileSystemError, match="Content must be a string for write"):
            validate_file_content(None, "write")

    def test_validate_integer_content(self) -> None:
        """Test validating integer as content."""
        with pytest.raises(
            FileSystemError, match="Content must be a string for append"
        ):
            validate_file_content(123, "append")

    def test_validate_list_content(self) -> None:
        """Test validating list as content."""
        with pytest.raises(
            FileSystemError, match="Content must be a string for replace"
        ):
            validate_file_content(["item1", "item2"], "replace")

    def test_validate_dict_content(self) -> None:
        """Test validating dictionary as content."""
        with pytest.raises(
            FileSystemError, match="Content must be a string for insert"
        ):
            validate_file_content({"key": "value"}, "insert")

    def test_validate_bytes_content(self) -> None:
        """Test validating bytes as content."""
        with pytest.raises(FileSystemError, match="Content must be a string for write"):
            validate_file_content(b"bytes content", "write")

    def test_validate_boolean_content(self) -> None:
        """Test validating boolean as content."""
        with pytest.raises(
            FileSystemError, match="Content must be a string for update"
        ):
            validate_file_content(True, "update")

    def test_validate_float_content(self) -> None:
        """Test validating float as content."""
        with pytest.raises(
            FileSystemError, match="Content must be a string for create"
        ):
            validate_file_content(3.14, "create")

    def test_validate_operation_in_content_error_message(self) -> None:
        """Test that operation name appears in content error messages."""
        with pytest.raises(
            FileSystemError, match="Content must be a string for custom operation"
        ):
            validate_file_content(123, "custom operation")

    def test_validate_content_with_newlines_and_tabs(self) -> None:
        """Test validating content with various whitespace characters."""
        content = (
            "Line 1\n\tIndented line\r\nWindows line ending\vVertical tab\fForm feed"
        )

        # Should not raise any exception
        validate_file_content(content, "write")

    def test_validate_json_string_content(self) -> None:
        """Test validating JSON string as content."""
        content = '{"key": "value", "number": 42, "array": [1, 2, 3]}'

        # Should not raise any exception - JSON strings are valid strings
        validate_file_content(content, "write")


# Integration tests
class TestValidationIntegration:
    """Integration tests for validation functions working together."""

    def test_validate_path_then_content(self, tmp_path: Path) -> None:
        """Test using path validation followed by content validation."""
        test_path = str(tmp_path / "test.txt")
        test_content = "Test content for integration"

        # Validate path
        validated_path = validate_path(test_path, "write")
        assert isinstance(validated_path, Path)

        # Validate content
        validate_file_content(test_content, "write")  # Should not raise

        # They should work together seamlessly
        validated_path.write_text(test_content)
        assert validated_path.read_text() == test_content

    def test_error_consistency(self) -> None:
        """Test that both functions raise consistent FileSystemError types."""
        # Both should raise FileSystemError
        with pytest.raises(FileSystemError):
            validate_path("", "test")

        with pytest.raises(FileSystemError):
            validate_file_content(123, "test")

    def test_validation_with_realistic_file_operations(self, tmp_path: Path) -> None:
        """Test validation functions in realistic file operation context."""
        # Simulate a complete file write operation validation
        file_path = str(tmp_path / "document.txt")
        file_content = (
            "# Document Title\n\nThis is a test document with multiple lines.\n"
        )

        # Step 1: Validate path
        validated_path = validate_path(file_path, "write file")

        # Step 2: Validate content
        validate_file_content(file_content, "write file")

        # Step 3: Perform operation (should work after validation)
        validated_path.write_text(file_content)

        # Verify the operation succeeded
        assert validated_path.exists()
        assert validated_path.read_text() == file_content
