"""Tests for profiling module."""

import os
import tempfile

import pytest

from basic_open_agent_tools.exceptions import ProfilingError
from basic_open_agent_tools.profiling import (
    benchmark_execution,
    compare_implementations,
    detect_memory_leaks,
    get_hotspots,
    get_memory_snapshot,
    measure_memory_usage,
    profile_function,
    profile_script,
)

# Sample code for testing
SAMPLE_MODULE = '''"""Sample module for profiling tests."""
import time

def fast_function(n: int) -> int:
    """A fast function."""
    return n * 2

def slow_function(n: int) -> int:
    """A slower function."""
    result = 0
    for i in range(n):
        result += i
    return result

def memory_function(size: int) -> list:
    """A function that allocates memory."""
    return [i for i in range(size)]

def leak_function() -> list:
    """A function that might leak memory."""
    global _cache
    if "_cache" not in globals():
        _cache = []
    _cache.append([0] * 10000)
    return _cache

def complex_function(n: int) -> int:
    """A more complex function."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b
'''

SAMPLE_SCRIPT = '''"""Sample script for profiling tests."""
def main():
    total = 0
    for i in range(1000):
        total += i ** 2
    print(f"Total: {total}")

if __name__ == "__main__":
    main()
'''

COMPARISON_MODULE_1 = '''"""First implementation for comparison."""
def bubble_sort(data: list) -> list:
    """Bubble sort implementation."""
    arr = data.copy()
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
'''

COMPARISON_MODULE_2 = '''"""Second implementation for comparison."""
def quick_sort(data: list) -> list:
    """Quick sort implementation."""
    if len(data) <= 1:
        return data
    pivot = data[len(data) // 2]
    left = [x for x in data if x < pivot]
    middle = [x for x in data if x == pivot]
    right = [x for x in data if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
'''


@pytest.fixture
def sample_module_file():
    """Create temporary sample module file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(SAMPLE_MODULE)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


@pytest.fixture
def sample_script_file():
    """Create temporary sample script file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(SAMPLE_SCRIPT)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


@pytest.fixture
def comparison_files():
    """Create temporary comparison module files."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f1:
        f1.write(COMPARISON_MODULE_1)
        temp_path1 = f1.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f2:
        f2.write(COMPARISON_MODULE_2)
        temp_path2 = f2.name

    yield temp_path1, temp_path2

    os.unlink(temp_path1)
    os.unlink(temp_path2)


# Performance Profiling Tests


def test_profile_function_basic(sample_module_file):
    """Test basic function profiling."""
    result = profile_function(sample_module_file, "fast_function", '{"n": 10}')

    assert "total_time" in result
    assert "function_calls" in result
    assert "primitive_calls" in result
    assert "top_functions" in result
    assert isinstance(result["total_time"], float)
    assert isinstance(result["function_calls"], int)
    assert isinstance(result["top_functions"], list)


def test_profile_function_with_dict_args(sample_module_file):
    """Test profiling with dictionary arguments."""
    result = profile_function(sample_module_file, "slow_function", '{"n": 100}')

    assert result["total_time"] >= 0
    assert result["function_calls"] > 0
    assert len(result["top_functions"]) > 0


def test_profile_function_with_list_args(sample_module_file):
    """Test profiling with list arguments."""
    result = profile_function(sample_module_file, "fast_function", "[5]")

    assert result["total_time"] >= 0
    assert "top_functions" in result


def test_profile_function_invalid_file():
    """Test profiling with non-existent file."""
    with pytest.raises(FileNotFoundError):
        profile_function("/nonexistent/file.py", "func", "{}")


def test_profile_function_invalid_function(sample_module_file):
    """Test profiling with non-existent function."""
    with pytest.raises(ProfilingError, match="not found"):
        profile_function(sample_module_file, "nonexistent_func", "{}")


def test_profile_function_invalid_json(sample_module_file):
    """Test profiling with invalid JSON."""
    with pytest.raises(ProfilingError, match="Invalid JSON"):
        profile_function(sample_module_file, "fast_function", "not json")


def test_profile_function_type_errors(sample_module_file):
    """Test profiling with wrong types."""
    with pytest.raises(TypeError):
        profile_function(123, "func", "{}")

    with pytest.raises(TypeError):
        profile_function(sample_module_file, 123, "{}")

    with pytest.raises(TypeError):
        profile_function(sample_module_file, "func", 123)


def test_profile_script_basic(sample_script_file):
    """Test basic script profiling."""
    result = profile_script(sample_script_file)

    assert "total_time" in result
    assert "function_calls" in result
    assert "primitive_calls" in result
    assert "top_functions" in result
    assert isinstance(result["total_time"], float)
    assert len(result["top_functions"]) > 0


def test_profile_script_invalid_file():
    """Test script profiling with non-existent file."""
    with pytest.raises(FileNotFoundError):
        profile_script("/nonexistent/script.py")


def test_profile_script_type_error():
    """Test script profiling with wrong type."""
    with pytest.raises(TypeError):
        profile_script(123)


def test_get_hotspots_basic():
    """Test hotspot extraction from profile data."""
    profile_output = """         5 function calls in 0.123 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.100    0.100    0.120    0.120 module.py:10(slow_func)
        2    0.020    0.010    0.020    0.010 module.py:20(helper)
        1    0.002    0.002    0.002    0.002 module.py:30(fast_func)
"""

    hotspots = get_hotspots(profile_output)

    assert isinstance(hotspots, list)
    assert len(hotspots) >= 3
    assert "function" in hotspots[0]
    assert "cumtime" in hotspots[0]
    assert "percent" in hotspots[0]


def test_get_hotspots_empty_string():
    """Test hotspot extraction with empty string."""
    hotspots = get_hotspots("")
    assert hotspots == []


def test_get_hotspots_type_error():
    """Test hotspot extraction with wrong type."""
    with pytest.raises(TypeError):
        get_hotspots(123)


# Memory Analysis Tests


def test_measure_memory_usage_basic(sample_module_file):
    """Test basic memory measurement."""
    result = measure_memory_usage(
        sample_module_file, "memory_function", '{"size": 1000}'
    )

    assert "peak_memory_mb" in result
    assert "current_memory_mb" in result
    assert "memory_delta_mb" in result
    assert "allocation_count" in result
    assert "top_allocations" in result
    assert isinstance(result["peak_memory_mb"], float)
    assert isinstance(result["top_allocations"], list)
    assert result["peak_memory_mb"] >= 0


def test_measure_memory_usage_small_allocation(sample_module_file):
    """Test memory measurement with small allocation."""
    result = measure_memory_usage(sample_module_file, "fast_function", '{"n": 5}')

    assert result["peak_memory_mb"] >= 0
    assert result["allocation_count"] >= 0


def test_measure_memory_usage_invalid_file():
    """Test memory measurement with non-existent file."""
    with pytest.raises(FileNotFoundError):
        measure_memory_usage("/nonexistent/file.py", "func", "{}")


def test_measure_memory_usage_invalid_function(sample_module_file):
    """Test memory measurement with non-existent function."""
    with pytest.raises(ProfilingError, match="not found"):
        measure_memory_usage(sample_module_file, "nonexistent", "{}")


def test_measure_memory_usage_type_errors(sample_module_file):
    """Test memory measurement with wrong types."""
    with pytest.raises(TypeError):
        measure_memory_usage(123, "func", "{}")

    with pytest.raises(TypeError):
        measure_memory_usage(sample_module_file, 123, "{}")

    with pytest.raises(TypeError):
        measure_memory_usage(sample_module_file, "func", 123)


def test_detect_memory_leaks_basic(sample_module_file):
    """Test basic memory leak detection."""
    result = detect_memory_leaks(
        sample_module_file, "memory_function", '{"size": 100}', 5
    )

    assert isinstance(result, list)
    assert len(result) == 5
    assert "iteration" in result[0]
    assert "memory_mb" in result[0]
    assert "delta_mb" in result[0]
    assert "leak_detected" in result[0]
    assert "evidence" in result[0]


def test_detect_memory_leaks_no_leak(sample_module_file):
    """Test leak detection with non-leaking function."""
    result = detect_memory_leaks(sample_module_file, "fast_function", '{"n": 10}', 5)

    assert len(result) == 5
    # Most iterations should not show a leak for this simple function
    assert all(isinstance(r["leak_detected"], bool) for r in result)


def test_detect_memory_leaks_invalid_iterations(sample_module_file):
    """Test leak detection with invalid iterations."""
    with pytest.raises(ValueError, match="at least 2"):
        detect_memory_leaks(sample_module_file, "fast_function", "{}", 1)


def test_detect_memory_leaks_type_errors(sample_module_file):
    """Test leak detection with wrong types."""
    with pytest.raises(TypeError):
        detect_memory_leaks(123, "func", "{}", 5)

    with pytest.raises(TypeError):
        detect_memory_leaks(sample_module_file, 123, "{}", 5)

    with pytest.raises(TypeError):
        detect_memory_leaks(sample_module_file, "func", 123, 5)

    with pytest.raises(TypeError):
        detect_memory_leaks(sample_module_file, "func", "{}", "5")


def test_get_memory_snapshot_basic(sample_script_file):
    """Test basic memory snapshot."""
    result = get_memory_snapshot(sample_script_file)

    assert "total_allocated_mb" in result
    assert "peak_memory_mb" in result
    assert "top_allocations" in result
    assert "allocation_count" in result
    assert isinstance(result["total_allocated_mb"], float)
    assert isinstance(result["top_allocations"], list)
    assert result["allocation_count"] > 0


def test_get_memory_snapshot_invalid_file():
    """Test memory snapshot with non-existent file."""
    with pytest.raises(FileNotFoundError):
        get_memory_snapshot("/nonexistent/script.py")


def test_get_memory_snapshot_type_error():
    """Test memory snapshot with wrong type."""
    with pytest.raises(TypeError):
        get_memory_snapshot(123)


# Benchmarking Tests


def test_benchmark_execution_basic(sample_module_file):
    """Test basic benchmarking."""
    result = benchmark_execution(sample_module_file, "fast_function", '{"n": 10}', 10)

    assert "iterations" in result
    assert "min_time" in result
    assert "max_time" in result
    assert "mean_time" in result
    assert "median_time" in result
    assert "stddev_time" in result
    assert "total_time" in result
    assert result["iterations"] == 10
    assert result["min_time"] <= result["mean_time"] <= result["max_time"]


def test_benchmark_execution_single_iteration(sample_module_file):
    """Test benchmarking with single iteration."""
    result = benchmark_execution(sample_module_file, "fast_function", '{"n": 5}', 1)

    assert result["iterations"] == 1
    assert result["stddev_time"] == 0.0  # No stddev with single iteration


def test_benchmark_execution_multiple_iterations(sample_module_file):
    """Test benchmarking with multiple iterations."""
    result = benchmark_execution(
        sample_module_file, "complex_function", '{"n": 20}', 50
    )

    assert result["iterations"] == 50
    assert result["stddev_time"] >= 0.0
    assert result["total_time"] > 0


def test_benchmark_execution_invalid_iterations(sample_module_file):
    """Test benchmarking with invalid iterations."""
    with pytest.raises(ValueError, match="at least 1"):
        benchmark_execution(sample_module_file, "fast_function", "{}", 0)


def test_benchmark_execution_type_errors(sample_module_file):
    """Test benchmarking with wrong types."""
    with pytest.raises(TypeError):
        benchmark_execution(123, "func", "{}", 10)

    with pytest.raises(TypeError):
        benchmark_execution(sample_module_file, 123, "{}", 10)

    with pytest.raises(TypeError):
        benchmark_execution(sample_module_file, "func", 123, 10)

    with pytest.raises(TypeError):
        benchmark_execution(sample_module_file, "func", "{}", "10")


def test_compare_implementations_basic(comparison_files):
    """Test basic implementation comparison."""
    file1, file2 = comparison_files
    test_data = "[5, 2, 8, 1, 9, 3, 7]"

    result = compare_implementations(
        file1,
        "bubble_sort",
        f'{{"data": {test_data}}}',
        file2,
        "quick_sort",
        f'{{"data": {test_data}}}',
        10,
    )

    assert "implementation1" in result
    assert "implementation2" in result
    assert "winner" in result
    assert "speedup_factor" in result
    assert "difference_ms" in result

    # Check implementation details
    assert result["implementation1"]["name"] == "bubble_sort"
    assert result["implementation2"]["name"] == "quick_sort"

    # Winner should be one of the two
    assert result["winner"] in ["bubble_sort", "quick_sort"]

    # Speedup should be positive
    assert result["speedup_factor"] > 0


def test_compare_implementations_clear_winner(comparison_files):
    """Test comparison with clear performance difference."""
    file1, file2 = comparison_files
    # Larger dataset makes difference more pronounced
    test_data = list(range(100, 0, -1))  # Worst case for bubble sort

    result = compare_implementations(
        file1,
        "bubble_sort",
        f'{{"data": {test_data}}}',
        file2,
        "quick_sort",
        f'{{"data": {test_data}}}',
        5,
    )

    # Quick sort should be significantly faster
    assert result["speedup_factor"] > 1.0
    assert result["difference_ms"] > 0


def test_compare_implementations_invalid_iterations(comparison_files):
    """Test comparison with invalid iterations."""
    file1, file2 = comparison_files

    with pytest.raises(ValueError, match="at least 1"):
        compare_implementations(
            file1,
            "bubble_sort",
            '{"data": [1,2,3]}',
            file2,
            "quick_sort",
            '{"data": [1,2,3]}',
            0,
        )


def test_compare_implementations_type_errors(comparison_files):
    """Test comparison with wrong types."""
    file1, file2 = comparison_files

    with pytest.raises(TypeError):
        compare_implementations(123, "func1", "{}", file2, "func2", "{}", 10)

    with pytest.raises(TypeError):
        compare_implementations(file1, 123, "{}", file2, "func2", "{}", 10)

    with pytest.raises(TypeError):
        compare_implementations(file1, "func1", 123, file2, "func2", "{}", 10)


def test_compare_implementations_missing_file(comparison_files):
    """Test comparison with missing file."""
    file1, _ = comparison_files

    with pytest.raises(FileNotFoundError):
        compare_implementations(
            file1,
            "bubble_sort",
            '{"data": [1]}',
            "/nonexistent/file.py",
            "func",
            '{"data": [1]}',
            5,
        )
