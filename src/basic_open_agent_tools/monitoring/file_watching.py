"""File and directory monitoring utilities."""

import os
import time
from typing import Dict, List, Union

try:
    from strands import tool as strands_tool
except ImportError:
    def strands_tool(func):
        return func

from ..exceptions import BasicAgentToolsError


@strands_tool
def watch_file_changes(file_path: str, check_interval: int = 1) -> Dict[str, Union[str, float, bool]]:
    """Watch a file for changes."""
    if not isinstance(file_path, str) or not file_path.strip():
        raise BasicAgentToolsError("File path must be a non-empty string")

    if not os.path.exists(file_path):
        raise BasicAgentToolsError(f"File not found: {file_path}")

    try:
        initial_stat = os.stat(file_path)
        initial_mtime = initial_stat.st_mtime
        initial_size = initial_stat.st_size

        time.sleep(check_interval)

        current_stat = os.stat(file_path)
        current_mtime = current_stat.st_mtime
        current_size = current_stat.st_size

        has_changed = (current_mtime != initial_mtime) or (current_size != initial_size)

        return {
            "file_path": file_path,
            "initial_modified_time": initial_mtime,
            "current_modified_time": current_mtime,
            "initial_size": initial_size,
            "current_size": current_size,
            "has_changed": has_changed,
            "check_interval_seconds": check_interval
        }
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to watch file changes: {str(e)}")


@strands_tool
def monitor_directory(directory_path: str) -> Dict[str, Union[str, int, List[str]]]:
    """Monitor a directory for files and changes."""
    if not isinstance(directory_path, str) or not directory_path.strip():
        raise BasicAgentToolsError("Directory path must be a non-empty string")

    if not os.path.exists(directory_path):
        raise BasicAgentToolsError(f"Directory not found: {directory_path}")

    if not os.path.isdir(directory_path):
        raise BasicAgentToolsError(f"Path is not a directory: {directory_path}")

    try:
        files = []
        total_size = 0

        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isfile(item_path):
                stat = os.stat(item_path)
                files.append({
                    "name": item,
                    "size": stat.st_size,
                    "modified_time": stat.st_mtime
                })
                total_size += stat.st_size

        return {
            "directory_path": directory_path,
            "file_count": len(files),
            "total_size_bytes": total_size,
            "files": files,
            "scan_timestamp": time.time()
        }
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to monitor directory: {str(e)}")
