# basic-open-agent-tools

An open foundational toolkit providing essential components for building AI agents with minimal dependencies for local (non-HTTP/API) actions. Designed to offer core utilities and interfaces that developers can easily integrate into their own agents to avoid excess boilerplate, while being simpler than solutions requiring MCP or A2A.

## Installation

```bash
pip install basic-open-agent-tools
```

Or with UV:
```bash
uv add basic-open-agent-tools
```

## Quick Start

```python
import logging
import warnings
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

import basic_open_agent_tools as boat

# Load tools by category
fs_tools = boat.load_all_filesystem_tools()    # 18 functions
text_tools = boat.load_all_text_tools()       # 10 functions

# Merge for agent use (automatically deduplicates)
agent_tools = boat.merge_tool_lists(fs_tools, text_tools)


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

"""

```

## Documentation

- **[Getting Started](docs/getting-started.md)** - Installation and quick start guide
- **[Examples](docs/examples.md)** - Detailed usage examples and patterns
- **[Contributing](docs/contributing.md)** - Development setup and guidelines

## Current Features

### File System Tools ✅ (18 functions)
- File operations (read, write, append, delete, copy, move)
- Directory operations (create, list, delete, tree visualization)
- File information and existence checking
- Path validation and error handling

### Text Processing Tools ✅ (10 functions)
- Text cleaning and normalization
- Case conversion utilities (snake_case, camelCase, Title Case)
- Smart text splitting and sentence extraction
- HTML tag removal and Unicode normalization

### Data Tools ✅ (28 functions - Phase 1 Complete)
**Phase 1 ✅**: Data structures, JSON/CSV processing, validation (28 functions)
- Data structure manipulation (flatten, merge, nested access)
- JSON serialization with compression and validation  
- CSV file processing and data cleaning
- Schema validation and data type checking

**Phase 2 📋**: Object serialization, configuration files (15 functions)
**Phase 3 📋**: Data transformation, YAML/TOML support (16 functions)  
**Phase 4 📋**: Binary data, archives, streaming (18 functions)
**Phase 5 📋**: Caching, database processing (13 functions)

### Future Modules 🚧
- **Network Tools** - HTTP utilities, API helpers
- **System Tools** - Process management, system information  
- **Crypto Tools** - Hashing, encoding, basic cryptographic utilities
- **Utilities** - Development and debugging helpers

## Contributing

We welcome contributions! Please see our [Contributing Guide](docs/contributing.md) for development setup, coding standards, and pull request process.



