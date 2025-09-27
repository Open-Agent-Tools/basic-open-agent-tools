"""Advanced compression utilities for ZIP, GZIP, BZIP2, and XZ formats."""

import bz2
import gzip
import lzma
import os
import shutil
import zipfile
from typing import Any, Callable, Optional, Union

try:
    from strands import tool as strands_tool
except ImportError:

    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        return func


from ..exceptions import BasicAgentToolsError


@strands_tool
def create_zip(source_paths: list[str], output_path: str, force: bool) -> str:
    """Create a ZIP archive from files and directories with permission checking."""
    print(f"[ARCHIVE] Creating ZIP: {output_path} from {len(source_paths)} sources (force={force})")

    if not isinstance(source_paths, list) or not source_paths:
        raise BasicAgentToolsError("Source paths must be a non-empty list")

    if not isinstance(output_path, str) or not output_path.strip():
        raise BasicAgentToolsError("Output path must be a non-empty string")

    if not isinstance(force, bool):
        raise BasicAgentToolsError("force must be a boolean")

    # Check if output file exists
    file_existed = os.path.exists(output_path)

    if file_existed and not force:
        print(f"[ARCHIVE] ZIP creation blocked - file exists and force=False: {output_path}")
        raise BasicAgentToolsError(
            f"ZIP archive already exists: {output_path}. Use force=True to overwrite."
        )

    try:
        files_added = []
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for source_path in source_paths:
                if os.path.isfile(source_path):
                    zf.write(source_path, os.path.basename(source_path))
                    files_added.append(source_path)
                elif os.path.isdir(source_path):
                    for root, _dirs, files in os.walk(source_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_name = os.path.relpath(
                                file_path, os.path.dirname(source_path)
                            )
                            zf.write(file_path, arc_name)
                            files_added.append(file_path)

        # Calculate stats for feedback
        archive_size = os.path.getsize(output_path)
        file_count = len(files_added)
        action = "Overwrote" if file_existed else "Created"

        result = f"{action} ZIP archive {output_path} with {file_count} files ({archive_size} bytes)"
        print(f"[ARCHIVE] {result}")
        return result
    except Exception as e:
        print(f"[ARCHIVE] ZIP creation failed: {e}")
        raise BasicAgentToolsError(f"Failed to create ZIP archive: {str(e)}")


@strands_tool
def extract_zip(zip_path: str, extract_to: str, force: bool) -> str:
    """Extract a ZIP archive to a directory with permission checking."""
    print(f"[ARCHIVE] Extracting ZIP: {zip_path} to {extract_to} (force={force})")

    if not isinstance(zip_path, str) or not zip_path.strip():
        raise BasicAgentToolsError("ZIP path must be a non-empty string")

    if not isinstance(extract_to, str) or not extract_to.strip():
        raise BasicAgentToolsError("Extract path must be a non-empty string")

    if not isinstance(force, bool):
        raise BasicAgentToolsError("force must be a boolean")

    if not os.path.exists(zip_path):
        print(f"[ARCHIVE] ZIP file not found: {zip_path}")
        raise BasicAgentToolsError(f"ZIP file not found: {zip_path}")

    # Check if extraction directory exists and has contents
    extract_exists = os.path.exists(extract_to)
    if extract_exists and not force:
        try:
            if os.listdir(extract_to):  # Directory exists and has contents
                raise BasicAgentToolsError(
                    f"Extract directory already exists and is not empty: {extract_to}. Use force=True to proceed."
                )
        except OSError:
            pass  # Can't read directory, proceed anyway

    try:
        # Create extraction directory if it doesn't exist
        os.makedirs(extract_to, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_to)
            files_extracted = len(zf.namelist())

        # Calculate archive size for feedback
        archive_size = os.path.getsize(zip_path)

        result = f"Extracted ZIP archive {zip_path} to {extract_to} ({files_extracted} files, {archive_size} bytes)"
        print(f"[ARCHIVE] {result}")
        return result
    except Exception as e:
        print(f"[ARCHIVE] ZIP extraction failed: {e}")
        raise BasicAgentToolsError(f"Failed to extract ZIP archive: {str(e)}")


@strands_tool
def compress_files(file_paths: list[str], output_path: str, force: bool) -> str:
    """Compress multiple files into a ZIP archive."""
    print(f"[ARCHIVE] Compressing {len(file_paths)} files to: {output_path}")
    return create_zip(file_paths, output_path, force)


@strands_tool
def compress_file_gzip(
    input_path: str, output_path: Optional[str] = None
) -> dict[str, Union[str, int, float]]:
    """
    Compress a file using gzip compression.

    Args:
        input_path: Path to input file
        output_path: Path for compressed file (defaults to input_path.gz)

    Returns:
        Dictionary with compression results

    Raises:
        BasicAgentToolsError: If compression fails
    """
    if not isinstance(input_path, str) or not input_path.strip():
        raise BasicAgentToolsError("Input path must be a non-empty string")

    input_path = input_path.strip()

    if not os.path.exists(input_path):
        raise BasicAgentToolsError(f"Input file not found: {input_path}")

    if not os.path.isfile(input_path):
        raise BasicAgentToolsError(f"Input path is not a file: {input_path}")

    if output_path is None:
        output_path = f"{input_path}.gz"
    elif not isinstance(output_path, str) or not output_path.strip():
        raise BasicAgentToolsError("Output path must be a non-empty string")
    else:
        output_path = output_path.strip()

    try:
        input_size = os.path.getsize(input_path)

        with open(input_path, "rb") as f_in:
            with gzip.open(output_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        output_size = os.path.getsize(output_path)
        compression_ratio = output_size / input_size if input_size > 0 else 0

        return {
            "input_path": input_path,
            "output_path": output_path,
            "input_size_bytes": input_size,
            "output_size_bytes": output_size,
            "compression_ratio": round(compression_ratio, 3),
            "space_saved_bytes": input_size - output_size,
            "compression_percent": round((1 - compression_ratio) * 100, 1),
            "compression_type": "gzip",
            "compression_status": "success",
        }

    except Exception as e:
        raise BasicAgentToolsError(f"Failed to compress file with gzip: {str(e)}")


@strands_tool
def decompress_file_gzip(
    input_path: str, output_path: Optional[str] = None
) -> dict[str, Union[str, int]]:
    """
    Decompress a gzip compressed file.

    Args:
        input_path: Path to gzip file
        output_path: Path for decompressed file (defaults to input without .gz)

    Returns:
        Dictionary with decompression results

    Raises:
        BasicAgentToolsError: If decompression fails
    """
    if not isinstance(input_path, str) or not input_path.strip():
        raise BasicAgentToolsError("Input path must be a non-empty string")

    input_path = input_path.strip()

    if not os.path.exists(input_path):
        raise BasicAgentToolsError(f"Input file not found: {input_path}")

    if output_path is None:
        if input_path.endswith(".gz"):
            output_path = input_path[:-3]
        else:
            output_path = f"{input_path}.decompressed"
    elif not isinstance(output_path, str) or not output_path.strip():
        raise BasicAgentToolsError("Output path must be a non-empty string")
    else:
        output_path = output_path.strip()

    try:
        input_size = os.path.getsize(input_path)

        with gzip.open(input_path, "rb") as f_in:
            with open(output_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        output_size = os.path.getsize(output_path)

        return {
            "input_path": input_path,
            "output_path": output_path,
            "compressed_size_bytes": input_size,
            "decompressed_size_bytes": output_size,
            "expansion_ratio": round(output_size / input_size, 2)
            if input_size > 0
            else 0,
            "decompression_type": "gzip",
            "decompression_status": "success",
        }

    except Exception as e:
        raise BasicAgentToolsError(f"Failed to decompress gzip file: {str(e)}")


@strands_tool
def compress_file_bzip2(
    input_path: str, output_path: Optional[str] = None
) -> dict[str, Union[str, int, float]]:
    """
    Compress a file using bzip2 compression.

    Args:
        input_path: Path to input file
        output_path: Path for compressed file (defaults to input_path.bz2)

    Returns:
        Dictionary with compression results

    Raises:
        BasicAgentToolsError: If compression fails
    """
    if not isinstance(input_path, str) or not input_path.strip():
        raise BasicAgentToolsError("Input path must be a non-empty string")

    input_path = input_path.strip()

    if not os.path.exists(input_path):
        raise BasicAgentToolsError(f"Input file not found: {input_path}")

    if not os.path.isfile(input_path):
        raise BasicAgentToolsError(f"Input path is not a file: {input_path}")

    if output_path is None:
        output_path = f"{input_path}.bz2"
    elif not isinstance(output_path, str) or not output_path.strip():
        raise BasicAgentToolsError("Output path must be a non-empty string")
    else:
        output_path = output_path.strip()

    try:
        input_size = os.path.getsize(input_path)

        with open(input_path, "rb") as f_in:
            with bz2.BZ2File(output_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        output_size = os.path.getsize(output_path)
        compression_ratio = output_size / input_size if input_size > 0 else 0

        return {
            "input_path": input_path,
            "output_path": output_path,
            "input_size_bytes": input_size,
            "output_size_bytes": output_size,
            "compression_ratio": round(compression_ratio, 3),
            "space_saved_bytes": input_size - output_size,
            "compression_percent": round((1 - compression_ratio) * 100, 1),
            "compression_type": "bzip2",
            "compression_status": "success",
        }

    except Exception as e:
        raise BasicAgentToolsError(f"Failed to compress file with bzip2: {str(e)}")


@strands_tool
def compress_file_xz(
    input_path: str, output_path: Optional[str] = None
) -> dict[str, Union[str, int, float]]:
    """
    Compress a file using XZ/LZMA compression.

    Args:
        input_path: Path to input file
        output_path: Path for compressed file (defaults to input_path.xz)

    Returns:
        Dictionary with compression results

    Raises:
        BasicAgentToolsError: If compression fails
    """
    if not isinstance(input_path, str) or not input_path.strip():
        raise BasicAgentToolsError("Input path must be a non-empty string")

    input_path = input_path.strip()

    if not os.path.exists(input_path):
        raise BasicAgentToolsError(f"Input file not found: {input_path}")

    if not os.path.isfile(input_path):
        raise BasicAgentToolsError(f"Input path is not a file: {input_path}")

    if output_path is None:
        output_path = f"{input_path}.xz"
    elif not isinstance(output_path, str) or not output_path.strip():
        raise BasicAgentToolsError("Output path must be a non-empty string")
    else:
        output_path = output_path.strip()

    try:
        input_size = os.path.getsize(input_path)

        with open(input_path, "rb") as f_in:
            with lzma.LZMAFile(output_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        output_size = os.path.getsize(output_path)
        compression_ratio = output_size / input_size if input_size > 0 else 0

        return {
            "input_path": input_path,
            "output_path": output_path,
            "input_size_bytes": input_size,
            "output_size_bytes": output_size,
            "compression_ratio": round(compression_ratio, 3),
            "space_saved_bytes": input_size - output_size,
            "compression_percent": round((1 - compression_ratio) * 100, 1),
            "compression_type": "xz/lzma",
            "compression_status": "success",
        }

    except Exception as e:
        raise BasicAgentToolsError(f"Failed to compress file with XZ: {str(e)}")
