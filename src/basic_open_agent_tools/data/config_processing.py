"""Configuration file processing tools for AI agents.

This module provides functions for reading, writing, and manipulating
configuration files in various formats (YAML, TOML, INI).

Note: Some functions require optional dependencies:
- YAML functions require PyYAML
- TOML functions require tomli (Python < 3.11) or tomllib (Python >= 3.11)
"""

import configparser
import os
import sys
from typing import Any, Dict, List, Optional

from ..exceptions import DataError

# Optional imports with graceful fallbacks
try:
    import yaml  # type: ignore[import-untyped]

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# For TOML, use stdlib tomllib if available (Python 3.11+), otherwise try tomli
if sys.version_info >= (3, 11):
    try:
        import tomllib

        TOML_AVAILABLE = True
    except ImportError:
        TOML_AVAILABLE = False
else:
    try:
        import tomli  # type: ignore[import-not-found]

        TOML_AVAILABLE = True
    except ImportError:
        TOML_AVAILABLE = False


def read_yaml_file(file_path: str) -> Dict[str, Any]:
    """Read a YAML configuration file.

    Args:
        file_path: Path to the YAML file

    Returns:
        Dictionary containing the parsed YAML data

    Raises:
        DataError: If PyYAML is not installed or the file cannot be read
        ValueError: If the YAML file is invalid

    Example:
        >>> # Requires PyYAML to be installed
        >>> config = read_yaml_file("config.yaml")
        >>> isinstance(config, dict)
        True
    """
    if not YAML_AVAILABLE:
        raise DataError(
            "PyYAML is required for YAML processing. "
            "Install it with: pip install pyyaml"
        )

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"YAML file not found: {file_path}")

    try:
        with open(file_path, encoding="utf-8") as file:
            return yaml.safe_load(file) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML file: {str(e)}")
    except Exception as e:
        raise DataError(f"Failed to read YAML file: {str(e)}")


def write_yaml_file(data: Dict[str, Any], file_path: str) -> None:
    """Write data to a YAML configuration file.

    Args:
        data: Dictionary containing the data to write
        file_path: Path where the YAML file will be written

    Raises:
        DataError: If PyYAML is not installed or the file cannot be written
        TypeError: If the data is not serializable to YAML

    Example:
        >>> # Requires PyYAML to be installed
        >>> data = {"server": {"host": "localhost", "port": 8080}}
        >>> write_yaml_file(data, "config.yaml")
    """
    if not YAML_AVAILABLE:
        raise DataError(
            "PyYAML is required for YAML processing. "
            "Install it with: pip install pyyaml"
        )

    try:
        with open(file_path, "w", encoding="utf-8") as file:
            yaml.dump(data, file, default_flow_style=False, sort_keys=False)
    except yaml.YAMLError as e:
        raise TypeError(f"Data is not YAML serializable: {str(e)}")
    except Exception as e:
        raise DataError(f"Failed to write YAML file: {str(e)}")


def read_toml_file(file_path: str) -> Dict[str, Any]:
    """Read a TOML configuration file.

    Args:
        file_path: Path to the TOML file

    Returns:
        Dictionary containing the parsed TOML data

    Raises:
        DataError: If tomli/tomllib is not installed or the file cannot be read
        ValueError: If the TOML file is invalid

    Example:
        >>> # Requires tomli or Python 3.11+ (tomllib)
        >>> config = read_toml_file("pyproject.toml")
        >>> isinstance(config, dict)
        True
    """
    if not TOML_AVAILABLE:
        raise DataError(
            "TOML support requires tomli (Python < 3.11) or tomllib (Python >= 3.11). "
            "Install tomli with: pip install tomli"
        )

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"TOML file not found: {file_path}")

    try:
        with open(file_path, "rb") as file:
            if sys.version_info >= (3, 11):
                return tomllib.load(file) or {}
            else:
                return tomli.load(file) or {}
    except ValueError as e:
        # Both tomli.TOMLDecodeError and tomllib.TOMLDecodeError inherit from ValueError
        raise ValueError(f"Invalid TOML file: {str(e)}")
    except Exception as e:
        raise DataError(f"Failed to read TOML file: {str(e)}")


def write_toml_file(data: Dict[str, Any], file_path: str) -> None:
    """Write data to a TOML configuration file.

    Args:
        data: Dictionary containing the data to write
        file_path: Path where the TOML file will be written

    Raises:
        DataError: If tomli_w is not installed or the file cannot be written
        TypeError: If the data is not serializable to TOML

    Example:
        >>> # Requires tomli_w to be installed
        >>> data = {"tool": {"name": "example", "version": "1.0.0"}}
        >>> write_toml_file(data, "config.toml")
    """
    try:
        import tomli_w  # type: ignore[import-not-found]
    except ImportError:
        raise DataError(
            "tomli_w is required for writing TOML files. "
            "Install it with: pip install tomli-w"
        )

    try:
        with open(file_path, "wb") as file:
            tomli_w.dump(data, file)
    except Exception as e:
        raise DataError(f"Failed to write TOML file: {str(e)}")


def read_ini_file(file_path: str) -> Dict[str, Dict[str, str]]:
    """Read an INI configuration file.

    Args:
        file_path: Path to the INI file

    Returns:
        Nested dictionary containing the parsed INI data, with sections as keys

    Raises:
        FileNotFoundError: If the file does not exist
        DataError: If the file cannot be read

    Example:
        >>> config = read_ini_file("config.ini")
        >>> "section_name" in config
        True
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"INI file not found: {file_path}")

    config = configparser.ConfigParser()

    try:
        config.read(file_path, encoding="utf-8")

        # Convert to dictionary
        result = {}
        for section in config.sections():
            result[section] = dict(config[section])

        return result
    except Exception as e:
        raise DataError(f"Failed to read INI file: {str(e)}")


def write_ini_file(data: Dict[str, Dict[str, str]], file_path: str) -> None:
    """Write data to an INI configuration file.

    Args:
        data: Nested dictionary with sections as keys and key-value pairs as values
        file_path: Path where the INI file will be written

    Raises:
        DataError: If the file cannot be written or the data format is invalid

    Example:
        >>> data = {
        ...     "server": {"host": "localhost", "port": "8080"},
        ...     "auth": {"enabled": "true", "timeout": "30"}
        ... }
        >>> write_ini_file(data, "config.ini")
    """
    config = configparser.ConfigParser()

    try:
        # Add sections and values
        for section, values in data.items():
            config[section] = {}
            for key, value in values.items():
                # ConfigParser requires string values
                config[section][key] = str(value)

        # Write to file
        with open(file_path, "w", encoding="utf-8") as file:
            config.write(file)
    except Exception as e:
        raise DataError(f"Failed to write INI file: {str(e)}")


def validate_config_schema(
    config_data: Dict[str, Any], schema: Dict[str, Any]
) -> List[str]:
    """Validate configuration data against a schema.

    This function performs basic validation of configuration data against a schema
    that specifies required fields, types, and allowed values.

    Args:
        config_data: The configuration data to validate
        schema: Schema definition with the following structure:
            {
                "field_name": {
                    "type": str/int/float/bool/list/dict,
                    "required": True/False,
                    "allowed_values": [list of allowed values] (optional)
                }
            }

    Returns:
        List of validation error messages (empty if validation passes)

    Example:
        >>> config = {"port": 8080, "debug": True}
        >>> schema = {
        ...     "port": {"type": int, "required": True},
        ...     "host": {"type": str, "required": False},
        ...     "debug": {"type": bool, "required": False}
        ... }
        >>> validate_config_schema(config, schema)
        []  # Empty list means validation passed
    """
    errors = []

    # Check for required fields and type validation
    for field_name, field_schema in schema.items():
        required = field_schema.get("required", False)
        expected_type = field_schema.get("type")
        allowed_values = field_schema.get("allowed_values")

        # Check if required field is present
        if required and field_name not in config_data:
            errors.append(f"Required field '{field_name}' is missing")
            continue

        # Skip validation for optional fields that are not present
        if field_name not in config_data:
            continue

        value = config_data[field_name]

        # Type validation
        if expected_type and not isinstance(value, expected_type):
            errors.append(
                f"Field '{field_name}' has incorrect type: expected {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )

        # Allowed values validation
        if allowed_values is not None and value not in allowed_values:
            errors.append(
                f"Field '{field_name}' has invalid value: {value}. "
                f"Allowed values: {allowed_values}"
            )

    # Check for unknown fields
    for field_name in config_data:
        if field_name not in schema:
            errors.append(f"Unknown field '{field_name}' not defined in schema")

    return errors


def merge_config_files(
    *config_paths: str, format_type: Optional[str] = None
) -> Dict[str, Any]:
    """Merge multiple configuration files into a single configuration.

    Later files in the list override values from earlier files.
    All files must be of the same format type.

    Args:
        *config_paths: Paths to the configuration files to merge
        format_type: Format of the config files ("yaml", "toml", "ini")
            If None, the format is determined from file extensions

    Returns:
        Merged configuration dictionary

    Raises:
        DataError: If files cannot be read or have different formats
        ValueError: If no config paths are provided

    Example:
        >>> # Merge default config with user config (YAML format)
        >>> merged = merge_config_files("default.yaml", "user.yaml")
    """
    if not config_paths:
        raise ValueError("At least one config file path must be provided")

    # Determine format from file extension if not specified
    if format_type is None:
        ext = os.path.splitext(config_paths[0])[1].lower()
        if ext in (".yaml", ".yml"):
            format_type = "yaml"
        elif ext == ".toml":
            format_type = "toml"
        elif ext == ".ini":
            format_type = "ini"
        else:
            raise DataError(f"Cannot determine config format from extension: {ext}")

    # Validate all files have the same format
    for path in config_paths:
        ext = os.path.splitext(path)[1].lower()
        if (
            format_type == "yaml"
            and ext not in (".yaml", ".yml")
            or format_type == "toml"
            and ext != ".toml"
            or format_type == "ini"
            and ext != ".ini"
        ):
            raise DataError(f"File {path} does not match format type {format_type}")

    # Read and merge configs
    merged_config: Dict[str, Any] = {}

    for path in config_paths:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Config file not found: {path}")

        # Read config based on format
        if format_type == "yaml":
            config = read_yaml_file(path)
        elif format_type == "toml":
            config = read_toml_file(path)
        elif format_type == "ini":
            config = read_ini_file(path)
        else:
            raise DataError(f"Unsupported config format: {format_type}")

        # Deep merge the configs
        merged_config = _deep_merge(merged_config, config)

    return merged_config


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries, with override values taking precedence.

    Args:
        base: Base dictionary
        override: Dictionary with values to override

    Returns:
        New merged dictionary
    """
    result = base.copy()

    for key, value in override.items():
        # If both values are dictionaries, merge them recursively
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            # Otherwise, override the value
            result[key] = value

    return result
