"""CSV processing utilities for AI agents."""

import csv
import io
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..exceptions import DataError
from ..types import DataDict, PathLike


def read_csv_file(
    file_path: PathLike, delimiter: str = ",", headers: bool = True
) -> List[DataDict]:
    """Read CSV file and return as list of dictionaries.

    Args:
        file_path: Path to the CSV file
        delimiter: CSV field delimiter
        headers: Whether first row contains headers

    Returns:
        List of dictionaries representing CSV rows

    Raises:
        DataError: If file cannot be read or parsed
        TypeError: If arguments have wrong types

    Example:
        >>> # Assuming file contains: name,age\\nAlice,25\\nBob,30
        >>> data = read_csv_file("people.csv")
        >>> data
        [{'name': 'Alice', 'age': '25'}, {'name': 'Bob', 'age': '30'}]
    """
    if not isinstance(file_path, (str, Path)):
        raise TypeError("file_path must be a string or Path")
    if not isinstance(delimiter, str):
        raise TypeError("delimiter must be a string")
    if not isinstance(headers, bool):
        raise TypeError("headers must be a boolean")

    file_path = Path(file_path)

    try:
        with open(file_path, encoding="utf-8", newline="") as csvfile:
            if headers:
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                return [dict(row) for row in reader]
            else:
                reader = csv.reader(csvfile, delimiter=delimiter)  # type: ignore[assignment]
                rows = list(reader)
                if not rows:
                    return []
                # Create numeric headers for headerless CSV
                num_cols = len(rows[0]) if rows else 0
                headers_list = [f"col_{i}" for i in range(num_cols)]
                return [dict(zip(headers_list, row)) for row in rows]
    except FileNotFoundError:
        raise DataError(f"CSV file not found: {file_path}")
    except UnicodeDecodeError as e:
        raise DataError(f"Failed to decode CSV file {file_path}: {e}")
    except csv.Error as e:
        raise DataError(f"Failed to parse CSV file {file_path}: {e}")


def write_csv_file(
    data: List[DataDict],
    file_path: PathLike,
    delimiter: str = ",",
    headers: bool = True,
) -> None:
    """Write list of dictionaries to CSV file.

    Args:
        data: List of dictionaries to write
        file_path: Path where CSV file will be created
        delimiter: CSV field delimiter
        headers: Whether to write headers as first row

    Raises:
        DataError: If file cannot be written
        TypeError: If arguments have wrong types

    Example:
        >>> data = [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 30}]
        >>> write_csv_file(data, "output.csv")
    """
    if not isinstance(data, list):
        raise TypeError("data must be a list")
    if not isinstance(file_path, (str, Path)):
        raise TypeError("file_path must be a string or Path")
    if not isinstance(delimiter, str):
        raise TypeError("delimiter must be a string")
    if not isinstance(headers, bool):
        raise TypeError("headers must be a boolean")

    if not data:
        # Write empty file for empty data
        Path(file_path).write_text("", encoding="utf-8")
        return

    # Validate all items are dictionaries
    if not all(isinstance(item, dict) for item in data):
        raise TypeError("All items in data must be dictionaries")

    file_path = Path(file_path)

    try:
        # Get all unique fieldnames from all dictionaries
        fieldnames = []
        for item in data:
            for key in item.keys():
                if key not in fieldnames:
                    fieldnames.append(key)

        with open(file_path, "w", encoding="utf-8", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=delimiter)
            if headers:
                writer.writeheader()
            writer.writerows(data)
    except OSError as e:
        raise DataError(f"Failed to write CSV file {file_path}: {e}")


def csv_to_dict_list(csv_data: str, delimiter: str = ",") -> List[DataDict]:
    """Convert CSV string to list of dictionaries.

    Args:
        csv_data: CSV data as string
        delimiter: CSV field delimiter

    Returns:
        List of dictionaries representing CSV rows

    Raises:
        DataError: If CSV data cannot be parsed
        TypeError: If arguments have wrong types

    Example:
        >>> csv_str = "name,age\\nAlice,25\\nBob,30"
        >>> csv_to_dict_list(csv_str)
        [{'name': 'Alice', 'age': '25'}, {'name': 'Bob', 'age': '30'}]
    """
    if not isinstance(csv_data, str):
        raise TypeError("csv_data must be a string")
    if not isinstance(delimiter, str):
        raise TypeError("delimiter must be a string")

    try:
        reader = csv.DictReader(io.StringIO(csv_data), delimiter=delimiter)
        return [dict(row) for row in reader]
    except csv.Error as e:
        raise DataError(f"Failed to parse CSV data: {e}")


def dict_list_to_csv(data: List[DataDict], delimiter: str = ",") -> str:
    """Convert list of dictionaries to CSV string.

    Args:
        data: List of dictionaries to convert
        delimiter: CSV field delimiter

    Returns:
        CSV data as string

    Raises:
        TypeError: If arguments have wrong types

    Example:
        >>> data = [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 30}]
        >>> dict_list_to_csv(data)
        'name,age\\nAlice,25\\nBob,30\\n'
    """
    if not isinstance(data, list):
        raise TypeError("data must be a list")
    if not isinstance(delimiter, str):
        raise TypeError("delimiter must be a string")

    if not data:
        return ""

    # Validate all items are dictionaries
    if not all(isinstance(item, dict) for item in data):
        raise TypeError("All items in data must be dictionaries")

    # Get all unique fieldnames
    fieldnames = []
    for item in data:
        for key in item.keys():
            if key not in fieldnames:
                fieldnames.append(key)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=delimiter)
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()


def detect_csv_delimiter(file_path: PathLike, sample_size: int = 1024) -> str:
    """Auto-detect CSV delimiter by analyzing file content.

    Args:
        file_path: Path to the CSV file
        sample_size: Number of characters to sample for detection

    Returns:
        Detected delimiter character

    Raises:
        DataError: If file cannot be read or delimiter cannot be detected
        TypeError: If arguments have wrong types

    Example:
        >>> detect_csv_delimiter("data.csv")
        ','
        >>> detect_csv_delimiter("data.tsv")
        '\\t'
    """
    if not isinstance(file_path, (str, Path)):
        raise TypeError("file_path must be a string or Path")
    if not isinstance(sample_size, int) or sample_size <= 0:
        raise TypeError("sample_size must be a positive integer")

    file_path = Path(file_path)

    try:
        with open(file_path, encoding="utf-8") as csvfile:
            sample = csvfile.read(sample_size)

        if not sample:
            raise DataError("File is empty, cannot detect delimiter")

        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(sample).delimiter
        return delimiter
    except FileNotFoundError:
        raise DataError(f"CSV file not found: {file_path}")
    except UnicodeDecodeError as e:
        raise DataError(f"Failed to decode CSV file {file_path}: {e}")
    except csv.Error as e:
        raise DataError(f"Failed to detect delimiter in {file_path}: {e}")


def validate_csv_structure(
    file_path: PathLike, expected_columns: Optional[List[str]] = None
) -> bool:
    """Validate CSV file structure and column headers.

    Args:
        file_path: Path to the CSV file
        expected_columns: List of expected column names (None to skip check)

    Returns:
        True if CSV structure is valid

    Raises:
        DataError: If file cannot be read or structure is invalid
        TypeError: If arguments have wrong types

    Example:
        >>> validate_csv_structure("data.csv", ["name", "age", "email"])
        True
        >>> validate_csv_structure("malformed.csv")
        False
    """
    if not isinstance(file_path, (str, Path)):
        raise TypeError("file_path must be a string or Path")
    if expected_columns is not None and not isinstance(expected_columns, list):
        raise TypeError("expected_columns must be a list or None")

    try:
        # Check if file is empty first
        file_path = Path(file_path)
        if file_path.stat().st_size == 0:
            return True  # Empty file is considered valid

        # Try to detect delimiter first
        delimiter = detect_csv_delimiter(file_path)

        # Read first few rows to validate structure
        data = read_csv_file(file_path, delimiter=delimiter, headers=True)

        if not data:
            return True  # Empty file is considered valid

        # Check if expected columns are present
        if expected_columns is not None:
            first_row = data[0]
            actual_columns = set(first_row.keys())
            expected_set = set(expected_columns)

            if not expected_set.issubset(actual_columns):
                missing = expected_set - actual_columns
                raise DataError(f"Missing expected columns: {missing}")

        return True
    except DataError:
        # Re-raise DataError as-is
        raise
    except Exception as e:
        raise DataError(f"Invalid CSV structure in {file_path}: {e}")


def clean_csv_data(
    data: List[DataDict], rules: Optional[Dict[str, Any]] = None
) -> List[DataDict]:
    """Clean CSV data according to specified rules.

    Args:
        data: List of dictionaries to clean
        rules: Dictionary of cleaning rules (None for default cleaning)

    Returns:
        Cleaned list of dictionaries

    Raises:
        TypeError: If arguments have wrong types

    Example:
        >>> data = [{'name': '  Alice  ', 'age': '', 'score': 'N/A'}]
        >>> rules = {'strip_whitespace': True, 'remove_empty': True, 'na_values': ['N/A']}
        >>> clean_csv_data(data, rules)
        [{'name': 'Alice', 'score': None}]
    """
    if not isinstance(data, list):
        raise TypeError("data must be a list")
    if rules is not None and not isinstance(rules, dict):
        raise TypeError("rules must be a dictionary or None")

    if not data:
        return data

    # Default cleaning rules
    default_rules = {
        "strip_whitespace": True,
        "remove_empty": False,
        "na_values": ["N/A", "n/a", "NA", "null", "NULL", "None"],
    }

    # Merge with provided rules
    if rules:
        default_rules.update(rules)

    cleaned_data = []

    for row in data:
        if not isinstance(row, dict):
            continue  # type: ignore[unreachable]

        cleaned_row = {}

        for key, value in row.items():
            # Convert to string for processing
            if not isinstance(value, str):
                value = str(value) if value is not None else ""

            # Strip whitespace
            if default_rules.get("strip_whitespace", False):
                value = value.strip()

            # Handle NA values
            na_values = default_rules.get("na_values", [])
            if isinstance(na_values, list) and value in na_values:
                value = None

            # Remove empty fields if requested
            if default_rules.get("remove_empty", False):
                if value == "" or value is None:
                    continue

            cleaned_row[key] = value

        cleaned_data.append(cleaned_row)

    return cleaned_data
