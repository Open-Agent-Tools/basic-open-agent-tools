"""Tests for process management tools."""

from unittest.mock import Mock, PropertyMock, patch

import pytest

from basic_open_agent_tools.exceptions import BasicAgentToolsError
from basic_open_agent_tools.system.processes import (
    get_current_process_info,
    get_process_info,
    is_process_running,
    list_running_processes,
)


class TestGetCurrentProcessInfo:
    """Test the get_current_process_info function."""

    def test_psutil_not_available_error(self):
        """Test error when psutil is not available."""
        with patch("basic_open_agent_tools.system.processes.HAS_PSUTIL", False):
            with pytest.raises(BasicAgentToolsError, match="psutil package required"):
                get_current_process_info()

    @patch("basic_open_agent_tools.system.processes.HAS_PSUTIL", True)
    @patch("basic_open_agent_tools.system.processes.psutil")
    def test_successful_current_process_info(self, mock_psutil):
        """Test successful current process information retrieval."""
        # Mock process object
        mock_process = Mock()
        mock_process.pid = 1234
        mock_process.name.return_value = "python"
        mock_process.status.return_value = "running"
        mock_process.cpu_percent.return_value = 15.5
        mock_process.memory_percent.return_value = 5.2

        # Mock memory info
        mock_memory = Mock()
        mock_memory.rss = 50000000
        mock_memory.vms = 100000000
        mock_process.memory_info.return_value = mock_memory

        mock_process.create_time.return_value = 1600000000
        mock_process.num_threads.return_value = 8
        mock_process.username.return_value = "testuser"
        mock_process.cwd.return_value = "/home/testuser"

        mock_psutil.Process.return_value = mock_process

        result = get_current_process_info()

        expected_keys = [
            "pid",
            "name",
            "status",
            "cpu_percent",
            "memory_percent",
            "memory_info_rss",
            "memory_info_vms",
            "create_time",
            "num_threads",
            "username",
            "cwd",
        ]

        for key in expected_keys:
            assert key in result

        assert result["pid"] == 1234
        assert result["name"] == "python"
        assert result["status"] == "running"
        assert result["cpu_percent"] == 15.5
        assert result["memory_info_rss"] == 50000000


class TestListRunningProcesses:
    """Test the list_running_processes function."""

    def test_invalid_limit(self):
        """Test error handling for invalid limit values."""
        with pytest.raises(
            BasicAgentToolsError, match="Limit must be an integer between 1 and 100"
        ):
            list_running_processes(limit=0)

        with pytest.raises(
            BasicAgentToolsError, match="Limit must be an integer between 1 and 100"
        ):
            list_running_processes(limit=101)

        with pytest.raises(
            BasicAgentToolsError, match="Limit must be an integer between 1 and 100"
        ):
            list_running_processes(limit="10")

    def test_psutil_not_available_error(self):
        """Test error when psutil is not available."""
        with patch("basic_open_agent_tools.system.processes.HAS_PSUTIL", False):
            with pytest.raises(BasicAgentToolsError, match="psutil package required"):
                list_running_processes(limit=10)

    @patch("basic_open_agent_tools.system.processes.HAS_PSUTIL", True)
    @patch("basic_open_agent_tools.system.processes.psutil")
    def test_successful_process_listing(self, mock_psutil):
        """Test successful process listing."""
        # Mock process iterator
        mock_processes = []
        for i in range(5):
            mock_proc = Mock()
            mock_proc.info = {
                "pid": 1000 + i,
                "name": f"process_{i}",
                "status": "running",
                "cpu_percent": 10.0 + i,
                "memory_percent": 5.0 + i,
            }
            mock_processes.append(mock_proc)

        mock_psutil.process_iter.return_value = mock_processes

        result = list_running_processes(limit=10)

        assert isinstance(result, list)
        assert len(result) == 5

        # Check first process
        first_process = result[0]
        expected_keys = ["pid", "name", "status", "cpu_percent", "memory_percent"]
        for key in expected_keys:
            assert key in first_process

        # Should be sorted by CPU usage (highest first)
        assert result[0]["cpu_percent"] >= result[-1]["cpu_percent"]

    @patch("basic_open_agent_tools.system.processes.HAS_PSUTIL", True)
    @patch("basic_open_agent_tools.system.processes.psutil")
    def test_process_access_denied_handling(self, mock_psutil):
        """Test handling of access denied errors."""
        # Create mock exceptions
        Exception("Access denied")
        Exception("No such process")

        mock_psutil.AccessDenied = type("AccessDenied", (Exception,), {})
        mock_psutil.NoSuchProcess = type("NoSuchProcess", (Exception,), {})

        mock_processes = []

        # First process - accessible
        mock_proc1 = Mock()
        mock_proc1.info = {
            "pid": 1000,
            "name": "accessible_process",
            "status": "running",
            "cpu_percent": 10.0,
            "memory_percent": 5.0,
        }
        mock_processes.append(mock_proc1)

        # Second process - access denied
        mock_proc2 = Mock()
        # Make accessing .info raise an exception immediately
        type(mock_proc2).info = PropertyMock(side_effect=mock_psutil.AccessDenied())
        mock_processes.append(mock_proc2)

        mock_psutil.process_iter.return_value = mock_processes

        result = list_running_processes(limit=10)

        # Should only return the accessible process
        assert len(result) == 1
        assert result[0]["name"] == "accessible_process"

    @patch("basic_open_agent_tools.system.processes.HAS_PSUTIL", True)
    @patch("basic_open_agent_tools.system.processes.psutil")
    def test_limit_enforcement(self, mock_psutil):
        """Test that the limit parameter is enforced."""
        # Create more processes than the limit
        mock_processes = []
        for i in range(10):
            mock_proc = Mock()
            mock_proc.info = {
                "pid": 1000 + i,
                "name": f"process_{i}",
                "status": "running",
                "cpu_percent": 10.0,
                "memory_percent": 5.0,
            }
            mock_processes.append(mock_proc)

        mock_psutil.process_iter.return_value = mock_processes

        result = list_running_processes(limit=3)

        assert len(result) <= 3


class TestGetProcessInfo:
    """Test the get_process_info function."""

    def test_invalid_process_id(self):
        """Test error handling for invalid process IDs."""
        with pytest.raises(
            BasicAgentToolsError, match="Process ID must be a positive integer"
        ):
            get_process_info(0)

        with pytest.raises(
            BasicAgentToolsError, match="Process ID must be a positive integer"
        ):
            get_process_info(-1)

        with pytest.raises(
            BasicAgentToolsError, match="Process ID must be a positive integer"
        ):
            get_process_info("1234")

    def test_psutil_not_available_error(self):
        """Test error when psutil is not available."""
        with patch("basic_open_agent_tools.system.processes.HAS_PSUTIL", False):
            with pytest.raises(BasicAgentToolsError, match="psutil package required"):
                get_process_info(1234)

    @patch("basic_open_agent_tools.system.processes.HAS_PSUTIL", True)
    @patch("basic_open_agent_tools.system.processes.psutil")
    def test_successful_process_info_retrieval(self, mock_psutil):
        """Test successful process information retrieval."""
        # Mock process object
        mock_process = Mock()
        mock_process.pid = 1234
        mock_process.name.return_value = "test_process"
        mock_process.status.return_value = "running"
        mock_process.cpu_percent.return_value = 25.0
        mock_process.memory_percent.return_value = 10.5

        # Mock memory info
        mock_memory = Mock()
        mock_memory.rss = 75000000
        mock_memory.vms = 150000000
        mock_process.memory_info.return_value = mock_memory

        mock_process.create_time.return_value = 1600000000
        mock_process.num_threads.return_value = 4
        mock_process.username.return_value = "testuser"
        mock_process.cwd.return_value = "/home/test"
        mock_process.cmdline.return_value = ["python", "script.py"]
        mock_process.ppid.return_value = 999

        mock_psutil.Process.return_value = mock_process

        result = get_process_info(1234)

        expected_keys = [
            "pid",
            "name",
            "status",
            "cpu_percent",
            "memory_percent",
            "memory_info_rss",
            "memory_info_vms",
            "create_time",
            "num_threads",
            "username",
            "cwd",
            "cmdline",
            "parent_pid",
        ]

        for key in expected_keys:
            assert key in result

        assert result["pid"] == 1234
        assert result["cmdline"] == "python script.py"
        assert result["parent_pid"] == 999

    @patch("basic_open_agent_tools.system.processes.HAS_PSUTIL", True)
    @patch("basic_open_agent_tools.system.processes.psutil")
    def test_process_not_found_error(self, mock_psutil):
        """Test handling of process not found error."""
        import psutil

        mock_psutil.Process.side_effect = psutil.NoSuchProcess(1234)
        mock_psutil.NoSuchProcess = psutil.NoSuchProcess

        with pytest.raises(
            BasicAgentToolsError, match="Process with PID 1234 not found"
        ):
            get_process_info(1234)


class TestIsProcessRunning:
    """Test the is_process_running function."""

    def test_invalid_process_name(self):
        """Test error handling for invalid process names."""
        with pytest.raises(
            BasicAgentToolsError, match="Process name must be a non-empty string"
        ):
            is_process_running("")

        with pytest.raises(
            BasicAgentToolsError, match="Process name must be a non-empty string"
        ):
            is_process_running(None)

        with pytest.raises(
            BasicAgentToolsError, match="Process name must be a non-empty string"
        ):
            is_process_running("   ")

    def test_psutil_not_available_error(self):
        """Test error when psutil is not available."""
        with patch("basic_open_agent_tools.system.processes.HAS_PSUTIL", False):
            with pytest.raises(BasicAgentToolsError, match="psutil package required"):
                is_process_running("python")

    @patch("basic_open_agent_tools.system.processes.HAS_PSUTIL", True)
    @patch("basic_open_agent_tools.system.processes.psutil")
    def test_process_running_found(self, mock_psutil):
        """Test finding a running process."""
        # Mock process iterator
        mock_processes = []

        # Create matching processes
        for i in range(2):
            mock_proc = Mock()
            mock_proc.info = {"pid": 1000 + i, "name": "python"}
            mock_processes.append(mock_proc)

        # Create non-matching process
        mock_proc_other = Mock()
        mock_proc_other.info = {"pid": 2000, "name": "chrome"}
        mock_processes.append(mock_proc_other)

        mock_psutil.process_iter.return_value = mock_processes

        result = is_process_running("python")

        assert result["process_name"] == "python"
        assert result["is_running"] is True
        assert result["process_count"] == 2
        assert result["pids"] == [1000, 1001]

    @patch("basic_open_agent_tools.system.processes.HAS_PSUTIL", True)
    @patch("basic_open_agent_tools.system.processes.psutil")
    def test_process_not_running(self, mock_psutil):
        """Test when process is not running."""
        # Mock process iterator with no matching processes
        mock_processes = []
        mock_proc = Mock()
        mock_proc.info = {"pid": 1000, "name": "chrome"}
        mock_processes.append(mock_proc)

        mock_psutil.process_iter.return_value = mock_processes

        result = is_process_running("python")

        assert result["process_name"] == "python"
        assert result["is_running"] is False
        assert result["process_count"] == 0
        assert result["pids"] == []

    @patch("basic_open_agent_tools.system.processes.HAS_PSUTIL", True)
    @patch("basic_open_agent_tools.system.processes.psutil")
    def test_case_insensitive_matching(self, mock_psutil):
        """Test case-insensitive process name matching."""
        mock_processes = []
        mock_proc = Mock()
        mock_proc.info = {"pid": 1000, "name": "Python.exe"}
        mock_processes.append(mock_proc)

        mock_psutil.process_iter.return_value = mock_processes

        result = is_process_running("python.exe")

        assert result["is_running"] is True
        assert result["process_count"] == 1
