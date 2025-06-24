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
from basic_open_agent_tools.file_system.operations import (
    append_to_file, copy_file, create_directory, delete_directory, delete_file,
    list_directory_contents, move_file, read_file_to_string, write_file_from_string,
)
from basic_open_agent_tools.file_system.info import (
    directory_exists, file_exists, get_file_info, get_file_size, is_empty_directory,
)

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
    tools=[
        append_to_file, copy_file, create_directory, delete_directory, delete_file,
        directory_exists, file_exists, get_file_info, get_file_size, is_empty_directory,
        list_directory_contents, move_file, read_file_to_string, write_file_from_string,
    ],
)


```

## Documentation

- **[Getting Started](docs/getting-started.md)** - Installation and quick start guide
- **[API Reference](docs/api-reference.md)** - Complete function documentation
- **[Examples](docs/examples.md)** - Detailed usage examples and patterns
- **[Contributing](docs/contributing.md)** - Development setup and guidelines

## Current Features

### File System Tools
- File operations (read, write, append, delete, copy, move)
- Directory operations (create, list, delete, tree visualization)
- File information and existence checking
- Path validation and error handling

### Planned Modules
- HTTP request utilities
- Text processing and manipulation
- Data parsing and conversion
- System information and process management
- Cryptographic utilities
- Common helper functions

## Contributing

We welcome contributions! Please see our [Contributing Guide](docs/contributing.md) for development setup, coding standards, and pull request process.



