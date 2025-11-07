"""CSV processing utilities for AI agents."""

import csv
import io

from .._logging import get_logger
from ..confirmation import check_user_confirmation
from ..decorators import strands_tool
from ..exceptions import DataError

logger = get_logger("data.csv_tools")


def _generate_csv_preview(data: list[dict[str, str]], delimiter: str = ",") -> str:
    """Generate a preview of CSV data for confirmation prompts.

    Args:
        data: The CSV data as list of dictionaries
        delimiter: CSV delimiter character

    Returns:
        Formatted preview string with row/column count and sample rows
    """
    if not data:
        return "Writing empty CSV file (0 rows)"

    row_count = len(data)
    col_count = len(data[0].keys()) if data else 0

    preview = f"Writing {row_count} rows, {col_count} columns\n"

    # Show first 5 rows as preview
    sample_rows = min(5, len(data))
    if sample_rows > 0:
        preview += f"\nFirst {sample_rows} row(s):\n"
        for i, row in enumerate(data[:sample_rows]):
            row_str = delimiter.join(f"{k}={v}" for k, v in list(row.items())[:3])
            if len(row.items()) > 3:
                row_str += f"... ({len(row)} total fields)"
            preview += f"  {i + 1}. {row_str}\n"

    return preview.strip()


@strands_tool
def read_csv_simple(
    file_path: str, delimiter: str, headers: bool
) -> list[dict[str, str]]:
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

    logger.info(f"Reading CSV: {file_path_str}")
    logger.debug(f"delimiter: '{delimiter}', headers: {headers}")

    try:
        with open(file_path_str, encoding="utf-8", newline="") as csvfile:
            if headers:
                dict_reader = csv.DictReader(csvfile, delimiter=delimiter)
                result = [dict(row) for row in dict_reader]
            else:
                # If no headers, use col_N as keys
                csv_reader = csv.reader(csvfile, delimiter=delimiter)
                data = list(csv_reader)
                if not data:
                    result = []
                else:
                    result = []
                    for row in data:
                        row_dict = {f"col_{i}": value for i, value in enumerate(row)}
                        result.append(row_dict)

            logger.info(f"CSV loaded successfully: {len(result)} rows")
            logger.debug(
                f"First row keys: {list(result[0].keys()) if result else 'none'}"
            )
            return result
    except FileNotFoundError:
        logger.debug(f"CSV file not found: {file_path_str}")
        raise DataError(f"CSV file not found: {file_path_str}")
    except UnicodeDecodeError as e:
        logger.error(f"CSV encoding error: {e}")
        raise DataError(f"Failed to decode CSV file {file_path_str}: {e}")
    except csv.Error as e:
        logger.error(f"CSV parse error: {e}")
        raise DataError(f"Failed to parse CSV file {file_path_str}: {e}")


@strands_tool
def write_csv_simple(
    data: list[dict[str, str]],
    file_path: str,
    delimiter: str,
    headers: bool,
    skip_confirm: bool,
) -> str:
    """Write list of dictionaries to CSV file with permission checking.

    Args:
        data: List of dictionaries to write
        file_path: Path where CSV file will be created as a string
        delimiter: CSV delimiter character
        headers: Whether to write headers
        skip_confirm: If True, skip confirmation and overwrite existing files. IMPORTANT: Agents should default to skip_confirm=False for safety.

    Returns:
        String describing the operation result

    Raises:
        TypeError: If data is not a list, contains non-dictionary items, or file_path is not a string
        DataError: If file cannot be written or exists without skip_confirm

    Example:
        >>> data = [{'name': 'Alice', 'age': '25'}, {'name': 'Bob', 'age': '30'}]
        >>> write_csv_simple(data, "output.csv", ",", True, skip_confirm=True)
        "Created CSV file output.csv with 2 rows and 2 columns"
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

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    # Check if file exists
    import os

    file_existed = os.path.exists(file_path_str)

    logger.info(f"Writing CSV: {file_path_str} ({len(data)} rows)")
    logger.debug(
        f"delimiter: '{delimiter}', headers: {headers}, skip_confirm: {skip_confirm}, file_existed: {file_existed}"
    )

    if file_existed:
        # Check user confirmation - show preview of NEW data being written
        preview = _generate_csv_preview(data, delimiter)
        confirmed, decline_reason = check_user_confirmation(
            operation="overwrite existing CSV file",
            target=file_path_str,
            skip_confirm=skip_confirm,
            preview_info=preview,
        )

        if not confirmed:
            reason_msg = f" (reason: {decline_reason})" if decline_reason else ""
            logger.debug(f"CSV write cancelled by user: {file_path_str}{reason_msg}")
            return f"Operation cancelled by user{reason_msg}: {file_path_str}"

    if not data:
        # Write empty file for empty data
        try:
            with open(file_path_str, "w", encoding="utf-8") as f:
                f.write("")
            action = "Overwrote" if file_existed else "Created"
            return f"{action} empty CSV file: {file_path_str}"
        except OSError as e:
            raise DataError(f"Failed to write CSV file {file_path_str}: {e}")

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

        # Calculate stats for feedback
        row_count = len(data)
        col_count = len(fieldnames)
        action = "Overwrote" if file_existed else "Created"

        # Get file size
        file_size = os.path.getsize(file_path_str)

        result = f"{action} CSV file {file_path_str} with {row_count} rows and {col_count} columns ({file_size} bytes)"
        logger.info(
            f"CSV written successfully: {row_count} rows, {col_count} columns, {file_size} bytes ({action.lower()})"
        )
        logger.debug(f"{result}")
        return result
    except OSError as e:
        logger.error(f"CSV write error: {e}")
        raise DataError(f"Failed to write CSV file {file_path_str}: {e}")


@strands_tool
def csv_to_dict_list(csv_data: str, delimiter: str) -> list[dict[str, str]]:
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


@strands_tool
def dict_list_to_csv(data: list[dict[str, str]], delimiter: str) -> str:
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


@strands_tool
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


@strands_tool
def validate_csv_structure(file_path: str, expected_columns: list[str]) -> bool:
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

        try:
            if os.path.getsize(file_path_str) == 0:
                return True  # Empty file is considered valid
        except FileNotFoundError:
            raise DataError(f"CSV file not found: {file_path_str}")

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


@strands_tool
def clean_csv_data(
    data: list[dict[str, str]], rules: dict[str, str]
) -> list[dict[str, str]]:
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
            continue  # type: ignore[unreachable]

        cleaned_row = {}

        for key, value in row.items():
            # Convert to string for processing (defensive against mixed types)
            if not isinstance(value, str):
                value = str(value) if value is not None else ""  # type: ignore[unreachable]

            # Strip whitespace
            if default_rules.get("strip_whitespace", False):
                value = value.strip()

            # Handle NA values
            na_values = default_rules.get("na_values", [])
            if isinstance(na_values, list) and value in na_values:
                value = ""

            # Remove empty fields if requested
            if default_rules.get("remove_empty", False):
                if value == "":
                    continue

            cleaned_row[key] = value

        cleaned_data.append(cleaned_row)

    return cleaned_data


@strands_tool
def get_csv_header(file_path: str, delimiter: str) -> list[str]:
    """Get column names from CSV file without reading the entire file.

    This function reads only the first line of the CSV file to extract column names,
    making it efficient for large files when you only need to know the structure.

    Args:
        file_path: Path to the CSV file as a string
        delimiter: CSV delimiter character (e.g., ',', ';', '\\t')

    Returns:
        List of column names as strings

    Raises:
        TypeError: If file_path or delimiter is not a string
        DataError: If file cannot be read or has no headers

    Example:
        >>> get_csv_header("data.csv", ",")
        ['name', 'age', 'email', 'city']
        >>> get_csv_header("data.tsv", "\\t")
        ['id', 'product', 'price']
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(delimiter, str):
        raise TypeError("delimiter must be a string")

    logger.info(f"Getting CSV header: {file_path}")
    logger.debug(f"delimiter: '{delimiter}'")

    try:
        with open(file_path, encoding="utf-8", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=delimiter)
            header = next(reader)
            logger.info(f"CSV header retrieved: {len(header)} columns")
            logger.debug(f"Columns: {header}")
            return header
    except FileNotFoundError:
        logger.debug(f"CSV file not found: {file_path}")
        raise DataError(f"CSV file not found: {file_path}")
    except StopIteration:
        logger.debug(f"CSV file is empty: {file_path}")
        raise DataError(f"CSV file is empty: {file_path}")
    except UnicodeDecodeError as e:
        logger.error(f"CSV encoding error: {e}")
        raise DataError(f"Failed to decode CSV file {file_path}: {e}")
    except csv.Error as e:
        logger.error(f"CSV parse error: {e}")
        raise DataError(f"Failed to parse CSV file {file_path}: {e}")


@strands_tool
def preview_csv_rows(
    file_path: str, delimiter: str, num_rows: int
) -> list[dict[str, str]]:
    """Get first N rows of CSV file for preview without loading entire file.

    This function is useful for agents to inspect CSV data structure and content
    before processing the entire file. It's memory-efficient for large files.

    Args:
        file_path: Path to the CSV file as a string
        delimiter: CSV delimiter character (e.g., ',', ';', '\\t')
        num_rows: Number of rows to preview (must be positive)

    Returns:
        List of dictionaries representing the first N rows

    Raises:
        TypeError: If file_path or delimiter is not a string, or num_rows is not an integer
        DataError: If file cannot be read or parsed

    Example:
        >>> preview_csv_rows("data.csv", ",", 3)
        [
            {'name': 'Alice', 'age': '25', 'city': 'NYC'},
            {'name': 'Bob', 'age': '30', 'city': 'LA'},
            {'name': 'Charlie', 'age': '35', 'city': 'SF'}
        ]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(delimiter, str):
        raise TypeError("delimiter must be a string")

    if not isinstance(num_rows, int) or num_rows <= 0:
        raise TypeError("num_rows must be a positive integer")

    logger.info(f"Previewing CSV: {file_path} (first {num_rows} rows)")
    logger.debug(f"delimiter: '{delimiter}'")

    try:
        with open(file_path, encoding="utf-8", newline="") as csvfile:
            dict_reader = csv.DictReader(csvfile, delimiter=delimiter)
            result = []
            for i, row in enumerate(dict_reader):
                if i >= num_rows:
                    break
                result.append(dict(row))

            logger.info(f"CSV preview retrieved: {len(result)} rows")
            logger.debug(
                f"First row keys: {list(result[0].keys()) if result else 'none'}"
            )
            return result
    except FileNotFoundError:
        logger.debug(f"CSV file not found: {file_path}")
        raise DataError(f"CSV file not found: {file_path}")
    except UnicodeDecodeError as e:
        logger.error(f"CSV encoding error: {e}")
        raise DataError(f"Failed to decode CSV file {file_path}: {e}")
    except csv.Error as e:
        logger.error(f"CSV parse error: {e}")
        raise DataError(f"Failed to parse CSV file {file_path}: {e}")


@strands_tool
def get_csv_schema(file_path: str, delimiter: str, sample_rows: int) -> dict[str, str]:
    """Get CSV schema with inferred data types by sampling rows.

    This function analyzes a sample of rows to infer the data type of each column.
    Useful for agents to understand data structure before processing.

    Type inference rules:
    - "integer": All non-empty values can be parsed as integers
    - "float": All non-empty values can be parsed as floats (but not all integers)
    - "boolean": All non-empty values are "true", "false", "yes", "no", "1", "0"
    - "string": Default type for everything else

    Args:
        file_path: Path to the CSV file as a string
        delimiter: CSV delimiter character (e.g., ',', ';', '\\t')
        sample_rows: Number of rows to sample for type inference (must be positive)

    Returns:
        Dictionary mapping column names to inferred types

    Raises:
        TypeError: If file_path or delimiter is not a string, or sample_rows is not an integer
        DataError: If file cannot be read or parsed

    Example:
        >>> get_csv_schema("data.csv", ",", 100)
        {
            'name': 'string',
            'age': 'integer',
            'balance': 'float',
            'active': 'boolean'
        }
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(delimiter, str):
        raise TypeError("delimiter must be a string")

    if not isinstance(sample_rows, int) or sample_rows <= 0:
        raise TypeError("sample_rows must be a positive integer")

    logger.info(f"Getting CSV schema: {file_path} (sampling {sample_rows} rows)")
    logger.debug(f"delimiter: '{delimiter}'")

    # Get sample data
    sample_data = preview_csv_rows(file_path, delimiter, sample_rows)

    if not sample_data:
        logger.debug("CSV file is empty, returning empty schema")
        return {}

    # Initialize type tracking
    schema: dict[str, str] = {}
    column_values: dict[str, list[str]] = {}

    # Collect all non-empty values for each column
    for row in sample_data:
        for col, value in row.items():
            if col not in column_values:
                column_values[col] = []
            if value.strip():  # Only non-empty values
                column_values[col].append(value.strip())

    # Infer type for each column
    for col, values in column_values.items():
        if not values:
            schema[col] = "string"
            continue

        # Check if all values are integers
        all_int = True
        for val in values:
            try:
                int(val)
            except ValueError:
                all_int = False
                break

        if all_int:
            schema[col] = "integer"
            continue

        # Check if all values are floats
        all_float = True
        for val in values:
            try:
                float(val)
            except ValueError:
                all_float = False
                break

        if all_float:
            schema[col] = "float"
            continue

        # Check if all values are boolean
        boolean_values = {"true", "false", "yes", "no", "1", "0", "t", "f", "y", "n"}
        all_bool = all(val.lower() in boolean_values for val in values)

        if all_bool:
            schema[col] = "boolean"
            continue

        # Default to string
        schema[col] = "string"

    # Add columns with no non-empty values as string
    for row in sample_data:
        for col in row.keys():
            if col not in schema:
                schema[col] = "string"

    logger.info(f"CSV schema inferred: {len(schema)} columns")
    logger.debug(f"Schema: {schema}")
    return schema


@strands_tool
def get_csv_info(file_path: str, delimiter: str) -> dict[str, str]:
    """Get CSV file metadata including row count, column count, and file size.

    This function provides comprehensive metadata about a CSV file without loading
    the entire file into memory. Useful for agents to understand file characteristics
    before processing.

    Args:
        file_path: Path to the CSV file as a string
        delimiter: CSV delimiter character (e.g., ',', ';', '\\t')

    Returns:
        Dictionary with metadata including:
        - file_path: Path to the file
        - file_size_bytes: Size of file in bytes
        - row_count: Number of data rows (excluding header)
        - column_count: Number of columns
        - columns: Comma-separated list of column names

    Raises:
        TypeError: If file_path or delimiter is not a string
        DataError: If file cannot be read or parsed

    Example:
        >>> get_csv_info("data.csv", ",")
        {
            'file_path': 'data.csv',
            'file_size_bytes': '15420',
            'row_count': '1000',
            'column_count': '5',
            'columns': 'name,age,email,city,country'
        }
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(delimiter, str):
        raise TypeError("delimiter must be a string")

    logger.info(f"Getting CSV info: {file_path}")
    logger.debug(f"delimiter: '{delimiter}'")

    try:
        import os

        # Get file size
        file_size = os.path.getsize(file_path)

        # Get header
        header = get_csv_header(file_path, delimiter)

        # Count rows efficiently without loading entire file
        with open(file_path, encoding="utf-8", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=delimiter)
            next(reader)  # Skip header
            row_count = sum(1 for _ in reader)

        info = {
            "file_path": file_path,
            "file_size_bytes": str(file_size),
            "row_count": str(row_count),
            "column_count": str(len(header)),
            "columns": ",".join(header),
        }

        logger.info(
            f"CSV info retrieved: {row_count} rows, {len(header)} columns, {file_size} bytes"
        )
        logger.debug(f"Info: {info}")
        return info
    except FileNotFoundError:
        logger.debug(f"CSV file not found: {file_path}")
        raise DataError(f"CSV file not found: {file_path}")
    except UnicodeDecodeError as e:
        logger.error(f"CSV encoding error: {e}")
        raise DataError(f"Failed to decode CSV file {file_path}: {e}")
    except csv.Error as e:
        logger.error(f"CSV parse error: {e}")
        raise DataError(f"Failed to parse CSV file {file_path}: {e}")


@strands_tool
def select_csv_columns(
    file_path: str, delimiter: str, columns: list[str]
) -> list[dict[str, str]]:
    """Read only specific columns from CSV file, discarding others.

    This function is memory-efficient for wide CSV files when you only need
    a subset of columns. It reduces token usage by loading only required columns.

    Args:
        file_path: Path to the CSV file as a string
        delimiter: CSV delimiter character (e.g., ',', ';', '\\t')
        columns: List of column names to select

    Returns:
        List of dictionaries containing only the selected columns

    Raises:
        TypeError: If parameters are not the correct types
        DataError: If file cannot be read, columns don't exist, or file is malformed

    Example:
        >>> # CSV has: name,age,email,address,phone,city,country
        >>> # But you only need name and email
        >>> select_csv_columns("users.csv", ",", ["name", "email"])
        [
            {'name': 'Alice', 'email': 'alice@example.com'},
            {'name': 'Bob', 'email': 'bob@example.com'}
        ]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(delimiter, str):
        raise TypeError("delimiter must be a string")

    if not isinstance(columns, list):
        raise TypeError("columns must be a list")

    logger.info(f"Selecting {len(columns)} columns from CSV: {file_path} ({columns})")
    logger.debug(f"delimiter: '{delimiter}'")

    try:
        with open(file_path, encoding="utf-8", newline="") as csvfile:
            dict_reader = csv.DictReader(csvfile, delimiter=delimiter)

            # Check if requested columns exist
            if dict_reader.fieldnames:
                missing_columns = [
                    col for col in columns if col not in dict_reader.fieldnames
                ]
                if missing_columns:
                    raise DataError(
                        f"Columns not found in CSV: {missing_columns}. Available columns: {list(dict_reader.fieldnames)}"
                    )

            result = []
            for row in dict_reader:
                # Only include selected columns
                selected_row = {col: row[col] for col in columns if col in row}
                result.append(selected_row)

            logger.info(
                f"CSV columns selected: {len(result)} rows with {len(columns)} columns"
            )
            return result
    except FileNotFoundError:
        logger.debug(f"CSV file not found: {file_path}")
        raise DataError(f"CSV file not found: {file_path}")
    except UnicodeDecodeError as e:
        logger.error(f"CSV encoding error: {e}")
        raise DataError(f"Failed to decode CSV file {file_path}: {e}")
    except csv.Error as e:
        logger.error(f"CSV parse error: {e}")
        raise DataError(f"Failed to parse CSV file {file_path}: {e}")


@strands_tool
def filter_csv_rows(
    file_path: str, delimiter: str, column: str, value: str, operator: str
) -> list[dict[str, str]]:
    """Read only CSV rows matching filter criteria.

    This function reduces token usage by loading only rows that match
    specific criteria, avoiding full file loads for large datasets.

    Supported operators:
    - "equals": Exact match (case-sensitive)
    - "contains": Column value contains the search value
    - "startswith": Column value starts with the search value
    - "endswith": Column value ends with the search value
    - "greater_than": Numeric comparison (value > search)
    - "less_than": Numeric comparison (value < search)

    Args:
        file_path: Path to the CSV file as a string
        delimiter: CSV delimiter character (e.g., ',', ';', '\\t')
        column: Column name to filter on
        value: Value to compare against
        operator: Comparison operator (see supported operators above)

    Returns:
        List of dictionaries containing only rows matching the filter

    Raises:
        TypeError: If parameters are not the correct types
        DataError: If file cannot be read, column doesn't exist, or operator is invalid

    Example:
        >>> # Get only active users
        >>> filter_csv_rows("users.csv", ",", "status", "active", "equals")
        [{'name': 'Alice', 'status': 'active'}, {'name': 'Bob', 'status': 'active'}]

        >>> # Get users with email containing 'gmail'
        >>> filter_csv_rows("users.csv", ",", "email", "gmail", "contains")
        [{'name': 'Charlie', 'email': 'charlie@gmail.com'}]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(delimiter, str):
        raise TypeError("delimiter must be a string")

    if not isinstance(column, str):
        raise TypeError("column must be a string")

    if not isinstance(value, str):
        raise TypeError("value must be a string")

    if not isinstance(operator, str):
        raise TypeError("operator must be a string")

    valid_operators = [
        "equals",
        "contains",
        "startswith",
        "endswith",
        "greater_than",
        "less_than",
    ]
    if operator not in valid_operators:
        raise DataError(
            f"Invalid operator: {operator}. Valid operators: {valid_operators}"
        )

    logger.info(f"Filtering CSV: {file_path} WHERE {column} {operator} '{value}'")
    logger.debug(f"delimiter: '{delimiter}'")

    try:
        with open(file_path, encoding="utf-8", newline="") as csvfile:
            dict_reader = csv.DictReader(csvfile, delimiter=delimiter)

            # Check if column exists
            if dict_reader.fieldnames and column not in dict_reader.fieldnames:
                raise DataError(
                    f"Column '{column}' not found in CSV. Available columns: {list(dict_reader.fieldnames)}"
                )

            result = []
            for row in dict_reader:
                row_value = row.get(column, "")

                # Apply filter based on operator
                matches = False
                if operator == "equals":
                    matches = row_value == value
                elif operator == "contains":
                    matches = value in row_value
                elif operator == "startswith":
                    matches = row_value.startswith(value)
                elif operator == "endswith":
                    matches = row_value.endswith(value)
                elif operator == "greater_than":
                    try:
                        matches = float(row_value) > float(value)
                    except ValueError:
                        matches = False
                elif operator == "less_than":
                    try:
                        matches = float(row_value) < float(value)
                    except ValueError:
                        matches = False

                if matches:
                    result.append(dict(row))

            logger.info(f"CSV filter matched: {len(result)} rows")
            return result
    except FileNotFoundError:
        logger.debug(f"CSV file not found: {file_path}")
        raise DataError(f"CSV file not found: {file_path}")
    except UnicodeDecodeError as e:
        logger.error(f"CSV encoding error: {e}")
        raise DataError(f"Failed to decode CSV file {file_path}: {e}")
    except csv.Error as e:
        logger.error(f"CSV parse error: {e}")
        raise DataError(f"Failed to parse CSV file {file_path}: {e}")


@strands_tool
def get_csv_column_stats(
    file_path: str, delimiter: str, column: str, sample_size: int
) -> dict[str, str]:
    """Get statistics for a CSV column by sampling rows.

    This function provides insights about a column without loading the entire
    dataset, making it token-efficient for understanding data distributions.

    Statistics returned:
    - total_rows: Total number of rows in the file
    - unique_count: Number of unique values found in sample
    - null_count: Number of empty/null values in sample
    - sample_values: Up to 10 example values from the column
    - min_value: Minimum value (for numeric columns)
    - max_value: Maximum value (for numeric columns)

    Args:
        file_path: Path to the CSV file as a string
        delimiter: CSV delimiter character (e.g., ',', ';', '\\t')
        column: Column name to analyze
        sample_size: Number of rows to sample for statistics

    Returns:
        Dictionary with column statistics as strings

    Raises:
        TypeError: If parameters are not the correct types
        DataError: If file cannot be read or column doesn't exist

    Example:
        >>> get_csv_column_stats("sales.csv", ",", "country", 1000)
        {
            'total_rows': '5000',
            'unique_count': '25',
            'null_count': '3',
            'sample_values': 'USA,Canada,Mexico,Germany,France,UK,Spain,Italy,Japan,China',
            'min_value': 'N/A',
            'max_value': 'N/A'
        }
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(delimiter, str):
        raise TypeError("delimiter must be a string")

    if not isinstance(column, str):
        raise TypeError("column must be a string")

    if not isinstance(sample_size, int) or sample_size <= 0:
        raise TypeError("sample_size must be a positive integer")

    logger.info(
        f"Getting column stats for '{column}' in {file_path} (sample_size={sample_size})"
    )
    logger.debug(f"delimiter: '{delimiter}'")

    try:
        # First, count total rows
        with open(file_path, encoding="utf-8", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=delimiter)
            next(reader)  # Skip header
            total_rows = sum(1 for _ in reader)

        # Now sample for statistics
        sample_data = preview_csv_rows(file_path, delimiter, sample_size)

        if not sample_data:
            return {
                "total_rows": "0",
                "unique_count": "0",
                "null_count": "0",
                "sample_values": "",
                "min_value": "N/A",
                "max_value": "N/A",
            }

        # Check if column exists
        if column not in sample_data[0]:
            available_columns = list(sample_data[0].keys())
            raise DataError(
                f"Column '{column}' not found in CSV. Available columns: {available_columns}"
            )

        # Collect values
        values = [row[column] for row in sample_data]
        non_null_values = [v for v in values if v.strip()]

        # Calculate statistics
        unique_values = list(set(non_null_values))
        null_count = len(values) - len(non_null_values)

        # Sample values (up to 10)
        sample_values_str = ",".join(unique_values[:10])

        # Try numeric stats
        min_value = "N/A"
        max_value = "N/A"
        try:
            numeric_values = [float(v) for v in non_null_values]
            if numeric_values:
                min_value = str(min(numeric_values))
                max_value = str(max(numeric_values))
        except ValueError:
            pass  # Not numeric

        stats = {
            "total_rows": str(total_rows),
            "unique_count": str(len(unique_values)),
            "null_count": str(null_count),
            "sample_values": sample_values_str,
            "min_value": min_value,
            "max_value": max_value,
        }

        logger.info(
            f"Column stats calculated: {len(unique_values)} unique values, {null_count} nulls"
        )
        logger.debug(f"Stats: {stats}")
        return stats
    except FileNotFoundError:
        logger.debug(f"CSV file not found: {file_path}")
        raise DataError(f"CSV file not found: {file_path}")
    except UnicodeDecodeError as e:
        logger.error(f"CSV encoding error: {e}")
        raise DataError(f"Failed to decode CSV file {file_path}: {e}")
    except csv.Error as e:
        logger.error(f"CSV parse error: {e}")
        raise DataError(f"Failed to parse CSV file {file_path}: {e}")


@strands_tool
def sample_csv_rows(
    file_path: str, delimiter: str, sample_size: int, method: str
) -> list[dict[str, str]]:
    """Get a representative sample of CSV rows without loading entire file.

    This function enables efficient data analysis by sampling rather than
    loading complete datasets, significantly reducing token usage.

    Sampling methods:
    - "first": Get first N rows (same as preview_csv_rows)
    - "random": Get N random rows using reservoir sampling
    - "systematic": Get every Kth row to reach sample size

    Args:
        file_path: Path to the CSV file as a string
        delimiter: CSV delimiter character (e.g., ',', ';', '\\t')
        sample_size: Number of rows to sample
        method: Sampling method ("first", "random", "systematic")

    Returns:
        List of dictionaries representing sampled rows

    Raises:
        TypeError: If parameters are not the correct types
        DataError: If file cannot be read or method is invalid

    Example:
        >>> # Get 100 random rows for analysis
        >>> sample_csv_rows("large_data.csv", ",", 100, "random")
        [{'id': '42', 'value': '123'}, {'id': '156', 'value': '789'}, ...]

        >>> # Get systematic sample (every 10th row)
        >>> sample_csv_rows("data.csv", ",", 50, "systematic")
        [{'row': '10'}, {'row': '20'}, {'row': '30'}, ...]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(delimiter, str):
        raise TypeError("delimiter must be a string")

    if not isinstance(sample_size, int) or sample_size <= 0:
        raise TypeError("sample_size must be a positive integer")

    if not isinstance(method, str):
        raise TypeError("method must be a string")

    valid_methods = ["first", "random", "systematic"]
    if method not in valid_methods:
        raise DataError(f"Invalid method: {method}. Valid methods: {valid_methods}")

    logger.info(f"Sampling CSV: {file_path} (size={sample_size}, method={method})")
    logger.debug(f"delimiter: '{delimiter}'")

    try:
        if method == "first":
            # Use existing preview function
            result_preview: list[dict[str, str]] = preview_csv_rows(
                file_path, delimiter, sample_size
            )
            return result_preview

        elif method == "random":
            # Reservoir sampling for random selection
            import random

            with open(file_path, encoding="utf-8", newline="") as csvfile:
                dict_reader = csv.DictReader(csvfile, delimiter=delimiter)
                reservoir: list[dict[str, str]] = []

                for i, row in enumerate(dict_reader):
                    if i < sample_size:
                        reservoir.append(dict(row))
                    else:
                        # Randomly replace elements with decreasing probability
                        j = random.randint(0, i)
                        if j < sample_size:
                            reservoir[j] = dict(row)

                logger.info(f"CSV random sample retrieved: {len(reservoir)} rows")
                return reservoir

        else:  # systematic
            # Count total rows first
            with open(file_path, encoding="utf-8", newline="") as csvfile:
                reader = csv.reader(csvfile, delimiter=delimiter)
                next(reader)  # Skip header
                total_rows = sum(1 for _ in reader)

            if total_rows == 0:
                return []

            # Calculate interval
            interval = max(1, total_rows // sample_size)

            # Sample every Kth row
            with open(file_path, encoding="utf-8", newline="") as csvfile:
                dict_reader = csv.DictReader(csvfile, delimiter=delimiter)
                result: list[dict[str, str]] = []
                for i, row in enumerate(dict_reader):
                    if i % interval == 0 and len(result) < sample_size:
                        result.append(dict(row))

                logger.info(
                    f"CSV systematic sample retrieved: {len(result)} rows (interval={interval})"
                )
                return result

    except FileNotFoundError:
        logger.debug(f"CSV file not found: {file_path}")
        raise DataError(f"CSV file not found: {file_path}")
    except UnicodeDecodeError as e:
        logger.error(f"CSV encoding error: {e}")
        raise DataError(f"Failed to decode CSV file {file_path}: {e}")
    except csv.Error as e:
        logger.error(f"CSV parse error: {e}")
        raise DataError(f"Failed to parse CSV file {file_path}: {e}")


@strands_tool
def get_csv_row_range(
    file_path: str, delimiter: str, start_row: int, end_row: int
) -> list[dict[str, str]]:
    """Get specific range of rows from CSV file (pagination support).

    This function enables efficient pagination and chunked processing of
    large CSV files, loading only the requested row range.

    Args:
        file_path: Path to the CSV file as a string
        delimiter: CSV delimiter character (e.g., ',', ';', '\\t')
        start_row: Starting row index (0-based, inclusive)
        end_row: Ending row index (0-based, exclusive)

    Returns:
        List of dictionaries representing rows in the specified range

    Raises:
        TypeError: If parameters are not the correct types
        DataError: If file cannot be read or row indices are invalid

    Example:
        >>> # Get rows 100-200 for processing
        >>> get_csv_row_range("data.csv", ",", 100, 200)
        [{'id': '101', ...}, {'id': '102', ...}, ...]

        >>> # Paginate through large file
        >>> page_size = 100
        >>> get_csv_row_range("data.csv", ",", 0, page_size)  # Page 1
        >>> get_csv_row_range("data.csv", ",", page_size, page_size*2)  # Page 2
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(delimiter, str):
        raise TypeError("delimiter must be a string")

    if not isinstance(start_row, int) or start_row < 0:
        raise TypeError("start_row must be a non-negative integer")

    if not isinstance(end_row, int) or end_row < 0:
        raise TypeError("end_row must be a non-negative integer")

    if end_row <= start_row:
        raise DataError("end_row must be greater than start_row")

    logger.info(f"Getting CSV row range: {file_path} [rows {start_row}:{end_row}]")
    logger.debug(f"delimiter: '{delimiter}'")

    try:
        with open(file_path, encoding="utf-8", newline="") as csvfile:
            dict_reader = csv.DictReader(csvfile, delimiter=delimiter)
            result = []

            for i, row in enumerate(dict_reader):
                if i < start_row:
                    continue
                if i >= end_row:
                    break
                result.append(dict(row))

            logger.info(f"CSV row range retrieved: {len(result)} rows")
            return result
    except FileNotFoundError:
        logger.debug(f"CSV file not found: {file_path}")
        raise DataError(f"CSV file not found: {file_path}")
    except UnicodeDecodeError as e:
        logger.error(f"CSV encoding error: {e}")
        raise DataError(f"Failed to decode CSV file {file_path}: {e}")
    except csv.Error as e:
        logger.error(f"CSV parse error: {e}")
        raise DataError(f"Failed to parse CSV file {file_path}: {e}")


@strands_tool
def count_csv_rows(
    file_path: str, delimiter: str, filter_column: str, filter_value: str
) -> int:
    """Count CSV rows, optionally matching filter criteria.

    This function efficiently counts rows without loading data into memory,
    enabling agents to understand dataset size before processing.

    Args:
        file_path: Path to the CSV file as a string
        delimiter: CSV delimiter character (e.g., ',', ';', '\\t')
        filter_column: Column to filter on (empty string for no filter)
        filter_value: Value to match (ignored if filter_column is empty)

    Returns:
        Number of rows matching the criteria (or total if no filter)

    Raises:
        TypeError: If parameters are not the correct types
        DataError: If file cannot be read or filter column doesn't exist

    Example:
        >>> # Count all rows
        >>> count_csv_rows("data.csv", ",", "", "")
        5000

        >>> # Count rows where status='active'
        >>> count_csv_rows("users.csv", ",", "status", "active")
        342
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(delimiter, str):
        raise TypeError("delimiter must be a string")

    if not isinstance(filter_column, str):
        raise TypeError("filter_column must be a string")

    if not isinstance(filter_value, str):
        raise TypeError("filter_value must be a string")

    logger.info(f"Counting CSV rows: {file_path}")
    if filter_column:
        logger.info(f"Filter: {filter_column} = '{filter_value}'")
    logger.debug(f"delimiter: '{delimiter}'")

    try:
        with open(file_path, encoding="utf-8", newline="") as csvfile:
            if not filter_column:
                # No filter - just count all rows
                reader = csv.reader(csvfile, delimiter=delimiter)
                next(reader)  # Skip header
                count = sum(1 for _ in reader)
            else:
                # Filter and count
                dict_reader = csv.DictReader(csvfile, delimiter=delimiter)

                # Check if column exists
                if (
                    dict_reader.fieldnames
                    and filter_column not in dict_reader.fieldnames
                ):
                    raise DataError(
                        f"Column '{filter_column}' not found in CSV. Available columns: {list(dict_reader.fieldnames)}"
                    )

                count = 0
                for row in dict_reader:
                    if row.get(filter_column, "") == filter_value:
                        count += 1

            logger.info(f"CSV row count: {count}")
            return count
    except FileNotFoundError:
        logger.debug(f"CSV file not found: {file_path}")
        raise DataError(f"CSV file not found: {file_path}")
    except UnicodeDecodeError as e:
        logger.error(f"CSV encoding error: {e}")
        raise DataError(f"Failed to decode CSV file {file_path}: {e}")
    except csv.Error as e:
        logger.error(f"CSV parse error: {e}")
        raise DataError(f"Failed to parse CSV file {file_path}: {e}")


@strands_tool
def get_csv_value_counts(
    file_path: str, delimiter: str, column: str, top_n: int
) -> dict[str, str]:
    """Get frequency counts for column values (top N most common).

    This function provides distribution analysis without loading entire
    datasets, enabling agents to understand data patterns efficiently.

    Args:
        file_path: Path to the CSV file as a string
        delimiter: CSV delimiter character (e.g., ',', ';', '\\t')
        column: Column name to count values for
        top_n: Number of top values to return

    Returns:
        Dictionary mapping values to their frequency counts (as strings)

    Raises:
        TypeError: If parameters are not the correct types
        DataError: If file cannot be read or column doesn't exist

    Example:
        >>> # Get top 5 most common countries
        >>> get_csv_value_counts("sales.csv", ",", "country", 5)
        {
            'USA': '523',
            'Canada': '412',
            'UK': '398',
            'Germany': '287',
            'France': '256'
        }
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(delimiter, str):
        raise TypeError("delimiter must be a string")

    if not isinstance(column, str):
        raise TypeError("column must be a string")

    if not isinstance(top_n, int) or top_n <= 0:
        raise TypeError("top_n must be a positive integer")

    logger.info(f"Getting value counts for '{column}' in {file_path} (top {top_n})")
    logger.debug(f"delimiter: '{delimiter}'")

    try:
        from collections import Counter

        with open(file_path, encoding="utf-8", newline="") as csvfile:
            dict_reader = csv.DictReader(csvfile, delimiter=delimiter)

            # Check if column exists
            if dict_reader.fieldnames and column not in dict_reader.fieldnames:
                raise DataError(
                    f"Column '{column}' not found in CSV. Available columns: {list(dict_reader.fieldnames)}"
                )

            # Count values
            values = [row.get(column, "") for row in dict_reader]
            counter = Counter(values)

            # Get top N
            top_values = counter.most_common(top_n)
            result = {value: str(count) for value, count in top_values}

            logger.info(f"Value counts calculated: {len(result)} unique values")
            logger.debug(f"Top values: {result}")
            return result
    except FileNotFoundError:
        logger.debug(f"CSV file not found: {file_path}")
        raise DataError(f"CSV file not found: {file_path}")
    except UnicodeDecodeError as e:
        logger.error(f"CSV encoding error: {e}")
        raise DataError(f"Failed to decode CSV file {file_path}: {e}")
    except csv.Error as e:
        logger.error(f"CSV parse error: {e}")
        raise DataError(f"Failed to parse CSV file {file_path}: {e}")
