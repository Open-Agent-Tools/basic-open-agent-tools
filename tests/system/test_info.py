"""Tests for system information tools."""

from unittest.mock import Mock, patch

import pytest

from basic_open_agent_tools.exceptions import BasicAgentToolsError
from basic_open_agent_tools.system.info import (
    get_cpu_info,
    get_disk_usage,
    get_memory_info,
    get_system_info,
    get_uptime,
)


class TestGetSystemInfo:
    """Test the get_system_info function."""

    def test_successful_system_info_retrieval(self):
        """Test successful system information retrieval."""
        result = get_system_info()

        # Check that all expected keys are present
        expected_keys = [
            "system",
            "release",
            "version",
            "machine",
            "processor",
            "architecture",
            "platform",
            "node",
            "python_version",
        ]

        for key in expected_keys:
            assert key in result

        # Check that values are strings
        for _key, value in result.items():
            assert isinstance(value, str)

        # Basic validation - system should not be empty
        assert len(result["system"]) > 0


class TestGetCpuInfo:
    """Test the get_cpu_info function."""

    def test_psutil_not_available_error(self):
        """Test error when psutil is not available."""
        with patch("basic_open_agent_tools.system.info.HAS_PSUTIL", False):
            with pytest.raises(BasicAgentToolsError, match="psutil package required"):
                get_cpu_info()

    @patch("basic_open_agent_tools.system.info.HAS_PSUTIL", True)
    @patch("basic_open_agent_tools.system.info.psutil")
    def test_successful_cpu_info_retrieval(self, mock_psutil):
        """Test successful CPU information retrieval."""
        # Mock psutil functions
        mock_psutil.cpu_percent.return_value = 25.5
        mock_psutil.cpu_count.return_value = 4
        mock_freq = Mock()
        mock_freq.current = 2400.0
        mock_freq.min = 1200.0
        mock_freq.max = 3600.0
        mock_psutil.cpu_freq.return_value = mock_freq

        result = get_cpu_info()

        expected_keys = [
            "usage_percent",
            "physical_cores",
            "logical_cores",
            "processor",
            "current_frequency_mhz",
            "min_frequency_mhz",
            "max_frequency_mhz",
        ]

        for key in expected_keys:
            assert key in result

        assert result["usage_percent"] == 25.5
        assert result["physical_cores"] == 4
        assert result["current_frequency_mhz"] == 2400.0

    @patch("basic_open_agent_tools.system.info.HAS_PSUTIL", True)
    @patch("basic_open_agent_tools.system.info.psutil")
    def test_cpu_info_without_frequency(self, mock_psutil):
        """Test CPU info retrieval when frequency info is not available."""
        mock_psutil.cpu_percent.return_value = 25.5
        mock_psutil.cpu_count.return_value = 4
        mock_psutil.cpu_freq.return_value = None

        result = get_cpu_info()

        assert "usage_percent" in result
        assert "physical_cores" in result
        assert "current_frequency_mhz" not in result


class TestGetMemoryInfo:
    """Test the get_memory_info function."""

    def test_psutil_not_available_error(self):
        """Test error when psutil is not available."""
        with patch("basic_open_agent_tools.system.info.HAS_PSUTIL", False):
            with pytest.raises(BasicAgentToolsError, match="psutil package required"):
                get_memory_info()

    @patch("basic_open_agent_tools.system.info.HAS_PSUTIL", True)
    @patch("basic_open_agent_tools.system.info.psutil")
    def test_successful_memory_info_retrieval(self, mock_psutil):
        """Test successful memory information retrieval."""
        # Mock virtual memory
        mock_vmem = Mock()
        mock_vmem.total = 8000000000
        mock_vmem.available = 4000000000
        mock_vmem.used = 3000000000
        mock_vmem.free = 1000000000
        mock_vmem.percent = 37.5
        mock_psutil.virtual_memory.return_value = mock_vmem

        # Mock swap memory
        mock_swap = Mock()
        mock_swap.total = 2000000000
        mock_swap.used = 500000000
        mock_swap.free = 1500000000
        mock_swap.percent = 25.0
        mock_psutil.swap_memory.return_value = mock_swap

        result = get_memory_info()

        expected_keys = [
            "total_bytes",
            "available_bytes",
            "used_bytes",
            "free_bytes",
            "usage_percent",
            "swap_total_bytes",
            "swap_used_bytes",
            "swap_free_bytes",
            "swap_usage_percent",
        ]

        for key in expected_keys:
            assert key in result

        assert result["total_bytes"] == 8000000000
        assert result["usage_percent"] == 37.5
        assert result["swap_total_bytes"] == 2000000000
        assert result["swap_usage_percent"] == 25.0


class TestGetDiskUsage:
    """Test the get_disk_usage function."""

    def test_invalid_path_type(self):
        """Test error handling for invalid path types."""
        with pytest.raises(
            BasicAgentToolsError, match="Path must be a non-empty string"
        ):
            get_disk_usage("")

        with pytest.raises(
            BasicAgentToolsError, match="Path must be a non-empty string"
        ):
            get_disk_usage(None)

    def test_psutil_not_available_error(self):
        """Test error when psutil is not available."""
        with patch("basic_open_agent_tools.system.info.HAS_PSUTIL", False):
            with pytest.raises(BasicAgentToolsError, match="psutil package required"):
                get_disk_usage("/")

    @patch("basic_open_agent_tools.system.info.HAS_PSUTIL", True)
    @patch("basic_open_agent_tools.system.info.psutil")
    def test_successful_disk_usage_retrieval(self, mock_psutil):
        """Test successful disk usage retrieval."""
        mock_usage = Mock()
        mock_usage.total = 1000000000
        mock_usage.used = 600000000
        mock_usage.free = 400000000
        mock_psutil.disk_usage.return_value = mock_usage

        result = get_disk_usage("/tmp")

        expected_keys = [
            "path",
            "total_bytes",
            "used_bytes",
            "free_bytes",
            "usage_percent",
        ]

        for key in expected_keys:
            assert key in result

        assert result["path"] == "/tmp"
        assert result["total_bytes"] == 1000000000
        assert result["used_bytes"] == 600000000
        assert result["free_bytes"] == 400000000
        assert result["usage_percent"] == 60.0

    @patch("basic_open_agent_tools.system.info.HAS_PSUTIL", True)
    @patch("basic_open_agent_tools.system.info.psutil")
    def test_windows_default_path_conversion(self, mock_psutil):
        """Test Windows default path conversion."""
        mock_usage = Mock()
        mock_usage.total = 1000000000
        mock_usage.used = 600000000
        mock_usage.free = 400000000
        mock_psutil.disk_usage.return_value = mock_usage

        with patch("platform.system", return_value="Windows"):
            get_disk_usage("/")  # Default path

            # Should be converted to C:\\ on Windows
            mock_psutil.disk_usage.assert_called_with("C:\\")

    @patch("basic_open_agent_tools.system.info.HAS_PSUTIL", True)
    @patch("basic_open_agent_tools.system.info.psutil")
    def test_file_not_found_error(self, mock_psutil):
        """Test handling of FileNotFoundError."""
        mock_psutil.disk_usage.side_effect = FileNotFoundError()

        with pytest.raises(BasicAgentToolsError, match="Path not found"):
            get_disk_usage("/nonexistent")


class TestGetUptime:
    """Test the get_uptime function."""

    def test_psutil_not_available_error(self):
        """Test error when psutil is not available."""
        with patch("basic_open_agent_tools.system.info.HAS_PSUTIL", False):
            with pytest.raises(BasicAgentToolsError, match="psutil package required"):
                get_uptime()

    @patch("basic_open_agent_tools.system.info.HAS_PSUTIL", True)
    @patch("basic_open_agent_tools.system.info.psutil")
    @patch("basic_open_agent_tools.system.info.time")
    def test_successful_uptime_retrieval(self, mock_time, mock_psutil):
        """Test successful uptime retrieval."""
        # Mock boot time (1 day, 2 hours, 30 minutes, 45 seconds ago)
        boot_timestamp = 1000000000
        current_timestamp = boot_timestamp + (24 * 3600) + (2 * 3600) + (30 * 60) + 45

        mock_psutil.boot_time.return_value = boot_timestamp
        mock_time.time.return_value = current_timestamp
        mock_time.strftime.return_value = "2023-01-01 00:00:00"
        mock_time.localtime.return_value = "mock_time_struct"

        result = get_uptime()

        expected_keys = [
            "uptime_seconds",
            "boot_time_timestamp",
            "boot_time_iso",
            "uptime_days",
            "uptime_hours",
            "uptime_minutes",
            "uptime_seconds_remainder",
            "uptime_human",
        ]

        for key in expected_keys:
            assert key in result

        assert result["uptime_seconds"] == (24 * 3600) + (2 * 3600) + (30 * 60) + 45
        assert result["boot_time_timestamp"] == boot_timestamp
        assert result["uptime_days"] == 1
        assert result["uptime_hours"] == 2
        assert result["uptime_minutes"] == 30
        assert result["uptime_seconds_remainder"] == 45
        assert "1d 2h 30m 45s" in result["uptime_human"]
