"""Secret detection utilities for code scanning.

This module provides functions to scan Python code for hardcoded secrets,
credentials, and sensitive information using pattern matching.
"""

import os
import re
from re import Pattern
from typing import Any

from basic_open_agent_tools.code_analysis.patterns import (
    get_all_patterns,
)
from basic_open_agent_tools.exceptions import CodeAnalysisError


def scan_for_secrets(file_path: str) -> list[dict[str, Any]]:
    """Scan a Python file for hardcoded secrets and credentials.

    Analyzes a file for common secret patterns including API keys, passwords,
    private keys, and database credentials. Uses pattern matching to identify
    potential security issues.

    Args:
        file_path: Absolute path to the file to scan

    Returns:
        List of dictionaries, each containing:
        - secret_type: Type of secret detected
        - line_number: Line where secret was found
        - confidence: Detection confidence ("high", "medium", "low")
        - context: Surrounding code context
        - severity: Severity level of the finding

    Raises:
        TypeError: If file_path is not a string
        FileNotFoundError: If the file does not exist
        CodeAnalysisError: If file cannot be read

    Example:
        >>> secrets = scan_for_secrets("/path/to/config.py")
        >>> secrets[0]["secret_type"]
        "AWS Access Key ID"
        >>> secrets[0]["line_number"]
        15
    """
    if not isinstance(file_path, str):
        raise TypeError(f"file_path must be a string, got {type(file_path)}")

    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise CodeAnalysisError(f"Error reading file {file_path}: {str(e)}")

    findings = []
    patterns = get_all_patterns()

    for line_num, line in enumerate(lines, start=1):
        # Skip comments (but still scan them for accidental secrets)
        is_comment = line.strip().startswith("#")

        for pattern_info in patterns:
            pattern = pattern_info["pattern"]
            try:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for _match in matches:
                    # Get context (current line trimmed)
                    context = line.strip()

                    # Determine confidence based on context
                    confidence = "high"
                    if is_comment:
                        confidence = "low"  # Comments are less critical
                    elif "example" in line.lower() or "test" in line.lower():
                        confidence = "low"  # Likely example/test data
                    elif pattern_info["name"] == "High Entropy String":
                        confidence = "low"  # Generic pattern, lower confidence

                    findings.append(
                        {
                            "secret_type": pattern_info["name"],
                            "line_number": line_num,
                            "confidence": confidence,
                            "context": context,
                            "severity": pattern_info["severity"],
                            "description": pattern_info["description"],
                        }
                    )
            except re.error:
                # Skip invalid regex patterns
                continue

    return findings


def scan_directory_for_secrets(directory_path: str) -> list[dict[str, Any]]:
    """Recursively scan a directory for hardcoded secrets.

    Scans all Python files in a directory tree for hardcoded secrets and
    credentials. Returns comprehensive results with file paths and line numbers.

    Args:
        directory_path: Absolute path to the directory to scan

    Returns:
        List of dictionaries, each containing:
        - file_path: Path to file containing the secret
        - secret_type: Type of secret detected
        - line_number: Line where secret was found
        - confidence: Detection confidence
        - severity: Severity level
        - context: Code context

    Raises:
        TypeError: If directory_path is not a string
        FileNotFoundError: If the directory does not exist
        CodeAnalysisError: If directory cannot be accessed

    Example:
        >>> secrets = scan_directory_for_secrets("/path/to/project")
        >>> len(secrets)
        3
        >>> secrets[0]["file_path"]
        "/path/to/project/config.py"
    """
    if not isinstance(directory_path, str):
        raise TypeError(f"directory_path must be a string, got {type(directory_path)}")

    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Directory not found: {directory_path}")

    if not os.path.isdir(directory_path):
        raise CodeAnalysisError(f"Not a directory: {directory_path}")

    all_findings = []

    try:
        for root, dirs, files in os.walk(directory_path):
            # Skip common directories that shouldn't be scanned
            dirs[:] = [
                d
                for d in dirs
                if d not in [".git", ".venv", "venv", "__pycache__", "node_modules"]
            ]

            for file in files:
                # Scan Python files and common config files
                if file.endswith(
                    (".py", ".env", ".ini", ".conf", ".cfg", ".yaml", ".yml", ".json")
                ):
                    file_path = os.path.join(root, file)
                    try:
                        file_secrets = scan_for_secrets(file_path)
                        for secret in file_secrets:
                            secret["file_path"] = file_path
                        all_findings.extend(file_secrets)
                    except (FileNotFoundError, CodeAnalysisError):
                        # Skip files that can't be read
                        continue
    except Exception as e:
        raise CodeAnalysisError(f"Error scanning directory {directory_path}: {str(e)}")

    return all_findings


def validate_secret_patterns(content: str, patterns: list[str]) -> list[dict[str, Any]]:
    """Check content against custom secret patterns.

    Validates text content against a list of custom regex patterns to detect
    secrets or sensitive information. Useful for organization-specific patterns.

    Args:
        content: Text content to scan
        patterns: List of regex pattern strings to check against

    Returns:
        List of dictionaries, each containing:
        - pattern: The regex pattern that matched
        - line_number: Line where match was found
        - match: The matched text
        - context: Full line context

    Raises:
        TypeError: If content is not a string or patterns is not a list
        ValueError: If any pattern is not a valid string

    Example:
        >>> patterns = [r"INTERNAL_KEY_[A-Z0-9]+", r"SECRET_\\w+"]
        >>> results = validate_secret_patterns(code_content, patterns)
        >>> results[0]["pattern"]
        "INTERNAL_KEY_[A-Z0-9]+"
    """
    if not isinstance(content, str):
        raise TypeError(f"content must be a string, got {type(content)}")
    if not isinstance(patterns, list):
        raise TypeError(f"patterns must be a list, got {type(patterns)}")

    for pattern in patterns:
        if not isinstance(pattern, str):
            raise ValueError(f"All patterns must be strings, got {type(pattern)}")

    findings = []
    lines = content.splitlines()

    for pattern_str in patterns:
        try:
            compiled_pattern: Pattern[str] = re.compile(pattern_str, re.IGNORECASE)
        except re.error:
            # Skip invalid patterns but don't fail the entire function
            continue

        for line_num, line in enumerate(lines, start=1):
            matches = compiled_pattern.finditer(line)
            for match in matches:
                findings.append(
                    {
                        "pattern": pattern_str,
                        "line_number": line_num,
                        "match": match.group(0),
                        "context": line.strip(),
                    }
                )

    return findings
