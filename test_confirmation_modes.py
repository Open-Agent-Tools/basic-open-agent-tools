#!/usr/bin/env python3
"""Test script for confirmation system in different modes.

This script tests the three operational modes of the confirmation system:
1. Bypass mode (BYPASS_TOOL_CONSENT=true)
2. Agent mode (non-TTY environment)
3. Interactive mode (TTY environment - manual test only)

Usage:
    # Test bypass mode
    BYPASS_TOOL_CONSENT=true python3 test_confirmation_modes.py bypass

    # Test agent mode (simulates non-TTY)
    python3 test_confirmation_modes.py agent

    # Test interactive mode (run in terminal)
    python3 test_confirmation_modes.py interactive
"""

import os
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from basic_open_agent_tools.file_system.operations import write_file_from_string


def test_bypass_mode():
    """Test bypass mode with BYPASS_TOOL_CONSENT environment variable."""
    print("=" * 60)
    print("TEST: Bypass Mode (BYPASS_TOOL_CONSENT=true)")
    print("=" * 60)

    # Ensure env var is set
    os.environ["BYPASS_TOOL_CONSENT"] = "true"

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.txt"

        # Create file
        print("\n1. Creating file (should succeed)...")
        result = write_file_from_string(
            file_path=str(test_file),
            content="Initial content",
            skip_confirm=False  # Even with False, bypass should work
        )
        print(f"✓ {result}")

        # Overwrite file (should auto-bypass confirmation)
        print("\n2. Overwriting file (should bypass confirmation)...")
        result = write_file_from_string(
            file_path=str(test_file),
            content="Updated content",
            skip_confirm=False  # Bypass via env var
        )
        print(f"✓ {result}")

        print("\n✅ BYPASS MODE TEST PASSED")
        print("   Environment variable successfully bypassed all confirmations\n")


def test_agent_mode():
    """Test agent mode (non-TTY) - should raise error with instructions."""
    print("=" * 60)
    print("TEST: Agent Mode (non-TTY environment)")
    print("=" * 60)

    # Ensure bypass is NOT set
    os.environ.pop("BYPASS_TOOL_CONSENT", None)

    # We can't truly simulate non-TTY without subprocess, so we'll just
    # show what WOULD happen by testing with skip_confirm=False on existing file

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.txt"

        # Create file first (no confirmation needed)
        print("\n1. Creating initial file...")
        result = write_file_from_string(
            file_path=str(test_file),
            content="Initial content",
            skip_confirm=True  # Skip for initial creation
        )
        print(f"✓ {result}")

        # Now try to overwrite WITHOUT skip_confirm
        # In a real non-TTY environment, this would raise an error
        # In TTY (terminal), it will prompt for input
        print("\n2. Attempting to overwrite file with skip_confirm=False...")
        print("   (In non-TTY agent mode, this would raise BasicAgentToolsError)")
        print("   (In TTY terminal mode, this will prompt for confirmation)")

        if sys.stdin.isatty():
            print("\n⚠️  You are running in a TTY environment (terminal)")
            print("   To properly test agent mode, this needs to run in non-TTY")
            print("   (e.g., piped input or subprocess without terminal)")
            print("\n   For now, demonstrating what the error WOULD be:")
            print("\n   BasicAgentToolsError:")
            print("   CONFIRMATION_REQUIRED: overwrite existing file - " + str(test_file))
            print("   Preview: X bytes")
            print()
            print("   This operation requires user confirmation.")
            print("   Please ask the user for permission to proceed with this operation.")
            print("   If the user approves, retry the operation with skip_confirm=True.")
        else:
            # Actually in non-TTY - will raise error
            try:
                result = write_file_from_string(
                    file_path=str(test_file),
                    content="Updated content",
                    skip_confirm=False
                )
                print(f"❌ UNEXPECTED: Operation succeeded without error: {result}")
            except Exception as e:
                print(f"✓ Got expected error in agent mode:")
                print(f"  {type(e).__name__}: {e}")
                print("\n✅ AGENT MODE TEST PASSED")


def test_interactive_mode():
    """Test interactive mode - requires manual user input."""
    print("=" * 60)
    print("TEST: Interactive Mode (TTY with manual confirmation)")
    print("=" * 60)

    # Ensure bypass is NOT set
    os.environ.pop("BYPASS_TOOL_CONSENT", None)

    if not sys.stdin.isatty():
        print("❌ ERROR: Interactive mode requires a TTY terminal")
        print("   Run this test directly in a terminal")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.txt"

        # Create file first
        print("\n1. Creating initial file...")
        result = write_file_from_string(
            file_path=str(test_file),
            content="Initial content",
            skip_confirm=True
        )
        print(f"✓ {result}")

        # Now try to overwrite - should prompt user
        print("\n2. Attempting to overwrite file...")
        print("   You will be prompted for confirmation.")
        print("   Try answering 'y' first, then run again and try 'n'\n")

        result = write_file_from_string(
            file_path=str(test_file),
            content="Updated content",
            skip_confirm=False
        )
        print(f"\nResult: {result}")

        # Check if file was updated based on user response
        actual_content = test_file.read_text()
        if "Updated" in actual_content:
            print("\n✅ File was updated (user confirmed)")
        else:
            print("\n✅ File unchanged (user cancelled)")

        print("\n✅ INTERACTIVE MODE TEST COMPLETED")
        print("   Confirmation prompt worked correctly\n")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "bypass":
        test_bypass_mode()
    elif mode == "agent":
        test_agent_mode()
    elif mode == "interactive":
        test_interactive_mode()
    else:
        print(f"Unknown mode: {mode}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
