"""Centralized decorator definitions for agent framework integration.

This module provides decorators for integrating with AWS Strands Agents.

The decorator uses a graceful fallback pattern - if Strands is not installed,
the decorator becomes a no-op that simply returns the original function unchanged.
This allows the toolkit to work with or without Strands installed.
"""

from typing import Any, Callable

# AWS Strands decorator with graceful fallback
try:
    from strands import tool as strands_tool
except ImportError:
    # Create a no-op decorator if strands is not installed
    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        """No-op decorator when Strands is not available."""
        return func


__all__: list[str] = ["strands_tool"]
