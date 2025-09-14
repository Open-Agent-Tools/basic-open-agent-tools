"""Utilities tools for AI agents.

This module provides essential utility functions for AI agents, including
timing controls, debugging helpers, and operational utilities. All functions use
simplified type signatures to prevent "signature too complex" errors when used
with AI agent frameworks.
"""

from .timing import sleep_seconds

__all__ = ["sleep_seconds"]