"""Tests for basic_open_agent_tools.data.config_processing module."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from basic_open_agent_tools.data.config_processing import (
    merge_config_files,
    read_ini_file,
    read_toml_file,
    read_yaml_file,
    validate_config_schema,
    write_ini_file,
    write_toml_file,
    write_yaml_file,
)
from basic_open_agent_tools.exceptions import DataError


class TestReadYamlFile:
    """Test cases for read_yaml_file function."""

    def test_read_yaml_file_with_yaml_available(self, tmp_path: Path) -> None:
        """Test reading YAML file when PyYAML is available."""
        yaml_file = tmp_path / "test.yaml"
        yaml_content = """
database:
  host: localhost
  port: 5432
  enabled: true
app:
  name: "Test App"
  version: 1.2
"""
        yaml_file.write_text(yaml_content, encoding="utf-8")

        with patch("basic_open_agent_tools.data.config_processing.HAS_YAML", True):
            import yaml

            with patch("basic_open_agent_tools.data.config_processing.yaml", yaml):
                result = read_yaml_file(str(yaml_file))

        expected = {
            "database": {"host": "localhost", "port": 5432, "enabled": True},
            "app": {"name": "Test App", "version": 1.2},
        }
        assert result == expected

    def test_read_yaml_file_empty_file(self, tmp_path: Path) -> None:
        """Test reading empty YAML file."""
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text("", encoding="utf-8")

        with patch("basic_open_agent_tools.data.config_processing.HAS_YAML", True):
            import yaml

            with patch("basic_open_agent_tools.data.config_processing.yaml", yaml):
                result = read_yaml_file(str(yaml_file))

        assert result == {}

    def test_read_yaml_file_simple_data(self, tmp_path: Path) -> None:
        """Test reading YAML file with simple data types."""
        yaml_file = tmp_path / "simple.yaml"
        yaml_content = """
string_value: "hello"
int_value: 42
float_value: 3.14
bool_value: false
null_value: null
list_value:
  - item1
  - item2
  - item3
"""
        yaml_file.write_text(yaml_content, encoding="utf-8")

        with patch("basic_open_agent_tools.data.config_processing.HAS_YAML", True):
            import yaml

            with patch("basic_open_agent_tools.data.config_processing.yaml", yaml):
                result = read_yaml_file(str(yaml_file))

        expected = {
            "string_value": "hello",
            "int_value": 42,
            "float_value": 3.14,
            "bool_value": False,
            "null_value": None,
            "list_value": ["item1", "item2", "item3"],
        }
        assert result == expected

    def test_read_yaml_file_unicode_content(self, tmp_path: Path) -> None:
        """Test reading YAML file with Unicode content."""
        yaml_file = tmp_path / "unicode.yaml"
        yaml_content = """
chinese: "北京"
japanese: "東京"
russian: "Москва"
emoji: "🚀"
"""
        yaml_file.write_text(yaml_content, encoding="utf-8")

        with patch("basic_open_agent_tools.data.config_processing.HAS_YAML", True):
            import yaml

            with patch("basic_open_agent_tools.data.config_processing.yaml", yaml):
                result = read_yaml_file(str(yaml_file))

        expected = {
            "chinese": "北京",
            "japanese": "東京",
            "russian": "Москва",
            "emoji": "🚀",
        }
        assert result == expected

    def test_read_yaml_file_not_found(self) -> None:
        """Test error handling when YAML file doesn't exist."""
        with patch("basic_open_agent_tools.data.config_processing.HAS_YAML", True):
            with pytest.raises(FileNotFoundError, match="YAML file not found"):
                read_yaml_file("nonexistent.yaml")

    def test_read_yaml_file_invalid_yaml(self, tmp_path: Path) -> None:
        """Test error handling for invalid YAML syntax."""
        yaml_file = tmp_path / "invalid.yaml"
        yaml_content = """
invalid: yaml
  bad: indentation
    worse: nesting
"""
        yaml_file.write_text(yaml_content, encoding="utf-8")

        with patch("basic_open_agent_tools.data.config_processing.HAS_YAML", True):
            import yaml

            with patch("basic_open_agent_tools.data.config_processing.yaml", yaml):
                with pytest.raises(ValueError, match="Failed to parse YAML file"):
                    read_yaml_file(str(yaml_file))

    def test_read_yaml_file_yaml_not_available(self) -> None:
        """Test error when PyYAML is not installed."""
        with patch("basic_open_agent_tools.data.config_processing.HAS_YAML", False):
            with pytest.raises(DataError, match="YAML support not available"):
                read_yaml_file("test.yaml")

    def test_read_yaml_file_permission_error(self, tmp_path: Path) -> None:
        """Test error handling for permission denied."""
        yaml_file = tmp_path / "no_permission.yaml"
        yaml_file.write_text("test: value", encoding="utf-8")

        with patch("basic_open_agent_tools.data.config_processing.HAS_YAML", True):
            import yaml

            with patch("basic_open_agent_tools.data.config_processing.yaml", yaml):
                with patch(
                    "builtins.open", side_effect=PermissionError("Permission denied")
                ):
                    with pytest.raises(DataError, match="Failed to read YAML file"):
                        read_yaml_file(str(yaml_file))


class TestWriteYamlFile:
    """Test cases for write_yaml_file function."""

    def test_write_yaml_file_basic_data(self, tmp_path: Path) -> None:
        """Test writing basic data to YAML file."""
        yaml_file = tmp_path / "output.yaml"
        data = {
            "database": {"host": "localhost", "port": 5432},
            "app": {"name": "Test App", "debug": True},
        }

        with patch("basic_open_agent_tools.data.config_processing.HAS_YAML", True):
            import yaml

            with patch("basic_open_agent_tools.data.config_processing.yaml", yaml):
                write_yaml_file(data, str(yaml_file), skip_confirm=True)

        # Verify file was created and contains expected content
        assert yaml_file.exists()
        content = yaml_file.read_text(encoding="utf-8")
        assert "database:" in content
        assert "host: localhost" in content
        assert "port: 5432" in content

    def test_write_yaml_file_unicode_data(self, tmp_path: Path) -> None:
        """Test writing Unicode data to YAML file."""
        yaml_file = tmp_path / "unicode.yaml"
        data = {"cities": {"chinese": "北京", "japanese": "東京", "russian": "Москва"}}

        with patch("basic_open_agent_tools.data.config_processing.HAS_YAML", True):
            import yaml

            with patch("basic_open_agent_tools.data.config_processing.yaml", yaml):
                write_yaml_file(data, str(yaml_file), skip_confirm=True)

        assert yaml_file.exists()
        content = yaml_file.read_text(encoding="utf-8")
        assert "北京" in content

    def test_write_yaml_file_complex_data(self, tmp_path: Path) -> None:
        """Test writing complex nested data structures."""
        yaml_file = tmp_path / "complex.yaml"
        data = {
            "servers": [
                {"name": "web1", "ip": "192.168.1.10", "roles": ["web", "api"]},
                {"name": "db1", "ip": "192.168.1.20", "roles": ["database"]},
            ],
            "config": {
                "timeout": 30,
                "retries": 3,
                "options": {"ssl": True, "compression": False},
            },
        }

        with patch("basic_open_agent_tools.data.config_processing.HAS_YAML", True):
            import yaml

            with patch("basic_open_agent_tools.data.config_processing.yaml", yaml):
                write_yaml_file(data, str(yaml_file), skip_confirm=True)

        assert yaml_file.exists()
        content = yaml_file.read_text(encoding="utf-8")
        assert "servers:" in content
        assert "web1" in content

    def test_write_yaml_file_empty_data(self, tmp_path: Path) -> None:
        """Test writing empty dictionary."""
        yaml_file = tmp_path / "empty.yaml"
        data = {}

        with patch("basic_open_agent_tools.data.config_processing.HAS_YAML", True):
            import yaml

            with patch("basic_open_agent_tools.data.config_processing.yaml", yaml):
                write_yaml_file(data, str(yaml_file), skip_confirm=True)

        assert yaml_file.exists()
        content = yaml_file.read_text(encoding="utf-8")
        assert content.strip() == "{}"

    def test_write_yaml_file_yaml_not_available(self) -> None:
        """Test error when PyYAML is not installed."""
        with patch("basic_open_agent_tools.data.config_processing.HAS_YAML", False):
            with pytest.raises(DataError, match="YAML support not available"):
                write_yaml_file({}, "test.yaml", skip_confirm=True)

    def test_write_yaml_file_permission_error(self, tmp_path: Path) -> None:
        """Test error handling for permission denied."""
        yaml_file = tmp_path / "no_permission.yaml"

        with patch("basic_open_agent_tools.data.config_processing.HAS_YAML", True):
            import yaml

            with patch("basic_open_agent_tools.data.config_processing.yaml", yaml):
                with patch(
                    "builtins.open", side_effect=PermissionError("Permission denied")
                ):
                    with pytest.raises(DataError, match="Failed to write YAML file"):
                        write_yaml_file({"test": "data"}, str(yaml_file), skip_confirm=True)


class TestReadTomlFile:
    """Test cases for read_toml_file function."""

    def test_read_toml_file_basic_data(self, tmp_path: Path) -> None:
        """Test reading basic TOML file."""
        toml_file = tmp_path / "test.toml"
        toml_content = """
[database]
host = "localhost"
port = 5432
enabled = true

[app]
name = "Test App"
version = 1.2
"""
        toml_file.write_text(toml_content, encoding="utf-8")

        with patch("basic_open_agent_tools.data.config_processing.HAS_TOML", True):
            import tomli

            with patch("basic_open_agent_tools.data.config_processing.tomli", tomli):
                result = read_toml_file(str(toml_file))

        expected = {
            "database": {"host": "localhost", "port": 5432, "enabled": True},
            "app": {"name": "Test App", "version": 1.2},
        }
        assert result == expected

    def test_read_toml_file_arrays_and_inline_tables(self, tmp_path: Path) -> None:
        """Test reading TOML with arrays and inline tables."""
        toml_file = tmp_path / "complex.toml"
        toml_content = """
servers = ["web1", "web2", "db1"]

[database]
connection = { host = "localhost", port = 5432, ssl = true }

[[products]]
name = "Hammer"
sku = 738594937

[[products]]
name = "Nail"
sku = 284758393
"""
        toml_file.write_text(toml_content, encoding="utf-8")

        with patch("basic_open_agent_tools.data.config_processing.HAS_TOML", True):
            import tomli

            with patch("basic_open_agent_tools.data.config_processing.tomli", tomli):
                result = read_toml_file(str(toml_file))

        assert "servers" in result
        assert result["servers"] == ["web1", "web2", "db1"]
        assert "database" in result
        assert result["database"]["connection"]["host"] == "localhost"

    def test_read_toml_file_unicode_content(self, tmp_path: Path) -> None:
        """Test reading TOML file with Unicode content."""
        toml_file = tmp_path / "unicode.toml"
        toml_content = """
chinese = "北京"
japanese = "東京"
russian = "Москва"
emoji = "🚀"
"""
        toml_file.write_text(toml_content, encoding="utf-8")

        with patch("basic_open_agent_tools.data.config_processing.HAS_TOML", True):
            import tomli

            with patch("basic_open_agent_tools.data.config_processing.tomli", tomli):
                result = read_toml_file(str(toml_file))

        expected = {
            "chinese": "北京",
            "japanese": "東京",
            "russian": "Москва",
            "emoji": "🚀",
        }
        assert result == expected

    def test_read_toml_file_empty_file(self, tmp_path: Path) -> None:
        """Test reading empty TOML file."""
        toml_file = tmp_path / "empty.toml"
        toml_file.write_text("", encoding="utf-8")

        with patch("basic_open_agent_tools.data.config_processing.HAS_TOML", True):
            import tomli

            with patch("basic_open_agent_tools.data.config_processing.tomli", tomli):
                result = read_toml_file(str(toml_file))

        assert result == {}

    def test_read_toml_file_not_found(self) -> None:
        """Test error handling when TOML file doesn't exist."""
        with patch("basic_open_agent_tools.data.config_processing.HAS_TOML", True):
            with pytest.raises(FileNotFoundError, match="TOML file not found"):
                read_toml_file("nonexistent.toml")

    def test_read_toml_file_invalid_toml(self, tmp_path: Path) -> None:
        """Test error handling for invalid TOML syntax."""
        toml_file = tmp_path / "invalid.toml"
        toml_content = """
[database
host = "localhost"  # Missing closing bracket
"""
        toml_file.write_text(toml_content, encoding="utf-8")

        with patch("basic_open_agent_tools.data.config_processing.HAS_TOML", True):
            import tomli

            with patch("basic_open_agent_tools.data.config_processing.tomli", tomli):
                with pytest.raises(ValueError, match="Failed to parse TOML file"):
                    read_toml_file(str(toml_file))

    def test_read_toml_file_toml_not_available(self) -> None:
        """Test error when TOML support is not installed."""
        with patch("basic_open_agent_tools.data.config_processing.HAS_TOML", False):
            with pytest.raises(DataError, match="TOML support not available"):
                read_toml_file("test.toml")

    def test_read_toml_file_permission_error(self, tmp_path: Path) -> None:
        """Test error handling for permission denied."""
        toml_file = tmp_path / "no_permission.toml"
        toml_file.write_text("test = 'value'", encoding="utf-8")

        with patch("basic_open_agent_tools.data.config_processing.HAS_TOML", True):
            import tomli

            with patch("basic_open_agent_tools.data.config_processing.tomli", tomli):
                with patch(
                    "builtins.open", side_effect=PermissionError("Permission denied")
                ):
                    with pytest.raises(DataError, match="Failed to read TOML file"):
                        read_toml_file(str(toml_file))


class TestWriteTomlFile:
    """Test cases for write_toml_file function."""

    def test_write_toml_file_basic_data(self, tmp_path: Path) -> None:
        """Test writing basic data to TOML file."""
        toml_file = tmp_path / "output.toml"
        data = {
            "database": {"host": "localhost", "port": 5432},
            "app": {"name": "Test App", "debug": True},
        }

        with patch("basic_open_agent_tools.data.config_processing.HAS_TOML", True):
            import tomli_w

            with patch(
                "basic_open_agent_tools.data.config_processing.tomli_w", tomli_w
            ):
                write_toml_file(data, str(toml_file))

        # Verify file was created
        assert toml_file.exists()
        content = toml_file.read_text(encoding="utf-8")
        assert "[database]" in content
        assert "host = " in content

    def test_write_toml_file_unicode_data(self, tmp_path: Path) -> None:
        """Test writing Unicode data to TOML file."""
        toml_file = tmp_path / "unicode.toml"
        data = {"cities": {"chinese": "北京", "japanese": "東京"}}

        with patch("basic_open_agent_tools.data.config_processing.HAS_TOML", True):
            import tomli_w

            with patch(
                "basic_open_agent_tools.data.config_processing.tomli_w", tomli_w
            ):
                write_toml_file(data, str(toml_file))

        assert toml_file.exists()

    def test_write_toml_file_complex_data(self, tmp_path: Path) -> None:
        """Test writing complex nested data structures."""
        toml_file = tmp_path / "complex.toml"
        data = {
            "servers": ["web1", "web2"],
            "database": {"host": "localhost", "port": 5432, "ssl": True},
        }

        with patch("basic_open_agent_tools.data.config_processing.HAS_TOML", True):
            import tomli_w

            with patch(
                "basic_open_agent_tools.data.config_processing.tomli_w", tomli_w
            ):
                write_toml_file(data, str(toml_file))

        assert toml_file.exists()

    def test_write_toml_file_empty_data(self, tmp_path: Path) -> None:
        """Test writing empty dictionary."""
        toml_file = tmp_path / "empty.toml"
        data = {}

        with patch("basic_open_agent_tools.data.config_processing.HAS_TOML", True):
            import tomli_w

            with patch(
                "basic_open_agent_tools.data.config_processing.tomli_w", tomli_w
            ):
                write_toml_file(data, str(toml_file))

        assert toml_file.exists()

    def test_write_toml_file_toml_not_available(self) -> None:
        """Test error when TOML support is not installed."""
        with patch("basic_open_agent_tools.data.config_processing.HAS_TOML", False):
            with pytest.raises(DataError, match="TOML support not available"):
                write_toml_file({}, "test.toml")

    def test_write_toml_file_permission_error(self, tmp_path: Path) -> None:
        """Test error handling for permission denied."""
        toml_file = tmp_path / "no_permission.toml"

        with patch("basic_open_agent_tools.data.config_processing.HAS_TOML", True):
            import tomli_w

            with patch(
                "basic_open_agent_tools.data.config_processing.tomli_w", tomli_w
            ):
                with patch(
                    "builtins.open", side_effect=PermissionError("Permission denied")
                ):
                    with pytest.raises(DataError, match="Failed to write TOML file"):
                        write_toml_file({"test": "data"}, str(toml_file))


class TestReadIniFile:
    """Test cases for read_ini_file function."""

    def test_read_ini_file_basic_data(self, tmp_path: Path) -> None:
        """Test reading basic INI file."""
        ini_file = tmp_path / "test.ini"
        ini_content = """
[database]
host = localhost
port = 5432
enabled = true

[app]
name = Test App
version = 1.2
debug = false
"""
        ini_file.write_text(ini_content, encoding="utf-8")

        result = read_ini_file(str(ini_file))

        expected = {
            "database": {"host": "localhost", "port": "5432", "enabled": "true"},
            "app": {"name": "Test App", "version": "1.2", "debug": "false"},
        }
        assert result == expected

    def test_read_ini_file_multiple_sections(self, tmp_path: Path) -> None:
        """Test reading INI file with multiple sections."""
        ini_file = tmp_path / "multi.ini"
        ini_content = """
[section1]
key1 = value1
key2 = value2

[section2]
keyA = valueA
keyB = valueB

[section3]
setting1 = enabled
setting2 = disabled
"""
        ini_file.write_text(ini_content, encoding="utf-8")

        result = read_ini_file(str(ini_file))

        assert len(result) == 3
        assert "section1" in result
        assert "section2" in result
        assert "section3" in result
        assert result["section1"]["key1"] == "value1"
        assert result["section2"]["keya"] == "valueA"

    def test_read_ini_file_unicode_content(self, tmp_path: Path) -> None:
        """Test reading INI file with Unicode content."""
        ini_file = tmp_path / "unicode.ini"
        ini_content = """
[cities]
chinese = 北京
japanese = 東京
russian = Москва
"""
        ini_file.write_text(ini_content, encoding="utf-8")

        result = read_ini_file(str(ini_file))

        expected = {
            "cities": {"chinese": "北京", "japanese": "東京", "russian": "Москва"}
        }
        assert result == expected

    def test_read_ini_file_empty_file(self, tmp_path: Path) -> None:
        """Test reading empty INI file."""
        ini_file = tmp_path / "empty.ini"
        ini_file.write_text("", encoding="utf-8")

        result = read_ini_file(str(ini_file))

        assert result == {}

    def test_read_ini_file_only_values_no_sections(self, tmp_path: Path) -> None:
        """Test reading INI file with values but no sections."""
        ini_file = tmp_path / "nosections.ini"
        ini_content = """# Just comments and whitespace

"""
        ini_file.write_text(ini_content, encoding="utf-8")

        result = read_ini_file(str(ini_file))

        assert result == {}

    def test_read_ini_file_not_found(self) -> None:
        """Test error handling when INI file doesn't exist."""
        with pytest.raises(FileNotFoundError, match="INI file not found"):
            read_ini_file("nonexistent.ini")

    def test_read_ini_file_malformed_ini(self, tmp_path: Path) -> None:
        """Test error handling for malformed INI file."""
        ini_file = tmp_path / "malformed.ini"
        ini_content = """
[section1]
key without value
"""
        ini_file.write_text(ini_content, encoding="utf-8")

        with pytest.raises(DataError, match="Failed to parse INI file"):
            read_ini_file(str(ini_file))

    def test_read_ini_file_permission_error(self, tmp_path: Path) -> None:
        """Test error handling for permission denied."""
        ini_file = tmp_path / "no_permission.ini"
        ini_file.write_text("[test]\nkey=value", encoding="utf-8")

        with patch("os.path.isfile", return_value=True):
            with patch(
                "configparser.ConfigParser.read",
                side_effect=PermissionError("Permission denied"),
            ):
                with pytest.raises(DataError, match="Failed to read INI file"):
                    read_ini_file(str(ini_file))


class TestWriteIniFile:
    """Test cases for write_ini_file function."""

    def test_write_ini_file_basic_data(self, tmp_path: Path) -> None:
        """Test writing basic data to INI file."""
        ini_file = tmp_path / "output.ini"
        data = {
            "database": {"host": "localhost", "port": "5432"},
            "app": {"name": "Test App", "debug": "true"},
        }

        write_ini_file(data, str(ini_file))

        # Verify file was created and contains expected content
        assert ini_file.exists()
        content = ini_file.read_text(encoding="utf-8")
        assert "[database]" in content
        assert "host = localhost" in content
        assert "[app]" in content

    def test_write_ini_file_unicode_data(self, tmp_path: Path) -> None:
        """Test writing Unicode data to INI file."""
        ini_file = tmp_path / "unicode.ini"
        data = {"cities": {"chinese": "北京", "japanese": "東京"}}

        write_ini_file(data, str(ini_file))

        assert ini_file.exists()
        content = ini_file.read_text(encoding="utf-8")
        assert "北京" in content

    def test_write_ini_file_mixed_value_types(self, tmp_path: Path) -> None:
        """Test writing mixed value types (all converted to strings)."""
        ini_file = tmp_path / "mixed.ini"
        data = {
            "settings": {
                "string_val": "hello",
                "int_val": 42,
                "float_val": 3.14,
                "bool_val": True,
            }
        }

        write_ini_file(data, str(ini_file))

        assert ini_file.exists()
        content = ini_file.read_text(encoding="utf-8")
        assert "string_val = hello" in content
        assert "int_val = 42" in content
        assert "float_val = 3.14" in content
        assert "bool_val = True" in content

    def test_write_ini_file_empty_data(self, tmp_path: Path) -> None:
        """Test writing empty dictionary."""
        ini_file = tmp_path / "empty.ini"
        data = {}

        write_ini_file(data, str(ini_file))

        assert ini_file.exists()
        content = ini_file.read_text(encoding="utf-8").strip()
        # Empty data should create empty file or just whitespace
        assert len(content) == 0 or content.isspace()

    def test_write_ini_file_non_dict_section_data(self, tmp_path: Path) -> None:
        """Test writing data where section values are not dictionaries."""
        ini_file = tmp_path / "non_dict.ini"
        data = {"section1": "not_a_dict", "section2": {"key": "value"}}

        write_ini_file(data, str(ini_file))

        assert ini_file.exists()
        content = ini_file.read_text(encoding="utf-8")
        # Should still create sections, non-dict values are skipped
        assert "[section1]" in content
        assert "[section2]" in content

    def test_write_ini_file_permission_error(self, tmp_path: Path) -> None:
        """Test error handling for permission denied."""
        ini_file = tmp_path / "no_permission.ini"

        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with pytest.raises(DataError, match="Failed to write INI file"):
                write_ini_file({"test": {"key": "value"}}, str(ini_file))


class TestValidateConfigSchema:
    """Test cases for validate_config_schema function."""

    def test_validate_config_schema_valid_config(self) -> None:
        """Test validation of valid configuration."""
        config = {"host": "localhost", "port": 5432, "debug": True, "name": "test_app"}
        schema = {
            "host": {"type": str, "required": True},
            "port": {"type": int, "required": True},
            "debug": {"type": bool, "required": False},
            "name": {"type": str, "required": False},
        }

        errors = validate_config_schema(config, schema)

        assert errors == []

    def test_validate_config_schema_missing_required_fields(self) -> None:
        """Test validation with missing required fields."""
        config = {
            "host": "localhost"
            # Missing required port
        }
        schema = {
            "host": {"type": str, "required": True},
            "port": {"type": int, "required": True},
        }

        errors = validate_config_schema(config, schema)

        assert len(errors) == 1
        assert "Required field 'port' is missing" in errors[0]

    def test_validate_config_schema_type_mismatches(self) -> None:
        """Test validation with type mismatches."""
        config = {
            "host": "localhost",
            "port": "5432",  # Should be int
            "debug": "true",  # Should be bool
        }
        schema = {
            "host": {"type": str, "required": True},
            "port": {"type": int, "required": True},
            "debug": {"type": bool, "required": False},
        }

        errors = validate_config_schema(config, schema)

        assert len(errors) == 2
        assert any("port" in error and "incorrect type" in error for error in errors)
        assert any("debug" in error and "incorrect type" in error for error in errors)

    def test_validate_config_schema_allowed_values(self) -> None:
        """Test validation with allowed values constraint."""
        config = {"log_level": "DEBUG", "environment": "production"}
        schema = {
            "log_level": {
                "type": str,
                "required": True,
                "allowed_values": ["DEBUG", "INFO", "WARNING", "ERROR"],
            },
            "environment": {
                "type": str,
                "required": True,
                "allowed_values": ["development", "staging", "production"],
            },
        }

        errors = validate_config_schema(config, schema)

        assert errors == []

    def test_validate_config_schema_invalid_allowed_values(self) -> None:
        """Test validation with invalid allowed values."""
        config = {
            "log_level": "TRACE",  # Not in allowed values
            "environment": "prod",  # Not in allowed values
        }
        schema = {
            "log_level": {
                "type": str,
                "required": True,
                "allowed_values": ["DEBUG", "INFO", "WARNING", "ERROR"],
            },
            "environment": {
                "type": str,
                "required": True,
                "allowed_values": ["development", "staging", "production"],
            },
        }

        errors = validate_config_schema(config, schema)

        assert len(errors) == 2
        assert any(
            "log_level" in error and "invalid value" in error for error in errors
        )
        assert any(
            "environment" in error and "invalid value" in error for error in errors
        )

    def test_validate_config_schema_unknown_fields(self) -> None:
        """Test validation with unknown fields in configuration."""
        config = {
            "host": "localhost",
            "port": 5432,
            "unknown_field": "value",
            "another_unknown": 123,
        }
        schema = {
            "host": {"type": str, "required": True},
            "port": {"type": int, "required": True},
        }

        errors = validate_config_schema(config, schema)

        assert len(errors) == 2
        assert any(
            "unknown_field" in error and "Unknown field" in error for error in errors
        )
        assert any(
            "another_unknown" in error and "Unknown field" in error for error in errors
        )

    def test_validate_config_schema_optional_fields(self) -> None:
        """Test validation with optional fields."""
        config = {
            "host": "localhost",
            "port": 5432,
            # Optional fields not provided
        }
        schema = {
            "host": {"type": str, "required": True},
            "port": {"type": int, "required": True},
            "timeout": {"type": int, "required": False},
            "ssl": {"type": bool, "required": False},
        }

        errors = validate_config_schema(config, schema)

        assert errors == []

    def test_validate_config_schema_no_type_specified(self) -> None:
        """Test validation when schema field has no type specified."""
        config = {"field1": "any_value", "field2": 42}
        schema = {
            "field1": {"required": True},  # No type specified
            "field2": {"required": True},  # No type specified
        }

        errors = validate_config_schema(config, schema)

        assert errors == []

    def test_validate_config_schema_empty_config_empty_schema(self) -> None:
        """Test validation with empty config and schema."""
        config = {}
        schema = {}

        errors = validate_config_schema(config, schema)

        assert errors == []

    def test_validate_config_schema_complex_types(self) -> None:
        """Test validation with complex data types."""
        config = {
            "servers": ["web1", "web2"],
            "database_config": {"host": "localhost", "port": 5432},
            "feature_flags": {"new_ui": True, "beta_api": False},
        }
        schema = {
            "servers": {"type": list, "required": True},
            "database_config": {"type": dict, "required": True},
            "feature_flags": {"type": dict, "required": False},
        }

        errors = validate_config_schema(config, schema)

        assert errors == []


class TestMergeConfigFiles:
    """Test cases for merge_config_files function."""

    def test_merge_config_files_yaml_single_file(self, tmp_path: Path) -> None:
        """Test merging single YAML configuration file."""
        yaml_file = tmp_path / "config.yaml"
        yaml_content = """
database:
  host: localhost
  port: 5432
app:
  name: "Test App"
"""
        yaml_file.write_text(yaml_content, encoding="utf-8")

        with patch("basic_open_agent_tools.data.config_processing.HAS_YAML", True):
            import yaml

            with patch("basic_open_agent_tools.data.config_processing.yaml", yaml):
                result = merge_config_files([str(yaml_file)], "yaml")

        expected = {
            "database": {"host": "localhost", "port": 5432},
            "app": {"name": "Test App"},
        }
        assert result == expected

    def test_merge_config_files_yaml_multiple_files(self, tmp_path: Path) -> None:
        """Test merging multiple YAML configuration files."""
        base_file = tmp_path / "base.yaml"
        override_file = tmp_path / "override.yaml"

        base_content = """
database:
  host: localhost
  port: 5432
  timeout: 30
app:
  name: "Base App"
  debug: false
"""
        override_content = """
database:
  host: production-db
  ssl: true
app:
  debug: true
logging:
  level: INFO
"""

        base_file.write_text(base_content, encoding="utf-8")
        override_file.write_text(override_content, encoding="utf-8")

        with patch("basic_open_agent_tools.data.config_processing.HAS_YAML", True):
            import yaml

            with patch("basic_open_agent_tools.data.config_processing.yaml", yaml):
                result = merge_config_files(
                    [str(base_file), str(override_file)], "yaml"
                )

        # Should deep merge with override taking precedence
        expected = {
            "database": {
                "host": "production-db",  # Overridden
                "port": 5432,  # From base
                "timeout": 30,  # From base
                "ssl": True,  # Added from override
            },
            "app": {
                "name": "Base App",  # From base
                "debug": True,  # Overridden
            },
            "logging": {
                "level": "INFO"  # Added from override
            },
        }
        assert result == expected

    def test_merge_config_files_toml_files(self, tmp_path: Path) -> None:
        """Test merging TOML configuration files."""
        toml_file1 = tmp_path / "config1.toml"
        toml_file2 = tmp_path / "config2.toml"

        toml_content1 = """
[database]
host = "localhost"
port = 5432

[app]
name = "App1"
"""
        toml_content2 = """
[database]
ssl = true

[app]
version = "2.0"

[cache]
enabled = true
"""

        toml_file1.write_text(toml_content1, encoding="utf-8")
        toml_file2.write_text(toml_content2, encoding="utf-8")

        with patch("basic_open_agent_tools.data.config_processing.HAS_TOML", True):
            import tomli

            with patch("basic_open_agent_tools.data.config_processing.tomli", tomli):
                result = merge_config_files([str(toml_file1), str(toml_file2)], "toml")

        expected = {
            "database": {"host": "localhost", "port": 5432, "ssl": True},
            "app": {"name": "App1", "version": "2.0"},
            "cache": {"enabled": True},
        }
        assert result == expected

    def test_merge_config_files_ini_files(self, tmp_path: Path) -> None:
        """Test merging INI configuration files."""
        ini_file1 = tmp_path / "config1.ini"
        ini_file2 = tmp_path / "config2.ini"

        ini_content1 = """
[database]
host = localhost
port = 5432

[app]
name = App1
"""
        ini_content2 = """
[database]
ssl = true

[app]
version = 2.0

[cache]
enabled = true
"""

        ini_file1.write_text(ini_content1, encoding="utf-8")
        ini_file2.write_text(ini_content2, encoding="utf-8")

        result = merge_config_files([str(ini_file1), str(ini_file2)], "ini")

        expected = {
            "database": {"host": "localhost", "port": "5432", "ssl": "true"},
            "app": {"name": "App1", "version": "2.0"},
            "cache": {"enabled": "true"},
        }
        assert result == expected

    def test_merge_config_files_json_files(self, tmp_path: Path) -> None:
        """Test merging JSON configuration files."""
        json_file1 = tmp_path / "config1.json"
        json_file2 = tmp_path / "config2.json"

        config1 = {
            "database": {"host": "localhost", "port": 5432},
            "app": {"name": "App1", "debug": False},
        }
        config2 = {
            "database": {"ssl": True},
            "app": {"debug": True, "version": "2.0"},
            "logging": {"level": "INFO"},
        }

        json_file1.write_text(json.dumps(config1), encoding="utf-8")
        json_file2.write_text(json.dumps(config2), encoding="utf-8")

        result = merge_config_files([str(json_file1), str(json_file2)], "json")

        expected = {
            "database": {"host": "localhost", "port": 5432, "ssl": True},
            "app": {"name": "App1", "debug": True, "version": "2.0"},
            "logging": {"level": "INFO"},
        }
        assert result == expected

    def test_merge_config_files_empty_list(self) -> None:
        """Test error handling for empty config paths list."""
        with pytest.raises(ValueError, match="No configuration files provided"):
            merge_config_files([], "yaml")

    def test_merge_config_files_invalid_format(self, tmp_path: Path) -> None:
        """Test error handling for invalid format type."""
        config_file = tmp_path / "config.txt"
        config_file.write_text("test", encoding="utf-8")

        with pytest.raises(ValueError, match="format_type must be one of"):
            merge_config_files([str(config_file)], "invalid_format")

    def test_merge_config_files_missing_file(self) -> None:
        """Test error handling for missing configuration file."""
        with patch("basic_open_agent_tools.data.config_processing.HAS_YAML", True):
            with pytest.raises(FileNotFoundError):
                merge_config_files(["nonexistent.yaml"], "yaml")

    def test_merge_config_files_deep_merge_behavior(self, tmp_path: Path) -> None:
        """Test that deep merging works correctly for nested structures."""
        json_file1 = tmp_path / "deep1.json"
        json_file2 = tmp_path / "deep2.json"

        config1 = {
            "level1": {"level2": {"key1": "value1", "key2": "value2"}, "other": "data"}
        }
        config2 = {
            "level1": {
                "level2": {"key2": "overridden", "key3": "value3"},
                "new_key": "new_value",
            }
        }

        json_file1.write_text(json.dumps(config1), encoding="utf-8")
        json_file2.write_text(json.dumps(config2), encoding="utf-8")

        result = merge_config_files([str(json_file1), str(json_file2)], "json")

        expected = {
            "level1": {
                "level2": {
                    "key1": "value1",  # From first file
                    "key2": "overridden",  # Overridden by second file
                    "key3": "value3",  # Added by second file
                },
                "other": "data",  # From first file
                "new_key": "new_value",  # Added by second file
            }
        }
        assert result == expected


class TestConfigProcessingIntegration:
    """Integration tests for config processing functions working together."""

    def test_yaml_round_trip(self, tmp_path: Path) -> None:
        """Test YAML write and read round trip."""
        yaml_file = tmp_path / "roundtrip.yaml"
        original_data = {
            "database": {"host": "localhost", "port": 5432, "ssl": True},
            "app": {"name": "Test App", "version": 1.0, "features": ["auth", "api"]},
        }

        with patch("basic_open_agent_tools.data.config_processing.HAS_YAML", True):
            import yaml

            with patch("basic_open_agent_tools.data.config_processing.yaml", yaml):
                # Write then read back
                write_yaml_file(original_data, str(yaml_file))
                result = read_yaml_file(str(yaml_file))

        assert result == original_data

    def test_toml_round_trip(self, tmp_path: Path) -> None:
        """Test TOML write and read round trip."""
        toml_file = tmp_path / "roundtrip.toml"
        original_data = {
            "database": {"host": "localhost", "port": 5432, "ssl": True},
            "app": {"name": "Test App", "version": 1.0},
        }

        with patch("basic_open_agent_tools.data.config_processing.HAS_TOML", True):
            import tomli
            import tomli_w

            with patch("basic_open_agent_tools.data.config_processing.tomli", tomli):
                with patch(
                    "basic_open_agent_tools.data.config_processing.tomli_w", tomli_w
                ):
                    # Write then read back
                    write_toml_file(original_data, str(toml_file))
                    result = read_toml_file(str(toml_file))

        assert result == original_data

    def test_ini_round_trip(self, tmp_path: Path) -> None:
        """Test INI write and read round trip."""
        ini_file = tmp_path / "roundtrip.ini"
        original_data = {
            "database": {"host": "localhost", "port": "5432"},
            "app": {"name": "Test App", "version": "1.0"},
        }

        # Write then read back
        write_ini_file(original_data, str(ini_file))
        result = read_ini_file(str(ini_file))

        assert result == original_data

    def test_validate_and_merge_workflow(self, tmp_path: Path) -> None:
        """Test complete workflow: merge configs then validate."""
        config1_file = tmp_path / "base.json"
        config2_file = tmp_path / "override.json"

        config1 = {"host": "localhost", "port": 5432, "debug": False}
        config2 = {"port": 8080, "ssl": True}

        config1_file.write_text(json.dumps(config1), encoding="utf-8")
        config2_file.write_text(json.dumps(config2), encoding="utf-8")

        # Merge configs
        merged = merge_config_files([str(config1_file), str(config2_file)], "json")

        # Validate merged config
        schema = {
            "host": {"type": str, "required": True},
            "port": {"type": int, "required": True},
            "debug": {"type": bool, "required": False},
            "ssl": {"type": bool, "required": False},
        }

        errors = validate_config_schema(merged, schema)

        assert errors == []
        assert merged["host"] == "localhost"
        assert merged["port"] == 8080  # Overridden
        assert merged["ssl"] is True  # Added
        assert merged["debug"] is False  # From base

    def test_multi_format_config_validation(self, tmp_path: Path) -> None:
        """Test validation workflow with different config formats."""
        # Create configs in different formats with same schema
        schema = {
            "database_host": {"type": str, "required": True},
            "database_port": {"type": int, "required": True},
            "app_debug": {"type": bool, "required": False},
        }

        # YAML config
        yaml_file = tmp_path / "config.yaml"
        yaml_content = """
database_host: localhost
database_port: 5432
app_debug: true
"""
        yaml_file.write_text(yaml_content, encoding="utf-8")

        # INI config
        ini_file = tmp_path / "config.ini"
        ini_content = """
[main]
database_host = localhost
database_port = 5432
app_debug = false
"""
        ini_file.write_text(ini_content, encoding="utf-8")

        # Test YAML validation
        with patch("basic_open_agent_tools.data.config_processing.HAS_YAML", True):
            import yaml

            with patch("basic_open_agent_tools.data.config_processing.yaml", yaml):
                yaml_config = read_yaml_file(str(yaml_file))
                yaml_errors = validate_config_schema(yaml_config, schema)
                assert yaml_errors == []

        # Test INI validation (needs to extract from 'main' section)
        ini_config = read_ini_file(str(ini_file))
        main_config = {
            "database_host": ini_config["main"]["database_host"],
            "database_port": int(ini_config["main"]["database_port"]),  # Convert to int
            "app_debug": ini_config["main"]["app_debug"].lower()
            == "true",  # Convert to bool
        }
        ini_errors = validate_config_schema(main_config, schema)
        assert ini_errors == []
