"""Tests for confirmation module.

Tests the 3-mode hybrid confirmation system:
1. Bypass mode (skip_confirm=True or BYPASS_TOOL_CONSENT env var)
2. Interactive mode (TTY with user input)
3. Agent mode (non-TTY raises instructive error)
"""

from io import StringIO
from unittest.mock import patch

import pytest

from basic_open_agent_tools.confirmation import (
    _interactive_confirm,
    _is_interactive_terminal,
    _raise_agent_confirmation_error,
    check_user_confirmation,
)
from basic_open_agent_tools.exceptions import BasicAgentToolsError


class TestBypassMode:
    """Test bypass mode with skip_confirm=True or BYPASS_TOOL_CONSENT."""

    def test_bypass_with_skip_confirm_true(self):
        """Test bypass when skip_confirm=True."""
        result = check_user_confirmation(
            operation="test operation",
            target="/test/path",
            skip_confirm=True,
            preview_info="test preview",
        )
        assert result is True

    def test_bypass_with_environment_variable(self, monkeypatch):
        """Test bypass when BYPASS_TOOL_CONSENT=true."""
        monkeypatch.setenv("BYPASS_TOOL_CONSENT", "true")

        with patch("builtins.print") as mock_print:
            result = check_user_confirmation(
                operation="test operation",
                target="/test/path",
                skip_confirm=False,
            )

        assert result is True
        # Should print bypass message
        mock_print.assert_called_once_with(
            "[BYPASS] Confirmation bypassed via BYPASS_TOOL_CONSENT"
        )

    def test_bypass_environment_variable_case_insensitive(self, monkeypatch):
        """Test BYPASS_TOOL_CONSENT is case-insensitive."""
        monkeypatch.setenv("BYPASS_TOOL_CONSENT", "TRUE")

        result = check_user_confirmation(
            operation="test operation",
            target="/test/path",
            skip_confirm=False,
        )

        assert result is True

    def test_bypass_environment_variable_false(self, monkeypatch):
        """Test BYPASS_TOOL_CONSENT=false does not bypass."""
        monkeypatch.setenv("BYPASS_TOOL_CONSENT", "false")

        # Should not bypass, will go to agent mode (non-TTY in tests)
        with pytest.raises(BasicAgentToolsError, match="CONFIRMATION_REQUIRED"):
            check_user_confirmation(
                operation="test operation",
                target="/test/path",
                skip_confirm=False,
            )

    def test_skip_confirm_takes_precedence_over_env(self, monkeypatch):
        """Test skip_confirm=True takes precedence even if env var is false."""
        monkeypatch.setenv("BYPASS_TOOL_CONSENT", "false")

        result = check_user_confirmation(
            operation="test operation",
            target="/test/path",
            skip_confirm=True,
        )

        assert result is True


class TestInteractiveMode:
    """Test interactive mode with TTY and user input."""

    def test_interactive_confirm_yes(self):
        """Test interactive confirmation with 'y' response."""
        with patch("sys.stdin", StringIO("y\n")):
            with patch("builtins.print") as mock_print:
                result = _interactive_confirm(
                    operation="delete file",
                    target="/test/file.txt",
                    preview_info="1024 bytes",
                )

        assert result is True
        # Check confirmation message was printed
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Confirmation Required" in str(call) for call in calls)
        assert any("delete file" in str(call) for call in calls)
        assert any("/test/file.txt" in str(call) for call in calls)
        assert any("1024 bytes" in str(call) for call in calls)
        assert any("Confirmed" in str(call) for call in calls)

    def test_interactive_confirm_no(self):
        """Test interactive confirmation with 'n' response."""
        with patch("sys.stdin", StringIO("n\n")):
            with patch("builtins.print") as mock_print:
                result = _interactive_confirm(
                    operation="delete file",
                    target="/test/file.txt",
                )

        assert result is False
        # Check cancelled message was printed
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Cancelled" in str(call) for call in calls)

    def test_interactive_confirm_empty_defaults_no(self):
        """Test interactive confirmation with empty input defaults to no."""
        with patch("sys.stdin", StringIO("\n")):
            with patch("builtins.print"):
                result = _interactive_confirm(
                    operation="delete file",
                    target="/test/file.txt",
                )

        assert result is False

    def test_interactive_confirm_random_input_defaults_no(self):
        """Test interactive confirmation with random input defaults to no."""
        with patch("sys.stdin", StringIO("maybe\n")):
            with patch("builtins.print"):
                result = _interactive_confirm(
                    operation="delete file",
                    target="/test/file.txt",
                )

        assert result is False

    def test_interactive_confirm_without_preview(self):
        """Test interactive confirmation without preview info."""
        with patch("sys.stdin", StringIO("y\n")):
            with patch("builtins.print") as mock_print:
                result = _interactive_confirm(
                    operation="delete file",
                    target="/test/file.txt",
                    preview_info=None,
                )

        assert result is True
        # Preview should not be in output
        calls = [str(call) for call in mock_print.call_args_list]
        assert not any("Preview" in str(call) for call in calls)

    def test_interactive_confirm_eof_error(self):
        """Test interactive confirmation handles EOF gracefully."""
        with patch("builtins.input", side_effect=EOFError):
            with patch("builtins.print") as mock_print:
                result = _interactive_confirm(
                    operation="delete file",
                    target="/test/file.txt",
                )

        assert result is False
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("interrupted" in str(call).lower() for call in calls)

    def test_interactive_confirm_keyboard_interrupt(self):
        """Test interactive confirmation handles Ctrl+C gracefully."""
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            with patch("builtins.print") as mock_print:
                result = _interactive_confirm(
                    operation="delete file",
                    target="/test/file.txt",
                )

        assert result is False
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("interrupted" in str(call).lower() for call in calls)

    def test_is_interactive_terminal_detection(self):
        """Test TTY detection (mocked)."""
        # In test environment, stdin/stdout are not TTY
        # This tests the actual behavior in pytest
        assert _is_interactive_terminal() is False

        # Test with mocked TTY
        with patch("sys.stdin.isatty", return_value=True):
            with patch("sys.stdout.isatty", return_value=True):
                assert _is_interactive_terminal() is True

        # Test with only stdin as TTY
        with patch("sys.stdin.isatty", return_value=True):
            with patch("sys.stdout.isatty", return_value=False):
                assert _is_interactive_terminal() is False

        # Test with only stdout as TTY
        with patch("sys.stdin.isatty", return_value=False):
            with patch("sys.stdout.isatty", return_value=True):
                assert _is_interactive_terminal() is False


class TestAgentMode:
    """Test agent mode with non-TTY environment."""

    def test_agent_mode_raises_error(self):
        """Test agent mode raises CONFIRMATION_REQUIRED error."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            _raise_agent_confirmation_error(
                operation="overwrite file",
                target="/test/file.txt",
            )

        error_msg = str(exc_info.value)
        assert "CONFIRMATION_REQUIRED" in error_msg
        assert "overwrite file" in error_msg
        assert "/test/file.txt" in error_msg
        assert "ask the user" in error_msg
        assert "skip_confirm=True" in error_msg

    def test_agent_mode_with_preview_info(self):
        """Test agent mode includes preview info in error."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            _raise_agent_confirmation_error(
                operation="delete directory",
                target="/test/dir",
                preview_info="5 files, 1024 bytes",
            )

        error_msg = str(exc_info.value)
        assert "CONFIRMATION_REQUIRED" in error_msg
        assert "delete directory" in error_msg
        assert "/test/dir" in error_msg
        assert "5 files, 1024 bytes" in error_msg

    def test_agent_mode_without_preview_info(self):
        """Test agent mode without preview info."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            _raise_agent_confirmation_error(
                operation="create file",
                target="/test/new.txt",
                preview_info=None,
            )

        error_msg = str(exc_info.value)
        assert "CONFIRMATION_REQUIRED" in error_msg
        assert "Preview" not in error_msg  # Should not include preview section

    def test_check_user_confirmation_agent_mode_default(self):
        """Test check_user_confirmation goes to agent mode in non-TTY environment."""
        # In pytest, we're not in a TTY, so should raise error
        with pytest.raises(BasicAgentToolsError, match="CONFIRMATION_REQUIRED"):
            check_user_confirmation(
                operation="test operation",
                target="/test/path",
                skip_confirm=False,
            )


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""

    def test_file_overwrite_scenario_bypass(self):
        """Test file overwrite scenario with bypass mode."""
        result = check_user_confirmation(
            operation="overwrite existing file",
            target="/app/config.yml",
            skip_confirm=True,
            preview_info="2048 bytes",
        )
        assert result is True

    def test_file_delete_scenario_agent(self):
        """Test file delete scenario in agent mode."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            check_user_confirmation(
                operation="delete file",
                target="/important/data.db",
                skip_confirm=False,
                preview_info="10MB database file",
            )

        error_msg = str(exc_info.value)
        assert "CONFIRMATION_REQUIRED" in error_msg
        assert "delete file" in error_msg
        assert "/important/data.db" in error_msg
        assert "10MB database file" in error_msg

    def test_directory_delete_scenario_interactive(self):
        """Test directory delete scenario in interactive mode."""
        # Need to patch _is_interactive_terminal directly since check_user_confirmation
        # calls it internally
        with patch(
            "basic_open_agent_tools.confirmation._is_interactive_terminal",
            return_value=True,
        ):
            with patch("sys.stdin", StringIO("n\n")):
                with patch("builtins.print"):
                    result = check_user_confirmation(
                        operation="delete directory",
                        target="/tmp/old_data",
                        skip_confirm=False,
                        preview_info="50 files",
                    )

        assert result is False

    def test_ci_environment_bypass(self, monkeypatch):
        """Test CI environment with BYPASS_TOOL_CONSENT."""
        monkeypatch.setenv("BYPASS_TOOL_CONSENT", "true")
        monkeypatch.setenv("CI", "true")

        with patch("builtins.print") as mock_print:
            result = check_user_confirmation(
                operation="overwrite test results",
                target="/test-results/output.xml",
                skip_confirm=False,
            )

        assert result is True
        mock_print.assert_called_once_with(
            "[BYPASS] Confirmation bypassed via BYPASS_TOOL_CONSENT"
        )

    def test_multiple_confirmations_same_session(self, monkeypatch):
        """Test multiple confirmations in same session."""
        # First with bypass
        result1 = check_user_confirmation(
            operation="write file",
            target="/tmp/file1.txt",
            skip_confirm=True,
        )
        assert result1 is True

        # Then without bypass (should raise in non-TTY)
        with pytest.raises(BasicAgentToolsError):
            check_user_confirmation(
                operation="write file",
                target="/tmp/file2.txt",
                skip_confirm=False,
            )

        # Then with env var bypass
        monkeypatch.setenv("BYPASS_TOOL_CONSENT", "true")
        result3 = check_user_confirmation(
            operation="write file",
            target="/tmp/file3.txt",
            skip_confirm=False,
        )
        assert result3 is True


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_operation_string(self):
        """Test with empty operation string."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            _raise_agent_confirmation_error(
                operation="",
                target="/test/path",
            )

        error_msg = str(exc_info.value)
        assert "CONFIRMATION_REQUIRED" in error_msg

    def test_empty_target_string(self):
        """Test with empty target string."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            _raise_agent_confirmation_error(
                operation="delete",
                target="",
            )

        error_msg = str(exc_info.value)
        assert "CONFIRMATION_REQUIRED" in error_msg

    def test_special_characters_in_strings(self):
        """Test with special characters in operation and target."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            _raise_agent_confirmation_error(
                operation="delete file with 'quotes' and \"quotes\"",
                target="/path/with spaces/and-special!@#$%chars.txt",
                preview_info="Size: 1KB, Modified: 2024-01-01",
            )

        error_msg = str(exc_info.value)
        assert "CONFIRMATION_REQUIRED" in error_msg
        assert "quotes" in error_msg
        assert "special!@#$%chars" in error_msg

    def test_unicode_characters(self):
        """Test with Unicode characters."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            _raise_agent_confirmation_error(
                operation="删除文件",  # "delete file" in Chinese
                target="/data/文档.txt",  # "document.txt" in Chinese
                preview_info="大小: 1MB",  # "size: 1MB" in Chinese
            )

        error_msg = str(exc_info.value)
        assert "CONFIRMATION_REQUIRED" in error_msg
        assert "删除文件" in error_msg
        assert "文档.txt" in error_msg

    def test_very_long_strings(self):
        """Test with very long operation and target strings."""
        long_operation = "a" * 1000
        long_target = "/path/" + "b" * 1000 + ".txt"
        long_preview = "c" * 1000

        with pytest.raises(BasicAgentToolsError) as exc_info:
            _raise_agent_confirmation_error(
                operation=long_operation,
                target=long_target,
                preview_info=long_preview,
            )

        error_msg = str(exc_info.value)
        assert "CONFIRMATION_REQUIRED" in error_msg
        assert long_operation in error_msg
        assert long_target in error_msg
        assert long_preview in error_msg
