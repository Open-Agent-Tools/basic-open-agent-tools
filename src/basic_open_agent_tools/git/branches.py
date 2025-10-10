"""Git branch information and analysis.

This module provides read-only functions to query git branch information
including listing branches and getting detailed branch metadata.
"""

import os
import subprocess
from typing import Any

from basic_open_agent_tools.exceptions import GitError


def list_branches(repository_path: str) -> list[str]:
    """List all branches in a git repository.

    Retrieves a list of all branch names in the repository, including both
    local and remote branches.

    Args:
        repository_path: Absolute path to the git repository

    Returns:
        List of branch names as strings

    Raises:
        TypeError: If repository_path is not a string
        FileNotFoundError: If repository path does not exist
        GitError: If path is not a git repository or git command fails

    Example:
        >>> branches = list_branches("/path/to/repo")
        >>> branches
        ["main", "develop", "feature/new-api", "origin/main"]
        >>> "main" in branches
        True
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
        # Get local and remote branches
        result = subprocess.run(
            ["git", "-C", repository_path, "branch", "-a", "--format=%(refname:short)"],
            capture_output=True,
            text=True,
            check=True,
        )

        branches = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return branches

    except subprocess.CalledProcessError as e:
        raise GitError(f"Git command failed: {e.stderr}")


def get_branch_info(repository_path: str, branch_name: str) -> dict[str, Any]:
    """Get detailed information about a specific branch.

    Retrieves detailed metadata about a branch including its last commit,
    author, date, and upstream tracking information.

    Args:
        repository_path: Absolute path to the git repository
        branch_name: Name of the branch to query

    Returns:
        Dictionary containing:
        - branch_name: Name of the branch
        - last_commit: Last commit hash
        - last_commit_message: Message of last commit
        - author: Author of last commit
        - date: Date of last commit (ISO 8601 format)
        - ahead: Number of commits ahead of upstream (or None)
        - behind: Number of commits behind upstream (or None)

    Raises:
        TypeError: If arguments are not strings
        FileNotFoundError: If repository path does not exist
        GitError: If path is not a git repository, branch not found, or git command fails

    Example:
        >>> info = get_branch_info("/path/to/repo", "main")
        >>> info["branch_name"]
        "main"
        >>> info["last_commit_message"]
        "Fix bug in parser"
        >>> info["ahead"]
        2
    """
    if not isinstance(repository_path, str):
        raise TypeError(
            f"repository_path must be a string, got {type(repository_path)}"
        )
    if not isinstance(branch_name, str):
        raise TypeError(f"branch_name must be a string, got {type(branch_name)}")

    if not os.path.exists(repository_path):
        raise FileNotFoundError(f"Repository path not found: {repository_path}")

    if not os.path.isdir(os.path.join(repository_path, ".git")):
        raise GitError(f"Not a git repository: {repository_path}")

    try:
        # Get last commit information
        log_result = subprocess.run(
            [
                "git",
                "-C",
                repository_path,
                "log",
                branch_name,
                "-1",
                "--format=%H%n%an%n%aI%n%s",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        lines = log_result.stdout.strip().split("\n")
        if len(lines) < 4:
            raise GitError(f"Branch not found: {branch_name}")

        last_commit = lines[0].strip()
        author = lines[1].strip()
        date = lines[2].strip()
        message = lines[3].strip()

        # Try to get ahead/behind counts for upstream
        ahead = None
        behind = None

        try:
            upstream_result = subprocess.run(
                [
                    "git",
                    "-C",
                    repository_path,
                    "rev-list",
                    "--left-right",
                    "--count",
                    f"{branch_name}...@{{u}}",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            counts = upstream_result.stdout.strip().split()
            if len(counts) == 2:
                ahead = int(counts[0])
                behind = int(counts[1])
        except subprocess.CalledProcessError:
            # No upstream tracking, leave as None
            pass

        return {
            "branch_name": branch_name,
            "last_commit": last_commit,
            "last_commit_message": message,
            "author": author,
            "date": date,
            "ahead": ahead,
            "behind": behind,
        }

    except subprocess.CalledProcessError as e:
        raise GitError(f"Git command failed: {e.stderr}")
