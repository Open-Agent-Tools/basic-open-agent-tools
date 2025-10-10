"""Issue analysis and prioritization utilities for static analysis results.

This module provides functions to filter, group, and prioritize issues from
static analysis tools to help agents focus on the most important problems.
"""

from typing import Any


def filter_issues_by_severity(
    issues: list[dict[str, Any]], severity: str
) -> list[dict[str, Any]]:
    """Filter static analysis issues by severity level.

    Filters a list of issues to include only those matching the specified
    severity level. Useful for focusing on critical errors or specific issue types.

    Args:
        issues: List of issue dictionaries from parse_ruff_json or parse_mypy_json
        severity: Severity level to filter by (e.g., "error", "warning", "note")

    Returns:
        List of filtered issue dictionaries matching the severity level

    Raises:
        TypeError: If issues is not a list or severity is not a string
        ValueError: If issues list contains non-dict items

    Example:
        >>> issues = parse_ruff_json(ruff_output)
        >>> errors = filter_issues_by_severity(issues, "error")
        >>> len(errors)
        5
        >>> all(issue["severity"] == "error" for issue in errors)
        True
    """
    if not isinstance(issues, list):
        raise TypeError(f"issues must be a list, got {type(issues)}")
    if not isinstance(severity, str):
        raise TypeError(f"severity must be a string, got {type(severity)}")

    filtered = []
    for issue in issues:
        if not isinstance(issue, dict):
            raise ValueError(f"All items in issues must be dicts, got {type(issue)}")

        if issue.get("severity") == severity:
            filtered.append(issue)

    return filtered


def group_issues_by_file(
    issues: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Group static analysis issues by file path.

    Groups issues into a dictionary mapping file paths to lists of issues
    in those files. Useful for organizing issues by location.

    Args:
        issues: List of issue dictionaries from parse_ruff_json or parse_mypy_json

    Returns:
        Dictionary mapping file paths to lists of issues in those files

    Raises:
        TypeError: If issues is not a list
        ValueError: If issues list contains non-dict items

    Example:
        >>> issues = parse_ruff_json(ruff_output)
        >>> by_file = group_issues_by_file(issues)
        >>> by_file["src/module.py"]
        [{'file': 'src/module.py', 'line': 10, ...}, ...]
        >>> len(by_file)
        3
    """
    if not isinstance(issues, list):
        raise TypeError(f"issues must be a list, got {type(issues)}")

    grouped: dict[str, list[dict[str, Any]]] = {}

    for issue in issues:
        if not isinstance(issue, dict):
            raise ValueError(f"All items in issues must be dicts, got {type(issue)}")

        file_path = issue.get("file", "unknown")
        if file_path not in grouped:
            grouped[file_path] = []
        grouped[file_path].append(issue)

    return grouped


def prioritize_issues(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort issues by priority based on severity and frequency.

    Assigns priority scores to issues and sorts them with highest priority first.
    Priority is calculated based on severity level and issue type frequency.

    Priority scoring:
    - error severity: 100 points
    - warning severity: 50 points
    - note severity: 25 points
    - Other severities: 10 points

    Args:
        issues: List of issue dictionaries from parse_ruff_json or parse_mypy_json

    Returns:
        List of issue dictionaries sorted by priority (highest first),
        each with added "priority_score" field

    Raises:
        TypeError: If issues is not a list
        ValueError: If issues list contains non-dict items

    Example:
        >>> issues = parse_ruff_json(ruff_output)
        >>> prioritized = prioritize_issues(issues)
        >>> prioritized[0]["priority_score"]
        100
        >>> prioritized[0]["severity"]
        "error"
        >>> prioritized[-1]["severity"]
        "note"
    """
    if not isinstance(issues, list):
        raise TypeError(f"issues must be a list, got {type(issues)}")

    # Count issue type frequency
    issue_counts: dict[str, int] = {}
    for issue in issues:
        if not isinstance(issue, dict):
            raise ValueError(f"All items in issues must be dicts, got {type(issue)}")

        # Use rule_code (ruff) or error_code (mypy) as the issue type
        issue_type = issue.get("rule_code") or issue.get("error_code") or "unknown"
        issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1

    # Calculate priority scores
    scored_issues = []
    for issue in issues:
        severity = issue.get("severity", "unknown")

        # Base score from severity
        if severity == "error":
            base_score = 100
        elif severity == "warning":
            base_score = 50
        elif severity == "note":
            base_score = 25
        else:
            base_score = 10

        # Frequency bonus (up to 20 points for very common issues)
        issue_type = issue.get("rule_code") or issue.get("error_code") or "unknown"
        frequency = issue_counts.get(issue_type, 1)
        frequency_bonus = min(20, frequency * 2)

        priority_score = base_score + frequency_bonus

        # Create new dict with priority score
        scored_issue = dict(issue)
        scored_issue["priority_score"] = priority_score
        scored_issues.append(scored_issue)

    # Sort by priority score descending
    scored_issues.sort(key=lambda x: x["priority_score"], reverse=True)

    return scored_issues
