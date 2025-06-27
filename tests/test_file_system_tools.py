"""Tests for file system tools module.

This module provides comprehensive tests for the file system toolkit functions,
including both unit tests and integration tests for different usage patterns.
"""

import inspect
import os
import tempfile

import pytest

from basic_open_agent_tools.file_system import (
    append_to_file,
    copy_file,
    create_directory,
    delete_directory,
    delete_file,
    directory_exists,
    file_exists,
    generate_directory_tree,
    get_file_info,
    get_file_size,
    insert_at_line,
    is_empty_directory,
    list_all_directory_contents,
    list_directory_contents,
    move_file,
    read_file_to_string,
    replace_in_file,
    validate_file_content,
    validate_path,
    write_file_from_string,
)


class TestFileSystemOperations:
    """Test cases for file system operations."""

    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            test_file = f.name

        yield test_file

        # Cleanup
        if os.path.exists(test_file):
            os.unlink(test_file)

    @pytest.fixture
    def temp_directory_with_files(self):
        """Create a temporary directory with test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test structure
            os.makedirs(os.path.join(temp_dir, "subdir1"))
            os.makedirs(os.path.join(temp_dir, "subdir1", "nested"))
            os.makedirs(os.path.join(temp_dir, "subdir2"))
            os.makedirs(os.path.join(temp_dir, ".hidden"))

            # Create test files
            test_files = {
                "file1.txt": "Content of file 1",
                "file2.md": "# Markdown file\nContent here",
                "subdir1/nested_file.py": "print('nested file')",
                "subdir1/nested/deep_file.json": '{"key": "value"}',
                "subdir2/another_file.txt": "Another file content",
                ".hidden/secret.txt": "secret content",
            }

            for file_path, content in test_files.items():
                full_path = os.path.join(temp_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w") as f:
                    f.write(content)

            yield temp_dir

    def test_file_read_write_operations(self, temp_file):
        """Test basic file read/write operations."""
        # Test write
        content = "Hello, World!\nThis is a test file.\nWith multiple lines."
        result = write_file_from_string(temp_file, content)
        assert result is True

        # Test read
        read_content = read_file_to_string(temp_file)
        assert read_content == content

        # Test append
        append_content = "\nAppended line"
        result = append_to_file(temp_file, append_content)
        assert result is True

        # Verify append
        updated_content = read_file_to_string(temp_file)
        assert updated_content == content + append_content

    def test_file_existence_and_info(self, temp_file):
        """Test file existence checking and information retrieval."""
        # Test non-existent file
        assert file_exists("/nonexistent/file.txt") is False

        # Create file and test existence
        write_file_from_string(temp_file, "test content")
        assert file_exists(temp_file) is True

        # Test file size
        size = get_file_size(temp_file)
        assert size > 0

        # Test file info
        info = get_file_info(temp_file)
        assert "size" in info
        assert "modified_time" in info
        assert "is_file" in info
        assert info["size"] > 0

    def test_directory_operations(self, temp_directory_with_files):
        """Test directory operations."""
        # Test directory existence
        assert directory_exists(temp_directory_with_files) is True
        assert directory_exists("/nonexistent/directory") is False

        # Test creating new directory
        new_dir = os.path.join(temp_directory_with_files, "new_subdir")
        result = create_directory(new_dir)
        assert result is True
        assert directory_exists(new_dir) is True

        # Test empty directory check
        assert is_empty_directory(new_dir) is True
        assert is_empty_directory(temp_directory_with_files) is False

        # Test directory listing
        contents = list_directory_contents(temp_directory_with_files, False)
        assert "subdir1" in contents
        assert "subdir2" in contents
        assert "file1.txt" in contents
        assert "file2.md" in contents
        assert ".hidden" not in contents  # Hidden files excluded

        # Test directory listing with hidden files
        contents_with_hidden = list_directory_contents(temp_directory_with_files, True)
        assert ".hidden" in contents_with_hidden

    def test_file_manipulation_operations(self, temp_file):
        """Test file manipulation operations."""
        # Create initial content
        content = "Line 1\nLine 2\nLine 3\nLine 4"
        write_file_from_string(temp_file, content)

        # Test text replacement
        result = replace_in_file(temp_file, "Line 2", "Modified Line 2", -1)
        assert result is True

        updated_content = read_file_to_string(temp_file)
        assert "Modified Line 2" in updated_content
        # Note: Line 2 might still exist in other lines, check specific replacement
        lines = updated_content.split("\n")
        assert lines[1] == "Modified Line 2"

        # Test limited replacement count
        write_file_from_string(temp_file, "Hello Hello Hello")
        result = replace_in_file(temp_file, "Hello", "Hi", 2)
        assert result is True

        updated_content = read_file_to_string(temp_file)
        assert updated_content.count("Hi") == 2
        assert updated_content.count("Hello") == 1

        # Test line insertion
        write_file_from_string(temp_file, "Line 1\nLine 2\nLine 3")
        result = insert_at_line(temp_file, 2, "Inserted Line")
        assert result is True

        updated_content = read_file_to_string(temp_file)
        lines = updated_content.split("\n")
        assert lines[0] == "Line 1"
        assert lines[1] == "Inserted Line"
        assert lines[2] == "Line 2"
        assert lines[3] == "Line 3"

    def test_file_copy_move_delete(self, temp_directory_with_files):
        """Test file copy, move, and delete operations."""
        source_file = os.path.join(temp_directory_with_files, "file1.txt")
        copy_destination = os.path.join(temp_directory_with_files, "file1_copy.txt")
        move_destination = os.path.join(
            temp_directory_with_files, "subdir1", "file1_moved.txt"
        )

        # Test file copy
        result = copy_file(source_file, copy_destination)
        assert result is True
        assert file_exists(copy_destination) is True

        # Verify copy content
        original_content = read_file_to_string(source_file)
        copied_content = read_file_to_string(copy_destination)
        assert original_content == copied_content

        # Test file move
        result = move_file(copy_destination, move_destination)
        assert result is True
        assert file_exists(move_destination) is True
        assert file_exists(copy_destination) is False

        # Test file delete
        result = delete_file(move_destination)
        assert result is True
        assert file_exists(move_destination) is False

        # Test directory delete
        empty_dir = os.path.join(temp_directory_with_files, "empty_dir")
        create_directory(empty_dir)
        result = delete_directory(empty_dir, False)  # Non-recursive for empty dir
        assert result is True
        assert directory_exists(empty_dir) is False

    def test_tree_operations(self, temp_directory_with_files):
        """Test directory tree operations."""
        # Test basic tree generation
        tree = generate_directory_tree(temp_directory_with_files, 3, False)
        assert "subdir1" in tree
        assert "subdir2" in tree
        assert "file1.txt" in tree
        assert "file2.md" in tree
        assert "nested_file.py" in tree
        assert "deep_file.json" in tree
        assert ".hidden" not in tree  # Hidden files excluded

        # Test tree with hidden files
        tree_with_hidden = generate_directory_tree(temp_directory_with_files, 3, True)
        assert ".hidden" in tree_with_hidden
        assert "secret.txt" in tree_with_hidden

        # Test depth limiting
        shallow_tree = generate_directory_tree(temp_directory_with_files, 1, False)
        assert "subdir1" in shallow_tree
        assert "file1.txt" in shallow_tree
        assert "nested_file.py" not in shallow_tree  # Too deep
        assert "deep_file.json" not in shallow_tree  # Too deep

        # Test complete directory listing
        all_contents = list_all_directory_contents(temp_directory_with_files)
        assert len(all_contents) > 0
        # Should include nested files in the tree string
        assert "subdir1" in all_contents
        assert "nested_file.py" in all_contents

    def test_validation_operations(self, temp_file):
        """Test validation operations."""
        # Test path validation - it should return a Path object, not boolean
        from pathlib import Path

        result_path = validate_path(temp_file, "test")
        assert isinstance(result_path, Path)

        # Test file content validation
        write_file_from_string(temp_file, "valid content")
        # validate_file_content validates content string, not file content
        validate_file_content("valid content", "test")  # Should not raise


class TestFileSystemCompatibility:
    """Test Google AI compatibility for file system functions."""

    def test_function_signatures_compatibility(self):
        """Test that all file system functions have Google AI compatible signatures."""
        functions_to_test = [
            read_file_to_string,
            write_file_from_string,
            append_to_file,
            replace_in_file,
            insert_at_line,
            list_directory_contents,
            create_directory,
            delete_file,
            delete_directory,
            move_file,
            copy_file,
            get_file_info,
            file_exists,
            directory_exists,
            get_file_size,
            is_empty_directory,
            list_all_directory_contents,
            generate_directory_tree,
            validate_path,
            validate_file_content,
        ]

        for func in functions_to_test:
            sig = inspect.signature(func)

            # Check that no parameters have default values
            for param_name, param in sig.parameters.items():
                assert param.default == inspect.Parameter.empty, (
                    f"Function {func.__name__} parameter {param_name} has default value, "
                    "violating Google AI requirements"
                )

            # Check that return type is specified
            assert sig.return_annotation != inspect.Signature.empty, (
                f"Function {func.__name__} missing return type annotation"
            )

    def test_parameter_types_compatibility(self):
        """Test that parameter types are Google AI compatible."""
        # Test specific functions with known parameter types
        sig = inspect.signature(generate_directory_tree)
        params = sig.parameters

        assert params["directory_path"].annotation is str
        assert params["max_depth"].annotation is int
        assert params["include_hidden"].annotation is bool
        assert sig.return_annotation is str

        # Test list_directory_contents
        sig = inspect.signature(list_directory_contents)
        params = sig.parameters

        assert params["directory_path"].annotation is str
        assert params["include_hidden"].annotation is bool
        # Should return List[str] - check if it's a list type
        return_annotation = sig.return_annotation
        assert (
            hasattr(return_annotation, "__origin__")
            and return_annotation.__origin__ is list
        )


class TestFileSystemIntegration:
    """Integration tests combining multiple file system operations."""

    @pytest.fixture
    def temp_directory_with_files(self):
        """Create a temporary directory with test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test structure
            os.makedirs(os.path.join(temp_dir, "subdir1"))
            os.makedirs(os.path.join(temp_dir, "subdir1", "nested"))
            os.makedirs(os.path.join(temp_dir, "subdir2"))
            os.makedirs(os.path.join(temp_dir, ".hidden"))

            # Create test files
            test_files = {
                "file1.txt": "Content of file 1",
                "file2.md": "# Markdown file\nContent here",
                "subdir1/nested_file.py": "print('nested file')",
                "subdir1/nested/deep_file.json": '{"key": "value"}',
                "subdir2/another_file.txt": "Another file content",
                ".hidden/secret.txt": "secret content",
            }

            for file_path, content in test_files.items():
                full_path = os.path.join(temp_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w") as f:
                    f.write(content)

            yield temp_dir

    def test_complete_file_workflow(self, temp_directory_with_files):
        """Test complete file manipulation workflow."""
        # Create a new file
        new_file = os.path.join(temp_directory_with_files, "workflow_test.txt")
        initial_content = "Initial content\nLine 2\nLine 3"

        # Write initial content
        write_file_from_string(new_file, initial_content)
        assert file_exists(new_file) is True

        # Modify content
        replace_in_file(new_file, "Line 2", "Modified Line 2", -1)
        insert_at_line(new_file, 1, "Inserted at beginning")
        append_to_file(new_file, "\nAppended at end")

        # Verify final content
        final_content = read_file_to_string(new_file)
        lines = final_content.split("\n")
        assert lines[0] == "Inserted at beginning"
        assert lines[1] == "Initial content"
        assert lines[2] == "Modified Line 2"
        assert lines[3] == "Line 3"
        assert lines[4] == "Appended at end"

        # Copy to backup
        backup_file = os.path.join(temp_directory_with_files, "workflow_backup.txt")
        copy_file(new_file, backup_file)

        # Verify backup
        backup_content = read_file_to_string(backup_file)
        assert backup_content == final_content

        # Move to subdirectory
        moved_file = os.path.join(
            temp_directory_with_files, "subdir1", "workflow_moved.txt"
        )
        move_file(backup_file, moved_file)

        assert file_exists(moved_file) is True
        assert file_exists(backup_file) is False

        # Clean up
        delete_file(new_file)
        delete_file(moved_file)

        assert file_exists(new_file) is False
        assert file_exists(moved_file) is False

    def test_directory_tree_analysis_workflow(self, temp_directory_with_files):
        """Test directory analysis workflow using tree operations."""
        # Get basic directory structure
        contents = list_directory_contents(temp_directory_with_files, False)
        assert len(contents) > 0

        # Get detailed tree view
        tree = generate_directory_tree(temp_directory_with_files, 3, False)

        # Verify tree contains expected structure
        expected_items = ["subdir1", "subdir2", "file1.txt", "file2.md"]
        for item in expected_items:
            assert item in tree

        # Get complete file listing
        all_files = list_all_directory_contents(temp_directory_with_files)

        # Should have more files than just top-level
        assert len(all_files) > len(contents)

        # Should include nested files in the string representation
        assert "subdir1" in all_files
        assert "nested_file.py" in all_files


class TestModuleImports:
    """Test that functions can be imported individually and from different locations."""

    def test_individual_function_imports(self):
        """Test that individual functions can be imported from their specific modules."""
        # Test info module imports
        from basic_open_agent_tools.file_system.info import (
            directory_exists,
            file_exists,
            get_file_info,
            get_file_size,
            is_empty_directory,
        )

        # Test operations module imports
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

        # Test tree module imports
        from basic_open_agent_tools.file_system.tree import (
            generate_directory_tree,
            list_all_directory_contents,
        )

        # Test validation module imports
        from basic_open_agent_tools.file_system.validation import (
            validate_file_content,
            validate_path,
        )

        # Verify all imports are callable
        functions = [
            directory_exists,
            file_exists,
            get_file_info,
            get_file_size,
            is_empty_directory,
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
            generate_directory_tree,
            list_all_directory_contents,
            validate_file_content,
            validate_path,
        ]

        for func in functions:
            assert callable(func), f"Function {func.__name__} is not callable"

    def test_module_level_imports(self):
        """Test that functions can be imported from the main file_system module."""
        # All functions should be available from the main module
        from basic_open_agent_tools.file_system import (
            append_to_file,
            copy_file,
            create_directory,
            delete_directory,
            delete_file,
            directory_exists,
            file_exists,
            generate_directory_tree,
            get_file_info,
            get_file_size,
            insert_at_line,
            is_empty_directory,
            list_all_directory_contents,
            list_directory_contents,
            move_file,
            read_file_to_string,
            replace_in_file,
            validate_file_content,
            validate_path,
            write_file_from_string,
        )

        # Test that they're all callable
        functions = [
            append_to_file,
            copy_file,
            create_directory,
            delete_directory,
            delete_file,
            directory_exists,
            file_exists,
            generate_directory_tree,
            get_file_info,
            get_file_size,
            insert_at_line,
            is_empty_directory,
            list_all_directory_contents,
            list_directory_contents,
            move_file,
            read_file_to_string,
            replace_in_file,
            validate_file_content,
            validate_path,
            write_file_from_string,
        ]

        for func in functions:
            assert callable(func), f"Function {func.__name__} is not callable"
