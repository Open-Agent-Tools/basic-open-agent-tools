"""Tests for configuration file processing functions."""

import os
import tempfile

import pytest

from basic_open_agent_tools.data.config_processing import (
    _deep_merge,
    merge_config_files,
    read_ini_file,
    validate_config_schema,
    write_ini_file,
)

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


class TestValidateConfigSchema:
    """Tests for validate_config_schema function."""

    def test_validate_config_schema_valid(self):
        """Test validation with valid config."""
        config = {"port": 8080, "debug": True, "host": "localhost"}
        schema = {
            "port": {"type": int, "required": True},
            "host": {"type": str, "required": True},
            "debug": {"type": bool, "required": False},
        }

        errors = validate_config_schema(config, schema)
        assert len(errors) == 0

    def test_validate_config_schema_missing_required(self):
        """Test validation with missing required field."""
        config = {"debug": True}
        schema = {
            "port": {"type": int, "required": True},
            "debug": {"type": bool, "required": False},
        }

        errors = validate_config_schema(config, schema)
        assert len(errors) == 1
        assert "missing" in errors[0]
        assert "port" in errors[0]

    def test_validate_config_schema_wrong_type(self):
        """Test validation with wrong type."""
        config = {"port": "8080", "debug": True}
        schema = {
            "port": {"type": int, "required": True},
            "debug": {"type": bool, "required": False},
        }

        errors = validate_config_schema(config, schema)
        assert len(errors) == 1
        assert "incorrect type" in errors[0]
        assert "port" in errors[0]

    def test_validate_config_schema_allowed_values(self):
        """Test validation with allowed values constraint."""
        config = {"mode": "production", "debug": True}
        schema = {
            "mode": {
                "type": str,
                "required": True,
                "allowed_values": ["development", "production", "test"],
            },
            "debug": {"type": bool, "required": False},
        }

        # Valid value
        errors = validate_config_schema(config, schema)
        assert len(errors) == 0

        # Invalid value
        config["mode"] = "invalid"
        errors = validate_config_schema(config, schema)
        assert len(errors) == 1
        assert "invalid value" in errors[0]
        assert "mode" in errors[0]

    def test_validate_config_schema_unknown_field(self):
        """Test validation with unknown field."""
        config = {"port": 8080, "unknown": "value"}
        schema = {"port": {"type": int, "required": True}}

        errors = validate_config_schema(config, schema)
        assert len(errors) == 1
        assert "unknown field" in errors[0].lower()
        assert "unknown" in errors[0]


class TestIniProcessing:
    """Tests for INI file processing functions."""

    def test_read_write_ini_file(self):
        """Test reading and writing INI files."""
        with tempfile.NamedTemporaryFile(suffix=".ini", delete=False) as temp:
            temp_path = temp.name

        try:
            # Test data
            config_data = {
                "server": {"host": "localhost", "port": "8080"},
                "auth": {"enabled": "true", "timeout": "30"},
            }

            # Write and read back
            write_ini_file(config_data, temp_path)
            read_data = read_ini_file(temp_path)

            # Verify
            assert "server" in read_data
            assert "auth" in read_data
            assert read_data["server"]["host"] == "localhost"
            assert read_data["server"]["port"] == "8080"
            assert read_data["auth"]["enabled"] == "true"
            assert read_data["auth"]["timeout"] == "30"

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_read_ini_file_not_found(self):
        """Test reading a non-existent INI file."""
        with pytest.raises(FileNotFoundError):
            read_ini_file("nonexistent.ini")


class TestDeepMerge:
    """Tests for _deep_merge helper function."""

    def test_deep_merge_basic(self):
        """Test basic dictionary merging."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}

        result = _deep_merge(base, override)

        assert result["a"] == 1
        assert result["b"] == 3  # Overridden
        assert result["c"] == 4  # Added

    def test_deep_merge_nested(self):
        """Test merging nested dictionaries."""
        base = {
            "server": {"host": "localhost", "port": 8080},
            "logging": {"level": "info"},
        }
        override = {"server": {"port": 9090, "debug": True}, "auth": {"enabled": True}}

        result = _deep_merge(base, override)

        # Check nested merge
        assert result["server"]["host"] == "localhost"  # Preserved
        assert result["server"]["port"] == 9090  # Overridden
        assert result["server"]["debug"] is True  # Added

        # Check other fields
        assert result["logging"]["level"] == "info"  # Preserved
        assert result["auth"]["enabled"] is True  # Added


class TestMergeConfigFiles:
    """Tests for merge_config_files function."""

    def test_merge_config_files_ini(self):
        """Test merging INI config files."""
        with tempfile.NamedTemporaryFile(
            suffix=".ini", delete=False
        ) as temp1, tempfile.NamedTemporaryFile(suffix=".ini", delete=False) as temp2:
            temp1_path = temp1.name
            temp2_path = temp2.name

        try:
            # Create test files
            config1 = {
                "server": {"host": "localhost", "port": "8080"},
                "logging": {"level": "info"},
            }
            config2 = {
                "server": {"port": "9090", "debug": "true"},
                "auth": {"enabled": "true"},
            }

            write_ini_file(config1, temp1_path)
            write_ini_file(config2, temp2_path)

            # Merge configs
            merged = merge_config_files([temp1_path, temp2_path], "ini")

            # Verify
            assert merged["server"]["host"] == "localhost"
            assert merged["server"]["port"] == "9090"  # Overridden
            assert merged["server"]["debug"] == "true"
            assert merged["logging"]["level"] == "info"
            assert merged["auth"]["enabled"] == "true"

        finally:
            # Clean up
            for path in [temp1_path, temp2_path]:
                if os.path.exists(path):
                    os.unlink(path)

    def test_merge_config_files_no_paths(self):
        """Test merging with no config paths."""
        with pytest.raises(ValueError):
            merge_config_files([], "ini")

    def test_merge_config_files_mixed_formats(self):
        """Test merging files with different formats."""
        with tempfile.NamedTemporaryFile(
            suffix=".ini", delete=False
        ) as temp1, tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as temp2:
            temp1_path = temp1.name
            temp2_path = temp2.name

        try:
            # Create test files
            config = {"server": {"host": "localhost"}}
            write_ini_file(config, temp1_path)

            # Try to merge different formats
            with pytest.raises(ValueError):  # Now raises ValueError for invalid format
                merge_config_files([temp1_path, temp2_path], "invalid_format")

        finally:
            # Clean up
            for path in [temp1_path, temp2_path]:
                if os.path.exists(path):
                    os.unlink(path)


@pytest.mark.skipif(not YAML_AVAILABLE, reason="PyYAML not installed")
class TestYamlProcessing:
    """Tests for YAML file processing functions."""

    def test_read_write_yaml_file(self):
        """Test reading and writing YAML files."""
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as temp:
            temp_path = temp.name

        try:
            # Test data
            config_data = {
                "server": {"host": "localhost", "port": 8080},
                "auth": {"enabled": True, "timeout": 30},
            }

            # Write and read back
            write_yaml_file(config_data, temp_path)
            read_data = read_yaml_file(temp_path)

            # Verify
            assert read_data["server"]["host"] == "localhost"
            assert read_data["server"]["port"] == 8080
            assert read_data["auth"]["enabled"] is True
            assert read_data["auth"]["timeout"] == 30

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_read_yaml_file_not_found(self):
        """Test reading a non-existent YAML file."""
        with pytest.raises(FileNotFoundError):
            read_yaml_file("nonexistent.yaml")

    def test_read_yaml_file_invalid(self):
        """Test reading an invalid YAML file."""
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as temp:
            temp_path = temp.name
            temp.write(b"invalid: yaml: content: - [")

        try:
            with pytest.raises(ValueError):
                read_yaml_file(temp_path)

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)


@pytest.mark.skipif(not TOML_AVAILABLE, reason="TOML library not installed")
class TestTomlReading:
    """Tests for TOML file reading functions."""

    def test_read_toml_file(self):
        """Test reading a TOML file."""
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as temp:
            temp_path = temp.name
            # Write a simple TOML file
            temp.write(
                b'[server]\nhost = "localhost"\nport = 8080\n\n[auth]\nenabled = true\n'
            )

        try:
            # Read the file
            config = read_toml_file(temp_path)

            # Verify
            assert config["server"]["host"] == "localhost"
            assert config["server"]["port"] == 8080
            assert config["auth"]["enabled"] is True

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_read_toml_file_not_found(self):
        """Test reading a non-existent TOML file."""
        with pytest.raises(FileNotFoundError):
            read_toml_file("nonexistent.toml")

    def test_read_toml_file_invalid(self):
        """Test reading an invalid TOML file."""
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as temp:
            temp_path = temp.name
            temp.write(b"invalid toml content")

        try:
            with pytest.raises(ValueError):
                read_toml_file(temp_path)

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)


@pytest.mark.skipif(not TOML_WRITE_AVAILABLE, reason="tomli_w not installed")
class TestTomlWriting:
    """Tests for TOML file writing functions."""

    def test_write_toml_file(self):
        """Test writing a TOML file."""
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as temp:
            temp_path = temp.name

        try:
            # Test data
            config_data = {
                "server": {"host": "localhost", "port": 8080},
                "auth": {"enabled": True, "timeout": 30},
            }

            # Write the file
            write_toml_file(config_data, temp_path)

            # Verify by reading it back
            if TOML_AVAILABLE:
                config = read_toml_file(temp_path)
                assert config["server"]["host"] == "localhost"
                assert config["server"]["port"] == 8080
                assert config["auth"]["enabled"] is True
                assert config["auth"]["timeout"] == 30

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
