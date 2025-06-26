"""Tests for file system tools module."""

import os
import tempfile

from basic_open_agent_tools import file_system


class TestFileSystemModule:
    """Test cases for file system module."""

    def test_read_write_file(self):
        """Test basic file read/write operations."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            test_file = f.name

        try:
            # Test write
            content = "Hello, World!"
            result = file_system.write_file_from_string(test_file, content)
            assert result is True

            # Test read
            read_content = file_system.read_file_to_string(test_file)
            assert read_content == content

        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)

    def test_file_exists(self):
        """Test file existence checking."""
        with tempfile.NamedTemporaryFile() as f:
            assert file_system.file_exists(f.name) is True

        assert file_system.file_exists("/nonexistent/file.txt") is False

    def test_directory_operations(self):
        """Test directory operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_subdir = os.path.join(temp_dir, "test_subdir")

            # Test directory creation
            result = file_system.create_directory(test_subdir)
            assert result is True
            assert file_system.directory_exists(test_subdir) is True

            # Test listing directory contents
            contents = file_system.list_directory_contents(temp_dir)
            assert "test_subdir" in contents

    def test_enhanced_tree_functionality(self):
        """Test enhanced directory tree functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test structure
            os.makedirs(os.path.join(temp_dir, "subdir1"))
            os.makedirs(os.path.join(temp_dir, "subdir1", "nested"))

            with open(os.path.join(temp_dir, "file1.txt"), "w") as f:
                f.write("test")
            with open(os.path.join(temp_dir, "subdir1", "file2.txt"), "w") as f:
                f.write("test")

            # Test enhanced tree function
            tree = file_system.generate_directory_tree(temp_dir, max_depth=2)
            assert "subdir1" in tree
            assert "file1.txt" in tree
            assert "file2.txt" in tree

            # Test depth limiting
            shallow_tree = file_system.generate_directory_tree(temp_dir, max_depth=1)
            assert "subdir1" in shallow_tree
            assert "nested" not in shallow_tree

    def test_replace_in_file(self):
        """Test targeted text replacement in files."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            test_file = f.name

        try:
            # Create test file with content
            content = "Hello world!\nThis is a test.\nHello again!"
            file_system.write_file_from_string(test_file, content)

            # Test replacement
            result = file_system.replace_in_file(test_file, "Hello", "Hi")
            assert result is True

            # Verify replacement
            updated_content = file_system.read_file_to_string(test_file)
            assert "Hi world!" in updated_content
            assert "Hi again!" in updated_content
            assert "This is a test." in updated_content

            # Test limited replacement count
            file_system.write_file_from_string(test_file, content)
            result = file_system.replace_in_file(test_file, "Hello", "Hi", count=1)
            assert result is True

            updated_content = file_system.read_file_to_string(test_file)
            assert updated_content.count("Hi") == 1
            assert updated_content.count("Hello") == 1

        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)

    def test_insert_at_line(self):
        """Test inserting content at specific line numbers."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            test_file = f.name

        try:
            # Create test file with multiple lines
            content = "Line 1\nLine 2\nLine 3"
            file_system.write_file_from_string(test_file, content)

            # Test inserting at beginning
            result = file_system.insert_at_line(test_file, 1, "New Line 1")
            assert result is True

            updated_content = file_system.read_file_to_string(test_file)
            lines = updated_content.split("\n")
            assert lines[0] == "New Line 1"
            assert lines[1] == "Line 1"

            # Test inserting in middle
            file_system.write_file_from_string(test_file, content)
            result = file_system.insert_at_line(test_file, 2, "Inserted Line")
            assert result is True

            updated_content = file_system.read_file_to_string(test_file)
            lines = updated_content.split("\n")
            assert lines[0] == "Line 1"
            assert lines[1] == "Inserted Line"
            assert lines[2] == "Line 2"

            # Test inserting beyond file length (should append)
            file_system.write_file_from_string(test_file, content)
            result = file_system.insert_at_line(test_file, 10, "Appended Line")
            assert result is True

            updated_content = file_system.read_file_to_string(test_file)
            assert "Appended Line" in updated_content

        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)

    def test_submodule_imports(self):
        """Test that individual submodules can be imported."""
        from basic_open_agent_tools.file_system.info import file_exists
        from basic_open_agent_tools.file_system.operations import (
            insert_at_line,
            read_file_to_string,
            replace_in_file,
        )
        from basic_open_agent_tools.file_system.tree import list_all_directory_contents
        from basic_open_agent_tools.file_system.validation import validate_path

        # Just test that imports work
        assert callable(read_file_to_string)
        assert callable(replace_in_file)
        assert callable(insert_at_line)
        assert callable(file_exists)
        assert callable(list_all_directory_contents)
        assert callable(validate_path)
