"""Tests for runtime inspection tools."""

import os
import sys
from unittest.mock import patch

from basic_open_agent_tools.system.runtime import (
    get_current_directory,
    get_file_system_context,
    get_network_environment,
    get_python_module_info,
    inspect_runtime_environment,
)


class TestInspectRuntimeEnvironment:
    """Test the inspect_runtime_environment function."""

    def test_successful_runtime_inspection(self):
        """Test successful runtime environment inspection."""
        result = inspect_runtime_environment()

        # Check that all expected keys are present
        expected_keys = [
            "process_id",
            "username",
            "current_working_directory",
            "script_path",
            "python_executable",
            "python_version",
            "python_paths",
            "operating_system",
            "hostname",
            "important_environment_variables",
            "timestamp",
            "timestamp_iso",
        ]

        for key in expected_keys:
            assert key in result

        # Check data types and basic validation
        assert isinstance(result["process_id"], int)
        assert isinstance(result["python_version"], str)
        assert isinstance(result["python_paths"], list)
        assert isinstance(result["important_environment_variables"], dict)
        assert isinstance(result["timestamp"], float)
        assert result["timestamp"] > 0

    def test_environment_variables_extraction(self):
        """Test that important environment variables are extracted correctly."""
        # Set a test environment variable
        test_env_vars = {"TEST_VAR": "test_value", "PATH": "/usr/bin"}

        with patch.dict(os.environ, test_env_vars, clear=False):
            result = inspect_runtime_environment()

            # PATH should be included as it's in the important list
            if "PATH" in os.environ:
                assert "PATH" in result["important_environment_variables"]

    def test_command_line_arguments(self):
        """Test command line arguments extraction."""
        original_argv = sys.argv.copy()
        try:
            sys.argv = ["test_script.py", "--arg1", "value1"]

            result = inspect_runtime_environment()

            assert result["command_line_args"] == ["test_script.py", "--arg1", "value1"]
            assert result["script_path"] == "test_script.py"

        finally:
            sys.argv = original_argv

    @patch("os.getlogin")
    def test_username_fallback(self, mock_getlogin):
        """Test username extraction with fallback methods."""
        mock_getlogin.side_effect = OSError("No login")

        with patch.dict(os.environ, {"USER": "test_user"}, clear=False):
            result = inspect_runtime_environment()
            assert result["username"] == "test_user"


class TestGetPythonModuleInfo:
    """Test the get_python_module_info function."""

    def test_successful_module_info_retrieval(self):
        """Test successful Python module information retrieval."""
        result = get_python_module_info()

        # Check expected keys
        expected_keys = [
            "loaded_modules_count",
            "loaded_modules",
            "builtin_modules_count",
            "builtin_modules",
            "installed_packages_count",
            "installed_packages",
            "pkg_resources_available",
        ]

        for key in expected_keys:
            assert key in result

        # Check data types
        assert isinstance(result["loaded_modules"], list)
        assert isinstance(result["builtin_modules"], list)
        assert isinstance(result["installed_packages"], list)
        assert isinstance(result["pkg_resources_available"], bool)

        # Check counts match list lengths
        assert result["loaded_modules_count"] == len(result["loaded_modules"])
        assert result["builtin_modules_count"] == len(result["builtin_modules"])
        assert result["installed_packages_count"] == len(result["installed_packages"])

        # Should have some basic modules loaded
        assert len(result["loaded_modules"]) > 0
        assert len(result["builtin_modules"]) > 0

    def test_sorted_module_lists(self):
        """Test that module lists are sorted."""
        result = get_python_module_info()

        # Lists should be sorted
        assert result["loaded_modules"] == sorted(result["loaded_modules"])
        assert result["builtin_modules"] == sorted(result["builtin_modules"])
        assert result["installed_packages"] == sorted(result["installed_packages"])


class TestGetFileSystemContext:
    """Test the get_file_system_context function."""

    def test_successful_filesystem_context_retrieval(self):
        """Test successful file system context retrieval."""
        result = get_file_system_context()

        # Check expected keys
        expected_keys = [
            "current_directory",
            "current_directory_contents",
            "current_directory_item_count",
            "common_project_files_present",
            "common_directories_present",
            "parent_directories",
            "is_git_repository",
            "is_python_project",
            "has_virtual_environment",
        ]

        for key in expected_keys:
            assert key in result

        # Check data types
        assert isinstance(result["current_directory"], str)
        assert isinstance(result["current_directory_contents"], list)
        assert isinstance(result["current_directory_item_count"], int)
        assert isinstance(result["common_project_files_present"], list)
        assert isinstance(result["common_directories_present"], list)
        assert isinstance(result["parent_directories"], list)
        assert isinstance(result["is_git_repository"], bool)
        assert isinstance(result["is_python_project"], bool)
        assert isinstance(result["has_virtual_environment"], bool)

        # Item count should match list length
        assert result["current_directory_item_count"] == len(
            result["current_directory_contents"]
        )

    @patch("pathlib.Path.iterdir")
    def test_permission_denied_handling(self, mock_iterdir):
        """Test handling of permission denied errors."""
        mock_iterdir.side_effect = PermissionError("Access denied")

        result = get_file_system_context()

        assert result["current_directory_contents"] == ["<permission denied>"]
        assert result["current_directory_item_count"] == 1


class TestGetNetworkEnvironment:
    """Test the get_network_environment function."""

    def test_successful_network_environment_retrieval(self):
        """Test successful network environment retrieval."""
        result = get_network_environment()

        # Check expected keys
        expected_keys = [
            "hostname",
            "fqdn",
            "local_ip_address",
            "has_proxy_configuration",
            "proxy_environment_variables",
            "socket_family_support",
        ]

        for key in expected_keys:
            assert key in result

        # Check data types
        assert isinstance(result["hostname"], str)
        assert isinstance(result["fqdn"], str)
        assert isinstance(result["local_ip_address"], str)
        assert isinstance(result["has_proxy_configuration"], bool)
        assert isinstance(result["proxy_environment_variables"], dict)
        assert isinstance(result["socket_family_support"], dict)

        # Socket family support should have expected keys
        socket_support = result["socket_family_support"]
        assert "ipv4" in socket_support
        assert "ipv6" in socket_support
        assert "unix" in socket_support

    def test_proxy_environment_detection(self):
        """Test proxy environment variable detection."""
        proxy_vars = {
            "HTTP_PROXY": "http://proxy.example.com:8080",
            "HTTPS_PROXY": "https://proxy.example.com:8080",
        }

        with patch.dict(os.environ, proxy_vars, clear=False):
            result = get_network_environment()

            assert result["has_proxy_configuration"] is True
            assert "HTTP_PROXY" in result["proxy_environment_variables"]
            assert (
                result["proxy_environment_variables"]["HTTP_PROXY"]
                == "http://proxy.example.com:8080"
            )

    @patch("socket.socket")
    def test_local_ip_detection_failure(self, mock_socket):
        """Test handling when local IP detection fails."""
        mock_socket.side_effect = Exception("Network error")

        result = get_network_environment()

        assert result["local_ip_address"] == "unknown"

    @patch("socket.getfqdn")
    def test_fqdn_fallback(self, mock_getfqdn):
        """Test FQDN fallback to hostname."""
        mock_getfqdn.side_effect = Exception("DNS error")

        with patch("socket.gethostname", return_value="test-host"):
            result = get_network_environment()

            assert result["hostname"] == "test-host"
            assert result["fqdn"] == "test-host"  # Should fallback to hostname


class TestGetCurrentDirectory:
    """Test the get_current_directory function."""

    def test_successful_current_directory_retrieval(self):
        """Test successful retrieval of current working directory."""
        result = get_current_directory()

        # Check that result is a string and is an absolute path
        assert isinstance(result, str)
        assert len(result) > 0
        assert os.path.isabs(result)

        # Verify it matches os.getcwd()
        assert result == os.getcwd()

    @patch("os.getcwd")
    def test_error_handling(self, mock_getcwd):
        """Test error handling when getcwd fails."""
        from basic_open_agent_tools.exceptions import BasicAgentToolsError

        mock_getcwd.side_effect = Exception("Permission denied")

        try:
            get_current_directory()
            raise AssertionError("Expected BasicAgentToolsError")
        except BasicAgentToolsError as e:
            assert "Failed to get current directory" in str(e)
