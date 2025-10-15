"""Test if modules with missing dependencies fail to import."""

import sys
import importlib


def test_module_import_with_missing_deps():
    """Test if tool modules fail to import when dependencies are missing."""

    print("=== Testing Module Import Failures ===\n")

    # Remove openpyxl if it exists to simulate missing dependency
    if 'openpyxl' in sys.modules:
        del sys.modules['openpyxl']

    # Try to import Excel reading module
    try:
        print("Attempting to import excel.reading module...")
        from basic_open_agent_tools.excel import reading
        print(f"✓ Successfully imported! HAS_OPENPYXL={reading.HAS_OPENPYXL}")
        print(f"  Functions available: {len([x for x in dir(reading) if not x.startswith('_')])}")
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        print("  This means ALL Excel tools are inaccessible!")

    # Try Word module
    try:
        print("\nAttempting to import word.reading module...")
        from basic_open_agent_tools.word import reading as word_reading
        print(f"✓ Successfully imported! HAS_DOCX={word_reading.HAS_DOCX}")
    except ImportError as e:
        print(f"✗ Import failed: {e}")

    # Try PDF module
    try:
        print("\nAttempting to import pdf.parsing module...")
        from basic_open_agent_tools.pdf import parsing
        print(f"✓ Successfully imported! HAS_PYPDF={parsing.HAS_PYPDF}")
    except ImportError as e:
        print(f"✗ Import failed: {e}")


def test_load_all_tools_with_missing_deps():
    """Test if load_all_tools() silently excludes broken tools."""

    print("\n\n=== Testing load_all_tools() with Missing Dependencies ===\n")

    try:
        import basic_open_agent_tools as boat
        tools = boat.load_all_tools()
        print(f"Total tools loaded: {len(tools)}")

        # Check which modules are represented
        from collections import defaultdict
        by_module = defaultdict(int)

        for tool in tools:
            module = tool.__module__.split('.')[2] if len(tool.__module__.split('.')) > 2 else 'unknown'
            by_module[module] += 1

        print(f"\nTools by module:")
        for module in sorted(by_module.keys()):
            print(f"  {module}: {by_module[module]} tools")

        # Check if Excel tools are present
        excel_tools = [t for t in tools if 'excel' in t.__module__]
        word_tools = [t for t in tools if 'word' in t.__module__]
        pdf_tools = [t for t in tools if 'pdf' in t.__module__]

        print(f"\nSpecific module tools:")
        print(f"  Excel tools: {len(excel_tools)}")
        print(f"  Word tools: {len(word_tools)}")
        print(f"  PDF tools: {len(pdf_tools)}")

    except Exception as e:
        print(f"✗ Failed to load tools: {e}")


if __name__ == "__main__":
    test_module_import_with_missing_deps()
    test_load_all_tools_with_missing_deps()

    print("\n\n=== ROOT CAUSE ANALYSIS ===")
    print("If imports failed, the problem is that optional dependencies are")
    print("imported at MODULE level (not inside functions), which prevents the")
    print("entire module from loading when the dependency is missing.")
    print("\nThis causes agent frameworks to silently skip those tools.")
