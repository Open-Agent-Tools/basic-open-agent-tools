"""Tests for basic_open_agent_tools.file_system.tree module."""

import os
from pathlib import Path

import pytest

from basic_open_agent_tools.exceptions import FileSystemError
from basic_open_agent_tools.file_system.tree import (
    generate_directory_tree,
    list_all_directory_contents,
)


class TestListAllDirectoryContents:
    """Test cases for list_all_directory_contents function."""

    def test_list_simple_directory(self, tmp_path: Path) -> None:
        """Test listing a simple directory with files."""
        # Create test structure
        (tmp_path / "file1.txt").touch()
        (tmp_path / "file2.py").touch()

        result = list_all_directory_contents(str(tmp_path))

        # Check that the tree format is correct and contains files
        assert tmp_path.name in result
        assert "file1.txt" in result
        assert "file2.py" in result
        assert "└──" in result or "├──" in result

    def test_list_nested_directory(self, tmp_path: Path) -> None:
        """Test listing a directory with subdirectories."""
        # Create nested structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "root_file.txt").touch()
        (subdir / "nested_file.txt").touch()

        result = list_all_directory_contents(str(tmp_path))

        # Check structure is represented
        assert tmp_path.name in result
        assert "root_file.txt" in result
        assert "subdir" in result
        assert "nested_file.txt" in result
        # Check tree formatting
        assert "└──" in result or "├──" in result

    def test_list_empty_directory(self, tmp_path: Path) -> None:
        """Test listing an empty directory."""
        result = list_all_directory_contents(str(tmp_path))

        # Should just show the directory name
        assert tmp_path.name in result

    def test_list_excludes_hidden_files(self, tmp_path: Path) -> None:
        """Test that hidden files are excluded by default."""
        # Create visible and hidden files
        (tmp_path / "visible.txt").touch()
        (tmp_path / ".hidden.txt").touch()
        (tmp_path / ".hidden_dir").mkdir()

        result = list_all_directory_contents(str(tmp_path))

        # Should include visible file but not hidden ones
        assert "visible.txt" in result
        assert ".hidden.txt" not in result
        assert ".hidden_dir" not in result

    def test_list_deep_nested_structure(self, tmp_path: Path) -> None:
        """Test listing a deeply nested directory structure."""
        # Create deep structure: root/level1/level2/level3
        level1 = tmp_path / "level1"
        level2 = level1 / "level2"
        level3 = level2 / "level3"
        level3.mkdir(parents=True)

        (tmp_path / "root.txt").touch()
        (level1 / "l1.txt").touch()
        (level2 / "l2.txt").touch()
        (level3 / "l3.txt").touch()

        result = list_all_directory_contents(str(tmp_path))

        # All levels should be represented
        assert "root.txt" in result
        assert "level1" in result
        assert "l1.txt" in result
        assert "level2" in result
        assert "l2.txt" in result
        assert "level3" in result
        assert "l3.txt" in result

    def test_list_sorted_output(self, tmp_path: Path) -> None:
        """Test that directory contents are sorted alphabetically."""
        # Create files in non-alphabetical order
        files = ["zebra.txt", "alpha.txt", "beta.txt"]
        for filename in files:
            (tmp_path / filename).touch()

        result = list_all_directory_contents(str(tmp_path))

        # Find positions of filenames in output
        alpha_pos = result.find("alpha.txt")
        beta_pos = result.find("beta.txt")
        zebra_pos = result.find("zebra.txt")

        # Should be in alphabetical order
        assert alpha_pos < beta_pos < zebra_pos

    def test_list_nonexistent_directory(self) -> None:
        """Test listing a nonexistent directory raises error."""
        with pytest.raises(FileSystemError, match="not found"):
            list_all_directory_contents("/nonexistent/directory")

    def test_list_file_instead_of_directory(self, tmp_path: Path) -> None:
        """Test listing a file instead of directory raises error."""
        test_file = tmp_path / "test.txt"
        test_file.touch()

        with pytest.raises(FileSystemError, match="Directory not found"):
            list_all_directory_contents(str(test_file))

    def test_list_permission_denied_subdirectory(self, tmp_path: Path) -> None:
        """Test handling permission denied errors gracefully."""
        # Create a subdirectory
        restricted_dir = tmp_path / "restricted"
        restricted_dir.mkdir()
        (restricted_dir / "file.txt").touch()

        # Remove read permissions (Unix only)
        if os.name != "nt":  # Skip on Windows
            restricted_dir.chmod(0o000)
            try:
                result = list_all_directory_contents(str(tmp_path))
                # Should contain error message for unreadable directory
                assert "Error reading directory" in result
            finally:
                # Restore permissions for cleanup
                restricted_dir.chmod(0o755)

    def test_list_empty_subdirectory(self, tmp_path: Path) -> None:
        """Test listing directory with empty subdirectories."""
        subdir = tmp_path / "empty_subdir"
        subdir.mkdir()
        (tmp_path / "file.txt").touch()

        result = list_all_directory_contents(str(tmp_path))

        assert "empty_subdir" in result
        assert "file.txt" in result


class TestGenerateDirectoryTree:
    """Test cases for generate_directory_tree function."""

    def test_generate_with_max_depth_0(self, tmp_path: Path) -> None:
        """Test generating tree with max depth 0 (root only)."""
        # Create nested structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "file.txt").touch()
        (subdir / "nested.txt").touch()

        result = generate_directory_tree(str(tmp_path), 0, False)

        # Should only show root directory name
        assert tmp_path.name in result
        assert "file.txt" not in result
        assert "subdir" not in result
        assert "nested.txt" not in result

    def test_generate_with_max_depth_1(self, tmp_path: Path) -> None:
        """Test generating tree with max depth 1."""
        # Create nested structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "file.txt").touch()
        (subdir / "nested.txt").touch()

        result = generate_directory_tree(str(tmp_path), 1, False)

        # Should show root and first level only
        assert tmp_path.name in result
        assert "file.txt" in result
        assert "subdir" in result
        assert "nested.txt" not in result  # Too deep

    def test_generate_with_max_depth_2(self, tmp_path: Path) -> None:
        """Test generating tree with max depth 2."""
        # Create deep structure
        level1 = tmp_path / "level1"
        level2 = level1 / "level2"
        level3 = level2 / "level3"
        level3.mkdir(parents=True)

        (tmp_path / "root.txt").touch()
        (level1 / "l1.txt").touch()
        (level2 / "l2.txt").touch()
        (level3 / "l3.txt").touch()

        result = generate_directory_tree(str(tmp_path), 2, False)

        # Should show up to level 2 directories, but not their contents beyond max_depth
        assert "root.txt" in result
        assert "level1" in result
        assert "l1.txt" in result
        assert "level2" in result
        # l2.txt is at depth 2, so it won't be shown (depth limit reached)
        assert "l2.txt" not in result  # At max depth boundary
        assert "level3" not in result  # Too deep
        assert "l3.txt" not in result  # Too deep

    def test_generate_include_hidden_true(self, tmp_path: Path) -> None:
        """Test generating tree with hidden files included."""
        # Create visible and hidden files
        (tmp_path / "visible.txt").touch()
        (tmp_path / ".hidden.txt").touch()
        hidden_dir = tmp_path / ".hidden_dir"
        hidden_dir.mkdir()
        (hidden_dir / "inside_hidden.txt").touch()

        result = generate_directory_tree(str(tmp_path), 5, True)

        # Should include both visible and hidden
        assert "visible.txt" in result
        assert ".hidden.txt" in result
        assert ".hidden_dir" in result
        assert "inside_hidden.txt" in result

    def test_generate_include_hidden_false(self, tmp_path: Path) -> None:
        """Test generating tree with hidden files excluded."""
        # Create visible and hidden files
        (tmp_path / "visible.txt").touch()
        (tmp_path / ".hidden.txt").touch()
        (tmp_path / ".hidden_dir").mkdir()

        result = generate_directory_tree(str(tmp_path), 5, False)

        # Should exclude hidden files
        assert "visible.txt" in result
        assert ".hidden.txt" not in result
        assert ".hidden_dir" not in result

    def test_generate_large_max_depth(self, tmp_path: Path) -> None:
        """Test generating tree with very large max depth."""
        # Create moderate depth structure
        current = tmp_path
        for i in range(5):
            current = current / f"level{i}"
            current.mkdir()
            (current / f"file{i}.txt").touch()

        result = generate_directory_tree(str(tmp_path), 100, False)

        # Should include all levels since max_depth is large
        for i in range(5):
            assert f"level{i}" in result
            assert f"file{i}.txt" in result

    def test_generate_tree_formatting(self, tmp_path: Path) -> None:
        """Test that tree formatting uses correct characters."""
        # Create simple structure
        (tmp_path / "file1.txt").touch()
        (tmp_path / "file2.txt").touch()
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.txt").touch()

        result = generate_directory_tree(str(tmp_path), 5, False)

        # Should contain tree formatting characters
        assert "└──" in result or "├──" in result
        # Should contain connecting lines for nested content
        if "subdir" in result and "nested.txt" in result:
            assert "│" in result or "    " in result

    def test_generate_nonexistent_directory(self) -> None:
        """Test generating tree for nonexistent directory raises error."""
        with pytest.raises(FileSystemError, match="not found"):
            generate_directory_tree("/nonexistent/directory", 5, False)

    def test_generate_file_instead_of_directory(self, tmp_path: Path) -> None:
        """Test generating tree for file instead of directory raises error."""
        test_file = tmp_path / "test.txt"
        test_file.touch()

        with pytest.raises(FileSystemError, match="Directory not found"):
            generate_directory_tree(str(test_file), 5, False)

    def test_generate_empty_directory(self, tmp_path: Path) -> None:
        """Test generating tree for empty directory."""
        result = generate_directory_tree(str(tmp_path), 5, False)

        # Should show just the directory name
        assert tmp_path.name in result

    def test_generate_permission_denied_subdirectory(self, tmp_path: Path) -> None:
        """Test handling permission denied errors gracefully."""
        # Create a subdirectory
        restricted_dir = tmp_path / "restricted"
        restricted_dir.mkdir()
        (restricted_dir / "file.txt").touch()

        # Remove read permissions (Unix only)
        if os.name != "nt":  # Skip on Windows
            restricted_dir.chmod(0o000)
            try:
                result = generate_directory_tree(str(tmp_path), 5, False)
                # Should contain error message for unreadable directory
                assert "Error reading directory" in result
            finally:
                # Restore permissions for cleanup
                restricted_dir.chmod(0o755)

    def test_generate_sorted_contents(self, tmp_path: Path) -> None:
        """Test that generated tree contents are sorted."""
        # Create files in non-alphabetical order
        files = ["zebra.txt", "alpha.txt", "beta.txt"]
        for filename in files:
            (tmp_path / filename).touch()

        result = generate_directory_tree(str(tmp_path), 5, False)

        # Find positions of filenames in output
        alpha_pos = result.find("alpha.txt")
        beta_pos = result.find("beta.txt")
        zebra_pos = result.find("zebra.txt")

        # Should be in alphabetical order
        assert alpha_pos < beta_pos < zebra_pos

    def test_generate_mixed_files_and_directories(self, tmp_path: Path) -> None:
        """Test tree generation with mixed files and directories."""
        # Create mixed content
        (tmp_path / "file1.txt").touch()
        dir1 = tmp_path / "dir1"
        dir1.mkdir()
        (tmp_path / "file2.txt").touch()
        dir2 = tmp_path / "dir2"
        dir2.mkdir()
        (dir1 / "nested1.txt").touch()
        (dir2 / "nested2.txt").touch()

        result = generate_directory_tree(str(tmp_path), 5, False)

        # All content should be included
        assert "file1.txt" in result
        assert "file2.txt" in result
        assert "dir1" in result
        assert "dir2" in result
        assert "nested1.txt" in result
        assert "nested2.txt" in result

    def test_generate_negative_max_depth(self, tmp_path: Path) -> None:
        """Test tree generation with negative max depth."""
        (tmp_path / "file.txt").touch()

        # Negative depth should show nothing beyond root
        result = generate_directory_tree(str(tmp_path), -1, False)

        # Should only show root directory
        assert tmp_path.name in result
        assert "file.txt" not in result


# Integration tests
class TestTreeIntegration:
    """Integration tests for tree functions."""

    def test_both_functions_same_structure(self, tmp_path: Path) -> None:
        """Test that both functions handle the same structure consistently."""
        # Create identical test structure
        (tmp_path / "file.txt").touch()
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.txt").touch()

        # Get results from both functions
        list_result = list_all_directory_contents(str(tmp_path))
        tree_result = generate_directory_tree(str(tmp_path), 10, False)

        # Both should contain the same files (though formatting may differ)
        for filename in ["file.txt", "subdir", "nested.txt"]:
            assert filename in list_result
            assert filename in tree_result

    def test_consistent_error_handling(self, tmp_path: Path) -> None:
        """Test that both functions handle errors consistently."""
        test_file = tmp_path / "test.txt"
        test_file.touch()

        # Both should raise similar errors for non-directories
        with pytest.raises(FileSystemError):
            list_all_directory_contents(str(test_file))

        with pytest.raises(FileSystemError):
            generate_directory_tree(str(test_file), 5, False)
