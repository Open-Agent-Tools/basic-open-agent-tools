"""Tests for git repository information and analysis tools.

These tests use the actual repository to test real git operations.
"""

import os
import tempfile

import pytest

from basic_open_agent_tools.exceptions import GitError
from basic_open_agent_tools.git import (
    get_branch_info,
    get_current_branch,
    get_file_at_commit,
    get_file_history,
    get_git_blame,
    get_git_diff,
    get_git_log,
    get_git_status,
    list_branches,
)

# Use the actual repository for testing
REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


class TestGetGitStatus:
    """Tests for get_git_status function."""

    def test_get_git_status_basic(self):
        """Test getting git status from actual repository."""
        status = get_git_status(REPO_PATH)

        assert "branch" in status
        assert "staged" in status
        assert "unstaged" in status
        assert "untracked" in status
        assert "clean" in status
        assert isinstance(status["branch"], str)
        assert isinstance(status["staged"], list)
        assert isinstance(status["unstaged"], list)
        assert isinstance(status["untracked"], list)
        assert isinstance(status["clean"], bool)

    def test_get_git_status_invalid_type(self):
        """Test that non-string input raises TypeError."""
        with pytest.raises(TypeError, match="repository_path must be a string"):
            get_git_status(123)  # type: ignore[arg-type]

    def test_get_git_status_nonexistent_path(self):
        """Test that nonexistent path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            get_git_status("/nonexistent/path")

    def test_get_git_status_not_a_repo(self):
        """Test that non-git directory raises GitError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(GitError, match="Not a git repository"):
                get_git_status(tmpdir)


class TestGetCurrentBranch:
    """Tests for get_current_branch function."""

    def test_get_current_branch_basic(self):
        """Test getting current branch."""
        branch = get_current_branch(REPO_PATH)

        assert isinstance(branch, str)
        assert len(branch) > 0

    def test_get_current_branch_invalid_type(self):
        """Test that non-string input raises TypeError."""
        with pytest.raises(TypeError, match="repository_path must be a string"):
            get_current_branch([])  # type: ignore[arg-type]

    def test_get_current_branch_nonexistent_path(self):
        """Test that nonexistent path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            get_current_branch("/nonexistent/path")

    def test_get_current_branch_not_a_repo(self):
        """Test that non-git directory raises GitError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(GitError, match="Not a git repository"):
                get_current_branch(tmpdir)


class TestGetGitDiff:
    """Tests for get_git_diff function."""

    def test_get_git_diff_basic(self):
        """Test getting diff for a file."""
        # Test with a real file from the repo
        diff = get_git_diff(REPO_PATH, "README.md")

        # Diff should be a string (may be empty if no changes)
        assert isinstance(diff, str)

    def test_get_git_diff_invalid_types(self):
        """Test that non-string inputs raise TypeError."""
        with pytest.raises(TypeError, match="repository_path must be a string"):
            get_git_diff(123, "file.py")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="file_path must be a string"):
            get_git_diff(REPO_PATH, 456)  # type: ignore[arg-type]

    def test_get_git_diff_nonexistent_repo(self):
        """Test that nonexistent path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            get_git_diff("/nonexistent/path", "file.py")

    def test_get_git_diff_not_a_repo(self):
        """Test that non-git directory raises GitError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(GitError, match="Not a git repository"):
                get_git_diff(tmpdir, "file.py")


class TestGetGitLog:
    """Tests for get_git_log function."""

    def test_get_git_log_basic(self):
        """Test getting git log."""
        log = get_git_log(REPO_PATH, 5)

        assert isinstance(log, list)
        assert len(log) <= 5

        if log:
            commit = log[0]
            assert "commit_hash" in commit
            assert "author" in commit
            assert "email" in commit
            assert "date" in commit
            assert "message" in commit
            assert isinstance(commit["commit_hash"], str)
            assert len(commit["commit_hash"]) == 40  # Full SHA hash

    def test_get_git_log_single_commit(self):
        """Test getting single commit."""
        log = get_git_log(REPO_PATH, 1)

        assert len(log) == 1

    def test_get_git_log_invalid_types(self):
        """Test that invalid types raise TypeError."""
        with pytest.raises(TypeError, match="repository_path must be a string"):
            get_git_log(123, 5)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="max_count must be an int"):
            get_git_log(REPO_PATH, "5")  # type: ignore[arg-type]

    def test_get_git_log_invalid_count(self):
        """Test that count < 1 raises ValueError."""
        with pytest.raises(ValueError, match="max_count must be at least 1"):
            get_git_log(REPO_PATH, 0)

    def test_get_git_log_nonexistent_repo(self):
        """Test that nonexistent path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            get_git_log("/nonexistent/path", 5)

    def test_get_git_log_not_a_repo(self):
        """Test that non-git directory raises GitError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(GitError, match="Not a git repository"):
                get_git_log(tmpdir, 5)


class TestGetGitBlame:
    """Tests for get_git_blame function."""

    def test_get_git_blame_basic(self):
        """Test getting git blame."""
        # Use README.md which should exist
        blame = get_git_blame(REPO_PATH, "README.md")

        assert isinstance(blame, list)
        if blame:
            line = blame[0]
            assert "line_number" in line
            assert "commit_hash" in line
            assert "author" in line
            assert "date" in line
            assert "content" in line
            assert line["line_number"] == 1

    def test_get_git_blame_invalid_types(self):
        """Test that invalid types raise TypeError."""
        with pytest.raises(TypeError, match="repository_path must be a string"):
            get_git_blame(123, "file.py")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="file_path must be a string"):
            get_git_blame(REPO_PATH, 456)  # type: ignore[arg-type]

    def test_get_git_blame_nonexistent_repo(self):
        """Test that nonexistent path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            get_git_blame("/nonexistent/path", "file.py")

    def test_get_git_blame_not_a_repo(self):
        """Test that non-git directory raises GitError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(GitError, match="Not a git repository"):
                get_git_blame(tmpdir, "file.py")


class TestGetFileHistory:
    """Tests for get_file_history function."""

    def test_get_file_history_basic(self):
        """Test getting file history."""
        # Use README.md which should have history
        history = get_file_history(REPO_PATH, "README.md")

        assert isinstance(history, list)
        if history:
            commit = history[0]
            assert "commit_hash" in commit
            assert "author" in commit
            assert "date" in commit
            assert "message" in commit
            assert "changes" in commit

    def test_get_file_history_invalid_types(self):
        """Test that invalid types raise TypeError."""
        with pytest.raises(TypeError, match="repository_path must be a string"):
            get_file_history(123, "file.py")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="file_path must be a string"):
            get_file_history(REPO_PATH, 456)  # type: ignore[arg-type]

    def test_get_file_history_nonexistent_repo(self):
        """Test that nonexistent path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            get_file_history("/nonexistent/path", "file.py")

    def test_get_file_history_not_a_repo(self):
        """Test that non-git directory raises GitError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(GitError, match="Not a git repository"):
                get_file_history(tmpdir, "file.py")


class TestGetFileAtCommit:
    """Tests for get_file_at_commit function."""

    def test_get_file_at_commit_basic(self):
        """Test getting file at specific commit."""
        # Get current commit hash
        log = get_git_log(REPO_PATH, 1)
        if log:
            commit_hash = log[0]["commit_hash"]

            # Get README.md at that commit
            content = get_file_at_commit(REPO_PATH, "README.md", commit_hash)

            assert isinstance(content, str)
            assert len(content) > 0

    def test_get_file_at_commit_invalid_types(self):
        """Test that invalid types raise TypeError."""
        with pytest.raises(TypeError, match="repository_path must be a string"):
            get_file_at_commit(123, "file.py", "abc123")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="file_path must be a string"):
            get_file_at_commit(REPO_PATH, 456, "abc123")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="commit_hash must be a string"):
            get_file_at_commit(REPO_PATH, "file.py", 789)  # type: ignore[arg-type]

    def test_get_file_at_commit_nonexistent_repo(self):
        """Test that nonexistent path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            get_file_at_commit("/nonexistent/path", "file.py", "abc123")

    def test_get_file_at_commit_not_a_repo(self):
        """Test that non-git directory raises GitError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(GitError, match="Not a git repository"):
                get_file_at_commit(tmpdir, "file.py", "abc123")


class TestListBranches:
    """Tests for list_branches function."""

    def test_list_branches_basic(self):
        """Test listing branches."""
        branches = list_branches(REPO_PATH)

        assert isinstance(branches, list)
        assert len(branches) > 0

        # Should at least have the current branch
        current = get_current_branch(REPO_PATH)
        assert current in branches

    def test_list_branches_invalid_type(self):
        """Test that non-string input raises TypeError."""
        with pytest.raises(TypeError, match="repository_path must be a string"):
            list_branches(123)  # type: ignore[arg-type]

    def test_list_branches_nonexistent_repo(self):
        """Test that nonexistent path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            list_branches("/nonexistent/path")

    def test_list_branches_not_a_repo(self):
        """Test that non-git directory raises GitError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(GitError, match="Not a git repository"):
                list_branches(tmpdir)


class TestGetBranchInfo:
    """Tests for get_branch_info function."""

    def test_get_branch_info_basic(self):
        """Test getting branch information."""
        # Get current branch
        current = get_current_branch(REPO_PATH)

        info = get_branch_info(REPO_PATH, current)

        assert info["branch_name"] == current
        assert "last_commit" in info
        assert "last_commit_message" in info
        assert "author" in info
        assert "date" in info
        assert isinstance(info["last_commit"], str)
        assert len(info["last_commit"]) == 40  # Full SHA hash

    def test_get_branch_info_ahead_behind(self):
        """Test that ahead/behind counts are included."""
        current = get_current_branch(REPO_PATH)
        info = get_branch_info(REPO_PATH, current)

        # ahead and behind may be None or int
        assert "ahead" in info
        assert "behind" in info
        assert info["ahead"] is None or isinstance(info["ahead"], int)
        assert info["behind"] is None or isinstance(info["behind"], int)

    def test_get_branch_info_invalid_types(self):
        """Test that invalid types raise TypeError."""
        with pytest.raises(TypeError, match="repository_path must be a string"):
            get_branch_info(123, "main")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="branch_name must be a string"):
            get_branch_info(REPO_PATH, 456)  # type: ignore[arg-type]

    def test_get_branch_info_nonexistent_repo(self):
        """Test that nonexistent path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            get_branch_info("/nonexistent/path", "main")

    def test_get_branch_info_not_a_repo(self):
        """Test that non-git directory raises GitError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(GitError, match="Not a git repository"):
                get_branch_info(tmpdir, "main")

    def test_get_branch_info_nonexistent_branch(self):
        """Test that nonexistent branch raises GitError."""
        with pytest.raises(GitError):
            get_branch_info(REPO_PATH, "nonexistent-branch-xyz")
