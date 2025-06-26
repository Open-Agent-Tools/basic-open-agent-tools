"""Archive processing tools for AI agents.

This module provides functions for creating, extracting, and manipulating
archive files (ZIP, TAR) with a focus on safety and ease of use.
"""

import os
import tarfile
import zipfile
from typing import Any, Dict, List, Optional, Union

from ..exceptions import DataError


def create_zip_archive(
    files: Union[List[str], Dict[str, str]], archive_path: str
) -> None:
    """Create a ZIP archive containing the specified files.

    Args:
        files: Either a list of file paths to include, or a dictionary mapping
            source file paths to destination paths within the archive
        archive_path: Path where the ZIP archive will be created

    Raises:
        FileNotFoundError: If any source file does not exist
        DataError: If the archive cannot be created

    Example:
        >>> # Create a ZIP with original filenames
        >>> create_zip_archive(["file1.txt", "file2.txt"], "archive.zip")
        >>> # Create a ZIP with custom paths in the archive
        >>> create_zip_archive({"file1.txt": "docs/file1.txt"}, "archive.zip")
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(archive_path)), exist_ok=True)

    # Check if files exist before creating the archive
    if isinstance(files, list):
        for file_path in files:
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
    else:
        for src_path in files.keys():
            if not os.path.isfile(src_path):
                raise FileNotFoundError(f"File not found: {src_path}")

    try:
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
            if isinstance(files, list):
                # List of files - use original filenames
                for file_path in files:
                    zip_file.write(file_path, os.path.basename(file_path))
            else:
                # Dictionary mapping source paths to archive paths
                for src_path, archive_name in files.items():
                    zip_file.write(src_path, archive_name)
    except (zipfile.BadZipFile, OSError) as e:
        raise DataError(f"Failed to create ZIP archive: {str(e)}")


def extract_zip_archive(
    archive_path: str, extract_to: str, safe_extraction: bool = True
) -> List[str]:
    """Extract a ZIP archive to the specified directory.

    Args:
        archive_path: Path to the ZIP archive
        extract_to: Directory where files will be extracted
        safe_extraction: If True, prevents extracting files outside the target directory

    Returns:
        List of paths to the extracted files (relative to extract_to)

    Raises:
        FileNotFoundError: If the archive does not exist
        DataError: If the archive is invalid or extraction fails

    Example:
        >>> extracted_files = extract_zip_archive("archive.zip", "output_dir")
        >>> len(extracted_files) > 0
        True
    """
    if not os.path.isfile(archive_path):
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    try:
        # Create extraction directory if it doesn't exist
        os.makedirs(extract_to, exist_ok=True)

        # Get the absolute path of the extraction directory for safety checks
        extract_to_abs = os.path.abspath(extract_to)
        extracted_files = []

        with zipfile.ZipFile(archive_path, "r") as zip_file:
            # Check for path traversal attacks if safe_extraction is enabled
            if safe_extraction:
                for file_info in zip_file.infolist():
                    file_path = os.path.abspath(
                        os.path.join(extract_to, file_info.filename)
                    )
                    if not file_path.startswith(extract_to_abs):
                        raise DataError(
                            f"Attempted path traversal in ZIP: {file_info.filename}"
                        )

            # Extract all files
            zip_file.extractall(extract_to)

            # Return the list of extracted files
            for file_info in zip_file.infolist():
                if not file_info.is_dir():
                    extracted_files.append(file_info.filename)

        return extracted_files

    except zipfile.BadZipFile:
        raise DataError("Invalid ZIP archive")
    except OSError as e:
        raise DataError(f"Failed to extract ZIP archive: {str(e)}")


def list_archive_contents(archive_path: str) -> List[Dict[str, Any]]:
    """List the contents of an archive file (ZIP or TAR).

    Args:
        archive_path: Path to the archive file

    Returns:
        List of dictionaries containing information about each file in the archive:
        - name: Filename within the archive
        - size: Size in bytes
        - is_dir: True if the entry is a directory
        - compressed_size: Compressed size (ZIP only)
        - mtime: Modification time

    Raises:
        FileNotFoundError: If the archive does not exist
        DataError: If the archive is invalid or cannot be read

    Example:
        >>> contents = list_archive_contents("archive.zip")
        >>> isinstance(contents, list) and len(contents) > 0
        True
        >>> "name" in contents[0] and "size" in contents[0]
        True
    """
    if not os.path.isfile(archive_path):
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    extension = os.path.splitext(archive_path)[1].lower()

    try:
        if extension in (".zip", ".jar", ".apk"):
            # ZIP archive
            with zipfile.ZipFile(archive_path, "r") as zip_file:
                contents = []
                for file_info in zip_file.infolist():
                    contents.append(
                        {
                            "name": file_info.filename,
                            "size": file_info.file_size,
                            "compressed_size": file_info.compress_size,
                            "is_dir": file_info.is_dir(),
                            "mtime": file_info.date_time,
                        }
                    )
                return contents

        elif extension in (".tar", ".tgz", ".gz", ".bz2", ".xz"):
            # TAR archive
            with tarfile.open(archive_path, "r:*") as tar_file:
                contents = []
                for member in tar_file.getmembers():
                    contents.append(
                        {
                            "name": member.name,
                            "size": member.size,
                            "is_dir": member.isdir(),
                            "mtime": member.mtime,
                            "mode": member.mode,
                        }
                    )
                return contents

        else:
            raise DataError(f"Unsupported archive format: {extension}")

    except (zipfile.BadZipFile, tarfile.ReadError) as e:
        raise DataError(f"Invalid archive file: {str(e)}")
    except OSError as e:
        raise DataError(f"Failed to read archive: {str(e)}")


def add_to_archive(
    archive_path: str, file_path: str, archive_name: Optional[str] = None
) -> None:
    """Add a file to an existing archive.

    Args:
        archive_path: Path to the archive file
        file_path: Path to the file to add
        archive_name: Name to use within the archive (if None, uses the original filename)

    Raises:
        FileNotFoundError: If the archive or file does not exist
        DataError: If the file cannot be added to the archive

    Example:
        >>> # Add a file to an existing ZIP archive
        >>> add_to_archive("archive.zip", "new_file.txt")
        >>> # Add with a custom path in the archive
        >>> add_to_archive("archive.zip", "new_file.txt", "docs/file.txt")
    """
    if not os.path.isfile(archive_path):
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Use original filename if archive_name is not specified
    if archive_name is None:
        archive_name = os.path.basename(file_path)

    extension = os.path.splitext(archive_path)[1].lower()

    try:
        if extension in (".zip", ".jar", ".apk"):
            # ZIP archive
            with zipfile.ZipFile(archive_path, "a", zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.write(file_path, archive_name)

        elif extension in (".tar", ".tgz", ".gz", ".bz2", ".xz"):
            # TAR archive - need to create a new archive with the added file
            mode = _get_tar_mode(extension)

            # Create a temporary file
            temp_path = archive_path + ".tmp"

            # Copy the original archive and add the new file
            if mode == "gz":
                with tarfile.open(archive_path, "r:gz") as src_tar, tarfile.open(
                    temp_path, "w:gz"
                ) as dest_tar:
                    # Copy existing files
                    for member in src_tar.getmembers():
                        dest_tar.addfile(
                            member,
                            src_tar.extractfile(member) if not member.isdir() else None,
                        )
                    # Add the new file
                    dest_tar.add(file_path, arcname=archive_name)
            elif mode == "bz2":
                with tarfile.open(archive_path, "r:bz2") as src_tar, tarfile.open(
                    temp_path, "w:bz2"
                ) as dest_tar:
                    # Copy existing files
                    for member in src_tar.getmembers():
                        dest_tar.addfile(
                            member,
                            src_tar.extractfile(member) if not member.isdir() else None,
                        )
                    # Add the new file
                    dest_tar.add(file_path, arcname=archive_name)
            elif mode == "xz":
                with tarfile.open(archive_path, "r:xz") as src_tar, tarfile.open(
                    temp_path, "w:xz"
                ) as dest_tar:
                    # Copy existing files
                    for member in src_tar.getmembers():
                        dest_tar.addfile(
                            member,
                            src_tar.extractfile(member) if not member.isdir() else None,
                        )
                    # Add the new file
                    dest_tar.add(file_path, arcname=archive_name)
            else:
                with tarfile.open(archive_path, "r") as src_tar, tarfile.open(
                    temp_path, "w"
                ) as dest_tar:
                    # Copy existing files
                    for member in src_tar.getmembers():
                        dest_tar.addfile(
                            member,
                            src_tar.extractfile(member) if not member.isdir() else None,
                        )
                    # Add the new file
                    dest_tar.add(file_path, arcname=archive_name)

            # Replace the original archive with the new one
            os.replace(temp_path, archive_path)

        else:
            raise DataError(f"Unsupported archive format: {extension}")

    except (zipfile.BadZipFile, tarfile.ReadError) as e:
        raise DataError(f"Invalid archive file: {str(e)}")
    except OSError as e:
        raise DataError(f"Failed to add file to archive: {str(e)}")


def create_tar_archive(
    files: Union[List[str], Dict[str, str]],
    archive_path: str,
    compression: Optional[str] = None,
) -> None:
    """Create a TAR archive containing the specified files.

    Args:
        files: Either a list of file paths to include, or a dictionary mapping
            source file paths to destination paths within the archive
        archive_path: Path where the TAR archive will be created
        compression: Compression method (None, "gz", "bz2", "xz")

    Raises:
        FileNotFoundError: If any source file does not exist
        DataError: If the archive cannot be created or the compression method is invalid

    Example:
        >>> # Create an uncompressed TAR
        >>> create_tar_archive(["file1.txt", "file2.txt"], "archive.tar")
        >>> # Create a compressed TAR with custom paths
        >>> create_tar_archive({"file1.txt": "docs/file1.txt"}, "archive.tar.gz", "gz")
    """
    # Validate compression method
    valid_compressions = (None, "gz", "bz2", "xz")
    if compression not in valid_compressions:
        raise DataError(
            f"Invalid compression method: {compression}. "
            f"Must be one of: {', '.join(str(c) for c in valid_compressions)}"
        )

    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(archive_path)), exist_ok=True)

        # Use explicit mode strings to satisfy MyPy type checking
        if compression == "gz":
            with tarfile.open(archive_path, "w:gz") as tar_file:
                _add_files_to_tar(tar_file, files)
        elif compression == "bz2":
            with tarfile.open(archive_path, "w:bz2") as tar_file:
                _add_files_to_tar(tar_file, files)
        elif compression == "xz":
            with tarfile.open(archive_path, "w:xz") as tar_file:
                _add_files_to_tar(tar_file, files)
        else:
            with tarfile.open(archive_path, "w") as tar_file:
                _add_files_to_tar(tar_file, files)

    except tarfile.TarError as e:
        raise DataError(f"Failed to create TAR archive: {str(e)}")
    except OSError as e:
        raise DataError(f"Failed to create TAR archive: {str(e)}")


def extract_tar_archive(
    archive_path: str, extract_to: str, safe_extraction: bool = True
) -> List[str]:
    """Extract a TAR archive to the specified directory.

    Args:
        archive_path: Path to the TAR archive
        extract_to: Directory where files will be extracted
        safe_extraction: If True, prevents extracting files outside the target directory

    Returns:
        List of paths to the extracted files (relative to extract_to)

    Raises:
        FileNotFoundError: If the archive does not exist
        DataError: If the archive is invalid or extraction fails

    Example:
        >>> extracted_files = extract_tar_archive("archive.tar.gz", "output_dir")
        >>> len(extracted_files) > 0
        True
    """
    if not os.path.isfile(archive_path):
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    try:
        # Create extraction directory if it doesn't exist
        os.makedirs(extract_to, exist_ok=True)

        # Get the absolute path of the extraction directory for safety checks
        extract_to_abs = os.path.abspath(extract_to)
        extracted_files = []

        with tarfile.open(archive_path, "r:*") as tar_file:
            # Check for path traversal attacks if safe_extraction is enabled
            if safe_extraction:
                for member in tar_file.getmembers():
                    file_path = os.path.abspath(os.path.join(extract_to, member.name))
                    if not file_path.startswith(extract_to_abs):
                        raise DataError(
                            f"Attempted path traversal in TAR: {member.name}"
                        )

                    # Also check for absolute paths in the archive
                    if member.name.startswith(("/", "~")):
                        raise DataError(f"Absolute path in TAR: {member.name}")

            # Extract all files
            tar_file.extractall(extract_to)

            # Return the list of extracted files
            for member in tar_file.getmembers():
                if not member.isdir():
                    extracted_files.append(member.name)

        return extracted_files

    except tarfile.ReadError:
        raise DataError("Invalid TAR archive")
    except OSError as e:
        raise DataError(f"Failed to extract TAR archive: {str(e)}")


def validate_archive_integrity(archive_path: str) -> bool:
    """Check if an archive file is valid and not corrupted.

    Args:
        archive_path: Path to the archive file

    Returns:
        True if the archive is valid, False otherwise

    Example:
        >>> # Check if a ZIP file is valid
        >>> validate_archive_integrity("archive.zip")
        True
    """
    if not os.path.isfile(archive_path):
        return False

    extension = os.path.splitext(archive_path)[1].lower()

    try:
        if extension in (".zip", ".jar", ".apk"):
            # ZIP archive
            with zipfile.ZipFile(archive_path, "r") as zip_file:
                # testzip() returns None if the archive is valid
                return zip_file.testzip() is None

        elif extension in (".tar", ".tgz", ".gz", ".bz2", ".xz"):
            # TAR archive
            with tarfile.open(archive_path, "r:*") as tar_file:
                # Try to read the members to check integrity
                tar_file.getmembers()
                return True

        else:
            # Unsupported format
            return False

    except (zipfile.BadZipFile, tarfile.ReadError, OSError):
        return False


def _add_files_to_tar(
    tar_file: tarfile.TarFile, files: Union[List[str], Dict[str, str]]
) -> None:
    """Helper function to add files to a tar archive."""
    if isinstance(files, list):
        # List of files - use original filenames
        for file_path in files:
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            tar_file.add(file_path, arcname=os.path.basename(file_path))
    else:
        # Dictionary mapping source paths to archive paths
        for src_path, archive_name in files.items():
            if not os.path.isfile(src_path):
                raise FileNotFoundError(f"File not found: {src_path}")
            tar_file.add(src_path, arcname=archive_name)


def _get_tar_mode(extension: str) -> str:
    """Get the appropriate mode for tarfile operations based on file extension.

    Args:
        extension: File extension including the dot (e.g., ".tar.gz")

    Returns:
        Mode string for tarfile operations
    """
    if extension.endswith(".gz") or extension.endswith(".tgz"):
        return "gz"
    elif extension.endswith(".bz2"):
        return "bz2"
    elif extension.endswith(".xz"):
        return "xz"
    else:
        return ""  # Uncompressed
