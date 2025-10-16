"""Timing and execution control tools for AI agents.

Provides timing utilities and execution control functions with agent-friendly signatures.
"""

import signal
import time
from typing import Any, Union

from ..decorators import strands_tool
from ..exceptions import BasicAgentToolsError


@strands_tool
def sleep_seconds(seconds: float) -> dict[str, Union[str, float]]:
    """Pause execution for the specified number of seconds.

    This function provides a controlled sleep mechanism that can be interrupted
    with Ctrl+C (SIGINT) and provides feedback about the sleep operation.

    Args:
        seconds: Number of seconds to sleep (can be fractional)

    Returns:
        Dictionary containing:
        - status: "completed" or "interrupted"
        - requested_seconds: The requested sleep duration
        - actual_seconds: The actual time slept (if interrupted)
        - message: Human-readable status message

    Raises:
        BasicAgentToolsError: If seconds is negative or invalid

    Example:
        >>> result = sleep_seconds(2.5)
        >>> print(result["status"])
        completed
        >>> print(result["actual_seconds"])
        2.5
    """
    if not isinstance(seconds, (int, float)):
        raise BasicAgentToolsError("Seconds must be a number (int or float)")

    if seconds < 0:
        raise BasicAgentToolsError("Seconds cannot be negative")

    if seconds > 3600:  # 1 hour maximum
        raise BasicAgentToolsError("Maximum sleep duration is 3600 seconds (1 hour)")

    start_time = time.time()
    interrupted = False

    def signal_handler(signum: int, frame: Any) -> None:
        nonlocal interrupted
        interrupted = True

    # Set up signal handler for graceful interruption
    original_handler = None
    if hasattr(signal, "SIGINT"):
        try:
            original_handler = signal.signal(signal.SIGINT, signal_handler)
        except (ValueError, OSError):
            # Signal handling might not be available in all environments
            pass

    try:
        time.sleep(seconds)
    except KeyboardInterrupt:
        interrupted = True

    # Restore original signal handler
    if original_handler is not None:
        try:
            signal.signal(signal.SIGINT, original_handler)
        except (ValueError, OSError):
            pass

    actual_seconds = time.time() - start_time

    if interrupted:
        return {
            "status": "interrupted",
            "requested_seconds": float(seconds),
            "actual_seconds": round(actual_seconds, 3),
            "message": f"Sleep interrupted after {actual_seconds:.3f} seconds (requested {seconds} seconds)",
        }
    else:
        return {
            "status": "completed",
            "requested_seconds": float(seconds),
            "actual_seconds": round(actual_seconds, 3),
            "message": f"Successfully slept for {actual_seconds:.3f} seconds",
        }


@strands_tool
def sleep_milliseconds(milliseconds: float) -> dict[str, Union[str, float]]:
    """Pause execution for the specified number of milliseconds.

    Convenience function for shorter sleep durations.

    Args:
        milliseconds: Number of milliseconds to sleep

    Returns:
        Dictionary with sleep operation results (same as sleep_seconds)

    Raises:
        BasicAgentToolsError: If milliseconds is negative or invalid

    Example:
        >>> result = sleep_milliseconds(500)  # Sleep for 0.5 seconds
        >>> print(result["status"])
        completed
    """
    if not isinstance(milliseconds, (int, float)):
        raise BasicAgentToolsError("Milliseconds must be a number (int or float)")

    if milliseconds < 0:
        raise BasicAgentToolsError("Milliseconds cannot be negative")

    seconds = milliseconds / 1000.0
    result: dict[str, Union[str, float]] = sleep_seconds(seconds)

    # Update the result to reflect milliseconds
    result["requested_milliseconds"] = float(milliseconds)
    result["actual_milliseconds"] = round(float(result["actual_seconds"]) * 1000, 1)

    return result


@strands_tool
def precise_sleep(seconds: float) -> dict[str, Union[str, float]]:
    """Perform a high-precision sleep using busy-waiting for the final portion.

    This function combines time.sleep() with busy-waiting to achieve more precise
    timing, useful for timing-critical applications. Uses sleep() for most of the
    duration and busy-waiting for the final 10ms.

    Args:
        seconds: Number of seconds to sleep precisely

    Returns:
        Dictionary with precise sleep operation results

    Raises:
        BasicAgentToolsError: If seconds is negative or too large

    Example:
        >>> result = precise_sleep(0.001)  # 1ms precise sleep
        >>> print(result["status"])
        completed
    """
    if not isinstance(seconds, (int, float)):
        raise BasicAgentToolsError("Seconds must be a number (int or float)")

    if seconds < 0:
        raise BasicAgentToolsError("Seconds cannot be negative")

    if seconds > 60:  # 1 minute maximum for precise sleep
        raise BasicAgentToolsError("Maximum precise sleep duration is 60 seconds")

    start_time = time.time()

    # Use regular sleep for most of the duration
    if seconds > 0.01:  # 10ms threshold
        coarse_sleep = seconds - 0.01
        time.sleep(coarse_sleep)

    # Use busy-waiting for the final precise portion
    target_time = start_time + seconds
    while time.time() < target_time:
        pass

    actual_seconds = time.time() - start_time

    return {
        "status": "completed",
        "requested_seconds": float(seconds),
        "actual_seconds": round(actual_seconds, 6),
        "precision": "high",
        "message": f"Precise sleep completed in {actual_seconds:.6f} seconds (requested {seconds} seconds)",
    }
