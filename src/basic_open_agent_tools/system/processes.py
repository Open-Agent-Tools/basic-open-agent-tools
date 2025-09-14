"""Process management and information tools."""

from typing import Any, Callable, Union

try:
    import psutil  # type: ignore[import-untyped]

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    from strands import tool as strands_tool
except ImportError:

    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        """Fallback decorator when strands is not available."""
        return func


from ..exceptions import BasicAgentToolsError


@strands_tool
def get_current_process_info() -> dict[str, Union[str, int, float, Any]]:
    """
    Get information about the current process.

    Returns:
        Dictionary with current process details

    Raises:
        BasicAgentToolsError: If process information cannot be retrieved
    """
    if not HAS_PSUTIL:
        raise BasicAgentToolsError(
            "psutil package required for process information - install with: pip install psutil"
        )

    try:
        current_process = psutil.Process()

        return {
            "pid": current_process.pid,
            "name": current_process.name(),
            "status": current_process.status(),
            "cpu_percent": current_process.cpu_percent(),
            "memory_percent": current_process.memory_percent(),
            "memory_info_rss": current_process.memory_info().rss,
            "memory_info_vms": current_process.memory_info().vms,
            "create_time": current_process.create_time(),
            "num_threads": current_process.num_threads(),
            "username": current_process.username()
            if hasattr(current_process, "username")
            else "unknown",
            "cwd": current_process.cwd(),
        }
    except Exception as e:
        raise BasicAgentToolsError(
            f"Failed to get current process information: {str(e)}"
        )


@strands_tool
def list_running_processes(limit: int = 20) -> list[dict[str, Union[str, int, float]]]:
    """
    List basic information about running processes.

    Args:
        limit: Maximum number of processes to return (1-100)

    Returns:
        List of dictionaries with process information

    Raises:
        BasicAgentToolsError: If process list cannot be retrieved
    """
    if not HAS_PSUTIL:
        raise BasicAgentToolsError(
            "psutil package required for process information - install with: pip install psutil"
        )

    if not isinstance(limit, int) or limit < 1 or limit > 100:
        raise BasicAgentToolsError("Limit must be an integer between 1 and 100")

    try:
        processes = []

        for proc in psutil.process_iter(
            ["pid", "name", "status", "cpu_percent", "memory_percent"]
        ):
            try:
                process_info = proc.info
                processes.append(
                    {
                        "pid": process_info["pid"],
                        "name": process_info["name"],
                        "status": process_info["status"],
                        "cpu_percent": process_info["cpu_percent"] or 0.0,
                        "memory_percent": process_info["memory_percent"] or 0.0,
                    }
                )

                if len(processes) >= limit:
                    break

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Skip processes that disappeared or we can't access
                continue

        # Sort by CPU usage (highest first)
        processes.sort(key=lambda x: x["cpu_percent"], reverse=True)

        return processes[:limit]

    except Exception as e:
        raise BasicAgentToolsError(f"Failed to list running processes: {str(e)}")


@strands_tool
def get_process_info(process_id: int) -> dict[str, Union[str, int, float, None]]:
    """
    Get information about a specific process by PID.

    Args:
        process_id: Process ID to get information for

    Returns:
        Dictionary with process details

    Raises:
        BasicAgentToolsError: If process not found or information cannot be retrieved
    """
    if not HAS_PSUTIL:
        raise BasicAgentToolsError(
            "psutil package required for process information - install with: pip install psutil"
        )

    if not isinstance(process_id, int) or process_id <= 0:
        raise BasicAgentToolsError("Process ID must be a positive integer")

    try:
        process = psutil.Process(process_id)

        return {
            "pid": process.pid,
            "name": process.name(),
            "status": process.status(),
            "cpu_percent": process.cpu_percent(),
            "memory_percent": process.memory_percent(),
            "memory_info_rss": process.memory_info().rss,
            "memory_info_vms": process.memory_info().vms,
            "create_time": process.create_time(),
            "num_threads": process.num_threads(),
            "username": process.username()
            if hasattr(process, "username")
            else "unknown",
            "cwd": process.cwd() if process.cwd() else "unknown",
            "cmdline": " ".join(process.cmdline()) if process.cmdline() else "unknown",
            "parent_pid": process.ppid() if process.ppid() else None,
        }

    except psutil.NoSuchProcess:
        raise BasicAgentToolsError(f"Process with PID {process_id} not found")
    except psutil.AccessDenied:
        raise BasicAgentToolsError(f"Access denied to process with PID {process_id}")
    except Exception as e:
        raise BasicAgentToolsError(
            f"Failed to get information for process {process_id}: {str(e)}"
        )


@strands_tool
def is_process_running(
    process_name: str,
) -> dict[str, Union[bool, int, list[int], str]]:
    """
    Check if a process with the given name is running.

    Args:
        process_name: Name of the process to check

    Returns:
        Dictionary with process status information

    Raises:
        BasicAgentToolsError: If process name is invalid
    """
    if not HAS_PSUTIL:
        raise BasicAgentToolsError(
            "psutil package required for process information - install with: pip install psutil"
        )

    if not isinstance(process_name, str) or not process_name.strip():
        raise BasicAgentToolsError("Process name must be a non-empty string")

    process_name = process_name.strip().lower()

    try:
        matching_pids = []

        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if proc.info["name"] and proc.info["name"].lower() == process_name:
                    matching_pids.append(proc.info["pid"])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Skip processes that disappeared or we can't access
                continue

        return {
            "process_name": process_name,
            "is_running": len(matching_pids) > 0,
            "process_count": len(matching_pids),
            "pids": matching_pids,
        }

    except Exception as e:
        raise BasicAgentToolsError(
            f"Failed to check if process '{process_name}' is running: {str(e)}"
        )
