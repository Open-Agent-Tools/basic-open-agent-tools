"""Tests for code analysis module."""

from pathlib import Path

import pytest

from basic_open_agent_tools.code_analysis import (
    calculate_complexity,
    calculate_function_complexity,
    extract_classes,
    extract_functions,
    extract_imports,
    find_unused_imports,
    get_code_metrics,
    identify_complex_functions,
    organize_imports,
    parse_python_ast,
    scan_directory_for_secrets,
    scan_for_secrets,
    validate_import_order,
    validate_secret_patterns,
)
from basic_open_agent_tools.exceptions import CodeAnalysisError

# Sample Python code for testing
SAMPLE_CODE = '''"""Sample module for testing."""

import os
import sys
import json
from typing import List, Dict
from collections import defaultdict
import unused_module

def simple_function(x: int) -> int:
    """A simple function."""
    return x + 1

def complex_function(x: int, y: int) -> int:
    """A complex function with branches."""
    if x > 0:
        if y > 0:
            return x + y
        else:
            return x - y
    elif x < 0:
        if y > 0:
            return y - x
        else:
            return -(x + y)
    else:
        return y

class MyClass:
    """A sample class."""

    def __init__(self):
        self.value = 0

    def method(self):
        return self.value

async def async_function():
    """An async function."""
    pass
'''

SECRETS_CODE = '''"""Config file with secrets."""

# API Keys
aws_key = "AKIAIOSFODNN7EXAMPLE"
openai_key = "sk-1234567890abcdefghijklmnopqrstuvwxyzABCDEFGH"

# Passwords
db_password = "SuperSecret123!"

# This is just an example key for testing: sk-test-1234
'''


class TestASTParsingFunctions:
    """Test AST parsing functions."""

    def test_parse_python_ast(self, tmp_path: Path) -> None:
        """Test parsing complete AST structure."""
        test_file = tmp_path / "test.py"
        test_file.write_text(SAMPLE_CODE)

        result = parse_python_ast(str(test_file))

        assert "functions" in result
        assert "classes" in result
        assert "imports" in result
        assert "module_docstring" in result
        assert "line_count" in result

        assert len(result["functions"]) >= 3
        assert len(result["classes"]) >= 1
        assert result["module_docstring"] == "Sample module for testing."

    def test_extract_functions(self, tmp_path: Path) -> None:
        """Test extracting function definitions."""
        test_file = tmp_path / "test.py"
        test_file.write_text(SAMPLE_CODE)

        functions = extract_functions(str(test_file))

        assert len(functions) >= 3

        # Check simple function
        simple = [f for f in functions if f["name"] == "simple_function"][0]
        assert simple["params"] == ["x"]
        assert simple["return_type"] == "int"
        assert "is_async" in simple
        assert simple["is_async"] is False

        # Check async function
        async_func = [f for f in functions if f["name"] == "async_function"][0]
        assert async_func["is_async"] is True

    def test_extract_classes(self, tmp_path: Path) -> None:
        """Test extracting class definitions."""
        test_file = tmp_path / "test.py"
        test_file.write_text(SAMPLE_CODE)

        classes = extract_classes(str(test_file))

        assert len(classes) >= 1
        my_class = classes[0]
        assert my_class["name"] == "MyClass"
        assert "__init__" in my_class["methods"]
        assert "method" in my_class["methods"]
        assert my_class["docstring"] == "A sample class."

    def test_extract_imports(self, tmp_path: Path) -> None:
        """Test extracting import statements."""
        test_file = tmp_path / "test.py"
        test_file.write_text(SAMPLE_CODE)

        imports = extract_imports(str(test_file))

        assert "stdlib" in imports
        assert "third_party" in imports
        assert "local" in imports
        assert "all" in imports

        # Check standard library imports
        assert "os" in imports["stdlib"]
        assert "sys" in imports["stdlib"]
        assert "json" in imports["stdlib"]

    def test_file_not_found(self) -> None:
        """Test error handling for missing file."""
        with pytest.raises(FileNotFoundError):
            parse_python_ast("/nonexistent/file.py")

    def test_syntax_error(self, tmp_path: Path) -> None:
        """Test error handling for syntax errors."""
        test_file = tmp_path / "invalid.py"
        test_file.write_text("def invalid syntax()")

        with pytest.raises(CodeAnalysisError) as exc_info:
            parse_python_ast(str(test_file))
        assert "Syntax error" in str(exc_info.value)


class TestComplexityFunctions:
    """Test complexity calculation functions."""

    def test_calculate_complexity(self, tmp_path: Path) -> None:
        """Test calculating complexity for all functions."""
        test_file = tmp_path / "test.py"
        test_file.write_text(SAMPLE_CODE)

        result = calculate_complexity(str(test_file))

        assert "functions" in result
        assert "average_complexity" in result
        assert "max_complexity" in result
        assert "total_functions" in result

        # Simple function should have low complexity
        simple = [f for f in result["functions"] if f["name"] == "simple_function"][0]
        assert simple["complexity"] == 1

        # Complex function should have higher complexity
        complex_func = [
            f for f in result["functions"] if f["name"] == "complex_function"
        ][0]
        assert complex_func["complexity"] >= 5

    def test_calculate_function_complexity(self, tmp_path: Path) -> None:
        """Test calculating complexity for specific function."""
        test_file = tmp_path / "test.py"
        test_file.write_text(SAMPLE_CODE)

        simple_complexity = calculate_function_complexity(
            str(test_file), "simple_function"
        )
        assert simple_complexity == 1

        complex_complexity = calculate_function_complexity(
            str(test_file), "complex_function"
        )
        assert complex_complexity >= 5

    def test_function_not_found(self, tmp_path: Path) -> None:
        """Test error when function doesn't exist."""
        test_file = tmp_path / "test.py"
        test_file.write_text(SAMPLE_CODE)

        with pytest.raises(CodeAnalysisError) as exc_info:
            calculate_function_complexity(str(test_file), "nonexistent_function")
        assert "not found" in str(exc_info.value)

    def test_get_code_metrics(self, tmp_path: Path) -> None:
        """Test getting comprehensive code metrics."""
        test_file = tmp_path / "test.py"
        test_file.write_text(SAMPLE_CODE)

        metrics = get_code_metrics(str(test_file))

        assert "total_lines" in metrics
        assert "source_lines" in metrics
        assert "comment_lines" in metrics
        assert "blank_lines" in metrics
        assert "comment_ratio" in metrics
        assert "average_complexity" in metrics
        assert "function_count" in metrics
        assert "class_count" in metrics

        assert metrics["function_count"] >= 3
        assert metrics["class_count"] >= 1
        assert metrics["total_lines"] > 0

    def test_identify_complex_functions(self, tmp_path: Path) -> None:
        """Test identifying complex functions above threshold."""
        test_file = tmp_path / "test.py"
        test_file.write_text(SAMPLE_CODE)

        # Low threshold should find complex function
        complex_funcs = identify_complex_functions(str(test_file), 4)
        assert len(complex_funcs) > 0

        complex_func = complex_funcs[0]
        assert "name" in complex_func
        assert "complexity" in complex_func
        assert "suggestion" in complex_func
        assert complex_func["complexity"] >= 5

        # High threshold should find nothing
        complex_funcs_high = identify_complex_functions(str(test_file), 100)
        assert len(complex_funcs_high) == 0


class TestImportFunctions:
    """Test import management functions."""

    def test_find_unused_imports(self, tmp_path: Path) -> None:
        """Test finding unused imports."""
        test_file = tmp_path / "test.py"
        test_file.write_text(SAMPLE_CODE)

        unused = find_unused_imports(str(test_file))

        # unused_module is imported but not used
        assert "unused_module" in unused

    def test_organize_imports(self, tmp_path: Path) -> None:
        """Test organizing imports."""
        test_file = tmp_path / "test.py"
        test_file.write_text(SAMPLE_CODE)

        organized = organize_imports(str(test_file))

        # Should have groups separated by blank lines
        assert "\n\n" in organized

        # Should contain all imports
        assert "import os" in organized or "import sys" in organized

    def test_validate_import_order(self, tmp_path: Path) -> None:
        """Test validating import order."""
        # Code with correct order
        correct_code = """import os
import sys

import requests

from .local import helper
"""
        test_file = tmp_path / "correct.py"
        test_file.write_text(correct_code)

        result = validate_import_order(str(test_file))
        assert "is_valid" in result
        assert "violations" in result
        assert "suggestions" in result

        # Code with incorrect order
        incorrect_code = """import requests
import os
"""
        test_file2 = tmp_path / "incorrect.py"
        test_file2.write_text(incorrect_code)

        result2 = validate_import_order(str(test_file2))
        assert result2["is_valid"] is False
        assert len(result2["violations"]) > 0


class TestSecretDetection:
    """Test secret detection functions."""

    def test_scan_for_secrets(self, tmp_path: Path) -> None:
        """Test scanning file for secrets."""
        test_file = tmp_path / "secrets.py"
        test_file.write_text(SECRETS_CODE)

        secrets = scan_for_secrets(str(test_file))

        assert len(secrets) > 0

        # Check for AWS key
        aws_secrets = [s for s in secrets if "AWS" in s["secret_type"]]
        assert len(aws_secrets) > 0

        # Check structure
        secret = secrets[0]
        assert "secret_type" in secret
        assert "line_number" in secret
        assert "confidence" in secret
        assert "context" in secret
        assert "severity" in secret

    def test_scan_directory_for_secrets(self, tmp_path: Path) -> None:
        """Test scanning directory for secrets."""
        # Create test files
        (tmp_path / "file1.py").write_text(SECRETS_CODE)
        (tmp_path / "file2.py").write_text('print("clean")')

        secrets = scan_directory_for_secrets(str(tmp_path))

        assert len(secrets) > 0
        assert all("file_path" in s for s in secrets)

        # Should only find secrets in file1.py
        file1_secrets = [s for s in secrets if "file1.py" in s["file_path"]]
        assert len(file1_secrets) > 0

    def test_validate_secret_patterns(self) -> None:
        """Test validating custom secret patterns."""
        content = """
        INTERNAL_KEY_ABC123
        SECRET_PASSWORD = "test"
        """
        patterns = [r"INTERNAL_KEY_[A-Z0-9]+", r"SECRET_\\w+"]

        results = validate_secret_patterns(content, patterns)

        assert len(results) > 0
        result = results[0]
        assert "pattern" in result
        assert "line_number" in result
        assert "match" in result
        assert "context" in result

    def test_empty_file(self, tmp_path: Path) -> None:
        """Test scanning empty file."""
        test_file = tmp_path / "empty.py"
        test_file.write_text("")

        secrets = scan_for_secrets(str(test_file))
        assert secrets == []


class TestTypeValidation:
    """Test type validation for parameters."""

    def test_parse_python_ast_type_error(self) -> None:
        """Test type error for non-string path."""
        with pytest.raises(TypeError):
            parse_python_ast(123)  # type: ignore

    def test_calculate_function_complexity_type_error(self, tmp_path: Path) -> None:
        """Test type errors for complexity calculation."""
        test_file = tmp_path / "test.py"
        test_file.write_text(SAMPLE_CODE)

        with pytest.raises(TypeError):
            calculate_function_complexity(123, "func")  # type: ignore

        with pytest.raises(TypeError):
            calculate_function_complexity(str(test_file), 123)  # type: ignore

    def test_identify_complex_functions_value_error(self, tmp_path: Path) -> None:
        """Test value error for invalid threshold."""
        test_file = tmp_path / "test.py"
        test_file.write_text(SAMPLE_CODE)

        with pytest.raises(ValueError):
            identify_complex_functions(str(test_file), 0)

    def test_validate_secret_patterns_type_errors(self) -> None:
        """Test type errors for secret pattern validation."""
        with pytest.raises(TypeError):
            validate_secret_patterns(123, [])  # type: ignore

        with pytest.raises(TypeError):
            validate_secret_patterns("content", "not a list")  # type: ignore
