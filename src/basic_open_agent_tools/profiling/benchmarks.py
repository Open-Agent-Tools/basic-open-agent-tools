"""Benchmarking utilities for comparing function performance.

This module provides functions to benchmark Python function execution over
multiple iterations and compare different implementations.
"""

import importlib.util
import os
import statistics
import time
from typing import Any

from basic_open_agent_tools.exceptions import ProfilingError


def benchmark_execution(
    file_path: str, function_name: str, args_json: str, iterations: int
) -> dict[str, Any]:
    """Benchmark function execution over multiple iterations.

    Executes a function multiple times and collects detailed timing statistics
    including min, max, mean, median, and standard deviation.

    Args:
        file_path: Absolute path to the Python file containing the function
        function_name: Name of the function to benchmark
        args_json: JSON string of arguments to pass
        iterations: Number of iterations to run

    Returns:
        Dictionary containing:
        - iterations: Number of iterations run
        - min_time: Minimum execution time in seconds
        - max_time: Maximum execution time in seconds
        - mean_time: Mean execution time in seconds
        - median_time: Median execution time in seconds
        - stddev_time: Standard deviation of execution times
        - total_time: Total time for all iterations

    Raises:
        TypeError: If arguments are not correct types
        ValueError: If iterations is less than 1
        FileNotFoundError: If the file does not exist
        ProfilingError: If function cannot be found or executed

    Example:
        >>> result = benchmark_execution("/path/to/module.py", "calculate", '{"n": 100}', 100)
        >>> result["mean_time"]
        0.0023
        >>> result["stddev_time"]
        0.0001
    """
    if not isinstance(file_path, str):
        raise TypeError(f"file_path must be a string, got {type(file_path)}")
    if not isinstance(function_name, str):
        raise TypeError(f"function_name must be a string, got {type(function_name)}")
    if not isinstance(args_json, str):
        raise TypeError(f"args_json must be a string, got {type(args_json)}")
    if not isinstance(iterations, int):
        raise TypeError(f"iterations must be an int, got {type(iterations)}")

    if iterations < 1:
        raise ValueError("iterations must be at least 1")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Import the module
    try:
        spec = importlib.util.spec_from_file_location("benchmark_module", file_path)
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

    # Run benchmark
    times = []
    try:
        for _ in range(iterations):
            start = time.perf_counter()

            if isinstance(args_dict, dict):
                func(**args_dict)
            elif isinstance(args_dict, list):
                func(*args_dict)
            else:
                func(args_dict)

            end = time.perf_counter()
            times.append(end - start)

    except Exception as e:
        raise ProfilingError(f"Error executing function: {str(e)}")

    # Calculate statistics
    return {
        "iterations": iterations,
        "min_time": round(min(times), 6),
        "max_time": round(max(times), 6),
        "mean_time": round(statistics.mean(times), 6),
        "median_time": round(statistics.median(times), 6),
        "stddev_time": round(statistics.stdev(times), 6) if len(times) > 1 else 0.0,
        "total_time": round(sum(times), 6),
    }


def compare_implementations(
    file_path1: str,
    function_name1: str,
    args_json1: str,
    file_path2: str,
    function_name2: str,
    args_json2: str,
    iterations: int,
) -> dict[str, Any]:
    """Compare performance of two function implementations.

    Benchmarks two functions and compares their performance, determining which
    is faster and by what factor.

    Args:
        file_path1: Path to first Python file
        function_name1: Name of first function
        args_json1: JSON arguments for first function
        file_path2: Path to second Python file
        function_name2: Name of second function
        args_json2: JSON arguments for second function
        iterations: Number of iterations to run for each

    Returns:
        Dictionary containing:
        - implementation1: Benchmark results for first implementation
        - implementation2: Benchmark results for second implementation
        - winner: Name of faster implementation
        - speedup_factor: How many times faster the winner is
        - difference_ms: Time difference in milliseconds

    Raises:
        TypeError: If arguments are not correct types
        ValueError: If iterations is less than 1
        FileNotFoundError: If either file does not exist
        ProfilingError: If functions cannot be found or executed

    Example:
        >>> result = compare_implementations(
        ...     "/path/to/impl1.py", "sort_algo1", '{"data": [5,2,8]}',
        ...     "/path/to/impl2.py", "sort_algo2", '{"data": [5,2,8]}',
        ...     100
        ... )
        >>> result["winner"]
        "sort_algo2"
        >>> result["speedup_factor"]
        2.3
    """
    if not isinstance(file_path1, str):
        raise TypeError(f"file_path1 must be a string, got {type(file_path1)}")
    if not isinstance(function_name1, str):
        raise TypeError(f"function_name1 must be a string, got {type(function_name1)}")
    if not isinstance(args_json1, str):
        raise TypeError(f"args_json1 must be a string, got {type(args_json1)}")
    if not isinstance(file_path2, str):
        raise TypeError(f"file_path2 must be a string, got {type(file_path2)}")
    if not isinstance(function_name2, str):
        raise TypeError(f"function_name2 must be a string, got {type(function_name2)}")
    if not isinstance(args_json2, str):
        raise TypeError(f"args_json2 must be a string, got {type(args_json2)}")
    if not isinstance(iterations, int):
        raise TypeError(f"iterations must be an int, got {type(iterations)}")

    if iterations < 1:
        raise ValueError("iterations must be at least 1")

    # Benchmark first implementation
    result1 = benchmark_execution(file_path1, function_name1, args_json1, iterations)

    # Benchmark second implementation
    result2 = benchmark_execution(file_path2, function_name2, args_json2, iterations)

    # Compare results
    mean1 = result1["mean_time"]
    mean2 = result2["mean_time"]

    if mean1 < mean2:
        winner = function_name1
        speedup = mean2 / mean1 if mean1 > 0 else 0.0
    else:
        winner = function_name2
        speedup = mean1 / mean2 if mean2 > 0 else 0.0

    difference_ms = abs(mean1 - mean2) * 1000

    return {
        "implementation1": {
            "name": function_name1,
            "mean_time": mean1,
            "median_time": result1["median_time"],
            "stddev_time": result1["stddev_time"],
        },
        "implementation2": {
            "name": function_name2,
            "mean_time": mean2,
            "median_time": result2["median_time"],
            "stddev_time": result2["stddev_time"],
        },
        "winner": winner,
        "speedup_factor": round(speedup, 2),
        "difference_ms": round(difference_ms, 4),
    }
