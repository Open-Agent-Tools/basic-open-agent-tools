# Frequently Asked Questions (FAQ)

## General Questions

### What is basic-open-agent-tools?

**basic-open-agent-tools** is an open-source Python toolkit designed specifically for AI agent frameworks. It provides 166 essential functions across 12 modules for common operations like file handling, text processing, data manipulation, system operations, and more.

### Who should use this toolkit?

- **AI Agent Developers**: Building agents with frameworks like Google ADK, LangChain, or Strands
- **Automation Engineers**: Creating automated workflows and scripts
- **Python Developers**: Needing reliable utility functions with agent-friendly signatures
- **Research Teams**: Building AI systems that need local file and data operations

### How is this different from other Python libraries?

**Key Differences:**
- **Agent-Optimized**: Function signatures designed to prevent "signature too complex" errors
- **Minimal Dependencies**: Core functionality uses only Python standard library
- **AI-Friendly**: Comprehensive docstrings and structured return values for LLM understanding
- **Framework Agnostic**: Works with Google ADK, LangChain, Strands, and custom frameworks

## Installation & Setup

### How do I install basic-open-agent-tools?

```bash
# Basic installation (core functionality)
pip install basic-open-agent-tools

# With all optional features
pip install basic-open-agent-tools[all]

# Specific feature groups
pip install basic-open-agent-tools[system]  # System monitoring
pip install basic-open-agent-tools[pdf]     # PDF operations
```

### What Python versions are supported?

- **Supported**: Python 3.9, 3.10, 3.11, 3.12
- **Not Supported**: Python 3.8 and below (as of v0.9.1)

### Do I need additional dependencies?

**Core Functions**: No additional dependencies required

**Optional Dependencies**:
- `psutil` - System monitoring and process management (`[system]` group)
- `PyPDF2` + `reportlab` - PDF operations (`[pdf]` group)

### How do I upgrade from an older version?

```bash
# Upgrade to latest version
pip install --upgrade basic-open-agent-tools[all]

# Check current version
python -c "import basic_open_agent_tools; print(basic_open_agent_tools.__version__)"
```

See [CHANGELOG.md](../CHANGELOG.md) for version-specific migration notes.

## Usage Questions

### How do I load tools for my agent?

**Option 1: Load all tools at once**
```python
import basic_open_agent_tools as boat
all_tools = boat.load_all_tools()  # All 166 functions
```

**Option 2: Load by category**
```python
fs_tools = boat.load_all_filesystem_tools()    # 18 functions
text_tools = boat.load_all_text_tools()        # 10 functions
data_tools = boat.load_all_data_tools()        # 23 functions
```

**Option 3: Load and merge specific categories**
```python
selected_tools = boat.merge_tool_lists(
    boat.load_all_filesystem_tools(),
    boat.load_all_network_tools(),
    boat.load_all_crypto_tools()
)
```

### Can I use functions directly without an agent framework?

**Yes!** All functions work as standalone Python functions:

```python
from basic_open_agent_tools.file_system import read_file_to_string
from basic_open_agent_tools.text import clean_whitespace

# Direct function usage
content = read_file_to_string("/path/to/file.txt")
clean_text = clean_whitespace(content["file_content"])
```

### How do I handle errors?

All functions use consistent error handling:

```python
from basic_open_agent_tools.exceptions import BasicAgentToolsError

try:
    result = some_function(parameters)
    if result.get("success", False):
        print("Operation succeeded")
    else:
        print(f"Operation failed: {result.get('error_message')}")
except BasicAgentToolsError as e:
    print(f"Tool error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### How does the skip_confirm parameter work?

**The confirmation system adapts to your execution context with 3 modes:**

**1. Bypass Mode** (`skip_confirm=True` or `BYPASS_TOOL_CONSENT=true` env var)
```python
# Direct bypass
result = boat.file_system.write_file_from_string(
    file_path="/tmp/file.txt",
    content="Data",
    skip_confirm=True  # Proceeds immediately
)

# Or use environment variable for CI/CD
import os
os.environ['BYPASS_TOOL_CONSENT'] = 'true'
# All confirmations bypassed automatically
```

**2. Interactive Mode** (Terminal with `skip_confirm=False`)
```python
# In a terminal, you'll be prompted:
result = boat.file_system.write_file_from_string(
    file_path="/tmp/file.txt",
    content="Data",
    skip_confirm=False
)
# ⚠️  WARNING: overwrite existing file
# Target: /tmp/file.txt
# Preview: 1024 bytes
#
# Proceed? (y/n):
```

**3. Agent Mode** (Non-TTY with `skip_confirm=False`)
```python
# Agent receives instructive error to ask user
from basic_open_agent_tools.exceptions import BasicAgentToolsError

try:
    result = boat.file_system.write_file_from_string(
        file_path="/tmp/file.txt",
        content="Data",
        skip_confirm=False
    )
except BasicAgentToolsError as e:
    # Error says: "CONFIRMATION_REQUIRED: overwrite existing file"
    # Agent should ask user, then retry with skip_confirm=True
    print(e)
```

**Best practice for agents**: Always start with `skip_confirm=False`, handle `CONFIRMATION_REQUIRED` errors by asking the user, then retry with `skip_confirm=True` if approved.

### What's the difference between modules?

Each module serves a specific purpose:

| Module | Purpose | Example Functions |
|--------|---------|-------------------|
| **file_system** | File/directory operations | `read_file_to_string`, `create_directory` |
| **text** | Text processing | `clean_whitespace`, `to_snake_case` |
| **data** | JSON/CSV/config files | `read_json_file`, `write_csv_file` |
| **datetime** | Date/time operations | `get_current_datetime`, `add_days` |
| **network** | HTTP/DNS operations | `http_request`, `resolve_hostname` |
| **system** | System info/processes | `execute_shell_command`, `get_cpu_info` |
| **crypto** | Hashing/encoding | `hash_string_sha256`, `base64_encode` |
| **pdf** | PDF operations | `extract_text_from_pdf`, `merge_pdfs` |
| **archive** | Compression | `create_zip`, `compress_file_gzip` |
| **logging** | Structured logging | `log_info`, `setup_rotating_log` |
| **monitoring** | Performance/health | `monitor_function_performance` |
| **utilities** | Debugging/timing | `sleep_seconds`, `inspect_function_signature` |

## Agent Framework Integration

### How do I use this with Google ADK?

```python
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
import basic_open_agent_tools as boat

# Load tools
tools = boat.load_all_tools()

# Create agent
agent = Agent(
    model=LiteLlm(model="anthropic/claude-3-5-haiku-20241022"),
    name="MyAgent",
    instruction="You are a helpful assistant...",
    tools=tools
)
```

### How do I use this with LangChain?

```python
from langchain.tools import StructuredTool
from basic_open_agent_tools.file_system import read_file_to_string

# Wrap individual functions
file_reader = StructuredTool.from_function(
    func=read_file_to_string,
    name="read_file",
    description="Read file content"
)

# Or load all tools and wrap them
import basic_open_agent_tools as boat
tools = boat.load_all_tools()
langchain_tools = [StructuredTool.from_function(func=tool) for tool in tools]
```

### How do I use this with Strands Agents?

**Automatic compatibility** - all functions include `@strands_tool` decorators:

```python
from basic_open_agent_tools.file_system import read_file_to_string
# Function is automatically Strands-compatible
```

### Can I use this with custom agent frameworks?

**Yes!** Functions are designed to be framework-agnostic:

```python
# Functions return structured dictionaries
result = some_function(parameters)

# Extract data for your framework
if result["success"]:
    data = result["result"]
    # Use data in your framework
```

## Technical Questions

### Why do functions return dictionaries instead of simple values?

**Agent frameworks need structured data:**
- **Status Information**: Success/failure indicators
- **Metadata**: File sizes, timestamps, operation details
- **Error Details**: Specific error messages and types
- **Context**: Additional information for LLM reasoning

### What does "agent-friendly signatures" mean?

**Designed to prevent LLM integration issues:**
- **Simple Types Only**: `str`, `int`, `float`, `bool`, `List`, `Dict`
- **No Default Parameters**: Explicit parameter specification required
- **Typed Lists**: `List[str]` instead of bare `list`
- **No Union Types**: Avoid complex type specifications
- **JSON Serializable**: All types work with JSON serialization

### Why are there no default parameters?

**LLM frameworks handle defaults poorly:**
- Default values can confuse AI function calling
- Explicit parameters make function behavior clearer
- Reduces "signature too complex" errors
- Makes function calls more predictable

### How do I handle file paths on different operating systems?

**All functions handle cross-platform paths:**
- Use forward slashes `/` even on Windows
- Functions automatically convert to OS-appropriate format
- Absolute paths recommended for clarity
- Path validation built into file system functions

### Are functions thread-safe?

**Generally yes, but considerations:**
- **File Operations**: Thread-safe for different files, coordinate for same file
- **System Operations**: Thread-safe for read operations
- **Network Operations**: Thread-safe, no shared state
- **Logging**: Thread-safe with proper configuration

## Performance Questions

### How performant are the functions?

**Optimized for agent use cases:**
- **File Operations**: Efficient for typical file sizes (< 100MB)
- **Text Processing**: Fast for typical text lengths (< 1MB)
- **Network Operations**: Configurable timeouts, connection pooling
- **System Operations**: Minimal overhead, cached where appropriate

### Can I use this for large-scale operations?

**Recommendations by module:**
- **File System**: Good for < 10GB files, use chunking for larger
- **Data Processing**: Efficient for < 100MB JSON/CSV files
- **PDF Operations**: Optimized for < 100MB PDF files
- **Archive Operations**: Handles large archives efficiently
- **Network**: Suitable for typical API usage patterns

### How do I optimize memory usage?

**Best practices:**
- Process large files in chunks using appropriate functions
- Use streaming operations where available
- Clean up temporary files created by operations
- Monitor memory usage in long-running agents

## Troubleshooting

### I'm getting "signature too complex" errors

**This usually means:**
1. Using an older version - upgrade to latest
2. Function signature incompatible with your framework
3. Framework-specific configuration needed

**Solutions:**
```python
# Check function signature
from basic_open_agent_tools.utilities import inspect_function_signature
result = inspect_function_signature("function_name")
print(result["signature_details"])
```

### Functions are returning error dictionaries

**Common causes:**
1. **File Not Found**: Check file paths are absolute and exist
2. **Permission Denied**: Ensure proper file/directory permissions
3. **Invalid Parameters**: Check parameter types and ranges
4. **Missing Dependencies**: Install optional dependencies if needed

**Debugging:**
```python
result = some_function(parameters)
if not result.get("success", False):
    print("Error:", result.get("error_message"))
    print("Error Type:", result.get("error_type"))
```

### Import errors or missing modules

**Check installation:**
```bash
pip list | grep basic-open-agent-tools
pip install --upgrade basic-open-agent-tools[all]
```

**Check Python version:**
```bash
python --version  # Should be 3.9+
```

### Performance is slower than expected

**Common solutions:**
1. **File Operations**: Use appropriate functions for file size
2. **Network Operations**: Adjust timeout parameters
3. **System Operations**: Check system resource usage
4. **Logging**: Configure appropriate log levels

## Development Questions

### How do I contribute to the project?

See [Contributing Guide](contributing.md) for:
- Development environment setup
- Code style requirements
- Testing procedures
- Pull request process

### Can I request new functions or modules?

**Yes!** Please:
1. Check existing functions first ([API Reference](api-reference.md))
2. Open an issue describing the use case
3. Follow the agent-friendly design principles
4. Consider contributing the implementation

### How do I report bugs?

**Bug reports should include:**
1. **Version**: `basic_open_agent_tools.__version__`
2. **Python Version**: `python --version`
3. **Operating System**: Windows/macOS/Linux
4. **Agent Framework**: Google ADK/LangChain/Strands/Custom
5. **Code Example**: Minimal reproduction case
6. **Error Messages**: Full stack trace if available

### Is there a roadmap for future features?

Check the project's:
- **GitHub Issues**: Feature requests and planned improvements
- **TODO Files**: Module-specific development plans
- **CHANGELOG**: Recent additions and version history

## Security Questions

### Is this safe to use in agents?

**Security considerations:**
- **File Operations**: Include path validation and traversal protection
- **Shell Commands**: Limited to safe operations, no arbitrary code execution
- **Network Operations**: SSL verification, timeout controls
- **System Operations**: Read-only focus, no privileged operations

### What about credential handling?

**Not included by design:**
- No credential storage or management functions
- No encryption/decryption operations
- Use specialized libraries for security-critical operations
- See [Security Policy](../SECURITY.md) for guidelines

### Can agents access sensitive system resources?

**Limited by design:**
- **System Tools**: Read-only operations preferred
- **File System**: Standard file permissions apply
- **Network**: No port scanning or bulk operations
- **Process Management**: Information gathering only

## Getting Help

### Where can I find more documentation?

- **[Getting Started](getting-started.md)** - Installation and basic usage
- **[API Reference](api-reference.md)** - Complete function reference
- **[Examples](examples.md)** - Usage patterns and integration examples
- **[Contributing](contributing.md)** - Development and contribution guide
- **[Glossary](glossary.md)** - Agent framework terminology

### How do I get support?

1. **Check Documentation**: Start with relevant module README
2. **Search Issues**: Look for similar problems on GitHub
3. **Create Issue**: Provide detailed information and reproduction steps
4. **Community**: Engage with other users and maintainers

### Are there examples for my specific use case?

**Common patterns in [Examples](examples.md):**
- Agent integration with major frameworks
- File processing workflows
- Data analysis pipelines
- System monitoring setups
- Network operation patterns

If your use case isn't covered, please request an example in the issues!