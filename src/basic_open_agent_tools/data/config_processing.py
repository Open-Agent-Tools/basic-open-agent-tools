"""Configuration file processing utilities for AI agents."""

import configparser
import json

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
        confirmed = check_user_confirmation(
            operation="overwrite existing YAML file",
            target=file_path,
            skip_confirm=skip_confirm,
            preview_info=preview,
        )

        if not confirmed:
            logger.debug(f"YAML write cancelled by user: {file_path}")
            return f"Operation cancelled by user: {file_path}"

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
        confirmed = check_user_confirmation(
            operation="overwrite existing TOML file",
            target=file_path,
            skip_confirm=skip_confirm,
            preview_info=preview,
        )

        if not confirmed:
            logger.debug(f"TOML write cancelled by user: {file_path}")
            return f"Operation cancelled by user: {file_path}"

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
        confirmed = check_user_confirmation(
            operation="overwrite existing INI file",
            target=file_path,
            skip_confirm=skip_confirm,
            preview_info=preview,
        )

        if not confirmed:
            logger.debug(f"INI write cancelled by user: {file_path}")
            return f"Operation cancelled by user: {file_path}"

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
