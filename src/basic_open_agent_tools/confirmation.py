"""User confirmation system for tool operations.

This module provides a hybrid confirmation system that works in three modes:
1. Bypass mode: BYPASS_TOOL_CONSENT=true environment variable skips all confirmations
2. Interactive mode: If running in a terminal (TTY), prompts user directly (defaults to YES)
3. Agent mode: If not in TTY, raises error instructing agent to ask user

Interactive mode defaults to YES - users can simply press Enter to confirm, or type 'n' to cancel.

This design allows tools to work seamlessly in terminal environments (with direct
user prompts) and in agent frameworks (where the LLM asks the user via conversation).
"""

import os
import sys
from typing import NoReturn, Optional

from .exceptions import BasicAgentToolsError


def check_user_confirmation(
    operation: str,
    target: str,
    skip_confirm: bool,
    preview_info: Optional[str] = None,
) -> tuple[bool, Optional[str]]:
    """Check if user confirmation is needed and handle accordingly.

    This function supports three operational modes:

    1. **Bypass Mode**: If skip_confirm=True or BYPASS_TOOL_CONSENT environment
       variable is set to "true", confirmation is skipped entirely.

    2. **Interactive Mode**: If running in a terminal (stdin/stdout are TTY),
       displays a confirmation prompt and waits for user input. If user declines,
       prompts for an optional decline reason.

    3. **Agent Mode**: If not in a terminal (e.g., running through an LLM agent),
       raises an error instructing the agent to ask the user for permission.

    Args:
        operation: Description of the operation requiring confirmation
                  (e.g., "overwrite existing file", "delete directory")
        target: The target path/resource being modified
        skip_confirm: If True, skip confirmation entirely
        preview_info: Optional preview information to show the user
                     (e.g., file size, number of items)

    Returns:
        Tuple of (confirmed, decline_reason):
        - confirmed: True if operation should proceed, False if user declined
        - decline_reason: None if confirmed, user's reason string if declined (may be empty)

    Raises:
        BasicAgentToolsError: In agent mode when confirmation is needed

    Examples:
        >>> # In terminal: prompts user directly (defaults to YES)
        >>> confirmed, reason = check_user_confirmation("overwrite file", "/path/to/file.txt", False)
        ⚠️  Confirmation Required
        Operation: overwrite file
        Target: /path/to/file.txt
        Do you want to proceed? [Y/n]:
        >>> confirmed
        True

        >>> # User declines with reason
        >>> confirmed, reason = check_user_confirmation("delete file", "/path/to/file.txt", False)
        Do you want to proceed? [Y/n]: n
        ✗ Cancelled by user
        Decline Reason (optional): file still needed for testing
        >>> confirmed, reason
        (False, "file still needed for testing")

        >>> # With bypass
        >>> check_user_confirmation("overwrite file", "/path/to/file.txt", True)
        (True, None)
    """
    # Mode 1: Bypass confirmation if skip_confirm=True or BYPASS_TOOL_CONSENT is set
    bypass_env = os.getenv("BYPASS_TOOL_CONSENT", "false").lower() == "true"

    if skip_confirm or bypass_env:
        if bypass_env:
            print("[BYPASS] Confirmation bypassed via BYPASS_TOOL_CONSENT")
        return (True, None)

    # Mode 2: Interactive terminal mode - prompt user directly
    if _is_interactive_terminal():
        return _interactive_confirm(operation, target, preview_info)

    # Mode 3: Agent mode - raise error with instructions for the agent
    _raise_agent_confirmation_error(operation, target, preview_info)


def _is_interactive_terminal() -> bool:
    """Check if running in an interactive terminal environment.

    Returns:
        True if both stdin and stdout are TTY (terminal), False otherwise
    """
    return sys.stdin.isatty() and sys.stdout.isatty()


def _interactive_confirm(
    operation: str, target: str, preview_info: Optional[str] = None
) -> tuple[bool, Optional[str]]:
    """Display interactive terminal confirmation prompt.

    Defaults to YES - pressing Enter confirms the operation.
    User must explicitly type 'n' or 'no' to cancel.
    If user declines, prompts for an optional reason.

    Args:
        operation: Description of the operation
        target: Target path/resource
        preview_info: Optional preview information

    Returns:
        Tuple of (confirmed, decline_reason):
        - confirmed: True if user confirmed, False if declined
        - decline_reason: None if confirmed, user's reason string if declined (may be empty)
    """
    print("\n⚠️  Confirmation Required")
    print(f"Operation: {operation}")
    print(f"Target: {target}")

    if preview_info:
        print()
        # Check if preview contains newlines for multi-line content
        if "\n" in preview_info:
            # Multi-line preview - display as-is without indentation
            print(preview_info)
        else:
            # Single-line preview - indent for readability
            print(f"Preview: {preview_info}")

    try:
        response = input("\nDo you want to proceed? [Y/n]: ").strip().lower()

        # Default to Yes (empty response or 'y'/'yes' confirms)
        if response in ("", "y", "yes"):
            print("✓ Confirmed - proceeding\n")
            return (True, None)
        else:
            print("✗ Cancelled by user")
            # Prompt for optional decline reason
            decline_reason = input("Decline Reason (optional): ").strip()
            print()  # Extra newline for spacing
            return (False, decline_reason)
    except (EOFError, KeyboardInterrupt):
        # Handle Ctrl+C or EOF gracefully
        print("\n✗ Cancelled by user (interrupted)\n")
        return (False, "interrupted by user")


def _raise_agent_confirmation_error(
    operation: str, target: str, preview_info: Optional[str] = None
) -> NoReturn:
    """Raise error for agent mode with instructions for the LLM.

    This error message is designed to be parsed by LLM agents and instruct
    them on how to proceed: ask the user for permission, then retry with
    skip_confirm=True if approved.

    Args:
        operation: Description of the operation
        target: Target path/resource
        preview_info: Optional preview information

    Raises:
        BasicAgentToolsError: Always raises with instructions for agent
    """
    error_message = f"CONFIRMATION_REQUIRED: {operation} - {target}"

    if preview_info:
        error_message += f"\nPreview: {preview_info}"

    error_message += (
        "\n\nThis operation requires user confirmation. "
        "Please ask the user for permission to proceed with this operation. "
        "If the user approves, retry the operation with skip_confirm=True."
    )

    raise BasicAgentToolsError(error_message)
