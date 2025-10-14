# Markdown Tools

Markdown processing tools for AI agents with parsing, generation, and conversion capabilities.

## Installation

```bash
# Part of base package - no additional dependencies
pip install basic-open-agent-tools
```

## Dependencies

- **None**: Uses Python standard library only

## Features

### Parsing & Extraction (6 functions)

- Parse Markdown structure (frontmatter, headings, sections)
- Extract headings, links, code blocks, and tables
- Convert Markdown to plain text

### Generation & Creation (6 functions)

- Create Markdown files with or without frontmatter
- Generate tables and lists as Markdown strings
- Append content to existing files
- Convert Markdown to HTML

## Usage Examples

### Parsing

```python
from basic_open_agent_tools.markdown import (
    parse_markdown_to_dict,
    extract_markdown_headings,
    extract_markdown_links
)

# Parse entire structure
data = parse_markdown_to_dict("/path/to/file.md")
print(data['frontmatter'])
print(data['headings'])

# Extract specific elements
headings = extract_markdown_headings("/path/to/file.md")
links = extract_markdown_links("/path/to/file.md")
```

### Generation

```python
from basic_open_agent_tools.markdown import (
    create_markdown_from_text,
    create_markdown_with_frontmatter,
    create_markdown_table,
    create_markdown_list
)

# Simple file
create_markdown_from_text("/tmp/doc.md", "# Hello\n\nWorld", True)

# With frontmatter
fm = {'title': 'My Post', 'date': '2024-01-01'}
create_markdown_with_frontmatter("/tmp/post.md", fm, "Content", True)

# Generate table
headers = ['Name', 'Age']
rows = [['Alice', '30'], ['Bob', '25']]
table_md = create_markdown_table(headers, rows)

# Generate list
items = ['First', 'Second', 'Third']
list_md = create_markdown_list(items, ordered=True)
```

### Conversion

```python
from basic_open_agent_tools.markdown import (
    markdown_to_plain_text,
    markdown_to_html_string
)

# Strip formatting
plain = markdown_to_plain_text("/path/to/file.md")

# Convert to HTML
html = markdown_to_html_string("# Hello\n\n**Bold** text")
```

## Function Reference

### Parsing Functions
- `parse_markdown_to_dict(file_path)` - Parse entire structure
- `extract_markdown_headings(file_path)` - Extract headings with levels
- `extract_markdown_links(file_path)` - Extract all links
- `extract_markdown_code_blocks(file_path)` - Extract fenced code blocks
- `extract_markdown_tables(file_path)` - Extract tables as 3D lists
- `markdown_to_plain_text(file_path)` - Convert to plain text

### Generation Functions
- `create_markdown_from_text(file_path, content, skip_confirm)` - Create simple file
- `create_markdown_with_frontmatter(file_path, frontmatter, content, skip_confirm)` - With YAML frontmatter
- `create_markdown_table(headers, rows)` - Generate table string
- `create_markdown_list(items, ordered)` - Generate list string
- `append_to_markdown(file_path, content, skip_confirm)` - Append content
- `markdown_to_html_string(markdown_text)` - Convert to HTML

## Safety Features

- **File size limits**: Maximum 10MB for parsing
- **Permission checks**: Validates read/write permissions
- **Overwrite protection**: `skip_confirm` parameter prevents accidents
- **Path validation**: Ensures parent directories exist
- **No external dependencies**: Pure Python stdlib implementation

## Google ADK Compliance

All functions follow Google ADK Function Tool standards:
- ✅ JSON-serializable types only
- ✅ No default parameter values
- ✅ Typed lists with item specifications
- ✅ Consistent exception patterns
- ✅ Comprehensive docstrings for LLM understanding

## Limitations

- Maximum file size: 10MB
- HTML conversion supports basic Markdown elements only
- Table parsing requires standard pipe syntax
- Frontmatter must be valid YAML key: value format

## Agent Framework Integration

Compatible with:
- Google ADK
- LangChain
- Strands Agents
- Custom agent frameworks

## Contributing

See TODO.md for planned enhancements and feature requests.
