"""Comprehensive file editor tool for AI agents.

This module provides a unified file editing interface similar to strands editor
but designed for cross-platform compatibility and all agent frameworks.
"""

import re
from pathlib import Path
from typing import Any, Callable, Union

try:
    from strands import tool as strands_tool
except ImportError:
    # Create a no-op decorator if strands is not installed
    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        return func


from ..exceptions import FileSystemError
from .operations import (
    insert_at_line,
    read_file_to_string,
    replace_in_file,
    write_file_from_string,
)
from .validation import validate_path


@strands_tool
def file_editor(
    command: str, path: str, force: bool, **kwargs: Union[str, int, bool]
) -> str:
    """Comprehensive file editor with multiple operations.

    This tool provides a unified interface for file editing operations including
    viewing, creating, modifying, and searching files. It's designed to be safe
    and informative for AI agents working with code and text files.

    Args:
        command: The operation to perform
        path: Path to the file or directory
        force: If True, bypasses confirmations and safety checks (yes-to-all mode)
        **kwargs: Additional parameters based on command:
            - view: view_range (str, optional) - line range like "1-10" or "5"
            - create: content (str, optional) - initial file content
            - str_replace: old_str (str), new_str (str) - text to replace
            - insert: line_number (int), content (str) - where and what to insert
            - find: pattern (str), use_regex (bool, optional) - search pattern

    Returns:
        String result describing the operation outcome or file contents

    Raises:
        FileSystemError: If file operations fail
        ValueError: If command or parameters are invalid
    """
    valid_commands = ["view", "create", "str_replace", "insert", "find"]
    if command not in valid_commands:
        raise ValueError(
            f"Invalid command '{command}'. Must be one of: {valid_commands}"
        )

    file_path = validate_path(path, command)

    if command == "view":
        return _view_file(file_path, kwargs.get("view_range"))
    elif command == "create":
        return _create_file(file_path, kwargs.get("content", ""), force)
    elif command == "str_replace":
        old_str = kwargs.get("old_str")
        new_str = kwargs.get("new_str")
        if old_str is None or new_str is None:
            raise ValueError("str_replace requires 'old_str' and 'new_str' parameters")
        return _str_replace(file_path, str(old_str), str(new_str))
    elif command == "insert":
        line_number = kwargs.get("line_number")
        content = kwargs.get("content")
        if line_number is None or content is None:
            raise ValueError("insert requires 'line_number' and 'content' parameters")
        return _insert_at_line(file_path, int(line_number), str(content))
    elif command == "find":
        pattern = kwargs.get("pattern")
        if pattern is None:
            raise ValueError("find requires 'pattern' parameter")
        use_regex = bool(kwargs.get("use_regex", False))
        return _find_in_file(file_path, str(pattern), use_regex)

    return f"Unknown command: {command}"


def _view_file(file_path: Path, view_range: Union[str, None]) -> str:
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
            start_line, end_line = _parse_line_range(view_range, len(lines))
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
            result += f"Lines {view_range}:\n"
        result += "\n".join(formatted_lines)

        return result

    except (OSError, UnicodeDecodeError) as e:
        raise FileSystemError(f"Failed to read file {file_path}: {e}")


def _create_file(file_path: Path, content: str, force: bool) -> str:
    """Create a new file with optional content."""
    file_existed = file_path.exists()

    if file_existed and not force:
        raise FileSystemError(
            f"File already exists: {file_path}. Use force=True to overwrite."
        )

    try:
        write_file_from_string(str(file_path), content)
        line_count = len(content.splitlines()) if content else 0
        action = "Overwrote" if file_existed else "Created"
        return f"{action} file {file_path} with {line_count} lines"

    except Exception as e:
        raise FileSystemError(f"Failed to create file {file_path}: {e}")


def _str_replace(file_path: Path, old_str: str, new_str: str) -> str:
    """Replace text in file."""
    if not file_path.is_file():
        raise FileSystemError(f"File not found: {file_path}")

    if not old_str:
        raise ValueError("old_str cannot be empty")

    try:
        content = read_file_to_string(str(file_path))

        if old_str not in content:
            return f"No occurrences of '{old_str}' found in {file_path}"

        # Count occurrences before replacement
        occurrence_count = content.count(old_str)

        # Use existing replace_in_file function (-1 means replace all)
        replace_in_file(str(file_path), old_str, new_str, -1)

        return f"Replaced {occurrence_count} occurrence(s) of '{old_str}' with '{new_str}' in {file_path}"

    except Exception as e:
        raise FileSystemError(f"Failed to replace text in file {file_path}: {e}")


def _insert_at_line(file_path: Path, line_number: int, content: str) -> str:
    """Insert content at a specific line number."""
    if not file_path.is_file():
        raise FileSystemError(f"File not found: {file_path}")

    if line_number < 1:
        raise ValueError("line_number must be 1 or greater")

    try:
        # Use existing insert_at_line function
        insert_at_line(str(file_path), line_number, content)

        # Determine position description for user feedback
        lines = read_file_to_string(str(file_path)).splitlines()
        if line_number > len(lines):
            position_desc = f"end (line {len(lines)})"
        else:
            position_desc = f"line {line_number}"

        return f"Inserted content at {position_desc} in {file_path}"

    except Exception as e:
        raise FileSystemError(f"Failed to insert content in file {file_path}: {e}")


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
