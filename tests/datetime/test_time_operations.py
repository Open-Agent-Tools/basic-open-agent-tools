"""Tests for extended time operations."""

import pytest

from basic_open_agent_tools.datetime.operations import (
    add_hours,
    add_minutes,
    calculate_time_difference,
    subtract_hours,
    subtract_minutes,
)


class TestAddHours:
    """Tests for add_hours function."""

    def test_add_positive_hours(self):
        """Test adding positive hours."""
        result = add_hours("2025-07-08T14:30:45", 2)
        assert result == "2025-07-08T16:30:45"

    def test_add_negative_hours(self):
        """Test adding negative hours (subtract)."""
        result = add_hours("2025-07-08T14:30:45", -3)
        assert result == "2025-07-08T11:30:45"

    def test_add_hours_cross_day(self):
        """Test adding hours that crosses day boundary."""
        result = add_hours("2025-07-08T22:30:45", 4)
        assert result == "2025-07-09T02:30:45"

    def test_add_hours_cross_month(self):
        """Test adding hours that crosses month boundary."""
        result = add_hours("2025-06-30T22:00:00", 5)
        assert result == "2025-07-01T03:00:00"

    def test_add_hours_cross_year(self):
        """Test adding hours that crosses year boundary."""
        result = add_hours("2024-12-31T23:00:00", 2)
        assert result == "2025-01-01T01:00:00"

    def test_add_zero_hours(self):
        """Test adding zero hours."""
        result = add_hours("2025-07-08T14:30:45", 0)
        assert result == "2025-07-08T14:30:45"

    def test_invalid_datetime(self):
        """Test with invalid datetime format."""
        with pytest.raises(ValueError, match="Invalid ISO datetime format"):
            add_hours("not-a-datetime", 2)

    def test_non_string_datetime(self):
        """Test with non-string datetime."""
        with pytest.raises(TypeError, match="datetime_string must be a string"):
            add_hours(None, 2)

    def test_non_integer_hours(self):
        """Test with non-integer hours."""
        with pytest.raises(TypeError, match="hours must be an integer"):
            add_hours("2025-07-08T14:30:45", "2")


class TestSubtractHours:
    """Tests for subtract_hours function."""

    def test_subtract_positive_hours(self):
        """Test subtracting positive hours."""
        result = subtract_hours("2025-07-08T14:30:45", 2)
        assert result == "2025-07-08T12:30:45"

    def test_subtract_hours_cross_day(self):
        """Test subtracting hours that crosses day boundary."""
        result = subtract_hours("2025-07-08T02:30:45", 4)
        assert result == "2025-07-07T22:30:45"

    def test_subtract_hours_cross_month(self):
        """Test subtracting hours that crosses month boundary."""
        result = subtract_hours("2025-07-01T03:00:00", 5)
        assert result == "2025-06-30T22:00:00"

    def test_subtract_hours_cross_year(self):
        """Test subtracting hours that crosses year boundary."""
        result = subtract_hours("2025-01-01T01:00:00", 2)
        assert result == "2024-12-31T23:00:00"

    def test_subtract_negative_hours(self):
        """Test subtracting negative hours raises error."""
        with pytest.raises(ValueError, match="hours must be positive"):
            subtract_hours("2025-07-08T14:30:45", -2)

    def test_invalid_datetime(self):
        """Test with invalid datetime format."""
        with pytest.raises(ValueError, match="Invalid ISO datetime format"):
            subtract_hours("invalid", 2)

    def test_non_string_datetime(self):
        """Test with non-string datetime."""
        with pytest.raises(TypeError, match="datetime_string must be a string"):
            subtract_hours(20250708, 2)

    def test_non_integer_hours(self):
        """Test with non-integer hours."""
        with pytest.raises(TypeError, match="hours must be an integer"):
            subtract_hours("2025-07-08T14:30:45", 2.5)


class TestAddMinutes:
    """Tests for add_minutes function."""

    def test_add_positive_minutes(self):
        """Test adding positive minutes."""
        result = add_minutes("2025-07-08T14:30:45", 30)
        assert result == "2025-07-08T15:00:45"

    def test_add_negative_minutes(self):
        """Test adding negative minutes (subtract)."""
        result = add_minutes("2025-07-08T14:30:45", -15)
        assert result == "2025-07-08T14:15:45"

    def test_add_minutes_cross_hour(self):
        """Test adding minutes that crosses hour boundary."""
        result = add_minutes("2025-07-08T14:45:30", 20)
        assert result == "2025-07-08T15:05:30"

    def test_add_minutes_cross_day(self):
        """Test adding minutes that crosses day boundary."""
        result = add_minutes("2025-07-08T23:45:00", 30)
        assert result == "2025-07-09T00:15:00"

    def test_add_zero_minutes(self):
        """Test adding zero minutes."""
        result = add_minutes("2025-07-08T14:30:45", 0)
        assert result == "2025-07-08T14:30:45"

    def test_add_large_minutes(self):
        """Test adding large number of minutes."""
        result = add_minutes("2025-07-08T14:30:45", 1440)  # 24 hours
        assert result == "2025-07-09T14:30:45"

    def test_invalid_datetime(self):
        """Test with invalid datetime format."""
        with pytest.raises(ValueError, match="Invalid ISO datetime format"):
            add_minutes("2025/07/08 14:30:45", 30)

    def test_non_string_datetime(self):
        """Test with non-string datetime."""
        with pytest.raises(TypeError, match="datetime_string must be a string"):
            add_minutes(None, 30)

    def test_non_integer_minutes(self):
        """Test with non-integer minutes."""
        with pytest.raises(TypeError, match="minutes must be an integer"):
            add_minutes("2025-07-08T14:30:45", "30")


class TestSubtractMinutes:
    """Tests for subtract_minutes function."""

    def test_subtract_positive_minutes(self):
        """Test subtracting positive minutes."""
        result = subtract_minutes("2025-07-08T14:30:45", 15)
        assert result == "2025-07-08T14:15:45"

    def test_subtract_minutes_cross_hour(self):
        """Test subtracting minutes that crosses hour boundary."""
        result = subtract_minutes("2025-07-08T15:10:30", 20)
        assert result == "2025-07-08T14:50:30"

    def test_subtract_minutes_cross_day(self):
        """Test subtracting minutes that crosses day boundary."""
        result = subtract_minutes("2025-07-08T00:15:00", 30)
        assert result == "2025-07-07T23:45:00"

    def test_subtract_large_minutes(self):
        """Test subtracting large number of minutes."""
        result = subtract_minutes("2025-07-08T14:30:45", 1440)  # 24 hours
        assert result == "2025-07-07T14:30:45"

    def test_subtract_negative_minutes(self):
        """Test subtracting negative minutes raises error."""
        with pytest.raises(ValueError, match="minutes must be positive"):
            subtract_minutes("2025-07-08T14:30:45", -15)

    def test_invalid_datetime(self):
        """Test with invalid datetime format."""
        with pytest.raises(ValueError, match="Invalid ISO datetime format"):
            subtract_minutes("not-valid", 15)

    def test_non_string_datetime(self):
        """Test with non-string datetime."""
        with pytest.raises(TypeError, match="datetime_string must be a string"):
            subtract_minutes(["2025-07-08T14:30:45"], 15)

    def test_non_integer_minutes(self):
        """Test with non-integer minutes."""
        with pytest.raises(TypeError, match="minutes must be an integer"):
            subtract_minutes("2025-07-08T14:30:45", None)


class TestCalculateTimeDifference:
    """Tests for calculate_time_difference function."""

    def test_difference_in_seconds(self):
        """Test time difference in seconds."""
        result = calculate_time_difference("14:30:00", "14:32:30", "seconds")
        assert result == 150

    def test_difference_in_minutes(self):
        """Test time difference in minutes."""
        result = calculate_time_difference("14:30:00", "16:45:00", "minutes")
        assert result == 135

    def test_difference_in_hours(self):
        """Test time difference in hours."""
        result = calculate_time_difference("09:00:00", "17:00:00", "hours")
        assert result == 8

    def test_negative_difference(self):
        """Test negative difference when time2 is before time1."""
        result = calculate_time_difference("16:00:00", "14:00:00", "hours")
        assert result == -2

    def test_same_time(self):
        """Test difference when times are the same."""
        result = calculate_time_difference("14:30:00", "14:30:00", "seconds")
        assert result == 0

    def test_with_microseconds(self):
        """Test with times including microseconds."""
        result = calculate_time_difference(
            "14:30:00.000000", "14:30:30.500000", "seconds"
        )
        assert result == 30

    def test_invalid_unit(self):
        """Test with invalid unit."""
        with pytest.raises(
            ValueError, match="unit must be 'hours', 'minutes', or 'seconds'"
        ):
            calculate_time_difference("14:30:00", "15:30:00", "days")

    def test_invalid_time1(self):
        """Test with invalid time1 format."""
        with pytest.raises(ValueError, match="Invalid ISO time format"):
            calculate_time_difference("not-a-time", "15:30:00", "minutes")

    def test_invalid_time2(self):
        """Test with invalid time2 format."""
        with pytest.raises(ValueError, match="Invalid ISO time format"):
            calculate_time_difference("14:30:00", "25:00:00", "minutes")

    def test_non_string_time1(self):
        """Test with non-string time1."""
        with pytest.raises(TypeError, match="time1 must be a string"):
            calculate_time_difference(None, "15:30:00", "minutes")

    def test_non_string_time2(self):
        """Test with non-string time2."""
        with pytest.raises(TypeError, match="time2 must be a string"):
            calculate_time_difference("14:30:00", None, "minutes")

    def test_non_string_unit(self):
        """Test with non-string unit."""
        with pytest.raises(TypeError, match="unit must be a string"):
            calculate_time_difference("14:30:00", "15:30:00", None)
