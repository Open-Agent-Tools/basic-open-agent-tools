"""Business day operations for AI agents.

This module provides business day calculations and utilities using ISO format
strings for consistent date representation.
"""

from datetime import date, timedelta
from typing import Any, Callable

try:
    from strands import tool as strands_tool
except ImportError:
    # Create a no-op decorator if strands is not installed
    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]  # type: ignore
        return func


@strands_tool
def get_next_business_day(date_string: str) -> str:
    """Get the next business day after the given date.

    Returns the next business day (Monday-Friday) after the given date.
    If the given date is already a business day, returns the next business day.

    Args:
        date_string: The date string in ISO format (YYYY-MM-DD)

    Returns:
        The next business day in ISO format (YYYY-MM-DD)

    Raises:
        TypeError: If date_string is not a string
        ValueError: If date_string is not a valid ISO format date

    Example:
        >>> result = get_next_business_day("2025-07-04")  # Friday
        >>> result
        "2025-07-07"  # Monday
        >>> result = get_next_business_day("2025-07-05")  # Saturday
        >>> result
        "2025-07-07"  # Monday
    """
    if not isinstance(date_string, str):
        raise TypeError("date_string must be a string")

    try:
        current_date = date.fromisoformat(date_string)
    except ValueError as e:
        raise ValueError(f"Invalid ISO date format '{date_string}': {e}")

    # Move to next day
    next_date = current_date + timedelta(days=1)

    # Find next business day (Monday=0, Sunday=6)
    while next_date.weekday() > 4:  # Saturday=5, Sunday=6
        next_date += timedelta(days=1)

    return next_date.isoformat()


@strands_tool
def is_business_day(date_string: str) -> bool:
    """Check if a date is a business day.

    Returns True if the date is a business day (Monday-Friday),
    False if it's a weekend (Saturday-Sunday).

    Args:
        date_string: The date string in ISO format (YYYY-MM-DD)

    Returns:
        True if the date is a business day, False otherwise

    Raises:
        TypeError: If date_string is not a string
        ValueError: If date_string is not a valid ISO format date

    Example:
        >>> result = is_business_day("2025-07-07")  # Monday
        >>> result
        True
        >>> result = is_business_day("2025-07-05")  # Saturday
        >>> result
        False
    """
    if not isinstance(date_string, str):
        raise TypeError("date_string must be a string")

    try:
        dt = date.fromisoformat(date_string)
    except ValueError as e:
        raise ValueError(f"Invalid ISO date format '{date_string}': {e}")

    # Monday=0, Friday=4, Saturday=5, Sunday=6
    return dt.weekday() < 5
