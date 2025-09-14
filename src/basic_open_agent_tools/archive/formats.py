"""TAR archive format utilities."""

import os
import tarfile
from typing import Any, Callable, Union

try:
    from strands import tool as strands_tool
except ImportError:

    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        return func


from ..exceptions import BasicAgentToolsError


@strands_tool
def create_tar(
    source_paths: list[str], output_path: str, compression: str = "gzip"
) -> dict[str, Union[str, int]]:
    """Create a TAR archive from files and directories."""
    if not isinstance(source_paths, list) or not source_paths:
        raise BasicAgentToolsError("Source paths must be a non-empty list")

    if compression not in ["none", "gzip", "bzip2"]:
        raise BasicAgentToolsError("Compression must be 'none', 'gzip', or 'bzip2'")

    try:
        mode_map = {"none": "w", "gzip": "w:gz", "bzip2": "w:bz2"}
        mode = mode_map[compression]

        with tarfile.open(output_path, mode) as tf:
            for source_path in source_paths:
                tf.add(source_path, arcname=os.path.basename(source_path))

        return {
            "output_path": output_path,
            "compression": compression,
            "file_size_bytes": os.path.getsize(output_path),
            "status": "success",
        }
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to create TAR archive: {str(e)}")


@strands_tool
def extract_tar(tar_path: str, extract_to: str) -> dict[str, Union[str, int]]:
    """Extract a TAR archive to a directory."""
    if not os.path.exists(tar_path):
        raise BasicAgentToolsError(f"TAR file not found: {tar_path}")

    try:
        with tarfile.open(tar_path, "r:*") as tf:
            tf.extractall(extract_to)
            files_extracted = len(tf.getnames())

        return {
            "tar_path": tar_path,
            "extract_to": extract_to,
            "files_extracted": files_extracted,
            "status": "success",
        }
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to extract TAR archive: {str(e)}")
