"""Test script to verify BYPASS_TOOL_CONSENT behavior on Windows.

Run this script to diagnose environment variable issues:

Windows CMD:
    set BYPASS_TOOL_CONSENT=true
    python test_bypass_windows.py

Windows PowerShell:
    $env:BYPASS_TOOL_CONSENT = "true"
    python test_bypass_windows.py

Windows PowerShell (permanent for session):
    [System.Environment]::SetEnvironmentVariable('BYPASS_TOOL_CONSENT', 'true', 'Process')
    python test_bypass_windows.py
"""

import os
import sys
import tempfile
from pathlib import Path

# Add src to path for local testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from basic_open_agent_tools.confirmation import check_user_confirmation
from basic_open_agent_tools.exceptions import BasicAgentToolsError


def test_env_var_visibility():
    """Test if environment variable is visible to Python."""
    print("=" * 70)
    print("ENVIRONMENT VARIABLE VISIBILITY TEST")
    print("=" * 70)

    bypass_value = os.getenv("BYPASS_TOOL_CONSENT")
    print(f"\n1. Raw value from os.getenv(): {repr(bypass_value)}")
    print(f"2. Type: {type(bypass_value)}")

    if bypass_value:
        print(f"3. Lowercase: {bypass_value.lower()}")
        print(f"4. Equals 'true': {bypass_value.lower() == 'true'}")
    else:
        print("3. Variable is NOT SET (None)")

    print("\nAll environment variables containing 'BYPASS':")
    for key, value in os.environ.items():
        if "BYPASS" in key.upper():
            print(f"  {key} = {repr(value)}")

    if not bypass_value:
        print("\n⚠️  BYPASS_TOOL_CONSENT is not set!")
        print("\nTry setting it in the SAME command window where you run Python:")
        print("  CMD:        set BYPASS_TOOL_CONSENT=true && python test_bypass_windows.py")
        print("  PowerShell: $env:BYPASS_TOOL_CONSENT='true'; python test_bypass_windows.py")


def test_bypass_functionality():
    """Test if bypass actually works."""
    print("\n" + "=" * 70)
    print("BYPASS FUNCTIONALITY TEST")
    print("=" * 70)

    bypass_value = os.getenv("BYPASS_TOOL_CONSENT", "false").lower()
    print(f"\nEnvironment variable value: {repr(bypass_value)}")
    print(f"Will bypass: {bypass_value == 'true'}")

    # Test 1: With skip_confirm=False (should bypass if env var is true)
    print("\nTest 1: skip_confirm=False (relies on BYPASS_TOOL_CONSENT)")
    try:
        result = check_user_confirmation(
            operation="test operation",
            target="/test/path.txt",
            skip_confirm=False,
            preview_info="Test file"
        )
        print(f"✓ Result: {result}")
        print("✓ Bypass worked! (no error raised)")
    except BasicAgentToolsError as e:
        print(f"✗ Error raised: {e}")
        print("✗ Bypass did NOT work (expected error in non-TTY)")

    # Test 2: With skip_confirm=True (should always bypass)
    print("\nTest 2: skip_confirm=True (should always bypass)")
    result = check_user_confirmation(
        operation="test operation",
        target="/test/path2.txt",
        skip_confirm=True,
        preview_info="Test file"
    )
    print(f"✓ Result: {result}")
    print("✓ Direct bypass worked")


def test_with_actual_file_operation():
    """Test with an actual file operation."""
    print("\n" + "=" * 70)
    print("ACTUAL FILE OPERATION TEST")
    print("=" * 70)

    from basic_open_agent_tools.file_system.operations import write_file_from_string

    # Create a temp file path
    temp_file = Path(tempfile.gettempdir()) / "bypass_test.txt"

    print(f"\nAttempting to write to: {temp_file}")
    print(f"BYPASS_TOOL_CONSENT = {repr(os.getenv('BYPASS_TOOL_CONSENT'))}")

    try:
        result = write_file_from_string(
            file_path=str(temp_file),
            content="Test content for bypass verification",
            skip_confirm=False  # Rely on BYPASS_TOOL_CONSENT
        )
        print(f"\n✓ File write succeeded!")
        print(f"✓ Result: {result[:100]}...")

        # Clean up
        if temp_file.exists():
            temp_file.unlink()
            print(f"✓ Cleaned up temp file")

    except BasicAgentToolsError as e:
        if "CONFIRMATION_REQUIRED" in str(e):
            print(f"\n✗ Confirmation required (bypass NOT working)")
            print(f"✗ Error: {str(e)[:200]}...")
        else:
            print(f"\n✗ Unexpected error: {e}")


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "BYPASS_TOOL_CONSENT DIAGNOSTIC TOOL" + " " * 18 + "║")
    print("╚" + "=" * 68 + "╝")

    print(f"\nPlatform: {sys.platform}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Working directory: {os.getcwd()}")

    test_env_var_visibility()
    test_bypass_functionality()
    test_with_actual_file_operation()

    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)

    bypass_value = os.getenv("BYPASS_TOOL_CONSENT")

    if bypass_value and bypass_value.lower() == "true":
        print("\n✓ Environment variable is set correctly!")
        print("✓ Bypass should be working.")
    else:
        print("\n⚠️  Environment variable is NOT set or incorrect.")
        print("\nFor Windows users:")
        print("\n1. CMD (Command Prompt):")
        print("   set BYPASS_TOOL_CONSENT=true")
        print("   python your_script.py")
        print("   ")
        print("   Or in one line:")
        print("   set BYPASS_TOOL_CONSENT=true && python your_script.py")

        print("\n2. PowerShell:")
        print("   $env:BYPASS_TOOL_CONSENT = 'true'")
        print("   python your_script.py")
        print("   ")
        print("   Or in one line:")
        print("   $env:BYPASS_TOOL_CONSENT='true'; python your_script.py")

        print("\n3. Set in Python script directly:")
        print("   import os")
        print("   os.environ['BYPASS_TOOL_CONSENT'] = 'true'")
        print("   # Then run your operations")

        print("\n4. Permanent (Windows System Properties):")
        print("   - Search for 'Environment Variables' in Windows")
        print("   - Add BYPASS_TOOL_CONSENT = true")
        print("   - Restart terminal/Python")

    print("\n" + "=" * 70)
    print()


if __name__ == "__main__":
    main()
