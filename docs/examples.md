# Examples

## Basic File Operations

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

## Integration with Other Tools

### Using with Different Import Patterns

```python
# Pattern 1: Main module import (recommended)
from basic_open_agent_tools import file_system
file_system.read_file_to_string("example.txt")

# Pattern 2: Submodule imports for specific functions
from basic_open_agent_tools.file_system.operations import read_file_to_string, write_file_from_string
from basic_open_agent_tools.file_system.info import file_exists, get_file_info
from basic_open_agent_tools.file_system.tree import generate_directory_tree

content = read_file_to_string("example.txt")
info = get_file_info("example.txt")
tree = generate_directory_tree(".")

# Pattern 3: Mixed imports
from basic_open_agent_tools import file_system
from basic_open_agent_tools.file_system.validation import validate_path

# Use main module for most operations
file_system.create_directory("new_folder")

# Use specific imports for specialized functions
path = validate_path("./some/path", "custom operation")
```