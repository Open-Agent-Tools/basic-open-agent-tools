"""Profiling and performance analysis tools.

This module provides functions for profiling Python code performance, analyzing
memory usage, and benchmarking function execution.
"""

from basic_open_agent_tools.profiling.benchmarks import (
    benchmark_execution,
    compare_implementations,
)
from basic_open_agent_tools.profiling.memory import (
    detect_memory_leaks,
    get_memory_snapshot,
    measure_memory_usage,
)
from basic_open_agent_tools.profiling.performance import (
    get_hotspots,
    profile_function,
    profile_script,
)

__all__ = [
    # Performance profiling
    "profile_function",
    "profile_script",
    "get_hotspots",
    # Memory analysis
    "measure_memory_usage",
    "detect_memory_leaks",
    "get_memory_snapshot",
    # Benchmarking
    "benchmark_execution",
    "compare_implementations",
]
