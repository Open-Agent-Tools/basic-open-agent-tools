"""TAR archive format utilities."""

import os
import tarfile
from typing import Union

from .._logging import get_logger
from ..confirmation import check_user_confirmation
from ..decorators import strands_tool
from ..exceptions import BasicAgentToolsError
from .compression import _generate_archive_preview

logger = get_logger("archive.formats")


@strands_tool
def create_tar(
    source_paths: list[str], output_path: str, compression: str, skip_confirm: bool
) -> str:
    """Create a TAR archive from files and directories with permission checking.

    Args:
        source_paths: List of file/directory paths to include in archive
        output_path: Path for the output TAR file
        compression: Compression type ('none', 'gzip', or 'bzip2')
        skip_confirm: If True, skip confirmation and overwrite existing files. IMPORTANT: Agents should default to skip_confirm=False for safety.

    Returns:
        String describing the operation result

    Raises:
        BasicAgentToolsError: If archive creation fails or file exists without skip_confirm
    """
    if not isinstance(source_paths, list) or not source_paths:
        raise BasicAgentToolsError("Source paths must be a non-empty list")

    if compression not in ["none", "gzip", "bzip2"]:
        raise BasicAgentToolsError("Compression must be 'none', 'gzip', or 'bzip2'")

    if not isinstance(skip_confirm, bool):
        raise BasicAgentToolsError("skip_confirm must be a boolean")

    # Check if output file exists
    file_existed = os.path.exists(output_path)

    logger.info(
        f"Creating TAR: {output_path} from {len(source_paths)} source(s), compression={compression}"
    )
    logger.debug(f"skip_confirm: {skip_confirm}, file_existed: {file_existed}")

    if file_existed:
        # Check user confirmation - show preview of NEW archive being created
        preview = _generate_archive_preview(source_paths)
        confirmed = check_user_confirmation(
            operation="overwrite existing TAR archive",
            target=output_path,
            skip_confirm=skip_confirm,
            preview_info=preview,
        )

        if not confirmed:
            logger.debug(f"TAR creation cancelled by user: {output_path}")
            return f"Operation cancelled by user: {output_path}"

    try:
        mode_map = {"none": "w", "gzip": "w:gz", "bzip2": "w:bz2"}
        mode = mode_map[compression]

        files_added = 0
        with tarfile.open(output_path, mode) as tf:  # type: ignore[call-overload]
            for source_path in source_paths:
                tf.add(source_path, arcname=os.path.basename(source_path))
                files_added += 1

        # Calculate stats for feedback
        file_size = os.path.getsize(output_path)
        action = "Overwrote" if file_existed else "Created"

        result = f"{action} TAR archive {output_path} with {files_added} items using {compression} compression ({file_size} bytes)"
        logger.info(
            f"TAR created successfully: {files_added} items, {file_size} bytes ({action.lower()})"
        )
        return result
    except Exception as e:
        logger.error(f"TAR creation failed: {e}")
        raise BasicAgentToolsError(f"Failed to create TAR archive: {str(e)}")


@strands_tool
def extract_tar(tar_path: str, extract_to: str) -> dict[str, Union[str, int]]:
    """Extract a TAR archive to a directory."""
    if not os.path.exists(tar_path):
        logger.debug(f"TAR file not found: {tar_path}")
        raise BasicAgentToolsError(f"TAR file not found: {tar_path}")

    archive_size = os.path.getsize(tar_path)
    logger.info(f"Extracting TAR: {tar_path} → {extract_to} ({archive_size} bytes)")

    try:
        with tarfile.open(tar_path, "r:*") as tf:
            tf.extractall(extract_to)
            files_extracted = len(tf.getnames())

        result = {
            "tar_path": tar_path,
            "extract_to": extract_to,
            "files_extracted": files_extracted,
            "status": "success",
        }

        logger.info(f"TAR extracted successfully: {files_extracted} files")
        return result  # type: ignore[return-value]
    except Exception as e:
        logger.error(f"TAR extraction failed: {e}")
        raise BasicAgentToolsError(f"Failed to extract TAR archive: {str(e)}")
