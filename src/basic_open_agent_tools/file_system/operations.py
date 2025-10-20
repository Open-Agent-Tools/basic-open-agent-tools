"""Core file and directory operations."""

import shutil

from .._logging import get_logger
from ..confirmation import check_user_confirmation
from ..decorators import strands_tool
from ..exceptions import FileSystemError
from .validation import validate_file_content, validate_path

logger = get_logger("file_system.operations")


def _generate_content_preview(content: str, max_chars: int = 1200) -> str:
    """Generate a preview of content for confirmation prompts.

    Args:
        content: The content to preview
        max_chars: Maximum number of characters to show in preview

    Returns:
        Formatted preview string with line count, byte size, and content sample
    """
    line_count = len(content.splitlines()) if content else 0
    byte_size = len(content.encode("utf-8"))

    preview = f"Writing {line_count} lines ({byte_size} bytes)\n"

    if content:
        # Show first max_chars of content with actual formatting
        sample = content[:max_chars]
        truncated = len(content) > max_chars

        preview += "Content preview:\n"
        preview += "─" * 40 + "\n"
        preview += sample
        if truncated:
            preview += "\n" + "─" * 40
            preview += (
                f"\n[...truncated, showing first {max_chars} of {len(content)} chars]"
            )
        else:
            preview += "\n" + "─" * 40
    else:
        preview += "Content: (empty file)"

    return preview


@strands_tool
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

    logger.info(f"Reading file: {path}")

    try:
        content: str = path.read_text(encoding="utf-8").strip()
        logger.info(f"File read successfully: {len(content)} characters")
        logger.debug(
            f"Content preview: {content[:100]}{'...' if len(content) > 100 else ''}"
        )
        return content
    except (OSError, UnicodeDecodeError) as e:
        logger.error(f"Failed to read {path}: {e}")
        raise FileSystemError(f"Failed to read file {path}: {e}")


@strands_tool
def write_file_from_string(file_path: str, content: str, skip_confirm: bool) -> str:
    """Write string content to a text file with permission checking.

    Args:
        file_path: Path to the output file
        content: String content to write
        skip_confirm: If True, skip confirmation and overwrite existing files. IMPORTANT: Agents should default to skip_confirm=False for safety.

    Returns:
        String describing the operation result

    Raises:
        FileSystemError: If write operation fails or file exists without skip_confirm
    """
    validate_file_content(content, "write")
    path = validate_path(file_path, "write")

    file_existed = path.exists()
    line_count = len(content.splitlines()) if content else 0
    byte_size = len(content.encode("utf-8"))

    logger.info(f"Writing file: {path} ({line_count} lines, {byte_size} bytes)")
    logger.debug(f"File exists: {file_existed}, skip_confirm: {skip_confirm}")

    if file_existed:
        # Check user confirmation (interactive prompt, agent error, or bypass)
        # Show preview of NEW content being written, not old file size
        preview = _generate_content_preview(content)
        confirmed = check_user_confirmation(
            operation="overwrite existing file",
            target=str(path),
            skip_confirm=skip_confirm,
            preview_info=preview,
        )

        if not confirmed:
            logger.debug(f"Write cancelled by user: {path}")
            return f"Operation cancelled by user: {path}"

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

        action = "Overwrote" if file_existed else "Created"
        result = f"{action} file {path} with {line_count} lines"
        logger.info(
            f"File written successfully: {action.lower()} {line_count} lines, {byte_size} bytes"
        )
        logger.debug(f"{result}")
        return result
    except OSError as e:
        logger.error(f"Failed to write {path}: {e}")
        raise FileSystemError(f"Failed to write file {path}: {e}")


@strands_tool
def append_to_file(file_path: str, content: str) -> str:
    """Append string content to a text file.

    Args:
        file_path: Path to the file
        content: String content to append

    Returns:
        String describing the operation result

    Raises:
        FileSystemError: If append operation fails
    """
    validate_file_content(content, "append")
    path = validate_path(file_path, "append")

    file_existed = path.exists()
    original_size = path.stat().st_size if file_existed else 0

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as file:
            file.write(content)

        new_size = path.stat().st_size
        bytes_added = new_size - original_size
        line_count = len(content.splitlines()) if content else 0

        if file_existed:
            return f"Appended {line_count} lines ({bytes_added} bytes) to {path}"
        else:
            return f"Created file {path} with {line_count} lines ({bytes_added} bytes)"
    except OSError as e:
        raise FileSystemError(f"Failed to append to file {path}: {e}")


@strands_tool
def list_directory_contents(directory_path: str, include_hidden: bool) -> list[str]:
    """List contents of a directory.

    Args:
        directory_path: Path to the directory
        include_hidden: Whether to include hidden files/directories

    Returns:
        Sorted list of file and directory names

    Raises:
        FileSystemError: If directory doesn't exist or can't be read
    """
    logger.debug(
        f"Listing directory: {directory_path} (include_hidden={include_hidden})"
    )

    path = validate_path(directory_path, "list directory")

    if not path.is_dir():
        raise FileSystemError(f"Directory not found: {path}")

    try:
        contents = [item.name for item in path.iterdir()]
        if not include_hidden:
            contents = [name for name in contents if not name.startswith(".")]
        sorted_contents = sorted(contents)
        logger.debug(f"Found {len(sorted_contents)} items in {path}")
        return sorted_contents
    except OSError as e:
        logger.error(f"Failed to list directory {path}: {e}")
        raise FileSystemError(f"Failed to list directory {path}: {e}")


@strands_tool
def create_directory(directory_path: str, skip_confirm: bool) -> str:
    """Create a directory and any necessary parent directories.

    Args:
        directory_path: Path to the directory to create
        skip_confirm: If True, skip confirmation and proceed even if directory already exists. IMPORTANT: Agents should default to skip_confirm=False for safety.

    Returns:
        String describing the operation result

    Raises:
        FileSystemError: If directory creation fails or exists without skip_confirm
    """
    path = validate_path(directory_path, "create directory")

    already_existed = path.exists()

    if already_existed:
        # Check user confirmation (interactive prompt, agent error, or bypass)
        confirmed = check_user_confirmation(
            operation="use existing directory",
            target=str(path),
            skip_confirm=skip_confirm,
            preview_info="Directory already exists",
        )

        if not confirmed:
            return f"Operation cancelled by user: {path}"

    try:
        path.mkdir(parents=True, exist_ok=True)

        if already_existed:
            return f"Directory already exists: {path}"
        else:
            return f"Created directory: {path}"
    except OSError as e:
        raise FileSystemError(f"Failed to create directory {path}: {e}")


@strands_tool
def delete_file(file_path: str, skip_confirm: bool) -> str:
    """Delete a file with permission checking.

    Args:
        file_path: Path to the file to delete
        skip_confirm: If True, skip confirmation and proceed with deletion. IMPORTANT: Agents should default to skip_confirm=False for safety.

    Returns:
        String describing the operation result

    Raises:
        FileSystemError: If deletion fails or file doesn't exist without skip_confirm
    """
    path = validate_path(file_path, "delete file")

    if not path.exists():
        # For non-existent files, check if we need confirmation for the error suppression
        confirmed = check_user_confirmation(
            operation="suppress file-not-found error",
            target=str(path),
            skip_confirm=skip_confirm,
            preview_info="File does not exist",
        )

        if not confirmed:
            raise FileSystemError(f"File not found: {path}")

        return f"File not found (already deleted): {path}"

    if not path.is_file():
        raise FileSystemError(f"Path is not a file: {path}")

    # Get file info before deletion
    file_size = path.stat().st_size

    logger.info(f"Deleting file: {path} ({file_size} bytes)")
    logger.debug(f"skip_confirm: {skip_confirm}")

    # Check user confirmation for deletion
    confirmed = check_user_confirmation(
        operation="delete file",
        target=str(path),
        skip_confirm=skip_confirm,
        preview_info=f"File size: {file_size} bytes",
    )

    if not confirmed:
        logger.debug(f"Deletion cancelled by user: {path}")
        return f"Operation cancelled by user: {path}"

    try:
        path.unlink()
        result = f"Deleted file {path} ({file_size} bytes)"
        logger.info(f"File deleted successfully: {file_size} bytes")
        logger.debug(f"{result}")
        return result
    except OSError as e:
        logger.error(f"Failed to delete {path}: {e}")
        raise FileSystemError(f"Failed to delete file {path}: {e}")


@strands_tool
def delete_directory(directory_path: str, recursive: bool, skip_confirm: bool) -> str:
    """Delete a directory with permission checking.

    Args:
        directory_path: Path to the directory to delete
        recursive: If True, delete directory and all contents recursively
        skip_confirm: If True, skip confirmation and proceed with deletion. IMPORTANT: Agents should default to skip_confirm=False for safety.

    Returns:
        String describing the operation result

    Raises:
        FileSystemError: If deletion fails or directory doesn't exist without skip_confirm
    """
    path = validate_path(directory_path, "delete directory")

    if not path.exists():
        # Check confirmation for error suppression
        confirmed = check_user_confirmation(
            operation="suppress directory-not-found error",
            target=str(path),
            skip_confirm=skip_confirm,
            preview_info="Directory does not exist",
        )

        if not confirmed:
            raise FileSystemError(f"Directory not found: {path}")

        return f"Directory not found (already deleted): {path}"

    if not path.is_dir():
        raise FileSystemError(f"Path is not a directory: {path}")

    # Count contents before deletion
    try:
        contents = list(path.iterdir())
        item_count = len(contents)

        if not recursive and item_count > 0:
            raise FileSystemError(
                f"Directory not empty: {path}. Use recursive=True to delete contents."
            )
    except OSError:
        item_count = 0  # Can't read contents, proceed anyway

    # Check user confirmation for deletion
    preview = f"Contains {item_count} items" if item_count > 0 else "Empty directory"
    if recursive and item_count > 0:
        preview += " (recursive deletion)"

    confirmed = check_user_confirmation(
        operation="delete directory",
        target=str(path),
        skip_confirm=skip_confirm,
        preview_info=preview,
    )

    if not confirmed:
        return f"Operation cancelled by user: {path}"

    try:
        if recursive:
            shutil.rmtree(path)
            if item_count > 0:
                return f"Deleted directory {path} and {item_count} items recursively"
            else:
                return f"Deleted empty directory: {path}"
        else:
            path.rmdir()  # Only works if directory is empty
            return f"Deleted empty directory: {path}"
    except OSError as e:
        raise FileSystemError(f"Failed to delete directory {path}: {e}")


@strands_tool
def move_file(source_path: str, destination_path: str, skip_confirm: bool) -> str:
    """Move or rename a file or directory with permission checking.

    Args:
        source_path: Current path of the file/directory
        destination_path: New path for the file/directory
        skip_confirm: If True, skip confirmation and overwrite destination if it exists. IMPORTANT: Agents should default to skip_confirm=False for safety.

    Returns:
        String describing the operation result

    Raises:
        FileSystemError: If move operation fails or destination exists without skip_confirm
    """
    src_path = validate_path(source_path, "move source")
    dst_path = validate_path(destination_path, "move destination")

    if not src_path.exists():
        raise FileSystemError(f"Source path not found: {src_path}")

    destination_existed = dst_path.exists()

    # Get source info before move
    is_directory = src_path.is_dir()
    if src_path.is_file():
        file_size = src_path.stat().st_size
        size_info = f" ({file_size} bytes)"
        preview = (
            f"Will overwrite existing file ({dst_path.stat().st_size} bytes)"
            if destination_existed
            else None
        )
    else:
        size_info = ""
        preview = "Will overwrite existing directory" if destination_existed else None

    item_type = "directory" if is_directory else "file"

    logger.info(f"Moving {item_type}: {src_path} → {dst_path}{size_info}")
    logger.debug(
        f"Destination exists: {destination_existed}, skip_confirm: {skip_confirm}"
    )

    if destination_existed:
        # Check user confirmation for overwrite
        confirmed = check_user_confirmation(
            operation=f"overwrite existing {item_type} during move",
            target=str(dst_path),
            skip_confirm=skip_confirm,
            preview_info=preview if destination_existed else None,
        )

        if not confirmed:
            logger.debug(f"Move cancelled by user: {src_path} -> {dst_path}")
            return f"Operation cancelled by user: move from {src_path} to {dst_path}"

    try:
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_path), str(dst_path))

        action = "Moved and overwrote" if destination_existed else "Moved"
        result = f"{action} {item_type} from {src_path} to {dst_path}{size_info}"
        logger.info(f"Move completed successfully: {action.lower()} {item_type}")
        logger.debug(f"{result}")
        return result
    except OSError as e:
        logger.error(f"Failed to move {src_path} to {dst_path}: {e}")
        raise FileSystemError(f"Failed to move {src_path} to {dst_path}: {e}")


@strands_tool
def copy_file(source_path: str, destination_path: str, skip_confirm: bool) -> str:
    """Copy a file or directory with permission checking.

    Args:
        source_path: Path of the source file/directory
        destination_path: Path for the copied file/directory
        skip_confirm: If True, skip confirmation and overwrite destination if it exists. IMPORTANT: Agents should default to skip_confirm=False for safety.

    Returns:
        String describing the operation result

    Raises:
        FileSystemError: If copy operation fails or destination exists without skip_confirm
    """
    src_path = validate_path(source_path, "copy source")
    dst_path = validate_path(destination_path, "copy destination")

    if not src_path.exists():
        raise FileSystemError(f"Source path not found: {src_path}")

    destination_existed = dst_path.exists()

    # Get source info
    is_directory = src_path.is_dir()
    if src_path.is_file():
        file_size = src_path.stat().st_size
        size_info = f" ({file_size} bytes)"
        preview = (
            f"Will overwrite existing file ({dst_path.stat().st_size} bytes)"
            if destination_existed
            else None
        )
    else:
        # Count directory contents
        try:
            contents = list(src_path.rglob("*"))
            file_count = len([p for p in contents if p.is_file()])
            size_info = f" ({file_count} files)"
            preview = (
                f"Will overwrite existing directory ({file_count} files to copy)"
                if destination_existed
                else None
            )
        except OSError:
            size_info = ""
            preview = (
                "Will overwrite existing directory" if destination_existed else None
            )

    item_type = "directory" if is_directory else "file"

    logger.info(f"Copying {item_type}: {src_path} → {dst_path}{size_info}")
    logger.debug(
        f"Destination exists: {destination_existed}, skip_confirm: {skip_confirm}"
    )

    if destination_existed:
        # Check user confirmation for overwrite
        confirmed = check_user_confirmation(
            operation=f"overwrite existing {item_type} during copy",
            target=str(dst_path),
            skip_confirm=skip_confirm,
            preview_info=preview,
        )

        if not confirmed:
            return f"Operation cancelled by user: copy from {src_path} to {dst_path}"

    try:
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        if src_path.is_file():
            shutil.copy2(str(src_path), str(dst_path))
        else:
            if destination_existed:
                shutil.rmtree(dst_path)  # Remove existing directory first
            shutil.copytree(str(src_path), str(dst_path))

        action = "Copied and overwrote" if destination_existed else "Copied"
        result = f"{action} {item_type} from {src_path} to {dst_path}{size_info}"
        logger.info(f"Copy completed successfully: {action.lower()} {item_type}")
        return result
    except OSError as e:
        raise FileSystemError(f"Failed to copy {src_path} to {dst_path}: {e}")


@strands_tool
def replace_in_file(file_path: str, old_text: str, new_text: str, count: int) -> str:
    """Replace occurrences of text within a file with detailed feedback.

    This function performs targeted text replacement, making it safer for agents
    to make small changes without accidentally removing other content.

    Args:
        file_path: Path to the file to modify
        old_text: Text to search for and replace
        new_text: Text to replace the old text with
        count: Maximum number of replacements to make (-1 for all occurrences)

    Returns:
        String describing the operation result

    Raises:
        FileSystemError: If file doesn't exist, can't be read, or write fails
        ValueError: If old_text is empty
    """
    if not old_text:
        raise ValueError("old_text cannot be empty")

    # Enhanced input logging for security auditing
    logger.debug(
        f"replace_in_file: file_path='{file_path}', old_text='{old_text[:100]}{'...' if len(old_text) > 100 else ''}', new_text='{new_text[:100]}{'...' if len(new_text) > 100 else ''}', count={count}"
    )

    validate_file_content(new_text, "replace")
    path = validate_path(file_path, "replace")

    if not path.is_file():
        raise FileSystemError(f"File not found: {path}")

    try:
        # Read current content
        content = path.read_text(encoding="utf-8")

        # Count total occurrences before replacement
        total_occurrences = content.count(old_text)

        if total_occurrences == 0:
            return f"No occurrences of '{old_text}' found in {path}"

        # Perform replacement
        updated_content = content.replace(old_text, new_text, count)

        # Count actual replacements made
        remaining_occurrences = updated_content.count(old_text)
        replacements_made = total_occurrences - remaining_occurrences

        # Write back to file
        path.write_text(updated_content, encoding="utf-8")

        if count == -1 or replacements_made == total_occurrences:
            return f"Replaced {replacements_made} occurrence(s) of '{old_text}' with '{new_text}' in {path}"
        else:
            return f"Replaced {replacements_made} of {total_occurrences} occurrence(s) of '{old_text}' with '{new_text}' in {path}"
    except (OSError, UnicodeDecodeError) as e:
        raise FileSystemError(f"Failed to replace text in file {path}: {e}")


@strands_tool
def insert_at_line(file_path: str, line_number: int, content: str) -> str:
    """Insert content at a specific line number in a file with detailed feedback.

    This function allows precise insertion of text at a specific line,
    making it safer for agents to add content without overwriting files.

    Args:
        file_path: Path to the file to modify
        line_number: Line number to insert at (1-based indexing)
        content: Content to insert (will be added as a new line)

    Returns:
        String describing the operation result

    Raises:
        FileSystemError: If file doesn't exist, can't be read, or write fails
        ValueError: If line_number is less than 1
    """
    if line_number < 1:
        raise ValueError("line_number must be 1 or greater")

    # Enhanced input logging for security auditing
    logger.debug(
        f"insert_at_line: file_path='{file_path}', line_number={line_number}, content='{content[:100]}{'...' if len(content) > 100 else ''}')"
    )

    validate_file_content(content, "insert")
    path = validate_path(file_path, "insert")

    if not path.is_file():
        raise FileSystemError(f"File not found: {path}")

    try:
        # Read current lines
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        original_line_count = len(lines)

        # Ensure content ends with newline if it doesn't already
        if content and not content.endswith("\n"):
            content += "\n"

        # Insert at specified line (convert to 0-based index)
        insert_index = line_number - 1

        # Determine position description for feedback
        if insert_index >= original_line_count:
            lines.append(content)
            position_desc = f"end (after line {original_line_count})"
        else:
            lines.insert(insert_index, content)
            position_desc = f"line {line_number}"

        # Write back to file
        path.write_text("".join(lines), encoding="utf-8")

        new_line_count = len(lines)
        content_lines = len(content.splitlines()) if content else 0

        return f"Inserted {content_lines} line(s) at {position_desc} in {path} (file now has {new_line_count} lines)"
    except (OSError, UnicodeDecodeError) as e:
        raise FileSystemError(f"Failed to insert content in file {path}: {e}")
