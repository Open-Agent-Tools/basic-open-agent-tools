"""Common type definitions for basic-open-agent-tools."""

from pathlib import Path
from typing import Any, Dict, List, Union

# Common type aliases currently in use
PathLike = Union[str, Path]

# Data-related type aliases
DataDict = Dict[str, Any]
NestedData = Union[Dict[str, Any], List[Any], str, int, float, bool, None]
ValidationResult = Dict[str, Any]

# Additional types will be added as modules are implemented
