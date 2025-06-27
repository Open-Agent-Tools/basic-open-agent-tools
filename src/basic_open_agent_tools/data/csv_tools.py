"""CSV processing utilities for AI agents."""

import csv
import io

from ..exceptions import DataError


def read_csv_simple(file_path: str, delimiter: str, headers: bool) -> list:
    """Read CSV file and return as list of dictionaries.

    Args:
        file_path: Path to the CSV file as a string
        delimiter: CSV delimiter character (default: ',')
        headers: Whether the CSV file has headers (default: True)

    Returns:
        List of dictionaries representing CSV rows with string values

    Raises:
        TypeError: If file_path is not a string
        DataError: If file cannot be read or parsed

    Example:
        >>> # Assuming file contains: name,age\\nAlice,25\\nBob,30
        >>> data = read_csv_simple("people.csv")
        >>> data
        [{'name': 'Alice', 'age': '25'}, {'name': 'Bob', 'age': '30'}]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    file_path_str = file_path

    if not isinstance(delimiter, str):
        raise TypeError("delimiter must be a string")

    if not isinstance(headers, bool):
        raise TypeError("headers must be a boolean")

    try:
        with open(file_path_str, encoding="utf-8", newline="") as csvfile:
            if headers:
                dict_reader = csv.DictReader(csvfile, delimiter=delimiter)
                return [dict(row) for row in dict_reader]
            else:
                # If no headers, use col_N as keys
                csv_reader = csv.reader(csvfile, delimiter=delimiter)
                data = list(csv_reader)
                if not data:
                    return []

                result = []
                for row in data:
                    row_dict = {f"col_{i}": value for i, value in enumerate(row)}
                    result.append(row_dict)
                return result
    except FileNotFoundError:
        raise DataError(f"CSV file not found: {file_path_str}")
    except UnicodeDecodeError as e:
        raise DataError(f"Failed to decode CSV file {file_path_str}: {e}")
    except csv.Error as e:
        raise DataError(f"Failed to parse CSV file {file_path_str}: {e}")


def write_csv_simple(data: list, file_path: str, delimiter: str, headers: bool) -> None:
    """Write list of dictionaries to CSV file.

    Args:
        data: List of dictionaries to write
        file_path: Path where CSV file will be created as a string
        delimiter: CSV delimiter character
        headers: Whether to write headers

    Raises:
        TypeError: If data is not a list, contains non-dictionary items, or file_path is not a string
        DataError: If file cannot be written

    Example:
        >>> data = [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 30}]
        >>> write_csv_simple(data, "output.csv")
    """
    # Check if data is a list
    if not isinstance(data, list):
        raise TypeError("data must be a list")

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    file_path_str = file_path

    if not isinstance(delimiter, str):
        raise TypeError("delimiter must be a string")

    if not isinstance(headers, bool):
        raise TypeError("headers must be a boolean")

    if not data:
        # Write empty file for empty data
        with open(file_path_str, "w", encoding="utf-8") as f:
            f.write("")
        return

    try:
        # Validate all items are dictionaries
        for item in data:
            if not isinstance(item, dict):
                raise TypeError("All items in data must be dictionaries")

        # Get all unique fieldnames from all dictionaries
        fieldnames = []
        for item in data:
            for key in item.keys():
                if key not in fieldnames:
                    fieldnames.append(key)

        with open(file_path_str, "w", encoding="utf-8", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=delimiter)
            if headers:
                writer.writeheader()
            writer.writerows(data)
    except OSError as e:
        raise DataError(f"Failed to write CSV file {file_path_str}: {e}")


def csv_to_dict_list(csv_data: str, delimiter: str) -> list:
    """Convert CSV string to list of dictionaries.

    Args:
        csv_data: CSV data as string
        delimiter: CSV delimiter character (default: ',')

    Returns:
        List of dictionaries representing CSV rows

    Raises:
        TypeError: If csv_data is not a string or delimiter is not a string
        DataError: If CSV data cannot be parsed

    Example:
        >>> csv_str = "name,age\\nAlice,25\\nBob,30"
        >>> csv_to_dict_list(csv_str)
        [{'name': 'Alice', 'age': '25'}, {'name': 'Bob', 'age': '30'}]
        >>> csv_str = "name;age\\nAlice;25\\nBob;30"
        >>> csv_to_dict_list(csv_str, delimiter=';')
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


def dict_list_to_csv(data: list, delimiter: str) -> str:
    """Convert list of dictionaries to CSV string.

    Args:
        data: List of dictionaries to convert
        delimiter: CSV delimiter character (default: ',')

    Returns:
        CSV data as string

    Raises:
        TypeError: If data is not a list or contains non-dictionary items

    Example:
        >>> data = [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 30}]
        >>> dict_list_to_csv(data)
        'name,age\\nAlice,25\\nBob,30\\n'
        >>> dict_list_to_csv(data, delimiter=';')
        'name;age\\nAlice;25\\nBob;30\\n'
    """
    if not isinstance(data, list):
        raise TypeError("data must be a list")

    if not data:
        return ""

    # Validate all items are dictionaries
    for item in data:
        if not isinstance(item, dict):
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


def detect_csv_delimiter(file_path: str, sample_size: int) -> str:
    """Auto-detect CSV delimiter by analyzing file content.

    Args:
        file_path: Path to the CSV file as a string
        sample_size: Number of characters to sample for detection

    Returns:
        Detected delimiter character

    Raises:
        TypeError: If file_path is not a string, or sample_size is not a positive integer
        DataError: If file cannot be read or delimiter cannot be detected

    Example:
        >>> detect_csv_delimiter("data.csv")
        ','
        >>> detect_csv_delimiter("data.tsv")
        '\\t'
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    file_path_str = file_path

    if not isinstance(sample_size, int) or sample_size <= 0:
        raise TypeError("sample_size must be a positive integer")

    try:
        with open(file_path_str, encoding="utf-8") as csvfile:
            sample = csvfile.read(sample_size)

        if not sample:
            raise DataError("File is empty, cannot detect delimiter")

        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(sample).delimiter
        return delimiter
    except FileNotFoundError:
        raise DataError(f"CSV file not found: {file_path_str}")
    except UnicodeDecodeError as e:
        raise DataError(f"Failed to decode CSV file {file_path_str}: {e}")
    except csv.Error as e:
        raise DataError(f"Failed to detect delimiter in {file_path_str}: {e}")


def validate_csv_structure(file_path: str, expected_columns: list) -> bool:
    """Validate CSV file structure and column headers.

    Args:
        file_path: Path to the CSV file as a string
        expected_columns: List of expected column names

    Returns:
        True if CSV structure is valid

    Raises:
        TypeError: If file_path is not a string, or expected_columns is not a list
        DataError: If file cannot be read or structure is invalid

    Example:
        >>> validate_csv_structure("data.csv", ["name", "age", "email"])
        True
        >>> validate_csv_structure("malformed.csv")
        False
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    file_path_str = file_path

    if not isinstance(expected_columns, list):
        raise TypeError("expected_columns must be a list")

    try:
        # Check if file is empty first
        import os

        if os.path.getsize(file_path_str) == 0:
            return True  # Empty file is considered valid

        # Read first few rows to validate structure
        data = read_csv_simple(file_path_str, ",", True)

        if not data:
            return True  # Empty file is considered valid

        # Check if expected columns are present
        if expected_columns:
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
        raise DataError(f"Invalid CSV structure in {file_path_str}: {e}")


def clean_csv_data(data: list, rules: dict) -> list:
    """Clean CSV data according to specified rules.

    Args:
        data: List of dictionaries to clean
        rules: Dictionary of cleaning rules

    Returns:
        Cleaned list of dictionaries

    Raises:
        TypeError: If data is not a list or rules is not a dictionary

    Example:
        >>> data = [{'name': '  Alice  ', 'age': '', 'score': 'N/A'}]
        >>> rules = {'strip_whitespace': True, 'remove_empty': True, 'na_values': ['N/A']}
        >>> clean_csv_data(data, rules)
        [{'name': 'Alice', 'score': None}]
    """
    if not isinstance(data, list):
        raise TypeError("data must be a list")

    if not isinstance(rules, dict):
        raise TypeError("rules must be a dictionary")

    if not data:
        return data

    # Default cleaning rules
    default_rules = {
        "strip_whitespace": True,
        "remove_empty": False,
        "na_values": ["N/A", "n/a", "NA", "null", "NULL", "None"],
    }

    # Merge with provided rules
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
