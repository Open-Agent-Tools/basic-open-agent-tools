# Text Processing Tools Status

## Overview
Text manipulation, formatting, and processing utilities for AI agents.

## Current Status
All planned text processing modules have been implemented and tested:
- ✅ Text cleaning and whitespace normalization
- ✅ String case conversion (snake_case, camelCase, Title Case)
- ✅ HTML tag stripping and text extraction
- ✅ Unicode normalization and encoding handling
- ✅ Line ending normalization across platforms
- ✅ Smart text splitting with word preservation
- ✅ Sentence extraction and text parsing
- ✅ Advanced text joining with proper formatting

## Design Considerations for Agent Tools
- Unicode-aware text processing
- Functions designed as individual agent tools
- Memory-efficient string operations
- Clear error messages and handling
- Platform-independent line ending handling
- Consistent API design across modules
- Functions suitable for agent framework integration
- Clear function signatures optimized for AI tool usage
- Safe text processing without code execution risks
- Configurable behavior for different use cases
- **Focus on text transformation, not analysis** (NLP belongs in separate module)
- **Exclude regex-heavy operations** (provide simple, predictable transformations)
- Support for common text formatting needs
- Preserve text integrity during transformations
- Handle edge cases gracefully

## Excluded from Text Module (Separate Module Considerations)
- **Natural Language Processing** - Sentiment analysis, entity extraction, language detection (requires ML models)
- **Text Analytics** - Word frequency, readability scores, statistical analysis (separate analytics module)
- **Template Engines** - Complex templating systems (separate templating module)
- **Markdown/Rich Text Processing** - Complex markup parsing and rendering (separate markup module)

## Function Signatures

### Text Cleaning
- `clean_whitespace(text: str) -> str` - Remove extra spaces, tabs, and normalize whitespace
- `normalize_line_endings(text: str, style: str) -> str` - Standardize line endings (unix/windows/mac)
- `strip_html_tags(text: str) -> str` - Remove HTML tags and extract plain text
- `normalize_unicode(text: str, form: str) -> str` - Normalize Unicode text (NFC, NFD, NFKC, NFKD)

### Case Conversion
- `to_snake_case(text: str) -> str` - Convert to snake_case format
- `to_camel_case(text: str, upper_first: bool) -> str` - Convert to camelCase or PascalCase
- `to_title_case(text: str) -> str` - Convert to Title Case with smart capitalization

### Text Splitting and Joining
- `smart_split_lines(text: str, max_length: int, preserve_words: bool) -> List[str]` - Split text into lines with word preservation
- `extract_sentences(text: str) -> List[str]` - Extract sentences with proper boundary detection
- `join_with_oxford_comma(items: List[str], conjunction: str) -> str` - Join list items with proper grammar

## Security Features
- No code execution or eval operations
- Safe HTML tag removal without parsing vulnerabilities
- Input validation for all transformation functions
- Memory limits for large text processing
- Protection against algorithmic complexity attacks

## Performance Considerations
- Efficient string operations using built-in methods
- Memory-conscious processing for large texts
- Optimized regex patterns where used
- Minimal copying for transformation operations

## Agent Integration
Compatible with:
- **Google ADK**: Direct function imports as tools
- **LangChain**: Wrappable with StructuredTool
- **Strands Agents**: Native @strands_tool decorator support
- **Custom Agents**: Simple function-based API

## Example Usage

```python
import basic_open_agent_tools as boat

# Load text processing tools
text_tools = boat.load_all_text_tools()

# Individual function usage
from basic_open_agent_tools.text import clean_whitespace, to_snake_case

# Clean up messy text
cleaned_text = clean_whitespace("  Hello    world  \\n\\n  ")

# Convert to snake_case for programming
variable_name = to_snake_case("User Full Name")  # "user_full_name"
```

## Module Structure
- **processing.py** - Core text processing and transformation functions (10 functions)

## Common Use Cases
- **Data Cleaning**: Normalize whitespace and line endings in imported text
- **Code Generation**: Convert natural language to programming identifiers
- **Content Processing**: Clean HTML content and extract readable text
- **Text Formatting**: Prepare text for display with proper capitalization
- **Data Import**: Standardize text data from various sources
- **Template Processing**: Format lists and text for human-readable output

## Text Processing Pipeline
Many functions can be chained together for comprehensive text processing:
1. `normalize_unicode()` - Standardize character encoding
2. `strip_html_tags()` - Remove markup if present
3. `clean_whitespace()` - Normalize spacing
4. `normalize_line_endings()` - Standardize line breaks
5. Apply case conversion as needed

**Total Functions**: 10 agent-ready tools with Google ADK compatibility