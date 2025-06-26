"""CSV processing utilities for AI agents."""

import csv
import io
from typing import Optional

from ..exceptions import DataError


def read_csv_simple(file_path: str) -> list:
    """Read CSV file and return as list of dictionaries.

    Args:
        file_path: Path to the CSV file (string)

    Returns:
        List of dictionaries representing CSV rows with string values

    Raises:
        DataError: If file cannot be read or parsed

    Example:
        >>> # Assuming file contains: name,age\\nAlice,25\\nBob,30
        >>> data = read_csv_simple("people.csv")
        >>> data
        [{'name': 'Alice', 'age': '25'}, {'name': 'Bob', 'age': '30'}]
    """
    try:
        with open(file_path, encoding="utf-8", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            return [dict(row) for row in reader]
    except FileNotFoundError:
        raise DataError(f"CSV file not found: {file_path}")
    except UnicodeDecodeError as e:
        raise DataError(f"Failed to decode CSV file {file_path}: {e}")
    except csv.Error as e:
        raise DataError(f"Failed to parse CSV file {file_path}: {e}")


def write_csv_simple(data: list, file_path: str) -> None:
    """Write list of dictionaries to CSV file.

    Args:
        data: List of dictionaries to write
        file_path: Path where CSV file will be created

    Raises:
        DataError: If file cannot be written

    Example:
        >>> data = [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 30}]
        >>> write_csv_simple(data, "output.csv")
    """
    if not data:
        # Write empty file for empty data
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("")
        return

    try:
        # Get all unique fieldnames from all dictionaries
        fieldnames = []
        for item in data:
            for key in item.keys():
                if key not in fieldnames:
                    fieldnames.append(key)

        with open(file_path, "w", encoding="utf-8", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    except OSError as e:
        raise DataError(f"Failed to write CSV file {file_path}: {e}")


def csv_to_dict_list(csv_data: str) -> list:
    """Convert CSV string to list of dictionaries.

    Args:
        csv_data: CSV data as string

    Returns:
        List of dictionaries representing CSV rows

    Raises:
        DataError: If CSV data cannot be parsed

    Example:
        >>> csv_str = "name,age\\nAlice,25\\nBob,30"
        >>> csv_to_dict_list(csv_str)
        [{'name': 'Alice', 'age': '25'}, {'name': 'Bob', 'age': '30'}]
    """
    try:
        reader = csv.DictReader(io.StringIO(csv_data))
        return [dict(row) for row in reader]
    except csv.Error as e:
        raise DataError(f"Failed to parse CSV data: {e}")


def dict_list_to_csv(data: list) -> str:
    """Convert list of dictionaries to CSV string.

    Args:
        data: List of dictionaries to convert

    Returns:
        CSV data as string

    Example:
        >>> data = [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 30}]
        >>> dict_list_to_csv(data)
        'name,age\\nAlice,25\\nBob,30\\n'
    """
    if not data:
        return ""

    # Get all unique fieldnames
    fieldnames = []
    for item in data:
        for key in item.keys():
            if key not in fieldnames:
                fieldnames.append(key)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()


def detect_csv_delimiter(file_path: str, sample_size: int = 1024) -> str:
    """Auto-detect CSV delimiter by analyzing file content.

    Args:
        file_path: Path to the CSV file
        sample_size: Number of characters to sample for detection

    Returns:
        Detected delimiter character

    Raises:
        DataError: If file cannot be read or delimiter cannot be detected

    Example:
        >>> detect_csv_delimiter("data.csv")
        ','
        >>> detect_csv_delimiter("data.tsv")
        '\\t'
    """
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


def validate_csv_structure(file_path: str, expected_columns: Optional[list] = None) -> bool:
    """Validate CSV file structure and column headers.

    Args:
        file_path: Path to the CSV file
        expected_columns: List of expected column names (optional)

    Returns:
        True if CSV structure is valid

    Raises:
        DataError: If file cannot be read or structure is invalid

    Example:
        >>> validate_csv_structure("data.csv", ["name", "age", "email"])
        True
        >>> validate_csv_structure("malformed.csv")
        False
    """
    try:
        # Check if file is empty first
        import os

        if os.path.getsize(file_path) == 0:
            return True  # Empty file is considered valid

        # Read first few rows to validate structure
        data = read_csv_simple(file_path)

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


def clean_csv_data(data: list, rules: Optional[dict] = None) -> list:
    """Clean CSV data according to specified rules.

    Args:
        data: List of dictionaries to clean
        rules: Dictionary of cleaning rules (optional)

    Returns:
        Cleaned list of dictionaries

    Example:
        >>> data = [{'name': '  Alice  ', 'age': '', 'score': 'N/A'}]
        >>> rules = {'strip_whitespace': True, 'remove_empty': True, 'na_values': ['N/A']}
        >>> clean_csv_data(data, rules)
        [{'name': 'Alice', 'score': None}]
    """
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
            continue

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
