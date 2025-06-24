# Getting Started

## Installation

Install using pip:

```bash
pip install basic-open-agent-tools
```

Or using uv:

```bash
uv add basic-open-agent-tools
```

## Package Purpose

**basic-open-agent-tools** is designed as a **toolkit for AI agent frameworks**, providing essential tool functions that agents can use to perform file system operations. Rather than being used directly by developers, these functions are typically imported as **tools** for AI agents.

## Quick Start: Agent Integration

### Creating a File Operations Agent

```python
import logging
import warnings
from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from basic_open_agent_tools.file_system.operations import (
    append_to_file, copy_file, create_directory, delete_directory, delete_file,
    list_directory_contents, move_file, read_file_to_string, write_file_from_string,
)
from basic_open_agent_tools.file_system.info import (
    directory_exists, file_exists, get_file_info, get_file_size, is_empty_directory,
)

# Load environment and configure
load_dotenv()
MODEL_NAME = "anthropic/claude-3-5-haiku-20241022"

# Define agent instructions
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

# Create specialized file operations agent
file_ops_agent = Agent(
    model=LiteLlm(model=MODEL_NAME),
    name="FileOps",
    instruction=agent_instruction,
    description="Specialized file and directory operations sub-agent for the Python developer.",
    tools=[
        append_to_file, copy_file, create_directory, delete_directory, delete_file,
        directory_exists, file_exists, get_file_info, get_file_size, is_empty_directory,
        list_directory_contents, move_file, read_file_to_string, write_file_from_string,
    ],
)
```

### Direct Usage (Alternative)

While designed for agents, functions can also be used directly:

```python
from basic_open_agent_tools import file_system

# Read and write files
content = file_system.read_file_to_string("example.txt")
file_system.write_file_from_string("output.txt", "Hello World!")

# Check file existence
if file_system.file_exists("myfile.txt"):
    print("File exists!")

# Work with directories
file_system.create_directory("new_folder")
contents = file_system.list_directory_contents(".")
```

## Import Patterns for Agent Tools

### Individual Function Imports (Recommended for Agents)

```python
# Import specific functions to use as agent tools
from basic_open_agent_tools.file_system.operations import (
    read_file_to_string, write_file_from_string, append_to_file,
    create_directory, delete_file, move_file, copy_file
)
from basic_open_agent_tools.file_system.info import (
    file_exists, directory_exists, get_file_info, get_file_size
)
from basic_open_agent_tools.file_system.tree import (
    generate_directory_tree, list_all_directory_contents
)

# Use in agent tools list
tools = [read_file_to_string, write_file_from_string, file_exists, ...]
```

### Module Import (For Direct Usage)

```python
# Import module for direct developer usage
from basic_open_agent_tools import file_system

# Use module functions
file_system.read_file_to_string("file.txt")
```

## Agent Framework Integration

This toolkit is designed to work with various AI agent frameworks:

- **Google ADK** - As shown in the example above
- **LangChain** - Functions can be wrapped as LangChain tools
- **Custom Agents** - Direct function integration
- **MCP Servers** - Can be adapted for Model Context Protocol

## Next Steps

- Check out the [API Reference](api-reference.md) for complete function documentation
- See [Examples](examples.md) for agent integration patterns and usage scenarios
- Read [Contributing](contributing.md) if you want to help develop the project