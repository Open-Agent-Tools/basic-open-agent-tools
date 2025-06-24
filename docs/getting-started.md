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

## Quick Start

### File System Operations

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

# Generate directory trees
tree = file_system.generate_directory_tree(".", max_depth=2)
print(tree)
```

### Available Import Patterns

```python
# Main module import
from basic_open_agent_tools import file_system

# Submodule imports
from basic_open_agent_tools.file_system.operations import read_file_to_string
from basic_open_agent_tools.file_system.info import get_file_info
from basic_open_agent_tools.file_system.tree import generate_directory_tree
from basic_open_agent_tools.file_system.validation import validate_path
```

## Next Steps

- Check out the [API Reference](api-reference.md) for complete function documentation
- See [Examples](examples.md) for more detailed usage scenarios
- Read [Contributing](contributing.md) if you want to help develop the project