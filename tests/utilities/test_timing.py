"""Tests for timing utilities."""

import time
from unittest.mock import patch

import pytest

from basic_open_agent_tools.exceptions import BasicAgentToolsError
from basic_open_agent_tools.utilities.timing import (
    precise_sleep,
    sleep_milliseconds,
    sleep_seconds,
)


class TestSleepSeconds:
    """Test the sleep_seconds function."""

    def test_invalid_input_type(self):
        """Test error handling for invalid input types."""
        with pytest.raises(BasicAgentToolsError, match="Seconds must be a number"):
            sleep_seconds("invalid")

        with pytest.raises(BasicAgentToolsError, match="Seconds must be a number"):
            sleep_seconds(None)

    def test_negative_seconds(self):
        """Test error handling for negative seconds."""
        with pytest.raises(BasicAgentToolsError, match="Seconds cannot be negative"):
            sleep_seconds(-1)

    def test_too_large_seconds(self):
        """Test error handling for seconds greater than 1 hour."""
        with pytest.raises(
            BasicAgentToolsError, match="Maximum sleep duration is 3600 seconds"
        ):
            sleep_seconds(3601)

    def test_successful_sleep(self):
        """Test successful sleep operation."""
        start_time = time.time()
        result = sleep_seconds(0.1)  # 100ms
        end_time = time.time()

        assert result["status"] == "completed"
        assert result["requested_seconds"] == 0.1
        assert 0.09 <= result["actual_seconds"] <= 0.2  # Allow some variance
        assert 0.09 <= (end_time - start_time) <= 0.2
        assert "Successfully slept" in result["message"]

    def test_zero_seconds(self):
        """Test sleep with zero seconds."""
        result = sleep_seconds(0)

        assert result["status"] == "completed"
        assert result["requested_seconds"] == 0.0
        assert result["actual_seconds"] >= 0

    def test_fractional_seconds(self):
        """Test sleep with fractional seconds."""
        result = sleep_seconds(0.05)  # 50ms

        assert result["status"] == "completed"
        assert result["requested_seconds"] == 0.05
        assert 0.04 <= result["actual_seconds"] <= 0.1

    @patch("time.sleep")
    def test_keyboard_interrupt_handling(self, mock_sleep):
        """Test handling of KeyboardInterrupt during sleep."""
        mock_sleep.side_effect = KeyboardInterrupt()

        result = sleep_seconds(1.0)

        assert result["status"] == "interrupted"
        assert result["requested_seconds"] == 1.0
        assert result["actual_seconds"] < 1.0
        assert "Sleep interrupted" in result["message"]

    @patch("signal.signal")
    def test_signal_handler_setup_failure(self, mock_signal):
        """Test graceful handling when signal setup fails."""
        mock_signal.side_effect = ValueError("Signal not available")

        # Should still work even if signal handling fails
        result = sleep_seconds(0.01)

        assert result["status"] == "completed"


class TestSleepMilliseconds:
    """Test the sleep_milliseconds function."""

    def test_invalid_input_type(self):
        """Test error handling for invalid input types."""
        with pytest.raises(BasicAgentToolsError, match="Milliseconds must be a number"):
            sleep_milliseconds("invalid")

    def test_negative_milliseconds(self):
        """Test error handling for negative milliseconds."""
        with pytest.raises(
            BasicAgentToolsError, match="Milliseconds cannot be negative"
        ):
            sleep_milliseconds(-1)

    def test_successful_sleep_milliseconds(self):
        """Test successful sleep in milliseconds."""
        result = sleep_milliseconds(100)  # 100ms

        assert result["status"] == "completed"
        assert result["requested_milliseconds"] == 100.0
        assert result["requested_seconds"] == 0.1
        assert 90 <= result["actual_milliseconds"] <= 200  # Allow variance

    def test_zero_milliseconds(self):
        """Test sleep with zero milliseconds."""
        result = sleep_milliseconds(0)

        assert result["status"] == "completed"
        assert result["requested_milliseconds"] == 0.0
        assert result["actual_milliseconds"] >= 0

    def test_fractional_milliseconds(self):
        """Test sleep with fractional milliseconds."""
        result = sleep_milliseconds(50.5)

        assert result["status"] == "completed"
        assert result["requested_milliseconds"] == 50.5
        assert result["requested_seconds"] == 0.0505


class TestPreciseSleep:
    """Test the precise_sleep function."""

    def test_invalid_input_type(self):
        """Test error handling for invalid input types."""
        with pytest.raises(BasicAgentToolsError, match="Seconds must be a number"):
            precise_sleep("invalid")

    def test_negative_seconds(self):
        """Test error handling for negative seconds."""
        with pytest.raises(BasicAgentToolsError, match="Seconds cannot be negative"):
            precise_sleep(-1)

    def test_too_large_seconds(self):
        """Test error handling for seconds greater than 60."""
        with pytest.raises(
            BasicAgentToolsError, match="Maximum precise sleep duration is 60 seconds"
        ):
            precise_sleep(61)

    def test_short_precise_sleep(self):
        """Test precise sleep for very short durations."""
        start_time = time.time()
        result = precise_sleep(0.001)  # 1ms
        end_time = time.time()

        assert result["status"] == "completed"
        assert result["requested_seconds"] == 0.001
        assert result["precision"] == "high"
        assert (
            0.0005 <= result["actual_seconds"] <= 0.005
        )  # Allow some variance for precision
        assert 0.0005 <= (end_time - start_time) <= 0.005

    def test_longer_precise_sleep(self):
        """Test precise sleep for longer durations that use both sleep and busy-wait."""
        start_time = time.time()
        result = precise_sleep(0.05)  # 50ms
        end_time = time.time()

        assert result["status"] == "completed"
        assert result["requested_seconds"] == 0.05
        assert result["precision"] == "high"
        assert 0.045 <= result["actual_seconds"] <= 0.065
        assert 0.045 <= (end_time - start_time) <= 0.065

    @patch("time.sleep")
    @patch("time.time")
    def test_precise_sleep_logic(self, mock_time, mock_sleep):
        """Test the logic of combining sleep and busy-wait."""
        # Mock time progression with enough values for all calls
        # Start time, after regular sleep, then busy-wait progression, final time
        time_values = [0.0, 0.04, 0.049, 0.0499, 0.05, 0.051]
        mock_time.side_effect = time_values

        result = precise_sleep(0.05)

        # Should call regular sleep for most of the duration
        mock_sleep.assert_called_once_with(0.04)  # 0.05 - 0.01

        # Verify result structure
        assert result["status"] == "completed"
        assert result["requested_seconds"] == 0.05

    def test_very_short_precise_sleep(self):
        """Test precise sleep for durations shorter than 10ms threshold."""
        result = precise_sleep(0.005)  # 5ms

        assert result["status"] == "completed"
        assert result["requested_seconds"] == 0.005
        assert result["precision"] == "high"

    def test_zero_precise_sleep(self):
        """Test precise sleep with zero duration."""
        result = precise_sleep(0)

        assert result["status"] == "completed"
        assert result["requested_seconds"] == 0.0
        assert result["actual_seconds"] >= 0
