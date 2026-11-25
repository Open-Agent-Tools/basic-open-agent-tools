"""Centralized decorator definitions for agent framework integration.

This module provides decorators for integrating with AWS Strands Agents.

If Strands is not installed, the decorator returns the original function unchanged.
"""

from typing import Any, Callable

try:
    from strands import tool as strands_tool
except ImportError:

    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        """No-op decorator when Strands is not available."""
        return func


__all__: list[str] = ["strands_tool"]
