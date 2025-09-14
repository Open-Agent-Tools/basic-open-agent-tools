"""Tests for performance monitoring functions."""

import os
import tempfile
from unittest.mock import patch, MagicMock
import pytest
from basic_open_agent_tools.monitoring.performance import (
    monitor_function_performance,
    get_system_load_average,
    profile_code_execution,
    benchmark_disk_io
)
from basic_open_agent_tools.exceptions import BasicAgentToolsError


class TestMonitorFunctionPerformance:
    """Test cases for monitor_function_performance function."""

    def test_missing_psutil_dependency(self):
        """Test error when psutil is not available."""
        with patch('basic_open_agent_tools.monitoring.performance.HAS_PSUTIL', False):
            with pytest.raises(BasicAgentToolsError) as exc_info:
                monitor_function_performance(5)
            assert "psutil package required" in str(exc_info.value)

    def test_invalid_duration_type(self):
        """Test with invalid duration type."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            monitor_function_performance("invalid")
        assert "Duration must be an integer" in str(exc_info.value)

    def test_invalid_duration_range(self):
        """Test with duration out of valid range."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            monitor_function_performance(0)
        assert "Duration must be an integer between 1 and 3600 seconds" in str(exc_info.value)

        with pytest.raises(BasicAgentToolsError) as exc_info:
            monitor_function_performance(3601)
        assert "Duration must be an integer between 1 and 3600 seconds" in str(exc_info.value)

    @patch('basic_open_agent_tools.monitoring.performance.HAS_PSUTIL', True)
    @patch('basic_open_agent_tools.monitoring.performance.psutil')
    @patch('time.sleep')
    @patch('time.time')
    def test_successful_monitoring(self, mock_time, mock_sleep, mock_psutil):
        """Test successful performance monitoring."""
        # Mock time progression
        mock_time.side_effect = [0, 2, 4, 6]  # Start, then 3 samples at 2-second intervals

        # Mock psutil functions
        mock_psutil.cpu_percent.side_effect = [25.0, 30.0, 35.0]

        mock_memory = MagicMock()
        mock_memory.percent = [50.0, 55.0, 60.0][0]  # Will be called 3 times
        mock_psutil.virtual_memory.side_effect = [
            MagicMock(percent=50.0),
            MagicMock(percent=55.0),
            MagicMock(percent=60.0)
        ]

        mock_disk = MagicMock()
        mock_disk.percent = [70.0, 72.0, 75.0][0]  # Will be called 3 times
        mock_psutil.disk_usage.side_effect = [
            MagicMock(percent=70.0),
            MagicMock(percent=72.0),
            MagicMock(percent=75.0)
        ]

        result = monitor_function_performance(5)

        assert result["monitoring_duration_seconds"] == 5
        assert result["sample_count"] == 3
        assert result["sampling_interval_seconds"] == 2
        assert result["monitoring_status"] == "completed"

        # Check CPU metrics
        assert result["cpu_usage_average"] == 30.0  # (25+30+35)/3
        assert result["cpu_usage_min"] == 25.0
        assert result["cpu_usage_max"] == 35.0
        assert result["cpu_samples"] == [25.0, 30.0, 35.0]

        # Check memory metrics
        assert result["memory_usage_average"] == 55.0  # (50+55+60)/3
        assert result["memory_usage_min"] == 50.0
        assert result["memory_usage_max"] == 60.0

        # Check disk metrics
        assert result["disk_usage_average"] == 72.33  # (70+72+75)/3 rounded
        assert result["disk_usage_min"] == 70.0
        assert result["disk_usage_max"] == 75.0

    @patch('basic_open_agent_tools.monitoring.performance.HAS_PSUTIL', True)
    @patch('basic_open_agent_tools.monitoring.performance.psutil')
    @patch('time.sleep')
    @patch('time.time')
    def test_monitoring_with_exception(self, mock_time, mock_sleep, mock_psutil):
        """Test monitoring when psutil raises an exception."""
        mock_time.side_effect = [0, 2]
        mock_psutil.cpu_percent.side_effect = Exception("CPU monitoring failed")

        with pytest.raises(BasicAgentToolsError) as exc_info:
            monitor_function_performance(5)
        assert "Failed to monitor performance" in str(exc_info.value)


class TestGetSystemLoadAverage:
    """Test cases for get_system_load_average function."""

    def test_missing_psutil_dependency(self):
        """Test error when psutil is not available."""
        with patch('basic_open_agent_tools.monitoring.performance.HAS_PSUTIL', False):
            with pytest.raises(BasicAgentToolsError) as exc_info:
                get_system_load_average()
            assert "psutil package required" in str(exc_info.value)

    @patch('basic_open_agent_tools.monitoring.performance.HAS_PSUTIL', True)
    @patch('basic_open_agent_tools.monitoring.performance.psutil')
    def test_successful_load_average_unix(self, mock_psutil):
        """Test successful load average retrieval on Unix systems."""
        # Mock Unix system with load average support
        mock_psutil.getloadavg.return_value = (1.5, 2.0, 2.5)

        result = get_system_load_average()

        assert result["load_1_minute"] == 1.5
        assert result["load_5_minute"] == 2.0
        assert result["load_15_minute"] == 2.5
        assert result["system_type"] == "unix_like"
        assert result["load_average_available"] is True
        assert result["retrieval_status"] == "success"

    @patch('basic_open_agent_tools.monitoring.performance.HAS_PSUTIL', True)
    @patch('basic_open_agent_tools.monitoring.performance.psutil')
    def test_load_average_not_available(self, mock_psutil):
        """Test when load average is not available (e.g., Windows)."""
        # Mock Windows system where getloadavg raises AttributeError
        mock_psutil.getloadavg.side_effect = AttributeError("Load average not available")

        result = get_system_load_average()

        assert result["load_1_minute"] is None
        assert result["load_5_minute"] is None
        assert result["load_15_minute"] is None
        assert result["system_type"] == "windows_or_unsupported"
        assert result["load_average_available"] is False
        assert result["retrieval_status"] == "not_available"

    @patch('basic_open_agent_tools.monitoring.performance.HAS_PSUTIL', True)
    @patch('basic_open_agent_tools.monitoring.performance.psutil')
    def test_load_average_with_exception(self, mock_psutil):
        """Test when psutil raises an unexpected exception."""
        mock_psutil.getloadavg.side_effect = OSError("Permission denied")

        with pytest.raises(BasicAgentToolsError) as exc_info:
            get_system_load_average()
        assert "Failed to retrieve system load average" in str(exc_info.value)


class TestProfileCodeExecution:
    """Test cases for profile_code_execution function."""

    def test_invalid_code_type(self):
        """Test with invalid code snippet type."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            profile_code_execution(123)
        assert "Code snippet must be a non-empty string" in str(exc_info.value)

    def test_empty_code_string(self):
        """Test with empty code string."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            profile_code_execution("")
        assert "Code snippet must be a non-empty string" in str(exc_info.value)

    def test_invalid_iterations_type(self):
        """Test with invalid iterations type."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            profile_code_execution("x = 1", "invalid")
        assert "Iterations must be an integer between 1 and 10000" in str(exc_info.value)

    def test_invalid_iterations_value(self):
        """Test with invalid iterations value."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            profile_code_execution("x = 1", 0)
        assert "Iterations must be an integer between 1 and 10000" in str(exc_info.value)

        with pytest.raises(BasicAgentToolsError) as exc_info:
            profile_code_execution("x = 1", 10001)
        assert "Iterations must be an integer between 1 and 10000" in str(exc_info.value)

    def test_successful_code_profiling(self):
        """Test successful code profiling."""
        result = profile_code_execution("x = 1 + 2", 2)

        assert result["code_snippet"] == "x = 1 + 2"
        assert result["iterations"] == 2
        assert "total_execution_time_seconds" in result
        assert "avg_execution_time_seconds" in result
        assert "min_execution_time_seconds" in result
        assert "max_execution_time_seconds" in result
        assert "executions_per_second" in result
        assert result["profiling_successful"] is True
        assert result["profiling_status"] == "completed"

        # Check that all timing values are reasonable
        assert result["total_execution_time_seconds"] > 0
        assert result["avg_execution_time_seconds"] > 0
        assert result["min_execution_time_seconds"] >= 0
        assert result["max_execution_time_seconds"] >= result["min_execution_time_seconds"]

    def test_code_with_syntax_error(self):
        """Test profiling code with syntax error."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            profile_code_execution("x = 1 +", 1)
        assert "Syntax error in code snippet" in str(exc_info.value)

    def test_code_with_runtime_error(self):
        """Test profiling code with runtime error."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            profile_code_execution("x = 1 / 0", 1)
        assert "Failed to profile code execution" in str(exc_info.value)

    def test_dangerous_code_prevention(self):
        """Test that dangerous code is prevented."""
        dangerous_codes = [
            "import os",
            "exec('print(1)')",
            "eval('1+1')",
            "__import__('os')",
            "open('/etc/passwd')"
        ]

        for dangerous_code in dangerous_codes:
            with pytest.raises(BasicAgentToolsError) as exc_info:
                profile_code_execution(dangerous_code, 1)
            assert "potentially dangerous keyword" in str(exc_info.value)


class TestBenchmarkDiskIo:
    """Test cases for benchmark_disk_io function."""

    def test_invalid_file_path_type(self):
        """Test with invalid file path type."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            benchmark_disk_io(123)
        assert "File path must be a non-empty string" in str(exc_info.value)

    def test_empty_file_path(self):
        """Test with empty file path."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            benchmark_disk_io("")
        assert "File path must be a non-empty string" in str(exc_info.value)

    def test_invalid_data_size_type(self):
        """Test with invalid data size type."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            benchmark_disk_io("test.dat", "invalid")
        assert "Data size must be an integer between 1 and 10240 KB" in str(exc_info.value)

    def test_invalid_data_size_value(self):
        """Test with invalid data size value."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            benchmark_disk_io("test.dat", 0)
        assert "Data size must be an integer between 1 and 10240 KB" in str(exc_info.value)

        with pytest.raises(BasicAgentToolsError) as exc_info:
            benchmark_disk_io("test.dat", 10241)  # > 10240 KB
        assert "Data size must be an integer between 1 and 10240 KB" in str(exc_info.value)

    @patch('os.path.dirname')
    @patch('os.access')
    def test_directory_not_writable(self, mock_access, mock_dirname):
        """Test when directory is not writable."""
        mock_dirname.return_value = "/readonly"
        mock_access.return_value = False

        with pytest.raises(BasicAgentToolsError) as exc_info:
            benchmark_disk_io("/readonly/test.dat")
        assert "Directory is not writable" in str(exc_info.value)

    def test_successful_disk_benchmark(self):
        """Test successful disk I/O benchmarking."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "benchmark_test.dat")

            # Use a small data size for faster testing
            result = benchmark_disk_io(test_file, 1)  # 1KB

            assert result["file_path"] == test_file
            assert result["data_size_kb"] == 1
            assert result["data_size_bytes"] == 1024
            assert result["benchmark_status"] == "completed"

            # Check that timing metrics exist and are reasonable
            assert "write_time_seconds" in result
            assert "read_time_seconds" in result
            assert "total_time_seconds" in result
            assert "write_speed_mbps" in result
            assert "read_speed_mbps" in result

            # Timing should be positive
            assert result["write_time_seconds"] > 0
            assert result["read_time_seconds"] > 0
            assert result["total_time_seconds"] > 0

            # Speed should be positive
            assert result["write_speed_mbps"] > 0
            assert result["read_speed_mbps"] > 0

            # Cleanup should have occurred
            assert not os.path.exists(test_file)

    @patch('builtins.open')
    def test_write_permission_error(self, mock_open):
        """Test when write operation fails due to permissions."""
        mock_open.side_effect = PermissionError("Permission denied")

        with pytest.raises(BasicAgentToolsError) as exc_info:
            benchmark_disk_io("/test/path/benchmark.dat", 1)
        assert "Failed to benchmark disk I/O" in str(exc_info.value)

    def test_insufficient_disk_space(self):
        """Test behavior with very large file size that might cause space issues."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "large_benchmark.dat")

            # This should still work but test the large file handling
            try:
                result = benchmark_disk_io(test_file, 1024)  # 1MB

                # If successful, verify the results
                assert result["data_size_kb"] == 1024
                assert result["data_size_bytes"] == 1024 * 1024
                assert result["benchmark_status"] == "completed"

            except BasicAgentToolsError as e:
                # If it fails due to space or other issues, that's also acceptable
                assert "Failed to benchmark disk I/O" in str(e)