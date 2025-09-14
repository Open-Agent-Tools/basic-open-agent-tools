# API Reference

Complete reference for all 166 functions across 12 modules in basic-open-agent-tools.

## Quick Navigation

- [Function Index](#function-index) - Alphabetical listing of all functions
- [Module Overview](#module-overview) - Functions grouped by module
- [Common Patterns](#common-patterns) - Shared parameter and return patterns
- [Type Reference](#type-reference) - Type signature explanations

## Function Index

**Alphabetical listing of all functions:**

| Function | Module | Description |
|----------|---------|-------------|
| `add_watermark_to_pdf` | pdf | Add text watermark to all pages of a PDF |
| `append_to_file` | file_system | Append text content to an existing file |
| `base64_decode` | crypto | Decode Base64 encoded data to string |
| `base64_encode` | crypto | Encode string data to Base64 format |
| `benchmark_disk_io` | monitoring | Benchmark disk read/write performance |
| `check_port_open` | network | Check if a port is open on remote host |
| `check_url_status` | monitoring | Check URL availability and response status |
| `clean_whitespace` | text | Remove extra whitespace from text |
| `cleanup_old_logs` | logging | Remove old log files based on age/count |
| `compress_file_bzip2` | archive | Compress single file using BZIP2 |
| `compress_file_gzip` | archive | Compress single file using GZIP |
| `compress_file_xz` | archive | Compress single file using XZ/LZMA |
| `compress_files` | archive | Create ZIP archive from multiple files |
| `configure_logger` | logging | Set up logger with specified settings |
| `copy_file` | file_system | Copy file from source to destination |
| `create_directory` | file_system | Create new directory with parent creation |
| `create_tar` | archive | Create TAR archive from files/directories |
| `create_zip` | archive | Create ZIP archive from files/directories |
| `decompress_file_gzip` | archive | Decompress GZIP file to original format |
| `delete_directory` | file_system | Remove directory and all contents |
| `delete_file` | file_system | Delete specified file |
| `directory_exists` | file_system | Check if directory exists |
| `execute_shell_command` | system | Execute shell commands cross-platform |
| `extract_pages_from_pdf` | pdf | Extract specific pages to new PDF |
| `extract_sentences` | text | Split text into individual sentences |
| `extract_tar` | archive | Extract TAR archive contents |
| `extract_text_from_pdf` | pdf | Extract text content from PDF files |
| `extract_zip` | archive | Extract ZIP archive contents |
| `file_exists` | file_system | Check if file exists at path |
| `format_exception_details` | utilities | Format exception information for debugging |
| `generate_date_range` | datetime | Create list of dates between start and end |
| `generate_directory_tree` | file_system | Create visual directory tree representation |
| `generate_random_bytes` | crypto | Generate random bytes as hex string |
| `generate_random_string` | crypto | Generate random string with character set |
| `generate_uuid4` | crypto | Generate random UUID version 4 |
| `get_call_stack_info` | utilities | Get current call stack information |
| `get_cpu_info` | system | Get CPU information and usage stats |
| `get_current_date` | datetime | Get current date in specified timezone |
| `get_current_datetime` | datetime | Get current date and time |
| `get_current_process_info` | system | Get information about current process |
| `get_current_time` | datetime | Get current time in specified timezone |
| `get_current_year` | datetime | Get current year as integer |
| `get_disk_usage` | system | Get disk usage for specified path |
| `get_env_var` | system | Get environment variable value |
| `get_file_info` | file_system | Get detailed file information |
| `get_file_size` | file_system | Get file size in bytes |
| `get_file_system_context` | system | Get file system context information |
| `get_memory_info` | system | Get system memory usage information |
| `get_network_environment` | system | Get network environment details |
| `get_pdf_info` | pdf | Get PDF metadata and document information |
| `get_process_info` | system | Get information about specific process |
| `get_python_module_info` | system | Get Python module and package information |
| `get_system_info` | system | Get comprehensive system information |
| `get_system_load_average` | monitoring | Get system load average information |
| `get_uptime` | system | Get system uptime in seconds |
| `hash_file_sha256` | crypto | Generate SHA-256 hash of file contents |
| `hash_string_md5` | crypto | Generate MD5 hash of string |
| `hash_string_sha256` | crypto | Generate SHA-256 hash of string |
| `hash_string_sha512` | crypto | Generate SHA-512 hash of string |
| `hex_decode` | crypto | Decode hexadecimal string to text |
| `hex_encode` | crypto | Encode string to hexadecimal |
| `http_request` | network | Make HTTP requests with error handling |
| `inspect_function_signature` | utilities | Analyze function signature details |
| `inspect_runtime_environment` | system | Get comprehensive runtime information |
| `is_business_day` | datetime | Check if date is a business day |
| `is_empty_directory` | file_system | Check if directory is empty |
| `is_leap_year` | datetime | Check if year is a leap year |
| `is_process_running` | system | Check if process with name is running |
| `join_with_oxford_comma` | text | Join list items with Oxford comma |
| `list_all_directory_contents` | file_system | List all files and subdirectories |
| `list_directory_contents` | file_system | List immediate directory contents |
| `list_env_vars` | system | List all environment variables |
| `list_running_processes` | system | List currently running processes |
| `log_error` | logging | Log error messages with context |
| `log_info` | logging | Log informational messages with context |
| `merge_pdfs` | pdf | Combine multiple PDF files into one |
| `monitor_directory` | monitoring | Monitor directory for file changes |
| `monitor_function_performance` | monitoring | Monitor system performance metrics |
| `move_file` | file_system | Move file from source to destination |
| `normalize_line_endings` | text | Standardize line endings in text |
| `normalize_unicode` | text | Normalize Unicode text representation |
| `ping_host` | monitoring | Ping remote host for connectivity |
| `precise_sleep` | utilities | High-precision sleep using busy-waiting |
| `profile_code_execution` | monitoring | Profile code execution performance |
| `read_csv_file` | data | Read CSV file with configurable options |
| `read_file_to_string` | file_system | Read entire file content as string |
| `read_ini_config` | data | Read INI configuration file |
| `read_json_file` | data | Read and parse JSON file |
| `read_toml_config` | data | Read TOML configuration file |
| `read_yaml_config` | data | Read YAML configuration file |
| `resolve_hostname` | network | Resolve hostname to IP addresses |
| `reverse_dns_lookup` | network | Perform reverse DNS lookup |
| `rotate_pdf_pages` | pdf | Rotate pages in PDF document |
| `run_bash` | system | Execute bash commands (Unix/macOS) |
| `run_powershell` | system | Execute PowerShell commands (Windows) |
| `set_env_var` | system | Set environment variable value |
| `setup_rotating_log` | logging | Set up automatic log file rotation |
| `sleep_milliseconds` | utilities | Sleep for millisecond durations |
| `sleep_seconds` | utilities | Sleep for specified seconds with interrupt |
| `smart_split_lines` | text | Split text into lines intelligently |
| `split_pdf_by_pages` | pdf | Split PDF into smaller files |
| `strip_html_tags` | text | Remove HTML tags from text |
| `text_to_pdf` | pdf | Convert plain text to PDF |
| `to_camel_case` | text | Convert text to camelCase |
| `to_snake_case` | text | Convert text to snake_case |
| `to_title_case` | text | Convert text to Title Case |
| `trace_variable_changes` | utilities | Trace how variables change |
| `url_decode` | crypto | Decode URL-encoded string |
| `url_encode` | crypto | Encode string for URL usage |
| `validate_config_schema` | data | Validate configuration against schema |
| `validate_csv_format` | data | Validate CSV file format |
| `validate_date_format` | datetime | Validate date string format |
| `validate_file_content` | file_system | Validate file content format |
| `validate_function_call` | utilities | Validate function call before execution |
| `validate_json_schema` | data | Validate JSON against schema |
| `validate_path` | file_system | Validate file/directory path |
| `validate_schema_simple` | data | Simple schema validation |
| `verify_hash` | crypto | Verify hash against expected value |
| `watch_file_changes` | monitoring | Watch file for changes |
| `write_csv_file` | data | Write data to CSV file |
| `write_file_from_string` | file_system | Write string content to file |
| `write_json_file` | data | Write data to JSON file |
| `write_toml_config` | data | Write data to TOML file |
| `write_yaml_config` | data | Write data to YAML file |

## Module Overview

### File System Tools (18 functions)
**Core file and directory operations**

| Function | Purpose |
|----------|---------|
| `read_file_to_string` | Read complete file content |
| `write_file_from_string` | Write content to file |
| `append_to_file` | Add content to existing file |
| `copy_file` | Copy file to new location |
| `move_file` | Move/rename file |
| `delete_file` | Remove file |
| `create_directory` | Create directory structure |
| `delete_directory` | Remove directory and contents |
| `list_directory_contents` | List immediate directory contents |
| `list_all_directory_contents` | Recursively list all contents |
| `generate_directory_tree` | Create visual tree representation |
| `file_exists` | Check file existence |
| `directory_exists` | Check directory existence |
| `get_file_info` | Get detailed file metadata |
| `get_file_size` | Get file size in bytes |
| `is_empty_directory` | Check if directory is empty |
| `validate_path` | Validate path format and safety |
| `validate_file_content` | Validate file content format |

### Text Processing Tools (10 functions)
**Text manipulation and formatting**

| Function | Purpose |
|----------|---------|
| `clean_whitespace` | Remove extra whitespace |
| `normalize_line_endings` | Standardize line endings |
| `normalize_unicode` | Normalize Unicode representation |
| `strip_html_tags` | Remove HTML markup |
| `to_snake_case` | Convert to snake_case |
| `to_camel_case` | Convert to camelCase |
| `to_title_case` | Convert to Title Case |
| `smart_split_lines` | Intelligent line splitting |
| `extract_sentences` | Split into sentences |
| `join_with_oxford_comma` | Join with proper comma usage |

### Data Processing Tools (23 functions)
**JSON, CSV, and configuration file operations**

#### JSON Operations (6 functions)
- `read_json_file`, `write_json_file`, `validate_json_schema`
- `serialize_json_safe`, `deserialize_json_safe`, `compress_json_data`

#### CSV Operations (6 functions)
- `read_csv_file`, `write_csv_file`, `validate_csv_format`
- `clean_csv_data`, `merge_csv_files`, `convert_csv_to_json`

#### Configuration Files (6 functions)
- `read_yaml_config`, `write_yaml_config`
- `read_toml_config`, `write_toml_config`
- `read_ini_config`, `process_config_templates`

#### Data Validation (5 functions)
- `validate_config_schema`, `validate_schema_simple`
- `validate_data_types`, `check_required_fields`, `sanitize_data_input`

### DateTime Tools (40 functions)
**Comprehensive date and time operations**

#### Current Date/Time (8 functions)
- `get_current_datetime`, `get_current_date`, `get_current_time`
- `get_current_year`, `get_current_month`, `get_current_day`
- `get_current_hour`, `get_current_minute`

#### Date Arithmetic (8 functions)
- `add_days`, `subtract_days`, `add_hours`, `subtract_hours`
- `add_minutes`, `subtract_minutes`, `days_between`, `hours_between`

#### Date Ranges (8 functions)
- `generate_date_range`, `generate_business_date_range`
- `get_dates_in_month`, `get_dates_in_quarter`
- `get_quarter_start_end`, `get_month_start_end`
- `get_week_start_end`, `get_year_start_end`

#### Validation (8 functions)
- `validate_date_format`, `validate_date_range`
- `validate_time_format`, `validate_datetime_string`
- `is_valid_timezone`, `is_valid_date`, `is_valid_time`, `parse_flexible_date`

#### Business Logic (8 functions)
- `is_business_day`, `is_weekend`, `is_holiday`
- `add_business_days`, `subtract_business_days`
- `get_next_business_day`, `get_previous_business_day`, `count_business_days`

### Network Tools (4 functions)
**HTTP client and network utilities**

| Function | Purpose |
|----------|---------|
| `http_request` | Make HTTP requests with error handling |
| `resolve_hostname` | Resolve hostnames to IP addresses |
| `reverse_dns_lookup` | Perform reverse DNS lookups |
| `check_port_open` | Check port accessibility |

### Utilities Tools (8 functions)
**Timing and debugging utilities**

#### Timing Controls (3 functions)
- `sleep_seconds`, `sleep_milliseconds`, `precise_sleep`

#### Debugging Tools (5 functions)
- `inspect_function_signature`, `get_call_stack_info`
- `format_exception_details`, `validate_function_call`, `trace_variable_changes`

### System Tools (19 functions)
**Cross-platform system operations**

#### Shell Operations (3 functions)
- `execute_shell_command`, `run_bash`, `run_powershell`

#### Process Management (4 functions)
- `get_current_process_info`, `list_running_processes`
- `get_process_info`, `is_process_running`

#### Environment Variables (3 functions)
- `get_env_var`, `set_env_var`, `list_env_vars`

#### System Information (5 functions)
- `get_system_info`, `get_cpu_info`, `get_memory_info`
- `get_disk_usage`, `get_uptime`

#### Runtime Environment (4 functions)
- `inspect_runtime_environment`, `get_python_module_info`
- `get_file_system_context`, `get_network_environment`

### Crypto Tools (14 functions)
**Hashing, encoding, and generation**

#### Hashing (5 functions)
- `hash_string_md5`, `hash_string_sha256`, `hash_string_sha512`
- `hash_file_sha256`, `verify_hash`

#### Encoding (6 functions)
- `base64_encode`, `base64_decode`
- `url_encode`, `url_decode`
- `hex_encode`, `hex_decode`

#### Generation (3 functions)
- `generate_uuid4`, `generate_random_string`, `generate_random_bytes`

### PDF Tools (8 functions)
**PDF reading, creation, and manipulation**

#### PDF Reading (2 functions)
- `extract_text_from_pdf`, `get_pdf_info`

#### PDF Creation (2 functions)
- `text_to_pdf`, `merge_pdfs`

#### PDF Manipulation (4 functions)
- `split_pdf_by_pages`, `extract_pages_from_pdf`
- `rotate_pdf_pages`, `add_watermark_to_pdf`

### Archive Tools (9 functions)
**Compression and archive operations**

#### ZIP Operations (3 functions)
- `create_zip`, `extract_zip`, `compress_files`

#### TAR Operations (2 functions)
- `create_tar`, `extract_tar`

#### Individual File Compression (4 functions)
- `compress_file_gzip`, `decompress_file_gzip`
- `compress_file_bzip2`, `compress_file_xz`

### Logging Tools (5 functions)
**Structured logging and rotation**

| Function | Purpose |
|----------|---------|
| `log_info` | Log informational messages |
| `log_error` | Log error messages |
| `configure_logger` | Set up logger configuration |
| `setup_rotating_log` | Configure automatic log rotation |
| `cleanup_old_logs` | Clean up old log files |

### Monitoring Tools (8 functions)
**File watching and performance monitoring**

#### File System Monitoring (2 functions)
- `watch_file_changes`, `monitor_directory`

#### Health Checking (2 functions)
- `check_url_status`, `ping_host`

#### Performance Analysis (4 functions)
- `monitor_function_performance`, `get_system_load_average`
- `profile_code_execution`, `benchmark_disk_io`

## Common Patterns

### Return Types

**Most functions return dictionaries with structured information:**

```python
# Success response pattern
{
    "status": "success",
    "operation_type": "file_read",
    "result": "actual_data",
    "metadata": {
        "file_size": 1024,
        "timestamp": "2024-09-14T10:30:00Z"
    }
}

# Error response pattern
{
    "status": "error",
    "error_type": "FileNotFoundError",
    "error_message": "File not found: /path/to/file.txt",
    "operation_type": "file_read"
}
```

### Parameter Patterns

**Common parameter types across functions:**

- **File Paths**: `str` - Always absolute paths preferred
- **Timeouts**: `int` - Seconds, typically range 1-300
- **Limits**: `int` - Count limits, typically range 1-1000
- **Context Data**: `Dict[str, str]` - Additional metadata
- **Options**: `str` - Enum-like string choices

### Agent-Friendly Design

**All functions follow these patterns:**

- **Simple Types**: Only `str`, `int`, `float`, `bool`, `List`, `Dict`
- **No Defaults**: Parameters without default values for LLM clarity
- **Typed Lists**: `List[Dict[str, str]]` instead of bare `list`
- **Structured Returns**: Consistent dictionary responses
- **Error Handling**: All errors wrapped in `BasicAgentToolsError`

## Type Reference

### Basic Types

```python
# Standard types used throughout
str          # Text data, file paths, messages
int          # Counts, sizes, timeouts, ports
float        # Measurements, percentages, time durations
bool         # Status flags, existence checks
```

### Container Types

```python
# List types (always with item specification)
List[str]                    # List of strings
List[int]                    # List of integers
List[Dict[str, str]]         # List of string dictionaries
List[Dict[str, Union[str, int, float]]]  # Mixed value dictionaries

# Dictionary types
Dict[str, str]               # String-to-string mapping
Dict[str, Union[str, int]]   # Mixed value dictionary
Dict[str, Union[str, int, float, bool]]  # Common return type
```

### Function Signatures

**Examples of proper agent-compatible signatures:**

```python
# ✅ CORRECT - Simple types, no defaults
def read_file_to_string(file_path: str) -> Dict[str, Union[str, int]]

# ✅ CORRECT - Typed list parameter
def merge_csv_files(file_paths: List[str], output_path: str) -> Dict[str, Union[str, int, bool]]

# ✅ CORRECT - Multiple simple parameters
def http_request(method: str, url: str, timeout: int) -> Dict[str, Union[str, int, bool]]
```

### Return Type Patterns

**Standard return dictionary structures:**

```python
# File operations
Dict[str, Union[str, int, bool]] = {
    "file_path": str,
    "operation": str,
    "success": bool,
    "file_size": int,
    "timestamp": str
}

# List operations
Dict[str, Union[str, int, List[str]]] = {
    "operation": str,
    "items_found": int,
    "items": List[str],
    "search_path": str
}

# Processing operations
Dict[str, Union[str, int, float, bool]] = {
    "operation": str,
    "success": bool,
    "processing_time": float,
    "items_processed": int,
    "result_summary": str
}
```

---

## Module Documentation Links

For detailed documentation of each module:

- **[File System Tools](https://github.com/open-agent-tools/basic-open-agent-tools/blob/main/src/basic_open_agent_tools/file_system/README.md)**
- **[Text Processing Tools](https://github.com/open-agent-tools/basic-open-agent-tools/blob/main/src/basic_open_agent_tools/text/README.md)**
- **[Data Processing Tools](https://github.com/open-agent-tools/basic-open-agent-tools/blob/main/src/basic_open_agent_tools/data/README.md)**
- **[DateTime Tools](https://github.com/open-agent-tools/basic-open-agent-tools/blob/main/src/basic_open_agent_tools/datetime/README.md)**
- **[Network Tools](https://github.com/open-agent-tools/basic-open-agent-tools/blob/main/src/basic_open_agent_tools/network/README.md)**
- **[Utilities Tools](https://github.com/open-agent-tools/basic-open-agent-tools/blob/main/src/basic_open_agent_tools/utilities/README.md)**
- **[System Tools](https://github.com/open-agent-tools/basic-open-agent-tools/blob/main/src/basic_open_agent_tools/system/README.md)**
- **[Crypto Tools](https://github.com/open-agent-tools/basic-open-agent-tools/blob/main/src/basic_open_agent_tools/crypto/README.md)**
- **[PDF Tools](https://github.com/open-agent-tools/basic-open-agent-tools/blob/main/src/basic_open_agent_tools/pdf/README.md)**
- **[Archive Tools](https://github.com/open-agent-tools/basic-open-agent-tools/blob/main/src/basic_open_agent_tools/archive/README.md)**
- **[Logging Tools](https://github.com/open-agent-tools/basic-open-agent-tools/blob/main/src/basic_open_agent_tools/logging/README.md)**
- **[Monitoring Tools](https://github.com/open-agent-tools/basic-open-agent-tools/blob/main/src/basic_open_agent_tools/monitoring/README.md)**