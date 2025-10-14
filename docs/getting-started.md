# Getting Started

## Installation

```bash
# Using pip
pip install basic-open-agent-tools

# Using uv
uv add basic-open-agent-tools
```

### Optional Dependencies

```bash
# All features
pip install basic-open-agent-tools[all]

# Specific features
pip install basic-open-agent-tools[system]      # Process management
pip install basic-open-agent-tools[pdf]         # PDF operations
pip install basic-open-agent-tools[word]        # Word documents
pip install basic-open-agent-tools[excel]       # Excel spreadsheets
pip install basic-open-agent-tools[powerpoint]  # PowerPoint presentations
pip install basic-open-agent-tools[image]       # Image processing
pip install basic-open-agent-tools[xml]         # XML parsing
```

## Core Concepts

**basic-open-agent-tools** is a toolkit designed for AI agent frameworks, providing 151 foundational functions across 20 modules that agents can use for local (non-HTTP/API) operations.

Key features:
- **Agent-Friendly**: Google ADK compatible signatures prevent "signature too complex" errors
- **Minimal Dependencies**: Pure Python core with optional dependencies only when needed
- **Type Safety**: Full type annotations for all functions
- **Comprehensive Docstrings**: Help AI understand function purpose and usage
- **Safety First**: Write operations include `skip_confirm` parameter for protection

## Quick Start

### Load All Tools

```python
import basic_open_agent_tools as boat

# Load all 151 functions
all_tools = boat.load_all_tools()

# Use with your agent framework
from google.adk.agents import Agent
agent = Agent(tools=all_tools)
```

### Load Specific Categories

```python
import basic_open_agent_tools as boat

# Load by category
fs_tools = boat.load_all_filesystem_tools()    # 18 functions
text_tools = boat.load_all_text_tools()        # 10 functions
data_tools = boat.load_all_data_tools()        # 23 functions

# Merge for agent use (automatically deduplicates)
agent_tools = boat.merge_tool_lists(fs_tools, text_tools, data_tools)
```

### Individual Function Imports

```python
# Import only what you need
from basic_open_agent_tools.file_system.operations import (
    read_file_to_string,
    write_file_from_string
)
from basic_open_agent_tools.text.processing import (
    clean_whitespace,
    normalize_line_endings
)

tools = [read_file_to_string, write_file_from_string, clean_whitespace]
```

### Direct Usage

While designed for agents, functions work directly too:

```python
from basic_open_agent_tools import file_system

# Read and write files
content = file_system.read_file_to_string("example.txt")
file_system.write_file_from_string(
    file_path="output.txt",
    content="Hello World!",
    skip_confirm=False  # Safe default
)
```

## Available Modules

### Core Operations (91 functions)
- **file_system** (18) - File and directory operations
- **text** (10) - Text processing and formatting
- **data** (23) - JSON, CSV, YAML, TOML, INI
- **datetime** (40) - Date/time operations

### Document Processing
- **pdf** (8) - PDF operations
- **word** - Word documents
- **excel** - Excel spreadsheets
- **powerpoint** - PowerPoint files
- **markdown** - Markdown processing
- **html** - HTML processing
- **xml** - XML parsing

### System & Network (31 functions)
- **system** (19) - Shell, processes, system info
- **network** (4) - HTTP, DNS, port checking
- **utilities** (8) - Debugging, timing

### Security & Data (23 functions)
- **crypto** (14) - Hashing, encoding
- **archive** (9) - ZIP, TAR, compression

### Additional (6+ functions)
- **logging** (5) - Structured logging
- **todo** - Task management
- **diagrams** - Diagram generation
- **image** - Image processing

## Safety Features

Many write operations include `skip_confirm` parameter:

```python
# Safe by default - raises error if file exists
result = boat.file_system.write_file_from_string(
    file_path="/tmp/example.txt",
    content="Hello, World!",
    skip_confirm=False
)

# Explicit overwrite when needed
result = boat.file_system.write_file_from_string(
    file_path="/tmp/example.txt",
    content="Updated content",
    skip_confirm=True  # Overwrites existing file
)
```

## Migration Notice

**Code analysis, git tools, profiling, and static analysis** modules (39 functions) migrated to **[coding-open-agent-tools](https://github.com/open-agent-tools/coding-open-agent-tools)**.

For coding-specific tools:
```bash
pip install coding-open-agent-tools
```

## Next Steps

- Check [API Reference](api-reference.md) for complete function listings
- Read [Examples](examples.md) for detailed usage patterns
- See [FAQ](faq.md) for common questions
- View [Contributing](contributing.md) to help develop the project
