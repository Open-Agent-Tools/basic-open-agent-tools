"""Date and time validation utilities for AI agents.

This module provides validation functions for dates, times, and ranges using ISO
format strings for consistent validation.
"""

from datetime import date, datetime

from ..decorators import strands_tool


@strands_tool
def validate_date_range(date_string: str, min_date: str, max_date: str) -> bool:
    """Validate that a date falls within a specified range.

    Checks if the given date is between min_date and max_date (inclusive).

    Args:
        date_string: The date to validate in ISO format (YYYY-MM-DD)
        min_date: The minimum allowed date in ISO format (YYYY-MM-DD)
        max_date: The maximum allowed date in ISO format (YYYY-MM-DD)

    Returns:
        True if the date is within the range, False otherwise

    Raises:
        TypeError: If any parameter is not a string
        ValueError: If any date is not valid ISO format

    Example:
        >>> result = validate_date_range("2025-06-15", "2025-01-01", "2025-12-31")
        >>> result
        True
        >>> result = validate_date_range("2024-12-31", "2025-01-01", "2025-12-31")
        >>> result
        False
    """
    if not isinstance(date_string, str):
        raise TypeError("date_string must be a string")
    if not isinstance(min_date, str):
        raise TypeError("min_date must be a string")
    if not isinstance(max_date, str):
        raise TypeError("max_date must be a string")

    try:
        target_date = date.fromisoformat(date_string)
        min_dt = date.fromisoformat(min_date)
        max_dt = date.fromisoformat(max_date)

        return min_dt <= target_date <= max_dt
    except ValueError as e:
        raise ValueError(f"Invalid ISO date format: {e}")


@strands_tool
def validate_datetime_range(
    datetime_string: str, min_datetime: str, max_datetime: str
) -> bool:
    """Validate that a datetime falls within a specified range.

    Checks if the given datetime is between min_datetime and max_datetime (inclusive).

    Args:
        datetime_string: The datetime to validate in ISO format (YYYY-MM-DDTHH:MM:SS)
        min_datetime: The minimum allowed datetime in ISO format (YYYY-MM-DDTHH:MM:SS)
        max_datetime: The maximum allowed datetime in ISO format (YYYY-MM-DDTHH:MM:SS)

    Returns:
        True if the datetime is within the range, False otherwise

    Raises:
        TypeError: If any parameter is not a string
        ValueError: If any datetime is not valid ISO format

    Example:
        >>> result = validate_datetime_range("2025-06-15T12:00:00", "2025-01-01T00:00:00", "2025-12-31T23:59:59")
        >>> result
        True
    """
    if not isinstance(datetime_string, str):
        raise TypeError("datetime_string must be a string")
    if not isinstance(min_datetime, str):
        raise TypeError("min_datetime must be a string")
    if not isinstance(max_datetime, str):
        raise TypeError("max_datetime must be a string")

    try:
        target_dt = datetime.fromisoformat(datetime_string)
        min_dt = datetime.fromisoformat(min_datetime)
        max_dt = datetime.fromisoformat(max_datetime)

        return min_dt <= target_dt <= max_dt
    except ValueError as e:
        raise ValueError(f"Invalid ISO datetime format: {e}")


@strands_tool
def is_valid_date_format(date_string: str, format_string: str) -> bool:
    """Check if a date string matches a specific format.

    Validates that the date string can be parsed with the given format string.

    Args:
        date_string: The date string to validate
        format_string: The expected format (e.g., "%Y-%m-%d", "%m/%d/%Y")

    Returns:
        True if the date string matches the format, False otherwise

    Raises:
        TypeError: If date_string or format_string is not a string

    Example:
        >>> result = is_valid_date_format("2025-07-08", "%Y-%m-%d")
        >>> result
        True
        >>> result = is_valid_date_format("07/08/2025", "%Y-%m-%d")
        >>> result
        False
    """
    if not isinstance(date_string, str):
        raise TypeError("date_string must be a string")
    if not isinstance(format_string, str):
        raise TypeError("format_string must be a string")

    try:
        datetime.strptime(date_string, format_string)
        return True
    except ValueError:
        return False


@strands_tool
def is_future_date(date_string: str, reference_date: str) -> bool:
    """Check if a date is in the future relative to a reference date.

    Args:
        date_string: The date to check in ISO format (YYYY-MM-DD)
        reference_date: The reference date in ISO format (YYYY-MM-DD)

    Returns:
        True if date_string is after reference_date, False otherwise

    Raises:
        TypeError: If date_string or reference_date is not a string
        ValueError: If any date is not valid ISO format

    Example:
        >>> result = is_future_date("2025-07-09", "2025-07-08")
        >>> result
        True
        >>> result = is_future_date("2025-07-07", "2025-07-08")
        >>> result
        False
    """
    if not isinstance(date_string, str):
        raise TypeError("date_string must be a string")
    if not isinstance(reference_date, str):
        raise TypeError("reference_date must be a string")

    try:
        target_date = date.fromisoformat(date_string)
        ref_date = date.fromisoformat(reference_date)

        return target_date > ref_date
    except ValueError as e:
        raise ValueError(f"Invalid ISO date format: {e}")


@strands_tool
def is_past_date(date_string: str, reference_date: str) -> bool:
    """Check if a date is in the past relative to a reference date.

    Args:
        date_string: The date to check in ISO format (YYYY-MM-DD)
        reference_date: The reference date in ISO format (YYYY-MM-DD)

    Returns:
        True if date_string is before reference_date, False otherwise

    Raises:
        TypeError: If date_string or reference_date is not a string
        ValueError: If any date is not valid ISO format

    Example:
        >>> result = is_past_date("2025-07-07", "2025-07-08")
        >>> result
        True
        >>> result = is_past_date("2025-07-09", "2025-07-08")
        >>> result
        False
    """
    if not isinstance(date_string, str):
        raise TypeError("date_string must be a string")
    if not isinstance(reference_date, str):
        raise TypeError("reference_date must be a string")

    try:
        target_date = date.fromisoformat(date_string)
        ref_date = date.fromisoformat(reference_date)

        return target_date < ref_date
    except ValueError as e:
        raise ValueError(f"Invalid ISO date format: {e}")
