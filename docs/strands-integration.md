# AWS Strands Integration Guide

This guide covers how to use basic-open-agent-tools with the AWS Strands framework to create powerful AI agents with comprehensive local operations capabilities.

## Overview

basic-open-agent-tools provides native integration with AWS Strands through:

- **@strands_tool decorators**: All functions are decorated for seamless Strands compatibility
- **Agent-friendly signatures**: JSON-serializable types and Google ADK compliance
- **A2A protocol compatibility**: Works with Agent-to-Agent communication
- **Comprehensive tool loading**: Helper functions for easy integration

## Installation

### Basic Installation

```bash
pip install basic-open-agent-tools[strands]
```

This installs:
- `basic-open-agent-tools` - The core toolkit
- `strands` - AWS Strands framework
- `anthropic` - Anthropic API client
- `python-dotenv` - Environment variable management

### Development Installation

```bash
pip install basic-open-agent-tools[dev]
```

This includes all Strands dependencies plus testing and development tools.

## Quick Start

### 1. Set Up Environment

Create a `.env` file:

```bash
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 2. Create Your First Strands Agent

```python
import os
from strands import Agent
from strands.models.anthropic import AnthropicModel
from dotenv import load_dotenv

import basic_open_agent_tools as boat

# Load environment variables
load_dotenv()

# Create Anthropic model
model = AnthropicModel(
    client_args={
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
    },
    model_id="claude-sonnet-4-20250514",
    max_tokens=1024,
    params={"temperature": 0.7},
)

# Load tools from basic-open-agent-tools
agent_tools = boat.merge_tool_lists(
    boat.load_all_filesystem_tools(),    # File operations
    boat.load_all_text_tools(),         # Text processing
    boat.load_all_data_tools()[:10],    # Data processing (limited)
    boat.load_all_network_tools()       # HTTP requests
)

# Create Strands agent
agent = Agent(
    model=model,
    name="Basic Tools Agent",
    description="Agent with comprehensive local operations capabilities",
    system_prompt=(
        "You are a helpful agent with access to file operations, "
        "text processing, data handling, and network capabilities. "
        "Use tools appropriately to assist users."
    ),
    tools=agent_tools
)

# Test the agent
response = agent("Hello! What capabilities do you have?")
print(response)
```

## Tool Loading Patterns

### Load All Tools

```python
import basic_open_agent_tools as boat

# Load all 150+ tools at once
all_tools = boat.load_all_tools()
agent = Agent(model=model, tools=all_tools)
```

### Load by Category

```python
# Load specific categories
file_tools = boat.load_all_filesystem_tools()      # 18 functions
text_tools = boat.load_all_text_tools()           # 10 functions
data_tools = boat.load_all_data_tools()           # 23 functions
datetime_tools = boat.load_all_datetime_tools()   # 40 functions
crypto_tools = boat.load_all_crypto_tools()       # 14 functions
network_tools = boat.load_all_network_tools()     # 4 functions
utilities_tools = boat.load_all_utilities_tools() # 8 functions

# System tools require optional dependency
try:
    system_tools = boat.load_all_system_tools()   # 19 functions
except ImportError:
    print("Install with: pip install basic-open-agent-tools[system]")
    system_tools = []
```

### Merge Selected Tools

```python
# Create custom tool combinations
custom_tools = boat.merge_tool_lists(
    file_tools,
    text_tools[:5],      # Limit to first 5 text tools
    data_tools[:10],     # Limit to first 10 data tools
    network_tools
)

agent = Agent(model=model, tools=custom_tools)
```

## Specialized Agent Examples

### File Operations Agent

```python
file_agent = Agent(
    model=model,
    name="FileOps Specialist",
    description="Expert in file and directory operations",
    system_prompt=(
        "You are a file operations specialist. You can read, write, "
        "create, delete, move, copy files and work with directories efficiently."
    ),
    tools=boat.load_all_filesystem_tools()
)
```

### Data Processing Agent

```python
data_agent = Agent(
    model=model,
    name="DataOps Specialist",
    description="Expert in data processing and transformation",
    system_prompt=(
        "You specialize in processing JSON, CSV, YAML and other data formats. "
        "You can validate, transform, and manipulate data efficiently."
    ),
    tools=boat.merge_tool_lists(
        boat.load_all_data_tools(),
        boat.load_all_text_tools()  # For data cleaning
    )
)
```

### Web Development Agent

```python
web_agent = Agent(
    model=model,
    name="Web Development Assistant",
    description="Assistant for web development tasks",
    system_prompt=(
        "You help with web development tasks including file management, "
        "text processing, data handling, and network operations."
    ),
    tools=boat.merge_tool_lists(
        boat.load_all_filesystem_tools(),
        boat.load_all_text_tools(),
        boat.load_all_data_tools(),
        boat.load_all_network_tools(),
        boat.load_all_crypto_tools()[:5]  # For tokens, hashes
    )
)
```

## A2A Protocol Integration

basic-open-agent-tools is fully compatible with AWS Strands A2A (Agent-to-Agent) protocol:

### Agent Card Example

```python
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

# Define agent capabilities
capabilities = AgentCapabilities(
    streaming=True,
    pushNotifications=True
)

# Define skills based on toolkit
skills = [
    AgentSkill(
        id="file_operations",
        name="File Operations",
        description="Complete file and directory management",
        tags=["file", "filesystem", "io"],
        examples=[
            "Read the contents of config.json",
            "Create a backup copy of important files",
            "Organize files into directories"
        ]
    ),
    AgentSkill(
        id="data_processing",
        name="Data Processing",
        description="JSON, CSV, YAML data handling",
        tags=["data", "json", "csv", "yaml"],
        examples=[
            "Parse and validate JSON configuration",
            "Convert CSV data to JSON format",
            "Extract specific fields from data files"
        ]
    )
]

# Create agent card
card = AgentCard(
    name="Basic Tools Agent",
    description="Comprehensive local operations agent",
    url="http://localhost:8087/",
    version="1.0.0",
    capabilities=capabilities,
    skills=skills
)
```

### Context Isolation

Tools work seamlessly with A2A context isolation:

```python
# Tools maintain state independence across contexts
from basic_open_agent_tools.crypto import generate_uuid4
from basic_open_agent_tools.text import clean_whitespace

# Each context gets independent results
context_1_uuid = generate_uuid4()  # Unique per context
context_2_uuid = generate_uuid4()  # Different UUID

# Text processing works independently
result1 = clean_whitespace("  text for context 1  ")
result2 = clean_whitespace("  text for context 2  ")
```

## Testing Your Integration

### Basic Compatibility Test

```python
import basic_open_agent_tools as boat
from strands import Agent
from strands.models.anthropic import AnthropicModel

# Test tool loading
tools = boat.load_all_filesystem_tools()[:5]  # Limit for testing
print(f"Loaded {len(tools)} tools")

# Test agent creation (requires API key)
model = AnthropicModel(
    client_args={"api_key": "your_api_key"},
    model_id="claude-sonnet-4-20250514"
)

agent = Agent(
    model=model,
    name="Test Agent",
    tools=tools
)

print("Agent created successfully!")
```

### Run Integration Tests

```bash
# Set environment for testing
export STRANDS_INTEGRATION_TEST=true
export ANTHROPIC_API_KEY=your_key_here

# Run compatibility tests (no API calls)
python -m pytest tests/strands/test_strands_decorators.py -v

# Run integration tests (requires API key)
python -m pytest tests/strands/test_strands_integration.py -v

# Run A2A compatibility tests
python -m pytest tests/strands/test_a2a_compatibility.py -v
```

## Best Practices

### Tool Selection

1. **Start Small**: Begin with a few tool categories
2. **Match Use Case**: Select tools that match your agent's purpose
3. **Performance**: Too many tools can slow agent initialization
4. **Testing**: Test with a subset before deploying all tools

### Error Handling

```python
try:
    response = agent("Process this file: /path/to/file.json")
except Exception as e:
    print(f"Agent error: {e}")
    # Errors are properly formatted for A2A protocols
```

### Resource Management

```python
# For system tools requiring optional dependencies
try:
    system_tools = boat.load_all_system_tools()
except ImportError:
    print("System tools not available - install with [system] extra")
    system_tools = []

# For PDF tools
try:
    pdf_tools = boat.load_all_pdf_tools()
except ImportError:
    print("PDF tools not available - install with [pdf] extra")
    pdf_tools = []
```

## Troubleshooting

### Common Issues

**ImportError: No module named 'strands'**
```bash
pip install basic-open-agent-tools[strands]
```

**API Key Not Found**
```bash
# Set in .env file
echo "ANTHROPIC_API_KEY=your_key" > .env

# Or set environment variable
export ANTHROPIC_API_KEY=your_key
```

**Too Many Tools Warning**
```python
# Limit tools to prevent performance issues
limited_tools = boat.load_all_tools()[:50]  # First 50 tools only
```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable Strands debug logging
agent = Agent(model=model, tools=tools, debug=True)
```

## Examples

See `examples/strands_agent_example.py` for a complete working example that demonstrates:

- Environment setup
- Tool loading strategies
- Agent creation
- Basic testing
- Error handling

## Contributing

To contribute Strands integration improvements:

1. Run the Strands test suite: `python -m pytest tests/strands/ -v`
2. Add tests for new functionality
3. Update documentation
4. Test with actual Strands agents

## Support

For Strands-specific issues:

1. Check the [Strands documentation](https://docs.aws.amazon.com/strands/)
2. Review integration tests in `tests/strands/`
3. Run the example agent to verify setup
4. Open issues with specific error messages and environment details