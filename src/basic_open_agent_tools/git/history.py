"""Git history and file tracking operations.

This module provides read-only functions to query git commit history,
file history, blame information, and retrieve file contents at specific commits.
"""

import os
import subprocess
from typing import Any

from basic_open_agent_tools.exceptions import GitError


def get_git_log(repository_path: str, max_count: int) -> list[dict[str, Any]]:
    """Get git commit history.

    Retrieves the commit history for a git repository with detailed information
    about each commit including hash, author, date, and message.

    Args:
        repository_path: Absolute path to the git repository
        max_count: Maximum number of commits to retrieve

    Returns:
        List of dictionaries, each containing:
        - commit_hash: Full commit SHA hash
        - author: Author name
        - email: Author email
        - date: Commit date (ISO 8601 format)
        - message: Commit message

    Raises:
        TypeError: If arguments are not correct types
        ValueError: If max_count is less than 1
        FileNotFoundError: If repository path does not exist
        GitError: If path is not a git repository or git command fails

    Example:
        >>> log = get_git_log("/path/to/repo", 5)
        >>> len(log)
        5
        >>> log[0]["author"]
        "John Doe"
        >>> log[0]["message"]
        "Fix bug in module"
    """
    if not isinstance(repository_path, str):
        raise TypeError(
            f"repository_path must be a string, got {type(repository_path)}"
        )
    if not isinstance(max_count, int):
        raise TypeError(f"max_count must be an int, got {type(max_count)}")

    if max_count < 1:
        raise ValueError("max_count must be at least 1")

    if not os.path.exists(repository_path):
        raise FileNotFoundError(f"Repository path not found: {repository_path}")

    if not os.path.isdir(os.path.join(repository_path, ".git")):
        raise GitError(f"Not a git repository: {repository_path}")

    try:
        # Use format string to get structured output
        result = subprocess.run(
            [
                "git",
                "-C",
                repository_path,
                "log",
                f"-{max_count}",
                "--format=%H%n%an%n%ae%n%aI%n%s%n%b%n---END---",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        commits = []
        lines = result.stdout.split("\n")
        i = 0

        while i < len(lines):
            if not lines[i]:
                i += 1
                continue

            commit_hash = lines[i].strip()
            if not commit_hash:
                i += 1
                continue

            # Extract commit information
            author = lines[i + 1].strip() if i + 1 < len(lines) else ""
            email = lines[i + 2].strip() if i + 2 < len(lines) else ""
            date = lines[i + 3].strip() if i + 3 < len(lines) else ""

            # Get message (subject + body until ---END---)
            message_lines = []
            j = i + 4
            while j < len(lines) and lines[j].strip() != "---END---":
                message_lines.append(lines[j])
                j += 1

            message = "\n".join(message_lines).strip()

            commits.append(
                {
                    "commit_hash": commit_hash,
                    "author": author,
                    "email": email,
                    "date": date,
                    "message": message,
                }
            )

            # Move to next commit (after ---END---)
            i = j + 1

        return commits

    except subprocess.CalledProcessError as e:
        raise GitError(f"Git command failed: {e.stderr}")


def get_git_blame(repository_path: str, file_path: str) -> list[dict[str, Any]]:
    """Get line-by-line blame information for a file.

    Retrieves git blame information showing which commit and author last
    modified each line in a file.

    Args:
        repository_path: Absolute path to the git repository
        file_path: Relative path to the file within the repository

    Returns:
        List of dictionaries, each containing:
        - line_number: Line number (1-indexed)
        - commit_hash: Commit hash that last modified this line
        - author: Author who made the change
        - date: Date of the commit
        - content: Line content

    Raises:
        TypeError: If arguments are not strings
        FileNotFoundError: If repository path does not exist
        GitError: If path is not a git repository or git command fails

    Example:
        >>> blame = get_git_blame("/path/to/repo", "src/module.py")
        >>> blame[0]["line_number"]
        1
        >>> blame[0]["author"]
        "Jane Smith"
        >>> blame[0]["content"]
        "def function():"
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
            ["git", "-C", repository_path, "blame", "--line-porcelain", file_path],
            capture_output=True,
            text=True,
            check=True,
        )

        blame_info = []
        lines = result.stdout.split("\n")
        i = 0
        line_number = 1

        while i < len(lines):
            line = lines[i].strip()

            # Each block starts with commit hash and line numbers
            if line and len(line.split()) >= 3:
                parts = line.split()
                commit_hash = parts[0]

                # Extract metadata from following lines
                author = ""
                date = ""
                content = ""

                j = i + 1
                while j < len(lines):
                    if lines[j].startswith("author "):
                        author = lines[j][7:].strip()
                    elif lines[j].startswith("author-time "):
                        # Convert timestamp to ISO format
                        import datetime

                        timestamp = int(lines[j][12:].strip())
                        date = datetime.datetime.fromtimestamp(timestamp).isoformat()
                    elif lines[j].startswith("\t"):
                        # This is the actual line content
                        content = lines[j][1:]  # Remove tab
                        j += 1
                        break
                    j += 1

                blame_info.append(
                    {
                        "line_number": line_number,
                        "commit_hash": commit_hash,
                        "author": author,
                        "date": date,
                        "content": content,
                    }
                )

                line_number += 1
                i = j
            else:
                i += 1

        return blame_info

    except subprocess.CalledProcessError as e:
        raise GitError(f"Git command failed: {e.stderr}")


def get_file_history(repository_path: str, file_path: str) -> list[dict[str, Any]]:
    """Get commit history for a specific file.

    Retrieves all commits that modified a specific file, including commit
    details and the nature of changes.

    Args:
        repository_path: Absolute path to the git repository
        file_path: Relative path to the file within the repository

    Returns:
        List of dictionaries, each containing:
        - commit_hash: Commit hash
        - author: Author name
        - date: Commit date (ISO 8601 format)
        - message: Commit message
        - changes: Summary of changes (insertions, deletions)

    Raises:
        TypeError: If arguments are not strings
        FileNotFoundError: If repository path does not exist
        GitError: If path is not a git repository or git command fails

    Example:
        >>> history = get_file_history("/path/to/repo", "src/module.py")
        >>> len(history)
        12
        >>> history[0]["message"]
        "Refactor module to use new API"
        >>> history[0]["changes"]
        "+15, -8"
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
            [
                "git",
                "-C",
                repository_path,
                "log",
                "--follow",  # Follow file renames
                "--format=%H%n%an%n%aI%n%s",
                "--numstat",
                "--",
                file_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        history = []
        lines = result.stdout.split("\n")
        i = 0

        while i < len(lines):
            if not lines[i]:
                i += 1
                continue

            commit_hash = lines[i].strip()
            if not commit_hash:
                i += 1
                continue

            author = lines[i + 1].strip() if i + 1 < len(lines) else ""
            date = lines[i + 2].strip() if i + 2 < len(lines) else ""
            message = lines[i + 3].strip() if i + 3 < len(lines) else ""

            # Look for numstat line (insertions/deletions)
            changes = ""
            if i + 4 < len(lines) and lines[i + 4].strip():
                stat_parts = lines[i + 4].strip().split("\t")
                if len(stat_parts) >= 2:
                    insertions = stat_parts[0]
                    deletions = stat_parts[1]
                    changes = f"+{insertions}, -{deletions}"

            history.append(
                {
                    "commit_hash": commit_hash,
                    "author": author,
                    "date": date,
                    "message": message,
                    "changes": changes,
                }
            )

            i += 5  # Move to next commit

        return history

    except subprocess.CalledProcessError as e:
        raise GitError(f"Git command failed: {e.stderr}")


def get_file_at_commit(repository_path: str, file_path: str, commit_hash: str) -> str:
    """Get file contents at a specific commit.

    Retrieves the contents of a file as it existed at a specific commit
    in the repository history.

    Args:
        repository_path: Absolute path to the git repository
        file_path: Relative path to the file within the repository
        commit_hash: Commit hash to retrieve file from

    Returns:
        File contents as a string

    Raises:
        TypeError: If arguments are not strings
        FileNotFoundError: If repository path does not exist
        GitError: If path is not a git repository, commit not found, or git command fails

    Example:
        >>> content = get_file_at_commit("/path/to/repo", "src/module.py", "abc123")
        >>> "def old_function" in content
        True
    """
    if not isinstance(repository_path, str):
        raise TypeError(
            f"repository_path must be a string, got {type(repository_path)}"
        )
    if not isinstance(file_path, str):
        raise TypeError(f"file_path must be a string, got {type(file_path)}")
    if not isinstance(commit_hash, str):
        raise TypeError(f"commit_hash must be a string, got {type(commit_hash)}")

    if not os.path.exists(repository_path):
        raise FileNotFoundError(f"Repository path not found: {repository_path}")

    if not os.path.isdir(os.path.join(repository_path, ".git")):
        raise GitError(f"Not a git repository: {repository_path}")

    try:
        result = subprocess.run(
            ["git", "-C", repository_path, "show", f"{commit_hash}:{file_path}"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout

    except subprocess.CalledProcessError as e:
        raise GitError(f"Git command failed: {e.stderr}")
