"""Tests for business day operations."""

import pytest

from basic_open_agent_tools.datetime.business import (
    get_next_business_day,
    is_business_day,
)


class TestGetNextBusinessDay:
    """Tests for get_next_business_day function."""

    def test_friday_to_monday(self):
        """Test next business day after Friday is Monday."""
        result = get_next_business_day("2025-07-04")  # Friday
        assert result == "2025-07-07"  # Monday

    def test_saturday_to_monday(self):
        """Test next business day after Saturday is Monday."""
        result = get_next_business_day("2025-07-05")  # Saturday
        assert result == "2025-07-07"  # Monday

    def test_sunday_to_monday(self):
        """Test next business day after Sunday is Monday."""
        result = get_next_business_day("2025-07-06")  # Sunday
        assert result == "2025-07-07"  # Monday

    def test_monday_to_tuesday(self):
        """Test next business day after Monday is Tuesday."""
        result = get_next_business_day("2025-07-07")  # Monday
        assert result == "2025-07-08"  # Tuesday

    def test_thursday_to_friday(self):
        """Test next business day after Thursday is Friday."""
        result = get_next_business_day("2025-07-03")  # Thursday
        assert result == "2025-07-04"  # Friday

    def test_year_boundary(self):
        """Test next business day across year boundary."""
        result = get_next_business_day("2024-12-31")  # Tuesday
        assert result == "2025-01-01"  # Wednesday

    def test_invalid_date(self):
        """Test with invalid date format."""
        with pytest.raises(ValueError, match="Invalid ISO date format"):
            get_next_business_day("not-a-date")

    def test_non_string_input(self):
        """Test with non-string input."""
        with pytest.raises(TypeError, match="date_string must be a string"):
            get_next_business_day(20250704)


class TestIsBusinessDay:
    """Tests for is_business_day function."""

    def test_monday_is_business_day(self):
        """Test that Monday is a business day."""
        assert is_business_day("2025-07-07") is True

    def test_tuesday_is_business_day(self):
        """Test that Tuesday is a business day."""
        assert is_business_day("2025-07-08") is True

    def test_wednesday_is_business_day(self):
        """Test that Wednesday is a business day."""
        assert is_business_day("2025-07-09") is True

    def test_thursday_is_business_day(self):
        """Test that Thursday is a business day."""
        assert is_business_day("2025-07-10") is True

    def test_friday_is_business_day(self):
        """Test that Friday is a business day."""
        assert is_business_day("2025-07-11") is True

    def test_saturday_not_business_day(self):
        """Test that Saturday is not a business day."""
        assert is_business_day("2025-07-05") is False

    def test_sunday_not_business_day(self):
        """Test that Sunday is not a business day."""
        assert is_business_day("2025-07-06") is False

    def test_invalid_date(self):
        """Test with invalid date format."""
        with pytest.raises(ValueError, match="Invalid ISO date format"):
            is_business_day("2025/07/07")

    def test_non_string_input(self):
        """Test with non-string input."""
        with pytest.raises(TypeError, match="date_string must be a string"):
            is_business_day(None)
