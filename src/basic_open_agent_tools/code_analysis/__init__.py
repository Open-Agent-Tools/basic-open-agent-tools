"""Code analysis tools for AI agents.

This module provides Python code analysis utilities including AST parsing,
complexity calculation, import management, and secret detection.

All functions follow Google ADK Function Tool standards:
- JSON-serializable types only (str, int, bool, dict, list)
- No default parameter values
- Consistent exception patterns
- Clear docstrings for LLM understanding
"""

from basic_open_agent_tools.code_analysis.ast_parsing import (
    extract_classes,
    extract_functions,
    extract_imports,
    parse_python_ast,
)
from basic_open_agent_tools.code_analysis.complexity import (
    calculate_complexity,
    calculate_function_complexity,
    get_code_metrics,
    identify_complex_functions,
)
from basic_open_agent_tools.code_analysis.imports import (
    find_unused_imports,
    organize_imports,
    validate_import_order,
)
from basic_open_agent_tools.code_analysis.secrets import (
    scan_directory_for_secrets,
    scan_for_secrets,
    validate_secret_patterns,
)

__all__ = [
    # AST Parsing
    "parse_python_ast",
    "extract_functions",
    "extract_classes",
    "extract_imports",
    # Complexity Analysis
    "calculate_complexity",
    "calculate_function_complexity",
    "get_code_metrics",
    "identify_complex_functions",
    # Import Management
    "find_unused_imports",
    "organize_imports",
    "validate_import_order",
    # Secret Detection
    "scan_for_secrets",
    "scan_directory_for_secrets",
    "validate_secret_patterns",
]
