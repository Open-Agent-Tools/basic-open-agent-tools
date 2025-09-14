"""Common type definitions for basic-open-agent-tools."""

from pathlib import Path
from typing import Any, Union

# Common type aliases currently in use
PathLike = Union[str, Path]

# Data-related type aliases
DataDict = dict[str, Any]
NestedData = Union[dict[str, Any], list[Any], str, int, float, bool, None]
ValidationResult = dict[str, Any]

# Additional types will be added as modules are implemented
