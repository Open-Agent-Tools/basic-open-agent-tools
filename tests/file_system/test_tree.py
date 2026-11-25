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
        (tmp_path / "file1.txt").touch()
        (tmp_path / "file2.py").touch()

        result = list_all_directory_contents(str(tmp_path))

        assert tmp_path.name in result
        assert "file1.txt" in result
        assert "file2.py" in result
        assert "└──" in result or "├──" in result

    def test_list_nested_directory(self, tmp_path: Path) -> None:
        """Test listing a directory with subdirectories."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "root_file.txt").touch()
        (subdir / "nested_file.txt").touch()

        result = list_all_directory_contents(str(tmp_path))

        assert tmp_path.name in result
        assert "root_file.txt" in result
        assert "subdir" in result
        assert "nested_file.txt" in result
        assert "└──" in result or "├──" in result

    def test_list_empty_directory(self, tmp_path: Path) -> None:
        """Test listing an empty directory."""
        result = list_all_directory_contents(str(tmp_path))

        assert tmp_path.name in result

    def test_list_excludes_hidden_files(self, tmp_path: Path) -> None:
        """Test that hidden files are excluded by default."""
        (tmp_path / "visible.txt").touch()
        (tmp_path / ".hidden.txt").touch()
        (tmp_path / ".hidden_dir").mkdir()

        result = list_all_directory_contents(str(tmp_path))

        assert "visible.txt" in result
        assert ".hidden.txt" not in result
        assert ".hidden_dir" not in result

    def test_list_deep_nested_structure(self, tmp_path: Path) -> None:
        """Test listing a deeply nested directory structure."""
        level1 = tmp_path / "level1"
        level2 = level1 / "level2"
        level3 = level2 / "level3"
        level3.mkdir(parents=True)

        (tmp_path / "root.txt").touch()
        (level1 / "l1.txt").touch()
        (level2 / "l2.txt").touch()
        (level3 / "l3.txt").touch()

        result = list_all_directory_contents(str(tmp_path))

        assert "root.txt" in result
        assert "level1" in result
        assert "l1.txt" in result
        assert "level2" in result
        assert "l2.txt" in result
        assert "level3" in result
        assert "l3.txt" in result

    def test_list_sorted_output(self, tmp_path: Path) -> None:
        """Test that directory contents are sorted alphabetically."""
        files = ["zebra.txt", "alpha.txt", "beta.txt"]
        for filename in files:
            (tmp_path / filename).touch()

        result = list_all_directory_contents(str(tmp_path))

        alpha_pos = result.find("alpha.txt")
        beta_pos = result.find("beta.txt")
        zebra_pos = result.find("zebra.txt")

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
        restricted_dir = tmp_path / "restricted"
        restricted_dir.mkdir()
        (restricted_dir / "file.txt").touch()

        if os.name != "nt":
            restricted_dir.chmod(0o000)
            try:
                result = list_all_directory_contents(str(tmp_path))
                assert "Error reading directory" in result
            finally:
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
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "file.txt").touch()
        (subdir / "nested.txt").touch()

        result = generate_directory_tree(str(tmp_path), 0, False)

        assert tmp_path.name in result
        assert "file.txt" not in result
        assert "subdir" not in result
        assert "nested.txt" not in result

    def test_generate_with_max_depth_1(self, tmp_path: Path) -> None:
        """Test generating tree with max depth 1."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "file.txt").touch()
        (subdir / "nested.txt").touch()

        result = generate_directory_tree(str(tmp_path), 1, False)

        assert tmp_path.name in result
        assert "file.txt" in result
        assert "subdir" in result
        assert "nested.txt" not in result

    def test_generate_with_max_depth_2(self, tmp_path: Path) -> None:
        """Test generating tree with max depth 2."""
        level1 = tmp_path / "level1"
        level2 = level1 / "level2"
        level3 = level2 / "level3"
        level3.mkdir(parents=True)

        (tmp_path / "root.txt").touch()
        (level1 / "l1.txt").touch()
        (level2 / "l2.txt").touch()
        (level3 / "l3.txt").touch()

        result = generate_directory_tree(str(tmp_path), 2, False)

        assert "root.txt" in result
        assert "level1" in result
        assert "l1.txt" in result
        assert "level2" in result
        assert "l2.txt" not in result
        assert "level3" not in result
        assert "l3.txt" not in result

    def test_generate_include_hidden_true(self, tmp_path: Path) -> None:
        """Test generating tree with hidden files included."""
        (tmp_path / "visible.txt").touch()
        (tmp_path / ".hidden.txt").touch()
        hidden_dir = tmp_path / ".hidden_dir"
        hidden_dir.mkdir()
        (hidden_dir / "inside_hidden.txt").touch()

        result = generate_directory_tree(str(tmp_path), 5, True)

        assert "visible.txt" in result
        assert ".hidden.txt" in result
        assert ".hidden_dir" in result
        assert "inside_hidden.txt" in result

    def test_generate_include_hidden_false(self, tmp_path: Path) -> None:
        """Test generating tree with hidden files excluded."""
        (tmp_path / "visible.txt").touch()
        (tmp_path / ".hidden.txt").touch()
        (tmp_path / ".hidden_dir").mkdir()

        result = generate_directory_tree(str(tmp_path), 5, False)

        assert "visible.txt" in result
        assert ".hidden.txt" not in result
        assert ".hidden_dir" not in result

    def test_generate_large_max_depth(self, tmp_path: Path) -> None:
        """Test generating tree with very large max depth."""
        current = tmp_path
        for i in range(5):
            current = current / f"level{i}"
            current.mkdir()
            (current / f"file{i}.txt").touch()

        result = generate_directory_tree(str(tmp_path), 100, False)

        for i in range(5):
            assert f"level{i}" in result
            assert f"file{i}.txt" in result

    def test_generate_tree_formatting(self, tmp_path: Path) -> None:
        """Test that tree formatting uses correct characters."""
        (tmp_path / "file1.txt").touch()
        (tmp_path / "file2.txt").touch()
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.txt").touch()

        result = generate_directory_tree(str(tmp_path), 5, False)

        assert "└──" in result or "├──" in result
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

        assert tmp_path.name in result

    def test_generate_permission_denied_subdirectory(self, tmp_path: Path) -> None:
        """Test handling permission denied errors gracefully."""
        restricted_dir = tmp_path / "restricted"
        restricted_dir.mkdir()
        (restricted_dir / "file.txt").touch()

        if os.name != "nt":
            restricted_dir.chmod(0o000)
            try:
                result = generate_directory_tree(str(tmp_path), 5, False)
                assert "Error reading directory" in result
            finally:
                restricted_dir.chmod(0o755)

    def test_generate_sorted_contents(self, tmp_path: Path) -> None:
        """Test that generated tree contents are sorted."""
        files = ["zebra.txt", "alpha.txt", "beta.txt"]
        for filename in files:
            (tmp_path / filename).touch()

        result = generate_directory_tree(str(tmp_path), 5, False)

        alpha_pos = result.find("alpha.txt")
        beta_pos = result.find("beta.txt")
        zebra_pos = result.find("zebra.txt")

        assert alpha_pos < beta_pos < zebra_pos

    def test_generate_mixed_files_and_directories(self, tmp_path: Path) -> None:
        """Test tree generation with mixed files and directories."""
        (tmp_path / "file1.txt").touch()
        dir1 = tmp_path / "dir1"
        dir1.mkdir()
        (tmp_path / "file2.txt").touch()
        dir2 = tmp_path / "dir2"
        dir2.mkdir()
        (dir1 / "nested1.txt").touch()
        (dir2 / "nested2.txt").touch()

        result = generate_directory_tree(str(tmp_path), 5, False)

        assert "file1.txt" in result
        assert "file2.txt" in result
        assert "dir1" in result
        assert "dir2" in result
        assert "nested1.txt" in result
        assert "nested2.txt" in result

    def test_generate_negative_max_depth(self, tmp_path: Path) -> None:
        """Test tree generation with negative max depth."""
        (tmp_path / "file.txt").touch()

        result = generate_directory_tree(str(tmp_path), -1, False)

        assert tmp_path.name in result
        assert "file.txt" not in result


class TestTreeIntegration:
    """Integration tests for tree functions."""

    def test_both_functions_same_structure(self, tmp_path: Path) -> None:
        """Test that both functions handle the same structure consistently."""
        (tmp_path / "file.txt").touch()
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.txt").touch()

        list_result = list_all_directory_contents(str(tmp_path))
        tree_result = generate_directory_tree(str(tmp_path), 10, False)

        for filename in ["file.txt", "subdir", "nested.txt"]:
            assert filename in list_result
            assert filename in tree_result

    def test_consistent_error_handling(self, tmp_path: Path) -> None:
        """Test that both functions handle errors consistently."""
        test_file = tmp_path / "test.txt"
        test_file.touch()

        with pytest.raises(FileSystemError):
            list_all_directory_contents(str(test_file))

        with pytest.raises(FileSystemError):
            generate_directory_tree(str(test_file), 5, False)
