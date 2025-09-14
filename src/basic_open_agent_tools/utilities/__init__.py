"""Utilities tools for AI agents.

This module provides essential utility functions for AI agents, including
timing controls, debugging helpers, and operational utilities. All functions use
simplified type signatures to prevent "signature too complex" errors when used
with AI agent frameworks.
"""

from .timing import sleep_seconds, sleep_milliseconds, precise_sleep
from .debugging import (
    inspect_function_signature, get_call_stack_info,
    format_exception_details, validate_function_call,
    trace_variable_changes
)

__all__ = [
    # Timing utilities
    "sleep_seconds", "sleep_milliseconds", "precise_sleep",
    # Debugging utilities
    "inspect_function_signature", "get_call_stack_info",
    "format_exception_details", "validate_function_call",
    "trace_variable_changes"
]
