"""File editor tools for AI agents.

This module provides simple, flat file editing tools that are easy for agents to use.
No complex multi-command interfaces or JSON parsing required.

Recommended tools:
- view_file_with_lines: View files with line numbers
- find_text_in_file: Search for text in files
- write_file_from_string: Create/write files (from operations module)
- replace_in_file: Replace text (from operations module)
- insert_at_line: Insert at specific line (from operations module)
"""

import re
from pathlib import Path
from typing import Union

from ..decorators import strands_tool
from ..exceptions import FileSystemError
from .operations import read_file_to_string
from .validation import validate_path


def _view_file(file_path: Path, view_range: Union[str, int, None]) -> str:
    """View file contents with optional line range."""
    if not file_path.exists():
        raise FileSystemError(f"File not found: {file_path}")

    if file_path.is_dir():
        # List directory contents
        try:
            contents = []
            for item in sorted(file_path.iterdir()):
                item_type = "DIR" if item.is_dir() else "FILE"
                contents.append(f"{item_type}: {item.name}")
            return f"Directory contents of {file_path}:\n" + "\n".join(contents)
        except OSError as e:
            raise FileSystemError(f"Failed to list directory {file_path}: {e}")

    try:
        content = read_file_to_string(str(file_path))
        lines = content.splitlines()

        if view_range:
            # Convert view_range to string if it's an int
            view_range_str = (
                str(view_range) if not isinstance(view_range, str) else view_range
            )
            start_line, end_line = _parse_line_range(view_range_str, len(lines))
            lines = lines[start_line - 1 : end_line]
            line_numbers = range(start_line, start_line + len(lines))
        else:
            line_numbers = range(1, len(lines) + 1)

        # Format with line numbers
        formatted_lines = []
        for line_num, line in zip(line_numbers, lines):
            formatted_lines.append(f"{line_num:4d}: {line}")

        result = f"File: {file_path}\n"
        if view_range:
            result += f"Lines {view_range_str}:\n"
        result += "\n".join(formatted_lines)

        return result

    except (OSError, UnicodeDecodeError) as e:
        raise FileSystemError(f"Failed to read file {file_path}: {e}")


def _find_in_file(file_path: Path, pattern: str, use_regex: bool) -> str:
    """Find text pattern in file."""
    if not file_path.is_file():
        raise FileSystemError(f"File not found: {file_path}")

    try:
        content = read_file_to_string(str(file_path))
        lines = content.splitlines()

        matches = []

        if use_regex:
            try:
                regex_pattern = re.compile(pattern)
                for line_num, line in enumerate(lines, 1):
                    if regex_pattern.search(line):
                        matches.append(f"{line_num:4d}: {line}")
            except re.error as e:
                raise ValueError(f"Invalid regex pattern '{pattern}': {e}")
        else:
            # Simple substring search
            for line_num, line in enumerate(lines, 1):
                if pattern in line:
                    matches.append(f"{line_num:4d}: {line}")

        if not matches:
            search_type = "regex" if use_regex else "text"
            return (
                f"No matches found for {search_type} pattern '{pattern}' in {file_path}"
            )

        result = f"Found {len(matches)} match(es) for '{pattern}' in {file_path}:\n"
        result += "\n".join(matches)

        return result

    except (OSError, UnicodeDecodeError) as e:
        raise FileSystemError(f"Failed to search file {file_path}: {e}")


def _parse_line_range(range_str: str, total_lines: int) -> tuple[int, int]:
    """Parse line range string into start and end line numbers."""
    range_str = range_str.strip()

    if "-" in range_str:
        # Range like "5-10"
        try:
            start_str, end_str = range_str.split("-", 1)
            start_line = int(start_str.strip())
            end_line = int(end_str.strip())
        except ValueError:
            raise ValueError(f"Invalid line range format: {range_str}")
    else:
        # Single line like "5"
        try:
            start_line = end_line = int(range_str)
        except ValueError:
            raise ValueError(f"Invalid line number: {range_str}")

    # Validate and clamp ranges
    start_line = max(1, start_line)
    end_line = min(total_lines, end_line)

    if start_line > end_line:
        raise ValueError(f"Start line {start_line} is greater than end line {end_line}")

    return start_line, end_line


# ============================================================================
# FLAT TOOLS - Simple file editor operations for agents
# ============================================================================
#
# These tools provide unique value beyond existing operations:
# - view_file_with_lines: Adds line numbers to file viewing
# - find_text_in_file: Search/grep functionality
#
# For other operations, use existing tools:
# - write_file_from_string: Create/write files
# - replace_in_file: Replace text with count control
# - insert_at_line: Insert at specific line
# ============================================================================


@strands_tool
def view_file_with_lines(path: str, start_line: str, end_line: str) -> str:
    """View file contents with line numbers and optional line range.

    Displays file contents with line numbers for easy reference.

    UNIQUE VALUE: Adds line numbers to file viewing, unlike read_file_to_string
    which returns raw content.

    Args:
        path: Path to the file to view (absolute or relative)
        start_line: Starting line number (empty string for beginning of file)
        end_line: Ending line number (empty string for end of file)

    Returns:
        File contents with line numbers, or directory listing if path is a directory

    Raises:
        FileSystemError: If file not found or cannot be read

    Example:
        >>> # View entire file
        >>> content = view_file_with_lines("/path/to/file.py", "", "")

        >>> # View lines 10-20
        >>> content = view_file_with_lines("/path/to/file.py", "10", "20")

        >>> # View single line 15
        >>> content = view_file_with_lines("/path/to/file.py", "15", "15")
    """
    file_path = validate_path(path, "view")

    # Construct view_range parameter for _view_file
    if start_line and end_line:
        view_range: Union[str, None] = f"{start_line}-{end_line}"
    elif start_line:
        view_range = start_line
    else:
        view_range = None

    return _view_file(file_path, view_range)


@strands_tool
def find_text_in_file(path: str, search_text: str, use_regex: bool) -> str:
    """Search for text or regex pattern in a file.

    Searches the file for the specified text or regex pattern and returns
    all matching lines with line numbers.

    Args:
        path: Path to the file to search (absolute or relative)
        search_text: Text to search for, or regex pattern if use_regex=True
        use_regex: Whether to treat search_text as a regex pattern
            - False: Simple substring search
            - True: Regular expression search

    Returns:
        Matching lines with line numbers, or message if no matches found

    Raises:
        FileSystemError: If file not found or cannot be read
        ValueError: If use_regex=True and regex pattern is invalid

    Example:
        >>> # Simple text search
        >>> result = find_text_in_file("file.py", "TODO", False)
        'Found 3 match(es) for 'TODO' in file.py:
          5: # TODO: Fix this
         23: # TODO: Implement feature
         47: # TODO: Add tests'

        >>> # Regex search for function definitions
        >>> result = find_text_in_file("file.py", "def \\\\w+\\\\(", True)
    """
    file_path = validate_path(path, "find")
    return _find_in_file(file_path, search_text, use_regex)
