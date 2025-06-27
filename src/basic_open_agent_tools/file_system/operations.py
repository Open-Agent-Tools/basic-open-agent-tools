"""Core file and directory operations."""

import shutil
from typing import List

from ..exceptions import FileSystemError
from .validation import validate_file_content, validate_path


def read_file_to_string(file_path: str) -> str:
    """Load string from a text file.

    Args:
        file_path: Path to the text file

    Returns:
        The file content as a string with leading/trailing whitespace stripped

    Raises:
        FileSystemError: If file doesn't exist or can't be read
    """
    path = validate_path(file_path, "read")

    if not path.is_file():
        raise FileSystemError(f"File not found: {path}")

    try:
        return path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError) as e:
        raise FileSystemError(f"Failed to read file {path}: {e}")


def write_file_from_string(file_path: str, content: str) -> bool:
    """Write string content to a text file.

    Args:
        file_path: Path to the output file
        content: String content to write

    Returns:
        True if successful

    Raises:
        FileSystemError: If write operation fails
    """
    validate_file_content(content, "write")
    path = validate_path(file_path, "write")

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return True
    except OSError as e:
        raise FileSystemError(f"Failed to write file {path}: {e}")


def append_to_file(file_path: str, content: str) -> bool:
    """Append string content to a text file.

    Args:
        file_path: Path to the file
        content: String content to append

    Returns:
        True if successful

    Raises:
        FileSystemError: If append operation fails
    """
    validate_file_content(content, "append")
    path = validate_path(file_path, "append")

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as file:
            file.write(content)
        return True
    except OSError as e:
        raise FileSystemError(f"Failed to append to file {path}: {e}")


def list_directory_contents(
    directory_path: str, include_hidden: bool = False
) -> List[str]:
    """List contents of a directory.

    Args:
        directory_path: Path to the directory
        include_hidden: Whether to include hidden files/directories

    Returns:
        Sorted list of file and directory names

    Raises:
        FileSystemError: If directory doesn't exist or can't be read
    """
    path = validate_path(directory_path, "list directory")

    if not path.is_dir():
        raise FileSystemError(f"Directory not found: {path}")

    try:
        contents = [item.name for item in path.iterdir()]
        if not include_hidden:
            contents = [name for name in contents if not name.startswith(".")]
        return sorted(contents)
    except OSError as e:
        raise FileSystemError(f"Failed to list directory {path}: {e}")


def create_directory(directory_path: str) -> bool:
    """Create a directory and any necessary parent directories.

    Args:
        directory_path: Path to the directory to create

    Returns:
        True if successful

    Raises:
        FileSystemError: If directory creation fails
    """
    path = validate_path(directory_path, "create directory")

    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except OSError as e:
        raise FileSystemError(f"Failed to create directory {path}: {e}")


def delete_file(file_path: str) -> bool:
    """Delete a file.

    Args:
        file_path: Path to the file to delete

    Returns:
        True if successful (including if file doesn't exist)

    Raises:
        FileSystemError: If deletion fails
    """
    path = validate_path(file_path, "delete file")

    try:
        path.unlink(missing_ok=True)
        return True
    except OSError as e:
        raise FileSystemError(f"Failed to delete file {path}: {e}")


def delete_directory(directory_path: str, recursive: bool) -> bool:
    """Delete a directory.

    Args:
        directory_path: Path to the directory to delete
        recursive: If True, delete directory and all contents recursively

    Returns:
        True if successful (including if directory doesn't exist)

    Raises:
        FileSystemError: If deletion fails
    """
    path = validate_path(directory_path, "delete directory")

    if not path.exists():
        return True

    try:
        if recursive:
            shutil.rmtree(path)
        else:
            path.rmdir()  # Only works if directory is empty
        return True
    except OSError as e:
        raise FileSystemError(f"Failed to delete directory {path}: {e}")


def move_file(source_path: str, destination_path: str) -> bool:
    """Move or rename a file or directory.

    Args:
        source_path: Current path of the file/directory
        destination_path: New path for the file/directory

    Returns:
        True if successful

    Raises:
        FileSystemError: If move operation fails
    """
    src_path = validate_path(source_path, "move source")
    dst_path = validate_path(destination_path, "move destination")

    if not src_path.exists():
        raise FileSystemError(f"Source path not found: {src_path}")

    try:
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_path), str(dst_path))
        return True
    except OSError as e:
        raise FileSystemError(f"Failed to move {src_path} to {dst_path}: {e}")


def copy_file(source_path: str, destination_path: str) -> bool:
    """Copy a file or directory.

    Args:
        source_path: Path of the source file/directory
        destination_path: Path for the copied file/directory

    Returns:
        True if successful

    Raises:
        FileSystemError: If copy operation fails
    """
    src_path = validate_path(source_path, "copy source")
    dst_path = validate_path(destination_path, "copy destination")

    if not src_path.exists():
        raise FileSystemError(f"Source path not found: {src_path}")

    try:
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        if src_path.is_file():
            shutil.copy2(str(src_path), str(dst_path))
        else:
            shutil.copytree(str(src_path), str(dst_path))
        return True
    except OSError as e:
        raise FileSystemError(f"Failed to copy {src_path} to {dst_path}: {e}")


def replace_in_file(
    file_path: str, old_text: str, new_text: str, count: int = -1
) -> bool:
    """Replace occurrences of text within a file without rewriting the entire content.

    This function performs targeted text replacement, making it safer for agents
    to make small changes without accidentally removing other content.

    Args:
        file_path: Path to the file to modify
        old_text: Text to search for and replace
        new_text: Text to replace the old text with
        count: Maximum number of replacements to make (-1 for all occurrences)

    Returns:
        True if successful (even if no replacements were made)

    Raises:
        FileSystemError: If file doesn't exist, can't be read, or write fails
        ValueError: If old_text is empty
    """
    if not old_text:
        raise ValueError("old_text cannot be empty")

    validate_file_content(new_text, "replace")
    path = validate_path(file_path, "replace")

    if not path.is_file():
        raise FileSystemError(f"File not found: {path}")

    try:
        # Read current content
        content = path.read_text(encoding="utf-8")

        # Perform replacement
        updated_content = content.replace(old_text, new_text, count)

        # Write back to file
        path.write_text(updated_content, encoding="utf-8")
        return True
    except (OSError, UnicodeDecodeError) as e:
        raise FileSystemError(f"Failed to replace text in file {path}: {e}")


def insert_at_line(file_path: str, line_number: int, content: str) -> bool:
    """Insert content at a specific line number in a file.

    This function allows precise insertion of text at a specific line,
    making it safer for agents to add content without overwriting files.

    Args:
        file_path: Path to the file to modify
        line_number: Line number to insert at (1-based indexing)
        content: Content to insert (will be added as a new line)

    Returns:
        True if successful

    Raises:
        FileSystemError: If file doesn't exist, can't be read, or write fails
        ValueError: If line_number is less than 1
    """
    if line_number < 1:
        raise ValueError("line_number must be 1 or greater")

    validate_file_content(content, "insert")
    path = validate_path(file_path, "insert")

    if not path.is_file():
        raise FileSystemError(f"File not found: {path}")

    try:
        # Read current lines
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

        # Ensure content ends with newline if it doesn't already
        if content and not content.endswith("\n"):
            content += "\n"

        # Insert at specified line (convert to 0-based index)
        insert_index = line_number - 1

        # If line number is beyond file length, append to end
        if insert_index >= len(lines):
            lines.append(content)
        else:
            lines.insert(insert_index, content)

        # Write back to file
        path.write_text("".join(lines), encoding="utf-8")
        return True
    except (OSError, UnicodeDecodeError) as e:
        raise FileSystemError(f"Failed to insert content in file {path}: {e}")
