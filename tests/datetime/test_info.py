"""Tests for datetime information extraction functions."""

import pytest

from basic_open_agent_tools.datetime.info import (
    get_day_of_year,
    get_days_in_month,
    get_month_name,
    get_week_number,
    get_weekday_name,
    is_leap_year,
)


class TestGetWeekdayName:
    """Tests for get_weekday_name function."""

    def test_monday(self):
        """Test getting weekday name for Monday."""
        result = get_weekday_name("2025-07-07")  # Monday
        assert result == "Monday"

    def test_friday(self):
        """Test getting weekday name for Friday."""
        result = get_weekday_name("2025-07-04")  # Friday
        assert result == "Friday"

    def test_sunday(self):
        """Test getting weekday name for Sunday."""
        result = get_weekday_name("2025-07-06")  # Sunday
        assert result == "Sunday"

    def test_invalid_date(self):
        """Test with invalid date format."""
        with pytest.raises(ValueError, match="Invalid ISO date format"):
            get_weekday_name("invalid-date")

    def test_non_string_input(self):
        """Test with non-string input."""
        with pytest.raises(TypeError, match="date_string must be a string"):
            get_weekday_name(20250708)


class TestGetMonthName:
    """Tests for get_month_name function."""

    def test_january(self):
        """Test getting month name for January."""
        result = get_month_name("2025-01-15")
        assert result == "January"

    def test_july(self):
        """Test getting month name for July."""
        result = get_month_name("2025-07-08")
        assert result == "July"

    def test_december(self):
        """Test getting month name for December."""
        result = get_month_name("2025-12-31")
        assert result == "December"

    def test_invalid_date(self):
        """Test with invalid date format."""
        with pytest.raises(ValueError, match="Invalid ISO date format"):
            get_month_name("not-a-date")

    def test_non_string_input(self):
        """Test with non-string input."""
        with pytest.raises(TypeError, match="date_string must be a string"):
            get_month_name(None)


class TestGetWeekNumber:
    """Tests for get_week_number function."""

    def test_first_week(self):
        """Test getting week number for first week of year."""
        result = get_week_number("2025-01-06")  # First Monday of 2025
        assert result == 2  # ISO week numbering

    def test_mid_year(self):
        """Test getting week number for mid-year."""
        result = get_week_number("2025-07-08")
        assert result == 28

    def test_last_week(self):
        """Test getting week number for last week of year."""
        result = get_week_number("2025-12-31")
        assert result in [1, 52, 53]  # Can be week 1 of next year

    def test_invalid_date(self):
        """Test with invalid date format."""
        with pytest.raises(ValueError, match="Invalid ISO date format"):
            get_week_number("2025/07/08")

    def test_non_string_input(self):
        """Test with non-string input."""
        with pytest.raises(TypeError, match="date_string must be a string"):
            get_week_number(["2025-07-08"])


class TestGetDayOfYear:
    """Tests for get_day_of_year function."""

    def test_january_first(self):
        """Test day of year for January 1st."""
        result = get_day_of_year("2025-01-01")
        assert result == 1

    def test_december_last(self):
        """Test day of year for December 31st."""
        result = get_day_of_year("2025-12-31")
        assert result == 365

    def test_leap_year_december_last(self):
        """Test day of year for December 31st in leap year."""
        result = get_day_of_year("2024-12-31")
        assert result == 366

    def test_mid_year(self):
        """Test day of year for mid-year date."""
        result = get_day_of_year("2025-07-08")
        assert result == 189

    def test_invalid_date(self):
        """Test with invalid date format."""
        with pytest.raises(ValueError, match="Invalid ISO date format"):
            get_day_of_year("invalid")

    def test_non_string_input(self):
        """Test with non-string input."""
        with pytest.raises(TypeError, match="date_string must be a string"):
            get_day_of_year(20250708)


class TestIsLeapYear:
    """Tests for is_leap_year function."""

    def test_leap_year_2024(self):
        """Test that 2024 is a leap year."""
        assert is_leap_year(2024) is True

    def test_non_leap_year_2025(self):
        """Test that 2025 is not a leap year."""
        assert is_leap_year(2025) is False

    def test_century_non_leap_1900(self):
        """Test that 1900 is not a leap year (century rule)."""
        assert is_leap_year(1900) is False

    def test_century_leap_2000(self):
        """Test that 2000 is a leap year (400 year rule)."""
        assert is_leap_year(2000) is True

    def test_non_integer_input(self):
        """Test with non-integer input."""
        with pytest.raises(TypeError, match="year must be an integer"):
            is_leap_year("2024")


class TestGetDaysInMonth:
    """Tests for get_days_in_month function."""

    def test_january_31_days(self):
        """Test January has 31 days."""
        result = get_days_in_month(2025, 1)
        assert result == 31

    def test_february_non_leap(self):
        """Test February in non-leap year has 28 days."""
        result = get_days_in_month(2025, 2)
        assert result == 28

    def test_february_leap(self):
        """Test February in leap year has 29 days."""
        result = get_days_in_month(2024, 2)
        assert result == 29

    def test_april_30_days(self):
        """Test April has 30 days."""
        result = get_days_in_month(2025, 4)
        assert result == 30

    def test_december_31_days(self):
        """Test December has 31 days."""
        result = get_days_in_month(2025, 12)
        assert result == 31

    def test_invalid_month_low(self):
        """Test with month < 1."""
        with pytest.raises(ValueError, match="month must be between 1 and 12"):
            get_days_in_month(2025, 0)

    def test_invalid_month_high(self):
        """Test with month > 12."""
        with pytest.raises(ValueError, match="month must be between 1 and 12"):
            get_days_in_month(2025, 13)

    def test_non_integer_year(self):
        """Test with non-integer year."""
        with pytest.raises(TypeError, match="year must be an integer"):
            get_days_in_month("2025", 7)

    def test_non_integer_month(self):
        """Test with non-integer month."""
        with pytest.raises(TypeError, match="month must be an integer"):
            get_days_in_month(2025, "7")
