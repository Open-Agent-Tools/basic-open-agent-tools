# Getting Started

## Installation

```bash
# Using pip
pip install basic-open-agent-tools

# Using uv
uv add basic-open-agent-tools
```

## Core Concepts

**basic-open-agent-tools** is a toolkit designed specifically for AI agent frameworks, providing essential functions that agents can use to perform operations like file handling, text processing, and data manipulation.

Key features:
- **Function-first design**: Each function works as a standalone agent tool
- **Minimal dependencies**: Uses Python standard library where possible
- **Type safety**: Full type annotations for all functions
- **Comprehensive docstrings**: Help AI understand function purpose and usage

## Quick Start

### Using the Simplified API

The simplest way to load tools for your agent:

```python
import basic_open_agent_tools as boat

# Load tools by category
fs_tools = boat.load_all_filesystem_tools()    # 18 functions
text_tools = boat.load_all_text_tools()        # 10 functions
data_tools = boat.load_all_data_tools()        # 28 functions

# Merge for agent use (automatically deduplicates)
agent_tools = boat.merge_tool_lists(fs_tools, text_tools, data_tools)

# Use with your agent framework
# agent = YourAgentFramework(tools=agent_tools)
```

### Individual Function Imports

For more control, import specific functions:

```python
# Import only the functions you need
from basic_open_agent_tools.file_system.operations import read_file_to_string, write_file_from_string
from basic_open_agent_tools.text.processing import clean_whitespace, normalize_line_endings

# Use in your agent's tools list
tools = [read_file_to_string, write_file_from_string, clean_whitespace, normalize_line_endings]
```

### Direct Usage (Alternative)

While designed for agents, functions can also be used directly:

```python
from basic_open_agent_tools import file_system

# Read and write files
content = file_system.read_file_to_string("example.txt")
file_system.write_file_from_string("output.txt", "Hello World!")
```

## Available Tool Categories

- **File System Tools** (18 functions): File operations, directory management, path validation
- **Text Processing Tools** (10 functions): Text cleaning, case conversion, smart splitting
- **Data Tools** (28 functions): Data structures, JSON/CSV processing, validation

## Next Steps

- Check [Examples](examples.md) for detailed usage patterns and agent integration
- Read [Contributing](contributing.md) if you want to help develop the project
