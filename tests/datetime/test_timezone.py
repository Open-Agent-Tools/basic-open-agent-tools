"""Tests for timezone operations."""

import pytest

from basic_open_agent_tools.datetime.timezone import (
    convert_timezone,
    get_timezone_offset,
    is_daylight_saving_time,
    is_valid_timezone,
)


class TestConvertTimezone:
    """Tests for convert_timezone function."""

    def test_utc_to_eastern(self):
        """Test converting from UTC to Eastern time."""
        result = convert_timezone("2025-07-08T14:30:45", "UTC", "America/New_York")
        # During DST, Eastern is UTC-4
        assert "10:30:45" in result
        assert "-04:00" in result

    def test_eastern_to_pacific(self):
        """Test converting from Eastern to Pacific time."""
        result = convert_timezone(
            "2025-07-08T10:30:45", "America/New_York", "America/Los_Angeles"
        )
        # Pacific is 3 hours behind Eastern
        assert "07:30:45" in result

    def test_utc_to_utc(self):
        """Test converting from UTC to UTC (no change)."""
        result = convert_timezone("2025-07-08T14:30:45", "UTC", "UTC")
        assert "14:30:45" in result

    def test_winter_time(self):
        """Test converting during winter (no DST)."""
        result = convert_timezone("2025-01-08T14:30:45", "UTC", "America/New_York")
        # During winter, Eastern is UTC-5
        assert "09:30:45" in result
        assert "-05:00" in result

    def test_invalid_datetime(self):
        """Test with invalid datetime format."""
        with pytest.raises(ValueError, match="Timezone conversion failed"):
            convert_timezone("not-a-datetime", "UTC", "America/New_York")

    def test_invalid_from_timezone(self):
        """Test with invalid source timezone."""
        with pytest.raises(ValueError, match="Timezone conversion failed"):
            convert_timezone("2025-07-08T14:30:45", "Invalid/Zone", "UTC")

    def test_invalid_to_timezone(self):
        """Test with invalid target timezone."""
        with pytest.raises(ValueError, match="Timezone conversion failed"):
            convert_timezone("2025-07-08T14:30:45", "UTC", "Invalid/Zone")

    def test_non_string_datetime(self):
        """Test with non-string datetime."""
        with pytest.raises(TypeError, match="datetime_string must be a string"):
            convert_timezone(20250708, "UTC", "America/New_York")

    def test_non_string_from_timezone(self):
        """Test with non-string from_timezone."""
        with pytest.raises(TypeError, match="from_timezone must be a string"):
            convert_timezone("2025-07-08T14:30:45", None, "America/New_York")

    def test_non_string_to_timezone(self):
        """Test with non-string to_timezone."""
        with pytest.raises(TypeError, match="to_timezone must be a string"):
            convert_timezone("2025-07-08T14:30:45", "UTC", None)


class TestGetTimezoneOffset:
    """Tests for get_timezone_offset function."""

    def test_utc_offset(self):
        """Test UTC has zero offset."""
        result = get_timezone_offset("UTC")
        assert result == "+00:00"

    def test_eastern_summer_offset(self):
        """Test Eastern time offset during summer (varies by actual date)."""
        result = get_timezone_offset("America/New_York")
        assert result in ["-04:00", "-05:00"]  # EDT or EST

    def test_pacific_offset(self):
        """Test Pacific time offset."""
        result = get_timezone_offset("America/Los_Angeles")
        assert result in ["-07:00", "-08:00"]  # PDT or PST

    def test_positive_offset(self):
        """Test timezone with positive offset."""
        result = get_timezone_offset("Europe/Paris")
        assert result in ["+01:00", "+02:00"]  # CET or CEST

    def test_invalid_timezone(self):
        """Test with invalid timezone."""
        with pytest.raises(ValueError, match="Invalid timezone"):
            get_timezone_offset("Invalid/Timezone")

    def test_non_string_input(self):
        """Test with non-string input."""
        with pytest.raises(TypeError, match="timezone must be a string"):
            get_timezone_offset(123)


class TestIsDaylightSavingTime:
    """Tests for is_daylight_saving_time function."""

    def test_summer_dst_true(self):
        """Test DST is active in summer for New York."""
        result = is_daylight_saving_time("2025-07-08T14:30:45", "America/New_York")
        assert result is True

    def test_winter_dst_false(self):
        """Test DST is not active in winter for New York."""
        result = is_daylight_saving_time("2025-01-08T14:30:45", "America/New_York")
        assert result is False

    def test_no_dst_timezone(self):
        """Test timezone that doesn't observe DST."""
        result = is_daylight_saving_time("2025-07-08T14:30:45", "UTC")
        assert result is False

    def test_arizona_no_dst(self):
        """Test Arizona doesn't observe DST."""
        result = is_daylight_saving_time("2025-07-08T14:30:45", "America/Phoenix")
        assert result is False

    def test_invalid_datetime(self):
        """Test with invalid datetime format."""
        with pytest.raises(ValueError, match="DST check failed"):
            is_daylight_saving_time("not-a-datetime", "America/New_York")

    def test_invalid_timezone(self):
        """Test with invalid timezone."""
        with pytest.raises(ValueError, match="DST check failed"):
            is_daylight_saving_time("2025-07-08T14:30:45", "Invalid/Zone")

    def test_non_string_datetime(self):
        """Test with non-string datetime."""
        with pytest.raises(TypeError, match="datetime_string must be a string"):
            is_daylight_saving_time(None, "America/New_York")

    def test_non_string_timezone(self):
        """Test with non-string timezone."""
        with pytest.raises(TypeError, match="timezone must be a string"):
            is_daylight_saving_time("2025-07-08T14:30:45", None)


class TestIsValidTimezone:
    """Tests for is_valid_timezone function."""

    def test_valid_utc(self):
        """Test UTC is valid."""
        assert is_valid_timezone("UTC") is True

    def test_valid_eastern(self):
        """Test Eastern timezone is valid."""
        assert is_valid_timezone("America/New_York") is True

    def test_valid_pacific(self):
        """Test Pacific timezone is valid."""
        assert is_valid_timezone("America/Los_Angeles") is True

    def test_valid_european(self):
        """Test European timezone is valid."""
        assert is_valid_timezone("Europe/London") is True

    def test_invalid_timezone(self):
        """Test invalid timezone returns False."""
        assert is_valid_timezone("Invalid/Timezone") is False

    def test_empty_string(self):
        """Test empty string returns False."""
        assert is_valid_timezone("") is False

    def test_random_string(self):
        """Test random string returns False."""
        assert is_valid_timezone("NotATimezone") is False

    def test_non_string_input(self):
        """Test with non-string input."""
        with pytest.raises(TypeError, match="timezone_string must be a string"):
            is_valid_timezone(None)
