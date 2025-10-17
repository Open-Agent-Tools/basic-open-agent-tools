"""Tests for shell execution tools."""

from unittest.mock import Mock, patch

import pytest

from basic_open_agent_tools.exceptions import BasicAgentToolsError
from basic_open_agent_tools.system.shell import (
    execute_shell_command,
    run_bash,
    run_powershell,
)


class TestExecuteShellCommand:
    """Test the execute_shell_command function."""

    def test_invalid_command_type(self):
        """Test error handling for invalid command types."""
        with pytest.raises(
            BasicAgentToolsError, match="Command must be a non-empty string"
        ):
            execute_shell_command(
                "", timeout=30, capture_output=True, working_directory=""
            )

        with pytest.raises(
            BasicAgentToolsError, match="Command must be a non-empty string"
        ):
            execute_shell_command(
                None, timeout=30, capture_output=True, working_directory=""
            )

        with pytest.raises(
            BasicAgentToolsError, match="Command must be a non-empty string"
        ):
            execute_shell_command(
                123, timeout=30, capture_output=True, working_directory=""
            )

    def test_invalid_timeout(self):
        """Test error handling for invalid timeout values."""
        with pytest.raises(
            BasicAgentToolsError, match="Timeout must be a positive integer"
        ):
            execute_shell_command(
                "echo test", timeout=0, capture_output=True, working_directory=""
            )

        with pytest.raises(
            BasicAgentToolsError, match="Timeout must be a positive integer"
        ):
            execute_shell_command(
                "echo test", timeout=-1, capture_output=True, working_directory=""
            )

        with pytest.raises(
            BasicAgentToolsError, match="Timeout must be a positive integer"
        ):
            execute_shell_command(
                "echo test", timeout=301, capture_output=True, working_directory=""
            )

        with pytest.raises(
            BasicAgentToolsError, match="Timeout must be a positive integer"
        ):
            execute_shell_command(
                "echo test", timeout="30", capture_output=True, working_directory=""
            )

    def test_invalid_working_directory(self):
        """Test error handling for invalid working directory."""
        with pytest.raises(
            BasicAgentToolsError, match="Working directory must be a string"
        ):
            execute_shell_command(
                "echo test", timeout=30, capture_output=True, working_directory=123
            )

    @patch("subprocess.run")
    def test_successful_command_execution(self, mock_run):
        """Test successful command execution."""
        # Mock successful command result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Hello World"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = execute_shell_command(
            "echo Hello World", timeout=30, capture_output=True, working_directory=""
        )

        assert result["status"] == "success"
        assert result["return_code"] == 0
        assert result["stdout"] == "Hello World"
        assert result["stderr"] == ""
        assert result["command"] == "echo Hello World"
        assert "platform" in result
        assert result["timeout_seconds"] == 30

    @patch("subprocess.run")
    def test_command_with_error_return_code(self, mock_run):
        """Test command that returns non-zero exit code."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Command failed"
        mock_run.return_value = mock_result

        result = execute_shell_command(
            "false", timeout=30, capture_output=True, working_directory=""
        )

        assert result["status"] == "error"
        assert result["return_code"] == 1
        assert result["stderr"] == "Command failed"

    @patch("subprocess.run")
    def test_command_timeout(self, mock_run):
        """Test command timeout handling."""
        from subprocess import TimeoutExpired

        mock_run.side_effect = TimeoutExpired("test", 5)

        with pytest.raises(
            BasicAgentToolsError, match="Command timed out after 5 seconds"
        ):
            execute_shell_command(
                "sleep 10", timeout=5, capture_output=True, working_directory=""
            )

    @patch("subprocess.run")
    def test_platform_specific_shell_windows(self, mock_run):
        """Test Windows-specific shell command construction."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "test"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        with patch("platform.system", return_value="Windows"):
            execute_shell_command(
                "dir", timeout=30, capture_output=True, working_directory=""
            )

            # Check that cmd.exe was used
            call_args = mock_run.call_args[0][0]
            assert call_args == ["cmd.exe", "/c", "dir"]

    @patch("subprocess.run")
    def test_platform_specific_shell_unix(self, mock_run):
        """Test Unix-specific shell command construction."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "test"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        with patch("platform.system", return_value="Linux"):
            execute_shell_command(
                "ls", timeout=30, capture_output=True, working_directory=""
            )

            # Check that sh was used
            call_args = mock_run.call_args[0][0]
            assert call_args == ["/bin/sh", "-c", "ls"]

    @patch("subprocess.run")
    def test_working_directory_parameter(self, mock_run):
        """Test working directory parameter."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        execute_shell_command(
            "pwd", timeout=30, capture_output=True, working_directory="/tmp"
        )

        # Check that cwd parameter was passed
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["cwd"] == "/tmp"


class TestRunBash:
    """Test the run_bash function."""

    def test_invalid_command_type(self):
        """Test error handling for invalid command types."""
        with pytest.raises(
            BasicAgentToolsError, match="Command must be a non-empty string"
        ):
            run_bash("", timeout=30, capture_output=True, working_directory="")

    def test_windows_platform_error(self):
        """Test error when trying to use bash on Windows."""
        with patch("platform.system", return_value="Windows"):
            with pytest.raises(
                BasicAgentToolsError, match="Bash execution not available on Windows"
            ):
                run_bash("ls", timeout=30, capture_output=True, working_directory="")

    @patch("subprocess.run")
    def test_successful_bash_execution(self, mock_run):
        """Test successful bash command execution."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "bash output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        with patch("platform.system", return_value="Linux"):
            result = run_bash(
                "echo bash output",
                timeout=30,
                capture_output=True,
                working_directory="",
            )

            assert result["status"] == "success"
            assert result["return_code"] == 0
            assert result["stdout"] == "bash output"
            assert result["shell"] == "bash"

            # Check that bash was used
            call_args = mock_run.call_args[0][0]
            assert call_args == ["/bin/bash", "-c", "echo bash output"]

    @patch("subprocess.run")
    def test_bash_not_found(self, mock_run):
        """Test handling when bash is not found."""
        mock_run.side_effect = FileNotFoundError()

        with patch("platform.system", return_value="Linux"):
            with pytest.raises(BasicAgentToolsError, match="Bash not found"):
                run_bash(
                    "echo test", timeout=30, capture_output=True, working_directory=""
                )


class TestRunPowershell:
    """Test the run_powershell function."""

    def test_invalid_command_type(self):
        """Test error handling for invalid command types."""
        with pytest.raises(
            BasicAgentToolsError, match="Command must be a non-empty string"
        ):
            run_powershell("", timeout=30, capture_output=True, working_directory="")

    def test_non_windows_platform_error(self):
        """Test error when trying to use PowerShell on non-Windows."""
        with patch("platform.system", return_value="Linux"):
            with pytest.raises(
                BasicAgentToolsError,
                match="PowerShell execution only available on Windows",
            ):
                run_powershell(
                    "Get-Process", timeout=30, capture_output=True, working_directory=""
                )

    @patch("subprocess.run")
    def test_successful_powershell_execution(self, mock_run):
        """Test successful PowerShell command execution."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "powershell output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        with patch("platform.system", return_value="Windows"):
            result = run_powershell(
                "Get-Date", timeout=30, capture_output=True, working_directory=""
            )

            assert result["status"] == "success"
            assert result["return_code"] == 0
            assert result["stdout"] == "powershell output"
            assert result["shell"] == "powershell"

            # Check that PowerShell was used with correct parameters
            call_args = mock_run.call_args[0][0]
            assert call_args == [
                "powershell.exe",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                "Get-Date",
            ]

    @patch("subprocess.run")
    def test_powershell_not_found(self, mock_run):
        """Test handling when PowerShell is not found."""
        mock_run.side_effect = FileNotFoundError()

        with patch("platform.system", return_value="Windows"):
            with pytest.raises(BasicAgentToolsError, match="PowerShell not found"):
                run_powershell(
                    "Get-Process", timeout=30, capture_output=True, working_directory=""
                )
