"""Performance profiling utilities using cProfile.

This module provides functions to profile Python code execution and identify
performance bottlenecks using the standard library cProfile module.
"""

import cProfile
import importlib.util
import os
import pstats
import sys
from typing import Any

from basic_open_agent_tools.exceptions import ProfilingError


def profile_function(
    file_path: str, function_name: str, args_json: str
) -> dict[str, Any]:
    """Profile a specific function execution with given arguments.

    Executes a function from a Python file with profiling enabled and returns
    performance metrics including execution time, function calls, and bottlenecks.

    Args:
        file_path: Absolute path to the Python file containing the function
        function_name: Name of the function to profile
        args_json: JSON string of arguments to pass (e.g., '{"x": 5, "y": 10}')

    Returns:
        Dictionary containing:
        - total_time: Total execution time in seconds
        - function_calls: Total number of function calls
        - primitive_calls: Number of primitive (non-recursive) calls
        - top_functions: List of top 10 time-consuming functions with details

    Raises:
        TypeError: If arguments are not strings
        FileNotFoundError: If the file does not exist
        ProfilingError: If function cannot be found or executed

    Example:
        >>> result = profile_function("/path/to/module.py", "calculate", '{"n": 100}')
        >>> result["total_time"]
        0.025
        >>> result["top_functions"][0]["function"]
        "calculate"
    """
    if not isinstance(file_path, str):
        raise TypeError(f"file_path must be a string, got {type(file_path)}")
    if not isinstance(function_name, str):
        raise TypeError(f"function_name must be a string, got {type(function_name)}")
    if not isinstance(args_json, str):
        raise TypeError(f"args_json must be a string, got {type(args_json)}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Import the module
    try:
        spec = importlib.util.spec_from_file_location("profiled_module", file_path)
        if spec is None or spec.loader is None:
            raise ProfilingError(f"Cannot load module from {file_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as e:
        raise ProfilingError(f"Error loading module {file_path}: {str(e)}")

    # Get the function
    if not hasattr(module, function_name):
        raise ProfilingError(f"Function '{function_name}' not found in {file_path}")
    func = getattr(module, function_name)

    # Parse arguments
    import json

    try:
        args_dict = json.loads(args_json)
    except json.JSONDecodeError as e:
        raise ProfilingError(f"Invalid JSON in args_json: {str(e)}")

    # Profile the function
    profiler = cProfile.Profile()
    try:
        profiler.enable()
        if isinstance(args_dict, dict):
            func(**args_dict)
        elif isinstance(args_dict, list):
            func(*args_dict)
        else:
            func(args_dict)
        profiler.disable()
    except Exception as e:
        raise ProfilingError(f"Error executing function: {str(e)}")

    # Extract statistics
    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")

    # Get top functions directly from stats
    top_functions = []
    for func_key, (cc, nc, tt, ct, _callers) in list(stats.stats.items())[:10]:  # type: ignore[attr-defined]
        filename, line, func_name = func_key
        top_functions.append(
            {
                "function": f"{filename}:{line}({func_name})",
                "ncalls": f"{nc}/{cc}" if nc != cc else str(nc),
                "tottime": round(tt, 6),
                "cumtime": round(ct, 6),
                "percall_tot": round(tt / nc, 6) if nc > 0 else 0.0,
                "percall_cum": round(ct / nc, 6) if nc > 0 else 0.0,
            }
        )

    return {
        "total_time": round(stats.total_tt, 6),  # type: ignore[attr-defined]
        "function_calls": stats.total_calls,  # type: ignore[attr-defined]
        "primitive_calls": stats.prim_calls,  # type: ignore[attr-defined]
        "top_functions": top_functions,
    }


def profile_script(file_path: str) -> dict[str, Any]:
    """Profile entire script execution.

    Executes a Python script with profiling enabled and returns comprehensive
    performance metrics including execution breakdown and call graphs.

    Args:
        file_path: Absolute path to the Python script to profile

    Returns:
        Dictionary containing:
        - total_time: Total execution time in seconds
        - function_calls: Total number of function calls
        - primitive_calls: Number of primitive calls
        - top_functions: List of top 20 functions by cumulative time

    Raises:
        TypeError: If file_path is not a string
        FileNotFoundError: If the file does not exist
        ProfilingError: If script cannot be executed

    Example:
        >>> result = profile_script("/path/to/script.py")
        >>> result["total_time"]
        1.234
        >>> len(result["top_functions"])
        20
    """
    if not isinstance(file_path, str):
        raise TypeError(f"file_path must be a string, got {type(file_path)}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Profile the script execution
    profiler = cProfile.Profile()

    # Save original argv
    original_argv = sys.argv

    try:
        # Set argv to script path
        sys.argv = [file_path]

        # Read and compile the script
        with open(file_path, encoding="utf-8") as f:
            code = compile(f.read(), file_path, "exec")

        # Execute with profiling
        profiler.enable()
        exec(code, {"__name__": "__main__", "__file__": file_path})
        profiler.disable()
    except Exception as e:
        raise ProfilingError(f"Error executing script {file_path}: {str(e)}")
    finally:
        # Restore original argv
        sys.argv = original_argv

    # Extract statistics
    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")

    # Get top functions directly from stats
    top_functions = []
    for func_key, (cc, nc, tt, ct, _callers) in list(stats.stats.items())[:20]:  # type: ignore[attr-defined]
        filename, line, func_name = func_key
        top_functions.append(
            {
                "function": f"{filename}:{line}({func_name})",
                "ncalls": f"{nc}/{cc}" if nc != cc else str(nc),
                "tottime": round(tt, 6),
                "cumtime": round(ct, 6),
                "percall_tot": round(tt / nc, 6) if nc > 0 else 0.0,
                "percall_cum": round(ct / nc, 6) if nc > 0 else 0.0,
            }
        )

    return {
        "total_time": round(stats.total_tt, 6),  # type: ignore[attr-defined]
        "function_calls": stats.total_calls,  # type: ignore[attr-defined]
        "primitive_calls": stats.prim_calls,  # type: ignore[attr-defined]
        "top_functions": top_functions,
    }


def get_hotspots(profile_data: str) -> list[dict[str, Any]]:
    """Parse cProfile output for performance hotspots.

    Analyzes cProfile statistics output and extracts performance hotspots,
    identifying functions that consume the most time.

    Args:
        profile_data: String output from cProfile (pstats format)

    Returns:
        List of dictionaries, each containing:
        - function: Function name/location
        - ncalls: Number of calls
        - tottime: Total time in function (excluding subcalls)
        - cumtime: Cumulative time (including subcalls)
        - percall: Time per call
        - percent: Percentage of total execution time

    Raises:
        TypeError: If profile_data is not a string
        ProfilingError: If profile_data cannot be parsed

    Example:
        >>> hotspots = get_hotspots(profile_output_string)
        >>> hotspots[0]["function"]
        "slow_function"
        >>> hotspots[0]["percent"]
        45.2
    """
    if not isinstance(profile_data, str):
        raise TypeError(f"profile_data must be a string, got {type(profile_data)}")

    hotspots = []
    lines = profile_data.split("\n")

    total_time = 0.0
    # Try to extract total time from header
    for line in lines[:10]:
        if "seconds" in line.lower() and "function calls" in line.lower():
            parts = line.split()
            for i, part in enumerate(parts):
                if part.replace(".", "").isdigit() and i > 0:
                    try:
                        total_time = float(part)
                        break
                    except ValueError:
                        continue

    # Parse function statistics
    for line in lines:
        stripped = line.strip()
        if (
            not stripped
            or "function calls" in line.lower()
            or "ncalls" in line.lower()
            or "Ordered by" in line
        ):
            continue

        parts = stripped.split()
        if len(parts) >= 6:
            # Check if first part looks like call count
            if parts[0].replace(".", "").replace("/", "").isdigit():
                try:
                    ncalls = parts[0]
                    tottime = float(parts[1])
                    _percall = float(parts[2])  # Not used but part of format
                    cumtime = float(parts[3])
                    percall_cum = float(parts[4])
                    function = " ".join(parts[5:])

                    # Calculate percentage if we have total time
                    percent = (cumtime / total_time * 100) if total_time > 0 else 0.0

                    hotspots.append(
                        {
                            "function": function,
                            "ncalls": ncalls,
                            "tottime": tottime,
                            "cumtime": cumtime,
                            "percall": percall_cum,
                            "percent": round(percent, 2),
                        }
                    )
                except (ValueError, IndexError):
                    continue

    # Sort by cumulative time descending
    hotspots.sort(key=lambda x: float(x["cumtime"]), reverse=True)  # type: ignore[arg-type]

    return hotspots[:20]  # Return top 20 hotspots
