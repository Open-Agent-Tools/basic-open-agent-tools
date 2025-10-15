"""Test what agent frameworks see when introspecting tools."""

import inspect
import basic_open_agent_tools as boat
from typing import get_type_hints


def test_google_adk_introspection():
    """Simulate how Google ADK might introspect tools."""
    tools = boat.load_all_tools()

    print(f"Total tools loaded: {len(tools)}")
    print(f"\n=== Testing Google ADK-style introspection ===")

    valid_tools = []
    failed_tools = []

    for tool in tools:
        try:
            # Google ADK needs to introspect signature and type hints
            sig = inspect.signature(tool)
            hints = get_type_hints(tool)

            # Check if it has required docstring
            if not tool.__doc__:
                failed_tools.append((tool.__name__, "Missing docstring"))
                continue

            # Check parameters are typed
            for param_name, param in sig.parameters.items():
                if param.annotation == inspect.Parameter.empty:
                    failed_tools.append((tool.__name__, f"Parameter {param_name} not typed"))
                    break
            else:
                valid_tools.append(tool)

        except Exception as e:
            failed_tools.append((tool.__name__, f"Introspection error: {e}"))

    print(f"\nValid tools: {len(valid_tools)}")
    print(f"Failed tools: {len(failed_tools)}")

    if failed_tools:
        print(f"\n=== Failed Tools (first 10) ===")
        for name, reason in failed_tools[:10]:
            print(f"  {name}: {reason}")

    return len(valid_tools), len(failed_tools)


def test_strands_introspection():
    """Test Strands decorator presence."""
    tools = boat.load_all_tools()

    print(f"\n\n=== Testing Strands decorator presence ===")

    strands_tools = []
    non_strands_tools = []

    for tool in tools:
        # Check if tool has Strands decorator marker
        if hasattr(tool, '_strands_tool'):
            strands_tools.append(tool)
        else:
            non_strands_tools.append(tool)

    print(f"Tools with @strands_tool: {len(strands_tools)}")
    print(f"Tools without @strands_tool: {len(non_strands_tools)}")

    return len(strands_tools), len(non_strands_tools)


def count_tools_by_module():
    """Count tools grouped by module."""
    tools = boat.load_all_tools()

    print(f"\n\n=== Tools by module ===")

    from collections import defaultdict
    by_module = defaultdict(list)

    for tool in tools:
        module = tool.__module__.split('.')[-1]
        by_module[module].append(tool.__name__)

    total = 0
    for module in sorted(by_module.keys()):
        count = len(by_module[module])
        total += count
        print(f"{module:20s}: {count:3d} tools")

    print(f"\nTotal: {total}")


if __name__ == "__main__":
    valid, failed = test_google_adk_introspection()
    strands, non_strands = test_strands_introspection()
    count_tools_by_module()

    print(f"\n\n=== SUMMARY ===")
    print(f"Total tools: 326")
    print(f"Google ADK valid: {valid}")
    print(f"Google ADK failed: {failed}")
    print(f"With @strands_tool: {strands}")
    print(f"Without @strands_tool: {non_strands}")

    if valid < 326:
        print(f"\n⚠️  WARNING: {326 - valid} tools may not work with Google ADK")
