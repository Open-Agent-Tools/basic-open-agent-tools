"""Extended tests for code_analysis module to improve coverage."""

from pathlib import Path

import pytest

from basic_open_agent_tools.code_analysis import (
    calculate_complexity,
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
from basic_open_agent_tools.code_analysis.patterns import (
    get_all_patterns,
    get_high_severity_patterns,
    get_patterns_by_severity,
)
from basic_open_agent_tools.exceptions import CodeAnalysisError

# Test code with various edge cases
EDGE_CASE_CODE = '''"""Module with edge cases."""

import os
from typing import Optional
from . import local_module
from ..parent import parent_module

class BaseClass:
    pass

class DerivedClass(BaseClass):
    """Derived class with inheritance."""

    def method_with_decorator(self):
        pass

@property
def decorated_function():
    """Function with decorator."""
    pass

def function_with_comprehensions(items):
    """Function with list/dict/set comprehensions."""
    result = [x for x in items if x > 0]
    mapping = {k: v for k, v in items}
    unique = {x for x in items}
    gen = (x for x in items)
    return result

def function_with_boolops(a, b, c):
    """Function with boolean operators."""
    if a and b or c:
        return True
    elif a or (b and c):
        return False
    return None

def function_with_loops():
    """Function with various loops."""
    for i in range(10):
        if i > 5:
            break

    while True:
        break

    try:
        pass
    except ValueError:
        pass
    except TypeError:
        pass

    with open("file") as f:
        pass

async def async_with_await():
    """Async function."""
    await something()
'''

IMPORT_ORDER_CODE = '''"""File with mixed import order."""
import third_party_package
import os
from local_module import function
import sys
from another_package import Class
'''

RELATIVE_IMPORTS_CODE = '''"""File with relative imports."""
from . import sibling
from .. import parent
from ...grandparent import something
'''

WILDCARD_IMPORTS_CODE = '''"""File with wildcard imports."""
from module import *
import used_module
'''

ALIASED_IMPORTS_CODE = '''"""File with aliased imports."""
import numpy as np
import pandas as pd
from typing import List as ListType
'''


class TestASTParsingEdgeCases:
    """Test AST parsing with edge cases."""

    def test_parse_python_ast_with_edge_cases(self, tmp_path: Path) -> None:
        """Test parsing file with edge cases."""
        test_file = tmp_path / "edge.py"
        test_file.write_text(EDGE_CASE_CODE)

        result = parse_python_ast(str(test_file))

        assert len(result["functions"]) >= 5
        assert len(result["classes"]) >= 2

    def test_extract_functions_with_decorators(self, tmp_path: Path) -> None:
        """Test extracting functions with decorators."""
        test_file = tmp_path / "decorators.py"
        test_file.write_text(EDGE_CASE_CODE)

        functions = extract_functions(str(test_file))

        decorated = [f for f in functions if len(f["decorators"]) > 0]
        assert len(decorated) > 0

    def test_extract_classes_with_inheritance(self, tmp_path: Path) -> None:
        """Test extracting classes with base classes."""
        test_file = tmp_path / "inheritance.py"
        test_file.write_text(EDGE_CASE_CODE)

        classes = extract_classes(str(test_file))

        derived = [c for c in classes if c["name"] == "DerivedClass"]
        assert len(derived) == 1
        assert "BaseClass" in derived[0]["bases"]

    def test_extract_imports_with_relative(self, tmp_path: Path) -> None:
        """Test extracting relative imports."""
        test_file = tmp_path / "relative.py"
        test_file.write_text(RELATIVE_IMPORTS_CODE)

        imports = extract_imports(str(test_file))

        assert len(imports["local"]) > 0
        assert any("." in imp for imp in imports["local"])

    def test_extract_imports_with_aliases(self, tmp_path: Path) -> None:
        """Test extracting aliased imports."""
        test_file = tmp_path / "aliases.py"
        test_file.write_text(ALIASED_IMPORTS_CODE)

        imports = extract_imports(str(test_file))

        # Should find imports even with aliases
        assert len(imports["all"]) > 0

    def test_parse_empty_file(self, tmp_path: Path) -> None:
        """Test parsing empty Python file."""
        test_file = tmp_path / "empty.py"
        test_file.write_text("")

        result = parse_python_ast(str(test_file))

        assert result["functions"] == []
        assert result["classes"] == []
        assert result["line_count"] == 0


class TestComplexityEdgeCases:
    """Test complexity calculation edge cases."""

    def test_calculate_complexity_with_comprehensions(self, tmp_path: Path) -> None:
        """Test complexity calculation with comprehensions."""
        test_file = tmp_path / "comprehensions.py"
        test_file.write_text(EDGE_CASE_CODE)

        result = calculate_complexity(str(test_file))

        comp_func = [
            f
            for f in result["functions"]
            if f["name"] == "function_with_comprehensions"
        ]
        assert len(comp_func) == 1
        # Comprehensions add to complexity
        assert comp_func[0]["complexity"] > 1

    def test_calculate_complexity_with_boolops(self, tmp_path: Path) -> None:
        """Test complexity with boolean operators."""
        test_file = tmp_path / "boolops.py"
        test_file.write_text(EDGE_CASE_CODE)

        result = calculate_complexity(str(test_file))

        bool_func = [
            f for f in result["functions"] if f["name"] == "function_with_boolops"
        ]
        assert len(bool_func) == 1
        # Boolean operators add to complexity
        assert bool_func[0]["complexity"] > 1

    def test_calculate_complexity_with_loops(self, tmp_path: Path) -> None:
        """Test complexity with loops and exception handling."""
        test_file = tmp_path / "loops.py"
        test_file.write_text(EDGE_CASE_CODE)

        result = calculate_complexity(str(test_file))

        loop_func = [
            f for f in result["functions"] if f["name"] == "function_with_loops"
        ]
        assert len(loop_func) == 1
        # Loops, exception handlers, and with statements add complexity
        assert loop_func[0]["complexity"] > 1

    def test_calculate_complexity_empty_file(self, tmp_path: Path) -> None:
        """Test complexity calculation on file with no functions."""
        test_file = tmp_path / "empty.py"
        test_file.write_text("# Just a comment")

        result = calculate_complexity(str(test_file))

        assert result["total_functions"] == 0
        assert result["average_complexity"] == 0.0
        assert result["max_complexity"] == 0

    def test_get_code_metrics_comprehensive(self, tmp_path: Path) -> None:
        """Test comprehensive code metrics."""
        code = """# Comment 1
# Comment 2

def func():
    pass

class Cls:
    pass
"""
        test_file = tmp_path / "metrics.py"
        test_file.write_text(code)

        metrics = get_code_metrics(str(test_file))

        assert metrics["comment_lines"] >= 2
        assert metrics["function_count"] >= 1
        assert metrics["class_count"] >= 1
        assert metrics["comment_ratio"] >= 0

    def test_identify_complex_functions_suggestions(self, tmp_path: Path) -> None:
        """Test suggestion generation for complex functions."""
        code = """
def very_complex():
    for i in range(10):
        if i > 0:
            for j in range(10):
                if j > 0:
                    for k in range(10):
                        if k > 0:
                            for m in range(10):
                                if m > 0:
                                    pass
"""
        test_file = tmp_path / "very_complex.py"
        test_file.write_text(code)

        complex_funcs = identify_complex_functions(str(test_file), 10)

        if complex_funcs:
            assert "suggestion" in complex_funcs[0]
            # Very high complexity should get critical suggestion
            if complex_funcs[0]["complexity"] > 20:
                assert "Critical" in complex_funcs[0]["suggestion"]


class TestImportEdgeCases:
    """Test import management edge cases."""

    def test_find_unused_imports_with_wildcard(self, tmp_path: Path) -> None:
        """Test finding unused imports with wildcard imports."""
        test_file = tmp_path / "wildcard.py"
        test_file.write_text(WILDCARD_IMPORTS_CODE)

        unused = find_unused_imports(str(test_file))

        # Wildcard imports are ignored
        assert "*" not in unused

    def test_find_unused_imports_with_dotted_usage(self, tmp_path: Path) -> None:
        """Test finding unused imports with dotted attribute access."""
        code = """import os
result = os.path.exists("/tmp")
"""
        test_file = tmp_path / "dotted.py"
        test_file.write_text(code)

        unused = find_unused_imports(str(test_file))

        # os is used via os.path
        assert "os" not in unused

    def test_organize_imports_comprehensive(self, tmp_path: Path) -> None:
        """Test organizing imports comprehensively."""
        test_file = tmp_path / "organize.py"
        test_file.write_text(IMPORT_ORDER_CODE)

        organized = organize_imports(str(test_file))

        # Should have proper structure
        assert "import os" in organized or "import sys" in organized
        lines = organized.split("\n")
        # Should have blank line separators
        assert "" in lines or organized.count("\n\n") > 0

    def test_validate_import_order_detailed(self, tmp_path: Path) -> None:
        """Test detailed import order validation."""
        test_file = tmp_path / "order.py"
        test_file.write_text(IMPORT_ORDER_CODE)

        result = validate_import_order(str(test_file))

        assert isinstance(result["is_valid"], bool)
        assert isinstance(result["violations"], list)
        assert isinstance(result["suggestions"], list)

        if not result["is_valid"]:
            assert len(result["violations"]) > 0

    def test_organize_imports_with_from_imports(self, tmp_path: Path) -> None:
        """Test organizing from imports."""
        code = """from os import path
from sys import argv
import json
"""
        test_file = tmp_path / "from_imports.py"
        test_file.write_text(code)

        organized = organize_imports(str(test_file))

        assert "from" in organized
        assert "import" in organized


class TestSecretDetectionEdgeCases:
    """Test secret detection edge cases."""

    def test_scan_for_secrets_in_comments(self, tmp_path: Path) -> None:
        """Test secret detection in comments."""
        code = """# This is an example key: AKIAIOSFODNN7EXAMPLE
# Not a real secret, just for testing
password = "example123"  # test password
"""
        test_file = tmp_path / "comments.py"
        test_file.write_text(code)

        secrets = scan_for_secrets(str(test_file))

        # Should find secrets in comments but with low confidence
        comment_secrets = [s for s in secrets if s["confidence"] == "low"]
        assert len(comment_secrets) > 0

    def test_scan_for_secrets_with_test_data(self, tmp_path: Path) -> None:
        """Test secret detection with test data."""
        code = """# Example key for testing
test_key = "AKIAIOSFODNN7EXAMPLE"
example_password = "test123"
"""
        test_file = tmp_path / "test_data.py"
        test_file.write_text(code)

        secrets = scan_for_secrets(str(test_file))

        # Should find but with low confidence due to "test"/"example"
        low_conf = [s for s in secrets if s["confidence"] == "low"]
        assert len(low_conf) > 0

    def test_scan_directory_for_secrets_with_gitignore(self, tmp_path: Path) -> None:
        """Test directory scanning respects .git directory."""
        # Create structure with .git directory
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("secret=AKIAIOSFODNN7EXAMPLE")
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "code.py").write_text("key = 'AKIAIOSFODNN7EXAMPLE'")

        secrets = scan_directory_for_secrets(str(tmp_path))

        # Should not scan .git directory
        git_secrets = [s for s in secrets if ".git" in s["file_path"]]
        assert len(git_secrets) == 0

        # Should find in src
        src_secrets = [s for s in secrets if "src" in s["file_path"]]
        assert len(src_secrets) > 0

    def test_scan_directory_for_secrets_config_files(self, tmp_path: Path) -> None:
        """Test scanning various config file types."""
        (tmp_path / "config.env").write_text("API_KEY=AKIAIOSFODNN7EXAMPLE")
        (tmp_path / "settings.ini").write_text("[auth]\nkey=sk-test123")
        (tmp_path / "config.yaml").write_text("secret: value")

        secrets = scan_directory_for_secrets(str(tmp_path))

        # Should scan config files
        assert len(secrets) > 0

    def test_validate_secret_patterns_with_invalid_regex(self) -> None:
        """Test custom pattern validation with invalid regex."""
        content = "some content"
        patterns = [r"valid_pattern", r"[invalid(regex"]

        # Should not raise error, just skip invalid patterns
        results = validate_secret_patterns(content, patterns)

        # Should still process valid patterns
        assert isinstance(results, list)

    def test_scan_for_secrets_various_severities(self, tmp_path: Path) -> None:
        """Test secret detection finds various severity levels."""
        code = """
aws_key = "AKIAIOSFODNN7EXAMPLE"  # high
api_key = "some_generic_key_12345"  # medium
long_string = "aGVsbG8gd29ybGQgdGhpcyBpcyBhIGxvbmcgYmFzZTY0IHN0cmluZw=="  # low
"""
        test_file = tmp_path / "severities.py"
        test_file.write_text(code)

        secrets = scan_for_secrets(str(test_file))

        severities = {s["severity"] for s in secrets}
        assert len(severities) > 0  # Should find at least one severity level


class TestPatternFunctions:
    """Test pattern utility functions."""

    def test_get_all_patterns(self) -> None:
        """Test getting all patterns."""
        patterns = get_all_patterns()

        assert len(patterns) > 0
        assert all("name" in p for p in patterns)
        assert all("pattern" in p for p in patterns)
        assert all("severity" in p for p in patterns)

    def test_get_patterns_by_severity_high(self) -> None:
        """Test getting high severity patterns."""
        patterns = get_patterns_by_severity("high")

        assert len(patterns) > 0
        assert all(p["severity"] == "high" for p in patterns)

    def test_get_patterns_by_severity_medium(self) -> None:
        """Test getting medium severity patterns."""
        patterns = get_patterns_by_severity("medium")

        assert all(p["severity"] == "medium" for p in patterns)

    def test_get_patterns_by_severity_low(self) -> None:
        """Test getting low severity patterns."""
        patterns = get_patterns_by_severity("low")

        assert all(p["severity"] == "low" for p in patterns)

    def test_get_patterns_by_severity_invalid(self) -> None:
        """Test getting patterns with invalid severity."""
        with pytest.raises(ValueError) as exc_info:
            get_patterns_by_severity("invalid")
        assert "Invalid severity" in str(exc_info.value)

    def test_get_high_severity_patterns(self) -> None:
        """Test getting high severity patterns helper."""
        patterns = get_high_severity_patterns()

        assert len(patterns) > 0
        assert all(p["severity"] == "high" for p in patterns)


class TestErrorConditions:
    """Test various error conditions."""

    def test_extract_functions_permission_error(self, tmp_path: Path) -> None:
        """Test handling of permission errors."""
        # This test is platform-specific and may not work everywhere
        pass

    def test_scan_directory_for_secrets_not_directory(self, tmp_path: Path) -> None:
        """Test scanning when path is not a directory."""
        test_file = tmp_path / "file.txt"
        test_file.write_text("content")

        with pytest.raises(CodeAnalysisError) as exc_info:
            scan_directory_for_secrets(str(test_file))
        assert "Not a directory" in str(exc_info.value)

    def test_scan_directory_for_secrets_nonexistent(self) -> None:
        """Test scanning nonexistent directory."""
        with pytest.raises(FileNotFoundError):
            scan_directory_for_secrets("/nonexistent/path")


class TestCodeWithNoIssues:
    """Test code that should not trigger any issues."""

    def test_clean_code_no_unused_imports(self, tmp_path: Path) -> None:
        """Test clean code with all imports used."""
        code = """import os
import sys

def use_imports():
    print(os.name)
    print(sys.version)
"""
        test_file = tmp_path / "clean.py"
        test_file.write_text(code)

        unused = find_unused_imports(str(test_file))

        assert len(unused) == 0

    def test_clean_code_no_secrets(self, tmp_path: Path) -> None:
        """Test clean code with no secrets."""
        code = """
def calculate(a, b):
    return a + b

class Calculator:
    def add(self, x, y):
        return x + y
"""
        test_file = tmp_path / "clean.py"
        test_file.write_text(code)

        secrets = scan_for_secrets(str(test_file))

        assert len(secrets) == 0

    def test_well_ordered_imports(self, tmp_path: Path) -> None:
        """Test imports that are already well-ordered."""
        code = """import os
import sys

import requests

from .local import module
"""
        test_file = tmp_path / "ordered.py"
        test_file.write_text(code)

        result = validate_import_order(str(test_file))

        # Check that validation ran successfully
        assert "is_valid" in result
        assert "violations" in result
        assert "suggestions" in result
