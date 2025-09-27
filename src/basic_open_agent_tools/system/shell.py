"""Cross-platform shell execution tools."""

import platform
import subprocess
import time
from typing import Any, Callable, Optional, Union

try:
    from strands import tool as strands_tool
except ImportError:

    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        """Fallback decorator when strands is not available."""
        return func


from ..exceptions import BasicAgentToolsError


@strands_tool
def execute_shell_command(
    command: str,
    timeout: int = 30,
    capture_output: bool = True,
    working_directory: Optional[str] = None,
) -> dict[str, Union[str, int, bool]]:
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

        # Print command info to stdout
        print(f"[SHELL] Executing: {command}")
        print(f"[SHELL] Platform: {system}")
        print(f"[SHELL] Working directory: {working_directory or 'current'}")
        print(f"[SHELL] Timeout: {timeout}s")
        print("-" * 50)

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

        # Print execution results to stdout
        print(f"[SHELL] Command completed in {execution_time:.3f}s")
        print(f"[SHELL] Return code: {result.returncode}")

        if capture_output and result.stdout:
            print(f"[SHELL] STDOUT:\n{result.stdout}")

        if capture_output and result.stderr:
            print(f"[SHELL] STDERR:\n{result.stderr}")

        print("-" * 50)

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
    timeout: int = 30,
    capture_output: bool = True,
    working_directory: Optional[str] = None,
) -> dict[str, Union[str, int, bool]]:
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
        # Use bash explicitly
        result = subprocess.run(
            ["/bin/bash", "-c", command],
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            cwd=working_directory,
        )

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
    timeout: int = 30,
    capture_output: bool = True,
    working_directory: Optional[str] = None,
) -> dict[str, Union[str, int, bool]]:
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
        # Use PowerShell with execution policy bypass for basic commands
        result = subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-Command", command],
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            cwd=working_directory,
        )

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
