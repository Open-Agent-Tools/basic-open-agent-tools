"""Log file parsing and inspection tools for AI agents."""

import json
import random
import re
from typing import Any, Optional

from ..decorators import strands_tool


def _parse_json_log_line(line: str) -> Optional[dict[str, Any]]:
    """Parse a JSON log line."""
    try:
        return json.loads(line.strip())  # type: ignore[no-any-return]
    except (json.JSONDecodeError, ValueError):
        return None


def _parse_syslog_line(line: str) -> Optional[dict[str, str]]:
    """Parse a syslog format line."""
    # Format: <timestamp> <hostname> <process>[<pid>]: <message>
    pattern = r"^(\w+\s+\d+\s+\d+:\d+:\d+)\s+(\S+)\s+(\S+?)(?:\[(\d+)\])?:\s+(.+)$"
    match = re.match(pattern, line)
    if match:
        return {
            "timestamp": match.group(1),
            "hostname": match.group(2),
            "process": match.group(3),
            "pid": match.group(4) or "",
            "message": match.group(5),
        }
    return None


def _parse_common_log_line(line: str) -> Optional[dict[str, str]]:
    """Parse common log format (CLF) line."""
    # Format: host ident authuser date request status bytes
    pattern = r'^(\S+) (\S+) (\S+) \[([^\]]+)\] "([^"]+)" (\d+) (\S+)'
    match = re.match(pattern, line)
    if match:
        return {
            "host": match.group(1),
            "ident": match.group(2),
            "authuser": match.group(3),
            "timestamp": match.group(4),
            "request": match.group(5),
            "status": match.group(6),
            "bytes": match.group(7),
        }
    return None


def _parse_keyvalue_log_line(line: str) -> Optional[dict[str, str]]:
    """Parse key=value format log line."""
    # Format: key1=value1 key2=value2 ...
    pattern = r"(\w+)=(?:\"([^\"]*)\"|([^\s]*))"
    matches = re.findall(pattern, line)
    if matches:
        result = {}
        for key, quoted_val, unquoted_val in matches:
            result[key] = quoted_val if quoted_val else unquoted_val
        return result
    return None


def _detect_format(line: str) -> str:
    """Detect log format from a sample line."""
    if line.strip().startswith("{"):
        return "json"
    elif _parse_syslog_line(line):
        return "syslog"
    elif _parse_common_log_line(line):
        return "clf"
    elif _parse_keyvalue_log_line(line):
        return "keyvalue"
    return "plain"


@strands_tool
def detect_log_format(file_path: str, sample_lines: int) -> str:
    """Auto-detect log format from sample lines.

    Analyzes first N lines of log file to determine format. Supports JSON,
    syslog, common log format (CLF), key=value, and plain text.

    Args:
        file_path: Path to log file
        sample_lines: Number of lines to analyze for format detection

    Returns:
        Format name: "json", "syslog", "clf", "keyvalue", or "plain"

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file cannot be read

    Example:
        >>> detect_log_format("app.log", 5)
        "json"
        >>> detect_log_format("syslog.log", 10)
        "syslog"
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(sample_lines, int):
        raise TypeError("sample_lines must be an integer")

    try:
        formats: dict[str, int] = {}
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            for _ in range(sample_lines):
                line = f.readline()
                if not line:
                    break
                format_type = _detect_format(line)
                formats[format_type] = formats.get(format_type, 0) + 1

        # Return most common format
        if formats:
            return max(formats.items(), key=lambda x: x[1])[0]
        return "plain"

    except FileNotFoundError:
        raise FileNotFoundError(f"Log file not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Failed to detect log format: {e}")


@strands_tool
def parse_log_entries(
    file_path: str, log_format: str, max_entries: int
) -> list[dict[str, str]]:
    """Parse log file entries into structured format.

    Reads log file and parses entries according to specified format. Returns
    structured data without loading entire file.

    Args:
        file_path: Path to log file
        log_format: Format type ("json", "syslog", "clf", "keyvalue", "plain")
        max_entries: Maximum number of entries to parse (-1 for all)

    Returns:
        List of dictionaries representing parsed log entries

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If format is invalid or file cannot be parsed
        FileNotFoundError: If file doesn't exist

    Example:
        >>> parse_log_entries("app.log", "json", 100)
        [{"level": "ERROR", "message": "Connection failed", "timestamp": "..."}]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(log_format, str):
        raise TypeError("log_format must be a string")
    if not isinstance(max_entries, int):
        raise TypeError("max_entries must be an integer")

    valid_formats = ["json", "syslog", "clf", "keyvalue", "plain"]
    if log_format not in valid_formats:
        raise ValueError(f"log_format must be one of {valid_formats}")

    try:
        entries = []
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f):
                if max_entries != -1 and i >= max_entries:
                    break

                line = line.strip()
                if not line:
                    continue

                if log_format == "json":
                    parsed = _parse_json_log_line(line)
                elif log_format == "syslog":
                    parsed = _parse_syslog_line(line)
                elif log_format == "clf":
                    parsed = _parse_common_log_line(line)
                elif log_format == "keyvalue":
                    parsed = _parse_keyvalue_log_line(line)
                else:  # plain
                    parsed = {"line": line}

                if parsed:
                    # Convert any non-string values to strings for JSON serialization
                    str_parsed = {k: str(v) for k, v in parsed.items()}
                    entries.append(str_parsed)

        return entries

    except FileNotFoundError:
        raise FileNotFoundError(f"Log file not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Failed to parse log entries: {e}")


@strands_tool
def filter_log_entries(
    file_path: str,
    log_format: str,
    filter_field: str,
    filter_value: str,
    max_results: int,
) -> list[dict[str, str]]:
    """Filter log entries by field value without loading entire file.

    Streams through log file and returns only entries where specified field
    matches value. Case-insensitive substring match.

    Args:
        file_path: Path to log file
        log_format: Format type ("json", "syslog", "clf", "keyvalue", "plain")
        filter_field: Field name to filter on
        filter_value: Value to match (case-insensitive substring)
        max_results: Maximum number of results (-1 for all)

    Returns:
        List of matching log entries

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If format is invalid or file cannot be parsed
        FileNotFoundError: If file doesn't exist

    Example:
        >>> filter_log_entries("app.log", "json", "level", "ERROR", 50)
        [{"level": "ERROR", "message": "Database connection timeout"}]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(log_format, str):
        raise TypeError("log_format must be a string")
    if not isinstance(filter_field, str):
        raise TypeError("filter_field must be a string")
    if not isinstance(filter_value, str):
        raise TypeError("filter_value must be a string")
    if not isinstance(max_results, int):
        raise TypeError("max_results must be an integer")

    # Parse all entries then filter
    all_entries = parse_log_entries(file_path, log_format, -1)

    filter_lower = filter_value.lower()
    results: list[dict[str, str]] = []

    for entry in all_entries:
        if max_results != -1 and len(results) >= max_results:
            break

        if filter_field in entry:
            if filter_lower in entry[filter_field].lower():
                results.append(entry)

    return results


@strands_tool
def get_log_errors(
    file_path: str, log_format: str, max_errors: int
) -> list[dict[str, str]]:
    """Extract ERROR and CRITICAL level entries from log file.

    Specialized filter for error-level logs. Searches for ERROR, CRITICAL,
    FATAL in common log level fields.

    Args:
        file_path: Path to log file
        log_format: Format type ("json", "syslog", "clf", "keyvalue", "plain")
        max_errors: Maximum number of errors to return (-1 for all)

    Returns:
        List of error-level log entries

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If format is invalid or file cannot be parsed
        FileNotFoundError: If file doesn't exist

    Example:
        >>> get_log_errors("app.log", "json", 10)
        [{"level": "ERROR", "message": "Connection timeout", "timestamp": "..."}]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(log_format, str):
        raise TypeError("log_format must be a string")
    if not isinstance(max_errors, int):
        raise TypeError("max_errors must be an integer")

    # Parse all entries
    all_entries = parse_log_entries(file_path, log_format, -1)

    errors: list[dict[str, str]] = []
    error_levels = ["error", "critical", "fatal"]

    for entry in all_entries:
        if max_errors != -1 and len(errors) >= max_errors:
            break

        # Check common level field names
        found_level = False
        for level_field in ["level", "severity", "loglevel", "priority"]:
            if level_field in entry:
                if entry[level_field].lower() in error_levels:
                    errors.append(entry)
                    found_level = True
                    break

        # Also check if message contains error keywords
        if not found_level and "message" in entry:
            msg_lower = entry["message"].lower()
            if any(
                keyword in msg_lower for keyword in ["error:", "critical:", "fatal:"]
            ):
                errors.append(entry)

    return errors


@strands_tool
def search_log_messages(
    file_path: str, log_format: str, search_pattern: str, max_results: int
) -> list[dict[str, str]]:
    """Search for pattern in log messages using regex.

    Searches log entries for messages matching regex pattern. More flexible
    than simple filtering.

    Args:
        file_path: Path to log file
        log_format: Format type ("json", "syslog", "clf", "keyvalue", "plain")
        search_pattern: Regex pattern to search for
        max_results: Maximum number of results (-1 for all)

    Returns:
        List of log entries with matching messages

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If format/pattern is invalid or file cannot be parsed
        FileNotFoundError: If file doesn't exist

    Example:
        >>> search_log_messages("app.log", "json", "timeout|failed", 20)
        [{"message": "Connection timeout after 30s", "level": "ERROR"}]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(log_format, str):
        raise TypeError("log_format must be a string")
    if not isinstance(search_pattern, str):
        raise TypeError("search_pattern must be a string")
    if not isinstance(max_results, int):
        raise TypeError("max_results must be an integer")

    try:
        pattern = re.compile(search_pattern, re.IGNORECASE)
    except re.error as e:
        raise ValueError(f"Invalid regex pattern: {e}")

    # Parse all entries
    all_entries = parse_log_entries(file_path, log_format, -1)

    results: list[dict[str, str]] = []

    for entry in all_entries:
        if max_results != -1 and len(results) >= max_results:
            break

        # Search in message field or line field
        for msg_field in ["message", "msg", "line", "text"]:
            if msg_field in entry:
                if pattern.search(entry[msg_field]):
                    results.append(entry)
                    break

    return results


@strands_tool
def get_log_summary(file_path: str, log_format: str) -> dict[str, str]:
    """Get summary statistics for log file without loading all entries.

    Analyzes log file and returns counts by level, total entries, and time
    range information.

    Args:
        file_path: Path to log file
        log_format: Format type ("json", "syslog", "clf", "keyvalue", "plain")

    Returns:
        Dictionary with summary statistics

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If format is invalid or file cannot be parsed
        FileNotFoundError: If file doesn't exist

    Example:
        >>> get_log_summary("app.log", "json")
        {
            "total_entries": "1523",
            "error_count": "45",
            "warning_count": "128",
            "info_count": "1350",
            "has_timestamps": "true"
        }
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(log_format, str):
        raise TypeError("log_format must be a string")

    # Parse all entries
    all_entries = parse_log_entries(file_path, log_format, -1)

    level_counts: dict[str, int] = {}
    has_timestamps = False

    for entry in all_entries:
        # Count by level
        for level_field in ["level", "severity", "loglevel", "priority"]:
            if level_field in entry:
                level = entry[level_field].lower()
                level_counts[level] = level_counts.get(level, 0) + 1

        # Check for timestamps
        if any(key in entry for key in ["timestamp", "time", "date", "datetime"]):
            has_timestamps = True

    # Convert to string values
    summary = {
        "total_entries": str(len(all_entries)),
        "has_timestamps": str(has_timestamps).lower(),
    }

    # Add level counts
    for level, count in level_counts.items():
        summary[f"{level}_count"] = str(count)

    return summary


@strands_tool
def sample_log_entries(
    file_path: str, log_format: str, sample_size: int, method: str
) -> list[dict[str, str]]:
    """Get representative sample of log entries without loading all.

    Samples log file using specified method: first N entries, random sample,
    or systematic sampling (evenly spaced).

    Args:
        file_path: Path to log file
        log_format: Format type ("json", "syslog", "clf", "keyvalue", "plain")
        sample_size: Number of entries to sample
        method: Sampling method ("first", "random", "systematic")

    Returns:
        List of sampled log entries

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If format/method is invalid or file cannot be parsed
        FileNotFoundError: If file doesn't exist

    Example:
        >>> sample_log_entries("app.log", "json", 50, "random")
        [{"level": "INFO", "message": "Request processed"}]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(log_format, str):
        raise TypeError("log_format must be a string")
    if not isinstance(sample_size, int):
        raise TypeError("sample_size must be an integer")
    if not isinstance(method, str):
        raise TypeError("method must be a string")

    valid_methods = ["first", "random", "systematic"]
    if method not in valid_methods:
        raise ValueError(f"method must be one of {valid_methods}")

    if method == "first":
        return parse_log_entries(file_path, log_format, sample_size)  # type: ignore[no-any-return]

    # For random and systematic, need all entries
    all_entries = parse_log_entries(file_path, log_format, -1)

    if len(all_entries) <= sample_size:
        return all_entries  # type: ignore[no-any-return]

    if method == "random":
        return random.sample(all_entries, sample_size)  # type: ignore[no-any-return]

    # Systematic sampling
    step = len(all_entries) // sample_size
    return [all_entries[i * step] for i in range(sample_size)]  # type: ignore[no-any-return]


@strands_tool
def get_log_time_range(file_path: str, log_format: str) -> dict[str, str]:
    """Get earliest and latest timestamps from log file.

    Scans log file to find time range covered by entries. Useful for
    understanding log coverage without loading all data.

    Args:
        file_path: Path to log file
        log_format: Format type ("json", "syslog", "clf", "keyvalue", "plain")

    Returns:
        Dictionary with earliest and latest timestamp strings

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If format is invalid or file cannot be parsed
        FileNotFoundError: If file doesn't exist

    Example:
        >>> get_log_time_range("app.log", "json")
        {
            "earliest": "2024-01-15 08:00:00",
            "latest": "2024-01-15 18:30:45",
            "entries_with_timestamps": "1523"
        }
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(log_format, str):
        raise TypeError("log_format must be a string")

    # Parse all entries
    all_entries = parse_log_entries(file_path, log_format, -1)

    timestamps = []
    timestamp_fields = ["timestamp", "time", "date", "datetime", "ts"]

    for entry in all_entries:
        for field in timestamp_fields:
            if field in entry:
                timestamps.append(entry[field])
                break

    if not timestamps:
        return {
            "earliest": "no timestamps found",
            "latest": "no timestamps found",
            "entries_with_timestamps": "0",
        }

    return {
        "earliest": min(timestamps),
        "latest": max(timestamps),
        "entries_with_timestamps": str(len(timestamps)),
    }


@strands_tool
def count_log_entries(
    file_path: str, log_format: str, filter_field: str, filter_value: str
) -> int:
    """Count log entries with optional filtering.

    Counts matching log entries without loading all into memory. If filter
    parameters provided, counts only matching entries.

    Args:
        file_path: Path to log file
        log_format: Format type ("json", "syslog", "clf", "keyvalue", "plain")
        filter_field: Field name to filter on (empty string for no filter)
        filter_value: Value to match (empty string for no filter)

    Returns:
        Count of matching entries

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If format is invalid or file cannot be parsed
        FileNotFoundError: If file doesn't exist

    Example:
        >>> count_log_entries("app.log", "json", "level", "ERROR")
        145
        >>> count_log_entries("app.log", "json", "", "")
        1523
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(log_format, str):
        raise TypeError("log_format must be a string")
    if not isinstance(filter_field, str):
        raise TypeError("filter_field must be a string")
    if not isinstance(filter_value, str):
        raise TypeError("filter_value must be a string")

    # Parse all entries
    all_entries = parse_log_entries(file_path, log_format, -1)

    # No filter
    if not filter_field or not filter_value:
        return len(all_entries)

    # With filter
    count = 0
    filter_lower = filter_value.lower()

    for entry in all_entries:
        if filter_field in entry:
            if filter_lower in entry[filter_field].lower():
                count += 1

    return count


@strands_tool
def extract_log_fields(
    file_path: str, log_format: str, field_names: list[str], max_entries: int
) -> list[dict[str, str]]:
    """Extract specific fields from log entries.

    Parses log file and returns only specified fields from each entry.
    More memory-efficient than loading all fields.

    Args:
        file_path: Path to log file
        log_format: Format type ("json", "syslog", "clf", "keyvalue", "plain")
        field_names: List of field names to extract
        max_entries: Maximum number of entries to process (-1 for all)

    Returns:
        List of dictionaries with only specified fields

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If format is invalid or file cannot be parsed
        FileNotFoundError: If file doesn't exist

    Example:
        >>> extract_log_fields("app.log", "json", ["timestamp", "level", "message"], 100)
        [{"timestamp": "...", "level": "ERROR", "message": "Connection failed"}]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(log_format, str):
        raise TypeError("log_format must be a string")
    if not isinstance(field_names, list):
        raise TypeError("field_names must be a list")
    if not isinstance(max_entries, int):
        raise TypeError("max_entries must be an integer")

    # Parse entries
    all_entries = parse_log_entries(file_path, log_format, max_entries)

    # Extract only specified fields
    result = []
    for entry in all_entries:
        extracted = {}
        for field in field_names:
            if field in entry:
                extracted[field] = entry[field]
        if extracted:  # Only include if at least one field was found
            result.append(extracted)

    return result
