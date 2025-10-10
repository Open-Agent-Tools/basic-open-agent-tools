"""Tests for static analysis output parsers and issue analysis."""

import json

import pytest

from basic_open_agent_tools.exceptions import StaticAnalysisError
from basic_open_agent_tools.static_analysis import (
    filter_issues_by_severity,
    group_issues_by_file,
    parse_mypy_json,
    parse_pytest_json,
    parse_ruff_json,
    prioritize_issues,
    summarize_static_analysis,
)

# Sample ruff JSON output
RUFF_JSON = json.dumps(
    [
        {
            "filename": "src/module.py",
            "location": {"row": 10, "column": 5},
            "code": "F401",
            "message": "unused import",
            "noqa_row": None,
        },
        {
            "filename": "src/module.py",
            "location": {"row": 20, "column": 10},
            "code": "E501",
            "message": "line too long",
            "noqa_row": 20,
        },
        {
            "filename": "src/utils.py",
            "location": {"row": 5, "column": 1},
            "code": "F401",
            "message": "unused import",
            "noqa_row": None,
        },
    ]
)

# Sample mypy JSON output (line-by-line)
MYPY_JSON = """{"file": "src/module.py", "line": 15, "column": 8, "severity": "error", "code": "attr-defined", "message": "Module has no attribute 'foo'"}
{"file": "src/utils.py", "line": 10, "column": 4, "severity": "error", "code": "arg-type", "message": "Argument 1 has incompatible type"}
{"file": "src/module.py", "line": 25, "column": 1, "severity": "note", "code": "misc", "message": "See documentation"}"""

# Sample pytest JSON output
PYTEST_JSON = json.dumps(
    {
        "summary": {"total": 10, "passed": 8, "failed": 2, "skipped": 0},
        "duration": 2.5,
        "tests": [
            {
                "nodeid": "tests/test_module.py::test_function",
                "outcome": "failed",
                "location": ["tests/test_module.py", 10, "test_function"],
                "call": {"longrepr": "AssertionError: expected 5 but got 3"},
            },
            {
                "nodeid": "tests/test_utils.py::test_helper",
                "outcome": "failed",
                "location": ["tests/test_utils.py", 20, "test_helper"],
                "call": {"longrepr": "TypeError: expected str but got int"},
            },
        ],
    }
)


class TestParseRuffJson:
    """Tests for parse_ruff_json function."""

    def test_parse_ruff_json_basic(self):
        """Test basic ruff JSON parsing."""
        issues = parse_ruff_json(RUFF_JSON)

        assert len(issues) == 3
        assert issues[0]["file"] == "src/module.py"
        assert issues[0]["line"] == 10
        assert issues[0]["column"] == 5
        assert issues[0]["rule_code"] == "F401"
        assert issues[0]["severity"] == "error"
        assert issues[0]["message"] == "unused import"

    def test_parse_ruff_json_warning_detection(self):
        """Test that noqa_row presence makes it a warning."""
        issues = parse_ruff_json(RUFF_JSON)

        # Second issue has noqa_row, should be warning
        assert issues[1]["severity"] == "warning"

    def test_parse_ruff_json_empty(self):
        """Test parsing empty ruff output."""
        issues = parse_ruff_json("[]")
        assert issues == []

    def test_parse_ruff_json_invalid_type(self):
        """Test that non-string input raises TypeError."""
        with pytest.raises(TypeError, match="json_output must be a string"):
            parse_ruff_json(123)  # type: ignore[arg-type]

    def test_parse_ruff_json_invalid_json(self):
        """Test that invalid JSON raises StaticAnalysisError."""
        with pytest.raises(StaticAnalysisError, match="Invalid JSON"):
            parse_ruff_json("not valid json")

    def test_parse_ruff_json_wrong_format(self):
        """Test that non-list JSON raises StaticAnalysisError."""
        with pytest.raises(StaticAnalysisError, match="Expected list"):
            parse_ruff_json('{"not": "a list"}')


class TestParseMypyJson:
    """Tests for parse_mypy_json function."""

    def test_parse_mypy_json_basic(self):
        """Test basic mypy JSON parsing."""
        errors = parse_mypy_json(MYPY_JSON)

        assert len(errors) == 3
        assert errors[0]["file"] == "src/module.py"
        assert errors[0]["line"] == 15
        assert errors[0]["column"] == 8
        assert errors[0]["severity"] == "error"
        assert errors[0]["error_code"] == "attr-defined"

    def test_parse_mypy_json_note_severity(self):
        """Test that note severity is preserved."""
        errors = parse_mypy_json(MYPY_JSON)

        assert errors[2]["severity"] == "note"

    def test_parse_mypy_json_empty(self):
        """Test parsing empty mypy output."""
        errors = parse_mypy_json("")
        assert errors == []

    def test_parse_mypy_json_invalid_type(self):
        """Test that non-string input raises TypeError."""
        with pytest.raises(TypeError, match="json_output must be a string"):
            parse_mypy_json([])  # type: ignore[arg-type]

    def test_parse_mypy_json_malformed_lines(self):
        """Test that malformed JSON lines are skipped."""
        malformed = """{"file": "test.py", "line": 1}
not json
{"file": "test2.py", "line": 2, "severity": "error", "code": "misc", "message": "test"}"""

        errors = parse_mypy_json(malformed)
        # Should only parse the valid lines
        assert len(errors) == 2


class TestParsePytestJson:
    """Tests for parse_pytest_json function."""

    def test_parse_pytest_json_basic(self):
        """Test basic pytest JSON parsing."""
        report = parse_pytest_json(PYTEST_JSON)

        assert report["total_tests"] == 10
        assert report["passed"] == 8
        assert report["failed"] == 2
        assert report["skipped"] == 0
        assert report["duration"] == 2.5

    def test_parse_pytest_json_failures(self):
        """Test that failures are extracted correctly."""
        report = parse_pytest_json(PYTEST_JSON)

        assert len(report["failures"]) == 2
        assert (
            report["failures"][0]["test_name"] == "tests/test_module.py::test_function"
        )
        assert report["failures"][0]["file"] == "tests/test_module.py"
        assert report["failures"][0]["line"] == 10

    def test_parse_pytest_json_empty_summary(self):
        """Test parsing pytest output with empty summary."""
        empty_json = json.dumps({"summary": {}, "tests": []})
        report = parse_pytest_json(empty_json)

        assert report["total_tests"] == 0
        assert report["passed"] == 0
        assert report["failures"] == []

    def test_parse_pytest_json_invalid_type(self):
        """Test that non-string input raises TypeError."""
        with pytest.raises(TypeError, match="json_output must be a string"):
            parse_pytest_json({"not": "a string"})  # type: ignore[arg-type]

    def test_parse_pytest_json_invalid_json(self):
        """Test that invalid JSON raises StaticAnalysisError."""
        with pytest.raises(StaticAnalysisError, match="Invalid JSON"):
            parse_pytest_json("not json")

    def test_parse_pytest_json_wrong_format(self):
        """Test that non-dict JSON raises StaticAnalysisError."""
        with pytest.raises(StaticAnalysisError, match="Expected dict"):
            parse_pytest_json("[1, 2, 3]")


class TestSummarizeStaticAnalysis:
    """Tests for summarize_static_analysis function."""

    def test_summarize_static_analysis_basic(self):
        """Test basic static analysis summary."""
        summary = summarize_static_analysis(RUFF_JSON, MYPY_JSON)

        assert summary["total_issues"] == 6  # 3 from ruff + 3 from mypy
        assert summary["by_tool"]["ruff"] == 3
        assert summary["by_tool"]["mypy"] == 3

    def test_summarize_static_analysis_by_severity(self):
        """Test that severity counts are correct."""
        summary = summarize_static_analysis(RUFF_JSON, MYPY_JSON)

        assert summary["by_severity"]["error"] == 4  # 2 from ruff + 2 from mypy
        assert summary["by_severity"]["warning"] == 1  # 1 from ruff
        assert summary["by_severity"]["note"] == 1  # 1 from mypy

    def test_summarize_static_analysis_by_file(self):
        """Test that file counts are correct."""
        summary = summarize_static_analysis(RUFF_JSON, MYPY_JSON)

        assert summary["by_file"]["src/module.py"] == 4
        assert summary["by_file"]["src/utils.py"] == 2

    def test_summarize_static_analysis_top_issues(self):
        """Test that top issues are identified."""
        summary = summarize_static_analysis(RUFF_JSON, MYPY_JSON)

        assert len(summary["top_issues"]) > 0
        # F401 appears twice
        f401_issue = next(
            (i for i in summary["top_issues"] if i["code"] == "F401"), None
        )
        assert f401_issue is not None
        assert f401_issue["count"] == 2

    def test_summarize_static_analysis_invalid_types(self):
        """Test that non-string inputs raise TypeError."""
        with pytest.raises(TypeError, match="ruff_json must be a string"):
            summarize_static_analysis(123, MYPY_JSON)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="mypy_json must be a string"):
            summarize_static_analysis(RUFF_JSON, 456)  # type: ignore[arg-type]


class TestFilterIssuesBySeverity:
    """Tests for filter_issues_by_severity function."""

    def test_filter_issues_by_severity_error(self):
        """Test filtering by error severity."""
        issues = parse_ruff_json(RUFF_JSON)
        errors = filter_issues_by_severity(issues, "error")

        assert len(errors) == 2
        assert all(issue["severity"] == "error" for issue in errors)

    def test_filter_issues_by_severity_warning(self):
        """Test filtering by warning severity."""
        issues = parse_ruff_json(RUFF_JSON)
        warnings = filter_issues_by_severity(issues, "warning")

        assert len(warnings) == 1
        assert warnings[0]["severity"] == "warning"

    def test_filter_issues_by_severity_no_match(self):
        """Test filtering with no matches."""
        issues = parse_ruff_json(RUFF_JSON)
        notes = filter_issues_by_severity(issues, "note")

        assert notes == []

    def test_filter_issues_by_severity_invalid_types(self):
        """Test that invalid types raise TypeError."""
        with pytest.raises(TypeError, match="issues must be a list"):
            filter_issues_by_severity("not a list", "error")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="severity must be a string"):
            filter_issues_by_severity([], 123)  # type: ignore[arg-type]

    def test_filter_issues_by_severity_invalid_item(self):
        """Test that non-dict items raise ValueError."""
        with pytest.raises(ValueError, match="must be dicts"):
            filter_issues_by_severity(["not a dict"], "error")  # type: ignore[list-item]


class TestGroupIssuesByFile:
    """Tests for group_issues_by_file function."""

    def test_group_issues_by_file_basic(self):
        """Test basic grouping by file."""
        issues = parse_ruff_json(RUFF_JSON)
        grouped = group_issues_by_file(issues)

        assert len(grouped) == 2
        assert "src/module.py" in grouped
        assert "src/utils.py" in grouped
        assert len(grouped["src/module.py"]) == 2
        assert len(grouped["src/utils.py"]) == 1

    def test_group_issues_by_file_empty(self):
        """Test grouping empty issue list."""
        grouped = group_issues_by_file([])
        assert grouped == {}

    def test_group_issues_by_file_unknown(self):
        """Test that issues without file are grouped as unknown."""
        issues = [{"line": 1, "message": "test"}]  # No file field
        grouped = group_issues_by_file(issues)

        assert "unknown" in grouped
        assert len(grouped["unknown"]) == 1

    def test_group_issues_by_file_invalid_type(self):
        """Test that non-list input raises TypeError."""
        with pytest.raises(TypeError, match="issues must be a list"):
            group_issues_by_file("not a list")  # type: ignore[arg-type]

    def test_group_issues_by_file_invalid_item(self):
        """Test that non-dict items raise ValueError."""
        with pytest.raises(ValueError, match="must be dicts"):
            group_issues_by_file(["not a dict"])  # type: ignore[list-item]


class TestPrioritizeIssues:
    """Tests for prioritize_issues function."""

    def test_prioritize_issues_basic(self):
        """Test basic issue prioritization."""
        issues = parse_ruff_json(RUFF_JSON)
        prioritized = prioritize_issues(issues)

        assert len(prioritized) == 3
        # All items should have priority_score
        assert all("priority_score" in issue for issue in prioritized)

    def test_prioritize_issues_severity_order(self):
        """Test that errors are prioritized higher than warnings."""
        issues = parse_ruff_json(RUFF_JSON)
        prioritized = prioritize_issues(issues)

        # Find error and warning
        errors = [i for i in prioritized if i["severity"] == "error"]
        warnings = [i for i in prioritized if i["severity"] == "warning"]

        if errors and warnings:
            # Errors should have higher scores than warnings
            assert errors[0]["priority_score"] > warnings[0]["priority_score"]

    def test_prioritize_issues_frequency_bonus(self):
        """Test that frequent issues get bonus points."""
        issues = parse_ruff_json(RUFF_JSON)
        prioritized = prioritize_issues(issues)

        # F401 appears twice, should have frequency bonus
        f401_issues = [i for i in prioritized if i["rule_code"] == "F401"]
        e501_issues = [i for i in prioritized if i["rule_code"] == "E501"]

        # F401 appears 2 times (frequency 2), E501 appears 1 time
        # Both are same severity (one error, one warning for F401)
        # The frequent F401 error should be higher priority
        f401_errors = [i for i in f401_issues if i["severity"] == "error"]
        if f401_errors and e501_issues:
            assert f401_errors[0]["priority_score"] > e501_issues[0]["priority_score"]

    def test_prioritize_issues_empty(self):
        """Test prioritizing empty issue list."""
        prioritized = prioritize_issues([])
        assert prioritized == []

    def test_prioritize_issues_invalid_type(self):
        """Test that non-list input raises TypeError."""
        with pytest.raises(TypeError, match="issues must be a list"):
            prioritize_issues("not a list")  # type: ignore[arg-type]

    def test_prioritize_issues_invalid_item(self):
        """Test that non-dict items raise ValueError."""
        with pytest.raises(ValueError, match="must be dicts"):
            prioritize_issues([123])  # type: ignore[list-item]
