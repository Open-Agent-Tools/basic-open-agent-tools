"""Comprehensive file editor tool for AI agents.

This module provides a unified file editing interface similar to strands editor
but designed for cross-platform compatibility and all agent frameworks.
"""

import json
import re
from pathlib import Path
from typing import Union, cast

from ..decorators import strands_tool
from ..exceptions import FileSystemError
from .operations import (
    insert_at_line,
    read_file_to_string,
    replace_in_file,
    write_file_from_string,
)
from .validation import validate_path


@strands_tool
def file_editor(command: str, path: str, skip_confirm: bool, options_json: str) -> str:
    """Comprehensive file editor with multiple operations.

    This tool provides a unified interface for file editing operations including
    viewing, creating, modifying, and searching files. It's designed to be safe
    and informative for AI agents working with code and text files.

    Args:
        command: The operation to perform
        path: Path to the file or directory
        skip_confirm: If True, skip confirmation and bypass safety checks. IMPORTANT: Agents should default to skip_confirm=False for safety.
        options_json: JSON string with command-specific options:
            - view: {"view_range": "1-10"} - line range (optional)
            - create: {"content": "text"} - initial content (optional)
            - str_replace: {"old_str": "x", "new_str": "y"} - required
            - insert: {"line_number": 5, "content": "text"} - required
            - find: {"pattern": "text", "use_regex": false} - pattern required

    Returns:
        String result describing the operation outcome or file contents

    Raises:
        FileSystemError: If file operations fail
        ValueError: If command or parameters are invalid
    """
    # Parse options from JSON
    try:
        options = (
            json.loads(options_json) if options_json and options_json != "{}" else {}
        )
        if not isinstance(options, dict):
            raise ValueError("options_json must be a JSON object")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in options_json: {e}")

    valid_commands = ["view", "create", "str_replace", "insert", "find"]
    if command not in valid_commands:
        raise ValueError(
            f"Invalid command '{command}'. Must be one of: {valid_commands}"
        )

    file_path = validate_path(path, command)

    if command == "view":
        return _view_file(file_path, options.get("view_range"))
    elif command == "create":
        return _create_file(file_path, options.get("content", ""), skip_confirm)
    elif command == "str_replace":
        old_str = options.get("old_str")
        new_str = options.get("new_str")
        if old_str is None or new_str is None:
            raise ValueError("str_replace requires 'old_str' and 'new_str' parameters")
        return _str_replace(file_path, str(old_str), str(new_str))
    elif command == "insert":
        line_number = options.get("line_number")
        content = options.get("content")
        if line_number is None or content is None:
            raise ValueError("insert requires 'line_number' and 'content' parameters")
        return _insert_at_line(file_path, int(line_number), str(content))
    elif command == "find":
        pattern = options.get("pattern")
        if pattern is None:
            raise ValueError("find requires 'pattern' parameter")
        use_regex = bool(options.get("use_regex", False))
        return _find_in_file(file_path, str(pattern), use_regex)

    return f"Unknown command: {command}"


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


def _create_file(file_path: Path, content: Union[str, int], skip_confirm: bool) -> str:
    """Create a new file with optional content."""
    # Convert content to string if needed
    content_str = str(content) if not isinstance(content, str) else content

    try:
        # Pass skip_confirm to write_file_from_string which handles confirmation
        return cast(
            str, write_file_from_string(str(file_path), content_str, skip_confirm)
        )

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
