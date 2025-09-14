# basic-open-agent-tools

An open foundational toolkit providing essential components for building AI agents with minimal dependencies for local (non-HTTP/API) actions. Designed with **agent-friendly type signatures** to eliminate "signature too complex" errors, while offering core utilities that developers can easily integrate into their agents to avoid excess boilerplate.

## Installation

```bash
pip install basic-open-agent-tools
```

Or with UV:
```bash
uv add basic-open-agent-tools
```

## Key Features

✨ **Agent-Friendly Design**: All functions use simplified type signatures to prevent "signature too complex" errors when used with AI agent frameworks

🚀 **Minimal Dependencies**: Pure Python implementation with no external dependencies for core functionality

🔧 **Modular Architecture**: Load only the tools you need with category-specific helpers, or use `load_all_tools()` for everything

🤝 **Multi-Framework Compatibility**: Native support for Google ADK, LangChain, Strands Agents, and custom agent frameworks with `@strands_tool` decorators

## Quick Start

```python
import logging
import warnings
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

import basic_open_agent_tools as boat

# Option 1: Load all tools at once (recommended)
agent_tools = boat.load_all_tools()  # All 93 functions from all modules

# Option 2: Load tools by category
fs_tools = boat.load_all_filesystem_tools()      # 18 functions
text_tools = boat.load_all_text_tools()         # 10 functions
data_tools = boat.load_all_data_tools()         # 23 functions
datetime_tools = boat.load_all_datetime_tools() # 40 functions
network_tools = boat.load_all_network_tools()   # 1 function
utilities_tools = boat.load_all_utilities_tools() # 1 function

# Merge selected categories (automatically deduplicates)
agent_tools = boat.merge_tool_lists(fs_tools, text_tools, network_tools, utilities_tools)


load_dotenv()

agent_instruction = """
**INSTRUCTION:**
You are FileOps, a specialized file and directory operations sub-agent.
Your role is to execute file operations (create, read, update, delete, move, copy) and directory operations (create, delete) with precision.
**Guidelines:**
- **Preserve Content:** Always read full file content before modifications; retain all original content except targeted changes.
- **Precision:** Execute instructions exactly, verify operations, and handle errors with specific details.
- **Communication:** Provide concise, technical status reports (success/failure, file paths, operation type, content preservation details).
- **Scope:** File/directory CRUD, move, copy, path validation. No code analysis.
- **Confirmation:** Confirm completion to the senior developer with specific details of modifications.
"""

logging.basicConfig(level=logging.ERROR)
warnings.filterwarnings("ignore")

file_ops_agent = Agent(
    model=LiteLlm(model="anthropic/claude-3-5-haiku-20241022"),
    name="FileOps",
    instruction=agent_instruction,
    description="Specialized file and directory operations sub-agent for the Python developer.",
    tools=agent_tools,
)

"""
The above would load:

File and Directory Operations:
    read_file_to_string
    write_file_from_string
    append_to_file
    list_directory_contents
    create_directory
    delete_file
    delete_directory
    move_file
    copy_file
    get_file_info
    file_exists
    directory_exists
    get_file_size
    is_empty_directory
    list_all_directory_contents
    generate_directory_tree
    validate_path
    validate_file_content

Text Processing Tools:
    clean_whitespace
    normalize_line_endings
    strip_html_tags
    normalize_unicode
    to_snake_case
    to_camel_case
    to_title_case
    smart_split_lines
    extract_sentences
    join_with_oxford_comma

Network Tools:
    http_request

Utilities Tools:
    sleep_seconds

"""

```

## Documentation

- **[Getting Started](docs/getting-started.md)** - Installation and quick start guide
- **[Examples](docs/examples.md)** - Detailed usage examples and patterns
- **[Contributing](docs/contributing.md)** - Development setup and guidelines

## Current Features

### File System Tools ✅ (18 functions)
📖 **[Complete Documentation](src/basic_open_agent_tools/file_system/README.md)**

- File operations (read, write, append, delete, copy, move)
- Directory operations (create, list, delete, tree visualization)
- File information and existence checking
- Path validation and security features

### Text Processing Tools ✅ (10 functions)
📖 **[Complete Documentation](src/basic_open_agent_tools/text/README.md)**

- Text cleaning and whitespace normalization
- Case conversion utilities (snake_case, camelCase, Title Case)
- Smart text splitting and sentence extraction
- HTML tag removal and Unicode normalization

### Data Processing Tools ✅ (23 functions)
📖 **[Complete Documentation](src/basic_open_agent_tools/data/README.md)**

- **JSON Processing**: Safe serialization, validation, compression
- **CSV Operations**: Reading, writing, cleaning, validation
- **Configuration Files**: YAML, TOML, INI processing
- **Data Validation**: Schema checking, type validation, field validation
- **Agent-Friendly Signatures**: All functions use basic Python types for maximum AI framework compatibility

### DateTime Tools ✅ (40 functions)
📖 **[Complete Documentation](src/basic_open_agent_tools/datetime/README.md)**

- **Current Date/Time**: Timezone-aware current date/time operations
- **Date Arithmetic**: Add/subtract days, hours, minutes with proper handling
- **Date Ranges**: Generate date ranges, quarters, business days
- **Validation**: ISO format validation, range checking, format verification
- **Business Logic**: Business day calculations, timezone conversions
- **Information Extraction**: Weekday names, month names, leap years

### Network Tools ✅ (1 function)
📖 **[Complete Documentation](src/basic_open_agent_tools/network/README.md)**

- **HTTP Client**: Make API calls and fetch web data with comprehensive error handling
- **Agent-Friendly**: Simplified type signatures and structured responses
- **Strands Compatible**: Native `@strands_tool` decorator support
- **Security**: SSL verification, timeout controls, proper error handling

### Utilities Tools ✅ (1 function)
📖 **[Complete Documentation](src/basic_open_agent_tools/utilities/README.md)**

- **Timing Controls**: Pause execution with interrupt handling
- **Precision Sleep**: High-precision timing for timing-critical operations
- **Strands Compatible**: Native `@strands_tool` decorator support
- **Agent-Friendly**: Structured responses with detailed timing information

**Total: 93 implemented functions** across 6 categories, designed specifically for building AI agents with local operations and HTTP requests.

## Helper Functions

### Load All Tools at Once ⚡
```python
import basic_open_agent_tools as boat

# Get all 93 functions from all modules
all_tools = boat.load_all_tools()

# Use with any agent framework
agent = Agent(tools=all_tools)
```

### Selective Loading 🎯
```python
# Load specific categories
network_tools = boat.load_all_network_tools()        # HTTP client
utilities_tools = boat.load_all_utilities_tools()    # Sleep functions
fs_tools = boat.load_all_filesystem_tools()          # File operations

# Merge selected tools
custom_tools = boat.merge_tool_lists(network_tools, fs_tools)
```

### Future Modules 🚧

- **System Tools** 📖 **[Planned Features](src/basic_open_agent_tools/system/README.md)** - Cross-platform shell (`execute_shell_command`, `run_powershell`, `run_bash`), process management (`run_command`, `kill_process`, `list_processes`), system info (`get_cpu_usage`, `get_memory_usage`, `get_disk_space`), environment variables (`set_env_var`, `get_env_var`, `list_env_vars`)
- **Crypto Tools** 📖 **[Planned Features](src/basic_open_agent_tools/crypto/README.md)** - Hashing (`hash_md5`, `hash_sha256`, `verify_hash`), encoding (`base64_encode`, `base64_decode`, `url_encode`), basic crypto (`generate_uuid`, `generate_random_string`)
- **PDF Tools** 📋 **Planned** - Reading (`extract_text_from_pdf`, `get_pdf_info`), creation (`text_to_pdf`, `merge_pdfs`)
- **Archive Tools** 📋 **Planned** - Compression (`create_zip`, `extract_zip`, `compress_files`), formats (`create_tar`, `extract_tar`)
- **Logging Tools** 📋 **Planned** - Structured logging (`log_info`, `log_error`, `configure_logger`), file rotation (`setup_rotating_log`, `cleanup_old_logs`)
- **Monitoring Tools** 📋 **Planned** - File watching (`watch_file_changes`, `monitor_directory`), health checks (`check_url_status`, `ping_host`)

## Contributing

We welcome contributions! Please see our [Contributing Guide](docs/contributing.md) for development setup, coding standards, and pull request process.



