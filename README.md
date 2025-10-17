# basic-open-agent-tools

An open foundational toolkit providing essential components for building AI agents with minimal dependencies for local (non-HTTP/API) actions.

## 🆕 What's New in v0.13.10

✅ **Test Improvements**: Fixed 8 test failures related to missing required parameters in network, system, and text modules

📊 **Coverage Enhancements**: Improved test coverage across 4 modules (text/processing, network/dns, system/environment, system/processes)

🐛 **Bug Fixes**: Fixed validation order in text processing to check types before logging operations

### Previous Release (v0.13.7)

🧹 **Decorator Cleanup**: Complete deprecation of `@adk_tool` decorator across all 351 functions - using `@strands_tool` only for cleaner codebase

📝 **Documentation Updates**: Enhanced agent prompt and CLAUDE.md with accurate decorator architecture (Google ADK uses signatures, not decorators)

✅ **Quality Improvements**: Updated all TODO files to v0.13.7 with decorator deprecation notes

### Previous Release (v0.13.6)

💬 **Enhanced Confirmation Previews**: Confirmation dialogs now show meaningful previews of new content being created instead of just old file sizes

📊 **Better User Feedback**: File writes show content previews, CSV writes show row/column counts with sample data, archive operations show file lists

🎯 **Comprehensive Coverage**: All 22 confirmation operations now provide context-aware previews for better decision making

### Previous Release (v0.13.3)

🔍 **Structured Logging**: Migrated 157 print statements to Python logging framework with `BOAT_LOG_LEVEL` environment variable control

🛡️ **Enhanced Error Handling**: Replaced all assert statements with explicit type checking and descriptive error messages

🧹 **Code Quality**: Improved type safety and debugging with proper exception raising patterns

### Previous Release (v0.13.2)

🎛️ **Enhanced Confirmation System**: Hybrid confirmation mode intelligently adapts to execution context (agent vs interactive vs bypass)

🤖 **Agent-Aware Operations**: File operations now raise structured `CONFIRMATION_REQUIRED` errors that LLM agents can interpret and act on

✅ **Smart Defaults**: `skip_confirm=False` safely handles both human interactions (prompts) and agent workflows (structured errors)

🔧 **Test Coverage**: Comprehensive test suite (27 tests) for confirmation system with 100% coverage

### Previous Release (v0.13.1)

🔀 **Module Migration**: Code analysis, git tools, profiling, and static analysis modules (39 functions) migrated to **[coding-open-agent-tools](https://github.com/open-agent-tools/coding-open-agent-tools)**

🎯 **Refocused Scope**: 151 foundational functions across 20 modules

📦 **Sibling Package**: For coding-specific tools, see **[coding-open-agent-tools](https://github.com/open-agent-tools/coding-open-agent-tools)**

## Installation

```bash
pip install basic-open-agent-tools
```

Or with UV:
```bash
uv add basic-open-agent-tools
```

### Optional Dependencies

```bash
# All features
pip install basic-open-agent-tools[all]

# Specific features
pip install basic-open-agent-tools[system]      # Process management, system info
pip install basic-open-agent-tools[pdf]         # PDF reading and creation
pip install basic-open-agent-tools[xml]         # XML parsing and validation
pip install basic-open-agent-tools[word]        # Word document operations
pip install basic-open-agent-tools[excel]       # Excel spreadsheet operations
pip install basic-open-agent-tools[powerpoint]  # PowerPoint presentations
pip install basic-open-agent-tools[image]       # Image processing
```

## Quick Start

```python
import basic_open_agent_tools as boat

# Load all tools
all_tools = boat.load_all_tools()  # 326 functions

# Or load specific categories
fs_tools = boat.load_all_filesystem_tools()
text_tools = boat.load_all_text_tools()
data_tools = boat.load_all_data_tools()

# Merge selected categories
custom_tools = boat.merge_tool_lists(fs_tools, text_tools, data_tools)

# Use with any agent framework
from google.adk.agents import Agent
agent = Agent(tools=all_tools)
```

## Available Modules

**21 modules** with **326 total functions** — all with `@strands_tool` decorator and Google ADK compatible signatures.

### 📊 Complete Module Breakdown

| Module | Functions | Description |
|--------|-----------|-------------|
| **Core Operations** | | |
| `file_system` | 19 | File and directory operations, tree generation |
| `text` | 10 | Text processing, case conversion, formatting |
| `data` | 23 | JSON, CSV, YAML, TOML processing and validation |
| `datetime` | 40 | Date/time operations, timezones, business days |
| **Document Processing** | | |
| `excel` | 24 | Spreadsheet reading, writing, formatting, charts |
| `xml` | 24 | XML parsing, authoring, validation, transformation |
| `pdf` | 20 | PDF creation, reading, manipulation |
| `word` | 18 | Word document operations and formatting |
| `html` | 17 | HTML generation and parsing |
| `diagrams` | 16 | Mermaid and PlantUML diagram generation |
| `markdown` | 12 | Markdown generation and parsing |
| `powerpoint` | 10 | PowerPoint presentation operations |
| **System & Network** | | |
| `system` | 19 | Shell commands, process management, environment |
| `network` | 4 | HTTP client, DNS lookup, port checking |
| `utilities` | 8 | Debugging, timing, performance tools |
| **Security & Data** | | |
| `crypto` | 14 | Hashing, encoding, UUID/token generation |
| `color` | 14 | Color conversion, palette generation, analysis |
| `image` | 12 | Image manipulation and metadata reading |
| `archive` | 9 | ZIP, TAR, GZIP, BZIP2, XZ compression |
| **Task Management** | | |
| `todo` | 8 | Task creation, validation, management |
| `logging` | 5 | Structured logging and log rotation |
| **TOTAL** | **326** | |

## Key Features

✨ **Agent-Friendly**: Simplified type signatures prevent "signature too complex" errors

🚀 **Minimal Dependencies**: Pure Python core with optional dependencies only when needed

🔧 **Modular**: Load only what you need

🤝 **Multi-Framework**: Works with Google ADK (signature-based), LangChain, Strands Agents (@strands_tool decorator), custom frameworks

🔍 **Enhanced Feedback**: Detailed operation confirmations with `skip_confirm` safety parameter

## Safety Features

### Smart Confirmation System (3 Modes)

All write/delete operations include a `skip_confirm` parameter with intelligent confirmation handling:

**🔄 Bypass Mode** - `skip_confirm=True` or `BYPASS_TOOL_CONSENT=true` env var
- Proceeds immediately without prompts
- Perfect for CI/CD and automation

**💬 Interactive Mode** - Terminal with `skip_confirm=False`
- Prompts user with `y/n` confirmation
- Shows preview info (file sizes, etc.)

**🤖 Agent Mode** - Non-TTY with `skip_confirm=False`
- Raises `CONFIRMATION_REQUIRED` error with instructions
- LLM agents can ask user and retry with `skip_confirm=True`

```python
# Safe by default - adapts to context
result = boat.file_system.write_file_from_string(
    file_path="/tmp/example.txt",
    content="Hello, World!",
    skip_confirm=False  # Interactive prompt OR agent error
)

# Explicit overwrite
result = boat.file_system.write_file_from_string(
    file_path="/tmp/example.txt",
    content="Updated content",
    skip_confirm=True  # Bypasses all confirmations
)

# Automation mode
import os
os.environ['BYPASS_TOOL_CONSENT'] = 'true'
# All confirmations bypassed for CI/CD
```

## Documentation

- **[Getting Started](docs/getting-started.md)** - Installation and setup
- **[API Reference](docs/api-reference.md)** - Complete function reference
- **[Examples](docs/examples.md)** - Usage examples and patterns
- **[FAQ](docs/faq.md)** - Troubleshooting and common questions
- **[Contributing](docs/contributing.md)** - Development guidelines
- **[Changelog](CHANGELOG.md)** - Version history

## Helper Functions

```python
import basic_open_agent_tools as boat

# Category loaders
boat.load_all_filesystem_tools()
boat.load_all_text_tools()
boat.load_all_data_tools()
boat.load_all_datetime_tools()
boat.load_all_network_tools()
boat.load_all_utilities_tools()
boat.load_all_system_tools()
boat.load_all_crypto_tools()
boat.load_all_pdf_tools()
boat.load_all_archive_tools()
boat.load_all_logging_tools()
boat.load_all_diagrams_tools()
boat.load_all_excel_tools()
boat.load_all_html_tools()
boat.load_all_image_tools()
boat.load_all_markdown_tools()
boat.load_all_powerpoint_tools()
boat.load_all_todo_tools()
boat.load_all_word_tools()
boat.load_all_xml_tools()

# Specialized data loaders
boat.load_data_config_tools()  # YAML, TOML, INI
boat.load_data_csv_tools()     # CSV operations
boat.load_data_json_tools()    # JSON operations
boat.load_data_validation_tools()  # Data validation

# Utility functions
boat.merge_tool_lists(*tool_lists)  # Merge and deduplicate
boat.list_all_available_tools()     # List all tool names
boat.get_tool_info(tool_name)       # Get tool metadata
```

## Contributing

We welcome contributions! See our [Contributing Guide](docs/contributing.md) for development setup, coding standards, and pull request process.

## License

MIT License - see [LICENSE](LICENSE) for details.
