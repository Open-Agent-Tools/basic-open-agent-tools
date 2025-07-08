"""Tests for datetime operations module."""

import pytest
from freezegun import freeze_time

from src.basic_open_agent_tools.datetime.operations import (
    add_days,
    get_current_date,
    get_current_datetime,
    get_current_time,
    is_valid_iso_date,
    is_valid_iso_datetime,
    is_valid_iso_time,
    subtract_days,
)


class TestGetCurrentDatetime:
    """Test get_current_datetime function."""

    @freeze_time("2025-07-08 14:30:45")
    def test_get_current_datetime_utc(self):
        """Test getting current datetime in UTC."""
        result = get_current_datetime("UTC")
        assert result.startswith("2025-07-08T14:30:45")
        assert result.endswith("+00:00")

    @freeze_time("2025-07-08 14:30:45")
    def test_get_current_datetime_timezone(self):
        """Test getting current datetime in different timezone."""
        result = get_current_datetime("America/New_York")
        assert result.startswith("2025-07-08T")
        assert "-04:00" in result or "-05:00" in result  # EST/EDT

    def test_get_current_datetime_invalid_timezone(self):
        """Test get_current_datetime with invalid timezone."""
        with pytest.raises(ValueError, match="Invalid timezone"):
            get_current_datetime("Invalid/Timezone")

    def test_get_current_datetime_non_string_timezone(self):
        """Test get_current_datetime with non-string timezone."""
        with pytest.raises(TypeError, match="timezone must be a string"):
            get_current_datetime(123)


class TestGetCurrentDate:
    """Test get_current_date function."""

    @freeze_time("2025-07-08 14:30:45")
    def test_get_current_date_utc(self):
        """Test getting current date in UTC."""
        result = get_current_date("UTC")
        assert result == "2025-07-08"

    @freeze_time("2025-07-08 14:30:45")
    def test_get_current_date_timezone(self):
        """Test getting current date in different timezone."""
        result = get_current_date("America/New_York")
        assert result == "2025-07-08"

    def test_get_current_date_invalid_timezone(self):
        """Test get_current_date with invalid timezone."""
        with pytest.raises(ValueError, match="Invalid timezone"):
            get_current_date("Invalid/Timezone")

    def test_get_current_date_non_string_timezone(self):
        """Test get_current_date with non-string timezone."""
        with pytest.raises(TypeError, match="timezone must be a string"):
            get_current_date(123)


class TestGetCurrentTime:
    """Test get_current_time function."""

    @freeze_time("2025-07-08 14:30:45.123456")
    def test_get_current_time_utc(self):
        """Test getting current time in UTC."""
        result = get_current_time("UTC")
        assert result.startswith("14:30:45")
        assert "123456" in result

    @freeze_time("2025-07-08 14:30:45")
    def test_get_current_time_timezone(self):
        """Test getting current time in different timezone."""
        result = get_current_time("America/New_York")
        assert ":" in result
        assert len(result.split(":")) >= 3  # HH:MM:SS format

    def test_get_current_time_invalid_timezone(self):
        """Test get_current_time with invalid timezone."""
        with pytest.raises(ValueError, match="Invalid timezone"):
            get_current_time("Invalid/Timezone")

    def test_get_current_time_non_string_timezone(self):
        """Test get_current_time with non-string timezone."""
        with pytest.raises(TypeError, match="timezone must be a string"):
            get_current_time(123)


class TestIsValidIsoDate:
    """Test is_valid_iso_date function."""

    def test_valid_iso_dates(self):
        """Test with valid ISO date strings."""
        valid_dates = [
            "2025-07-08",
            "2000-01-01",
            "2024-12-31",
            "1999-02-28",
            "2024-02-29",  # leap year
        ]
        for date_str in valid_dates:
            assert is_valid_iso_date(date_str) is True

    def test_invalid_iso_dates(self):
        """Test with invalid ISO date strings."""
        invalid_dates = [
            "invalid-date",
            "2025-13-01",  # invalid month
            "2025-12-32",  # invalid day
            "2025-02-30",  # invalid day for February
            "2023-02-29",  # not a leap year
            "07-08-2025",  # wrong format
            "2025/07/08",  # wrong separator
            "",
            "2025-7-8",  # missing leading zeros
        ]
        for date_str in invalid_dates:
            assert is_valid_iso_date(date_str) is False

    def test_non_string_input(self):
        """Test is_valid_iso_date with non-string input."""
        with pytest.raises(TypeError, match="date_string must be a string"):
            is_valid_iso_date(123)


class TestIsValidIsoTime:
    """Test is_valid_iso_time function."""

    def test_valid_iso_times(self):
        """Test with valid ISO time strings."""
        valid_times = [
            "14:30:45",
            "00:00:00",
            "23:59:59",
            "12:00:00.123456",
            "09:15:30.999999",
        ]
        for time_str in valid_times:
            assert is_valid_iso_time(time_str) is True

    def test_invalid_iso_times(self):
        """Test with invalid ISO time strings."""
        invalid_times = [
            "invalid-time",
            "25:00:00",  # invalid hour
            "12:60:00",  # invalid minute
            "12:30:60",  # invalid second
            "",
            "2:30:45",  # missing leading zero
        ]
        for time_str in invalid_times:
            assert is_valid_iso_time(time_str) is False

        # Python's fromisoformat() accepts these formats
        assert is_valid_iso_time("12:30") is True  # HH:MM format
        assert is_valid_iso_time("12:30:45:123") is True  # treats :123 as microseconds

    def test_non_string_input(self):
        """Test is_valid_iso_time with non-string input."""
        with pytest.raises(TypeError, match="time_string must be a string"):
            is_valid_iso_time(123)


class TestIsValidIsoDatetime:
    """Test is_valid_iso_datetime function."""

    def test_valid_iso_datetimes(self):
        """Test with valid ISO datetime strings."""
        valid_datetimes = [
            "2025-07-08T14:30:45",
            "2025-07-08T14:30:45.123456",
            "2025-07-08T00:00:00",
            "2025-12-31T23:59:59",
            "2025-07-08T14:30:45+00:00",
            "2025-07-08T14:30:45-05:00",
        ]
        for datetime_str in valid_datetimes:
            assert is_valid_iso_datetime(datetime_str) is True

    def test_invalid_iso_datetimes(self):
        """Test with invalid ISO datetime strings."""
        invalid_datetimes = [
            "invalid-datetime",
            "2025-07-08T25:30:45",  # invalid hour
            "2025-13-08T14:30:45",  # invalid month
            "",
            "14:30:45",  # time only
        ]
        for datetime_str in invalid_datetimes:
            assert is_valid_iso_datetime(datetime_str) is False

        # Python's fromisoformat() accepts these formats
        assert (
            is_valid_iso_datetime("2025-07-08 14:30:45") is True
        )  # space instead of T
        assert is_valid_iso_datetime("2025-07-08T14:30") is True  # missing seconds
        assert is_valid_iso_datetime("2025-07-08") is True  # date only (adds 00:00:00)

    def test_non_string_input(self):
        """Test is_valid_iso_datetime with non-string input."""
        with pytest.raises(TypeError, match="datetime_string must be a string"):
            is_valid_iso_datetime(123)


class TestAddDays:
    """Test add_days function."""

    def test_add_positive_days(self):
        """Test adding positive number of days."""
        result = add_days("2025-07-08", 7)
        assert result == "2025-07-15"

    def test_add_negative_days(self):
        """Test adding negative number of days (subtraction)."""
        result = add_days("2025-07-08", -7)
        assert result == "2025-07-01"

    def test_add_zero_days(self):
        """Test adding zero days."""
        result = add_days("2025-07-08", 0)
        assert result == "2025-07-08"

    def test_add_days_month_boundary(self):
        """Test adding days across month boundary."""
        result = add_days("2025-07-31", 1)
        assert result == "2025-08-01"

    def test_add_days_year_boundary(self):
        """Test adding days across year boundary."""
        result = add_days("2025-12-31", 1)
        assert result == "2026-01-01"

    def test_add_days_leap_year(self):
        """Test adding days in leap year."""
        result = add_days("2024-02-28", 1)
        assert result == "2024-02-29"

    def test_add_days_invalid_date(self):
        """Test add_days with invalid date string."""
        with pytest.raises(ValueError, match="Invalid ISO date format"):
            add_days("invalid-date", 1)

    def test_add_days_non_string_date(self):
        """Test add_days with non-string date."""
        with pytest.raises(TypeError, match="date_string must be a string"):
            add_days(123, 1)

    def test_add_days_non_integer_days(self):
        """Test add_days with non-integer days."""
        with pytest.raises(TypeError, match="days must be an integer"):
            add_days("2025-07-08", "5")


class TestSubtractDays:
    """Test subtract_days function."""

    def test_subtract_positive_days(self):
        """Test subtracting positive number of days."""
        result = subtract_days("2025-07-08", 7)
        assert result == "2025-07-01"

    def test_subtract_days_month_boundary(self):
        """Test subtracting days across month boundary."""
        result = subtract_days("2025-08-01", 1)
        assert result == "2025-07-31"

    def test_subtract_days_year_boundary(self):
        """Test subtracting days across year boundary."""
        result = subtract_days("2025-01-01", 1)
        assert result == "2024-12-31"

    def test_subtract_days_leap_year(self):
        """Test subtracting days in leap year."""
        result = subtract_days("2024-03-01", 1)
        assert result == "2024-02-29"

    def test_subtract_negative_days(self):
        """Test subtract_days with negative days."""
        with pytest.raises(ValueError, match="days must be positive"):
            subtract_days("2025-07-08", -7)

    def test_subtract_days_invalid_date(self):
        """Test subtract_days with invalid date string."""
        with pytest.raises(ValueError, match="Invalid ISO date format"):
            subtract_days("invalid-date", 1)

    def test_subtract_days_non_string_date(self):
        """Test subtract_days with non-string date."""
        with pytest.raises(TypeError, match="date_string must be a string"):
            subtract_days(123, 1)

    def test_subtract_days_non_integer_days(self):
        """Test subtract_days with non-integer days."""
        with pytest.raises(TypeError, match="days must be an integer"):
            subtract_days("2025-07-08", "5")


class TestDateTimeOperationsIntegration:
    """Integration tests for datetime operations."""

    def test_current_date_is_valid(self):
        """Test that current date is valid ISO format."""
        current_date = get_current_date("UTC")
        assert is_valid_iso_date(current_date) is True

    def test_current_time_is_valid(self):
        """Test that current time is valid ISO format."""
        current_time = get_current_time("UTC")
        assert is_valid_iso_time(current_time) is True

    def test_current_datetime_is_valid(self):
        """Test that current datetime is valid ISO format."""
        current_datetime = get_current_datetime("UTC")
        assert is_valid_iso_datetime(current_datetime) is True

    def test_add_subtract_days_roundtrip(self):
        """Test that add and subtract days are inverse operations."""
        original_date = "2025-07-08"
        days_to_add = 15

        # Add days then subtract the same amount
        added_date = add_days(original_date, days_to_add)
        result_date = subtract_days(added_date, days_to_add)

        assert result_date == original_date

    def test_multiple_timezone_consistency(self):
        """Test that date operations work consistently across timezones."""
        # All should return valid dates regardless of timezone
        timezones = ["UTC", "America/New_York", "Europe/London", "Asia/Tokyo"]

        for tz in timezones:
            current_date = get_current_date(tz)
            assert is_valid_iso_date(current_date) is True

            current_time = get_current_time(tz)
            assert is_valid_iso_time(current_time) is True

            current_datetime = get_current_datetime(tz)
            assert is_valid_iso_datetime(current_datetime) is True
