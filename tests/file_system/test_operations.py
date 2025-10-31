"""Tests for basic_open_agent_tools.file_system.operations module."""

from pathlib import Path
from unittest.mock import patch

import pytest

from basic_open_agent_tools.exceptions import FileSystemError
from basic_open_agent_tools.file_system.operations import (
    append_to_file,
    copy_file,
    create_directory,
    delete_directory,
    delete_file,
    insert_at_line,
    list_directory_contents,
    move_file,
    read_file_to_string,
    replace_in_file,
    write_file_from_string,
)


class TestReadFileToString:
    """Test cases for read_file_to_string function."""

    def test_read_existing_file(self, tmp_path: Path) -> None:
        """Test reading content from an existing file."""
        test_file = tmp_path / "test.txt"
        test_content = "  Hello World!  \n  "
        test_file.write_text(test_content, encoding="utf-8")

        result = read_file_to_string(str(test_file))
        assert result == "Hello World!"

    def test_read_empty_file(self, tmp_path: Path) -> None:
        """Test reading an empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("", encoding="utf-8")

        result = read_file_to_string(str(test_file))
        assert result == ""

    def test_read_unicode_content(self, tmp_path: Path) -> None:
        """Test reading file with Unicode content."""
        test_file = tmp_path / "unicode.txt"
        test_content = "Hello 世界! 🌍"
        test_file.write_text(test_content, encoding="utf-8")

        result = read_file_to_string(str(test_file))
        assert result == test_content

    def test_read_nonexistent_file(self, tmp_path: Path) -> None:
        """Test reading a file that doesn't exist."""
        nonexistent_file = tmp_path / "nonexistent.txt"

        with pytest.raises(FileSystemError, match="File not found"):
            read_file_to_string(str(nonexistent_file))

    def test_read_directory_instead_of_file(self, tmp_path: Path) -> None:
        """Test reading a directory path instead of a file."""
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()

        with pytest.raises(FileSystemError, match="File not found"):
            read_file_to_string(str(test_dir))

    def test_read_file_permission_denied(self, tmp_path: Path) -> None:
        """Test reading a file with permission denied."""
        test_file = tmp_path / "protected.txt"
        test_file.write_text("content", encoding="utf-8")

        with patch(
            "pathlib.Path.read_text", side_effect=PermissionError("Access denied")
        ):
            with pytest.raises(FileSystemError, match="Failed to read file"):
                read_file_to_string(str(test_file))

    def test_read_file_unicode_decode_error(self, tmp_path: Path) -> None:
        """Test reading a file with Unicode decode error."""
        test_file = tmp_path / "binary.txt"
        test_file.write_bytes(b"\xff\xfe\x00\x00")  # Invalid UTF-8

        with pytest.raises(FileSystemError, match="Failed to read file"):
            read_file_to_string(str(test_file))


class TestWriteFileFromString:
    """Test cases for write_file_from_string function."""

    def test_write_to_new_file(self, tmp_path: Path) -> None:
        """Test writing content to a new file."""
        test_file = tmp_path / "new.txt"
        test_content = "Hello World!"

        result = write_file_from_string(str(test_file), test_content, skip_confirm=True)
        assert isinstance(result, str) and result
        assert test_file.read_text(encoding="utf-8") == test_content

    def test_write_to_existing_file(self, tmp_path: Path) -> None:
        """Test writing content to overwrite an existing file."""
        test_file = tmp_path / "existing.txt"
        test_file.write_text("Old content", encoding="utf-8")
        new_content = "New content"

        result = write_file_from_string(str(test_file), new_content, skip_confirm=True)
        assert isinstance(result, str) and result
        assert test_file.read_text(encoding="utf-8") == new_content

    def test_write_empty_content(self, tmp_path: Path) -> None:
        """Test writing empty content to a file."""
        test_file = tmp_path / "empty.txt"

        result = write_file_from_string(str(test_file), "", skip_confirm=True)
        assert isinstance(result, str) and result
        assert test_file.read_text(encoding="utf-8") == ""

    def test_write_unicode_content(self, tmp_path: Path) -> None:
        """Test writing Unicode content to a file."""
        test_file = tmp_path / "unicode.txt"
        test_content = "Hello 世界! 🌍"

        result = write_file_from_string(str(test_file), test_content, skip_confirm=True)
        assert isinstance(result, str) and result
        assert test_file.read_text(encoding="utf-8") == test_content

    def test_write_creates_parent_directories(self, tmp_path: Path) -> None:
        """Test writing to a file in non-existent parent directories."""
        test_file = tmp_path / "nested" / "dir" / "test.txt"
        test_content = "Nested content"

        result = write_file_from_string(str(test_file), test_content, skip_confirm=True)
        assert isinstance(result, str) and result
        assert test_file.read_text(encoding="utf-8") == test_content

    def test_write_file_permission_denied(self, tmp_path: Path) -> None:
        """Test writing to a file with permission denied."""
        test_file = tmp_path / "protected.txt"

        with patch(
            "pathlib.Path.write_text", side_effect=PermissionError("Access denied")
        ):
            with pytest.raises(FileSystemError, match="Failed to write file"):
                write_file_from_string(str(test_file), "content", skip_confirm=True)

    def test_write_multiline_content(self, tmp_path: Path) -> None:
        """Test writing multiline content to a file."""
        test_file = tmp_path / "multiline.txt"
        test_content = "Line 1\nLine 2\nLine 3"

        result = write_file_from_string(str(test_file), test_content, skip_confirm=True)
        assert isinstance(result, str) and result
        assert test_file.read_text(encoding="utf-8") == test_content


class TestAppendToFile:
    """Test cases for append_to_file function."""

    def test_append_to_existing_file(self, tmp_path: Path) -> None:
        """Test appending content to an existing file."""
        test_file = tmp_path / "existing.txt"
        initial_content = "Initial content"
        append_content = "\nAppended content"
        test_file.write_text(initial_content, encoding="utf-8")

        result = append_to_file(str(test_file), append_content, skip_confirm=True)
        assert isinstance(result, str) and result
        assert test_file.read_text(encoding="utf-8") == initial_content + append_content

    def test_append_to_new_file(self, tmp_path: Path) -> None:
        """Test appending content to a new file."""
        test_file = tmp_path / "new.txt"
        test_content = "New content"

        result = append_to_file(str(test_file), test_content, skip_confirm=True)
        assert isinstance(result, str) and result
        assert test_file.read_text(encoding="utf-8") == test_content

    def test_append_empty_content(self, tmp_path: Path) -> None:
        """Test appending empty content to a file."""
        test_file = tmp_path / "test.txt"
        initial_content = "Initial"
        test_file.write_text(initial_content, encoding="utf-8")

        result = append_to_file(str(test_file), "", skip_confirm=True)
        assert isinstance(result, str) and result
        assert test_file.read_text(encoding="utf-8") == initial_content

    def test_append_creates_parent_directories(self, tmp_path: Path) -> None:
        """Test appending to a file in non-existent parent directories."""
        test_file = tmp_path / "nested" / "dir" / "test.txt"
        test_content = "Nested content"

        result = append_to_file(str(test_file), test_content, skip_confirm=True)
        assert isinstance(result, str) and result
        assert test_file.read_text(encoding="utf-8") == test_content

    def test_append_file_permission_denied(self, tmp_path: Path) -> None:
        """Test appending to a file with permission denied."""
        test_file = tmp_path / "protected.txt"

        with patch("pathlib.Path.open", side_effect=PermissionError("Access denied")):
            with pytest.raises(FileSystemError, match="Failed to append to file"):
                append_to_file(str(test_file), "content", skip_confirm=True)

    def test_append_multiple_times(self, tmp_path: Path) -> None:
        """Test multiple append operations to the same file."""
        test_file = tmp_path / "multi.txt"

        append_to_file(str(test_file), "First", skip_confirm=True)
        append_to_file(str(test_file), "Second", skip_confirm=True)
        append_to_file(str(test_file), "Third", skip_confirm=True)

        assert test_file.read_text(encoding="utf-8") == "FirstSecondThird"

    def test_append_with_confirmation_required(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that append requires confirmation when skip_confirm=False."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Initial content")

        # Simulate non-TTY environment (agent mode)
        monkeypatch.setattr("sys.stdin.isatty", lambda: False)

        # Should raise error asking for confirmation
        with pytest.raises(Exception, match="CONFIRMATION_REQUIRED"):
            append_to_file(str(test_file), "More content", skip_confirm=False)


class TestListDirectoryContents:
    """Test cases for list_directory_contents function."""

    def test_list_empty_directory(self, tmp_path: Path) -> None:
        """Test listing contents of an empty directory."""
        result = list_directory_contents(str(tmp_path), True)
        assert result == []

    def test_list_directory_with_files(self, tmp_path: Path) -> None:
        """Test listing directory with files and subdirectories."""
        (tmp_path / "file1.txt").write_text("content")
        (tmp_path / "file2.txt").write_text("content")
        (tmp_path / "subdir").mkdir()

        result = list_directory_contents(str(tmp_path), True)
        assert sorted(result) == ["file1.txt", "file2.txt", "subdir"]

    def test_list_directory_exclude_hidden(self, tmp_path: Path) -> None:
        """Test listing directory excluding hidden files."""
        (tmp_path / "visible.txt").write_text("content")
        (tmp_path / ".hidden.txt").write_text("content")
        (tmp_path / ".hidden_dir").mkdir()

        result = list_directory_contents(str(tmp_path), False)
        assert result == ["visible.txt"]

    def test_list_directory_include_hidden(self, tmp_path: Path) -> None:
        """Test listing directory including hidden files."""
        (tmp_path / "visible.txt").write_text("content")
        (tmp_path / ".hidden.txt").write_text("content")
        (tmp_path / ".hidden_dir").mkdir()

        result = list_directory_contents(str(tmp_path), True)
        assert sorted(result) == [".hidden.txt", ".hidden_dir", "visible.txt"]

    def test_list_nonexistent_directory(self, tmp_path: Path) -> None:
        """Test listing a directory that doesn't exist."""
        nonexistent_dir = tmp_path / "nonexistent"

        with pytest.raises(FileSystemError, match="Directory not found"):
            list_directory_contents(str(nonexistent_dir), True)

    def test_list_file_instead_of_directory(self, tmp_path: Path) -> None:
        """Test listing a file path instead of a directory."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with pytest.raises(FileSystemError, match="Directory not found"):
            list_directory_contents(str(test_file), True)

    def test_list_directory_permission_denied(self, tmp_path: Path) -> None:
        """Test listing a directory with permission denied."""
        with patch(
            "pathlib.Path.iterdir", side_effect=PermissionError("Access denied")
        ):
            with pytest.raises(FileSystemError, match="Failed to list directory"):
                list_directory_contents(str(tmp_path), True)

    def test_list_directory_sorting(self, tmp_path: Path) -> None:
        """Test that directory contents are sorted."""
        (tmp_path / "z_file.txt").write_text("content")
        (tmp_path / "a_file.txt").write_text("content")
        (tmp_path / "m_file.txt").write_text("content")

        result = list_directory_contents(str(tmp_path), True)
        assert result == ["a_file.txt", "m_file.txt", "z_file.txt"]


class TestCreateDirectory:
    """Test cases for create_directory function."""

    def test_create_new_directory(self, tmp_path: Path) -> None:
        """Test creating a new directory."""
        new_dir = tmp_path / "newdir"

        result = create_directory(str(new_dir), skip_confirm=True)
        assert isinstance(result, str) and result
        assert new_dir.is_dir()

    def test_create_existing_directory(self, tmp_path: Path) -> None:
        """Test creating a directory that already exists."""
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()

        result = create_directory(str(existing_dir), skip_confirm=True)
        assert isinstance(result, str) and result
        assert existing_dir.is_dir()

    def test_create_nested_directories(self, tmp_path: Path) -> None:
        """Test creating nested directories."""
        nested_dir = tmp_path / "level1" / "level2" / "level3"

        result = create_directory(str(nested_dir), skip_confirm=True)
        assert isinstance(result, str) and result
        assert nested_dir.is_dir()

    def test_create_directory_permission_denied(self, tmp_path: Path) -> None:
        """Test creating a directory with permission denied."""
        new_dir = tmp_path / "protected"

        with patch("pathlib.Path.mkdir", side_effect=PermissionError("Access denied")):
            with pytest.raises(FileSystemError, match="Failed to create directory"):
                create_directory(str(new_dir), skip_confirm=True)

    def test_create_directory_over_file(self, tmp_path: Path) -> None:
        """Test creating a directory where a file already exists."""
        test_file = tmp_path / "existing_file.txt"
        test_file.write_text("content")

        with pytest.raises(FileSystemError, match="Failed to create directory"):
            create_directory(str(test_file), skip_confirm=True)


class TestDeleteFile:
    """Test cases for delete_file function."""

    def test_delete_existing_file(self, tmp_path: Path) -> None:
        """Test deleting an existing file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        result = delete_file(str(test_file), skip_confirm=True)
        assert isinstance(result, str) and result
        assert not test_file.exists()

    def test_delete_nonexistent_file(self, tmp_path: Path) -> None:
        """Test deleting a file that doesn't exist."""
        nonexistent_file = tmp_path / "nonexistent.txt"

        result = delete_file(str(nonexistent_file), skip_confirm=True)
        assert isinstance(result, str)  # Should succeed with missing_ok=True

    def test_delete_file_permission_denied(self, tmp_path: Path) -> None:
        """Test deleting a file with permission denied."""
        test_file = tmp_path / "protected.txt"
        test_file.write_text("content")

        with patch("pathlib.Path.unlink", side_effect=PermissionError("Access denied")):
            with pytest.raises(FileSystemError, match="Failed to delete file"):
                delete_file(str(test_file), skip_confirm=True)

    def test_delete_directory_with_delete_file(self, tmp_path: Path) -> None:
        """Test deleting a directory using delete_file function."""
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()

        with pytest.raises(FileSystemError, match="Path is not a file"):
            delete_file(str(test_dir), skip_confirm=True)


class TestDeleteDirectory:
    """Test cases for delete_directory function."""

    def test_delete_empty_directory_non_recursive(self, tmp_path: Path) -> None:
        """Test deleting an empty directory non-recursively."""
        test_dir = tmp_path / "empty_dir"
        test_dir.mkdir()

        result = delete_directory(str(test_dir), False, skip_confirm=True)
        assert isinstance(result, str) and result
        assert not test_dir.exists()

    def test_delete_non_empty_directory_non_recursive(self, tmp_path: Path) -> None:
        """Test deleting a non-empty directory non-recursively."""
        test_dir = tmp_path / "non_empty_dir"
        test_dir.mkdir()
        (test_dir / "file.txt").write_text("content")

        with pytest.raises(FileSystemError, match="Directory not empty"):
            delete_directory(str(test_dir), False, skip_confirm=True)

    def test_delete_non_empty_directory_recursive(self, tmp_path: Path) -> None:
        """Test deleting a non-empty directory recursively."""
        test_dir = tmp_path / "non_empty_dir"
        test_dir.mkdir()
        (test_dir / "file.txt").write_text("content")
        (test_dir / "subdir").mkdir()
        (test_dir / "subdir" / "nested.txt").write_text("content")

        result = delete_directory(str(test_dir), True, skip_confirm=True)
        assert isinstance(result, str) and result
        assert not test_dir.exists()

    def test_delete_nonexistent_directory(self, tmp_path: Path) -> None:
        """Test deleting a directory that doesn't exist."""
        nonexistent_dir = tmp_path / "nonexistent"

        result = delete_directory(str(nonexistent_dir), True, skip_confirm=True)
        assert isinstance(result, str)  # Should succeed if directory doesn't exist

    def test_delete_directory_permission_denied(self, tmp_path: Path) -> None:
        """Test deleting a directory with permission denied."""
        test_dir = tmp_path / "protected_dir"
        test_dir.mkdir()

        with patch("pathlib.Path.rmdir", side_effect=PermissionError("Access denied")):
            with pytest.raises(FileSystemError, match="Failed to delete directory"):
                delete_directory(str(test_dir), False, skip_confirm=True)


class TestMoveFile:
    """Test cases for move_file function."""

    def test_move_file_to_new_location(self, tmp_path: Path) -> None:
        """Test moving a file to a new location."""
        source_file = tmp_path / "source.txt"
        dest_file = tmp_path / "destination.txt"
        test_content = "Test content"
        source_file.write_text(test_content)

        result = move_file(str(source_file), str(dest_file), skip_confirm=True)
        assert isinstance(result, str) and result
        assert not source_file.exists()
        assert dest_file.read_text() == test_content

    def test_move_file_to_different_directory(self, tmp_path: Path) -> None:
        """Test moving a file to a different directory."""
        source_file = tmp_path / "source.txt"
        dest_dir = tmp_path / "dest_dir"
        dest_file = dest_dir / "moved.txt"
        test_content = "Test content"
        source_file.write_text(test_content)

        result = move_file(str(source_file), str(dest_file), skip_confirm=True)
        assert isinstance(result, str) and result
        assert not source_file.exists()
        assert dest_file.read_text() == test_content

    def test_move_directory(self, tmp_path: Path) -> None:
        """Test moving a directory."""
        source_dir = tmp_path / "source_dir"
        dest_dir = tmp_path / "dest_dir"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("content")

        result = move_file(str(source_dir), str(dest_dir), skip_confirm=True)
        assert isinstance(result, str) and result
        assert not source_dir.exists()
        assert (dest_dir / "file.txt").read_text() == "content"

    def test_move_nonexistent_source(self, tmp_path: Path) -> None:
        """Test moving a file that doesn't exist."""
        nonexistent_file = tmp_path / "nonexistent.txt"
        dest_file = tmp_path / "destination.txt"

        with pytest.raises(FileSystemError, match="Source path not found"):
            move_file(str(nonexistent_file), str(dest_file), skip_confirm=True)

    def test_move_creates_destination_directory(self, tmp_path: Path) -> None:
        """Test moving a file to a destination with non-existent parent directories."""
        source_file = tmp_path / "source.txt"
        dest_file = tmp_path / "nested" / "dir" / "destination.txt"
        test_content = "Test content"
        source_file.write_text(test_content)

        result = move_file(str(source_file), str(dest_file), skip_confirm=True)
        assert isinstance(result, str) and result
        assert not source_file.exists()
        assert dest_file.read_text() == test_content

    def test_move_file_permission_denied(self, tmp_path: Path) -> None:
        """Test moving a file with permission denied."""
        source_file = tmp_path / "source.txt"
        dest_file = tmp_path / "destination.txt"
        source_file.write_text("content")

        with patch("shutil.move", side_effect=PermissionError("Access denied")):
            with pytest.raises(FileSystemError, match="Failed to move"):
                move_file(str(source_file), str(dest_file), skip_confirm=True)


class TestCopyFile:
    """Test cases for copy_file function."""

    def test_copy_file_to_new_location(self, tmp_path: Path) -> None:
        """Test copying a file to a new location."""
        source_file = tmp_path / "source.txt"
        dest_file = tmp_path / "destination.txt"
        test_content = "Test content"
        source_file.write_text(test_content)

        result = copy_file(str(source_file), str(dest_file), skip_confirm=True)
        assert isinstance(result, str) and result
        assert source_file.read_text() == test_content  # Original still exists
        assert dest_file.read_text() == test_content

    def test_copy_directory(self, tmp_path: Path) -> None:
        """Test copying a directory."""
        source_dir = tmp_path / "source_dir"
        dest_dir = tmp_path / "dest_dir"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("content")
        (source_dir / "subdir").mkdir()
        (source_dir / "subdir" / "nested.txt").write_text("nested")

        result = copy_file(str(source_dir), str(dest_dir), skip_confirm=True)
        assert isinstance(result, str) and result
        assert source_dir.exists()  # Original still exists
        assert (dest_dir / "file.txt").read_text() == "content"
        assert (dest_dir / "subdir" / "nested.txt").read_text() == "nested"

    def test_copy_nonexistent_source(self, tmp_path: Path) -> None:
        """Test copying a file that doesn't exist."""
        nonexistent_file = tmp_path / "nonexistent.txt"
        dest_file = tmp_path / "destination.txt"

        with pytest.raises(FileSystemError, match="Source path not found"):
            copy_file(str(nonexistent_file), str(dest_file), skip_confirm=True)

    def test_copy_creates_destination_directory(self, tmp_path: Path) -> None:
        """Test copying a file to a destination with non-existent parent directories."""
        source_file = tmp_path / "source.txt"
        dest_file = tmp_path / "nested" / "dir" / "destination.txt"
        test_content = "Test content"
        source_file.write_text(test_content)

        result = copy_file(str(source_file), str(dest_file), skip_confirm=True)
        assert isinstance(result, str) and result
        assert source_file.read_text() == test_content  # Original still exists
        assert dest_file.read_text() == test_content

    def test_copy_file_permission_denied(self, tmp_path: Path) -> None:
        """Test copying a file with permission denied."""
        source_file = tmp_path / "source.txt"
        dest_file = tmp_path / "destination.txt"
        source_file.write_text("content")

        with patch("shutil.copy2", side_effect=PermissionError("Access denied")):
            with pytest.raises(FileSystemError, match="Failed to copy"):
                copy_file(str(source_file), str(dest_file), skip_confirm=True)


class TestReplaceInFile:
    """Test cases for replace_in_file function."""

    def test_replace_single_occurrence(self, tmp_path: Path) -> None:
        """Test replacing a single occurrence of text."""
        test_file = tmp_path / "test.txt"
        original_content = "Hello world! This is a test."
        test_file.write_text(original_content)

        result = replace_in_file(str(test_file), "world", "universe", 1, skip_confirm=True)
        assert isinstance(result, str) and result
        assert test_file.read_text() == "Hello universe! This is a test."

    def test_replace_all_occurrences(self, tmp_path: Path) -> None:
        """Test replacing all occurrences of text."""
        test_file = tmp_path / "test.txt"
        original_content = "foo bar foo baz foo"
        test_file.write_text(original_content)

        result = replace_in_file(str(test_file), "foo", "bar", -1, skip_confirm=True)
        assert isinstance(result, str) and result
        assert test_file.read_text() == "bar bar bar baz bar"

    def test_replace_limited_count(self, tmp_path: Path) -> None:
        """Test replacing with a limited count."""
        test_file = tmp_path / "test.txt"
        original_content = "foo foo foo foo"
        test_file.write_text(original_content)

        result = replace_in_file(str(test_file), "foo", "bar", 2, skip_confirm=True)
        assert isinstance(result, str) and result
        assert test_file.read_text() == "bar bar foo foo"

    def test_replace_no_matches(self, tmp_path: Path) -> None:
        """Test replacing text that doesn't exist."""
        test_file = tmp_path / "test.txt"
        original_content = "Hello world!"
        test_file.write_text(original_content)

        result = replace_in_file(str(test_file), "xyz", "abc", 1, skip_confirm=True)
        assert isinstance(result, str) and result
        assert test_file.read_text() == original_content  # Unchanged

    def test_replace_empty_old_text(self, tmp_path: Path) -> None:
        """Test replacing with empty old_text."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with pytest.raises(ValueError, match="old_text cannot be empty"):
            replace_in_file(str(test_file), "", "new", 1, skip_confirm=True)

    def test_replace_nonexistent_file(self, tmp_path: Path) -> None:
        """Test replacing in a file that doesn't exist."""
        nonexistent_file = tmp_path / "nonexistent.txt"

        with pytest.raises(FileSystemError, match="File not found"):
            replace_in_file(str(nonexistent_file), "old", "new", 1, skip_confirm=True)

    def test_replace_multiline_text(self, tmp_path: Path) -> None:
        """Test replacing multiline text."""
        test_file = tmp_path / "test.txt"
        original_content = "Line 1\nOld text\nLine 3"
        test_file.write_text(original_content)

        result = replace_in_file(str(test_file), "Old text", "New text", 1, skip_confirm=True)
        assert isinstance(result, str) and result
        assert test_file.read_text() == "Line 1\nNew text\nLine 3"

    def test_replace_file_permission_denied(self, tmp_path: Path) -> None:
        """Test replacing in a file with permission denied."""
        test_file = tmp_path / "protected.txt"
        test_file.write_text("content")

        with patch(
            "pathlib.Path.read_text", side_effect=PermissionError("Access denied")
        ):
            with pytest.raises(FileSystemError, match="Failed to replace text in file"):
                replace_in_file(str(test_file), "old", "new", 1, skip_confirm=True)

    def test_replace_with_confirmation_required(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that replace requires confirmation when skip_confirm=False."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello world!")

        # Simulate non-TTY environment (agent mode)
        monkeypatch.setattr("sys.stdin.isatty", lambda: False)

        # Should raise error asking for confirmation
        with pytest.raises(Exception, match="CONFIRMATION_REQUIRED"):
            replace_in_file(str(test_file), "world", "universe", 1, skip_confirm=False)


class TestInsertAtLine:
    """Test cases for insert_at_line function."""

    def test_insert_at_beginning(self, tmp_path: Path) -> None:
        """Test inserting content at the beginning of a file."""
        test_file = tmp_path / "test.txt"
        original_content = "Line 1\nLine 2\nLine 3"
        test_file.write_text(original_content)

        result = insert_at_line(str(test_file), 1, "New first line", skip_confirm=True)
        assert isinstance(result, str) and result
        expected = "New first line\nLine 1\nLine 2\nLine 3"
        assert test_file.read_text() == expected

    def test_insert_in_middle(self, tmp_path: Path) -> None:
        """Test inserting content in the middle of a file."""
        test_file = tmp_path / "test.txt"
        original_content = "Line 1\nLine 2\nLine 3"
        test_file.write_text(original_content)

        result = insert_at_line(str(test_file), 2, "Inserted line", skip_confirm=True)
        assert isinstance(result, str) and result
        expected = "Line 1\nInserted line\nLine 2\nLine 3"
        assert test_file.read_text() == expected

    def test_insert_at_end(self, tmp_path: Path) -> None:
        """Test inserting content at the end of a file."""
        test_file = tmp_path / "test.txt"
        original_content = "Line 1\nLine 2"
        test_file.write_text(original_content)

        result = insert_at_line(str(test_file), 3, "New last line", skip_confirm=True)
        assert isinstance(result, str) and result
        expected = "Line 1\nLine 2New last line\n"
        assert test_file.read_text() == expected

    def test_insert_beyond_file_end(self, tmp_path: Path) -> None:
        """Test inserting content beyond the end of a file."""
        test_file = tmp_path / "test.txt"
        original_content = "Line 1\nLine 2"
        test_file.write_text(original_content)

        result = insert_at_line(str(test_file), 10, "Far beyond", skip_confirm=True)
        assert isinstance(result, str) and result
        expected = "Line 1\nLine 2Far beyond\n"
        assert test_file.read_text() == expected

    def test_insert_in_empty_file(self, tmp_path: Path) -> None:
        """Test inserting content in an empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")

        result = insert_at_line(str(test_file), 1, "First line", skip_confirm=True)
        assert isinstance(result, str) and result
        assert test_file.read_text() == "First line\n"

    def test_insert_content_with_newline(self, tmp_path: Path) -> None:
        """Test inserting content that already has a newline."""
        test_file = tmp_path / "test.txt"
        original_content = "Line 1\nLine 2"
        test_file.write_text(original_content)

        result = insert_at_line(str(test_file), 2, "Inserted line\n", skip_confirm=True)
        assert isinstance(result, str) and result
        expected = "Line 1\nInserted line\nLine 2"
        assert test_file.read_text() == expected

    def test_insert_invalid_line_number(self, tmp_path: Path) -> None:
        """Test inserting with invalid line number."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with pytest.raises(ValueError, match="line_number must be 1 or greater"):
            insert_at_line(str(test_file), 0, "content", skip_confirm=True)

        with pytest.raises(ValueError, match="line_number must be 1 or greater"):
            insert_at_line(str(test_file), -1, "content", skip_confirm=True)

    def test_insert_nonexistent_file(self, tmp_path: Path) -> None:
        """Test inserting in a file that doesn't exist."""
        nonexistent_file = tmp_path / "nonexistent.txt"

        with pytest.raises(FileSystemError, match="File not found"):
            insert_at_line(str(nonexistent_file), 1, "content", skip_confirm=True)

    def test_insert_file_permission_denied(self, tmp_path: Path) -> None:
        """Test inserting in a file with permission denied."""
        test_file = tmp_path / "protected.txt"
        test_file.write_text("content")

        with patch(
            "pathlib.Path.read_text", side_effect=PermissionError("Access denied")
        ):
            with pytest.raises(
                FileSystemError, match="Failed to insert content in file"
            ):
                insert_at_line(str(test_file), 1, "new content", skip_confirm=True)

    def test_insert_with_confirmation_required(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that insert requires confirmation when skip_confirm=False."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Line 1\nLine 2")

        # Simulate non-TTY environment (agent mode)
        monkeypatch.setattr("sys.stdin.isatty", lambda: False)

        # Should raise error asking for confirmation
        with pytest.raises(Exception, match="CONFIRMATION_REQUIRED"):
            insert_at_line(str(test_file), 2, "Inserted", skip_confirm=False)


# Integration tests
class TestOperationsIntegration:
    """Integration tests for multiple operations working together."""

    def test_write_read_workflow(self, tmp_path: Path) -> None:
        """Test writing then reading a file."""
        test_file = tmp_path / "workflow.txt"
        content = "Hello World!"

        write_result = write_file_from_string(
            str(test_file), content, skip_confirm=True
        )
        read_result = read_file_to_string(str(test_file))

        assert isinstance(write_result, str) and write_result
        assert read_result == content

    def test_copy_modify_workflow(self, tmp_path: Path) -> None:
        """Test copying a file then modifying it."""
        source_file = tmp_path / "source.txt"
        dest_file = tmp_path / "destination.txt"
        original_content = "Original content"
        source_file.write_text(original_content)

        # Copy file
        copy_result = copy_file(str(source_file), str(dest_file), skip_confirm=True)
        assert isinstance(copy_result, str) and copy_result

        # Modify copy
        replace_result = replace_in_file(str(dest_file), "Original", "Modified", 1, skip_confirm=True)
        assert isinstance(replace_result, str) and replace_result

        # Verify both files
        assert source_file.read_text() == original_content
        assert dest_file.read_text() == "Modified content"

    def test_directory_operations_workflow(self, tmp_path: Path) -> None:
        """Test creating, listing, and deleting directory operations."""
        test_dir = tmp_path / "test_workflow"

        # Create directory
        create_result = create_directory(str(test_dir), skip_confirm=True)
        assert isinstance(create_result, str) and create_result

        # Add some files
        (test_dir / "file1.txt").write_text("content1")
        (test_dir / "file2.txt").write_text("content2")

        # List contents
        contents = list_directory_contents(str(test_dir), True)
        assert sorted(contents) == ["file1.txt", "file2.txt"]

        # Delete directory
        delete_result = delete_directory(str(test_dir), True, skip_confirm=True)
        assert isinstance(delete_result, str) and delete_result
        assert not test_dir.exists()
