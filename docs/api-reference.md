# API Reference

Complete reference for all 151 functions across 20 modules in basic-open-agent-tools v0.13.1.

## Module Overview

### Core Operations (91 functions)

- **[file_system](../src/basic_open_agent_tools/file_system/README.md)** (18 functions) - File and directory operations
- **[text](../src/basic_open_agent_tools/text/README.md)** (10 functions) - Text processing and formatting
- **[data](../src/basic_open_agent_tools/data/README.md)** (23 functions) - JSON, CSV, YAML, TOML, INI processing
- **[datetime](../src/basic_open_agent_tools/datetime/README.md)** (40 functions) - Date/time operations and calculations

### Document Processing (modules implemented, function counts vary)

- **[pdf](../src/basic_open_agent_tools/pdf/README.md)** (8 functions) - PDF reading, creation, manipulation
- **word** - Word document operations (.docx files)
- **excel** - Excel spreadsheet operations (.xlsx files)
- **powerpoint** - PowerPoint presentation operations (.pptx files)
- **markdown** - Markdown processing and conversion
- **html** - HTML processing and manipulation
- **xml** - XML parsing and validation

### System & Network (31 functions)

- **[system](../src/basic_open_agent_tools/system/README.md)** (19 functions) - Shell commands, process management, system info
- **[network](../src/basic_open_agent_tools/network/README.md)** (4 functions) - HTTP client, DNS resolution, port checking
- **[utilities](../src/basic_open_agent_tools/utilities/README.md)** (8 functions) - Debugging, timing, code validation

### Security & Data (23 functions)

- **[crypto](../src/basic_open_agent_tools/crypto/README.md)** (14 functions) - Hashing, encoding, random generation
- **[archive](../src/basic_open_agent_tools/archive/README.md)** (9 functions) - ZIP, TAR, GZIP, BZIP2, XZ compression

### Additional Utilities (6+ functions)

- **[logging](../src/basic_open_agent_tools/logging/README.md)** (5 functions) - Structured logging and rotation
- **todo** - Task management operations
- **diagrams** - Diagram generation utilities
- **image** - Image processing operations

## Quick Function Lookup

For detailed function signatures, parameters, and examples, see the module-specific README files linked above.

### Common Patterns

All functions follow Google ADK standards:

```python
def function_name(
    param1: str,           # Only JSON-serializable types
    param2: int,           # No default values
    skip_confirm: bool     # Safety parameter for write ops
) -> dict:                 # Clear return type
    """Brief description.

    Detailed explanation for LLM understanding.

    Args:
        param1: Description
        param2: Description
        skip_confirm: If True, skip safety confirmations

    Returns:
        Dictionary with operation details

    Raises:
        ValueError: When parameters are invalid
    """
    pass
```

### Safety Parameter: skip_confirm

Write/delete operations include `skip_confirm` with **3-mode intelligent confirmation**:

**Modes:**
1. **Bypass** - `skip_confirm=True` or `BYPASS_TOOL_CONSENT=true` env var → proceeds immediately
2. **Interactive** - TTY terminal with `skip_confirm=False` → prompts user `y/n`
3. **Agent** - Non-TTY with `skip_confirm=False` → raises `CONFIRMATION_REQUIRED` error

**Functions with skip_confirm:**
- **File operations**: `write_file_from_string`, `create_directory`, `delete_file`, `delete_directory`, `move_file`, `copy_file`, `file_editor` (create)
- **Data operations**: `write_csv_simple`, `write_ini_file`, `write_yaml_file`, `write_toml_file`
- **Archive operations**: `create_zip`, `extract_zip`, `compress_files`, `create_tar`, `compress_file_gzip`, `compress_file_bzip2`, `compress_file_xz`
- **TODO operations**: `delete_task`

**For detailed confirmation system documentation**, see [Getting Started - Safety Features](getting-started.md#safety-features).

## Loading Tools

```python
import basic_open_agent_tools as boat

# Load all tools
all_tools = boat.load_all_tools()  # All 151 functions

# Load specific modules
fs_tools = boat.load_all_filesystem_tools()
text_tools = boat.load_all_text_tools()
data_tools = boat.load_all_data_tools()
datetime_tools = boat.load_all_datetime_tools()
network_tools = boat.load_all_network_tools()
utilities_tools = boat.load_all_utilities_tools()
system_tools = boat.load_all_system_tools()
crypto_tools = boat.load_all_crypto_tools()
pdf_tools = boat.load_all_pdf_tools()
archive_tools = boat.load_all_archive_tools()
logging_tools = boat.load_all_logging_tools()
diagrams_tools = boat.load_all_diagrams_tools()
excel_tools = boat.load_all_excel_tools()
html_tools = boat.load_all_html_tools()
image_tools = boat.load_all_image_tools()
markdown_tools = boat.load_all_markdown_tools()
powerpoint_tools = boat.load_all_powerpoint_tools()
todo_tools = boat.load_all_todo_tools()
word_tools = boat.load_all_word_tools()
xml_tools = boat.load_all_xml_tools()

# Specialized data loaders
config_tools = boat.load_data_config_tools()      # YAML, TOML, INI
csv_tools = boat.load_data_csv_tools()            # CSV operations
json_tools = boat.load_data_json_tools()          # JSON operations
validation_tools = boat.load_data_validation_tools()  # Data validation

# Merge selected tools
custom_tools = boat.merge_tool_lists(fs_tools, text_tools, network_tools)
```

## Helper Functions

```python
# List all available tool names
all_names = boat.list_all_available_tools()

# Get metadata for specific tool
tool_info = boat.get_tool_info("read_file_to_string")
```

## Migration Notice

**Code analysis, git tools, profiling, and static analysis** modules (39 functions) have been migrated to **[coding-open-agent-tools](https://github.com/open-agent-tools/coding-open-agent-tools)**.

For coding-specific functionality:
```bash
pip install coding-open-agent-tools
```

## See Also

- [Getting Started Guide](getting-started.md) - Installation and setup
- [Examples](examples.md) - Usage examples and patterns
- [FAQ](faq.md) - Common questions and troubleshooting
- [Changelog](../CHANGELOG.md) - Version history and changes
