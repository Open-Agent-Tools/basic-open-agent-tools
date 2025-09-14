"""Log rotation utilities."""

import glob
import logging.handlers
import os
from typing import Any, Callable, Union

try:
    from strands import tool as strands_tool
except ImportError:

    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        return func


from ..exceptions import BasicAgentToolsError


@strands_tool
def setup_rotating_log(
    logger_name: str,
    log_file: str,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5,
) -> dict[str, Union[str, int]]:
    """Set up a rotating file handler for a logger."""
    try:
        logger = logging.getLogger(logger_name)
        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return {
            "logger_name": logger_name,
            "log_file": log_file,
            "max_bytes": max_bytes,
            "backup_count": backup_count,
            "status": "configured",
        }
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to setup rotating log: {str(e)}")


@strands_tool
def cleanup_old_logs(
    log_pattern: str, keep_count: int = 5
) -> dict[str, Union[str, int]]:
    """Clean up old log files matching a pattern."""
    try:
        log_files = sorted(glob.glob(log_pattern), key=os.path.getmtime, reverse=True)
        files_to_delete = log_files[keep_count:]
        deleted_count = 0

        for file_path in files_to_delete:
            os.remove(file_path)
            deleted_count += 1

        return {
            "log_pattern": log_pattern,
            "files_found": len(log_files),
            "files_deleted": deleted_count,
            "files_kept": len(log_files) - deleted_count,
            "status": "completed",
        }
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to cleanup old logs: {str(e)}")
