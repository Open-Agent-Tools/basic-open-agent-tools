"""Agent evaluation tests for datetime tools.

This module tests all datetime functions with Google ADK compatibility
to ensure they work properly when integrated into agent frameworks.
"""

import pytest

from basic_open_agent_tools.datetime import (
    # Time operations
    add_hours,
    add_minutes,
    calculate_time_difference,
    # Timezone
    convert_timezone,
    # Date info
    get_day_of_year,
    get_days_in_month,
    get_month_name,
    # Business days
    get_next_business_day,
    get_timezone_offset,
    get_week_number,
    get_weekday_name,
    is_business_day,
    is_daylight_saving_time,
    # Validation
    is_future_date,
    is_leap_year,
    is_past_date,
    is_valid_date_format,
    is_valid_timezone,
    subtract_hours,
    subtract_minutes,
    validate_date_range,
    validate_datetime_range,
)


@pytest.mark.agent_evaluation
class TestDateTimeAgentEvaluation:
    """Test datetime functions for agent framework compatibility."""

    def test_time_operations_agent(self):
        """Test time operations with agent-style inputs."""
        # Add hours
        result = add_hours("2025-07-08T14:30:45", 2)
        assert isinstance(result, str)
        assert "16:30:45" in result

        # Subtract hours
        result = subtract_hours("2025-07-08T14:30:45", 2)
        assert isinstance(result, str)
        assert "12:30:45" in result

        # Add minutes
        result = add_minutes("2025-07-08T14:30:45", 30)
        assert isinstance(result, str)
        assert "15:00:45" in result

        # Subtract minutes
        result = subtract_minutes("2025-07-08T14:30:45", 15)
        assert isinstance(result, str)
        assert "14:15:45" in result

        # Calculate time difference
        result = calculate_time_difference("14:30:00", "16:45:00", "minutes")
        assert isinstance(result, int)
        assert result == 135

    def test_date_info_agent(self):
        """Test date information extraction with agent-style inputs."""
        # Get weekday name
        result = get_weekday_name("2025-07-08")
        assert isinstance(result, str)
        assert result == "Tuesday"

        # Get month name
        result = get_month_name("2025-07-08")
        assert isinstance(result, str)
        assert result == "July"

        # Get week number
        result = get_week_number("2025-07-08")
        assert isinstance(result, int)
        assert result == 28

        # Get day of year
        result = get_day_of_year("2025-07-08")
        assert isinstance(result, int)
        assert result == 189

        # Is leap year
        result = is_leap_year(2024)
        assert isinstance(result, bool)
        assert result is True

        # Get days in month
        result = get_days_in_month(2025, 7)
        assert isinstance(result, int)
        assert result == 31

    def test_business_day_agent(self):
        """Test business day operations with agent-style inputs."""
        # Get next business day
        result = get_next_business_day("2025-07-04")  # Friday
        assert isinstance(result, str)
        assert result == "2025-07-07"  # Monday

        # Is business day
        result = is_business_day("2025-07-07")  # Monday
        assert isinstance(result, bool)
        assert result is True

        result = is_business_day("2025-07-05")  # Saturday
        assert isinstance(result, bool)
        assert result is False

    def test_timezone_operations_agent(self):
        """Test timezone operations with agent-style inputs."""
        # Convert timezone
        result = convert_timezone("2025-07-08T14:30:45", "UTC", "America/New_York")
        assert isinstance(result, str)
        assert "10:30:45" in result

        # Get timezone offset
        result = get_timezone_offset("UTC")
        assert isinstance(result, str)
        assert result == "+00:00"

        # Is daylight saving time
        result = is_daylight_saving_time("2025-07-08T14:30:45", "America/New_York")
        assert isinstance(result, bool)
        assert result is True

        # Is valid timezone
        result = is_valid_timezone("America/New_York")
        assert isinstance(result, bool)
        assert result is True

    def test_validation_operations_agent(self):
        """Test validation operations with agent-style inputs."""
        # Validate date range
        result = validate_date_range("2025-06-15", "2025-01-01", "2025-12-31")
        assert isinstance(result, bool)
        assert result is True

        # Validate datetime range
        result = validate_datetime_range(
            "2025-06-15T12:00:00", "2025-01-01T00:00:00", "2025-12-31T23:59:59"
        )
        assert isinstance(result, bool)
        assert result is True

        # Is valid date format
        result = is_valid_date_format("2025-07-08", "%Y-%m-%d")
        assert isinstance(result, bool)
        assert result is True

        # Is future date
        result = is_future_date("2025-07-09", "2025-07-08")
        assert isinstance(result, bool)
        assert result is True

        # Is past date
        result = is_past_date("2025-07-07", "2025-07-08")
        assert isinstance(result, bool)
        assert result is True

    def test_agent_error_handling(self):
        """Test error handling with agent-style invalid inputs."""
        # Test with invalid datetime
        with pytest.raises(ValueError):
            add_hours("not-a-datetime", 2)

        # Test with wrong type
        with pytest.raises(TypeError):
            add_hours(None, 2)

        # Test with invalid timezone
        with pytest.raises(ValueError):
            convert_timezone("2025-07-08T14:30:45", "Invalid/Zone", "UTC")

        # Test with invalid unit
        with pytest.raises(ValueError):
            calculate_time_difference("14:30:00", "16:30:00", "invalid_unit")

    def test_agent_json_serializable_outputs(self):
        """Verify all outputs are JSON-serializable for agent frameworks."""
        import json

        # String outputs
        assert json.dumps(add_hours("2025-07-08T14:30:45", 2))
        assert json.dumps(get_weekday_name("2025-07-08"))
        assert json.dumps(get_next_business_day("2025-07-04"))
        assert json.dumps(get_timezone_offset("UTC"))

        # Integer outputs
        assert json.dumps(calculate_time_difference("14:30:00", "16:30:00", "minutes"))
        assert json.dumps(get_week_number("2025-07-08"))
        assert json.dumps(get_day_of_year("2025-07-08"))
        assert json.dumps(get_days_in_month(2025, 7))

        # Boolean outputs
        assert json.dumps(is_leap_year(2024))
        assert json.dumps(is_business_day("2025-07-07"))
        assert json.dumps(is_valid_timezone("UTC"))
        assert json.dumps(validate_date_range("2025-06-15", "2025-01-01", "2025-12-31"))
