"""Tests for environment variable operations."""

import pytest
import os
from unittest.mock import patch

from basic_open_agent_tools.system.environment import (
    get_env_var,
    set_env_var,
    list_env_vars,
)
from basic_open_agent_tools.exceptions import BasicAgentToolsError


class TestGetEnvVar:
    """Test the get_env_var function."""

    def test_invalid_variable_name(self):
        """Test error handling for invalid variable names."""
        with pytest.raises(BasicAgentToolsError, match="Variable name must be a non-empty string"):
            get_env_var("")

        with pytest.raises(BasicAgentToolsError, match="Variable name must be a non-empty string"):
            get_env_var(None)

        with pytest.raises(BasicAgentToolsError, match="Variable name must be a non-empty string"):
            get_env_var("   ")

    def test_existing_environment_variable(self):
        """Test getting an existing environment variable."""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}, clear=False):
            result = get_env_var("TEST_VAR")

            assert result["variable_name"] == "TEST_VAR"
            assert result["value"] == "test_value"
            assert result["exists"] is True
            assert result["is_empty"] is False

    def test_nonexistent_environment_variable(self):
        """Test getting a non-existent environment variable."""
        # Make sure the variable doesn't exist
        if "NONEXISTENT_VAR" in os.environ:
            del os.environ["NONEXISTENT_VAR"]

        result = get_env_var("NONEXISTENT_VAR")

        assert result["variable_name"] == "NONEXISTENT_VAR"
        assert result["value"] == ""
        assert result["exists"] is False
        assert result["is_empty"] is True

    def test_empty_environment_variable(self):
        """Test getting an environment variable with empty value."""
        with patch.dict(os.environ, {"EMPTY_VAR": ""}, clear=False):
            result = get_env_var("EMPTY_VAR")

            assert result["variable_name"] == "EMPTY_VAR"
            assert result["value"] == ""
            assert result["exists"] is True
            assert result["is_empty"] is True

    def test_whitespace_handling(self):
        """Test handling of variable names with whitespace."""
        with patch.dict(os.environ, {"WHITESPACE_VAR": "value"}, clear=False):
            result = get_env_var("  WHITESPACE_VAR  ")

            assert result["variable_name"] == "WHITESPACE_VAR"
            assert result["value"] == "value"
            assert result["exists"] is True


class TestSetEnvVar:
    """Test the set_env_var function."""

    def test_invalid_variable_name(self):
        """Test error handling for invalid variable names."""
        with pytest.raises(BasicAgentToolsError, match="Variable name must be a non-empty string"):
            set_env_var("", "value")

        with pytest.raises(BasicAgentToolsError, match="Variable name must be a non-empty string"):
            set_env_var(None, "value")

    def test_invalid_value_type(self):
        """Test error handling for invalid value types."""
        with pytest.raises(BasicAgentToolsError, match="Value must be a string"):
            set_env_var("TEST_VAR", 123)

        with pytest.raises(BasicAgentToolsError, match="Value must be a string"):
            set_env_var("TEST_VAR", None)

    def test_set_new_environment_variable(self):
        """Test setting a new environment variable."""
        # Ensure variable doesn't exist
        var_name = "NEW_TEST_VAR"
        if var_name in os.environ:
            del os.environ[var_name]

        result = set_env_var(var_name, "new_value")

        assert result["variable_name"] == var_name
        assert result["new_value"] == "new_value"
        assert result["previous_value"] == ""
        assert result["had_previous_value"] is False
        assert result["operation"] == "set"
        assert result["success"] is True

        # Verify it was actually set
        assert os.environ[var_name] == "new_value"

        # Clean up
        if var_name in os.environ:
            del os.environ[var_name]

    def test_overwrite_existing_environment_variable(self):
        """Test overwriting an existing environment variable."""
        var_name = "EXISTING_TEST_VAR"
        original_value = "original_value"
        new_value = "new_value"

        with patch.dict(os.environ, {var_name: original_value}, clear=False):
            result = set_env_var(var_name, new_value)

            assert result["variable_name"] == var_name
            assert result["new_value"] == new_value
            assert result["previous_value"] == original_value
            assert result["had_previous_value"] is True
            assert result["operation"] == "set"
            assert result["success"] is True

            # Verify it was actually updated
            assert os.environ[var_name] == new_value

    def test_set_empty_value(self):
        """Test setting an environment variable to empty string."""
        var_name = "EMPTY_TEST_VAR"

        result = set_env_var(var_name, "")

        assert result["new_value"] == ""
        assert result["success"] is True
        assert os.environ[var_name] == ""

        # Clean up
        if var_name in os.environ:
            del os.environ[var_name]

    def test_whitespace_handling_in_names(self):
        """Test handling of whitespace in variable names."""
        result = set_env_var("  WHITESPACE_NAME  ", "test_value")

        assert result["variable_name"] == "WHITESPACE_NAME"
        assert os.environ["WHITESPACE_NAME"] == "test_value"

        # Clean up
        if "WHITESPACE_NAME" in os.environ:
            del os.environ["WHITESPACE_NAME"]


class TestListEnvVars:
    """Test the list_env_vars function."""

    def test_invalid_filter_pattern_type(self):
        """Test error handling for invalid filter pattern type."""
        with pytest.raises(BasicAgentToolsError, match="Filter pattern must be a string or None"):
            list_env_vars(filter_pattern=123)

    def test_invalid_limit(self):
        """Test error handling for invalid limit values."""
        with pytest.raises(BasicAgentToolsError, match="Limit must be an integer between 1 and 200"):
            list_env_vars(limit=0)

        with pytest.raises(BasicAgentToolsError, match="Limit must be an integer between 1 and 200"):
            list_env_vars(limit=-1)

        with pytest.raises(BasicAgentToolsError, match="Limit must be an integer between 1 and 200"):
            list_env_vars(limit=201)

        with pytest.raises(BasicAgentToolsError, match="Limit must be an integer between 1 and 200"):
            list_env_vars(limit="10")

    def test_list_all_variables_no_filter(self):
        """Test listing environment variables without filter."""
        test_vars = {
            "TEST_VAR_1": "value1",
            "TEST_VAR_2": "value2",
            "ANOTHER_VAR": "value3"
        }

        with patch.dict(os.environ, test_vars, clear=False):
            result = list_env_vars(limit=200)  # High limit to get all

            assert isinstance(result["variables"], dict)
            assert result["filter_pattern"] is None
            assert result["limit_applied"] == 200
            assert result["total_found"] >= 3  # At least our test variables

            # Check that our test variables are included
            for var_name, var_value in test_vars.items():
                if var_name in result["variables"]:
                    assert result["variables"][var_name] == var_value

    def test_list_variables_with_filter(self):
        """Test listing environment variables with filter pattern."""
        test_vars = {
            "TEST_FILTER_1": "value1",
            "TEST_FILTER_2": "value2",
            "OTHER_VAR": "value3"
        }

        with patch.dict(os.environ, test_vars, clear=False):
            result = list_env_vars(filter_pattern="FILTER", limit=50)

            assert result["filter_pattern"] == "FILTER"
            assert result["total_found"] >= 2  # At least TEST_FILTER_1 and TEST_FILTER_2

            # Check that filtered variables are included
            filtered_vars = result["variables"]
            filter_found = 0
            for var_name in filtered_vars:
                if "FILTER" in var_name.upper():
                    filter_found += 1

            assert filter_found >= 2

    def test_case_insensitive_filtering(self):
        """Test that filtering is case-insensitive."""
        test_vars = {
            "Test_Case_Var": "value1",
            "TEST_CASE_VAR2": "value2",
            "other_var": "value3"
        }

        with patch.dict(os.environ, test_vars, clear=False):
            result = list_env_vars(filter_pattern="case", limit=50)

            # Should find both Test_Case_Var and TEST_CASE_VAR2
            case_vars_found = 0
            for var_name in result["variables"]:
                if "case" in var_name.lower():
                    case_vars_found += 1

            assert case_vars_found >= 2

    def test_limit_enforcement(self):
        """Test that the limit parameter is enforced."""
        # Use a small limit
        result = list_env_vars(limit=3)

        assert len(result["variables"]) <= 3
        assert result["total_found"] <= 3
        assert result["limit_applied"] == 3

    def test_empty_filter_results(self):
        """Test filtering with pattern that matches no variables."""
        result = list_env_vars(filter_pattern="VERY_UNLIKELY_TO_EXIST_12345", limit=50)

        assert result["total_found"] == 0
        assert len(result["variables"]) == 0
        assert result["filter_pattern"] == "VERY_UNLIKELY_TO_EXIST_12345"