"""Git status and diff operations.

This module provides read-only functions to query git repository status,
current branch, and file differences.
"""

import os
import subprocess
from typing import Any

from basic_open_agent_tools.exceptions import GitError


def get_git_status(repository_path: str) -> dict[str, Any]:
    """Get current git repository status.

    Retrieves the current status of a git repository including the current branch,
    staged files, unstaged files, and untracked files.

    Args:
        repository_path: Absolute path to the git repository

    Returns:
        Dictionary containing:
        - branch: Current branch name
        - staged: List of staged file paths
        - unstaged: List of unstaged modified file paths
        - untracked: List of untracked file paths
        - clean: Boolean indicating if working directory is clean

    Raises:
        TypeError: If repository_path is not a string
        FileNotFoundError: If repository path does not exist
        GitError: If path is not a git repository or git command fails

    Example:
        >>> status = get_git_status("/path/to/repo")
        >>> status["branch"]
        "main"
        >>> status["staged"]
        ["src/module.py", "tests/test_module.py"]
        >>> status["clean"]
        False
    """
    if not isinstance(repository_path, str):
        raise TypeError(
            f"repository_path must be a string, got {type(repository_path)}"
        )

    if not os.path.exists(repository_path):
        raise FileNotFoundError(f"Repository path not found: {repository_path}")

    if not os.path.isdir(os.path.join(repository_path, ".git")):
        raise GitError(f"Not a git repository: {repository_path}")

    try:
        # Get current branch
        branch_result = subprocess.run(
            ["git", "-C", repository_path, "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
        )
        branch = branch_result.stdout.strip()

        # Get status with porcelain format
        status_result = subprocess.run(
            ["git", "-C", repository_path, "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Parse status output
        staged = []
        unstaged = []
        untracked = []

        for line in status_result.stdout.splitlines():
            if not line:
                continue

            # Porcelain format: XY filename
            # X = staged status, Y = unstaged status
            status_code = line[:2]
            filename = line[3:]

            # Check staged status (first character)
            if status_code[0] != " " and status_code[0] != "?":
                staged.append(filename)

            # Check unstaged status (second character)
            if status_code[1] != " " and status_code[1] != "?":
                unstaged.append(filename)

            # Check untracked
            if status_code == "??":
                untracked.append(filename)

        clean = len(staged) == 0 and len(unstaged) == 0 and len(untracked) == 0

        return {
            "branch": branch,
            "staged": staged,
            "unstaged": unstaged,
            "untracked": untracked,
            "clean": clean,
        }

    except subprocess.CalledProcessError as e:
        raise GitError(f"Git command failed: {e.stderr}")


def get_current_branch(repository_path: str) -> str:
    """Get current git branch name.

    Retrieves the name of the currently checked out branch.

    Args:
        repository_path: Absolute path to the git repository

    Returns:
        Current branch name as a string

    Raises:
        TypeError: If repository_path is not a string
        FileNotFoundError: If repository path does not exist
        GitError: If path is not a git repository or git command fails

    Example:
        >>> branch = get_current_branch("/path/to/repo")
        >>> branch
        "main"
    """
    if not isinstance(repository_path, str):
        raise TypeError(
            f"repository_path must be a string, got {type(repository_path)}"
        )

    if not os.path.exists(repository_path):
        raise FileNotFoundError(f"Repository path not found: {repository_path}")

    if not os.path.isdir(os.path.join(repository_path, ".git")):
        raise GitError(f"Not a git repository: {repository_path}")

    try:
        result = subprocess.run(
            ["git", "-C", repository_path, "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        raise GitError(f"Git command failed: {e.stderr}")


def get_git_diff(repository_path: str, file_path: str) -> str:
    """Get git diff for a specific file.

    Retrieves the unified diff output showing changes to a file in the
    working directory compared to the last commit.

    Args:
        repository_path: Absolute path to the git repository
        file_path: Relative path to the file within the repository

    Returns:
        Unified diff output as a string

    Raises:
        TypeError: If arguments are not strings
        FileNotFoundError: If repository path does not exist
        GitError: If path is not a git repository or git command fails

    Example:
        >>> diff = get_git_diff("/path/to/repo", "src/module.py")
        >>> "def function" in diff
        True
        >>> "+new line" in diff
        True
    """
    if not isinstance(repository_path, str):
        raise TypeError(
            f"repository_path must be a string, got {type(repository_path)}"
        )
    if not isinstance(file_path, str):
        raise TypeError(f"file_path must be a string, got {type(file_path)}")

    if not os.path.exists(repository_path):
        raise FileNotFoundError(f"Repository path not found: {repository_path}")

    if not os.path.isdir(os.path.join(repository_path, ".git")):
        raise GitError(f"Not a git repository: {repository_path}")

    try:
        result = subprocess.run(
            ["git", "-C", repository_path, "diff", "HEAD", "--", file_path],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout

    except subprocess.CalledProcessError as e:
        raise GitError(f"Git command failed: {e.stderr}")
