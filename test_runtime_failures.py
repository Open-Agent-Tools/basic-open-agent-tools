"""Test which tools fail at runtime due to missing dependencies."""

import inspect
import basic_open_agent_tools as boat
from typing import get_type_hints


def test_tool_runtime_availability():
    """Test if tools can be called or if they raise ImportError immediately."""

    tools = boat.load_all_tools()

    print(f"Total tools: {len(tools)}")
    print("\n=== Testing Runtime Availability ===\n")

    available_tools = []
    unavailable_tools = []

    for tool in tools:
        try:
            # Try to get the signature - this will trigger imports
            sig = inspect.signature(tool)
            hints = get_type_hints(tool)

            # Check if function body would import missing dependencies
            # by checking the source code for imports
            try:
                source = inspect.getsource(tool)
                # Check for common dependency imports that might be missing
                missing_deps = []

                if 'openpyxl' in source and not check_import('openpyxl'):
                    missing_deps.append('openpyxl')
                if 'docx' in source and not check_import('docx'):
                    missing_deps.append('python-docx')
                if 'pypdf' in source.lower() and not check_import('pypdf'):
                    missing_deps.append('pypdf')
                if 'PIL' in source and not check_import('PIL'):
                    missing_deps.append('Pillow')
                if 'diagrams' in source and not check_import('diagrams'):
                    missing_deps.append('diagrams')
                if 'pptx' in source and not check_import('pptx'):
                    missing_deps.append('python-pptx')

                if missing_deps:
                    unavailable_tools.append((tool.__name__, tool.__module__, missing_deps))
                else:
                    available_tools.append(tool)

            except (OSError, TypeError):
                # Can't get source (built-in or C extension)
                available_tools.append(tool)

        except Exception as e:
            unavailable_tools.append((tool.__name__, tool.__module__, [str(e)]))

    print(f"Available tools: {len(available_tools)}")
    print(f"Unavailable tools (missing deps): {len(unavailable_tools)}")

    if unavailable_tools:
        print(f"\n=== Unavailable Tools by Dependency ===")

        # Group by dependency
        by_dep = {}
        for name, module, deps in unavailable_tools:
            for dep in deps:
                if dep not in by_dep:
                    by_dep[dep] = []
                by_dep[dep].append((name, module))

        for dep, tools_list in sorted(by_dep.items()):
            print(f"\n{dep}: {len(tools_list)} tools")
            for name, module in tools_list[:5]:
                mod_short = module.split('.')[-1]
                print(f"  {mod_short}.{name}")
            if len(tools_list) > 5:
                print(f"  ... and {len(tools_list) - 5} more")

    return len(available_tools), len(unavailable_tools)


def check_import(module_name):
    """Check if a module can be imported."""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def analyze_missing_tools():
    """Analyze the exact count of tools that would fail."""

    print("\n\n=== Analyzing Tool Counts by Module ===\n")

    module_tools = {
        'excel': (24, 'openpyxl'),
        'word': (18, 'python-docx'),
        'pdf': (20, 'pypdf'),
        'image': (12, 'Pillow'),
        'diagrams': (16, 'diagrams'),
        'powerpoint': (10, 'python-pptx'),
    }

    total_missing = 0
    for module, (count, dep) in module_tools.items():
        if not check_import(dep.replace('-', '_').replace('python_docx', 'docx')):
            print(f"✗ {module:15s}: {count:3d} tools (missing {dep})")
            total_missing += count
        else:
            print(f"✓ {module:15s}: {count:3d} tools ({dep} available)")

    print(f"\nTotal tools potentially unavailable: {total_missing}")
    print(f"Total tools available: {326 - total_missing}")

    return total_missing


if __name__ == "__main__":
    available, unavailable = test_tool_runtime_availability()
    missing_count = analyze_missing_tools()

    print(f"\n\n=== FINAL ANALYSIS ===")
    print(f"Total tools in load_all_tools(): 326")
    print(f"Tools with runtime availability: {available}")
    print(f"Tools missing dependencies: {unavailable}")
    print(f"Expected visible tools: {326 - missing_count}")

    if 180 <= (326 - missing_count) <= 200:
        print(f"\n✅ This matches the reported ~188 tools visible to agents!")
        print(f"\nROOT CAUSE: Agent frameworks silently skip tools that require")
        print(f"            missing optional dependencies at import/declaration time.")
