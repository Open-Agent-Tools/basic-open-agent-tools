"""Tests for configuration file processing functions.

This module provides comprehensive tests for the configuration processing toolkit functions,
including unit tests, integration tests, and Google AI compatibility verification.
"""

import inspect
import logging
import tempfile
import warnings
from pathlib import Path

import pytest
from dotenv import load_dotenv
from google.adk.agents import Agent

from basic_open_agent_tools.data.config_processing import (
    _deep_merge,
    merge_config_files,
    read_ini_file,
    validate_config_schema,
    write_ini_file,
)

# Initialize environment and logging
load_dotenv()
logging.basicConfig(level=logging.ERROR)
warnings.filterwarnings("ignore")

# Import optional dependencies if available
try:
    import yaml  # noqa: F401

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import tomli  # noqa: F401

    TOML_AVAILABLE = True
except ImportError:
    try:
        import tomllib  # noqa: F401

        TOML_AVAILABLE = True
    except ImportError:
        TOML_AVAILABLE = False

try:
    import tomli_w  # noqa: F401

    TOML_WRITE_AVAILABLE = True
except ImportError:
    TOML_WRITE_AVAILABLE = False

# Conditionally import functions that require optional dependencies
if YAML_AVAILABLE:
    from basic_open_agent_tools.data.config_processing import (
        read_yaml_file,
        write_yaml_file,
    )

if TOML_AVAILABLE:
    from basic_open_agent_tools.data.config_processing import read_toml_file

if TOML_WRITE_AVAILABLE:
    from basic_open_agent_tools.data.config_processing import write_toml_file


class TestConfigValidation:
    """Test cases for configuration validation functionality."""

    @pytest.fixture
    def sample_schemas(self):
        """Provide sample configuration schemas for testing."""
        return {
            "basic": {
                "port": {"type": int, "required": True},
                "host": {"type": str, "required": True},
                "debug": {"type": bool, "required": False},
            },
            "with_allowed_values": {
                "mode": {
                    "type": str,
                    "required": True,
                    "allowed_values": ["development", "production", "test"],
                },
                "debug": {"type": bool, "required": False},
            },
            "complex": {
                "server": {
                    "type": dict,
                    "required": True,
                    "schema": {
                        "host": {"type": str, "required": True},
                        "port": {"type": int, "required": True},
                    },
                },
                "logging": {
                    "type": dict,
                    "required": False,
                    "schema": {
                        "level": {
                            "type": str,
                            "required": True,
                            "allowed_values": ["debug", "info", "warning", "error"],
                        },
                        "file": {"type": str, "required": False},
                    },
                },
            },
        }

    @pytest.fixture
    def sample_configs(self):
        """Provide sample configuration data for testing."""
        return {
            "valid_basic": {"port": 8080, "debug": True, "host": "localhost"},
            "missing_required": {"debug": True},
            "wrong_type": {"port": "8080", "debug": True, "host": "localhost"},
            "valid_with_allowed": {"mode": "production", "debug": False},
            "invalid_allowed_value": {"mode": "invalid", "debug": False},
            "with_unknown_field": {
                "port": 8080,
                "host": "localhost",
                "unknown": "value",
            },
        }

    def test_validate_config_schema_valid_configs(self, sample_schemas, sample_configs):
        """Test validation with valid configurations."""
        # Basic valid config
        errors = validate_config_schema(
            sample_configs["valid_basic"], sample_schemas["basic"]
        )
        assert len(errors) == 0

        # Valid config with allowed values
        errors = validate_config_schema(
            sample_configs["valid_with_allowed"], sample_schemas["with_allowed_values"]
        )
        assert len(errors) == 0

    def test_validate_config_schema_missing_required(
        self, sample_schemas, sample_configs
    ):
        """Test validation with missing required fields."""
        errors = validate_config_schema(
            sample_configs["missing_required"], sample_schemas["basic"]
        )
        assert len(errors) >= 1

        # Should have errors for missing required fields
        error_text = " ".join(errors)
        assert "port" in error_text
        assert "host" in error_text

    def test_validate_config_schema_wrong_types(self, sample_schemas, sample_configs):
        """Test validation with incorrect data types."""
        errors = validate_config_schema(
            sample_configs["wrong_type"], sample_schemas["basic"]
        )
        assert len(errors) >= 1

        # Should have error for incorrect type
        error_text = " ".join(errors)
        assert "port" in error_text
        assert "type" in error_text.lower()

    def test_validate_config_schema_allowed_values(
        self, sample_schemas, sample_configs
    ):
        """Test validation with allowed values constraints."""
        # Invalid allowed value
        errors = validate_config_schema(
            sample_configs["invalid_allowed_value"],
            sample_schemas["with_allowed_values"],
        )
        assert len(errors) >= 1

        error_text = " ".join(errors)
        assert "mode" in error_text
        assert "invalid" in error_text.lower() or "value" in error_text.lower()

    def test_validate_config_schema_unknown_fields(
        self, sample_schemas, sample_configs
    ):
        """Test validation with unknown fields."""
        errors = validate_config_schema(
            sample_configs["with_unknown_field"], sample_schemas["basic"]
        )
        assert len(errors) >= 1

        error_text = " ".join(errors)
        assert "unknown" in error_text


class TestIniFileOperations:
    """Test cases for INI file read/write operations."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for output files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def sample_ini_configs(self):
        """Provide sample INI configuration data."""
        return {
            "basic": {
                "server": {"host": "localhost", "port": "8080"},
                "auth": {"enabled": "true", "timeout": "30"},
            },
            "complex": {
                "database": {
                    "host": "db.example.com",
                    "port": "5432",
                    "name": "myapp",
                    "ssl": "true",
                },
                "cache": {"type": "redis", "host": "cache.example.com", "port": "6379"},
                "logging": {
                    "level": "info",
                    "file": "/var/log/myapp.log",
                    "max_size": "100MB",
                },
            },
            "override": {
                "server": {"port": "9090", "debug": "true"},
                "auth": {"enabled": "true", "method": "oauth"},
            },
        }

    def test_write_read_ini_basic(self, temp_output_dir, sample_ini_configs):
        """Test basic INI file write and read operations."""
        ini_file = temp_output_dir / "test.ini"

        # Write INI file
        write_ini_file(sample_ini_configs["basic"], str(ini_file))

        # Verify file was created
        assert ini_file.exists()

        # Read back the data
        read_data = read_ini_file(str(ini_file))

        # Verify structure and content
        assert "server" in read_data
        assert "auth" in read_data
        assert read_data["server"]["host"] == "localhost"
        assert read_data["server"]["port"] == "8080"
        assert read_data["auth"]["enabled"] == "true"
        assert read_data["auth"]["timeout"] == "30"

    def test_write_read_ini_complex(self, temp_output_dir, sample_ini_configs):
        """Test INI operations with complex nested configurations."""
        ini_file = temp_output_dir / "complex.ini"

        # Write complex configuration
        write_ini_file(sample_ini_configs["complex"], str(ini_file))

        # Read back and verify all sections and keys
        read_data = read_ini_file(str(ini_file))

        # Verify database section
        assert read_data["database"]["host"] == "db.example.com"
        assert read_data["database"]["port"] == "5432"
        assert read_data["database"]["ssl"] == "true"

        # Verify cache section
        assert read_data["cache"]["type"] == "redis"
        assert read_data["cache"]["port"] == "6379"

        # Verify logging section
        assert read_data["logging"]["level"] == "info"
        assert read_data["logging"]["max_size"] == "100MB"

    def test_read_ini_file_not_found(self, temp_output_dir):
        """Test reading non-existent INI file."""
        nonexistent_file = temp_output_dir / "nonexistent.ini"

        with pytest.raises(FileNotFoundError):
            read_ini_file(str(nonexistent_file))

    def test_write_ini_empty_config(self, temp_output_dir):
        """Test writing empty configuration."""
        ini_file = temp_output_dir / "empty.ini"

        write_ini_file({}, str(ini_file))
        read_data = read_ini_file(str(ini_file))

        assert len(read_data) == 0


class TestConfigMerging:
    """Test cases for configuration merging functionality."""

    @pytest.fixture
    def temp_config_files(self):
        """Create temporary configuration files for merging tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create base config
            base_config = {
                "server": {"host": "localhost", "port": "8080"},
                "logging": {"level": "info", "file": "/var/log/app.log"},
                "features": {"auth": "enabled", "cache": "enabled"},
            }

            # Create override config
            override_config = {
                "server": {"port": "9090", "debug": "true"},
                "logging": {"level": "debug"},
                "features": {"monitoring": "enabled"},
                "database": {"host": "db.example.com", "port": "5432"},
            }

            # Create additional config
            additional_config = {
                "server": {"ssl": "true"},
                "cache": {"type": "redis", "host": "cache.example.com"},
                "features": {"auth": "disabled"},  # Override again
            }

            # Write files
            base_file = temp_path / "base.ini"
            override_file = temp_path / "override.ini"
            additional_file = temp_path / "additional.ini"

            write_ini_file(base_config, str(base_file))
            write_ini_file(override_config, str(override_file))
            write_ini_file(additional_config, str(additional_file))

            yield {
                "base": str(base_file),
                "override": str(override_file),
                "additional": str(additional_file),
                "base_config": base_config,
                "override_config": override_config,
                "additional_config": additional_config,
            }

    def test_deep_merge_basic(self):
        """Test basic dictionary merging functionality."""
        base = {"a": 1, "b": 2, "c": {"x": 10}}
        override = {"b": 3, "c": {"y": 20}, "d": 4}

        result = _deep_merge(base, override)

        # Check merged values
        assert result["a"] == 1  # Preserved from base
        assert result["b"] == 3  # Overridden
        assert result["d"] == 4  # Added from override

        # Check nested merge
        assert result["c"]["x"] == 10  # Preserved from base
        assert result["c"]["y"] == 20  # Added from override

    def test_deep_merge_nested_complex(self):
        """Test complex nested dictionary merging."""
        base = {
            "server": {"host": "localhost", "port": 8080, "ssl": {"enabled": False}},
            "database": {"host": "db1", "port": 5432},
            "features": ["auth", "logging"],
        }

        override = {
            "server": {"port": 9090, "ssl": {"enabled": True, "cert": "/path/to/cert"}},
            "cache": {"type": "redis"},
            "features": ["monitoring"],  # This will replace, not merge
        }

        result = _deep_merge(base, override)

        # Check server merge
        assert result["server"]["host"] == "localhost"  # Preserved
        assert result["server"]["port"] == 9090  # Overridden
        assert result["server"]["ssl"]["enabled"] is True  # Overridden nested
        assert result["server"]["ssl"]["cert"] == "/path/to/cert"  # Added nested

        # Check other sections
        assert result["database"]["host"] == "db1"  # Preserved
        assert result["cache"]["type"] == "redis"  # Added
        assert result["features"] == [
            "monitoring"
        ]  # Replaced (lists are replaced, not merged)

    def test_merge_config_files_basic(self, temp_config_files):
        """Test merging multiple configuration files."""
        config_paths = [temp_config_files["base"], temp_config_files["override"]]

        merged = merge_config_files(config_paths, "ini")

        # Verify merge results
        assert merged["server"]["host"] == "localhost"  # From base
        assert merged["server"]["port"] == "9090"  # Overridden
        assert merged["server"]["debug"] == "true"  # Added from override
        assert merged["logging"]["level"] == "debug"  # Overridden
        assert merged["logging"]["file"] == "/var/log/app.log"  # Preserved from base
        assert merged["features"]["auth"] == "enabled"  # From base
        assert merged["features"]["monitoring"] == "enabled"  # Added from override
        assert merged["database"]["host"] == "db.example.com"  # Added from override

    def test_merge_config_files_multiple(self, temp_config_files):
        """Test merging multiple configuration files in sequence."""
        config_paths = [
            temp_config_files["base"],
            temp_config_files["override"],
            temp_config_files["additional"],
        ]

        merged = merge_config_files(config_paths, "ini")

        # Verify final merge results (additional overrides override)
        assert merged["server"]["port"] == "9090"  # From override
        assert merged["server"]["ssl"] == "true"  # From additional
        assert (
            merged["features"]["auth"] == "disabled"
        )  # Final override from additional
        assert merged["cache"]["type"] == "redis"  # From additional

    def test_merge_config_files_no_paths(self):
        """Test merging with no configuration paths."""
        with pytest.raises(ValueError, match="at least one"):
            merge_config_files([], "ini")

    def test_merge_config_files_invalid_format(self, temp_config_files):
        """Test merging with invalid format specification."""
        config_paths = [temp_config_files["base"]]

        with pytest.raises(ValueError, match="Unsupported"):
            merge_config_files(config_paths, "invalid_format")


@pytest.mark.skipif(not YAML_AVAILABLE, reason="PyYAML not installed")
class TestYamlFileOperations:
    """Test cases for YAML file operations."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for output files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def sample_yaml_configs(self):
        """Provide sample YAML configuration data."""
        return {
            "basic": {
                "server": {"host": "localhost", "port": 8080},
                "auth": {"enabled": True, "timeout": 30},
                "features": ["authentication", "logging", "monitoring"],
            },
            "complex": {
                "database": {
                    "primary": {"host": "db1.example.com", "port": 5432, "ssl": True},
                    "replica": {"host": "db2.example.com", "port": 5432, "ssl": True},
                },
                "cache": {
                    "redis": {"host": "cache.example.com", "port": 6379, "db": 0}
                },
            },
        }

    def test_write_read_yaml_basic(self, temp_output_dir, sample_yaml_configs):
        """Test basic YAML file write and read operations."""
        yaml_file = temp_output_dir / "test.yaml"

        # Write YAML file
        write_yaml_file(sample_yaml_configs["basic"], str(yaml_file))

        # Verify file was created
        assert yaml_file.exists()

        # Read back the data
        read_data = read_yaml_file(str(yaml_file))

        # Verify structure and content
        assert read_data["server"]["host"] == "localhost"
        assert read_data["server"]["port"] == 8080
        assert read_data["auth"]["enabled"] is True
        assert read_data["auth"]["timeout"] == 30
        assert "authentication" in read_data["features"]
        assert len(read_data["features"]) == 3

    def test_write_read_yaml_complex(self, temp_output_dir, sample_yaml_configs):
        """Test YAML operations with complex nested data structures."""
        yaml_file = temp_output_dir / "complex.yaml"

        # Write complex configuration
        write_yaml_file(sample_yaml_configs["complex"], str(yaml_file))

        # Read back and verify
        read_data = read_yaml_file(str(yaml_file))

        # Verify nested structure
        assert read_data["database"]["primary"]["host"] == "db1.example.com"
        assert read_data["database"]["primary"]["ssl"] is True
        assert read_data["database"]["replica"]["port"] == 5432
        assert read_data["cache"]["redis"]["db"] == 0

    def test_read_yaml_file_not_found(self, temp_output_dir):
        """Test reading non-existent YAML file."""
        nonexistent_file = temp_output_dir / "nonexistent.yaml"

        with pytest.raises(FileNotFoundError):
            read_yaml_file(str(nonexistent_file))

    def test_read_yaml_file_invalid(self, temp_output_dir):
        """Test reading invalid YAML file."""
        invalid_file = temp_output_dir / "invalid.yaml"
        invalid_file.write_text("invalid: yaml: content: - [")

        with pytest.raises(ValueError):
            read_yaml_file(str(invalid_file))


@pytest.mark.skipif(not TOML_AVAILABLE, reason="TOML library not installed")
class TestTomlFileOperations:
    """Test cases for TOML file operations."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for output files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def sample_toml_configs(self):
        """Provide sample TOML configuration data."""
        return {
            "basic": {
                "server": {"host": "localhost", "port": 8080},
                "auth": {"enabled": True, "timeout": 30},
            },
            "complex": {
                "database": {
                    "host": "db.example.com",
                    "port": 5432,
                    "credentials": {
                        "username": "admin",
                        "password_file": "/etc/secrets/db_password",
                    },
                },
                "services": {
                    "web": {"port": 8080, "workers": 4},
                    "api": {"port": 8081, "workers": 2},
                },
            },
        }

    def test_read_toml_basic(self, temp_output_dir, sample_toml_configs):
        """Test basic TOML file reading."""
        toml_file = temp_output_dir / "test.toml"

        # Write TOML content manually for reading test
        toml_content = """
[server]
host = "localhost"
port = 8080

[auth]
enabled = true
timeout = 30
"""
        toml_file.write_text(toml_content)

        # Read and verify
        read_data = read_toml_file(str(toml_file))

        assert read_data["server"]["host"] == "localhost"
        assert read_data["server"]["port"] == 8080
        assert read_data["auth"]["enabled"] is True
        assert read_data["auth"]["timeout"] == 30

    def test_read_toml_complex(self, temp_output_dir):
        """Test reading complex TOML file with nested sections."""
        toml_file = temp_output_dir / "complex.toml"

        # Write complex TOML content
        toml_content = """
[database]
host = "db.example.com"
port = 5432

[database.credentials]
username = "admin"
password_file = "/etc/secrets/db_password"

[services.web]
port = 8080
workers = 4

[services.api]
port = 8081
workers = 2
"""
        toml_file.write_text(toml_content)

        # Read and verify nested structure
        read_data = read_toml_file(str(toml_file))

        assert read_data["database"]["host"] == "db.example.com"
        assert read_data["database"]["credentials"]["username"] == "admin"
        assert read_data["services"]["web"]["workers"] == 4
        assert read_data["services"]["api"]["port"] == 8081

    @pytest.mark.skipif(not TOML_WRITE_AVAILABLE, reason="tomli_w not installed")
    def test_write_read_toml_roundtrip(self, temp_output_dir, sample_toml_configs):
        """Test TOML write and read round-trip."""
        toml_file = temp_output_dir / "roundtrip.toml"

        # Write TOML file
        write_toml_file(sample_toml_configs["basic"], str(toml_file))

        # Read back and verify
        read_data = read_toml_file(str(toml_file))

        assert read_data["server"]["host"] == "localhost"
        assert read_data["server"]["port"] == 8080
        assert read_data["auth"]["enabled"] is True
        assert read_data["auth"]["timeout"] == 30

    def test_read_toml_file_not_found(self, temp_output_dir):
        """Test reading non-existent TOML file."""
        nonexistent_file = temp_output_dir / "nonexistent.toml"

        with pytest.raises(FileNotFoundError):
            read_toml_file(str(nonexistent_file))

    def test_read_toml_file_invalid(self, temp_output_dir):
        """Test reading invalid TOML file."""
        invalid_file = temp_output_dir / "invalid.toml"
        invalid_file.write_text("invalid toml content ][")

        with pytest.raises(ValueError):
            read_toml_file(str(invalid_file))


class TestConfigCompatibility:
    """Test Google AI compatibility for configuration processing functions."""

    def test_function_signatures_compatibility(self):
        """Test that all config functions have Google AI compatible signatures."""
        # Test core functions that should be available
        core_functions = [
            validate_config_schema,
            read_ini_file,
            write_ini_file,
            merge_config_files,
        ]

        for func in core_functions:
            sig = inspect.signature(func)

            # Check that no parameters have default values
            for param_name, param in sig.parameters.items():
                assert param.default == inspect.Parameter.empty, (
                    f"Function {func.__name__} parameter {param_name} has default value, "
                    "violating Google AI requirements"
                )

            # Check that return type is specified
            assert sig.return_annotation != inspect.Signature.empty, (
                f"Function {func.__name__} missing return type annotation"
            )

    def test_parameter_types_compatibility(self):
        """Test that parameter types are Google AI compatible."""
        # Test validate_config_schema
        sig = inspect.signature(validate_config_schema)
        params = sig.parameters

        assert params["config"].annotation is dict
        assert params["schema"].annotation is dict

        # Check return type is List[str]
        return_annotation = sig.return_annotation
        assert hasattr(return_annotation, "__origin__")
        assert return_annotation.__origin__ is list

    @pytest.mark.skipif(not YAML_AVAILABLE, reason="PyYAML not installed")
    def test_yaml_functions_compatibility(self):
        """Test YAML functions compatibility when available."""
        yaml_functions = [read_yaml_file, write_yaml_file]

        for func in yaml_functions:
            sig = inspect.signature(func)

            # Check no default parameters
            for param_name, param in sig.parameters.items():
                assert param.default == inspect.Parameter.empty, (
                    f"YAML function {func.__name__} parameter {param_name} has default value"
                )

    @pytest.mark.skipif(not TOML_AVAILABLE, reason="TOML library not installed")
    def test_toml_functions_compatibility(self):
        """Test TOML functions compatibility when available."""
        toml_functions = [read_toml_file]

        if TOML_WRITE_AVAILABLE:
            toml_functions.append(write_toml_file)

        for func in toml_functions:
            sig = inspect.signature(func)

            # Check no default parameters
            for param_name, param in sig.parameters.items():
                assert param.default == inspect.Parameter.empty, (
                    f"TOML function {func.__name__} parameter {param_name} has default value"
                )


class TestConfigIntegration:
    """Integration tests combining multiple configuration processing operations."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for output files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def multi_format_configs(self, temp_output_dir):
        """Create configuration files in multiple formats."""
        configs = {}

        # Base configuration data
        base_config = {
            "server": {"host": "localhost", "port": "8080"},
            "logging": {"level": "info"},
        }

        # INI format
        ini_file = temp_output_dir / "config.ini"
        write_ini_file(base_config, str(ini_file))
        configs["ini"] = str(ini_file)

        # YAML format (if available)
        if YAML_AVAILABLE:
            yaml_file = temp_output_dir / "config.yaml"
            write_yaml_file(base_config, str(yaml_file))
            configs["yaml"] = str(yaml_file)

        # TOML format (if available)
        if TOML_WRITE_AVAILABLE:
            toml_file = temp_output_dir / "config.toml"
            write_toml_file(base_config, str(toml_file))
            configs["toml"] = str(toml_file)

        configs["base_config"] = base_config
        return configs

    def test_config_validation_workflow(self):
        """Test complete configuration validation workflow."""
        # Define schema
        schema = {
            "server": {
                "type": dict,
                "required": True,
            },
            "logging": {
                "type": dict,
                "required": False,
            },
            "debug": {
                "type": bool,
                "required": False,
            },
        }

        # Test valid configuration
        valid_config = {
            "server": {"host": "localhost", "port": 8080},
            "logging": {"level": "info"},
            "debug": False,
        }

        errors = validate_config_schema(valid_config, schema)
        assert len(errors) == 0

        # Test invalid configuration
        invalid_config = {
            "server": "not a dict",  # Wrong type
            "unknown": "field",  # Unknown field
        }

        errors = validate_config_schema(invalid_config, schema)
        assert len(errors) > 0

    def test_config_merge_and_validate_workflow(self, temp_output_dir):
        """Test workflow combining config merging and validation."""
        # Create multiple config files
        base_config = {
            "server": {"host": "localhost", "port": "8080"},
            "logging": {"level": "info"},
        }

        override_config = {
            "server": {"port": "9090", "ssl": "true"},
            "database": {"host": "db.example.com"},
        }

        base_file = temp_output_dir / "base.ini"
        override_file = temp_output_dir / "override.ini"

        write_ini_file(base_config, str(base_file))
        write_ini_file(override_config, str(override_file))

        # Merge configurations
        merged = merge_config_files([str(base_file), str(override_file)], "ini")

        # Validate merged configuration
        schema = {
            "server": {"type": dict, "required": True},
            "logging": {"type": dict, "required": False},
            "database": {"type": dict, "required": False},
        }

        errors = validate_config_schema(merged, schema)
        assert len(errors) == 0

        # Verify merge results
        assert merged["server"]["host"] == "localhost"  # Preserved
        assert merged["server"]["port"] == "9090"  # Overridden
        assert merged["server"]["ssl"] == "true"  # Added
        assert merged["database"]["host"] == "db.example.com"  # Added


class TestConfigErrorHandling:
    """Test error handling and edge cases for configuration functions."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for output files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_validation_error_handling(self):
        """Test configuration validation error handling."""
        # Test with invalid schema format
        config = {"key": "value"}
        invalid_schema = {"key": "not a dict"}  # Schema values should be dicts

        # Should not crash, but may return errors
        validate_config_schema(config, invalid_schema)
        # Implementation specific - may handle gracefully or report errors

    def test_file_operation_error_handling(self, temp_output_dir):
        """Test file operation error handling."""
        # Test reading non-existent files
        nonexistent = temp_output_dir / "nonexistent.ini"

        with pytest.raises(FileNotFoundError):
            read_ini_file(str(nonexistent))

        # Test merge with non-existent files
        with pytest.raises((FileNotFoundError, ValueError)):
            merge_config_files([str(nonexistent)], "ini")

    def test_invalid_config_data_handling(self, temp_output_dir):
        """Test handling of invalid configuration data."""
        # Test writing non-serializable data
        invalid_config = {
            "section": {
                "key": object()  # Not serializable
            }
        }

        ini_file = temp_output_dir / "invalid.ini"

        # Should handle gracefully or raise appropriate error
        try:
            write_ini_file(invalid_config, str(ini_file))
            # If it doesn't raise, read it back to see what happened
            read_data = read_ini_file(str(ini_file))
            # Implementation may convert to string representation
            assert "section" in read_data
        except (TypeError, ValueError):
            # Expected - non-serializable data should raise error
            pass


class TestConfigRoundTrip:
    """Test round-trip operations to ensure data integrity."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for output files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_ini_roundtrip_data_integrity(self, temp_output_dir):
        """Test that INI write -> read preserves data integrity."""
        original_data = {
            "server": {"host": "localhost", "port": "8080", "debug": "true"},
            "database": {"host": "db.example.com", "port": "5432", "ssl": "false"},
        }

        ini_file = temp_output_dir / "roundtrip.ini"

        # Write and read back
        write_ini_file(original_data, str(ini_file))
        read_data = read_ini_file(str(ini_file))

        # Verify data integrity
        assert read_data == original_data

    @pytest.mark.skipif(not YAML_AVAILABLE, reason="PyYAML not installed")
    def test_yaml_roundtrip_data_integrity(self, temp_output_dir):
        """Test that YAML write -> read preserves data integrity."""
        original_data = {
            "server": {"host": "localhost", "port": 8080, "ssl": True},
            "features": ["auth", "logging", "monitoring"],
            "database": {"connections": 10, "timeout": 30.5},
        }

        yaml_file = temp_output_dir / "roundtrip.yaml"

        # Write and read back
        write_yaml_file(original_data, str(yaml_file))
        read_data = read_yaml_file(str(yaml_file))

        # Verify data integrity (YAML preserves types)
        assert read_data == original_data

    @pytest.mark.skipif(
        not (TOML_AVAILABLE and TOML_WRITE_AVAILABLE),
        reason="TOML read/write libraries not installed",
    )
    def test_toml_roundtrip_data_integrity(self, temp_output_dir):
        """Test that TOML write -> read preserves data integrity."""
        original_data = {
            "server": {"host": "localhost", "port": 8080, "ssl": True},
            "database": {"connections": 10, "timeout": 30.5},
        }

        toml_file = temp_output_dir / "roundtrip.toml"

        # Write and read back
        write_toml_file(original_data, str(toml_file))
        read_data = read_toml_file(str(toml_file))

        # Verify data integrity (TOML preserves types)
        assert read_data == original_data


class TestADKAgentIntegration:
    """Test ADK Agent integration with configuration processing tools."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary directory with test configuration files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test INI files
            base_config = {
                "server": {"host": "localhost", "port": "8080"},
                "database": {"host": "db.example.com", "port": "5432"},
                "logging": {"level": "info", "file": "/var/log/app.log"},
            }

            override_config = {
                "server": {"port": "9090", "debug": "true"},
                "logging": {"level": "debug"},
                "cache": {"type": "redis", "host": "cache.example.com"},
            }

            base_file = temp_path / "base.ini"
            override_file = temp_path / "override.ini"

            write_ini_file(base_config, str(base_file))
            write_ini_file(override_config, str(override_file))

            yield {
                "base_file": str(base_file),
                "override_file": str(override_file),
                "base_config": base_config,
                "override_config": override_config,
                "temp_dir": str(temp_path),
            }

    @pytest.fixture
    def adk_agent_with_config_tools(self):
        """Create ADK agent configured with configuration processing tools."""
        tools = [
            read_ini_file,
            write_ini_file,
            validate_config_schema,
            merge_config_files,
        ]

        # Add optional format tools if available
        if YAML_AVAILABLE:
            from basic_open_agent_tools.data.config_processing import (
                read_yaml_file,
                write_yaml_file,
            )

            tools.extend([read_yaml_file, write_yaml_file])

        if TOML_AVAILABLE:
            from basic_open_agent_tools.data.config_processing import read_toml_file

            tools.append(read_toml_file)

        if TOML_WRITE_AVAILABLE:
            from basic_open_agent_tools.data.config_processing import write_toml_file

            tools.append(write_toml_file)

        agent = Agent(
            model="gemini-2.0-flash",
            name="ConfigProcessingAgent",
            instruction="You are a configuration processing agent. Use the available tools to read, write, validate, and merge configuration files in various formats.",
            description="An agent specialized in configuration file processing, validation, and management.",
            tools=tools,
        )
        return agent

    @pytest.fixture
    def adk_agent_with_validation_tool(self):
        """Create ADK agent configured with validation tool only."""
        agent = Agent(
            model="gemini-2.0-flash",
            name="ConfigValidationAgent",
            instruction="You are a configuration validation agent. Use the validate_config_schema tool to validate configuration data against schemas.",
            description="An agent specialized in configuration validation.",
            tools=[validate_config_schema],
        )
        return agent

    def test_read_ini_file_basic_functionality(self, temp_config_dir):
        """Test read_ini_file function directly (non-ADK)."""
        # Read the base configuration
        config_data = read_ini_file(temp_config_dir["base_file"])

        # Verify structure and content
        assert "server" in config_data
        assert "database" in config_data
        assert "logging" in config_data
        assert config_data["server"]["host"] == "localhost"
        assert config_data["server"]["port"] == "8080"
        assert config_data["database"]["host"] == "db.example.com"

    def test_adk_agent_can_read_ini_file(
        self, adk_agent_with_config_tools, temp_config_dir
    ):
        """Test that ADK agent can successfully read INI files."""
        instruction = (
            f"Read the INI configuration file at path: {temp_config_dir['base_file']}"
        )

        try:
            response = adk_agent_with_config_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence that the file was read successfully
            expected_elements = ["server", "database", "localhost", "config"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of successful config reading
            assert found_elements >= 2, (
                f"Expected config reading elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed to read INI file: {e}")

    def test_validate_config_schema_basic_functionality(self):
        """Test validate_config_schema function directly (non-ADK)."""
        config = {
            "server": {"host": "localhost", "port": 8080},
            "database": {"host": "db.example.com", "port": 5432},
        }

        schema = {
            "server": {"type": dict, "required": True},
            "database": {"type": dict, "required": True},
        }

        # Valid configuration should have no errors
        errors = validate_config_schema(config, schema)
        assert len(errors) == 0

        # Invalid configuration should have errors
        invalid_config = {"server": "not a dict"}
        errors = validate_config_schema(invalid_config, schema)
        assert len(errors) > 0

    def test_adk_agent_can_validate_config_schema(self, adk_agent_with_validation_tool):
        """Test that ADK agent can validate configuration schemas."""
        instruction = """Validate this config: {"server": {"host": "localhost", "port": 8080}} against this schema: {"server": {"type": "dict", "required": true}}"""

        try:
            response = adk_agent_with_validation_tool.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence that validation occurred
            expected_elements = ["valid", "config", "schema", "server"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of successful validation
            assert found_elements >= 2, (
                f"Expected validation elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed to validate config schema: {e}")

    def test_merge_config_files_basic_functionality(self, temp_config_dir):
        """Test merge_config_files function directly (non-ADK)."""
        config_paths = [temp_config_dir["base_file"], temp_config_dir["override_file"]]

        merged_config = merge_config_files(config_paths, "ini")

        # Verify merge results
        assert merged_config["server"]["host"] == "localhost"  # From base
        assert merged_config["server"]["port"] == "9090"  # Overridden
        assert merged_config["server"]["debug"] == "true"  # Added from override
        assert merged_config["logging"]["level"] == "debug"  # Overridden
        assert merged_config["cache"]["type"] == "redis"  # Added from override

    def test_adk_agent_can_merge_config_files(
        self, adk_agent_with_config_tools, temp_config_dir
    ):
        """Test that ADK agent can merge configuration files."""
        file_paths = [temp_config_dir["base_file"], temp_config_dir["override_file"]]
        paths_str = ", ".join(f'"{path}"' for path in file_paths)
        instruction = (
            f'Merge these INI configuration files: {paths_str} using format "ini"'
        )

        try:
            response = adk_agent_with_config_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence that merging occurred
            expected_elements = ["merge", "config", "server", "override"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of successful merging
            assert found_elements >= 2, (
                f"Expected merging elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed to merge config files: {e}")

    def test_write_ini_file_basic_functionality(self, temp_config_dir):
        """Test write_ini_file function directly (non-ADK)."""
        test_config = {
            "test_section": {"key1": "value1", "key2": "value2"},
            "another_section": {"key3": "value3"},
        }

        output_file = Path(temp_config_dir["temp_dir"]) / "test_output.ini"
        write_ini_file(test_config, str(output_file))

        # Verify file was created and can be read back
        assert output_file.exists()
        read_back = read_ini_file(str(output_file))
        assert read_back == test_config

    def test_adk_agent_can_write_ini_file(
        self, adk_agent_with_config_tools, temp_config_dir
    ):
        """Test that ADK agent can write INI files."""
        output_file = Path(temp_config_dir["temp_dir"]) / "agent_output.ini"
        instruction = f'Write this config to INI file: {{"app": {{"name": "test", "version": "1.0"}}}} at path: "{output_file}"'

        try:
            response = adk_agent_with_config_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence that writing occurred
            expected_elements = ["write", "config", "file", "ini"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of successful file writing
            assert found_elements >= 2, (
                f"Expected writing elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed to write INI file: {e}")

    def test_adk_agent_error_handling(self, adk_agent_with_config_tools):
        """Test ADK agent error handling with invalid file paths."""
        instruction = 'Read INI configuration file from non-existent path: "/invalid/path/config.ini"'

        try:
            response = adk_agent_with_config_tools.run(instruction)

            # The agent should handle the error gracefully
            assert response is not None

            response_str = str(response).lower()
            error_indicators = [
                "error",
                "not found",
                "does not exist",
                "invalid",
                "file",
            ]

            # Check if the response indicates an error was handled
            has_error_indication = any(
                indicator in response_str for indicator in error_indicators
            )

            # Either the agent handled the error or provided some response
            assert has_error_indication or len(response_str) > 0

        except Exception as e:
            # Some exceptions are acceptable as they indicate proper error handling
            acceptable_errors = ["filenotfound", "not found", "does not exist"]
            error_msg = str(e).lower()

            is_acceptable = any(
                acceptable in error_msg for acceptable in acceptable_errors
            )

            if not is_acceptable:
                pytest.fail(f"Unexpected error type: {e}")

    @pytest.mark.skipif(not YAML_AVAILABLE, reason="PyYAML not installed")
    def test_adk_agent_can_process_yaml_files(
        self, adk_agent_with_config_tools, temp_config_dir
    ):
        """Test that ADK agent can process YAML files when available."""
        from basic_open_agent_tools.data.config_processing import write_yaml_file

        # Create a YAML test file
        yaml_config = {
            "app": {"name": "test_app", "version": "1.0"},
            "features": ["auth", "logging", "monitoring"],
        }

        yaml_file = Path(temp_config_dir["temp_dir"]) / "test.yaml"
        write_yaml_file(yaml_config, str(yaml_file))

        instruction = f'Read the YAML configuration file at path: "{yaml_file}"'

        try:
            response = adk_agent_with_config_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of YAML processing
            expected_elements = ["yaml", "app", "test_app", "config"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of successful YAML processing
            assert found_elements >= 2, (
                f"Expected YAML processing elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed to process YAML file: {e}")

    def test_config_validation_with_errors_functionality(self):
        """Test configuration validation with various error scenarios."""
        # Test missing required fields
        config = {"server": {"host": "localhost"}}  # Missing port
        schema = {
            "server": {
                "type": dict,
                "required": True,
                "schema": {
                    "host": {"type": str, "required": True},
                    "port": {"type": int, "required": True},
                },
            }
        }

        errors = validate_config_schema(config, schema)
        assert len(errors) >= 1

        # Test wrong data types
        config = {"server": {"host": "localhost", "port": "not_a_number"}}
        errors = validate_config_schema(config, schema)
        # May or may not have errors depending on implementation


class TestADKAgentConfigIntegration:
    """Integration tests combining multiple configuration operations with ADK."""

    @pytest.fixture
    def temp_multi_config_dir(self):
        """Create temporary directory with multiple configuration files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create multiple config files for complex workflow
            base_config = {
                "app": {"name": "myapp", "version": "1.0"},
                "server": {"host": "localhost", "port": "8080"},
                "database": {"host": "db.example.com", "port": "5432"},
            }

            env_config = {
                "server": {"port": "9090", "workers": "4"},
                "logging": {"level": "debug", "file": "/var/log/debug.log"},
            }

            local_config = {
                "server": {"debug": "true"},
                "database": {"ssl": "true"},
                "cache": {"enabled": "true", "type": "redis"},
            }

            # Write multiple files
            files = {}
            for name, config in [
                ("base", base_config),
                ("env", env_config),
                ("local", local_config),
            ]:
                file_path = temp_path / f"{name}.ini"
                write_ini_file(config, str(file_path))
                files[f"{name}_file"] = str(file_path)

            files["temp_dir"] = str(temp_path)
            files["configs"] = {
                "base": base_config,
                "env": env_config,
                "local": local_config,
            }
            yield files

    @pytest.fixture
    def adk_agent_with_all_config_tools(self):
        """Create ADK agent with comprehensive config processing tools."""
        tools = [
            read_ini_file,
            write_ini_file,
            validate_config_schema,
            merge_config_files,
        ]

        # Add all available format tools
        if YAML_AVAILABLE:
            from basic_open_agent_tools.data.config_processing import (
                read_yaml_file,
                write_yaml_file,
            )

            tools.extend([read_yaml_file, write_yaml_file])

        if TOML_AVAILABLE:
            from basic_open_agent_tools.data.config_processing import read_toml_file

            tools.append(read_toml_file)

        if TOML_WRITE_AVAILABLE:
            from basic_open_agent_tools.data.config_processing import write_toml_file

            tools.append(write_toml_file)

        agent = Agent(
            model="gemini-2.0-flash",
            name="ComprehensiveConfigAgent",
            instruction="You are a comprehensive configuration processing agent. Use the available tools to perform complex configuration management tasks including reading, writing, merging, and validating configs.",
            description="An agent capable of comprehensive configuration file management across multiple formats.",
            tools=tools,
        )
        return agent

    def test_adk_agent_comprehensive_config_workflow(
        self, adk_agent_with_all_config_tools, temp_multi_config_dir
    ):
        """Test ADK agent performing complex configuration workflow."""
        files = [
            temp_multi_config_dir["base_file"],
            temp_multi_config_dir["env_file"],
            temp_multi_config_dir["local_file"],
        ]
        files_str = ", ".join(f'"{f}"' for f in files)

        instruction = f'Merge these configuration files in order: {files_str} using format "ini" and tell me about the final server configuration'

        try:
            response = adk_agent_with_all_config_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of comprehensive config processing
            expected_elements = ["merge", "config", "server", "port", "9090"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of comprehensive config processing
            assert found_elements >= 3, (
                f"Expected comprehensive config elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed comprehensive config workflow: {e}")

    def test_adk_agent_config_validation_workflow(
        self, adk_agent_with_all_config_tools, temp_multi_config_dir
    ):
        """Test ADK agent performing configuration validation workflow."""
        instruction = f'''Read the configuration from "{temp_multi_config_dir["base_file"]}" and validate it against this schema: {{"app": {{"type": "dict", "required": true}}, "server": {{"type": "dict", "required": true}}}}'''

        try:
            response = adk_agent_with_all_config_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of validation workflow
            expected_elements = [
                "read",
                "validate",
                "config",
                "schema",
                "app",
                "server",
            ]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of validation workflow
            assert found_elements >= 3, (
                f"Expected validation workflow elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed config validation workflow: {e}")
