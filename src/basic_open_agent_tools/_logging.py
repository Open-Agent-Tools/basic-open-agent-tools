"""Internal logging utility for basic-open-agent-tools.

This module provides a centralized logging configuration for all toolkit modules.
It respects the BOAT_LOG_LEVEL environment variable and uses TTY-aware defaults
to provide appropriate output for interactive and automated environments.

Environment Variables:
    BOAT_LOG_LEVEL: Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                    If not set, defaults based on TTY:
                    - TTY (interactive terminal): INFO (show execution messages)
                    - Non-TTY (agents/automation): WARNING (silent operation)

Example:
    >>> import os
    >>> os.environ['BOAT_LOG_LEVEL'] = 'DEBUG'
    >>> logger = get_logger('my_module')
    >>> logger.debug('Debug message')
    [my_module] Debug message
"""

import logging
import os
import sys
from typing import Optional

# Global flag to track if logging has been configured
_logging_configured = False


def _configure_logging() -> None:
    """Configure root logger with consistent format and TTY-aware level.

    This function is called automatically when getting the first logger.
    It sets up the root logger with a format matching the existing
    [MODULE] message pattern used throughout the codebase.

    Log level is determined by:
    1. BOAT_LOG_LEVEL environment variable (if set) - explicit override
    2. TTY detection (if env var not set):
       - TTY (interactive): INFO level (show execution messages)
       - Non-TTY (agents): WARNING level (silent operation)
    """
    global _logging_configured

    if _logging_configured:
        return

    # Get log level from environment variable, or use TTY-aware default
    log_level_str = os.environ.get("BOAT_LOG_LEVEL", None)

    if log_level_str is None:
        # No explicit log level set - use TTY-aware default
        if sys.stdout.isatty():
            # Interactive terminal - show execution messages
            log_level_str = "INFO"
        else:
            # Agent/automation - silent operation
            log_level_str = "WARNING"
    else:
        log_level_str = log_level_str.upper()

    # Map string to logging level
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    log_level = level_map.get(log_level_str, logging.WARNING)

    # Configure root logger
    root_logger = logging.getLogger("basic_open_agent_tools")
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    # Create custom formatter that strips package prefix for cleaner output
    class ShortNameFormatter(logging.Formatter):
        """Formatter that displays only module names without package prefix."""

        def format(self, record: logging.LogRecord) -> str:
            # Strip 'basic_open_agent_tools.' prefix for cleaner display
            if record.name.startswith("basic_open_agent_tools."):
                record.name = record.name[len("basic_open_agent_tools.") :]
            return super().format(record)

    # Create formatter matching existing [MODULE] pattern
    formatter = ShortNameFormatter("[%(name)s] %(message)s")
    handler.setFormatter(formatter)

    # Add handler to root logger
    root_logger.addHandler(handler)

    # Prevent propagation to avoid duplicate messages
    root_logger.propagate = False

    _logging_configured = True


def get_logger(module_name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance for a specific module.

    This function returns a logger configured for the toolkit's internal use.
    The logger uses TTY-aware defaults:
    - Interactive terminals (TTY): INFO level by default
    - Agents/automation (non-TTY): WARNING level by default
    - BOAT_LOG_LEVEL environment variable can override defaults

    Args:
        module_name: Name of the module (e.g., 'file_system', 'network')
                    If None, returns the root toolkit logger.

    Returns:
        Configured logger instance

    Example:
        >>> logger = get_logger('file_system')
        >>> logger.info('Operation completed')
        [file_system] Operation completed
    """
    # Configure logging on first use
    _configure_logging()

    # Build logger name
    if module_name:
        logger_name = f"basic_open_agent_tools.{module_name}"
    else:
        logger_name = "basic_open_agent_tools"

    return logging.getLogger(logger_name)


# Convenience function for quick logging without getting logger first
def log_info(module_name: str, message: str) -> None:
    """Log an info message for a specific module.

    Args:
        module_name: Name of the module
        message: Message to log
    """
    get_logger(module_name).info(message)


def log_warning(module_name: str, message: str) -> None:
    """Log a warning message for a specific module.

    Args:
        module_name: Name of the module
        message: Message to log
    """
    get_logger(module_name).warning(message)


def log_error(module_name: str, message: str) -> None:
    """Log an error message for a specific module.

    Args:
        module_name: Name of the module
        message: Message to log
    """
    get_logger(module_name).error(message)


def log_debug(module_name: str, message: str) -> None:
    """Log a debug message for a specific module.

    Args:
        module_name: Name of the module
        message: Message to log
    """
    get_logger(module_name).debug(message)
