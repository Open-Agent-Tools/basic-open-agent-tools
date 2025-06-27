"""File and directory information utilities."""

from ..exceptions import FileSystemError
from .validation import validate_path


def get_file_info(file_path: str) -> dict:
    """Get file or directory information.

    Args:
        file_path: Path to the file or directory

    Returns:
        Dictionary with file info: size, modified_time, is_file, is_directory, etc.

    Raises:
        FileSystemError: If path doesn't exist or info can't be retrieved
    """
    path = validate_path(file_path, "get info")

    if not path.exists():
        raise FileSystemError(f"Path not found: {path}")

    try:
        stat = path.stat()
        return {
            "name": path.name,
            "size": stat.st_size,
            "modified_time": stat.st_mtime,
            "is_file": path.is_file(),
            "is_directory": path.is_dir(),
            "is_symlink": path.is_symlink(),
            "absolute_path": str(path),
            "parent": str(path.parent),
            "suffix": path.suffix,
            "permissions": oct(stat.st_mode)[-3:],
        }
    except OSError as e:
        raise FileSystemError(f"Failed to get info for {path}: {e}")


def file_exists(file_path: str) -> bool:
    """Check if a file exists.

    Args:
        file_path: Path to check

    Returns:
        True if file exists, False otherwise
    """
    try:
        path = validate_path(file_path, "check file existence")
        return path.is_file()
    except FileSystemError:
        return False


def directory_exists(directory_path: str) -> bool:
    """Check if a directory exists.

    Args:
        directory_path: Path to check

    Returns:
        True if directory exists, False otherwise
    """
    try:
        path = validate_path(directory_path, "check directory existence")
        return path.is_dir()
    except FileSystemError:
        return False


def get_file_size(file_path: str) -> int:
    """Get file size in bytes.

    Args:
        file_path: Path to the file

    Returns:
        File size in bytes

    Raises:
        FileSystemError: If file doesn't exist or size can't be retrieved
    """
    path = validate_path(file_path, "get file size")

    if not path.is_file():
        raise FileSystemError(f"File not found: {path}")

    try:
        return path.stat().st_size
    except OSError as e:
        raise FileSystemError(f"Failed to get size for {path}: {e}")


def is_empty_directory(directory_path: str) -> bool:
    """Check if a directory is empty.

    Args:
        directory_path: Path to the directory

    Returns:
        True if directory is empty, False otherwise

    Raises:
        FileSystemError: If directory doesn't exist or can't be read
    """
    path = validate_path(directory_path, "check empty directory")

    if not path.is_dir():
        raise FileSystemError(f"Directory not found: {path}")

    try:
        return not any(path.iterdir())
    except OSError as e:
        raise FileSystemError(f"Failed to check if directory is empty {path}: {e}")
