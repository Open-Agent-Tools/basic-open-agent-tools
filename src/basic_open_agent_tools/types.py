"""Common type definitions for basic-open-agent-tools."""

from pathlib import Path
from typing import Any, Union

PathLike = Union[str, Path]

DataDict = dict[str, Any]
NestedData = Union[dict[str, Any], list[Any], str, int, float, bool, None]
ValidationResult = dict[str, Any]
