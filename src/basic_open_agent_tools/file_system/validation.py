"""Path validation utilities for file system operations."""

from pathlib import Path

from ..exceptions import FileSystemError


def validate_path(path: str, operation: str) -> Path:
    """Validate and convert path string to Path object.

    Args:
        path: Path string to validate
        operation: Operation name for error messages

    Returns:
        Validated Path object

    Raises:
        FileSystemError: If path is invalid
    """
    if not path or not isinstance(path, str):
        raise FileSystemError(f"Invalid path for {operation}: {path}")

    try:
        return Path(path).resolve()
    except (OSError, ValueError) as e:
        raise FileSystemError(f"Invalid path for {operation}: {path} - {e}")


def validate_file_content(content: str, operation: str) -> None:
    """Validate file content for write operations.

    Args:
        content: Content to validate
        operation: Operation name for error messages

    Raises:
        FileSystemError: If content is not a string
    """
    if not isinstance(content, str):
        raise FileSystemError(f"Content must be a string for {operation}")
