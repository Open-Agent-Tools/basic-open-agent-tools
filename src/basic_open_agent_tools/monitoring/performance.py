"""Performance monitoring and profiling utilities."""

import time
from typing import Dict, List, Union

try:
    from strands import tool as strands_tool
except ImportError:

    def strands_tool(func):
        """Fallback decorator when strands is not available."""
        return func


# Try to import system monitoring library
try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from ..exceptions import BasicAgentToolsError


@strands_tool
def monitor_function_performance(
    duration_seconds: int = 60,
) -> Dict[str, Union[int, float, List]]:
    """
    Monitor system performance metrics over a specified duration.

    Args:
        duration_seconds: How long to monitor (1-3600 seconds)

    Returns:
        Dictionary with performance metrics

    Raises:
        BasicAgentToolsError: If monitoring fails or psutil unavailable
    """
    if not HAS_PSUTIL:
        raise BasicAgentToolsError(
            "psutil package required for performance monitoring - install with: pip install psutil"
        )

    if (
        not isinstance(duration_seconds, int)
        or duration_seconds < 1
        or duration_seconds > 3600
    ):
        raise BasicAgentToolsError(
            "Duration must be an integer between 1 and 3600 seconds"
        )

    try:
        cpu_samples = []
        memory_samples = []
        disk_samples = []
        start_time = time.time()

        # Sample every 2 seconds for the duration
        sample_interval = min(
            2, duration_seconds // 10 if duration_seconds >= 10 else 1
        )
        samples_taken = 0

        while time.time() - start_time < duration_seconds:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_samples.append(cpu_percent)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_samples.append(memory.percent)

            # Disk usage for root partition
            try:
                disk = psutil.disk_usage("/")
                disk_percent = (disk.used / disk.total) * 100 if disk.total > 0 else 0
            except Exception:
                # Windows fallback
                try:
                    disk = psutil.disk_usage("C:\\")
                    disk_percent = (
                        (disk.used / disk.total) * 100 if disk.total > 0 else 0
                    )
                except Exception:
                    disk_percent = 0

            disk_samples.append(disk_percent)

            samples_taken += 1
            time.sleep(sample_interval)

        # Calculate statistics
        def calc_stats(samples):
            if not samples:
                return {"min": 0, "max": 0, "avg": 0}
            return {
                "min": round(min(samples), 2),
                "max": round(max(samples), 2),
                "avg": round(sum(samples) / len(samples), 2),
            }

        actual_duration = time.time() - start_time

        return {
            "monitoring_duration_seconds": round(actual_duration, 2),
            "samples_taken": samples_taken,
            "sample_interval_seconds": sample_interval,
            "cpu_usage_percent": calc_stats(cpu_samples),
            "memory_usage_percent": calc_stats(memory_samples),
            "disk_usage_percent": calc_stats(disk_samples),
            "monitoring_status": "completed",
        }

    except Exception as e:
        raise BasicAgentToolsError(f"Performance monitoring failed: {str(e)}")


@strands_tool
def get_system_load_average() -> Dict[str, Union[float, str, bool]]:
    """
    Get system load average information.

    Returns:
        Dictionary with load average metrics

    Raises:
        BasicAgentToolsError: If load average cannot be retrieved
    """
    if not HAS_PSUTIL:
        raise BasicAgentToolsError(
            "psutil package required for load average - install with: pip install psutil"
        )

    try:
        # Load average is primarily a Unix concept
        load_available = hasattr(psutil, "getloadavg")

        result = {
            "load_average_available": load_available,
            "platform_support": "unix_like"
            if load_available
            else "windows_or_unsupported",
        }

        if load_available:
            try:
                load1, load5, load15 = psutil.getloadavg()
                result.update(
                    {
                        "load_1min": round(load1, 2),
                        "load_5min": round(load5, 2),
                        "load_15min": round(load15, 2),
                        "cpu_cores": psutil.cpu_count(),
                        "load_per_core_1min": round(load1 / psutil.cpu_count(), 2),
                        "system_busy_1min": load1 > psutil.cpu_count(),
                        "retrieval_status": "success",
                    }
                )
            except Exception as e:
                result["retrieval_status"] = f"error: {str(e)}"
        else:
            # For Windows, provide CPU usage as alternative
            cpu_percent = psutil.cpu_percent(interval=1)
            result.update(
                {
                    "alternative_cpu_usage_percent": cpu_percent,
                    "cpu_cores": psutil.cpu_count(),
                    "retrieval_status": "load_avg_unavailable_using_cpu_percent",
                }
            )

        return result

    except Exception as e:
        raise BasicAgentToolsError(f"Failed to get system load average: {str(e)}")


@strands_tool
def profile_code_execution(
    code_snippet: str, iterations: int = 1
) -> Dict[str, Union[float, str, int, bool]]:
    """
    Profile execution time of a code snippet.

    Args:
        code_snippet: Python code to profile (as string)
        iterations: Number of times to run the code

    Returns:
        Dictionary with profiling results

    Raises:
        BasicAgentToolsError: If profiling fails or code is invalid
    """
    if not isinstance(code_snippet, str) or not code_snippet.strip():
        raise BasicAgentToolsError("Code snippet must be a non-empty string")

    if not isinstance(iterations, int) or iterations < 1 or iterations > 10000:
        raise BasicAgentToolsError("Iterations must be an integer between 1 and 10000")

    # Basic security check - reject dangerous keywords
    dangerous_keywords = [
        "import os",
        "import sys",
        "exec(",
        "eval(",
        "__import__",
        "open(",
        "file(",
    ]
    code_lower = code_snippet.lower()
    for keyword in dangerous_keywords:
        if keyword in code_lower:
            raise BasicAgentToolsError(
                f"Code contains potentially dangerous keyword: {keyword}"
            )

    try:
        # Compile the code first to check for syntax errors
        compiled_code = compile(code_snippet, "<string>", "exec")

        execution_times = []
        total_start_time = time.perf_counter()

        for _i in range(iterations):
            start_time = time.perf_counter()

            # Execute in a restricted namespace
            namespace = {"__builtins__": {}}  # Minimal namespace for security
            exec(compiled_code, namespace)

            end_time = time.perf_counter()
            execution_times.append(end_time - start_time)

        total_end_time = time.perf_counter()

        # Calculate statistics
        min_time = min(execution_times)
        max_time = max(execution_times)
        avg_time = sum(execution_times) / len(execution_times)
        total_time = total_end_time - total_start_time

        return {
            "code_snippet": code_snippet[:100] + "..."
            if len(code_snippet) > 100
            else code_snippet,
            "iterations": iterations,
            "min_execution_time_seconds": round(min_time, 6),
            "max_execution_time_seconds": round(max_time, 6),
            "avg_execution_time_seconds": round(avg_time, 6),
            "total_execution_time_seconds": round(total_time, 6),
            "executions_per_second": round(1 / avg_time, 2)
            if avg_time > 0
            else float("inf"),
            "profiling_successful": True,
            "profiling_status": "completed",
        }

    except SyntaxError as e:
        raise BasicAgentToolsError(f"Syntax error in code snippet: {str(e)}")
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to profile code execution: {str(e)}")


@strands_tool
def benchmark_disk_io(
    file_path: str, data_size_kb: int = 1024
) -> Dict[str, Union[str, int, float]]:
    """
    Benchmark disk I/O performance by writing and reading test data.

    Args:
        file_path: Path for temporary test file
        data_size_kb: Size of test data in KB (1-10240)

    Returns:
        Dictionary with I/O benchmark results

    Raises:
        BasicAgentToolsError: If benchmarking fails
    """
    if not isinstance(file_path, str) or not file_path.strip():
        raise BasicAgentToolsError("File path must be a non-empty string")

    if not isinstance(data_size_kb, int) or data_size_kb < 1 or data_size_kb > 10240:
        raise BasicAgentToolsError(
            "Data size must be an integer between 1 and 10240 KB"
        )

    import os

    file_path = file_path.strip()

    try:
        # Generate test data
        test_data = b"A" * (data_size_kb * 1024)  # KB to bytes

        # Write benchmark
        write_start = time.perf_counter()
        with open(file_path, "wb") as f:
            f.write(test_data)
            f.flush()  # Ensure data is written to disk
            os.fsync(f.fileno())  # Force OS to write to disk
        write_end = time.perf_counter()

        write_time = write_end - write_start
        write_speed_mbps = (
            (data_size_kb / 1024) / write_time if write_time > 0 else float("inf")
        )

        # Read benchmark
        read_start = time.perf_counter()
        with open(file_path, "rb") as f:
            read_data = f.read()
        read_end = time.perf_counter()

        read_time = read_end - read_start
        read_speed_mbps = (
            (data_size_kb / 1024) / read_time if read_time > 0 else float("inf")
        )

        # Verify data integrity
        data_integrity_ok = len(read_data) == len(test_data) and read_data == test_data

        # Clean up
        try:
            os.remove(file_path)
        except Exception:
            pass  # Best effort cleanup

        return {
            "file_path": file_path,
            "data_size_kb": data_size_kb,
            "data_size_mb": round(data_size_kb / 1024, 2),
            "write_time_seconds": round(write_time, 4),
            "read_time_seconds": round(read_time, 4),
            "write_speed_mbps": round(write_speed_mbps, 2),
            "read_speed_mbps": round(read_speed_mbps, 2),
            "data_integrity_verified": data_integrity_ok,
            "benchmark_status": "completed",
        }

    except PermissionError:
        raise BasicAgentToolsError(f"Permission denied accessing file: {file_path}")
    except Exception as e:
        # Clean up on error
        try:
            os.remove(file_path)
        except Exception:
            pass
        raise BasicAgentToolsError(f"Disk I/O benchmark failed: {str(e)}")
