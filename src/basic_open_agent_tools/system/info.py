"""System information gathering tools."""

import platform
import time
from typing import Union

from ..decorators import strands_tool

try:
    import psutil  # type: ignore[import-untyped]

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


from ..exceptions import BasicAgentToolsError


@strands_tool
def get_system_info() -> dict[str, str]:
    """
    Get basic system information.

    Returns:
        Dictionary with system details

    Raises:
        BasicAgentToolsError: If system information cannot be retrieved
    """
    try:
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0],
            "platform": platform.platform(),
            "node": platform.node(),
            "python_version": platform.python_version(),
        }
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to get system information: {str(e)}")


@strands_tool
def get_cpu_info() -> dict[str, Union[str, int, float]]:
    """
    Get CPU information and usage statistics.

    Returns:
        Dictionary with CPU details

    Raises:
        BasicAgentToolsError: If CPU information cannot be retrieved
    """
    if not HAS_PSUTIL:
        raise BasicAgentToolsError(
            "psutil package required for CPU information - install with: pip install psutil"
        )

    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_count_logical = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()

        result = {
            "usage_percent": cpu_percent,
            "physical_cores": cpu_count,
            "logical_cores": cpu_count_logical,
            "processor": platform.processor(),
        }

        if cpu_freq:
            result.update(
                {
                    "current_frequency_mhz": cpu_freq.current,
                    "min_frequency_mhz": cpu_freq.min,
                    "max_frequency_mhz": cpu_freq.max,
                }
            )

        return result
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to get CPU information: {str(e)}")


@strands_tool
def get_memory_info() -> dict[str, Union[int, float]]:
    """
    Get memory usage statistics.

    Returns:
        Dictionary with memory details in bytes and percentages

    Raises:
        BasicAgentToolsError: If memory information cannot be retrieved
    """
    if not HAS_PSUTIL:
        raise BasicAgentToolsError(
            "psutil package required for memory information - install with: pip install psutil"
        )

    try:
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return {
            "total_bytes": memory.total,
            "available_bytes": memory.available,
            "used_bytes": memory.used,
            "free_bytes": memory.free,
            "usage_percent": memory.percent,
            "swap_total_bytes": swap.total,
            "swap_used_bytes": swap.used,
            "swap_free_bytes": swap.free,
            "swap_usage_percent": swap.percent,
        }
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to get memory information: {str(e)}")


@strands_tool
def get_disk_usage(path: str) -> dict[str, Union[int, float, str]]:
    """
    Get disk usage statistics for a given path.

    Args:
        path: Path to check disk usage for (defaults to root)

    Returns:
        Dictionary with disk usage details

    Raises:
        BasicAgentToolsError: If path is invalid or disk usage cannot be retrieved
    """
    if not HAS_PSUTIL:
        raise BasicAgentToolsError(
            "psutil package required for disk usage information - install with: pip install psutil"
        )

    if not isinstance(path, str) or not path.strip():
        raise BasicAgentToolsError("Path must be a non-empty string")

    # Default to appropriate root for platform
    if path == "/":
        system = platform.system().lower()
        if system == "windows":
            path = "C:\\"

    try:
        usage = psutil.disk_usage(path)

        return {
            "path": path,
            "total_bytes": usage.total,
            "used_bytes": usage.used,
            "free_bytes": usage.free,
            "usage_percent": (usage.used / usage.total) * 100 if usage.total > 0 else 0,
        }
    except FileNotFoundError:
        raise BasicAgentToolsError(f"Path not found: {path}")
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to get disk usage for {path}: {str(e)}")


@strands_tool
def get_uptime() -> dict[str, Union[int, float, str]]:
    """
    Get system uptime information.

    Returns:
        Dictionary with uptime details

    Raises:
        BasicAgentToolsError: If uptime cannot be retrieved
    """
    if not HAS_PSUTIL:
        raise BasicAgentToolsError(
            "psutil package required for uptime information - install with: pip install psutil"
        )

    try:
        boot_time = psutil.boot_time()
        current_time = time.time()
        uptime_seconds = current_time - boot_time

        # Calculate human-readable components
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)

        return {
            "uptime_seconds": uptime_seconds,
            "boot_time_timestamp": boot_time,
            "boot_time_iso": time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(boot_time)
            ),
            "uptime_days": days,
            "uptime_hours": hours,
            "uptime_minutes": minutes,
            "uptime_seconds_remainder": seconds,
            "uptime_human": f"{days}d {hours}h {minutes}m {seconds}s",
        }
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to get system uptime: {str(e)}")
