"""Logging utilities for agents."""

from .parsing import (
    count_log_entries,
    detect_log_format,
    extract_log_fields,
    filter_log_entries,
    get_log_errors,
    get_log_summary,
    get_log_time_range,
    parse_log_entries,
    sample_log_entries,
    search_log_messages,
)
from .rotation import cleanup_old_logs, setup_rotating_log
from .structured import configure_logger, log_error, log_info

__all__ = [
    # Structured logging (3)
    "log_info",
    "log_error",
    "configure_logger",
    # Log rotation (2)
    "setup_rotating_log",
    "cleanup_old_logs",
    # Log parsing and inspection (10 token-saving tools)
    "detect_log_format",
    "parse_log_entries",
    "filter_log_entries",
    "get_log_errors",
    "search_log_messages",
    "get_log_summary",
    "sample_log_entries",
    "get_log_time_range",
    "count_log_entries",
    "extract_log_fields",
]
