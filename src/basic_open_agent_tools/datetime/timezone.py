"""Timezone operations for AI agents.

This module provides timezone conversion and information utilities using ISO format
strings and standard timezone names.
"""

from datetime import datetime
from typing import Any, Callable

try:
    import zoneinfo
except ImportError:
    import pytz as zoneinfo  # type: ignore

try:
    from strands import tool as strands_tool
except ImportError:
    # Create a no-op decorator if strands is not installed
    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]  # type: ignore
        return func


@strands_tool
def convert_timezone(datetime_string: str, from_timezone: str, to_timezone: str) -> str:
    """Convert a datetime from one timezone to another.

    Takes a datetime string with timezone and converts it to a different timezone.

    Args:
        datetime_string: The datetime string in ISO format (YYYY-MM-DDTHH:MM:SS)
        from_timezone: The source timezone name (e.g., "UTC", "America/New_York")
        to_timezone: The target timezone name (e.g., "UTC", "Europe/London")

    Returns:
        The datetime string in the target timezone in ISO format

    Raises:
        TypeError: If any parameter is not a string
        ValueError: If datetime_string is invalid or timezone names are not valid

    Example:
        >>> result = convert_timezone("2025-07-08T14:30:45", "UTC", "America/New_York")
        >>> result
        "2025-07-08T10:30:45-04:00"
    """
    if not isinstance(datetime_string, str):
        raise TypeError("datetime_string must be a string")
    if not isinstance(from_timezone, str):
        raise TypeError("from_timezone must be a string")
    if not isinstance(to_timezone, str):
        raise TypeError("to_timezone must be a string")

    try:
        from_tz = zoneinfo.ZoneInfo(from_timezone)
        to_tz = zoneinfo.ZoneInfo(to_timezone)

        # Parse datetime and localize to source timezone
        dt = datetime.fromisoformat(datetime_string)
        dt_localized = dt.replace(tzinfo=from_tz)

        # Convert to target timezone
        dt_converted = dt_localized.astimezone(to_tz)

        return dt_converted.isoformat()
    except Exception as e:
        raise ValueError(f"Timezone conversion failed: {e}")


@strands_tool
def get_timezone_offset(timezone: str) -> str:
    """Get the current UTC offset for a timezone.

    Returns the current UTC offset for the specified timezone as a string.

    Args:
        timezone: The timezone name (e.g., "UTC", "America/New_York", "Europe/London")

    Returns:
        The UTC offset as a string (e.g., "+00:00", "-05:00", "+01:00")

    Raises:
        TypeError: If timezone is not a string
        ValueError: If timezone is not a valid timezone name

    Example:
        >>> result = get_timezone_offset("America/New_York")
        >>> result
        "-05:00"
    """
    if not isinstance(timezone, str):
        raise TypeError("timezone must be a string")

    try:
        tz = zoneinfo.ZoneInfo(timezone)
        now = datetime.now(tz)
        offset = now.strftime("%z")

        # Format as +HH:MM or -HH:MM
        if len(offset) == 5:  # +HHMM format
            return f"{offset[:3]}:{offset[3:]}"
        return offset
    except Exception as e:
        raise ValueError(f"Invalid timezone '{timezone}': {e}")


@strands_tool
def is_daylight_saving_time(datetime_string: str, timezone: str) -> bool:
    """Check if daylight saving time is in effect for a datetime in a timezone.

    Args:
        datetime_string: The datetime string in ISO format (YYYY-MM-DDTHH:MM:SS)
        timezone: The timezone name (e.g., "America/New_York", "Europe/London")

    Returns:
        True if daylight saving time is in effect, False otherwise

    Raises:
        TypeError: If datetime_string or timezone is not a string
        ValueError: If datetime_string is invalid or timezone is not valid

    Example:
        >>> result = is_daylight_saving_time("2025-07-08T14:30:45", "America/New_York")
        >>> result
        True
        >>> result = is_daylight_saving_time("2025-01-08T14:30:45", "America/New_York")
        >>> result
        False
    """
    if not isinstance(datetime_string, str):
        raise TypeError("datetime_string must be a string")
    if not isinstance(timezone, str):
        raise TypeError("timezone must be a string")

    try:
        tz = zoneinfo.ZoneInfo(timezone)
        dt = datetime.fromisoformat(datetime_string)
        dt_localized = dt.replace(tzinfo=tz)

        dst_offset = dt_localized.dst()
        return dst_offset is not None and dst_offset.total_seconds() > 0
    except Exception as e:
        raise ValueError(f"DST check failed: {e}")


@strands_tool
def is_valid_timezone(timezone_string: str) -> bool:
    """Check if a string is a valid timezone name.

    Args:
        timezone_string: The timezone string to validate

    Returns:
        True if the timezone string is valid, False otherwise

    Raises:
        TypeError: If timezone_string is not a string

    Example:
        >>> result = is_valid_timezone("America/New_York")
        >>> result
        True
        >>> result = is_valid_timezone("Invalid/Timezone")
        >>> result
        False
    """
    if not isinstance(timezone_string, str):
        raise TypeError("timezone_string must be a string")

    try:
        zoneinfo.ZoneInfo(timezone_string)
        return True
    except Exception:
        return False
