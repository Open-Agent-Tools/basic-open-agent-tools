"""Core date and time operations for AI agents.

This module provides fundamental date and time operations using ISO format strings.
All functions are designed to be agent-friendly with clear error handling.
"""

import zoneinfo
from datetime import date, datetime, time, timedelta

from ..decorators import strands_tool


@strands_tool
def get_current_datetime(timezone: str) -> str:
    """Get the current date and time in the specified timezone.

    Returns the current datetime as an ISO format string in the specified timezone.
    Agents can use this to get timestamped information or schedule operations.

    Args:
        timezone: The timezone name (e.g., "UTC", "America/New_York", "Europe/London")

    Returns:
        Current datetime in ISO format (YYYY-MM-DDTHH:MM:SS.ffffff+offset)

    Raises:
        TypeError: If timezone is not a string
        ValueError: If timezone is not a valid timezone name

    Example:
        >>> result = get_current_datetime("UTC")
        >>> result
        "2025-07-08T14:30:45.123456+00:00"
    """
    if not isinstance(timezone, str):
        raise TypeError("timezone must be a string")

    try:
        tz = zoneinfo.ZoneInfo(timezone)
        now = datetime.now(tz)
        return now.isoformat()
    except Exception as e:
        raise ValueError(f"Invalid timezone '{timezone}': {e}")


@strands_tool
def get_current_date(timezone: str) -> str:
    """Get the current date in the specified timezone.

    Returns the current date as an ISO format string in the specified timezone.
    Useful for agents that need to work with dates without time information.

    Args:
        timezone: The timezone name (e.g., "UTC", "America/New_York", "Europe/London")

    Returns:
        Current date in ISO format (YYYY-MM-DD)

    Raises:
        TypeError: If timezone is not a string
        ValueError: If timezone is not a valid timezone name

    Example:
        >>> result = get_current_date("UTC")
        >>> result
        "2025-07-08"
    """
    if not isinstance(timezone, str):
        raise TypeError("timezone must be a string")

    try:
        tz = zoneinfo.ZoneInfo(timezone)
        now = datetime.now(tz)
        return now.date().isoformat()
    except Exception as e:
        raise ValueError(f"Invalid timezone '{timezone}': {e}")


@strands_tool
def get_current_time(timezone: str) -> str:
    """Get the current time in the specified timezone.

    Returns the current time as an ISO format string in the specified timezone.
    Useful for agents that need to work with time information without date.

    Args:
        timezone: The timezone name (e.g., "UTC", "America/New_York", "Europe/London")

    Returns:
        Current time in ISO format (HH:MM:SS.ffffff)

    Raises:
        TypeError: If timezone is not a string
        ValueError: If timezone is not a valid timezone name

    Example:
        >>> result = get_current_time("UTC")
        >>> result
        "14:30:45.123456"
    """
    if not isinstance(timezone, str):
        raise TypeError("timezone must be a string")

    try:
        tz = zoneinfo.ZoneInfo(timezone)
        now = datetime.now(tz)
        return now.time().isoformat()
    except Exception as e:
        raise ValueError(f"Invalid timezone '{timezone}': {e}")


@strands_tool
def is_valid_iso_date(date_string: str) -> bool:
    """Check if a string is a valid ISO format date.

    Validates that the input string can be parsed as an ISO format date.
    Agents can use this to validate date inputs before processing.

    Args:
        date_string: The date string to validate (expected format: YYYY-MM-DD)

    Returns:
        True if the date string is valid ISO format, False otherwise

    Raises:
        TypeError: If date_string is not a string

    Example:
        >>> result = is_valid_iso_date("2025-07-08")
        >>> result
        True
        >>> result = is_valid_iso_date("invalid-date")
        >>> result
        False
    """
    if not isinstance(date_string, str):
        raise TypeError("date_string must be a string")

    try:
        date.fromisoformat(date_string)
        return True
    except ValueError:
        return False


@strands_tool
def is_valid_iso_time(time_string: str) -> bool:
    """Check if a string is a valid ISO format time.

    Validates that the input string can be parsed as an ISO format time.
    Agents can use this to validate time inputs before processing.

    Args:
        time_string: The time string to validate (expected format: HH:MM:SS or HH:MM:SS.ffffff)

    Returns:
        True if the time string is valid ISO format, False otherwise

    Raises:
        TypeError: If time_string is not a string

    Example:
        >>> result = is_valid_iso_time("14:30:45")
        >>> result
        True
        >>> result = is_valid_iso_time("invalid-time")
        >>> result
        False
    """
    if not isinstance(time_string, str):
        raise TypeError("time_string must be a string")

    try:
        time.fromisoformat(time_string)
        return True
    except ValueError:
        return False


@strands_tool
def is_valid_iso_datetime(datetime_string: str) -> bool:
    """Check if a string is a valid ISO format datetime.

    Validates that the input string can be parsed as an ISO format datetime.
    Agents can use this to validate datetime inputs before processing.

    Args:
        datetime_string: The datetime string to validate (expected format: YYYY-MM-DDTHH:MM:SS)

    Returns:
        True if the datetime string is valid ISO format, False otherwise

    Raises:
        TypeError: If datetime_string is not a string

    Example:
        >>> result = is_valid_iso_datetime("2025-07-08T14:30:45")
        >>> result
        True
        >>> result = is_valid_iso_datetime("invalid-datetime")
        >>> result
        False
    """
    if not isinstance(datetime_string, str):
        raise TypeError("datetime_string must be a string")

    try:
        datetime.fromisoformat(datetime_string)
        return True
    except ValueError:
        return False


@strands_tool
def add_days(date_string: str, days: int) -> str:
    """Add a specified number of days to a date.

    Takes an ISO format date string and adds the specified number of days,
    returning the result as an ISO format date string.

    Args:
        date_string: The date string in ISO format (YYYY-MM-DD)
        days: The number of days to add (can be negative to subtract)

    Returns:
        The new date in ISO format (YYYY-MM-DD)

    Raises:
        TypeError: If date_string is not a string or days is not an integer
        ValueError: If date_string is not a valid ISO format date

    Example:
        >>> result = add_days("2025-07-08", 7)
        >>> result
        "2025-07-15"
        >>> result = add_days("2025-07-08", -3)
        >>> result
        "2025-07-05"
    """
    if not isinstance(date_string, str):
        raise TypeError("date_string must be a string")
    if not isinstance(days, int):
        raise TypeError("days must be an integer")

    try:
        original_date = date.fromisoformat(date_string)
        new_date = original_date + timedelta(days=days)
        return new_date.isoformat()
    except ValueError as e:
        raise ValueError(f"Invalid ISO date format '{date_string}': {e}")


@strands_tool
def subtract_days(date_string: str, days: int) -> str:
    """Subtract a specified number of days from a date.

    Takes an ISO format date string and subtracts the specified number of days,
    returning the result as an ISO format date string.

    Args:
        date_string: The date string in ISO format (YYYY-MM-DD)
        days: The number of days to subtract (must be positive)

    Returns:
        The new date in ISO format (YYYY-MM-DD)

    Raises:
        TypeError: If date_string is not a string or days is not an integer
        ValueError: If date_string is not a valid ISO format date or days is negative

    Example:
        >>> result = subtract_days("2025-07-08", 7)
        >>> result
        "2025-07-01"
        >>> result = subtract_days("2025-07-08", 3)
        >>> result
        "2025-07-05"
    """
    if not isinstance(date_string, str):
        raise TypeError("date_string must be a string")
    if not isinstance(days, int):
        raise TypeError("days must be an integer")
    if days < 0:
        raise ValueError("days must be positive (use add_days for negative values)")

    try:
        original_date = date.fromisoformat(date_string)
        new_date = original_date - timedelta(days=days)
        return new_date.isoformat()
    except ValueError as e:
        raise ValueError(f"Invalid ISO date format '{date_string}': {e}")


@strands_tool
def add_hours(datetime_string: str, hours: int) -> str:
    """Add hours to a datetime string."""
    if not isinstance(datetime_string, str):
        raise TypeError("datetime_string must be a string")
    if not isinstance(hours, int):
        raise TypeError("hours must be an integer")

    try:
        dt = datetime.fromisoformat(datetime_string)
        return (dt + timedelta(hours=hours)).isoformat()
    except ValueError as e:
        raise ValueError(f"Invalid ISO datetime format '{datetime_string}': {e}")


@strands_tool
def subtract_hours(datetime_string: str, hours: int) -> str:
    """Subtract hours from a datetime string."""
    if not isinstance(datetime_string, str):
        raise TypeError("datetime_string must be a string")
    if not isinstance(hours, int):
        raise TypeError("hours must be an integer")
    if hours < 0:
        raise ValueError("hours must be positive")

    try:
        dt = datetime.fromisoformat(datetime_string)
        return (dt - timedelta(hours=hours)).isoformat()
    except ValueError as e:
        raise ValueError(f"Invalid ISO datetime format '{datetime_string}': {e}")


@strands_tool
def add_minutes(datetime_string: str, minutes: int) -> str:
    """Add minutes to a datetime string."""
    if not isinstance(datetime_string, str):
        raise TypeError("datetime_string must be a string")
    if not isinstance(minutes, int):
        raise TypeError("minutes must be an integer")

    try:
        dt = datetime.fromisoformat(datetime_string)
        return (dt + timedelta(minutes=minutes)).isoformat()
    except ValueError as e:
        raise ValueError(f"Invalid ISO datetime format '{datetime_string}': {e}")


@strands_tool
def subtract_minutes(datetime_string: str, minutes: int) -> str:
    """Subtract minutes from a datetime string."""
    if not isinstance(datetime_string, str):
        raise TypeError("datetime_string must be a string")
    if not isinstance(minutes, int):
        raise TypeError("minutes must be an integer")
    if minutes < 0:
        raise ValueError("minutes must be positive")

    try:
        dt = datetime.fromisoformat(datetime_string)
        return (dt - timedelta(minutes=minutes)).isoformat()
    except ValueError as e:
        raise ValueError(f"Invalid ISO datetime format '{datetime_string}': {e}")


@strands_tool
def calculate_time_difference(time1: str, time2: str, unit: str) -> int:
    """Calculate difference between two times in specified unit."""
    if not isinstance(time1, str):
        raise TypeError("time1 must be a string")
    if not isinstance(time2, str):
        raise TypeError("time2 must be a string")
    if not isinstance(unit, str):
        raise TypeError("unit must be a string")

    if unit not in ["hours", "minutes", "seconds"]:
        raise ValueError("unit must be 'hours', 'minutes', or 'seconds'")

    try:
        t1 = time.fromisoformat(time1)
        t2 = time.fromisoformat(time2)

        # Convert to datetime objects for timedelta calculation
        base_date = date.today()
        dt1 = datetime.combine(base_date, t1)
        dt2 = datetime.combine(base_date, t2)

        delta = dt2 - dt1
        total_seconds = int(delta.total_seconds())

        if unit == "seconds":
            return total_seconds
        elif unit == "minutes":
            return total_seconds // 60
        elif unit == "hours":
            return total_seconds // 3600
        else:
            return 0  # Should never reach here due to validation
    except ValueError as e:
        raise ValueError(f"Invalid ISO time format: {e}")
