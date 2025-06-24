# TODO: basic-open-agent-tools

This document provides an overview of planned development for the basic-open-agent-tools project, with references to detailed TODOs in each module.

## Project Vision

Create a comprehensive toolkit of **AI agent tools** providing essential functions for agent frameworks like Google ADK, LangChain, and custom agent implementations. Functions are designed for individual import as agent tools while maintaining clean module-level APIs for direct usage.

## Implementation Status

### ✅ Completed Modules

#### File System Tools (`src/basic_open_agent_tools/file_system/`)
**Status:** ✅ Fully Implemented  
**Functions:** 18 agent-ready functions across 4 submodules
- **Operations:** read, write, append, create, delete, move, copy
- **Information:** existence checking, file info, size queries  
- **Tree Operations:** directory tree generation with depth control
- **Validation:** path and content validation utilities

**Coverage:** 41% test coverage, all functions working

#### Text Processing Tools (`src/basic_open_agent_tools/text/`)
**Status:** ✅ Fully Implemented  
**Functions:** 10 agent-ready text processing functions
- **Normalization:** clean_whitespace, normalize_line_endings, normalize_unicode
- **HTML Processing:** strip_html_tags with intelligent spacing
- **Case Conversion:** to_snake_case, to_camel_case, to_title_case  
- **Text Manipulation:** smart_split_lines, extract_sentences, join_with_oxford_comma

**Coverage:** 98% test coverage, comprehensive quality assurance

#### Helper Functions (`src/basic_open_agent_tools/helpers.py`)
**Status:** ✅ Fully Implemented  
**Functions:** 5 top-level tool management functions
- **Tool Loading:** load_all_filesystem_tools(), load_all_text_tools()
- **Tool Management:** merge_tool_lists(), get_tool_info(), list_all_available_tools()
- **Agent Integration:** Designed for seamless agent framework integration

**Coverage:** 96% test coverage, full type safety

**Usage Example:**
```python
import basic_open_agent_tools as boat

# Load tools by category
fs_tools = boat.load_all_filesystem_tools()  # 18 functions
text_tools = boat.load_all_text_tools()     # 10 functions

# Add custom tools
def my_custom_tool(input: str) -> str:
    return input.upper()

# Merge all tools for agent use
agent_tools = boat.merge_tool_lists(fs_tools, text_tools, my_custom_tool)
# Result: 29 total functions ready for agent frameworks
```

---

## 🚧 Planned Modules

### High Priority

#### 1. Network Tools (`src/basic_open_agent_tools/network/`)
**Status:** 📋 Planned  
**See:** [network/TODO.md](src/basic_open_agent_tools/network/TODO.md)

**Key Functions:**
- URL and IP address validation
- Local network interface utilities
- Port checking and discovery
- Network connectivity testing

**Agent Use Cases:** Network validation, local discovery, connectivity checks

#### 2. Data Tools (`src/basic_open_agent_tools/data/`)
**Status:** 📋 Planned  
**See:** [data/TODO.md](src/basic_open_agent_tools/data/TODO.md)

**Key Functions:**
- Data structure manipulation
- Schema validation
- Serialization utilities (JSON, CSV, YAML)
- Data transformation and querying

**Agent Use Cases:** Data validation, transformation, structured processing

#### 3. System Tools (`src/basic_open_agent_tools/system/`)
**Status:** 📋 Planned  
**See:** [system/TODO.md](src/basic_open_agent_tools/system/TODO.md)

**Key Functions:**
- Process management and execution
- Environment variable handling
- Resource monitoring
- System information gathering

**Agent Use Cases:** Command execution, system monitoring, environment management

### Medium Priority

#### 4. Cryptographic Tools (`src/basic_open_agent_tools/crypto/`)
**Status:** 📋 Planned  
**See:** [crypto/TODO.md](src/basic_open_agent_tools/crypto/TODO.md)

**Key Functions:**
- File and string hashing (MD5, SHA256, SHA512)
- Encoding/decoding (Base64, URL, HTML entities)
- Random generation and UUIDs
- Data integrity verification

**Agent Use Cases:** Data integrity, encoding, secure random generation

**⚠️ Note:** NO encryption/decryption - integrity and encoding only

#### 5. Utility Tools (`src/basic_open_agent_tools/utilities/`)
**Status:** 📋 Planned  
**See:** [utilities/TODO.md](src/basic_open_agent_tools/utilities/TODO.md)

**Key Functions:**
- Logging and configuration utilities
- Caching and timing helpers
- Common decorators and error handling
- Testing and debugging utilities

**Agent Use Cases:** Infrastructure, debugging, performance optimization

---

## 🎯 Development Priorities

### Phase 1: Core Utilities (Next Release)
1. **Data Tools** - Critical for structured data handling
2. **Network Tools** - Important for connectivity and validation

### Phase 2: System Integration
3. **System Tools** - Process management and system interaction
4. **Crypto Tools** - Security and integrity features

### Phase 3: Infrastructure
5. **Utilities** - Development and debugging support

---

## 📋 Module TODO References

Each module has a detailed TODO.md file with specific implementation plans:

- **File System:** [src/basic_open_agent_tools/file_system/TODO.md](src/basic_open_agent_tools/file_system/TODO.md) ✅ *Implemented*
- **Text Processing:** ✅ *Fully Implemented* (10 functions + comprehensive tests)
- **Helper Functions:** ✅ *Fully Implemented* (5 tool management functions)
- **Network:** [src/basic_open_agent_tools/network/TODO.md](src/basic_open_agent_tools/network/TODO.md)
- **Data:** [src/basic_open_agent_tools/data/TODO.md](src/basic_open_agent_tools/data/TODO.md)
- **System:** [src/basic_open_agent_tools/system/TODO.md](src/basic_open_agent_tools/system/TODO.md)
- **Crypto:** [src/basic_open_agent_tools/crypto/TODO.md](src/basic_open_agent_tools/crypto/TODO.md)
- **Utilities:** [src/basic_open_agent_tools/utilities/TODO.md](src/basic_open_agent_tools/utilities/TODO.md)

---

## 🏗️ Architecture Guidelines

### Agent Tool Design Principles
- **Individual Function Imports:** Each function works as standalone agent tool
- **Clear Function Signatures:** Optimized for AI interpretation
- **Comprehensive Docstrings:** Help AI understand function purpose
- **Stateless Operations:** Thread-safe and concurrent-friendly
- **Consistent Error Handling:** Predictable exception patterns
- **Type Safety:** Full type annotations for all functions

### Framework Compatibility
- **Google ADK:** Direct function imports in tools list
- **LangChain:** Functions wrapped with StructuredTool
- **Custom Agents:** Direct function integration
- **MCP Servers:** Adaptable for Model Context Protocol

### Quality Standards
- **Testing:** Minimum 70% coverage target for new modules
- **Documentation:** Complete API reference and examples
- **Type Safety:** 100% mypy compliance
- **Code Quality:** All ruff checks passing
- **Dependencies:** Minimal external dependencies (prefer stdlib)

---

## 🚀 Getting Started with Development

### For Contributors
1. **Read:** [docs/contributing.md](docs/contributing.md) - Development setup and guidelines
2. **Choose Module:** Pick from planned modules above
3. **Review TODO:** Read the specific module's TODO.md file
4. **Follow Pattern:** Use file_system module as implementation reference

### For Users
1. **Current:** Use file_system and text processing tools for production workloads
2. **Helper Functions:** Use top-level helpers for easy tool loading and management
3. **Coming Soon:** Data processing and network tools (next release)
4. **Documentation:** See [docs/](docs/) for complete usage guides

---

## 📊 Progress Tracking

- **Modules Planned:** 7 total
- **Modules Implemented:** 2 (file_system ✅, text ✅) + helper functions ✅
- **Functions Available:** 33+ agent tools ready for use
  - **File System:** 18 functions (read, write, tree operations, validation)
  - **Text Processing:** 10 functions (normalization, case conversion, manipulation)
  - **Helper Functions:** 5 functions (tool loading, management, inspection)
- **Test Coverage:** 66% overall (98%+ for new implementations)
- **Quality Assurance:** Full ruff + mypy compliance, GPG signed commits
- **Agent Frameworks:** Google ADK, LangChain, Custom agents supported

**Next Milestone:** Data processing and network tools implementation