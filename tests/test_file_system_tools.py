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

    def test_submodule_imports(self):
        """Test that individual submodules can be imported."""
        from basic_open_agent_tools.file_system.info import file_exists
        from basic_open_agent_tools.file_system.operations import read_file_to_string
        from basic_open_agent_tools.file_system.tree import list_all_directory_contents
        from basic_open_agent_tools.file_system.validation import validate_path

        # Just test that imports work
        assert callable(read_file_to_string)
        assert callable(file_exists)
        assert callable(list_all_directory_contents)
        assert callable(validate_path)
