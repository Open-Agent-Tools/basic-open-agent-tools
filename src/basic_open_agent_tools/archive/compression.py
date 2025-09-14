"""ZIP compression utilities."""

import os
import zipfile
from typing import Dict, List, Union

try:
    from strands import tool as strands_tool
except ImportError:
    def strands_tool(func):
        return func

from ..exceptions import BasicAgentToolsError


@strands_tool
def create_zip(source_paths: List[str], output_path: str) -> Dict[str, Union[str, int, List[str]]]:
    """Create a ZIP archive from files and directories."""
    if not isinstance(source_paths, list) or not source_paths:
        raise BasicAgentToolsError("Source paths must be a non-empty list")

    if not isinstance(output_path, str) or not output_path.strip():
        raise BasicAgentToolsError("Output path must be a non-empty string")

    try:
        files_added = []
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for source_path in source_paths:
                if os.path.isfile(source_path):
                    zf.write(source_path, os.path.basename(source_path))
                    files_added.append(source_path)
                elif os.path.isdir(source_path):
                    for root, dirs, files in os.walk(source_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_name = os.path.relpath(file_path, os.path.dirname(source_path))
                            zf.write(file_path, arc_name)
                            files_added.append(file_path)

        return {
            "output_path": output_path,
            "files_added": len(files_added),
            "file_size_bytes": os.path.getsize(output_path),
            "status": "success"
        }
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to create ZIP archive: {str(e)}")


@strands_tool
def extract_zip(zip_path: str, extract_to: str) -> Dict[str, Union[str, int]]:
    """Extract a ZIP archive to a directory."""
    if not isinstance(zip_path, str) or not zip_path.strip():
        raise BasicAgentToolsError("ZIP path must be a non-empty string")

    if not os.path.exists(zip_path):
        raise BasicAgentToolsError(f"ZIP file not found: {zip_path}")

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_to)
            files_extracted = len(zf.namelist())

        return {
            "zip_path": zip_path,
            "extract_to": extract_to,
            "files_extracted": files_extracted,
            "status": "success"
        }
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to extract ZIP archive: {str(e)}")


@strands_tool
def compress_files(file_paths: List[str], output_path: str) -> Dict[str, Union[str, int]]:
    """Compress multiple files into a ZIP archive."""
    return create_zip(file_paths, output_path)
