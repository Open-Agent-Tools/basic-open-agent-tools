#!/usr/bin/env python3
"""Systematic rollout of confirmation system to all skip_confirm functions.

This script helps identify and update all functions using skip_confirm parameter
to use the new hybrid confirmation system.

Modules to update (27 remaining functions across 12 modules):
- archive/compression.py (6 functions)
- pdf/manipulation.py (3 functions)
- data/config_processing.py (3 functions)
- word/writing.py (3 functions)
- html/generation.py (4 functions)
- markdown/generation.py (2 functions)
- diagrams/mermaid.py (1 function)
- excel/writing.py (1 function)
- file_system/editor.py (1 function)
- pdf/creation.py (1 function)
- todo/operations.py (1 function)
- word/styles.py (1 function)
"""

import subprocess
import sys
from pathlib import Path

# Modules with skip_confirm functions (count)
MODULES = {
    "archive/compression.py": 6,
    "pdf/manipulation.py": 3,
    "data/config_processing.py": 3,
    "word/writing.py": 3,
    "html/generation.py": 4,
    "markdown/generation.py": 2,
    "diagrams/mermaid.py": 1,
    "excel/writing.py": 1,
    "file_system/editor.py": 1,
    "pdf/creation.py": 1,
    "todo/operations.py": 1,
    "word/styles.py": 1,
}


def list_functions_in_module(module_path: str) -> list[str]:
    """List all functions with skip_confirm in a module."""
    result = subprocess.run(
        ["rg", r"def \w+.*skip_confirm", module_path],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return []

    functions = []
    for line in result.stdout.strip().split("\n"):
        if ":" in line:
            # Extract function name
            func_def = line.split(":", 1)[1].strip()
            func_name = func_def.split("(")[0].replace("def ", "")
            functions.append(func_name)

    return functions


def main():
    src_dir = Path(__file__).parent / "src" / "basic_open_agent_tools"

    print("=" * 70)
    print("CONFIRMATION SYSTEM ROLLOUT PLAN")
    print("=" * 70)
    print()
    print("Modules requiring update:")
    print()

    total_functions = 0
    for module_rel_path, count in MODULES.items():
        module_path = src_dir / module_rel_path
        if not module_path.exists():
            print(f"❌ {module_rel_path}: FILE NOT FOUND")
            continue

        print(f"\n📁 {module_rel_path} ({count} functions)")
        functions = list_functions_in_module(str(module_path))

        for func in functions:
            print(f"   - {func}()")
            total_functions += 1

    print()
    print("=" * 70)
    print(f"Total: {total_functions} functions across {len(MODULES)} modules")
    print("=" * 70)
    print()
    print("Update Pattern:")
    print("1. Add import: from ..confirmation import check_user_confirmation")
    print("2. Replace error raises with check_user_confirmation() calls")
    print("3. Return cancellation message if not confirmed")
    print()
    print("Would you like to see the detailed update plan? (y/n)")


if __name__ == "__main__":
    main()
