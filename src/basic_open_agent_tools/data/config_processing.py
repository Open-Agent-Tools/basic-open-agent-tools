"""Configuration file processing utilities for AI agents."""

import configparser
import json
from typing import Any, Callable

try:
    from strands import tool as strands_tool
except ImportError:
    # Create a no-op decorator if strands is not installed
    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]  # type: ignore
        return func


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


@strands_tool
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
    print(f"[DATA] Reading YAML file: {file_path}")

    if not HAS_YAML:
        raise DataError("YAML support not available. Install PyYAML to use YAML files.")

    try:
        with open(file_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            result = data if data is not None else {}
            print(f"[DATA] YAML loaded: {len(result)} top-level keys")
            return result
    except FileNotFoundError:
        print(f"[DATA] YAML file not found: {file_path}")
        raise FileNotFoundError(f"YAML file not found: {file_path}")
    except yaml.YAMLError as e:
        print(f"[DATA] YAML parse error: {e}")
        raise ValueError(f"Failed to parse YAML file {file_path}: {e}")
    except Exception as e:
        print(f"[DATA] YAML read error: {e}")
        raise DataError(f"Failed to read YAML file {file_path}: {e}")


@strands_tool
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
    print(f"[DATA] Writing YAML file: {file_path} ({len(data)} top-level keys)")

    if not HAS_YAML:
        raise DataError("YAML support not available. Install PyYAML to use YAML files.")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)
        print(f"[DATA] YAML file written successfully: {file_path}")
    except Exception as e:
        raise DataError(f"Failed to write YAML file {file_path}: {e}")


@strands_tool
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
    print(f"[DATA] Reading TOML file: {file_path}")

    if not HAS_TOML:
        raise DataError(
            "TOML support not available. Install tomli and tomli-w to use TOML files."
        )

    try:
        with open(file_path, "rb") as f:
            result: dict = tomli.load(f)
            print(f"[DATA] TOML loaded: {len(result)} top-level keys")
            return result
    except FileNotFoundError:
        print(f"[DATA] TOML file not found: {file_path}")
        raise FileNotFoundError(f"TOML file not found: {file_path}")
    except tomli.TOMLDecodeError as e:
        print(f"[DATA] TOML parse error: {e}")
        raise ValueError(f"Failed to parse TOML file {file_path}: {e}")
    except Exception as e:
        print(f"[DATA] TOML read error: {e}")
        raise DataError(f"Failed to read TOML file {file_path}: {e}")


@strands_tool
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
    print(f"[DATA] Writing TOML file: {file_path} ({len(data)} top-level keys)")

    if not HAS_TOML:
        raise DataError(
            "TOML support not available. Install tomli and tomli-w to use TOML files."
        )

    try:
        with open(file_path, "wb") as f:
            tomli_w.dump(data, f)
        print(f"[DATA] TOML file written successfully: {file_path}")
    except Exception as e:
        print(f"[DATA] TOML write error: {e}")
        raise DataError(f"Failed to write TOML file {file_path}: {e}")


@strands_tool
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
    print(f"[DATA] Reading INI file: {file_path}")

    # Check if file exists first (ConfigParser.read doesn't raise FileNotFoundError)
    import os

    if not os.path.isfile(file_path):
        print(f"[DATA] INI file not found: {file_path}")
        raise FileNotFoundError(f"INI file not found: {file_path}")

    try:
        config = configparser.ConfigParser()
        config.read(file_path, encoding="utf-8")

        result = {}
        for section_name in config.sections():
            result[section_name] = dict(config[section_name])

        print(f"[DATA] INI loaded: {len(result)} sections")
        return result
    except FileNotFoundError:
        raise DataError(f"INI file not found: {file_path}")
    except configparser.Error as e:
        print(f"[DATA] INI parse error: {e}")
        raise DataError(f"Failed to parse INI file {file_path}: {e}")
    except Exception as e:
        print(f"[DATA] INI read error: {e}")
        raise DataError(f"Failed to read INI file {file_path}: {e}")


@strands_tool
def write_ini_file(data: dict, file_path: str, force: bool) -> str:
    """Write dictionary data to an INI file with permission checking.

    Args:
        data: Dictionary to write (nested dict representing sections)
        file_path: Path where INI file will be created
        force: If True, overwrite existing files without confirmation

    Returns:
        String describing the operation result

    Raises:
        DataError: If file cannot be written or exists without force

    Example:
        >>> data = {"database": {"host": "localhost", "port": "5432"}}
        >>> write_ini_file(data, "config.ini", force=True)
        "Created INI file config.ini with 1 sections (87 bytes)"
    """
    print(f"[DATA] Writing INI file: {file_path} ({len(data)} sections, force={force})")

    import os

    file_existed = os.path.exists(file_path)

    if file_existed and not force:
        print(f"[DATA] INI write blocked - file exists and force=False: {file_path}")
        raise DataError(
            f"INI file already exists: {file_path}. Use force=True to overwrite."
        )

    try:
        config = configparser.ConfigParser()
        section_count = 0

        for section_name, section_data in data.items():
            config.add_section(section_name)
            section_count += 1
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    config.set(section_name, key, str(value))

        with open(file_path, "w", encoding="utf-8") as f:
            config.write(f)

        # Calculate stats for feedback
        file_size = os.path.getsize(file_path)
        action = "Overwrote" if file_existed else "Created"

        result = f"{action} INI file {file_path} with {section_count} sections ({file_size} bytes)"
        print(f"[DATA] {result}")
        return result
    except Exception as e:
        print(f"[DATA] INI write error: {e}")
        raise DataError(f"Failed to write INI file {file_path}: {e}")


@strands_tool
def validate_config_schema(config_data: dict, schema_definition: dict) -> list:
    """Validate configuration data against a schema.

    Args:
        config_data: Configuration data to validate
        schema_definition: Schema definition with field specifications

    Returns:
        List of validation errors (empty if valid)

    Example:
        >>> config = {"host": "localhost", "port": 5432}
        >>> schema = {
        ...     "port": {"type": int, "required": True},
        ...     "host": {"type": str, "required": True}
        ... }
        >>> validate_config_schema(config, schema)
        []
    """
    errors = []

    # Check each field in the schema
    for field_name, field_spec in schema_definition.items():
        # Check if required field is present
        if field_spec.get("required", False) and field_name not in config_data:
            errors.append(f"Required field '{field_name}' is missing")
            continue

        # Skip validation if field is not in config data
        if field_name not in config_data:
            continue

        # Check type
        expected_type = field_spec.get("type")
        if expected_type and not isinstance(config_data[field_name], expected_type):
            actual_type = type(config_data[field_name]).__name__
            expected_type_name = expected_type.__name__
            errors.append(
                f"Field '{field_name}' has incorrect type: expected {expected_type_name}, got {actual_type}"
            )

        # Check allowed values
        allowed_values = field_spec.get("allowed_values")
        if allowed_values and config_data[field_name] not in allowed_values:
            errors.append(
                f"Field '{field_name}' has invalid value: {config_data[field_name]}. Allowed values: {allowed_values}"
            )

    # Check for unknown fields
    for field_name in config_data:
        if field_name not in schema_definition:
            errors.append(f"Unknown field '{field_name}' in configuration")

    return errors


@strands_tool
def merge_config_files(config_paths: list[str], format_type: str) -> dict:
    """Merge multiple configuration files into a single dictionary.

    Args:
        config_paths: List of paths to configuration files
        format_type: Format of the files ("yaml", "toml", "ini", or "json")

    Returns:
        Merged configuration dictionary

    Raises:
        ValueError: If no config paths are provided
        DataError: If files cannot be read or merged

    Example:
        >>> merge_config_files(["base.yaml", "override.yaml"], "yaml")
        {"database": {"host": "override-host", "port": 5432}}
        >>> merge_config_files(["single.yaml"], "yaml")
        {"database": {"host": "localhost", "port": 5432}}
    """
    # Use the provided list directly
    paths = config_paths

    if not paths:
        raise ValueError("No configuration files provided")

    # Validate format_type
    valid_formats = ["yaml", "toml", "ini", "json"]
    if format_type not in valid_formats:
        raise ValueError(f"format_type must be one of {valid_formats}")

    merged_config: dict = {}

    for config_path in paths:
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
