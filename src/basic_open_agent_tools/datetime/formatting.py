"""Human-readable date, time, and duration formatting for AI agents.

This module provides functions to format dates, times, and durations in
user-friendly formats that are easy to read and understand.
"""

import re
from datetime import date, time

from ..decorators import strands_tool


@strands_tool
def format_date_human_readable(date_string: str) -> str:
    """Convert ISO date to human-readable format.

    Converts an ISO format date (YYYY-MM-DD) to a human-readable format
    like "January 15, 2025". Agents can use this to present dates to users
    in a friendly format.

    Args:
        date_string: The date string in ISO format (YYYY-MM-DD)

    Returns:
        Human-readable date string (e.g., "January 15, 2025")

    Raises:
        TypeError: If date_string is not a string
        ValueError: If date_string is not a valid ISO format date

    Example:
        >>> result = format_date_human_readable("2025-01-15")
        >>> result
        "January 15, 2025"
        >>> result = format_date_human_readable("2025-12-31")
        >>> result
        "December 31, 2025"
    """
    if not isinstance(date_string, str):
        raise TypeError("date_string must be a string")

    try:
        parsed_date = date.fromisoformat(date_string)
        return parsed_date.strftime("%B %d, %Y")
    except ValueError as e:
        raise ValueError(f"Invalid ISO date format '{date_string}': {e}")


@strands_tool
def format_time_human_readable(time_string: str) -> str:
    """Convert ISO time to human-readable format.

    Converts an ISO format time (HH:MM:SS) to a human-readable 12-hour format
    like "2:30 PM". Agents can use this to present times to users in a
    familiar format.

    Args:
        time_string: The time string in ISO format (HH:MM:SS or HH:MM:SS.ffffff)

    Returns:
        Human-readable time string (e.g., "2:30 PM")

    Raises:
        TypeError: If time_string is not a string
        ValueError: If time_string is not a valid ISO format time

    Example:
        >>> result = format_time_human_readable("14:30:00")
        >>> result
        "2:30 PM"
        >>> result = format_time_human_readable("09:15:30")
        >>> result
        "9:15 AM"
    """
    if not isinstance(time_string, str):
        raise TypeError("time_string must be a string")

    try:
        parsed_time = time.fromisoformat(time_string)
        return parsed_time.strftime("%I:%M %p").lstrip("0")
    except ValueError as e:
        raise ValueError(f"Invalid ISO time format '{time_string}': {e}")


@strands_tool
def format_duration(seconds: int, format_type: str) -> str:
    """Format duration (in seconds) into human-readable string.

    Converts a duration in seconds to a human-readable format.
    Supports three format types: verbose, short, and compact.

    Args:
        seconds: The duration in seconds (must be non-negative)
        format_type: The output format ("verbose", "short", or "compact")

    Returns:
        Formatted duration string based on format_type:
        - verbose: "2 hours 1 minute 5 seconds"
        - short: "2h 1m 5s"
        - compact: "2:01:05"

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If seconds is negative or format_type is invalid

    Example:
        >>> result = format_duration(7265, "verbose")
        >>> result
        "2 hours 1 minute 5 seconds"
        >>> result = format_duration(7265, "short")
        >>> result
        "2h 1m 5s"
        >>> result = format_duration(7265, "compact")
        >>> result
        "2:01:05"
    """
    if not isinstance(seconds, int):
        raise TypeError("seconds must be an integer")
    if not isinstance(format_type, str):
        raise TypeError("format_type must be a string")

    if seconds < 0:
        raise ValueError("seconds must be non-negative")

    if format_type not in ["verbose", "short", "compact"]:
        raise ValueError("format_type must be 'verbose', 'short', or 'compact'")

    # Calculate components
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if format_type == "verbose":
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if secs > 0 or not parts:
            parts.append(f"{secs} second{'s' if secs != 1 else ''}")
        return " ".join(parts)

    elif format_type == "short":
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
        return " ".join(parts)

    else:  # compact
        if days > 0:
            return f"{days}:{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{hours}:{minutes:02d}:{secs:02d}"


@strands_tool
def parse_duration_string(duration_string: str) -> int:
    """Parse human-readable duration string to seconds.

    Converts various duration string formats to total seconds.
    Supports formats like "2 hours 30 minutes", "2h 30m", "1 day 3 hours", etc.

    Args:
        duration_string: The duration string to parse

    Returns:
        Total duration in seconds

    Raises:
        TypeError: If duration_string is not a string
        ValueError: If duration_string is not a valid duration format

    Example:
        >>> result = parse_duration_string("2 hours 30 minutes")
        >>> result
        9000
        >>> result = parse_duration_string("2h 30m")
        >>> result
        9000
        >>> result = parse_duration_string("1 day 3 hours 15 minutes")
        >>> result
        97500
    """
    if not isinstance(duration_string, str):
        raise TypeError("duration_string must be a string")

    duration_string = duration_string.lower().strip()

    if not duration_string:
        raise ValueError("duration_string cannot be empty")

    total_seconds: float = 0

    # Pattern for matching duration components
    # Matches: "2 days", "2d", "1.5 hours", "1.5h", etc.
    pattern = r"([\d.]+)\s*(days?|d|hours?|h|minutes?|m|seconds?|s)"

    matches = re.findall(pattern, duration_string)

    if not matches:
        raise ValueError(
            f"No valid duration components found in '{duration_string}'. "
            "Expected format like '2 hours 30 minutes' or '2h 30m'"
        )

    for value_str, unit in matches:
        try:
            value = float(value_str)
        except ValueError:
            raise ValueError(f"Invalid numeric value '{value_str}' in duration string")

        # Normalize units
        if unit in ["days", "day", "d"]:
            total_seconds += value * 86400
        elif unit in ["hours", "hour", "h"]:
            total_seconds += value * 3600
        elif unit in ["minutes", "minute", "m"]:
            total_seconds += value * 60
        elif unit in ["seconds", "second", "s"]:
            total_seconds += value
        else:
            raise ValueError(f"Unknown unit '{unit}' in duration string")

    return int(total_seconds)
