"""Memory analysis utilities using tracemalloc.

This module provides functions to measure memory usage, detect memory leaks,
and analyze memory allocation patterns in Python code.
"""

import importlib.util
import os
import sys
import tracemalloc
from typing import Any

from basic_open_agent_tools.exceptions import ProfilingError


def measure_memory_usage(
    file_path: str, function_name: str, args_json: str
) -> dict[str, Any]:
    """Measure memory usage of a specific function.

    Executes a function with memory tracking enabled and returns detailed
    memory usage metrics including peak usage and allocation counts.

    Args:
        file_path: Absolute path to the Python file containing the function
        function_name: Name of the function to measure
        args_json: JSON string of arguments to pass

    Returns:
        Dictionary containing:
        - peak_memory_mb: Peak memory usage in megabytes
        - current_memory_mb: Current memory usage in megabytes
        - memory_delta_mb: Memory increase during execution in megabytes
        - allocation_count: Number of memory allocations
        - top_allocations: Top 10 memory allocation locations

    Raises:
        TypeError: If arguments are not strings
        FileNotFoundError: If the file does not exist
        ProfilingError: If function cannot be found or executed

    Example:
        >>> result = measure_memory_usage("/path/to/module.py", "process_data", '{"size": 1000}')
        >>> result["peak_memory_mb"]
        25.4
        >>> result["allocation_count"]
        1523
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
        spec = importlib.util.spec_from_file_location("memory_module", file_path)
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

    # Start memory tracking
    tracemalloc.start()
    initial_snapshot = tracemalloc.take_snapshot()
    initial_current, initial_peak = tracemalloc.get_traced_memory()

    # Execute function
    try:
        if isinstance(args_dict, dict):
            func(**args_dict)
        elif isinstance(args_dict, list):
            func(*args_dict)
        else:
            func(args_dict)
    except Exception as e:
        tracemalloc.stop()
        raise ProfilingError(f"Error executing function: {str(e)}")

    # Get memory statistics
    current, peak = tracemalloc.get_traced_memory()
    final_snapshot = tracemalloc.take_snapshot()

    # Get top allocations
    top_stats = final_snapshot.compare_to(initial_snapshot, "lineno")
    top_allocations = []

    for stat in top_stats[:10]:
        top_allocations.append(
            {
                "file": stat.traceback.format()[0] if stat.traceback else "unknown",
                "size_mb": round(stat.size / 1024 / 1024, 4),
                "count": stat.count,
            }
        )

    tracemalloc.stop()

    return {
        "peak_memory_mb": round(peak / 1024 / 1024, 4),
        "current_memory_mb": round(current / 1024 / 1024, 4),
        "memory_delta_mb": round((peak - initial_peak) / 1024 / 1024, 4),
        "allocation_count": len(final_snapshot.statistics("lineno")),
        "top_allocations": top_allocations,
    }


def detect_memory_leaks(
    file_path: str, function_name: str, args_json: str, iterations: int
) -> list[dict[str, Any]]:
    """Identify potential memory leaks in a function.

    Executes a function multiple times and monitors memory growth to detect
    potential memory leaks. Returns detailed analysis of memory patterns.

    Args:
        file_path: Absolute path to the Python file containing the function
        function_name: Name of the function to test
        args_json: JSON string of arguments to pass
        iterations: Number of times to execute the function

    Returns:
        List of dictionaries containing:
        - iteration: Iteration number
        - memory_mb: Memory usage in megabytes
        - delta_mb: Change from previous iteration
        - leak_detected: Boolean indicating potential leak
        - evidence: Description of leak evidence if detected

    Raises:
        TypeError: If arguments are not correct types
        ValueError: If iterations is less than 2
        FileNotFoundError: If the file does not exist
        ProfilingError: If function cannot be found or executed

    Example:
        >>> result = detect_memory_leaks("/path/to/module.py", "cache_data", '{}', 10)
        >>> result[-1]["leak_detected"]
        True
        >>> result[-1]["evidence"]
        "Memory increased by 5.2 MB over 10 iterations"
    """
    if not isinstance(file_path, str):
        raise TypeError(f"file_path must be a string, got {type(file_path)}")
    if not isinstance(function_name, str):
        raise TypeError(f"function_name must be a string, got {type(function_name)}")
    if not isinstance(args_json, str):
        raise TypeError(f"args_json must be a string, got {type(args_json)}")
    if not isinstance(iterations, int):
        raise TypeError(f"iterations must be an int, got {type(iterations)}")

    if iterations < 2:
        raise ValueError("iterations must be at least 2")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Import the module
    try:
        spec = importlib.util.spec_from_file_location("leak_module", file_path)
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

    # Start memory tracking
    tracemalloc.start()
    results = []
    previous_memory = 0.0

    try:
        for i in range(iterations):
            # Execute function
            if isinstance(args_dict, dict):
                func(**args_dict)
            elif isinstance(args_dict, list):
                func(*args_dict)
            else:
                func(args_dict)

            # Get current memory
            current, peak = tracemalloc.get_traced_memory()
            current_mb = round(current / 1024 / 1024, 4)

            delta = current_mb - previous_memory if i > 0 else 0.0

            results.append(
                {
                    "iteration": i + 1,
                    "memory_mb": current_mb,
                    "delta_mb": round(delta, 4),
                    "leak_detected": False,
                    "evidence": "",
                }
            )

            previous_memory = current_mb

    except Exception as e:
        tracemalloc.stop()
        raise ProfilingError(f"Error executing function: {str(e)}")
    finally:
        tracemalloc.stop()

    # Analyze for leaks
    if len(results) >= 2:
        first_memory = float(results[0]["memory_mb"])  # type: ignore[arg-type]
        last_memory = float(results[-1]["memory_mb"])  # type: ignore[arg-type]
        total_growth = last_memory - first_memory

        # Check for consistent growth (potential leak)
        if total_growth > 1.0:  # More than 1 MB growth
            # Check if growth is consistent
            positive_deltas = sum(1 for r in results[1:] if float(r["delta_mb"]) > 0)  # type: ignore[misc,arg-type]
            if positive_deltas > int(len(results) * 0.7):  # 70% of iterations grew
                # Mark as leak
                results[-1]["leak_detected"] = True
                results[-1]["evidence"] = (
                    f"Memory increased by {round(total_growth, 2)} MB over {iterations} iterations"
                )

    return results


def get_memory_snapshot(file_path: str) -> dict[str, Any]:
    """Take a memory snapshot during script execution.

    Executes a Python script and captures detailed memory allocation information
    including total allocated memory and top allocation locations.

    Args:
        file_path: Absolute path to the Python script to profile

    Returns:
        Dictionary containing:
        - total_allocated_mb: Total memory allocated in megabytes
        - peak_memory_mb: Peak memory usage in megabytes
        - top_allocations: Top 20 memory allocation locations
        - allocation_count: Total number of allocations

    Raises:
        TypeError: If file_path is not a string
        FileNotFoundError: If the file does not exist
        ProfilingError: If script cannot be executed

    Example:
        >>> snapshot = get_memory_snapshot("/path/to/script.py")
        >>> snapshot["total_allocated_mb"]
        150.2
        >>> len(snapshot["top_allocations"])
        20
    """
    if not isinstance(file_path, str):
        raise TypeError(f"file_path must be a string, got {type(file_path)}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Start memory tracking
    tracemalloc.start()

    # Save original argv
    original_argv = sys.argv

    try:
        # Set argv to script path
        sys.argv = [file_path]

        # Read and execute the script
        with open(file_path, encoding="utf-8") as f:
            code = compile(f.read(), file_path, "exec")

        exec(code, {"__name__": "__main__", "__file__": file_path})

        # Get memory statistics
        current, peak = tracemalloc.get_traced_memory()
        snapshot = tracemalloc.take_snapshot()

        # Get top allocations
        top_stats = snapshot.statistics("lineno")
        top_allocations = []

        for stat in top_stats[:20]:
            top_allocations.append(
                {
                    "file": stat.traceback.format()[0] if stat.traceback else "unknown",
                    "size_mb": round(stat.size / 1024 / 1024, 4),
                    "count": stat.count,
                }
            )

        result = {
            "total_allocated_mb": round(current / 1024 / 1024, 4),
            "peak_memory_mb": round(peak / 1024 / 1024, 4),
            "top_allocations": top_allocations,
            "allocation_count": len(top_stats),
        }

    except Exception as e:
        raise ProfilingError(f"Error executing script {file_path}: {str(e)}")
    finally:
        # Restore original argv
        sys.argv = original_argv
        tracemalloc.stop()

    return result
