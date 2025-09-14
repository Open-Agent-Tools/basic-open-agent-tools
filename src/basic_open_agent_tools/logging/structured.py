"""Structured logging utilities."""

import json
import logging
import time
from typing import Any, Callable, Union

try:
    from strands import tool as strands_tool
except ImportError:

    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        return func


from ..exceptions import BasicAgentToolsError


@strands_tool
def log_info(
    message: str, logger_name: str = "agent", **kwargs
) -> dict[str, Union[str, float]]:
    """Log an info message with structured data."""
    if not isinstance(message, str):
        raise BasicAgentToolsError("Message must be a string")

    try:
        logger = logging.getLogger(logger_name)
        timestamp = time.time()

        log_entry = {
            "timestamp": timestamp,
            "level": "INFO",
            "message": message,
            **kwargs,
        }

        logger.info(json.dumps(log_entry))

        return {
            "level": "INFO",
            "message": message,
            "logger_name": logger_name,
            "timestamp": timestamp,
            "status": "logged",
        }
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to log info message: {str(e)}")


@strands_tool
def log_error(
    message: str, logger_name: str = "agent", **kwargs
) -> dict[str, Union[str, float]]:
    """Log an error message with structured data."""
    if not isinstance(message, str):
        raise BasicAgentToolsError("Message must be a string")

    try:
        logger = logging.getLogger(logger_name)
        timestamp = time.time()

        log_entry = {
            "timestamp": timestamp,
            "level": "ERROR",
            "message": message,
            **kwargs,
        }

        logger.error(json.dumps(log_entry))

        return {
            "level": "ERROR",
            "message": message,
            "logger_name": logger_name,
            "timestamp": timestamp,
            "status": "logged",
        }
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to log error message: {str(e)}")


@strands_tool
def configure_logger(
    logger_name: str, log_file: str, level: str = "INFO"
) -> dict[str, str]:
    """Configure a logger with file output."""
    if level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
        raise BasicAgentToolsError("Level must be DEBUG, INFO, WARNING, or ERROR")

    try:
        logger = logging.getLogger(logger_name)
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, level))

        return {
            "logger_name": logger_name,
            "log_file": log_file,
            "level": level,
            "status": "configured",
        }
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to configure logger: {str(e)}")
