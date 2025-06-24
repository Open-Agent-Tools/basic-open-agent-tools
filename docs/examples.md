# Examples

This document provides examples for both **AI agent integration** (primary use case) and direct usage patterns.

## AI Agent Integration Examples

### Google ADK File Operations Agent

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

# Configuration
load_dotenv()
logging.basicConfig(level=logging.ERROR)
warnings.filterwarnings("ignore")

# Agent instructions optimized for file operations
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

# Create specialized agent
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

# Usage example
response = file_ops_agent("Create a project structure with main.py, config.json, and a docs folder")
print(response)
```

### LangChain Tool Integration

```python
from langchain.tools import StructuredTool
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from basic_open_agent_tools.file_system.operations import (
    read_file_to_string, write_file_from_string, create_directory
)
from basic_open_agent_tools.file_system.info import file_exists

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
    StructuredTool.from_function(
        func=create_directory,
        name="create_directory",
        description="Create a directory and any necessary parent directories. Input should be a directory path string."
    ),
    StructuredTool.from_function(
        func=file_exists,
        name="file_exists",
        description="Check if a file exists. Input should be a file path string."
    ),
]

# Create LangChain agent with file tools
llm = OpenAI(temperature=0)
agent = initialize_agent(
    file_tools,
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Usage
result = agent.run("Create a new directory called 'project' and write a hello world script to main.py inside it")
```

### Custom Agent Framework Integration

```python
from basic_open_agent_tools.file_system.operations import *
from basic_open_agent_tools.file_system.info import *
from basic_open_agent_tools.file_system.tree import *

class FileSystemAgent:
    """Custom agent specialized in file system operations."""
    
    def __init__(self):
        # Map tool names to functions for easy access
        self.tools = {
            # File operations
            'read_file': read_file_to_string,
            'write_file': write_file_from_string,
            'append_file': append_to_file,
            'delete_file': delete_file,
            'copy_file': copy_file,
            'move_file': move_file,
            
            # Directory operations
            'create_directory': create_directory,
            'delete_directory': delete_directory,
            'list_directory': list_directory_contents,
            'directory_tree': generate_directory_tree,
            
            # Information tools
            'file_exists': file_exists,
            'directory_exists': directory_exists,
            'file_info': get_file_info,
            'file_size': get_file_size,
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
    
    def batch_operations(self, operations: list):
        """Execute multiple file operations in sequence."""
        results = []
        for op in operations:
            tool_name = op.pop('tool')
            result = self.execute_tool(tool_name, **op)
            results.append(result)
            if not result['success']:
                break  # Stop on first error
        return results

# Usage example
agent = FileSystemAgent()

# Single operation
result = agent.execute_tool('write_file', file_path='test.txt', content='Hello World!')
print(result)

# Batch operations
operations = [
    {'tool': 'create_directory', 'directory_path': 'project'},
    {'tool': 'write_file', 'file_path': 'project/main.py', 'content': 'print("Hello World!")'},
    {'tool': 'write_file', 'file_path': 'project/README.md', 'content': '# My Project'},
]
results = agent.batch_operations(operations)
```

## Direct Usage Examples

### Basic File Operations

### Reading and Writing Files

```python
from basic_open_agent_tools import file_system

# Write content to a file
content = "Hello, World!\nThis is a test file."
file_system.write_file_from_string("example.txt", content)

# Read content from a file
text = file_system.read_file_to_string("example.txt")
print(text)  # Output: Hello, World!\nThis is a test file.

# Append to an existing file
file_system.append_to_file("example.txt", "\nAppended line!")

# Read the updated content
updated_text = file_system.read_file_to_string("example.txt")
print(updated_text)
```

### File Information and Checks

```python
from basic_open_agent_tools import file_system

# Check if files exist
if file_system.file_exists("config.json"):
    print("Config file found!")
else:
    print("Config file missing")

# Get detailed file information
info = file_system.get_file_info("example.txt")
print(f"File size: {info['size']} bytes")
print(f"Modified: {info['modified']}")
print(f"Is readable: {info['readable']}")

# Check file size directly
size = file_system.get_file_size("example.txt")
print(f"File is {size} bytes")
```

## Directory Operations

### Creating and Managing Directories

```python
from basic_open_agent_tools import file_system

# Create a directory (including parent directories)
file_system.create_directory("projects/my-app/src")

# Check if directory exists
if file_system.directory_exists("projects"):
    print("Projects directory exists!")

# List directory contents
contents = file_system.list_directory_contents("projects")
print(f"Projects contains: {contents}")

# List contents including hidden files
all_contents = file_system.list_directory_contents(".", include_hidden=True)
print(f"Current directory (with hidden): {all_contents}")

# Check if directory is empty
if file_system.is_empty_directory("projects/my-app/src"):
    print("Source directory is empty")
```

### Directory Tree Visualization

```python
from basic_open_agent_tools import file_system

# Generate a directory tree with unlimited depth
tree = file_system.generate_directory_tree("projects")
print("Full project structure:")
print(tree)

# Generate a tree with limited depth
shallow_tree = file_system.generate_directory_tree(".", max_depth=2)
print("Current directory (2 levels deep):")
print(shallow_tree)

# Include hidden files in the tree
complete_tree = file_system.generate_directory_tree(".", max_depth=3, include_hidden=True)
print("Complete structure with hidden files:")
print(complete_tree)
```

### Recursive Directory Listing

```python
from basic_open_agent_tools import file_system

# Get all files and directories recursively  
all_items = file_system.list_all_directory_contents("projects")
print("All files and directories:")
for item in all_items:
    print(f"  {item}")

# Include hidden files in recursive listing
all_items_with_hidden = file_system.list_all_directory_contents("projects", include_hidden=True)
```

## File and Directory Management

### Moving and Copying

```python
from basic_open_agent_tools import file_system

# Copy a file
file_system.copy_file("example.txt", "backup/example_backup.txt")

# Move/rename a file
file_system.move_file("old_name.txt", "new_name.txt")

# Copy an entire directory
file_system.copy_file("source_dir", "backup_dir")

# Move a directory
file_system.move_file("temp_folder", "archive/old_temp")
```

### Cleanup Operations

```python
from basic_open_agent_tools import file_system

# Delete a single file
file_system.delete_file("temporary.txt")

# Delete an empty directory
file_system.delete_directory("empty_folder")

# Delete a directory and all its contents
file_system.delete_directory("old_project", recursive=True)
```

## Error Handling

### Handling File System Errors

```python
from basic_open_agent_tools import file_system
from basic_open_agent_tools.exceptions import FileSystemError

try:
    content = file_system.read_file_to_string("nonexistent.txt")
except FileSystemError as e:
    print(f"Error reading file: {e}")

try:
    file_system.write_file_from_string("/readonly/path/file.txt", "content")
except FileSystemError as e:
    print(f"Error writing file: {e}")

# Safe file operations with checks
file_path = "important.txt"
if file_system.file_exists(file_path):
    try:
        content = file_system.read_file_to_string(file_path)
        # Process content...
        file_system.write_file_from_string("processed.txt", content.upper())
    except FileSystemError as e:
        print(f"Failed to process file: {e}")
else:
    print(f"File {file_path} not found")
```

## Advanced Usage Patterns

### Configuration File Management

```python
from basic_open_agent_tools import file_system
import json

def load_config(config_path="config.json"):
    """Load configuration from JSON file."""
    if not file_system.file_exists(config_path):
        # Create default config
        default_config = {
            "debug": False,
            "port": 8080,
            "host": "localhost"
        }
        file_system.write_file_from_string(config_path, json.dumps(default_config, indent=2))
        return default_config
    
    config_text = file_system.read_file_to_string(config_path)
    return json.loads(config_text)

def save_config(config, config_path="config.json"):
    """Save configuration to JSON file."""
    config_text = json.dumps(config, indent=2)
    file_system.write_file_from_string(config_path, config_text)

# Usage
config = load_config()
config["debug"] = True
save_config(config)
```

### Log File Management

```python
from basic_open_agent_tools import file_system
from datetime import datetime

def log_message(message, log_file="app.log"):
    """Append a timestamped message to log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    # Create logs directory if it doesn't exist
    file_system.create_directory("logs")
    log_path = f"logs/{log_file}"
    
    file_system.append_to_file(log_path, log_entry)

def read_recent_logs(log_file="app.log", lines=50):
    """Read recent log entries."""
    log_path = f"logs/{log_file}"
    if not file_system.file_exists(log_path):
        return "No log file found"
    
    content = file_system.read_file_to_string(log_path)
    log_lines = content.split('\n')
    return '\n'.join(log_lines[-lines:])

# Usage
log_message("Application started")
log_message("Processing user request")
recent = read_recent_logs(lines=10)
print(recent)
```

### Project Structure Analysis

```python
from basic_open_agent_tools import file_system

def analyze_project_structure(project_path="."):
    """Analyze and report on project structure."""
    if not file_system.directory_exists(project_path):
        return "Project directory not found"
    
    # Get overview
    tree = file_system.generate_directory_tree(project_path, max_depth=3)
    all_files = file_system.list_all_directory_contents(project_path)
    
    # Count file types
    file_types = {}
    total_size = 0
    
    for file_path in all_files:
        if file_system.file_exists(file_path):
            # Get file extension
            ext = file_path.split('.')[-1] if '.' in file_path else 'no_extension'
            file_types[ext] = file_types.get(ext, 0) + 1
            
            # Add to total size
            total_size += file_system.get_file_size(file_path)
    
    # Generate report
    report = f"""Project Structure Analysis
{'=' * 30}

Directory Tree:
{tree}

File Statistics:
- Total files: {len(all_files)}
- Total size: {total_size:,} bytes

File Types:
"""
    for ext, count in sorted(file_types.items()):
        report += f"- .{ext}: {count} files\n"
    
    return report

# Usage
analysis = analyze_project_structure()
print(analysis)

# Save analysis to file
file_system.write_file_from_string("project_analysis.txt", analysis)
```

## Agent Tool Selection Strategies

### Minimal File Agent (Basic Operations)

```python
# For simple file operations agents
from basic_open_agent_tools.file_system.operations import (
    read_file_to_string, write_file_from_string, create_directory
)
from basic_open_agent_tools.file_system.info import file_exists, directory_exists

minimal_tools = [
    read_file_to_string, write_file_from_string, create_directory,
    file_exists, directory_exists
]
```

### Comprehensive File Agent (All Operations)

```python
# For full-featured file system agents
from basic_open_agent_tools.file_system.operations import (
    read_file_to_string, write_file_from_string, append_to_file,
    create_directory, delete_file, delete_directory, move_file, copy_file,
    list_directory_contents
)
from basic_open_agent_tools.file_system.info import (
    file_exists, directory_exists, get_file_info, get_file_size, is_empty_directory
)
from basic_open_agent_tools.file_system.tree import (
    generate_directory_tree, list_all_directory_contents
)

comprehensive_tools = [
    # All functions for maximum capability
    read_file_to_string, write_file_from_string, append_to_file,
    create_directory, delete_file, delete_directory, move_file, copy_file,
    list_directory_contents, file_exists, directory_exists, get_file_info,
    get_file_size, is_empty_directory, generate_directory_tree, list_all_directory_contents
]
```

### Specialized Read-Only Agent

```python
# For analysis and inspection agents (no modifications)
from basic_open_agent_tools.file_system.operations import (
    read_file_to_string, list_directory_contents
)
from basic_open_agent_tools.file_system.info import (
    file_exists, directory_exists, get_file_info, get_file_size
)
from basic_open_agent_tools.file_system.tree import generate_directory_tree

readonly_tools = [
    read_file_to_string, list_directory_contents, file_exists,
    directory_exists, get_file_info, get_file_size, generate_directory_tree
]
```

## Import Patterns for Different Use Cases

### Agent Framework Integration (Recommended)

```python
# Individual function imports for agent tools
from basic_open_agent_tools.file_system.operations import read_file_to_string, write_file_from_string
from basic_open_agent_tools.file_system.info import file_exists

# Use directly in agent framework
tools = [read_file_to_string, write_file_from_string, file_exists]
```

### Direct Developer Usage

```python
# Module import for scripting and direct usage
from basic_open_agent_tools import file_system

# Use module methods
content = file_system.read_file_to_string("example.txt")
file_system.write_file_from_string("output.txt", content.upper())
```

### Mixed Approach

```python
# Combine both patterns as needed
from basic_open_agent_tools import file_system
from basic_open_agent_tools.file_system.operations import read_file_to_string

# Use module for most operations
file_system.create_directory("new_folder")

# Use specific imports for agent tools or specialized functions
agent_tools = [read_file_to_string]
```