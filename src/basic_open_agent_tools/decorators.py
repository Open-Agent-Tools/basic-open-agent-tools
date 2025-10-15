"""Centralized decorator definitions for agent framework integration.

This module provides decorators for integrating with multiple agent frameworks:
- Google ADK (Agent Development Kit)
- AWS Strands Agents

The decorators use graceful fallback patterns - if a framework is not installed,
the decorator becomes a no-op that simply returns the original function unchanged.
This allows the toolkit to work with or without any specific framework installed.
"""

from typing import Any, Callable

# Google ADK decorator with graceful fallback
try:
    from google.adk.tools import adk_tool
except ImportError:
    # Create a no-op decorator if google-adk is not installed
    def adk_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        """No-op decorator when Google ADK is not available."""
        return func


# AWS Strands decorator with graceful fallback
try:
    from strands import tool as strands_tool
except ImportError:
    # Create a no-op decorator if strands is not installed
    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        """No-op decorator when Strands is not available."""
        return func


__all__: list[str] = ["adk_tool", "strands_tool"]
