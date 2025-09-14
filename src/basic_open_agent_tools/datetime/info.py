"""Date and time information extraction for AI agents.

This module provides functions to extract information from dates and times
using ISO format strings for consistent date/time representation.
"""

import calendar
from datetime import date
from typing import Any, Callable

try:
    from strands import tool as strands_tool
except ImportError:
    # Create a no-op decorator if strands is not installed
    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]  # type: ignore
        return func


@strands_tool
def get_weekday_name(date_string: str) -> str:
    """Get the weekday name for a date.

    Args:
        date_string: The date string in ISO format (YYYY-MM-DD)

    Returns:
        The weekday name (e.g., "Monday", "Tuesday")

    Raises:
        TypeError: If date_string is not a string
        ValueError: If date_string is not a valid ISO format date

    Example:
        >>> result = get_weekday_name("2025-07-08")
        >>> result
        "Tuesday"
    """
    if not isinstance(date_string, str):
        raise TypeError("date_string must be a string")

    try:
        dt = date.fromisoformat(date_string)
        return dt.strftime("%A")
    except ValueError as e:
        raise ValueError(f"Invalid ISO date format '{date_string}': {e}")


@strands_tool
def get_month_name(date_string: str) -> str:
    """Get the month name for a date.

    Args:
        date_string: The date string in ISO format (YYYY-MM-DD)

    Returns:
        The month name (e.g., "January", "February")

    Raises:
        TypeError: If date_string is not a string
        ValueError: If date_string is not a valid ISO format date

    Example:
        >>> result = get_month_name("2025-07-08")
        >>> result
        "July"
    """
    if not isinstance(date_string, str):
        raise TypeError("date_string must be a string")

    try:
        dt = date.fromisoformat(date_string)
        return dt.strftime("%B")
    except ValueError as e:
        raise ValueError(f"Invalid ISO date format '{date_string}': {e}")


@strands_tool
def get_week_number(date_string: str) -> int:
    """Get the ISO week number for a date.

    Args:
        date_string: The date string in ISO format (YYYY-MM-DD)

    Returns:
        The ISO week number (1-53)

    Raises:
        TypeError: If date_string is not a string
        ValueError: If date_string is not a valid ISO format date

    Example:
        >>> result = get_week_number("2025-07-08")
        >>> result
        28
    """
    if not isinstance(date_string, str):
        raise TypeError("date_string must be a string")

    try:
        dt = date.fromisoformat(date_string)
        return dt.isocalendar()[1]
    except ValueError as e:
        raise ValueError(f"Invalid ISO date format '{date_string}': {e}")


@strands_tool
def get_day_of_year(date_string: str) -> int:
    """Get the day of year for a date.

    Args:
        date_string: The date string in ISO format (YYYY-MM-DD)

    Returns:
        The day of year (1-366)

    Raises:
        TypeError: If date_string is not a string
        ValueError: If date_string is not a valid ISO format date

    Example:
        >>> result = get_day_of_year("2025-07-08")
        >>> result
        189
    """
    if not isinstance(date_string, str):
        raise TypeError("date_string must be a string")

    try:
        dt = date.fromisoformat(date_string)
        return dt.timetuple().tm_yday
    except ValueError as e:
        raise ValueError(f"Invalid ISO date format '{date_string}': {e}")


@strands_tool
def is_leap_year(year: int) -> bool:
    """Check if a year is a leap year.

    Args:
        year: The year to check (e.g., 2024)

    Returns:
        True if the year is a leap year, False otherwise

    Raises:
        TypeError: If year is not an integer

    Example:
        >>> result = is_leap_year(2024)
        >>> result
        True
        >>> result = is_leap_year(2025)
        >>> result
        False
    """
    if not isinstance(year, int):
        raise TypeError("year must be an integer")

    return calendar.isleap(year)


@strands_tool
def get_days_in_month(year: int, month: int) -> int:
    """Get the number of days in a month.

    Args:
        year: The year (e.g., 2025)
        month: The month (1-12)

    Returns:
        The number of days in the month (28-31)

    Raises:
        TypeError: If year or month is not an integer
        ValueError: If month is not 1-12

    Example:
        >>> result = get_days_in_month(2025, 2)
        >>> result
        28
        >>> result = get_days_in_month(2024, 2)
        >>> result
        29
    """
    if not isinstance(year, int):
        raise TypeError("year must be an integer")
    if not isinstance(month, int):
        raise TypeError("month must be an integer")

    if month < 1 or month > 12:
        raise ValueError("month must be between 1 and 12")

    return calendar.monthrange(year, month)[1]
