"""Directory tree listing functionality."""

from pathlib import Path
from typing import List, Optional

from ..exceptions import FileSystemError
from .validation import validate_path


def list_all_directory_contents(directory_path: str) -> str:
    """Generate a tree of all contents in a directory and its subdirectories.

    Args:
        directory_path: Path to the root directory to list

    Returns:
        Tree-like string representation of directory contents

    Raises:
        FileSystemError: If directory doesn't exist or can't be read
    """
    path = validate_path(directory_path, "list all directory contents")

    if not path.is_dir():
        raise FileSystemError(f"Directory not found: {path}")

    def _should_include(item_path: Path) -> bool:
        """Determine if an item should be included (exclude hidden files)."""
        return not item_path.name.startswith(".")

    def _generate_tree(
        current_path: Path, prefix: str = "", is_last: bool = True
    ) -> List[str]:
        """Recursively generate tree representation."""
        tree_lines = []

        # Prepare prefix for current level
        current_prefix = prefix + ("└── " if is_last else "├── ")
        next_prefix = prefix + ("    " if is_last else "│   ")

        # Add current directory/file to tree
        tree_lines.append(f"{current_prefix}{current_path.name}")

        # If it's a directory, explore its contents
        if current_path.is_dir():
            try:
                # Get contents, filtering hidden files
                contents = [
                    item
                    for item in sorted(current_path.iterdir())
                    if _should_include(item)
                ]

                # Recursively add subdirectories and files
                for i, item in enumerate(contents):
                    is_last_item = i == len(contents) - 1
                    tree_lines.extend(_generate_tree(item, next_prefix, is_last_item))
            except OSError as e:
                tree_lines.append(f"  [Error reading directory: {e}]")

        return tree_lines

    try:
        # Generate tree-like representation
        return "\n".join(_generate_tree(path))

    except OSError as e:
        raise FileSystemError(f"Failed to list directory contents {path}: {e}")


def generate_directory_tree(
    directory_path: str, max_depth: Optional[int] = None, include_hidden: bool = False
) -> str:
    """Generate a customizable directory tree.

    Args:
        directory_path: Path to the root directory to list
        max_depth: Maximum depth to traverse (None for unlimited)
        include_hidden: Whether to include hidden files/directories

    Returns:
        Tree-like string representation of directory contents

    Raises:
        FileSystemError: If directory doesn't exist or can't be read
    """
    path = validate_path(directory_path, "generate directory tree")

    if not path.is_dir():
        raise FileSystemError(f"Directory not found: {path}")

    def _should_include(item_path: Path) -> bool:
        """Determine if an item should be included."""
        if not include_hidden and item_path.name.startswith("."):
            return False
        return True

    def _generate_tree(
        current_path: Path, prefix: str = "", depth: int = 0, is_last: bool = True
    ) -> List[str]:
        """Recursively generate tree representation with depth control."""
        tree_lines: List[str] = []

        # Check depth limit
        if max_depth is not None and depth > max_depth:
            return tree_lines

        # Prepare prefix for current level
        current_prefix = prefix + ("└── " if is_last else "├── ")
        next_prefix = prefix + ("    " if is_last else "│   ")

        # Add current directory/file to tree
        tree_lines.append(f"{current_prefix}{current_path.name}")

        # If it's a directory and we haven't reached max depth, explore its contents
        if current_path.is_dir() and (max_depth is None or depth < max_depth):
            try:
                # Get contents, filtering based on include_hidden
                contents = [
                    item
                    for item in sorted(current_path.iterdir())
                    if _should_include(item)
                ]

                # Recursively add subdirectories and files
                for i, item in enumerate(contents):
                    is_last_item = i == len(contents) - 1
                    tree_lines.extend(
                        _generate_tree(item, next_prefix, depth + 1, is_last_item)
                    )
            except OSError as e:
                tree_lines.append(f"{next_prefix}[Error reading directory: {e}]")

        return tree_lines

    try:
        # Generate tree-like representation
        result = _generate_tree(path)
        return "\n".join(result) if result else path.name

    except OSError as e:
        raise FileSystemError(f"Failed to generate directory tree for {path}: {e}")
