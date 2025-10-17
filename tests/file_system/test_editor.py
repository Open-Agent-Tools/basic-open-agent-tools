"""Tests for the file editor tool."""

import json
from pathlib import Path

import pytest

from basic_open_agent_tools.exceptions import FileSystemError
from basic_open_agent_tools.file_system.editor import file_editor


class TestFileEditor:
    """Test cases for the file_editor function."""

    def test_view_file(self, tmp_path: Path) -> None:
        """Test viewing a file."""
        test_file = tmp_path / "test.txt"
        test_content = "line 1\nline 2\nline 3\n"
        test_file.write_text(test_content)

        result = file_editor("view", str(test_file), False, "{}")
        assert "test.txt" in result
        assert "1: line 1" in result
        assert "2: line 2" in result
        assert "3: line 3" in result

    def test_view_file_with_range(self, tmp_path: Path) -> None:
        """Test viewing a file with line range."""
        test_file = tmp_path / "test.txt"
        test_content = "line 1\nline 2\nline 3\nline 4\n"
        test_file.write_text(test_content)

        result = file_editor("view", str(test_file), False, '{"view_range": "2-3"}')
        assert "Lines 2-3:" in result
        assert "2: line 2" in result
        assert "3: line 3" in result
        assert "1: line 1" not in result
        assert "4: line 4" not in result

    def test_view_directory(self, tmp_path: Path) -> None:
        """Test viewing a directory."""
        # Create some test files
        (tmp_path / "file1.txt").write_text("content")
        (tmp_path / "subdir").mkdir()

        result = file_editor("view", str(tmp_path), False, "{}")
        assert "Directory contents" in result
        assert "FILE: file1.txt" in result
        assert "DIR: subdir" in result

    def test_create_file(self, tmp_path: Path) -> None:
        """Test creating a new file."""
        test_file = tmp_path / "new_file.txt"
        test_content = "Hello, world!"

        result = file_editor(
            "create", str(test_file), False, json.dumps({"content": test_content})
        )
        assert "Created file" in result
        assert test_file.exists()
        assert test_file.read_text() == test_content

    def test_create_file_force_overwrite(self, tmp_path: Path) -> None:
        """Test creating a file with force=True overwrites existing file."""
        test_file = tmp_path / "existing.txt"
        test_file.write_text("original content")

        new_content = "new content"
        result = file_editor(
            "create", str(test_file), True, json.dumps({"content": new_content})
        )
        assert "file" in result
        assert test_file.read_text() == new_content

    def test_create_file_exists_no_force(self, tmp_path: Path) -> None:
        """Test creating a file that exists without force raises error."""
        test_file = tmp_path / "existing.txt"
        test_file.write_text("original content")

        with pytest.raises(FileSystemError, match="CONFIRMATION_REQUIRED"):
            file_editor("create", str(test_file), False, '{"content": "new content"}')

    def test_str_replace(self, tmp_path: Path) -> None:
        """Test string replacement in file."""
        test_file = tmp_path / "test.txt"
        test_content = "Hello world\nHello universe\n"
        test_file.write_text(test_content)

        result = file_editor(
            "str_replace",
            str(test_file),
            False,
            '{"old_str": "Hello", "new_str": "Hi"}',
        )
        assert "Replaced 2 occurrence(s)" in result

        updated_content = test_file.read_text()
        assert "Hi world" in updated_content
        assert "Hi universe" in updated_content

    def test_str_replace_no_matches(self, tmp_path: Path) -> None:
        """Test string replacement with no matches."""
        test_file = tmp_path / "test.txt"
        test_content = "Hello world\n"
        test_file.write_text(test_content)

        result = file_editor(
            "str_replace",
            str(test_file),
            False,
            '{"old_str": "goodbye", "new_str": "farewell"}',
        )
        assert "No occurrences" in result

    def test_insert_at_line(self, tmp_path: Path) -> None:
        """Test inserting content at specific line."""
        test_file = tmp_path / "test.txt"
        test_content = "line 1\nline 2\nline 3\n"
        test_file.write_text(test_content)

        result = file_editor(
            "insert",
            str(test_file),
            False,
            '{"line_number": 2, "content": "inserted line"}',
        )
        assert "Inserted content at line 2" in result

        updated_content = test_file.read_text()
        lines = updated_content.splitlines()
        assert lines[1] == "inserted line"
        assert lines[2] == "line 2"

    def test_insert_at_end(self, tmp_path: Path) -> None:
        """Test inserting content beyond file length."""
        test_file = tmp_path / "test.txt"
        test_content = "line 1\nline 2\n"
        test_file.write_text(test_content)

        result = file_editor(
            "insert",
            str(test_file),
            False,
            '{"line_number": 10, "content": "appended line"}',
        )
        assert "end" in result

        updated_content = test_file.read_text()
        assert "appended line" in updated_content

    def test_find_text(self, tmp_path: Path) -> None:
        """Test finding text in file."""
        test_file = tmp_path / "test.txt"
        test_content = "apple\nbanana\napple pie\ncherry\n"
        test_file.write_text(test_content)

        result = file_editor("find", str(test_file), False, '{"pattern": "apple"}')
        assert "Found 2 match(es)" in result
        assert "1: apple" in result
        assert "3: apple pie" in result

    def test_find_regex(self, tmp_path: Path) -> None:
        """Test finding text with regex pattern."""
        test_file = tmp_path / "test.txt"
        test_content = "apple123\nbanana\napple456\ncherry\n"
        test_file.write_text(test_content)

        result = file_editor(
            "find",
            str(test_file),
            False,
            r'{"pattern": "apple\\d+", "use_regex": true}',
        )
        assert "Found 2 match(es)" in result
        assert "apple123" in result
        assert "apple456" in result

    def test_find_no_matches(self, tmp_path: Path) -> None:
        """Test finding text with no matches."""
        test_file = tmp_path / "test.txt"
        test_content = "apple\nbanana\n"
        test_file.write_text(test_content)

        result = file_editor("find", str(test_file), False, '{"pattern": "orange"}')
        assert "No matches found" in result

    def test_invalid_command(self, tmp_path: Path) -> None:
        """Test invalid command raises error."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with pytest.raises(ValueError, match="Invalid command"):
            file_editor("invalid_command", str(test_file), False, "{}")

    def test_missing_parameters(self, tmp_path: Path) -> None:
        """Test missing required parameters raise errors."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        # str_replace missing parameters
        with pytest.raises(ValueError, match="requires 'old_str' and 'new_str'"):
            file_editor("str_replace", str(test_file), False, '{"old_str": "hello"}')

        # insert missing parameters
        with pytest.raises(ValueError, match="requires 'line_number' and 'content'"):
            file_editor("insert", str(test_file), False, '{"line_number": 1}')

        # find missing parameters
        with pytest.raises(ValueError, match="requires 'pattern'"):
            file_editor("find", str(test_file), False, "{}")

    def test_file_not_found(self, tmp_path: Path) -> None:
        """Test operations on non-existent files raise errors."""
        nonexistent_file = tmp_path / "nonexistent.txt"

        with pytest.raises(FileSystemError, match="File not found"):
            file_editor("view", str(nonexistent_file), False, "{}")

        with pytest.raises(FileSystemError, match="File not found"):
            file_editor(
                "str_replace",
                str(nonexistent_file),
                False,
                '{"old_str": "old", "new_str": "new"}',
            )

    def test_invalid_line_range(self, tmp_path: Path) -> None:
        """Test invalid line range formats."""
        test_file = tmp_path / "test.txt"
        test_content = "line 1\nline 2\nline 3\n"
        test_file.write_text(test_content)

        # Test invalid range format
        with pytest.raises(ValueError, match="Invalid line range format"):
            file_editor("view", str(test_file), False, '{"view_range": "a-b"}')

        # Test invalid single line
        with pytest.raises(ValueError, match="Invalid line number"):
            file_editor("view", str(test_file), False, '{"view_range": "abc"}')

    def test_str_replace_empty_old_text(self, tmp_path: Path) -> None:
        """Test str_replace with empty old_str raises error."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with pytest.raises(ValueError, match="old_str cannot be empty"):
            file_editor(
                "str_replace",
                str(test_file),
                False,
                '{"old_str": "", "new_str": "replacement"}',
            )

    def test_invalid_regex_pattern(self, tmp_path: Path) -> None:
        """Test invalid regex pattern raises error."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with pytest.raises(ValueError, match="Invalid regex pattern"):
            file_editor(
                "find", str(test_file), False, '{"pattern": "[", "use_regex": true}'
            )
