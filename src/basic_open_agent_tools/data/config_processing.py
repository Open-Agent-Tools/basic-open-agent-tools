"""Configuration file processing utilities for AI agents."""

import configparser
import json
from typing import Optional

from ..exceptions import DataError

# Simple YAML support using json fallback
try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Simple TOML support
try:
    import tomli
    import tomli_w

    HAS_TOML = True
except ImportError:
    HAS_TOML = False


def read_yaml_file(file_path: str) -> dict:
    """Read and parse a YAML configuration file.

    Args:
        file_path: Path to the YAML file

    Returns:
        Dictionary containing the YAML data

    Raises:
        DataError: If file cannot be read or parsed

    Example:
        >>> read_yaml_file("config.yaml")
        {"database": {"host": "localhost", "port": 5432}}
    """
    if not HAS_YAML:
        raise DataError("YAML support not available. Install PyYAML to use YAML files.")

    try:
        with open(file_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if data is not None else {}
    except FileNotFoundError:
        raise DataError(f"YAML file not found: {file_path}")
    except yaml.YAMLError as e:
        raise DataError(f"Failed to parse YAML file {file_path}: {e}")
    except Exception as e:
        raise DataError(f"Failed to read YAML file {file_path}: {e}")


def write_yaml_file(data: dict, file_path: str) -> None:
    """Write dictionary data to a YAML file.

    Args:
        data: Dictionary to write
        file_path: Path where YAML file will be created

    Raises:
        DataError: If file cannot be written

    Example:
        >>> data = {"database": {"host": "localhost", "port": 5432}}
        >>> write_yaml_file(data, "config.yaml")
    """
    if not HAS_YAML:
        raise DataError("YAML support not available. Install PyYAML to use YAML files.")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        raise DataError(f"Failed to write YAML file {file_path}: {e}")


def read_toml_file(file_path: str) -> dict:
    """Read and parse a TOML configuration file.

    Args:
        file_path: Path to the TOML file

    Returns:
        Dictionary containing the TOML data

    Raises:
        DataError: If file cannot be read or parsed

    Example:
        >>> read_toml_file("config.toml")
        {"database": {"host": "localhost", "port": 5432}}
    """
    if not HAS_TOML:
        raise DataError(
            "TOML support not available. Install tomli and tomli-w to use TOML files."
        )

    try:
        with open(file_path, "rb") as f:
            return tomli.load(f)
    except FileNotFoundError:
        raise DataError(f"TOML file not found: {file_path}")
    except tomli.TOMLDecodeError as e:
        raise DataError(f"Failed to parse TOML file {file_path}: {e}")
    except Exception as e:
        raise DataError(f"Failed to read TOML file {file_path}: {e}")


def write_toml_file(data: dict, file_path: str) -> None:
    """Write dictionary data to a TOML file.

    Args:
        data: Dictionary to write
        file_path: Path where TOML file will be created

    Raises:
        DataError: If file cannot be written

    Example:
        >>> data = {"database": {"host": "localhost", "port": 5432}}
        >>> write_toml_file(data, "config.toml")
    """
    if not HAS_TOML:
        raise DataError(
            "TOML support not available. Install tomli and tomli-w to use TOML files."
        )

    try:
        with open(file_path, "wb") as f:
            tomli_w.dump(data, f)
    except Exception as e:
        raise DataError(f"Failed to write TOML file {file_path}: {e}")


def read_ini_file(file_path: str) -> dict:
    """Read and parse an INI configuration file.

    Args:
        file_path: Path to the INI file

    Returns:
        Dictionary containing the INI data

    Raises:
        DataError: If file cannot be read or parsed

    Example:
        >>> read_ini_file("config.ini")
        {"database": {"host": "localhost", "port": "5432"}}
    """
    try:
        config = configparser.ConfigParser()
        config.read(file_path, encoding="utf-8")

        result = {}
        for section_name in config.sections():
            result[section_name] = dict(config[section_name])

        return result
    except FileNotFoundError:
        raise DataError(f"INI file not found: {file_path}")
    except configparser.Error as e:
        raise DataError(f"Failed to parse INI file {file_path}: {e}")
    except Exception as e:
        raise DataError(f"Failed to read INI file {file_path}: {e}")


def write_ini_file(data: dict, file_path: str) -> None:
    """Write dictionary data to an INI file.

    Args:
        data: Dictionary to write (nested dict representing sections)
        file_path: Path where INI file will be created

    Raises:
        DataError: If file cannot be written

    Example:
        >>> data = {"database": {"host": "localhost", "port": "5432"}}
        >>> write_ini_file(data, "config.ini")
    """
    try:
        config = configparser.ConfigParser()

        for section_name, section_data in data.items():
            config.add_section(section_name)
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    config.set(section_name, key, str(value))

        with open(file_path, "w", encoding="utf-8") as f:
            config.write(f)
    except Exception as e:
        raise DataError(f"Failed to write INI file {file_path}: {e}")


def validate_config_schema(config_data: dict, schema: dict) -> list:
    """Validate configuration data against a schema.

    Args:
        config_data: Configuration data to validate
        schema: Schema definition

    Returns:
        List of validation errors (empty if valid)

    Example:
        >>> config = {"host": "localhost", "port": 5432}
        >>> schema = {"required": ["host", "port"], "types": {"port": "int"}}
        >>> validate_config_schema(config, schema)
        []
    """
    errors = []

    # Check required fields
    required_fields = schema.get("required", [])
    for field in required_fields:
        if field not in config_data:
            errors.append(f"Required field '{field}' is missing")

    # Check data types (simplified)
    type_map = schema.get("types", {})
    type_mapping = {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "list": list,
        "dict": dict,
    }

    for field, expected_type_name in type_map.items():
        if field in config_data:
            value = config_data[field]
            expected_type = type_mapping.get(expected_type_name)
            if expected_type and not isinstance(value, expected_type):
                actual_type = type(value).__name__
                errors.append(
                    f"Field '{field}': expected {expected_type_name}, got {actual_type}"
                )

    return errors


def merge_config_files(config_paths: list, format_type: Optional[str] = None) -> dict:
    """Merge multiple configuration files into a single dictionary.

    Args:
        config_paths: List of paths to configuration files
        format_type: Format of the files ("yaml", "toml", "ini", or None for auto-detect)

    Returns:
        Merged configuration dictionary

    Raises:
        DataError: If files cannot be read or merged

    Example:
        >>> merge_config_files(["base.yaml", "override.yaml"], "yaml")
        {"database": {"host": "override-host", "port": 5432}}
    """
    if not config_paths:
        return {}

    merged_config = {}

    for config_path in config_paths:
        # Auto-detect format if not specified
        if format_type is None:
            if config_path.endswith((".yml", ".yaml")):
                file_format = "yaml"
            elif config_path.endswith(".toml"):
                file_format = "toml"
            elif config_path.endswith(".ini"):
                file_format = "ini"
            elif config_path.endswith(".json"):
                file_format = "json"
            else:
                raise DataError(f"Cannot determine format for file: {config_path}")
        else:
            file_format = format_type

        # Read the file
        if file_format == "yaml":
            config_data = read_yaml_file(config_path)
        elif file_format == "toml":
            config_data = read_toml_file(config_path)
        elif file_format == "ini":
            config_data = read_ini_file(config_path)
        elif file_format == "json":
            try:
                with open(config_path, encoding="utf-8") as f:
                    config_data = json.load(f)
            except Exception as e:
                raise DataError(f"Failed to read JSON file {config_path}: {e}")
        else:
            raise DataError(f"Unsupported format: {file_format}")

        # Deep merge the configuration
        merged_config = _deep_merge(merged_config, config_data)

    return merged_config


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dictionaries."""
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value

    return result
