# Examples

This document provides examples for both **AI agent integration** (primary use case) and direct usage patterns.

## AI Agent Integration

### Using the Simplified API

The simplest way to integrate with agent frameworks:

```python
import basic_open_agent_tools as boat
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

# Load all tools by category
fs_tools = boat.load_all_filesystem_tools()
text_tools = boat.load_all_text_tools()
data_tools = boat.load_all_data_tools()

# Merge for agent use (automatically deduplicates)
agent_tools = boat.merge_tool_lists(fs_tools, text_tools, data_tools)

# Create agent with all tools
agent = Agent(
    model=LiteLlm(model="anthropic/claude-3-5-haiku-20241022"),
    name="FileOps",
    instruction="You are a file operations assistant...",
    tools=agent_tools,
)
```

### Framework-Specific Examples

#### Google ADK

```python
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from basic_open_agent_tools.file_system.operations import (
    read_file_to_string, write_file_from_string, create_directory
)
from basic_open_agent_tools.file_system.info import file_exists

# Create specialized agent
file_ops_agent = Agent(
    model=LiteLlm(model="anthropic/claude-3-5-haiku-20241022"),
    name="FileOps",
    instruction="You are a file operations assistant...",
    tools=[read_file_to_string, write_file_from_string, create_directory, file_exists],
)

# Usage example
response = file_ops_agent("Create a file named example.txt with 'Hello World' content")
```

#### LangChain

```python
from langchain.tools import StructuredTool
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from basic_open_agent_tools.file_system.operations import read_file_to_string, write_file_from_string

# Wrap functions as LangChain tools
file_tools = [
    StructuredTool.from_function(
        func=read_file_to_string,
        name="read_file",
        description="Read the contents of a text file. Input should be a file path string."
    ),
    StructuredTool.from_function(
        func=write_file_from_string,
        name="write_file", 
        description="Write content to a text file. Inputs: file_path (string) and content (string)."
    ),
]

# Create LangChain agent with file tools
agent = initialize_agent(
    file_tools,
    OpenAI(temperature=0),
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
```

#### Custom Agent Framework

```python
class FileSystemAgent:
    """Custom agent specialized in file system operations."""

    def __init__(self):
        from basic_open_agent_tools.file_system.operations import (
            read_file_to_string, write_file_from_string, create_directory
        )
        from basic_open_agent_tools.file_system.info import file_exists

        # Map tool names to functions
        self.tools = {
            'read_file': read_file_to_string,
            'write_file': write_file_from_string,
            'create_directory': create_directory,
            'file_exists': file_exists,
        }

    def execute_tool(self, tool_name: str, **kwargs):
        """Execute a file system tool with given parameters."""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        try:
            result = self.tools[tool_name](**kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Usage example
agent = FileSystemAgent()
result = agent.execute_tool('write_file', file_path='test.txt', content='Hello World!')
```

## Tool Selection Strategies

### By Function Type

#### Minimal File Agent (Basic Operations)

```python
# For simple file operations agents
from basic_open_agent_tools.file_system.operations import read_file_to_string, write_file_from_string
from basic_open_agent_tools.file_system.info import file_exists

minimal_tools = [read_file_to_string, write_file_from_string, file_exists]
```

#### Read-Only Agent (Analysis and Inspection)

```python
# For analysis and inspection agents (no modifications)
from basic_open_agent_tools.file_system.operations import read_file_to_string, list_directory_contents
from basic_open_agent_tools.file_system.info import file_exists, get_file_info
from basic_open_agent_tools.file_system.tree import generate_directory_tree

readonly_tools = [
    read_file_to_string, list_directory_contents, file_exists,
    get_file_info, generate_directory_tree
]
```

### By Module

#### File System Tools

```python
import basic_open_agent_tools as boat

# Get all file system tools
fs_tools = boat.load_all_filesystem_tools()

# Or import specific modules
from basic_open_agent_tools.file_system.operations import (
    read_file_to_string, write_file_from_string, append_to_file,
    create_directory, delete_file, move_file, copy_file
)
```

#### Text Processing Tools

```python
import basic_open_agent_tools as boat

# Get all text processing tools
text_tools = boat.load_all_text_tools()

# Or import specific functions
from basic_open_agent_tools.text.processing import (
    clean_whitespace, normalize_line_endings, strip_html_tags,
    to_snake_case, to_camel_case
)
```

#### Data Tools

```python
import basic_open_agent_tools as boat

# Get all data tools
data_tools = boat.load_all_data_tools()

# Or import specific functions
from basic_open_agent_tools.data.json_tools import (
    parse_json, format_json, validate_json_schema
)
from basic_open_agent_tools.data.csv_tools import (
    read_csv_to_dicts, write_dicts_to_csv
)
```

## Direct Usage Examples

### File System Operations

```python
from basic_open_agent_tools import file_system

# Read and write files
content = file_system.read_file_to_string("example.txt")
file_system.write_file_from_string("output.txt", "Hello World!")
file_system.append_to_file("log.txt", "New log entry")

# Directory operations
file_system.create_directory("projects/my-app/src")
contents = file_system.list_directory_contents("projects")
tree = file_system.generate_directory_tree("projects", max_depth=2)

# File management
file_system.copy_file("example.txt", "backup/example_backup.txt")
file_system.move_file("old_name.txt", "new_name.txt")
file_system.delete_file("temporary.txt")
```

### Text Processing

```python
from basic_open_agent_tools.text import processing

# Clean and normalize text
clean_text = processing.clean_whitespace("Text  with   extra    spaces")
normalized = processing.normalize_line_endings("Text\r\nwith\rmixed\nline endings")
plain_text = processing.strip_html_tags("<p>HTML <b>tags</b> removed</p>")

# Case conversion
snake = processing.to_snake_case("convertThisString")  # convert_this_string
camel = processing.to_camel_case("convert_this_string")  # convertThisString
title = processing.to_title_case("convert this string")  # Convert This String

# Text splitting
sentences = processing.extract_sentences("Hello there! How are you? I'm fine.")
```

### Data Processing

```python
from basic_open_agent_tools.data import json_tools, csv_tools, structures

# JSON operations
json_str = json_tools.format_json({"name": "test", "values": [1, 2, 3]})
parsed = json_tools.parse_json('{"name": "test", "values": [1, 2, 3]}')
is_valid = json_tools.validate_json_schema(parsed, {"type": "object", "required": ["name"]})

# CSV operations
data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
csv_tools.write_dicts_to_csv("people.csv", data)
loaded_data = csv_tools.read_csv_to_dicts("people.csv")

# Data structure operations
flat_dict = structures.flatten_dict({"user": {"name": "Alice", "details": {"age": 30}}})
nested = structures.unflatten_dict({"user.name": "Alice", "user.details.age": 30})
```

## Error Handling

```python
from basic_open_agent_tools import file_system
from basic_open_agent_tools.exceptions import FileSystemError

try:
    content = file_system.read_file_to_string("nonexistent.txt")
except FileSystemError as e:
    print(f"Error reading file: {e}")

# Safe file operations with checks
file_path = "important.txt"
if file_system.file_exists(file_path):
    try:
        content = file_system.read_file_to_string(file_path)
        # Process content...
    except FileSystemError as e:
        print(f"Failed to process file: {e}")
```

## Advanced Usage Patterns

### Configuration File Management

```python
from basic_open_agent_tools import file_system
import json

def load_config(config_path="config.json"):
    """Load configuration from JSON file with defaults."""
    if not file_system.file_exists(config_path):
        default_config = {"debug": False, "port": 8080}
        file_system.write_file_from_string(
            config_path, 
            json.dumps(default_config, indent=2)
        )
        return default_config

    return json.loads(file_system.read_file_to_string(config_path))

# Usage
config = load_config()
config["debug"] = True
file_system.write_file_from_string(
    "config.json", 
    json.dumps(config, indent=2)
)
```

### Project Analysis

```python
from basic_open_agent_tools import file_system

def analyze_project(project_path="."):
    """Generate a simple project analysis report."""
    tree = file_system.generate_directory_tree(project_path, max_depth=2)
    all_files = file_system.list_all_directory_contents(project_path)

    # Count file types
    file_types = {}
    for file_path in all_files:
        if file_system.file_exists(file_path):
            ext = file_path.split('.')[-1] if '.' in file_path else 'no_extension'
            file_types[ext] = file_types.get(ext, 0) + 1

    return {
        "tree": tree,
        "file_count": len(all_files),
        "file_types": file_types
    }

# Usage
analysis = analyze_project()
print(f"Project has {analysis['file_count']} files")
```
