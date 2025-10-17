"""Cross-platform shell execution tools."""

import platform
import subprocess
import time
from typing import Union

from .._logging import get_logger
from ..decorators import strands_tool
from ..exceptions import BasicAgentToolsError

logger = get_logger("system.shell")


@strands_tool
def execute_shell_command(
    command: str,
    timeout: int,
    capture_output: bool,
    working_directory: str,
) -> dict[str, Union[str, int, float, bool]]:
    """
    Execute a shell command cross-platform (Windows cmd, Unix bash/sh).

    Args:
        command: Command to execute
        timeout: Maximum execution time in seconds
        capture_output: Whether to capture stdout/stderr
        working_directory: Directory to execute command in

    Returns:
        Dictionary with execution results

    Raises:
        BasicAgentToolsError: If command execution fails
    """
    if not isinstance(command, str) or not command.strip():
        raise BasicAgentToolsError("Command must be a non-empty string")

    if not isinstance(timeout, int) or timeout <= 0 or timeout > 300:
        raise BasicAgentToolsError(
            "Timeout must be a positive integer up to 300 seconds"
        )

    if working_directory and not isinstance(working_directory, str):
        raise BasicAgentToolsError("Working directory must be a string")

    try:
        # Determine the appropriate shell based on platform
        system = platform.system().lower()

        if system == "windows":
            # Use cmd.exe on Windows
            shell_command = ["cmd.exe", "/c", command]
            shell = False  # Don't use shell=True on Windows for security
        else:
            # Use sh on Unix-like systems (more portable than bash)
            shell_command = ["/bin/sh", "-c", command]
            shell = False

        # Log command info
        logger.info(f"Executing: {command}")
        logger.debug(f"Platform: {system}")
        logger.debug(f"Working directory: {working_directory or 'current'}")
        logger.debug(f"Timeout: {timeout}s")

        # Execute the command
        start_time = time.time()

        result = subprocess.run(
            shell_command,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            cwd=working_directory,
            shell=shell,
        )

        end_time = time.time()
        execution_time = end_time - start_time

        # Log execution results
        logger.info(
            f"Command completed in {execution_time:.3f}s (return code: {result.returncode})"
        )

        if capture_output and result.stdout:
            logger.debug(f"STDOUT:\n{result.stdout}")

        if capture_output and result.stderr:
            logger.debug(f"STDERR:\n{result.stderr}")

        return {
            "status": "success" if result.returncode == 0 else "error",
            "return_code": result.returncode,
            "stdout": result.stdout if capture_output else "",
            "stderr": result.stderr if capture_output else "",
            "command": command,
            "platform": system,
            "execution_time_seconds": round(execution_time, 3),
            "working_directory": working_directory or "current",
            "timeout_seconds": timeout,
        }

    except subprocess.TimeoutExpired:
        raise BasicAgentToolsError(f"Command timed out after {timeout} seconds")
    except subprocess.CalledProcessError as e:
        raise BasicAgentToolsError(
            f"Command failed with return code {e.returncode}: {e.stderr}"
        )
    except FileNotFoundError:
        raise BasicAgentToolsError("Shell not found - unsupported platform")
    except Exception as e:
        raise BasicAgentToolsError(f"Command execution failed: {str(e)}")


@strands_tool
def run_bash(
    command: str,
    timeout: int,
    capture_output: bool,
    working_directory: str,
) -> dict[str, Union[str, int, float, bool]]:
    """
    Execute a bash command (Unix/Linux/macOS only).

    Args:
        command: Bash command to execute
        timeout: Maximum execution time in seconds
        capture_output: Whether to capture stdout/stderr
        working_directory: Directory to execute command in

    Returns:
        Dictionary with execution results

    Raises:
        BasicAgentToolsError: If not on Unix-like system or command fails
    """
    if not isinstance(command, str) or not command.strip():
        raise BasicAgentToolsError("Command must be a non-empty string")

    system = platform.system().lower()
    if system == "windows":
        raise BasicAgentToolsError("Bash execution not available on Windows")

    if not isinstance(timeout, int) or timeout <= 0 or timeout > 300:
        raise BasicAgentToolsError(
            "Timeout must be a positive integer up to 300 seconds"
        )

    try:
        # Log command info
        logger.info(f"Executing (bash): {command}")
        logger.debug(f"Platform: {system}")
        logger.debug(f"Working directory: {working_directory or 'current'}")
        logger.debug(f"Timeout: {timeout}s")

        # Execute the command
        start_time = time.time()

        # Use bash explicitly
        result = subprocess.run(
            ["/bin/bash", "-c", command],
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            cwd=working_directory,
        )

        end_time = time.time()
        execution_time = end_time - start_time

        # Log execution results
        logger.info(
            f"Command completed in {execution_time:.3f}s (return code: {result.returncode})"
        )

        if capture_output and result.stdout:
            logger.debug(f"STDOUT:\n{result.stdout}")

        if capture_output and result.stderr:
            logger.debug(f"STDERR:\n{result.stderr}")

        return {
            "status": "success" if result.returncode == 0 else "error",
            "return_code": result.returncode,
            "stdout": result.stdout if capture_output else "",
            "stderr": result.stderr if capture_output else "",
            "command": command,
            "shell": "bash",
            "platform": system,
            "working_directory": working_directory or "current",
            "timeout_seconds": timeout,
            "execution_time_seconds": round(execution_time, 3),
        }

    except subprocess.TimeoutExpired:
        raise BasicAgentToolsError(f"Bash command timed out after {timeout} seconds")
    except FileNotFoundError:
        raise BasicAgentToolsError("Bash not found - not available on this system")
    except Exception as e:
        raise BasicAgentToolsError(f"Bash command execution failed: {str(e)}")


@strands_tool
def run_powershell(
    command: str,
    timeout: int,
    capture_output: bool,
    working_directory: str,
) -> dict[str, Union[str, int, float, bool]]:
    """
    Execute a PowerShell command (Windows only).

    Args:
        command: PowerShell command to execute
        timeout: Maximum execution time in seconds
        capture_output: Whether to capture stdout/stderr
        working_directory: Directory to execute command in

    Returns:
        Dictionary with execution results

    Raises:
        BasicAgentToolsError: If not on Windows or command fails
    """
    if not isinstance(command, str) or not command.strip():
        raise BasicAgentToolsError("Command must be a non-empty string")

    system = platform.system().lower()
    if system != "windows":
        raise BasicAgentToolsError("PowerShell execution only available on Windows")

    if not isinstance(timeout, int) or timeout <= 0 or timeout > 300:
        raise BasicAgentToolsError(
            "Timeout must be a positive integer up to 300 seconds"
        )

    try:
        # Log command info
        logger.info(f"Executing (powershell): {command}")
        logger.debug(f"Platform: {system}")
        logger.debug(f"Working directory: {working_directory or 'current'}")
        logger.debug(f"Timeout: {timeout}s")

        # Execute the command
        start_time = time.time()

        # Use PowerShell with execution policy bypass for basic commands
        result = subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-Command", command],
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            cwd=working_directory,
        )

        end_time = time.time()
        execution_time = end_time - start_time

        # Log execution results
        logger.info(
            f"Command completed in {execution_time:.3f}s (return code: {result.returncode})"
        )

        if capture_output and result.stdout:
            logger.debug(f"STDOUT:\n{result.stdout}")

        if capture_output and result.stderr:
            logger.debug(f"STDERR:\n{result.stderr}")

        return {
            "status": "success" if result.returncode == 0 else "error",
            "return_code": result.returncode,
            "stdout": result.stdout if capture_output else "",
            "stderr": result.stderr if capture_output else "",
            "command": command,
            "shell": "powershell",
            "platform": system,
            "working_directory": working_directory or "current",
            "timeout_seconds": timeout,
            "execution_time_seconds": round(execution_time, 3),
        }

    except subprocess.TimeoutExpired:
        raise BasicAgentToolsError(
            f"PowerShell command timed out after {timeout} seconds"
        )
    except FileNotFoundError:
        raise BasicAgentToolsError(
            "PowerShell not found - not available on this system"
        )
    except Exception as e:
        raise BasicAgentToolsError(f"PowerShell command execution failed: {str(e)}")
