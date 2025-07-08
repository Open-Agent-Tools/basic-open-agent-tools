"""Tests for datetime validation utilities."""

import pytest

from basic_open_agent_tools.datetime.validation import (
    is_future_date,
    is_past_date,
    is_valid_date_format,
    validate_date_range,
    validate_datetime_range,
)


class TestValidateDateRange:
    """Tests for validate_date_range function."""

    def test_date_within_range(self):
        """Test date within valid range."""
        result = validate_date_range("2025-06-15", "2025-01-01", "2025-12-31")
        assert result is True

    def test_date_at_min_boundary(self):
        """Test date at minimum boundary."""
        result = validate_date_range("2025-01-01", "2025-01-01", "2025-12-31")
        assert result is True

    def test_date_at_max_boundary(self):
        """Test date at maximum boundary."""
        result = validate_date_range("2025-12-31", "2025-01-01", "2025-12-31")
        assert result is True

    def test_date_before_range(self):
        """Test date before valid range."""
        result = validate_date_range("2024-12-31", "2025-01-01", "2025-12-31")
        assert result is False

    def test_date_after_range(self):
        """Test date after valid range."""
        result = validate_date_range("2026-01-01", "2025-01-01", "2025-12-31")
        assert result is False

    def test_invalid_date_string(self):
        """Test with invalid date format."""
        with pytest.raises(ValueError, match="Invalid ISO date format"):
            validate_date_range("not-a-date", "2025-01-01", "2025-12-31")

    def test_invalid_min_date(self):
        """Test with invalid min_date format."""
        with pytest.raises(ValueError, match="Invalid ISO date format"):
            validate_date_range("2025-06-15", "invalid", "2025-12-31")

    def test_invalid_max_date(self):
        """Test with invalid max_date format."""
        with pytest.raises(ValueError, match="Invalid ISO date format"):
            validate_date_range("2025-06-15", "2025-01-01", "invalid")

    def test_non_string_date(self):
        """Test with non-string date_string."""
        with pytest.raises(TypeError, match="date_string must be a string"):
            validate_date_range(20250615, "2025-01-01", "2025-12-31")

    def test_non_string_min_date(self):
        """Test with non-string min_date."""
        with pytest.raises(TypeError, match="min_date must be a string"):
            validate_date_range("2025-06-15", None, "2025-12-31")

    def test_non_string_max_date(self):
        """Test with non-string max_date."""
        with pytest.raises(TypeError, match="max_date must be a string"):
            validate_date_range("2025-06-15", "2025-01-01", None)


class TestValidateDatetimeRange:
    """Tests for validate_datetime_range function."""

    def test_datetime_within_range(self):
        """Test datetime within valid range."""
        result = validate_datetime_range(
            "2025-06-15T12:00:00", "2025-01-01T00:00:00", "2025-12-31T23:59:59"
        )
        assert result is True

    def test_datetime_at_min_boundary(self):
        """Test datetime at minimum boundary."""
        result = validate_datetime_range(
            "2025-01-01T00:00:00", "2025-01-01T00:00:00", "2025-12-31T23:59:59"
        )
        assert result is True

    def test_datetime_at_max_boundary(self):
        """Test datetime at maximum boundary."""
        result = validate_datetime_range(
            "2025-12-31T23:59:59", "2025-01-01T00:00:00", "2025-12-31T23:59:59"
        )
        assert result is True

    def test_datetime_before_range(self):
        """Test datetime before valid range."""
        result = validate_datetime_range(
            "2024-12-31T23:59:59", "2025-01-01T00:00:00", "2025-12-31T23:59:59"
        )
        assert result is False

    def test_datetime_after_range(self):
        """Test datetime after valid range."""
        result = validate_datetime_range(
            "2026-01-01T00:00:00", "2025-01-01T00:00:00", "2025-12-31T23:59:59"
        )
        assert result is False

    def test_same_date_different_times(self):
        """Test same date but different times."""
        result = validate_datetime_range(
            "2025-06-15T14:30:00", "2025-06-15T12:00:00", "2025-06-15T18:00:00"
        )
        assert result is True

    def test_invalid_datetime_string(self):
        """Test with invalid datetime format."""
        with pytest.raises(ValueError, match="Invalid ISO datetime format"):
            validate_datetime_range(
                "not-a-datetime", "2025-01-01T00:00:00", "2025-12-31T23:59:59"
            )

    def test_non_string_datetime(self):
        """Test with non-string datetime_string."""
        with pytest.raises(TypeError, match="datetime_string must be a string"):
            validate_datetime_range(None, "2025-01-01T00:00:00", "2025-12-31T23:59:59")

    def test_non_string_min_datetime(self):
        """Test with non-string min_datetime."""
        with pytest.raises(TypeError, match="min_datetime must be a string"):
            validate_datetime_range("2025-06-15T12:00:00", None, "2025-12-31T23:59:59")

    def test_non_string_max_datetime(self):
        """Test with non-string max_datetime."""
        with pytest.raises(TypeError, match="max_datetime must be a string"):
            validate_datetime_range("2025-06-15T12:00:00", "2025-01-01T00:00:00", None)


class TestIsValidDateFormat:
    """Tests for is_valid_date_format function."""

    def test_iso_format_valid(self):
        """Test ISO format date is valid."""
        result = is_valid_date_format("2025-07-08", "%Y-%m-%d")
        assert result is True

    def test_us_format_valid(self):
        """Test US format date is valid."""
        result = is_valid_date_format("07/08/2025", "%m/%d/%Y")
        assert result is True

    def test_european_format_valid(self):
        """Test European format date is valid."""
        result = is_valid_date_format("08.07.2025", "%d.%m.%Y")
        assert result is True

    def test_wrong_format(self):
        """Test date with wrong format returns False."""
        result = is_valid_date_format("07/08/2025", "%Y-%m-%d")
        assert result is False

    def test_invalid_date(self):
        """Test invalid date returns False."""
        result = is_valid_date_format("2025-13-01", "%Y-%m-%d")
        assert result is False

    def test_datetime_format(self):
        """Test datetime format validation."""
        result = is_valid_date_format("2025-07-08 14:30:45", "%Y-%m-%d %H:%M:%S")
        assert result is True

    def test_non_string_date(self):
        """Test with non-string date_string."""
        with pytest.raises(TypeError, match="date_string must be a string"):
            is_valid_date_format(20250708, "%Y-%m-%d")

    def test_non_string_format(self):
        """Test with non-string format_string."""
        with pytest.raises(TypeError, match="format_string must be a string"):
            is_valid_date_format("2025-07-08", None)


class TestIsFutureDate:
    """Tests for is_future_date function."""

    def test_future_date(self):
        """Test date in future returns True."""
        result = is_future_date("2025-07-09", "2025-07-08")
        assert result is True

    def test_past_date(self):
        """Test date in past returns False."""
        result = is_future_date("2025-07-07", "2025-07-08")
        assert result is False

    def test_same_date(self):
        """Test same date returns False."""
        result = is_future_date("2025-07-08", "2025-07-08")
        assert result is False

    def test_far_future(self):
        """Test date far in future returns True."""
        result = is_future_date("2030-01-01", "2025-07-08")
        assert result is True

    def test_invalid_date_string(self):
        """Test with invalid date format."""
        with pytest.raises(ValueError, match="Invalid ISO date format"):
            is_future_date("not-a-date", "2025-07-08")

    def test_invalid_reference_date(self):
        """Test with invalid reference date format."""
        with pytest.raises(ValueError, match="Invalid ISO date format"):
            is_future_date("2025-07-09", "invalid")

    def test_non_string_date(self):
        """Test with non-string date_string."""
        with pytest.raises(TypeError, match="date_string must be a string"):
            is_future_date(None, "2025-07-08")

    def test_non_string_reference(self):
        """Test with non-string reference_date."""
        with pytest.raises(TypeError, match="reference_date must be a string"):
            is_future_date("2025-07-09", None)


class TestIsPastDate:
    """Tests for is_past_date function."""

    def test_past_date(self):
        """Test date in past returns True."""
        result = is_past_date("2025-07-07", "2025-07-08")
        assert result is True

    def test_future_date(self):
        """Test date in future returns False."""
        result = is_past_date("2025-07-09", "2025-07-08")
        assert result is False

    def test_same_date(self):
        """Test same date returns False."""
        result = is_past_date("2025-07-08", "2025-07-08")
        assert result is False

    def test_far_past(self):
        """Test date far in past returns True."""
        result = is_past_date("2020-01-01", "2025-07-08")
        assert result is True

    def test_invalid_date_string(self):
        """Test with invalid date format."""
        with pytest.raises(ValueError, match="Invalid ISO date format"):
            is_past_date("not-a-date", "2025-07-08")

    def test_invalid_reference_date(self):
        """Test with invalid reference date format."""
        with pytest.raises(ValueError, match="Invalid ISO date format"):
            is_past_date("2025-07-07", "invalid")

    def test_non_string_date(self):
        """Test with non-string date_string."""
        with pytest.raises(TypeError, match="date_string must be a string"):
            is_past_date(None, "2025-07-08")

    def test_non_string_reference(self):
        """Test with non-string reference_date."""
        with pytest.raises(TypeError, match="reference_date must be a string"):
            is_past_date("2025-07-07", None)
