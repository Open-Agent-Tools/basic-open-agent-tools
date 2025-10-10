"""JSON output parsers for static analysis tools.

This module provides functions to parse JSON output from ruff, mypy, and pytest
into structured formats that agents can use for analysis.
"""

import json
from typing import Any

from basic_open_agent_tools.exceptions import StaticAnalysisError


def parse_ruff_json(json_output: str) -> list[dict[str, Any]]:
    """Parse ruff JSON output into structured format.

    Parses the JSON output from ruff linter and returns a structured list of
    issues with file paths, line numbers, severity, and messages.

    Args:
        json_output: JSON string output from ruff (use --output-format=json)

    Returns:
        List of dictionaries, each containing:
        - file: File path where issue was found
        - line: Line number
        - column: Column number
        - rule_code: Ruff rule code (e.g., "F401")
        - severity: Severity level ("error", "warning")
        - message: Issue description

    Raises:
        TypeError: If json_output is not a string
        StaticAnalysisError: If JSON cannot be parsed

    Example:
        >>> output = subprocess.run(["ruff", "check", "--output-format=json", "src/"], capture_output=True, text=True)
        >>> issues = parse_ruff_json(output.stdout)
        >>> issues[0]["rule_code"]
        "F401"
    """
    if not isinstance(json_output, str):
        raise TypeError(f"json_output must be a string, got {type(json_output)}")

    try:
        data = json.loads(json_output)
    except json.JSONDecodeError as e:
        raise StaticAnalysisError(f"Invalid JSON in ruff output: {str(e)}")

    if not isinstance(data, list):
        raise StaticAnalysisError(f"Expected list from ruff JSON, got {type(data)}")

    issues = []
    for item in data:
        if not isinstance(item, dict):
            continue

        issues.append(
            {
                "file": item.get("filename", "unknown"),
                "line": item.get("location", {}).get("row", 0),
                "column": item.get("location", {}).get("column", 0),
                "rule_code": item.get("code", "unknown"),
                "severity": "error" if item.get("noqa_row") is None else "warning",
                "message": item.get("message", ""),
            }
        )

    return issues


def parse_mypy_json(json_output: str) -> list[dict[str, Any]]:
    """Parse mypy JSON output into structured format.

    Parses the JSON output from mypy type checker and returns a structured list
    of type errors with file paths, line numbers, and messages.

    Args:
        json_output: JSON string output from mypy (use --output=json)

    Returns:
        List of dictionaries, each containing:
        - file: File path where error was found
        - line: Line number
        - column: Column number
        - severity: Severity level ("error", "note")
        - error_code: Mypy error code (e.g., "attr-defined")
        - message: Error description

    Raises:
        TypeError: If json_output is not a string
        StaticAnalysisError: If JSON cannot be parsed

    Example:
        >>> output = subprocess.run(["mypy", "--output=json", "src/"], capture_output=True, text=True)
        >>> errors = parse_mypy_json(output.stdout)
        >>> errors[0]["error_code"]
        "attr-defined"
    """
    if not isinstance(json_output, str):
        raise TypeError(f"json_output must be a string, got {type(json_output)}")

    # Mypy outputs one JSON object per line
    errors = []
    for line in json_output.strip().split("\n"):
        if not line.strip():
            continue

        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue

        if not isinstance(item, dict):
            continue

        errors.append(
            {
                "file": item.get("file", "unknown"),
                "line": item.get("line", 0),
                "column": item.get("column", 0),
                "severity": item.get("severity", "error"),
                "error_code": item.get("code", "unknown"),
                "message": item.get("message", ""),
            }
        )

    return errors


def parse_pytest_json(json_output: str) -> dict[str, Any]:
    """Parse pytest JSON report into structured format.

    Parses the JSON output from pytest test runner and returns a structured
    summary with passed/failed counts, coverage information, and specific failures.

    Args:
        json_output: JSON string output from pytest (use --json-report)

    Returns:
        Dictionary containing:
        - total_tests: Total number of tests run
        - passed: Number of tests passed
        - failed: Number of tests failed
        - skipped: Number of tests skipped
        - duration: Total duration in seconds
        - failures: List of failed test details

    Raises:
        TypeError: If json_output is not a string
        StaticAnalysisError: If JSON cannot be parsed

    Example:
        >>> output = subprocess.run(["pytest", "--json-report", "--json-report-file=/dev/stdout"], capture_output=True, text=True)
        >>> report = parse_pytest_json(output.stdout)
        >>> report["passed"]
        42
    """
    if not isinstance(json_output, str):
        raise TypeError(f"json_output must be a string, got {type(json_output)}")

    try:
        data = json.loads(json_output)
    except json.JSONDecodeError as e:
        raise StaticAnalysisError(f"Invalid JSON in pytest output: {str(e)}")

    if not isinstance(data, dict):
        raise StaticAnalysisError(f"Expected dict from pytest JSON, got {type(data)}")

    # Extract summary information
    summary = data.get("summary", {})

    failures = []
    for test in data.get("tests", []):
        if test.get("outcome") == "failed":
            failures.append(
                {
                    "test_name": test.get("nodeid", "unknown"),
                    "file": test.get("location", ["unknown"])[0],
                    "line": test.get("location", [0, 0])[1],
                    "message": test.get("call", {}).get("longrepr", ""),
                }
            )

    return {
        "total_tests": summary.get("total", 0),
        "passed": summary.get("passed", 0),
        "failed": summary.get("failed", 0),
        "skipped": summary.get("skipped", 0),
        "duration": data.get("duration", 0.0),
        "failures": failures,
    }


def summarize_static_analysis(ruff_json: str, mypy_json: str) -> dict[str, Any]:
    """Combine multiple tool outputs into comprehensive summary.

    Combines ruff and mypy outputs into a single summary with total issue counts,
    breakdown by severity, and issues grouped by file.

    Args:
        ruff_json: JSON string output from ruff
        mypy_json: JSON string output from mypy

    Returns:
        Dictionary containing:
        - total_issues: Total number of issues found
        - by_severity: Count of issues by severity level
        - by_tool: Count of issues by tool
        - by_file: Issues grouped by file path
        - top_issues: Top 10 most common issue types

    Raises:
        TypeError: If arguments are not strings
        StaticAnalysisError: If JSON cannot be parsed

    Example:
        >>> summary = summarize_static_analysis(ruff_output, mypy_output)
        >>> summary["total_issues"]
        15
        >>> summary["by_severity"]["error"]
        10
    """
    if not isinstance(ruff_json, str):
        raise TypeError(f"ruff_json must be a string, got {type(ruff_json)}")
    if not isinstance(mypy_json, str):
        raise TypeError(f"mypy_json must be a string, got {type(mypy_json)}")

    # Parse both outputs
    ruff_issues = parse_ruff_json(ruff_json)
    mypy_issues = parse_mypy_json(mypy_json)

    all_issues = []

    # Add tool identifier to each issue
    for issue in ruff_issues:
        issue["tool"] = "ruff"
        all_issues.append(issue)

    for issue in mypy_issues:
        issue["tool"] = "mypy"
        all_issues.append(issue)

    # Count by severity
    by_severity: dict[str, int] = {}
    for issue in all_issues:
        severity = issue.get("severity", "unknown")
        by_severity[severity] = by_severity.get(severity, 0) + 1

    # Count by tool
    by_tool = {"ruff": len(ruff_issues), "mypy": len(mypy_issues)}

    # Group by file
    by_file: dict[str, list[dict[str, Any]]] = {}
    for issue in all_issues:
        file_path = issue.get("file", "unknown")
        if file_path not in by_file:
            by_file[file_path] = []
        by_file[file_path].append(issue)

    # Find top issues (by rule code / error code)
    issue_counts: dict[str, int] = {}
    for issue in all_issues:
        code = issue.get("rule_code") or issue.get("error_code", "unknown")
        issue_counts[code] = issue_counts.get(code, 0) + 1

    # Sort by count descending
    top_issues = sorted(
        [{"code": code, "count": count} for code, count in issue_counts.items()],
        key=lambda x: x["count"],  # type: ignore[arg-type,return-value]
        reverse=True,
    )[:10]

    return {
        "total_issues": len(all_issues),
        "by_severity": by_severity,
        "by_tool": by_tool,
        "by_file": {k: len(v) for k, v in by_file.items()},  # Just counts for summary
        "top_issues": top_issues,
    }
