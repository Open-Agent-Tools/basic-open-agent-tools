"""Code complexity analysis utilities.

This module provides functions to calculate code complexity metrics including
McCabe cyclomatic complexity and other code quality indicators.
"""

import ast
from typing import Any

from basic_open_agent_tools.exceptions import CodeAnalysisError


def calculate_complexity(file_path: str) -> dict[str, Any]:
    """Calculate McCabe cyclomatic complexity for all functions in a file.

    Analyzes a Python file and calculates the cyclomatic complexity for each
    function. Cyclomatic complexity measures the number of linearly independent
    paths through the code, which correlates with testing difficulty.

    Args:
        file_path: Absolute path to the Python file to analyze

    Returns:
        Dictionary containing:
        - functions: List of dicts with function name, complexity, line range
        - average_complexity: Average complexity across all functions
        - max_complexity: Highest complexity score in file
        - total_functions: Number of functions analyzed

    Raises:
        TypeError: If file_path is not a string
        FileNotFoundError: If the file does not exist
        CodeAnalysisError: If file cannot be parsed

    Example:
        >>> result = calculate_complexity("/path/to/module.py")
        >>> result["average_complexity"]
        3.5
        >>> result["functions"][0]["complexity"]
        5
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

    functions = []
    complexities = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            complexity = _calculate_node_complexity(node)
            functions.append(
                {
                    "name": node.name,
                    "complexity": complexity,
                    "line_start": node.lineno,
                    "line_end": node.end_lineno or node.lineno,
                }
            )
            complexities.append(complexity)

    if not complexities:
        return {
            "functions": [],
            "average_complexity": 0.0,
            "max_complexity": 0,
            "total_functions": 0,
        }

    return {
        "functions": functions,
        "average_complexity": sum(complexities) / len(complexities),
        "max_complexity": max(complexities),
        "total_functions": len(complexities),
    }


def calculate_function_complexity(file_path: str, function_name: str) -> int:
    """Calculate McCabe cyclomatic complexity for a specific function.

    Analyzes a single function in a Python file and returns its cyclomatic
    complexity score. This is useful for checking specific functions that
    may need refactoring.

    Args:
        file_path: Absolute path to the Python file containing the function
        function_name: Name of the function to analyze

    Returns:
        McCabe cyclomatic complexity score (integer >= 1)

    Raises:
        TypeError: If file_path or function_name is not a string
        FileNotFoundError: If the file does not exist
        CodeAnalysisError: If file cannot be parsed or function not found

    Example:
        >>> complexity = calculate_function_complexity("/path/to/module.py", "process_data")
        >>> complexity
        7
    """
    if not isinstance(file_path, str):
        raise TypeError(f"file_path must be a string, got {type(file_path)}")
    if not isinstance(function_name, str):
        raise TypeError(f"function_name must be a string, got {type(function_name)}")

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

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == function_name:
                return _calculate_node_complexity(node)

    raise CodeAnalysisError(f"Function '{function_name}' not found in {file_path}")


def get_code_metrics(file_path: str) -> dict[str, Any]:
    """Get comprehensive code metrics for a Python file.

    Analyzes a Python file and returns various code quality metrics including
    lines of code, complexity statistics, and function counts.

    Args:
        file_path: Absolute path to the Python file to analyze

    Returns:
        Dictionary containing:
        - total_lines: Total number of lines in file
        - source_lines: Lines of actual code (non-blank, non-comment)
        - comment_lines: Number of comment lines
        - blank_lines: Number of blank lines
        - comment_ratio: Ratio of comments to source lines (0.0-1.0)
        - average_complexity: Average McCabe complexity
        - max_complexity: Maximum McCabe complexity
        - function_count: Number of functions
        - class_count: Number of classes

    Raises:
        TypeError: If file_path is not a string
        FileNotFoundError: If the file does not exist
        CodeAnalysisError: If file cannot be parsed

    Example:
        >>> metrics = get_code_metrics("/path/to/module.py")
        >>> metrics["source_lines"]
        150
        >>> metrics["comment_ratio"]
        0.25
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

    # Count lines
    lines = source.splitlines()
    total_lines = len(lines)
    blank_lines = sum(1 for line in lines if not line.strip())
    comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
    source_lines = total_lines - blank_lines - comment_lines

    # Parse for complexity and counts
    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError as e:
        raise CodeAnalysisError(
            f"Syntax error in {file_path} at line {e.lineno}: {e.msg}"
        )
    except Exception as e:
        raise CodeAnalysisError(f"Error parsing {file_path}: {str(e)}")

    function_count = 0
    class_count = 0
    complexities = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function_count += 1
            complexities.append(_calculate_node_complexity(node))
        elif isinstance(node, ast.ClassDef):
            class_count += 1

    average_complexity = sum(complexities) / len(complexities) if complexities else 0.0
    max_complexity = max(complexities) if complexities else 0
    comment_ratio = comment_lines / source_lines if source_lines > 0 else 0.0

    return {
        "total_lines": total_lines,
        "source_lines": source_lines,
        "comment_lines": comment_lines,
        "blank_lines": blank_lines,
        "comment_ratio": round(comment_ratio, 3),
        "average_complexity": round(average_complexity, 2),
        "max_complexity": max_complexity,
        "function_count": function_count,
        "class_count": class_count,
    }


def identify_complex_functions(file_path: str, threshold: int) -> list[dict[str, Any]]:
    """Identify functions exceeding a complexity threshold.

    Analyzes a Python file and returns all functions with cyclomatic complexity
    exceeding the specified threshold. Useful for finding code that needs
    refactoring or increased test coverage.

    Args:
        file_path: Absolute path to the Python file to analyze
        threshold: Complexity threshold (functions above this are returned)

    Returns:
        List of dictionaries containing:
        - name: Function name
        - complexity: Complexity score
        - line_start: Starting line number
        - line_end: Ending line number
        - suggestion: Refactoring suggestion based on complexity

    Raises:
        TypeError: If file_path is not a string or threshold is not an int
        ValueError: If threshold is less than 1
        FileNotFoundError: If the file does not exist
        CodeAnalysisError: If file cannot be parsed

    Example:
        >>> complex_funcs = identify_complex_functions("/path/to/module.py", 10)
        >>> complex_funcs[0]["name"]
        "process_large_dataset"
        >>> complex_funcs[0]["complexity"]
        15
    """
    if not isinstance(file_path, str):
        raise TypeError(f"file_path must be a string, got {type(file_path)}")
    if not isinstance(threshold, int):
        raise TypeError(f"threshold must be an int, got {type(threshold)}")
    if threshold < 1:
        raise ValueError(f"threshold must be >= 1, got {threshold}")

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

    complex_functions = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            complexity = _calculate_node_complexity(node)
            if complexity > threshold:
                # Generate suggestion based on complexity level
                if complexity > 20:
                    suggestion = "Critical: Refactor immediately into smaller functions"
                elif complexity > 15:
                    suggestion = "High: Consider breaking into helper functions"
                elif complexity > 10:
                    suggestion = "Medium: Review for simplification opportunities"
                else:
                    suggestion = "Low: Minor refactoring may improve readability"

                complex_functions.append(
                    {
                        "name": node.name,
                        "complexity": complexity,
                        "line_start": node.lineno,
                        "line_end": node.end_lineno or node.lineno,
                        "suggestion": suggestion,
                    }
                )

    return complex_functions


def _calculate_node_complexity(node: ast.AST) -> int:
    """Calculate McCabe cyclomatic complexity for an AST node.

    Internal helper function that implements the McCabe complexity calculation.
    Complexity starts at 1 and increases for each decision point.

    Args:
        node: AST node to analyze (typically FunctionDef)

    Returns:
        McCabe cyclomatic complexity score
    """
    complexity = 1  # Base complexity

    for child in ast.walk(node):
        # Decision points that increase complexity
        if isinstance(
            child,
            (
                ast.If,  # if statement
                ast.While,  # while loop
                ast.For,  # for loop
                ast.ExceptHandler,  # except clause
                ast.With,  # with statement
                ast.Assert,  # assert statement
            ),
        ):
            complexity += 1
        # Boolean operators in conditions
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
        # Comprehensions
        elif isinstance(
            child, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)
        ):
            complexity += len(child.generators)

    return complexity
