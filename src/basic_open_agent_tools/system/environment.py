"""Environment variable operations."""

import os
from typing import Optional, Union

from ..decorators import strands_tool
from ..exceptions import BasicAgentToolsError


@strands_tool
def get_env_var(variable_name: str) -> dict[str, Union[str, bool]]:
    """
    Get the value of an environment variable.

    Args:
        variable_name: Name of the environment variable

    Returns:
        Dictionary with variable information

    Raises:
        BasicAgentToolsError: If variable name is invalid
    """
    if not isinstance(variable_name, str) or not variable_name.strip():
        raise BasicAgentToolsError("Variable name must be a non-empty string")

    variable_name = variable_name.strip()

    try:
        value = os.environ.get(variable_name)

        return {
            "variable_name": variable_name,
            "value": value if value is not None else "",
            "exists": value is not None,
            "is_empty": value == "" if value is not None else True,
        }

    except Exception as e:
        raise BasicAgentToolsError(
            f"Failed to get environment variable '{variable_name}': {str(e)}"
        )


@strands_tool
def set_env_var(variable_name: str, value: str) -> dict[str, Union[str, bool]]:
    """
    Set an environment variable (for current process only).

    Args:
        variable_name: Name of the environment variable
        value: Value to set

    Returns:
        Dictionary with operation result

    Raises:
        BasicAgentToolsError: If variable name or value is invalid
    """
    if not isinstance(variable_name, str) or not variable_name.strip():
        raise BasicAgentToolsError("Variable name must be a non-empty string")

    if not isinstance(value, str):
        raise BasicAgentToolsError("Value must be a string")

    variable_name = variable_name.strip()

    try:
        # Store previous value if it exists
        previous_value = os.environ.get(variable_name)

        # Set the new value
        os.environ[variable_name] = value

        return {
            "variable_name": variable_name,
            "new_value": value,
            "previous_value": previous_value if previous_value is not None else "",
            "had_previous_value": previous_value is not None,
            "operation": "set",
            "success": True,
        }

    except Exception as e:
        raise BasicAgentToolsError(
            f"Failed to set environment variable '{variable_name}': {str(e)}"
        )


@strands_tool
def list_env_vars(
    filter_pattern: str, limit: int
) -> dict[str, Union[int, dict[str, str], str, Optional[str]]]:
    """
    List environment variables, optionally filtered by name pattern.

    Args:
        filter_pattern: Optional pattern to filter variable names (case-insensitive)
        limit: Maximum number of variables to return (1-200)

    Returns:
        Dictionary with environment variables

    Raises:
        BasicAgentToolsError: If parameters are invalid
    """
    if filter_pattern is not None and not isinstance(filter_pattern, str):
        raise BasicAgentToolsError("Filter pattern must be a string or None")

    if not isinstance(limit, int) or limit < 1 or limit > 200:
        raise BasicAgentToolsError("Limit must be an integer between 1 and 200")

    try:
        variables = {}
        filter_lower = filter_pattern.lower() if filter_pattern else None

        for name, value in os.environ.items():
            # Apply filter if provided
            if filter_lower and filter_lower not in name.lower():
                continue

            variables[name] = value

            # Stop if we hit the limit
            if len(variables) >= limit:
                break

        return {
            "total_found": len(variables),
            "filter_pattern": filter_pattern,
            "limit_applied": limit,
            "variables": variables,
        }

    except Exception as e:
        raise BasicAgentToolsError(f"Failed to list environment variables: {str(e)}")
