# basic-open-agent-tools

An open foundational toolkit providing essential components for building AI agents with minimal dependencies for local (non-HTTP/API) actions.

## Installation

```bash
pip install basic-open-agent-tools
```

Or with UV:
```bash
uv add basic-open-agent-tools
```

### Optional Dependencies

```bash
pip install basic-open-agent-tools[all]          # Everything
pip install basic-open-agent-tools[system]       # Process management, system info
pip install basic-open-agent-tools[pdf]          # PDF reading and creation
pip install basic-open-agent-tools[xml]          # XML parsing and validation
pip install basic-open-agent-tools[word]         # Word document operations
pip install basic-open-agent-tools[excel]        # Excel spreadsheet operations
pip install basic-open-agent-tools[powerpoint]   # PowerPoint presentations
pip install basic-open-agent-tools[image]        # Image processing
pip install basic-open-agent-tools[data]         # YAML and TOML support
```

## Quick Start

```python
import basic_open_agent_tools as boat

# Essential tools for general-purpose agents (~23 tools)
tools = boat.load_essential()

# Pre-configured loadouts for specific roles
tools = boat.load_coder_loadout()              # ~105 tools for development
tools = boat.load_docs_loadout()               # ~130 tools for documentation
tools = boat.load_data_analyst_loadout()       # ~115 tools for data analysis
tools = boat.load_web_publisher_loadout()      # ~90 tools for web content
tools = boat.load_visual_designer_loadout()    # ~60 tools for graphics
tools = boat.load_office_suite_loadout()       # ~80 tools for Office work

# Or load everything
tools = boat.load_all_tools()                  # All 337 functions

# Use with any agent framework
from google.adk.agents import Agent
agent = Agent(tools=boat.load_coder_loadout())
```

## Available Modules

**21 modules** with **337 total functions** — all with `@strands_tool` decorator and Google ADK compatible signatures.

| Module | Count | Description |
|--------|------:|-------------|
| **Core Operations** | | |
| `file_system` | 19 | File/directory operations, tree generation |
| `text` | 10 | Text processing, case conversion, formatting |
| `data` | 23 | JSON, CSV, YAML, TOML processing and validation |
| `datetime` | 46 | Date/time operations, timezones, formatting, parsing |
| **Document Processing** | | |
| `excel` | 24 | Spreadsheet reading, writing, formatting, charts |
| `xml` | 24 | XML parsing, authoring, validation, transformation |
| `pdf` | 20 | PDF creation, reading, manipulation |
| `word` | 18 | Word document operations and formatting |
| `html` | 17 | HTML generation and parsing |
| `diagrams` | 16 | Mermaid and PlantUML diagram generation |
| `markdown` | 17 | Markdown generation, parsing, HTML conversion |
| `powerpoint` | 10 | PowerPoint presentation operations |
| **System & Network** | | |
| `system` | 19 | Shell commands, process management, environment |
| `network` | 4 | HTTP client, DNS lookup, port checking |
| `utilities` | 8 | Debugging, timing, performance tools |
| **Security & Data** | | |
| `crypto` | 14 | Hashing, encoding, UUID/token generation |
| `color` | 14 | Color conversion, palette generation, analysis |
| `image` | 12 | Image manipulation and metadata reading |
| `archive` | 9 | ZIP, TAR, GZIP, BZIP2, XZ compression |
| **Task Management** | | |
| `todo` | 8 | Task creation, validation, management |
| `logging` | 5 | Structured logging and log rotation |

## Key Features

- **Agent-Friendly** — Simplified type signatures prevent "signature too complex" errors
- **Minimal Dependencies** — Pure Python core; optional deps only when needed
- **Modular** — Load only what you need
- **Multi-Framework** — Works with Google ADK, LangChain, Strands Agents, custom frameworks
- **Smart Confirmations** — Write/delete operations adapt to interactive, agent, or automation contexts
- **Pre-configured Loadouts** — 6 curated tool bundles optimized for specific use cases

## Loadouts

Choose the right loadout for your agent's role to minimize token usage and maximize relevance:

| Loadout | Tools | Best For | Includes |
|---------|------:|----------|----------|
| `load_coder_loadout()` | ~105 | Dev, DevOps, automation | File system, system ops, network, logging, crypto, archive, configs |
| `load_docs_loadout()` | ~130 | Technical writing, reports | Word, PDF, Markdown, HTML, diagrams, images, text |
| `load_data_analyst_loadout()` | ~115 | Data/financial analysis, BI | Excel, CSV, validation, diagrams, JSON, YAML, XML |
| `load_web_publisher_loadout()` | ~90 | Web dev, content management | HTML, XML, Markdown, network, text processing |
| `load_visual_designer_loadout()` | ~60 | Graphics, infographics | Image processing, diagrams, color tools |
| `load_office_suite_loadout()` | ~80 | Office productivity | Excel, Word, PowerPoint, file operations |

## Tool Loaders

Beyond loadouts, build custom tool sets by combining loaders:

```python
import basic_open_agent_tools as boat

# Use-case focused loaders
boat.load_essential()              # ~23 most commonly needed tools
boat.load_core_readonly()          # 28 read-only tools (filesystem, text, data parsing)
boat.load_converters()             # 78 pure transformation tools (text, datetime, crypto, color)
boat.load_document_readers()       # Extract content from PDF, Word, Excel, PowerPoint, images
boat.load_writers()                # All file creation/modification tools
boat.load_analyst_tools()          # Data analysis and validation tools
boat.load_web_tools()              # HTML, Markdown, network operations
boat.load_devtools()               # Debugging, logging, performance measurement
boat.load_structured_data_tools()  # CSV, JSON, XML, YAML, TOML, INI
boat.load_office_suite()           # Excel, Word, PowerPoint tools
boat.load_markup_tools()           # HTML, Markdown, XML processing

# Per-module loaders (21 total — one for each module)
boat.load_all_filesystem_tools()
boat.load_all_text_tools()
boat.load_all_data_tools()
# ... etc.

# Combine and deduplicate
custom = boat.merge_tool_lists(
    boat.load_all_filesystem_tools(),
    boat.load_all_text_tools(),
    boat.load_all_data_tools(),
)

# Inspect available tools
boat.list_all_available_tools()    # List all tool names
boat.get_tool_info(some_tool)      # Get tool metadata
```

## Safety Features

All write/delete operations include a `skip_confirm` parameter with three modes:

| Mode | When | Behavior |
|------|------|----------|
| **Bypass** | `skip_confirm=True` or `BYPASS_TOOL_CONSENT=true` env var | Proceeds immediately — for CI/CD and automation |
| **Interactive** | Terminal with `skip_confirm=False` | Prompts user with `y/n` and preview info |
| **Agent** | Non-TTY with `skip_confirm=False` | Raises `CONFIRMATION_REQUIRED` error; LLM can ask user and retry |

```python
# Safe by default — adapts to context
boat.file_system.write_file_from_string(
    file_path="/tmp/example.txt",
    content="Hello, World!",
    skip_confirm=False  # Interactive prompt OR agent error
)

# Explicit bypass
boat.file_system.write_file_from_string(
    file_path="/tmp/example.txt",
    content="Updated content",
    skip_confirm=True
)
```

## Documentation

- **[Getting Started](docs/getting-started.md)** — Installation and setup
- **[API Reference](docs/api-reference.md)** — Complete function reference
- **[Examples](docs/examples.md)** — Usage examples and patterns
- **[FAQ](docs/faq.md)** — Troubleshooting and common questions
- **[Contributing](docs/contributing.md)** — Development guidelines
- **[Changelog](CHANGELOG.md)** — Version history

## Contributing

We welcome contributions! See our [Contributing Guide](docs/contributing.md) for development setup, coding standards, and pull request process.

## License

MIT License — see [LICENSE](LICENSE) for details.
