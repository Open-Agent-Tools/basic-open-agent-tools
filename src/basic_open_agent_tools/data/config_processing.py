"""Configuration file processing utilities for AI agents."""

import configparser
import json
from typing import Any

from .._logging import get_logger
from ..confirmation import check_user_confirmation
from ..decorators import strands_tool
from ..exceptions import DataError

# Simple YAML support using json fallback
try:
    import yaml  # type: ignore[import-untyped]

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Simple TOML support
try:
    import tomli  # type: ignore[import-not-found]
    import tomli_w  # type: ignore[import-not-found]

    HAS_TOML = True
except ImportError:
    HAS_TOML = False


logger = get_logger("data.config_processing")


def _generate_dict_preview(data: dict, format_name: str) -> str:
    """Generate a preview of dictionary data for confirmation prompts.

    Args:
        data: The dictionary data to preview
        format_name: Name of the format (YAML, TOML, INI, etc.)

    Returns:
        Formatted preview string with key count and sample entries
    """
    if not data:
        return f"Writing empty {format_name} file (0 keys)"

    key_count = len(data)
    preview = f"Writing {key_count} top-level key(s)\n"

    # Show first 10 keys and their values (truncated)
    sample_keys = min(10, len(data))
    if sample_keys > 0:
        preview += f"\nFirst {sample_keys} key(s):\n"
        for i, (key, value) in enumerate(list(data.items())[:sample_keys]):
            value_repr = repr(value)
            if len(value_repr) > 80:
                value_repr = value_repr[:77] + "..."
            preview += f"  {i + 1}. {key}: {value_repr}\n"

    return preview.strip()


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
    if not HAS_YAML:
        raise DataError("YAML support not available. Install PyYAML to use YAML files.")

    logger.info(f"Reading YAML: {file_path}")

    try:
        with open(file_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            result = data if data is not None else {}
            logger.info(f"YAML loaded successfully: {len(result)} top-level keys")
            logger.debug(f"Keys: {list(result.keys())[:5]}")
            return result
    except FileNotFoundError:
        logger.debug(f"YAML file not found: {file_path}")
        raise FileNotFoundError(f"YAML file not found: {file_path}")
    except yaml.YAMLError as e:
        logger.error(f"YAML parse error: {e}")
        raise ValueError(f"Failed to parse YAML file {file_path}: {e}")
    except Exception as e:
        logger.error(f"YAML read error: {e}")
        raise DataError(f"Failed to read YAML file {file_path}: {e}")


@strands_tool
def write_yaml_file(data: dict, file_path: str, skip_confirm: bool) -> str:
    """Write dictionary data to a YAML file with permission checking.

    Args:
        data: Dictionary to write
        file_path: Path where YAML file will be created
        skip_confirm: If True, skip confirmation and overwrite existing files. IMPORTANT: Agents should default to skip_confirm=False for safety.

    Returns:
        String describing the operation result

    Raises:
        DataError: If file cannot be written or exists without skip_confirm

    Example:
        >>> data = {"database": {"host": "localhost", "port": 5432}}
        >>> write_yaml_file(data, "config.yaml", skip_confirm=True)
        "Created YAML file config.yaml with 1 top-level keys (87 bytes)"
    """
    if not HAS_YAML:
        raise DataError("YAML support not available. Install PyYAML to use YAML files.")

    import os

    file_existed = os.path.exists(file_path)

    logger.info(f"Writing YAML: {file_path} ({len(data)} top-level keys)")
    logger.debug(f"File exists: {file_existed}, skip_confirm: {skip_confirm}")

    if file_existed:
        # Check user confirmation - show preview of NEW data being written
        preview = _generate_dict_preview(data, "YAML")
        confirmed, decline_reason = check_user_confirmation(
            operation="overwrite existing YAML file",
            target=file_path,
            skip_confirm=skip_confirm,
            preview_info=preview,
        )

        if not confirmed:
            reason_msg = f" (reason: {decline_reason})" if decline_reason else ""
            logger.debug(f"YAML write cancelled by user: {file_path}{reason_msg}")
            return f"Operation cancelled by user{reason_msg}: {file_path}"

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)

        # Calculate stats for feedback
        file_size = os.path.getsize(file_path)
        key_count = len(data)
        action = "Overwrote" if file_existed else "Created"

        result = f"{action} YAML file {file_path} with {key_count} top-level keys ({file_size} bytes)"
        logger.info(
            f"YAML written successfully: {key_count} keys, {file_size} bytes ({action.lower()})"
        )
        return result
    except Exception as e:
        logger.error(f"YAML write error: {e}")
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
    if not HAS_TOML:
        raise DataError(
            "TOML support not available. Install tomli and tomli-w to use TOML files."
        )

    logger.info(f"Reading TOML: {file_path}")

    try:
        with open(file_path, "rb") as f:
            result: dict = tomli.load(f)
            logger.info(f"TOML loaded successfully: {len(result)} top-level keys")
            logger.debug(f"Keys: {list(result.keys())[:5]}")
            return result
    except FileNotFoundError:
        logger.debug(f"TOML file not found: {file_path}")
        raise FileNotFoundError(f"TOML file not found: {file_path}")
    except tomli.TOMLDecodeError as e:
        logger.error(f"TOML parse error: {e}")
        raise ValueError(f"Failed to parse TOML file {file_path}: {e}")
    except Exception as e:
        logger.error(f"TOML read error: {e}")
        raise DataError(f"Failed to read TOML file {file_path}: {e}")


@strands_tool
def write_toml_file(data: dict, file_path: str, skip_confirm: bool) -> str:
    """Write dictionary data to a TOML file with permission checking.

    Args:
        data: Dictionary to write
        file_path: Path where TOML file will be created
        skip_confirm: If True, skip confirmation and overwrite existing files. IMPORTANT: Agents should default to skip_confirm=False for safety.

    Returns:
        String describing the operation result

    Raises:
        DataError: If file cannot be written or exists without skip_confirm

    Example:
        >>> data = {"database": {"host": "localhost", "port": 5432}}
        >>> write_toml_file(data, "config.toml", skip_confirm=True)
        "Created TOML file config.toml with 1 top-level keys (87 bytes)"
    """
    if not HAS_TOML:
        raise DataError(
            "TOML support not available. Install tomli and tomli-w to use TOML files."
        )

    import os

    file_existed = os.path.exists(file_path)

    logger.info(f"Writing TOML: {file_path} ({len(data)} top-level keys)")
    logger.debug(f"File exists: {file_existed}, skip_confirm: {skip_confirm}")

    if file_existed:
        # Check user confirmation - show preview of NEW data being written
        preview = _generate_dict_preview(data, "TOML")
        confirmed, decline_reason = check_user_confirmation(
            operation="overwrite existing TOML file",
            target=file_path,
            skip_confirm=skip_confirm,
            preview_info=preview,
        )

        if not confirmed:
            reason_msg = f" (reason: {decline_reason})" if decline_reason else ""
            logger.debug(f"TOML write cancelled by user: {file_path}{reason_msg}")
            return f"Operation cancelled by user{reason_msg}: {file_path}"

    try:
        with open(file_path, "wb") as f:
            tomli_w.dump(data, f)

        # Calculate stats for feedback
        file_size = os.path.getsize(file_path)
        key_count = len(data)
        action = "Overwrote" if file_existed else "Created"

        result = f"{action} TOML file {file_path} with {key_count} top-level keys ({file_size} bytes)"
        logger.info(
            f"TOML written successfully: {key_count} keys, {file_size} bytes ({action.lower()})"
        )
        return result
    except Exception as e:
        logger.error(f"TOML write error: {e}")
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
    # Check if file exists first (ConfigParser.read doesn't raise FileNotFoundError)
    import os

    if not os.path.isfile(file_path):
        logger.debug(f"INI file not found: {file_path}")
        raise FileNotFoundError(f"INI file not found: {file_path}")

    logger.info(f"Reading INI: {file_path}")

    try:
        config = configparser.ConfigParser()
        config.read(file_path, encoding="utf-8")

        result = {}
        for section_name in config.sections():
            result[section_name] = dict(config[section_name])

        logger.info(f"INI loaded successfully: {len(result)} sections")
        logger.debug(f"Sections: {list(result.keys())[:5]}")
        return result
    except FileNotFoundError:
        raise DataError(f"INI file not found: {file_path}")
    except configparser.Error as e:
        logger.error(f"INI parse error: {e}")
        raise DataError(f"Failed to parse INI file {file_path}: {e}")
    except Exception as e:
        logger.error(f"INI read error: {e}")
        raise DataError(f"Failed to read INI file {file_path}: {e}")


@strands_tool
def write_ini_file(data: dict, file_path: str, skip_confirm: bool) -> str:
    """Write dictionary data to an INI file with permission checking.

    Args:
        data: Dictionary to write (nested dict representing sections)
        file_path: Path where INI file will be created
        skip_confirm: If True, skip confirmation and overwrite existing files. IMPORTANT: Agents should default to skip_confirm=False for safety.

    Returns:
        String describing the operation result

    Raises:
        DataError: If file cannot be written or exists without skip_confirm

    Example:
        >>> data = {"database": {"host": "localhost", "port": "5432"}}
        >>> write_ini_file(data, "config.ini", skip_confirm=True)
        "Created INI file config.ini with 1 sections (87 bytes)"
    """
    import os

    file_existed = os.path.exists(file_path)

    logger.info(f"Writing INI: {file_path} ({len(data)} sections)")
    logger.debug(f"File exists: {file_existed}, skip_confirm: {skip_confirm}")

    if file_existed:
        # Check user confirmation - show preview of NEW data being written
        preview = _generate_dict_preview(data, "INI")
        confirmed, decline_reason = check_user_confirmation(
            operation="overwrite existing INI file",
            target=file_path,
            skip_confirm=skip_confirm,
            preview_info=preview,
        )

        if not confirmed:
            reason_msg = f" (reason: {decline_reason})" if decline_reason else ""
            logger.debug(f"INI write cancelled by user: {file_path}{reason_msg}")
            return f"Operation cancelled by user{reason_msg}: {file_path}"

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
        logger.info(
            f"INI written successfully: {section_count} sections, {file_size} bytes ({action.lower()})"
        )
        return result
    except Exception as e:
        logger.error(f"INI write error: {e}")
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


# ===== Token-Saving Config Inspection Tools =====


def _get_value_at_path(data: dict, path: str) -> tuple[bool, Any]:
    """Helper to navigate nested dict using dot notation.

    Args:
        data: Dictionary to navigate
        path: Dot-separated path (e.g., "database.host")

    Returns:
        Tuple of (found, value)
    """
    keys = path.split(".")
    current = data

    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return False, None
        current = current[key]

    return True, current


def _get_all_paths(data: dict, prefix: str = "") -> list[str]:
    """Helper to get all dot-notation paths in nested dict.

    Args:
        data: Dictionary to traverse
        prefix: Current path prefix

    Returns:
        List of all paths
    """
    paths = []

    for key, value in data.items():
        current_path = f"{prefix}.{key}" if prefix else key
        paths.append(current_path)

        if isinstance(value, dict):
            paths.extend(_get_all_paths(value, current_path))

    return paths


def _get_structure(data: Any, max_depth: int = -1, current_depth: int = 0) -> Any:
    """Helper to get structure without values.

    Args:
        data: Dictionary to analyze
        max_depth: Maximum depth to traverse (-1 for unlimited)
        current_depth: Current recursion depth

    Returns:
        Structure dict with types instead of values, or type name string
    """
    if not isinstance(data, dict):
        return type(data).__name__

    if max_depth != -1 and current_depth >= max_depth:
        return "dict"

    structure: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            structure[key] = _get_structure(value, max_depth, current_depth + 1)
        elif isinstance(value, list):
            if value and isinstance(value[0], dict):
                structure[key] = [
                    _get_structure(value[0], max_depth, current_depth + 1)
                ]
            else:
                structure[key] = "list"
        else:
            structure[key] = type(value).__name__

    return structure


@strands_tool
def get_config_keys(file_path: str, format_type: str, path: str) -> list[str]:
    """Get list of keys at specific path in config file without loading values.

    Works with YAML, TOML, and INI configuration files. Returns only the key
    names at the specified path level, not the actual values.

    Args:
        file_path: Path to config file
        format_type: Format of file ("yaml", "toml", or "ini")
        path: Dot-separated path to location (empty string for root level)

    Returns:
        List of key names at the specified path

    Raises:
        ValueError: If format_type is invalid or path not found
        FileNotFoundError: If file doesn't exist
        DataError: If file cannot be parsed

    Example:
        >>> get_config_keys("config.yaml", "yaml", "database")
        ["host", "port", "username", "password"]
        >>> get_config_keys("config.toml", "toml", "")
        ["database", "logging", "features"]
    """
    if format_type not in ["yaml", "toml", "ini"]:
        raise ValueError(
            f"format_type must be 'yaml', 'toml', or 'ini', got: {format_type}"
        )

    logger.info(f"Getting config keys: {file_path} at path '{path}'")

    # Load the appropriate config file
    if format_type == "yaml":
        data = read_yaml_file(file_path)
    elif format_type == "toml":
        data = read_toml_file(file_path)
    else:  # ini
        data = read_ini_file(file_path)

    # Navigate to the specified path
    if path:
        found, target = _get_value_at_path(data, path)
        if not found:
            raise ValueError(f"Path not found in config: {path}")
        if not isinstance(target, dict):
            raise ValueError(f"Path does not point to a dictionary: {path}")
        data = target

    keys = list(data.keys())
    logger.info(f"Found {len(keys)} keys at path '{path}'")
    return keys


@strands_tool
def get_config_value_at_path(file_path: str, format_type: str, path: str) -> str:
    """Get specific value from config file using dot notation path.

    Loads the config file and extracts only the value at the specified path.
    More efficient than loading entire config when you need a single value.

    Args:
        file_path: Path to config file
        format_type: Format of file ("yaml", "toml", or "ini")
        path: Dot-separated path to value (e.g., "database.host")

    Returns:
        String representation of the value at path

    Raises:
        ValueError: If format_type is invalid or path not found
        FileNotFoundError: If file doesn't exist
        DataError: If file cannot be parsed

    Example:
        >>> get_config_value_at_path("config.yaml", "yaml", "database.host")
        "localhost"
        >>> get_config_value_at_path("config.toml", "toml", "database.port")
        "5432"
    """
    if format_type not in ["yaml", "toml", "ini"]:
        raise ValueError(
            f"format_type must be 'yaml', 'toml', or 'ini', got: {format_type}"
        )

    if not path:
        raise ValueError("path cannot be empty")

    logger.info(f"Getting config value: {file_path} at path '{path}'")

    # Load the appropriate config file
    if format_type == "yaml":
        data = read_yaml_file(file_path)
    elif format_type == "toml":
        data = read_toml_file(file_path)
    else:  # ini
        data = read_ini_file(file_path)

    # Navigate to the value
    found, value = _get_value_at_path(data, path)
    if not found:
        raise ValueError(f"Path not found in config: {path}")

    logger.info(f"Found value at path '{path}': {type(value).__name__}")
    return str(value)


@strands_tool
def get_config_structure(file_path: str, format_type: str, max_depth: int) -> Any:
    """Get hierarchical structure overview of config file without values.

    Returns the schema/structure showing keys and types at each level, but not
    the actual values. Useful for understanding config file organization without
    loading all data.

    Args:
        file_path: Path to config file
        format_type: Format of file ("yaml", "toml", or "ini")
        max_depth: Maximum depth to traverse (-1 for unlimited)

    Returns:
        Dictionary showing structure with type names instead of values

    Raises:
        ValueError: If format_type is invalid
        FileNotFoundError: If file doesn't exist
        DataError: If file cannot be parsed

    Example:
        >>> get_config_structure("config.yaml", "yaml", 2)
        {
            "database": {
                "host": "str",
                "port": "int",
                "credentials": "dict"
            },
            "logging": {
                "level": "str",
                "handlers": "list"
            }
        }
    """
    if format_type not in ["yaml", "toml", "ini"]:
        raise ValueError(
            f"format_type must be 'yaml', 'toml', or 'ini', got: {format_type}"
        )

    logger.info(f"Getting config structure: {file_path} (max_depth={max_depth})")

    # Load the appropriate config file
    if format_type == "yaml":
        data = read_yaml_file(file_path)
    elif format_type == "toml":
        data = read_toml_file(file_path)
    else:  # ini
        data = read_ini_file(file_path)

    structure = _get_structure(data, max_depth)
    logger.info(
        f"Generated structure with {len(structure) if isinstance(structure, dict) else 0} top-level keys"
    )
    return structure


@strands_tool
def search_config_keys(
    file_path: str, format_type: str, search_pattern: str
) -> list[str]:
    """Find all paths in config file containing keys matching pattern.

    Searches through entire config hierarchy and returns dot-notation paths
    to all keys that match the search pattern (case-insensitive substring match).

    Args:
        file_path: Path to config file
        format_type: Format of file ("yaml", "toml", or "ini")
        search_pattern: Text pattern to search for in key names

    Returns:
        List of dot-notation paths to matching keys

    Raises:
        ValueError: If format_type is invalid
        FileNotFoundError: If file doesn't exist
        DataError: If file cannot be parsed

    Example:
        >>> search_config_keys("config.yaml", "yaml", "host")
        ["database.host", "cache.redis_host", "api.webhook_host"]
        >>> search_config_keys("config.toml", "toml", "port")
        ["database.port", "server.port", "monitoring.metrics_port"]
    """
    if format_type not in ["yaml", "toml", "ini"]:
        raise ValueError(
            f"format_type must be 'yaml', 'toml', or 'ini', got: {format_type}"
        )

    logger.info(f"Searching config keys: {file_path} for pattern '{search_pattern}'")

    # Load the appropriate config file
    if format_type == "yaml":
        data = read_yaml_file(file_path)
    elif format_type == "toml":
        data = read_toml_file(file_path)
    else:  # ini
        data = read_ini_file(file_path)

    # Get all paths and filter by pattern
    all_paths = _get_all_paths(data)
    pattern_lower = search_pattern.lower()

    matching_paths = [
        path for path in all_paths if pattern_lower in path.split(".")[-1].lower()
    ]

    logger.info(f"Found {len(matching_paths)} paths matching '{search_pattern}'")
    return matching_paths


@strands_tool
def count_config_items(file_path: str, format_type: str, path: str) -> int:
    """Count number of keys/items at specific path in config file.

    Returns count of direct child keys at the specified path level without
    loading or counting nested items.

    Args:
        file_path: Path to config file
        format_type: Format of file ("yaml", "toml", or "ini")
        path: Dot-separated path to location (empty string for root level)

    Returns:
        Count of keys at the specified path

    Raises:
        ValueError: If format_type is invalid or path not found
        FileNotFoundError: If file doesn't exist
        DataError: If file cannot be parsed

    Example:
        >>> count_config_items("config.yaml", "yaml", "database")
        4
        >>> count_config_items("config.toml", "toml", "")
        3
    """
    if format_type not in ["yaml", "toml", "ini"]:
        raise ValueError(
            f"format_type must be 'yaml', 'toml', or 'ini', got: {format_type}"
        )

    logger.info(f"Counting config items: {file_path} at path '{path}'")

    # Load the appropriate config file
    if format_type == "yaml":
        data = read_yaml_file(file_path)
    elif format_type == "toml":
        data = read_toml_file(file_path)
    else:  # ini
        data = read_ini_file(file_path)

    # Navigate to the specified path
    if path:
        found, target = _get_value_at_path(data, path)
        if not found:
            raise ValueError(f"Path not found in config: {path}")
        if not isinstance(target, dict):
            raise ValueError(f"Path does not point to a dictionary: {path}")
        data = target

    count = len(data)
    logger.info(f"Found {count} items at path '{path}'")
    return count


@strands_tool
def select_config_keys(file_path: str, format_type: str, key_paths: list[str]) -> dict:
    """Extract only specific keys from config file by their paths.

    Loads config and returns a new dictionary containing only the specified
    key paths. Useful for extracting a subset of configuration values.

    Args:
        file_path: Path to config file
        format_type: Format of file ("yaml", "toml", or "ini")
        key_paths: List of dot-notation paths to extract

    Returns:
        Dictionary with only the selected keys (preserves structure)

    Raises:
        ValueError: If format_type is invalid
        FileNotFoundError: If file doesn't exist
        DataError: If file cannot be parsed

    Example:
        >>> select_config_keys("config.yaml", "yaml", ["database.host", "database.port"])
        {"database": {"host": "localhost", "port": 5432}}
        >>> select_config_keys("config.toml", "toml", ["server.port", "logging.level"])
        {"server": {"port": 8080}, "logging": {"level": "INFO"}}
    """
    if format_type not in ["yaml", "toml", "ini"]:
        raise ValueError(
            f"format_type must be 'yaml', 'toml', or 'ini', got: {format_type}"
        )

    logger.info(f"Selecting config keys: {file_path} ({len(key_paths)} paths)")

    # Load the appropriate config file
    if format_type == "yaml":
        data = read_yaml_file(file_path)
    elif format_type == "toml":
        data = read_toml_file(file_path)
    else:  # ini
        data = read_ini_file(file_path)

    result: dict[str, Any] = {}

    for path in key_paths:
        found, value = _get_value_at_path(data, path)
        if found:
            # Build nested structure
            keys = path.split(".")
            current = result

            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]

            current[keys[-1]] = value

    logger.info(f"Selected {len(key_paths)} key paths")
    return result


@strands_tool
def filter_config_sections(
    file_path: str, format_type: str, section_pattern: str
) -> dict:
    """Get only sections/top-level keys matching pattern from config file.

    Filters config to return only top-level sections whose names match the
    search pattern (case-insensitive substring match). Particularly useful
    for INI files with multiple sections.

    Args:
        file_path: Path to config file
        format_type: Format of file ("yaml", "toml", or "ini")
        section_pattern: Text pattern to match section names

    Returns:
        Dictionary containing only matching sections

    Raises:
        ValueError: If format_type is invalid
        FileNotFoundError: If file doesn't exist
        DataError: If file cannot be parsed

    Example:
        >>> filter_config_sections("config.ini", "ini", "database")
        {"database": {"host": "localhost", "port": "5432"}}
        >>> filter_config_sections("config.yaml", "yaml", "test")
        {"test_database": {...}, "test_api": {...}}
    """
    if format_type not in ["yaml", "toml", "ini"]:
        raise ValueError(
            f"format_type must be 'yaml', 'toml', or 'ini', got: {format_type}"
        )

    logger.info(
        f"Filtering config sections: {file_path} for pattern '{section_pattern}'"
    )

    # Load the appropriate config file
    if format_type == "yaml":
        data = read_yaml_file(file_path)
    elif format_type == "toml":
        data = read_toml_file(file_path)
    else:  # ini
        data = read_ini_file(file_path)

    pattern_lower = section_pattern.lower()
    result = {key: value for key, value in data.items() if pattern_lower in key.lower()}

    logger.info(f"Found {len(result)} sections matching '{section_pattern}'")
    return result


@strands_tool
def preview_config_section(
    file_path: str, format_type: str, section_path: str, max_items: int
) -> dict:
    """Get first N items from config section without loading entire section.

    Returns a limited preview of items at the specified path. Useful for
    inspecting large config sections without loading all values.

    Args:
        file_path: Path to config file
        format_type: Format of file ("yaml", "toml", or "ini")
        section_path: Dot-separated path to section (empty string for root)
        max_items: Maximum number of items to return

    Returns:
        Dictionary with up to max_items keys from the section

    Raises:
        ValueError: If format_type is invalid or path not found
        FileNotFoundError: If file doesn't exist
        DataError: If file cannot be parsed

    Example:
        >>> preview_config_section("config.yaml", "yaml", "database", 2)
        {"host": "localhost", "port": 5432}
        >>> preview_config_section("config.toml", "toml", "", 3)
        {"database": {...}, "logging": {...}, "features": {...}}
    """
    if format_type not in ["yaml", "toml", "ini"]:
        raise ValueError(
            f"format_type must be 'yaml', 'toml', or 'ini', got: {format_type}"
        )

    logger.info(
        f"Previewing config section: {file_path} at '{section_path}' (max_items={max_items})"
    )

    # Load the appropriate config file
    if format_type == "yaml":
        data = read_yaml_file(file_path)
    elif format_type == "toml":
        data = read_toml_file(file_path)
    else:  # ini
        data = read_ini_file(file_path)

    # Navigate to the specified path
    if section_path:
        found, target = _get_value_at_path(data, section_path)
        if not found:
            raise ValueError(f"Path not found in config: {section_path}")
        if not isinstance(target, dict):
            raise ValueError(f"Path does not point to a dictionary: {section_path}")
        data = target

    # Get first N items
    result = dict(list(data.items())[:max_items])
    logger.info(f"Previewed {len(result)} items from section '{section_path}'")
    return result
