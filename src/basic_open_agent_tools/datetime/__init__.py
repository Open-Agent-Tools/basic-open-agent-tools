"""DateTime utilities for AI agents.

This module provides date and time manipulation tools with agent-friendly signatures.
All functions use ISO format strings for consistent date/time representation.
"""

from .business import (
    get_next_business_day,
    is_business_day,
)
from .info import (
    get_day_of_year,
    get_days_in_month,
    get_month_name,
    get_week_number,
    get_weekday_name,
    is_leap_year,
)
from .operations import (
    add_days,
    add_hours,
    add_minutes,
    calculate_time_difference,
    get_current_date,
    get_current_datetime,
    get_current_time,
    is_valid_iso_date,
    is_valid_iso_datetime,
    is_valid_iso_time,
    subtract_days,
    subtract_hours,
    subtract_minutes,
)
from .ranges import (
    calculate_days_between,
    get_business_days_in_range,
    get_date_range,
    get_days_ago,
    get_last_business_day,
    get_month_range,
    get_months_ago,
    get_quarter_dates,
    get_year_to_date_range,
    is_date_in_range,
)
from .timezone import (
    convert_timezone,
    get_timezone_offset,
    is_daylight_saving_time,
    is_valid_timezone,
)
from .validation import (
    is_future_date,
    is_past_date,
    is_valid_date_format,
    validate_date_range,
    validate_datetime_range,
)

__all__ = [
    # operations.py
    "add_days",
    "add_hours",
    "add_minutes",
    "calculate_time_difference",
    "get_current_date",
    "get_current_datetime",
    "get_current_time",
    "is_valid_iso_date",
    "is_valid_iso_datetime",
    "is_valid_iso_time",
    "subtract_days",
    "subtract_hours",
    "subtract_minutes",
    # ranges.py
    "calculate_days_between",
    "get_business_days_in_range",
    "get_date_range",
    "get_days_ago",
    "get_last_business_day",
    "get_month_range",
    "get_months_ago",
    "get_quarter_dates",
    "get_year_to_date_range",
    "is_date_in_range",
    # info.py
    "get_day_of_year",
    "get_days_in_month",
    "get_month_name",
    "get_week_number",
    "get_weekday_name",
    "is_leap_year",
    # business.py
    "get_next_business_day",
    "is_business_day",
    # timezone.py
    "convert_timezone",
    "get_timezone_offset",
    "is_daylight_saving_time",
    "is_valid_timezone",
    # validation.py
    "is_future_date",
    "is_past_date",
    "is_valid_date_format",
    "validate_date_range",
    "validate_datetime_range",
]
