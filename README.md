# basic-open-agent-tools

An open foundational toolkit providing essential components for building AI agents with minimal dependencies for local (non-HTTP/API) actions.

## 🆕 What's New in v1.3.0

🎯 **NEW: Loadouts** - 6 pre-configured tool bundles for specific use cases (coder, docs writer, data analyst, web publisher, visual designer, office suite)

📝 **Markdown Enhancements**: Advanced HTML conversion with blockquotes, tables, task lists, and 5 new parsing functions

📅 **DateTime Improvements**: 6 new formatting/parsing functions for human-readable dates, times, and durations

### Recent Updates

**v1.2.0** - Markdown and datetime enhancements, datetime essentials helper

**v1.1.0** - New helper functions: Added 10 use-case focused tool loaders for targeted agent capabilities

**v0.13.6** - Enhanced confirmation dialogs with content previews for better decision-making

**v0.13.3** - Added structured logging with `BOAT_LOG_LEVEL` environment variable control

**v0.13.2** - Smart confirmation system that adapts to interactive, agent, or automation contexts

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

# Option 1: Load all tools (337 functions)
all_tools = boat.load_all_tools()

# Option 2: Use pre-configured loadouts for specific use cases
coder_tools = boat.load_coder_loadout()              # ~105 tools for development
docs_tools = boat.load_docs_loadout()                # ~130 tools for documentation
analyst_tools = boat.load_data_analyst_loadout()     # ~115 tools for data analysis
web_tools = boat.load_web_publisher_loadout()        # ~90 tools for web content
designer_tools = boat.load_visual_designer_loadout() # ~60 tools for graphics
office_tools = boat.load_office_suite_loadout()      # ~80 tools for Office work

# Option 3: Load specific categories
fs_tools = boat.load_all_filesystem_tools()
text_tools = boat.load_all_text_tools()
data_tools = boat.load_all_data_tools()

# Merge selected categories
custom_tools = boat.merge_tool_lists(fs_tools, text_tools, data_tools)

# Use with any agent framework
from google.adk.agents import Agent

# General-purpose agent
agent = Agent(tools=all_tools)

# Specialized developer agent
dev_agent = Agent(tools=boat.load_coder_loadout())

# Documentation writer agent
docs_agent = Agent(tools=boat.load_docs_loadout())
```

## Available Modules

**21 modules** with **337 total functions** — all with `@strands_tool` decorator and Google ADK compatible signatures.

### 📊 Complete Module Breakdown

| Module | Functions | Description |
|--------|-----------|-------------|
| **Core Operations** | | |
| `file_system` | 19 | File and directory operations, tree generation |
| `text` | 10 | Text processing, case conversion, formatting |
| `data` | 23 | JSON, CSV, YAML, TOML processing and validation |
| `datetime` | 46 | Date/time operations, timezones, formatting, parsing |
| **Document Processing** | | |
| `excel` | 24 | Spreadsheet reading, writing, formatting, charts |
| `xml` | 24 | XML parsing, authoring, validation, transformation |
| `pdf` | 20 | PDF creation, reading, manipulation |
| `word` | 18 | Word document operations and formatting |
| `html` | 17 | HTML generation and parsing |
| `diagrams` | 16 | Mermaid and PlantUML diagram generation |
| `markdown` | 17 | Markdown generation, parsing, HTML conversion |
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
| **TOTAL** | **337** | |

## Key Features

✨ **Agent-Friendly**: Simplified type signatures prevent "signature too complex" errors

🚀 **Minimal Dependencies**: Pure Python core with optional dependencies only when needed

🔧 **Modular**: Load only what you need

🤝 **Multi-Framework**: Works with Google ADK (signature-based), LangChain, Strands Agents (@strands_tool decorator), custom frameworks

🔍 **Enhanced Feedback**: Detailed operation confirmations with `skip_confirm` safety parameter

🎯 **Pre-configured Loadouts**: 6 curated tool bundles optimized for specific use cases with minimal overlap

## Loadouts - Pre-configured Tool Bundles

Choose the right loadout for your agent's role to minimize token usage and maximize relevance:

### 1. `load_coder_loadout()` (~105 tools)
**For**: Software developers, DevOps engineers, automation scripts

**Includes**: File system, system operations, network, logging, crypto, archive, config files (YAML, TOML, JSON, INI)

**Example Agents**:
- DevOps agent managing deployments and server configs
- Project setup agent scaffolding new projects

### 2. `load_docs_loadout()` (~130 tools)
**For**: Technical writers, documentation creators, report generators

**Includes**: Word, PDF, Markdown, HTML, diagrams, images, text processing

**Example Agents**:
- Technical writer creating API documentation
- Report generator compiling findings into formatted documents

### 3. `load_data_analyst_loadout()` (~115 tools)
**For**: Data analysts, financial analysts, business intelligence

**Includes**: Excel, CSV, data validation, diagrams, structured data formats (JSON, YAML, XML)

**Example Agents**:
- Financial analyst processing budgets and creating reports
- BI agent generating dashboards and analytics

### 4. `load_web_publisher_loadout()` (~90 tools)
**For**: Web developers, content managers, blog publishers

**Includes**: HTML, XML, Markdown, network operations, text processing

**Example Agents**:
- Blog publisher converting drafts to HTML
- Documentation site generator creating static websites

### 5. `load_visual_designer_loadout()` (~60 tools)
**For**: Graphic designers, infographic creators, visual content producers

**Includes**: Image processing, diagrams, color tools, file operations

**Example Agents**:
- Infographic generator creating data visualizations
- Brand asset manager processing images and color palettes

### 6. `load_office_suite_loadout()` (~80 tools)
**For**: Office workers, business users, administrative assistants

**Includes**: Excel, Word, PowerPoint, file operations, datetime essentials

**Example Agents**:
- Office assistant creating business reports and presentations
- Administrative agent managing documents and schedules

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

### Rapid Loaders - Pre-configured Loadouts (6 total)

Optimized tool bundles for specific roles and use cases - minimal overlap, maximum relevance:

```python
import basic_open_agent_tools as boat

# Loadouts - Choose the one that matches your agent's role
boat.load_coder_loadout()           # ~105 tools - Development, DevOps, automation
boat.load_docs_loadout()            # ~130 tools - Document creation (Word, PDF, Markdown, HTML)
boat.load_data_analyst_loadout()    # ~115 tools - Data analysis (Excel, CSV, validation)
boat.load_web_publisher_loadout()   # ~90 tools - Web content (HTML, XML, Markdown)
boat.load_visual_designer_loadout() # ~60 tools - Graphics (Images, Diagrams, Color)
boat.load_office_suite_loadout()    # ~80 tools - Office productivity (Excel, Word, PowerPoint)
```

### Generic Loaders

Build custom tool sets by combining modules:

```python
# Master loader
boat.load_all_tools()  # Load all 337 functions

# Category loaders (21 total)
boat.load_all_filesystem_tools()
boat.load_all_text_tools()
boat.load_all_data_tools()
boat.load_all_datetime_tools()
boat.load_all_excel_tools()
boat.load_all_xml_tools()
boat.load_all_pdf_tools()
boat.load_all_word_tools()
boat.load_all_html_tools()
boat.load_all_markdown_tools()
boat.load_all_powerpoint_tools()
boat.load_all_diagrams_tools()
boat.load_all_system_tools()
boat.load_all_network_tools()
boat.load_all_utilities_tools()
boat.load_all_crypto_tools()
boat.load_all_color_tools()
boat.load_all_image_tools()
boat.load_all_archive_tools()
boat.load_all_todo_tools()
boat.load_all_logging_tools()

# Specialized data loaders (4 total)
boat.load_data_json_tools()    # JSON operations
boat.load_data_csv_tools()     # CSV operations
boat.load_data_validation_tools()  # Data validation
boat.load_data_config_tools()  # YAML, TOML, INI

# Use-case focused loaders (10 total)
boat.load_essential()          # ~25 most commonly needed tools
boat.load_core_readonly()      # 28 read-only tools (filesystem, text, data parsing)
boat.load_converters()         # 78 pure transformation tools (text, datetime, crypto, color)
boat.load_document_readers()   # Extract content from PDF, Word, Excel, PowerPoint, images
boat.load_writers()            # All file creation/modification tools
boat.load_analyst_tools()      # Data analysis and validation tools
boat.load_web_tools()          # HTML, Markdown, network operations
boat.load_devtools()           # Debugging, logging, performance measurement
boat.load_structured_data_tools()  # CSV, JSON, XML, YAML, TOML, INI
boat.load_office_suite()       # Excel, Word, PowerPoint tools
boat.load_markup_tools()       # HTML, Markdown, XML processing

# Utility functions
boat.merge_tool_lists(*tool_lists)  # Merge and deduplicate
boat.list_all_available_tools()     # List all tool names
boat.get_tool_info(tool_name)       # Get tool metadata
```

## Contributing

We welcome contributions! See our [Contributing Guide](docs/contributing.md) for development setup, coding standards, and pull request process.

## License

MIT License - see [LICENSE](LICENSE) for details.
