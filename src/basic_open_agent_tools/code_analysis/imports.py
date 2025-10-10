"""Import management and validation utilities.

This module provides functions to analyze, organize, and validate Python import
statements for code quality and consistency.
"""

import ast
from typing import Any

from basic_open_agent_tools.exceptions import CodeAnalysisError


def find_unused_imports(file_path: str) -> list[str]:
    """Identify imports that are not used in the file.

    Analyzes a Python file to find import statements where the imported names
    are never referenced in the code. This helps identify dead code and
    unnecessary dependencies.

    Args:
        file_path: Absolute path to the Python file to analyze

    Returns:
        List of unused import names (e.g., ["os", "sys", "json"])

    Raises:
        TypeError: If file_path is not a string
        FileNotFoundError: If the file does not exist
        CodeAnalysisError: If file cannot be parsed

    Example:
        >>> unused = find_unused_imports("/path/to/module.py")
        >>> unused
        ["collections", "tempfile"]
    """
    if not isinstance(file_path, str):
        raise TypeError(f"file_path must be a string, got {type(file_path)}")

    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise CodeAnalysisError(f"Error reading file {file_path}: {str(e)}")

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError as e:
        raise CodeAnalysisError(
            f"Syntax error in {file_path} at line {e.lineno}: {e.msg}"
        )
    except Exception as e:
        raise CodeAnalysisError(f"Error parsing {file_path}: {str(e)}")

    # Collect all imported names
    imported_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                # Use alias if present, otherwise use module name
                name = alias.asname if alias.asname else alias.name
                imported_names.add(name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name != "*":  # Ignore wildcard imports
                    name = alias.asname if alias.asname else alias.name
                    imported_names.add(name)

    # Find all name references in the code
    used_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used_names.add(node.id)
        elif isinstance(node, ast.Attribute):
            # For dotted names like os.path, add the first part
            if isinstance(node.value, ast.Name):
                used_names.add(node.value.id)

    # Imports that are never used
    unused = sorted(imported_names - used_names)

    return unused


def organize_imports(file_path: str) -> str:
    """Sort and organize imports according to PEP 8 conventions.

    Organizes Python imports into three groups (stdlib, third-party, local)
    with alphabetical sorting within each group. Returns the formatted import
    block as a string.

    Args:
        file_path: Absolute path to the Python file to analyze

    Returns:
        Formatted import block as string with proper grouping and sorting

    Raises:
        TypeError: If file_path is not a string
        FileNotFoundError: If the file does not exist
        CodeAnalysisError: If file cannot be parsed

    Example:
        >>> imports = organize_imports("/path/to/module.py")
        >>> print(imports)
        import os
        import sys
        <BLANKLINE>
        import requests
        <BLANKLINE>
        from .utils import helper
    """
    if not isinstance(file_path, str):
        raise TypeError(f"file_path must be a string, got {type(file_path)}")

    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise CodeAnalysisError(f"Error reading file {file_path}: {str(e)}")

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError as e:
        raise CodeAnalysisError(
            f"Syntax error in {file_path} at line {e.lineno}: {e.msg}"
        )
    except Exception as e:
        raise CodeAnalysisError(f"Error parsing {file_path}: {str(e)}")

    # Standard library modules (subset for detection)
    stdlib_modules = {
        "abc",
        "ast",
        "asyncio",
        "collections",
        "copy",
        "csv",
        "datetime",
        "enum",
        "functools",
        "io",
        "itertools",
        "json",
        "logging",
        "math",
        "os",
        "pathlib",
        "random",
        "re",
        "sys",
        "time",
        "typing",
        "unittest",
    }

    stdlib_imports = []
    third_party_imports = []
    local_imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name.split(".")[0]
                import_str = f"import {alias.name}"
                if alias.asname:
                    import_str += f" as {alias.asname}"

                if module_name in stdlib_modules:
                    stdlib_imports.append(import_str)
                else:
                    third_party_imports.append(import_str)

        elif isinstance(node, ast.ImportFrom):
            if node.level > 0:  # Relative import
                module_part = node.module or ""
                names = ", ".join(
                    f"{alias.name}" + (f" as {alias.asname}" if alias.asname else "")
                    for alias in node.names
                )
                import_str = f"from {'.' * node.level}{module_part} import {names}"
                local_imports.append(import_str)
            elif node.module:
                module_name = node.module.split(".")[0]
                names = ", ".join(
                    f"{alias.name}" + (f" as {alias.asname}" if alias.asname else "")
                    for alias in node.names
                )
                import_str = f"from {node.module} import {names}"

                if module_name in stdlib_modules:
                    stdlib_imports.append(import_str)
                else:
                    third_party_imports.append(import_str)

    # Sort each group
    stdlib_imports = sorted(set(stdlib_imports))
    third_party_imports = sorted(set(third_party_imports))
    local_imports = sorted(set(local_imports))

    # Build result with blank lines between groups
    result_parts = []
    if stdlib_imports:
        result_parts.append("\n".join(stdlib_imports))
    if third_party_imports:
        result_parts.append("\n".join(third_party_imports))
    if local_imports:
        result_parts.append("\n".join(local_imports))

    return "\n\n".join(result_parts)


def validate_import_order(file_path: str) -> dict[str, Any]:
    """Check if imports follow PEP 8 ordering conventions.

    Validates that imports are organized according to PEP 8 guidelines:
    1. Standard library imports
    2. Related third party imports
    3. Local application/library specific imports

    Args:
        file_path: Absolute path to the Python file to analyze

    Returns:
        Dictionary containing:
        - is_valid: Whether imports follow correct order (bool)
        - violations: List of ordering violations found
        - suggestions: List of suggested fixes

    Raises:
        TypeError: If file_path is not a string
        FileNotFoundError: If the file does not exist
        CodeAnalysisError: If file cannot be parsed

    Example:
        >>> result = validate_import_order("/path/to/module.py")
        >>> result["is_valid"]
        False
        >>> result["violations"]
        ["Third-party import 'requests' found before stdlib import 'os'"]
    """
    if not isinstance(file_path, str):
        raise TypeError(f"file_path must be a string, got {type(file_path)}")

    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise CodeAnalysisError(f"Error reading file {file_path}: {str(e)}")

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError as e:
        raise CodeAnalysisError(
            f"Syntax error in {file_path} at line {e.lineno}: {e.msg}"
        )
    except Exception as e:
        raise CodeAnalysisError(f"Error parsing {file_path}: {str(e)}")

    # Standard library modules
    stdlib_modules = {
        "abc",
        "ast",
        "asyncio",
        "collections",
        "copy",
        "csv",
        "datetime",
        "enum",
        "functools",
        "io",
        "itertools",
        "json",
        "logging",
        "math",
        "os",
        "pathlib",
        "random",
        "re",
        "sys",
        "time",
        "typing",
        "unittest",
    }

    # Track import order
    import_order = []  # List of (lineno, type, name)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name.split(".")[0]
                if module_name in stdlib_modules:
                    import_order.append((node.lineno, "stdlib", alias.name))
                else:
                    import_order.append((node.lineno, "third_party", alias.name))

        elif isinstance(node, ast.ImportFrom):
            if node.level > 0:  # Relative import
                module_name = node.module or ""
                import_order.append((node.lineno, "local", f".{module_name}"))
            elif node.module:
                module_name = node.module.split(".")[0]
                if module_name in stdlib_modules:
                    import_order.append((node.lineno, "stdlib", node.module))
                else:
                    import_order.append((node.lineno, "third_party", node.module))

    # Sort by line number to get actual order
    import_order.sort(key=lambda x: x[0])

    # Check for violations
    violations = []
    suggestions = []

    # Expected order: stdlib -> third_party -> local
    order_map = {"stdlib": 0, "third_party": 1, "local": 2}
    last_order = -1

    for lineno, import_type, name in import_order:
        current_order = order_map[import_type]
        if current_order < last_order:
            if import_type == "stdlib" and last_order >= 1:
                violations.append(
                    f"Line {lineno}: Standard library import '{name}' should come before third-party/local imports"
                )
                suggestions.append("Move standard library imports to the top")
            elif import_type == "third_party" and last_order == 2:
                violations.append(
                    f"Line {lineno}: Third-party import '{name}' should come before local imports"
                )
                suggestions.append("Move third-party imports before local imports")

        last_order = max(last_order, current_order)

    # Check for alphabetical order within groups
    groups: dict[str, list[tuple[int, str]]] = {
        "stdlib": [],
        "third_party": [],
        "local": [],
    }
    for lineno, import_type, name in import_order:
        groups[import_type].append((lineno, name))

    for group_name, items in groups.items():
        if len(items) > 1:
            names = [name for _, name in items]
            sorted_names = sorted(names)
            if names != sorted_names:
                violations.append(
                    f"{group_name.capitalize()} imports are not alphabetically sorted"
                )
                suggestions.append(f"Sort {group_name} imports alphabetically")

    is_valid = len(violations) == 0

    return {
        "is_valid": is_valid,
        "violations": violations,
        "suggestions": list(set(suggestions)),  # Remove duplicates
    }
