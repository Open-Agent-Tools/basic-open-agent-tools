"""Date range and period operations for AI agents.

This module provides date and time utilities for working with date ranges,
periods, and business day calculations. All functions use ISO format strings
for consistent date/time representation.
"""

from datetime import date, timedelta

from ..decorators import strands_tool


@strands_tool
def get_date_range(start_date: str, end_date: str) -> list[str]:
    """Generate all dates between two dates (inclusive).

    Returns a list of all dates from start_date to end_date, inclusive.
    Useful for analysis over specific periods.

    Args:
        start_date: The start date in ISO format (YYYY-MM-DD)
        end_date: The end date in ISO format (YYYY-MM-DD)

    Returns:
        List of date strings in ISO format (YYYY-MM-DD)

    Raises:
        TypeError: If start_date or end_date is not a string
        ValueError: If dates are not valid ISO format or start_date > end_date

    Example:
        >>> result = get_date_range("2025-01-01", "2025-01-03")
        >>> result
        ["2025-01-01", "2025-01-02", "2025-01-03"]
    """
    if not isinstance(start_date, str):
        raise TypeError("start_date must be a string")
    if not isinstance(end_date, str):
        raise TypeError("end_date must be a string")

    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError as e:
        raise ValueError(f"Invalid ISO date format: {e}")

    if start > end:
        raise ValueError("start_date must be less than or equal to end_date")

    dates = []
    current = start
    while current <= end:
        dates.append(current.isoformat())
        current += timedelta(days=1)

    return dates


@strands_tool
def get_quarter_dates(year: int, quarter: int) -> dict[str, str]:
    """Get start and end dates for a specific quarter.

    Returns the first and last dates of the specified quarter.
    Useful for quarterly analysis and reporting.

    Args:
        year: The year (e.g., 2025)
        quarter: The quarter number (1, 2, 3, or 4)

    Returns:
        Dictionary with 'start' and 'end' keys containing ISO date strings

    Raises:
        TypeError: If year or quarter is not an integer
        ValueError: If quarter is not 1, 2, 3, or 4

    Example:
        >>> result = get_quarter_dates(2025, 1)
        >>> result
        {"start": "2025-01-01", "end": "2025-03-31"}
    """
    if not isinstance(year, int):
        raise TypeError("year must be an integer")
    if not isinstance(quarter, int):
        raise TypeError("quarter must be an integer")

    if quarter not in [1, 2, 3, 4]:
        raise ValueError("quarter must be 1, 2, 3, or 4")

    quarter_months = {1: (1, 3), 2: (4, 6), 3: (7, 9), 4: (10, 12)}

    start_month, end_month = quarter_months[quarter]
    start_date = date(year, start_month, 1)

    # Get last day of end month
    if end_month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, end_month + 1, 1) - timedelta(days=1)

    return {"start": start_date.isoformat(), "end": end_date.isoformat()}


@strands_tool
def get_year_to_date_range(reference_date: str) -> dict[str, str]:
    """Get the date range from January 1st to the reference date.

    Returns the start of the year and the reference date as a range.
    Useful for year-to-date analysis.

    Args:
        reference_date: The reference date in ISO format (YYYY-MM-DD)

    Returns:
        Dictionary with 'start' and 'end' keys containing ISO date strings

    Raises:
        TypeError: If reference_date is not a string
        ValueError: If reference_date is not a valid ISO format date

    Example:
        >>> result = get_year_to_date_range("2025-06-30")
        >>> result
        {"start": "2025-01-01", "end": "2025-06-30"}
    """
    if not isinstance(reference_date, str):
        raise TypeError("reference_date must be a string")

    try:
        ref_date = date.fromisoformat(reference_date)
    except ValueError as e:
        raise ValueError(f"Invalid ISO date format: {e}")

    start_date = date(ref_date.year, 1, 1)

    return {"start": start_date.isoformat(), "end": reference_date}


@strands_tool
def get_days_ago(days: int, reference_date: str) -> str:
    """Get the date N days before the reference date.

    Calculates the date that is the specified number of days before
    the reference date. Useful for "last N days" type queries.

    Args:
        days: Number of days to go back (must be positive)
        reference_date: The reference date in ISO format (YYYY-MM-DD)

    Returns:
        Date string in ISO format (YYYY-MM-DD)

    Raises:
        TypeError: If days is not an integer or reference_date is not a string
        ValueError: If days is negative or reference_date is invalid

    Example:
        >>> result = get_days_ago(90, "2025-07-08")
        >>> result
        "2025-04-09"
    """
    if not isinstance(days, int):
        raise TypeError("days must be an integer")
    if not isinstance(reference_date, str):
        raise TypeError("reference_date must be a string")

    if days < 0:
        raise ValueError("days must be positive")

    try:
        ref_date = date.fromisoformat(reference_date)
    except ValueError as e:
        raise ValueError(f"Invalid ISO date format: {e}")

    target_date = ref_date - timedelta(days=days)
    return target_date.isoformat()


@strands_tool
def get_months_ago(months: int, reference_date: str) -> str:
    """Get the date N months before the reference date.

    Calculates the date that is the specified number of months before
    the reference date. Useful for "past N months" queries.

    Args:
        months: Number of months to go back (must be positive)
        reference_date: The reference date in ISO format (YYYY-MM-DD)

    Returns:
        Date string in ISO format (YYYY-MM-DD)

    Raises:
        TypeError: If months is not an integer or reference_date is not a string
        ValueError: If months is negative or reference_date is invalid

    Example:
        >>> result = get_months_ago(12, "2025-07-08")
        >>> result
        "2024-07-08"
    """
    if not isinstance(months, int):
        raise TypeError("months must be an integer")
    if not isinstance(reference_date, str):
        raise TypeError("reference_date must be a string")

    if months < 0:
        raise ValueError("months must be positive")

    try:
        ref_date = date.fromisoformat(reference_date)
    except ValueError as e:
        raise ValueError(f"Invalid ISO date format: {e}")

    # Calculate target year and month
    target_year = ref_date.year
    target_month = ref_date.month - months

    # Handle year rollover
    while target_month <= 0:
        target_month += 12
        target_year -= 1

    # Handle day overflow (e.g., Jan 31 -> Feb 31 doesn't exist)
    try:
        target_date = date(target_year, target_month, ref_date.day)
    except ValueError:
        # If day doesn't exist in target month, use last day of target month
        if target_month == 12:
            target_date = date(target_year + 1, 1, 1) - timedelta(days=1)
        else:
            target_date = date(target_year, target_month + 1, 1) - timedelta(days=1)

    return target_date.isoformat()


@strands_tool
def get_last_business_day(reference_date: str) -> str:
    """Get the last business day before or on the reference date.

    Returns the most recent business day (Monday-Friday) that is
    on or before the reference date. Excludes weekends.

    Args:
        reference_date: The reference date in ISO format (YYYY-MM-DD)

    Returns:
        Date string in ISO format (YYYY-MM-DD)

    Raises:
        TypeError: If reference_date is not a string
        ValueError: If reference_date is not a valid ISO format date

    Example:
        >>> result = get_last_business_day("2025-07-06")  # Sunday
        >>> result
        "2025-07-04"  # Friday
    """
    if not isinstance(reference_date, str):
        raise TypeError("reference_date must be a string")

    try:
        ref_date = date.fromisoformat(reference_date)
    except ValueError as e:
        raise ValueError(f"Invalid ISO date format: {e}")

    # Find the last business day (Monday=0, Sunday=6)
    current_date = ref_date
    while current_date.weekday() > 4:  # Saturday=5, Sunday=6
        current_date -= timedelta(days=1)

    return current_date.isoformat()


@strands_tool
def is_date_in_range(check_date: str, start_date: str, end_date: str) -> bool:
    """Check if a date falls within a specified range (inclusive).

    Determines whether the check_date is between start_date and end_date,
    inclusive. Useful for filtering data by date range.

    Args:
        check_date: The date to check in ISO format (YYYY-MM-DD)
        start_date: The start date in ISO format (YYYY-MM-DD)
        end_date: The end date in ISO format (YYYY-MM-DD)

    Returns:
        True if check_date is within the range, False otherwise

    Raises:
        TypeError: If any parameter is not a string
        ValueError: If any date is not valid ISO format

    Example:
        >>> result = is_date_in_range("2025-05-15", "2025-05-01", "2025-05-31")
        >>> result
        True
    """
    if not isinstance(check_date, str):
        raise TypeError("check_date must be a string")
    if not isinstance(start_date, str):
        raise TypeError("start_date must be a string")
    if not isinstance(end_date, str):
        raise TypeError("end_date must be a string")

    try:
        check = date.fromisoformat(check_date)
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError as e:
        raise ValueError(f"Invalid ISO date format: {e}")

    return start <= check <= end


@strands_tool
def get_month_range(year: int, month: int) -> dict[str, str]:
    """Get the start and end dates for a specific month.

    Returns the first and last dates of the specified month.
    Useful for monthly analysis and reporting.

    Args:
        year: The year (e.g., 2025)
        month: The month (1-12)

    Returns:
        Dictionary with 'start' and 'end' keys containing ISO date strings

    Raises:
        TypeError: If year or month is not an integer
        ValueError: If month is not 1-12

    Example:
        >>> result = get_month_range(2025, 5)
        >>> result
        {"start": "2025-05-01", "end": "2025-05-31"}
    """
    if not isinstance(year, int):
        raise TypeError("year must be an integer")
    if not isinstance(month, int):
        raise TypeError("month must be an integer")

    if month < 1 or month > 12:
        raise ValueError("month must be between 1 and 12")

    start_date = date(year, month, 1)

    # Get last day of month
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)

    return {"start": start_date.isoformat(), "end": end_date.isoformat()}


@strands_tool
def calculate_days_between(start_date: str, end_date: str) -> int:
    """Calculate the number of days between two dates.

    Returns the number of days from start_date to end_date.
    Positive if end_date is after start_date, negative if before.

    Args:
        start_date: The start date in ISO format (YYYY-MM-DD)
        end_date: The end date in ISO format (YYYY-MM-DD)

    Returns:
        Number of days between the dates (integer)

    Raises:
        TypeError: If start_date or end_date is not a string
        ValueError: If dates are not valid ISO format

    Example:
        >>> result = calculate_days_between("2025-01-01", "2025-01-31")
        >>> result
        30
    """
    if not isinstance(start_date, str):
        raise TypeError("start_date must be a string")
    if not isinstance(end_date, str):
        raise TypeError("end_date must be a string")

    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError as e:
        raise ValueError(f"Invalid ISO date format: {e}")

    return (end - start).days


@strands_tool
def get_business_days_in_range(start_date: str, end_date: str) -> int:
    """Count business days between two dates (inclusive).

    Returns the number of business days (Monday-Friday) between
    start_date and end_date, inclusive. Excludes weekends.

    Args:
        start_date: The start date in ISO format (YYYY-MM-DD)
        end_date: The end date in ISO format (YYYY-MM-DD)

    Returns:
        Number of business days (integer)

    Raises:
        TypeError: If start_date or end_date is not a string
        ValueError: If dates are not valid ISO format or start_date > end_date

    Example:
        >>> result = get_business_days_in_range("2025-07-07", "2025-07-11")  # Mon-Fri
        >>> result
        5
    """
    if not isinstance(start_date, str):
        raise TypeError("start_date must be a string")
    if not isinstance(end_date, str):
        raise TypeError("end_date must be a string")

    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError as e:
        raise ValueError(f"Invalid ISO date format: {e}")

    if start > end:
        raise ValueError("start_date must be less than or equal to end_date")

    business_days = 0
    current = start

    while current <= end:
        if current.weekday() < 5:  # Monday=0, Friday=4
            business_days += 1
        current += timedelta(days=1)

    return business_days
