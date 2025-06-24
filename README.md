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
from basic_open_agent_tools import file_system

# File operations
content = file_system.read_file_to_string("file.txt")
file_system.write_file_from_string("output.txt", "Hello!")

# Directory operations  
files = file_system.list_directory_contents("/path/to/dir")
file_system.create_directory("new_dir")

# Directory tree visualization
tree = file_system.generate_directory_tree(".", max_depth=2)
print(tree)
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



