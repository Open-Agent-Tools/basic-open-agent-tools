"""Test converting tools to Google ADK function declarations."""

import inspect
import basic_open_agent_tools as boat
from typing import get_type_hints


def convert_to_function_declaration(func):
    """
    Simulate Google ADK's function declaration conversion.
    This might fail silently for certain parameter types.
    """
    try:
        sig = inspect.signature(func)
        hints = get_type_hints(func)

        # Google ADK has restrictions on types
        for param_name, param in sig.parameters.items():
            if param.annotation == inspect.Parameter.empty:
                return None, f"Missing type annotation for {param_name}"

            # Get the actual type
            param_type = hints.get(param_name, param.annotation)

            # Check for problematic types
            type_str = str(param_type)

            # Check for Union types
            if "Union[" in type_str:
                return None, f"Union type not supported: {param_name}: {type_str}"

            # Check for Any type
            if "Any" in type_str:
                return None, f"Any type not supported: {param_name}: {type_str}"

            # Check for bare list without type parameter
            if type_str == "<class 'list'>" or param_type == list:
                return None, f"Untyped list: {param_name}"

            # Check for bytes
            if "bytes" in type_str.lower():
                return None, f"bytes not supported: {param_name}"

            # Check for default values
            if param.default != inspect.Parameter.empty:
                return None, f"Default values not supported: {param_name}={param.default}"

        return True, "OK"

    except Exception as e:
        return None, f"Conversion error: {e}"


def test_all_tools():
    """Test all tools for Google ADK compatibility."""
    tools = boat.load_all_tools()

    print(f"Total tools: {len(tools)}")
    print("\n=== Testing Google ADK Function Declaration Conversion ===")

    valid = []
    failed = []

    for tool in tools:
        success, message = convert_to_function_declaration(tool)
        if success:
            valid.append(tool)
        else:
            failed.append((tool.__name__, tool.__module__, message))

    print(f"\nValid tools: {len(valid)}")
    print(f"Failed tools: {len(failed)}")

    if failed:
        print(f"\n=== Failed Tools ===")
        failure_reasons = {}
        for name, module, reason in failed:
            reason_type = reason.split(":")[0]
            if reason_type not in failure_reasons:
                failure_reasons[reason_type] = []
            failure_reasons[reason_type].append((name, module, reason))

        for reason_type, tools_list in failure_reasons.items():
            print(f"\n{reason_type}: {len(tools_list)} tools")
            for name, module, reason in tools_list[:5]:
                print(f"  {module}.{name}: {reason}")
            if len(tools_list) > 5:
                print(f"  ... and {len(tools_list) - 5} more")

    return len(valid), len(failed)


if __name__ == "__main__":
    valid, failed = test_all_tools()

    print(f"\n\n=== SUMMARY ===")
    print(f"Total tools loaded: 326")
    print(f"Successfully converted: {valid}")
    print(f"Failed conversion: {failed}")
    print(f"Success rate: {valid/326*100:.1f}%")

    if failed > 0:
        expected_visible = 326 - failed
        print(f"\n⚠️  Expected visible tools in agent: {expected_visible}")
        if 180 <= expected_visible <= 195:
            print(f"✅ This matches the reported ~188 tools!")
