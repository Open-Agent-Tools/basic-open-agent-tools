# Word Tools

Comprehensive Word document processing tools for AI agents with reading, creation, and formatting capabilities.

## Installation

```bash
# Install with Word support
pip install basic-open-agent-tools[word]

# Or install all features
pip install basic-open-agent-tools[all]
```

## Dependencies

- **python-docx**: Required for reading and creating Word documents

## Features

### Reading & Extraction (6 functions)

- Extract text from entire document or as separate paragraphs
- Extract tables with full structure
- Get metadata (author, title, dates, etc.)
- Search text within documents
- Get comprehensive document information

### Document Creation & Modification (8 functions)

- Create simple documents from text
- Create multi-paragraph documents
- Add titles with heading styles
- Append paragraphs to existing documents
- Create structured documents with headings
- Add tables to documents
- Fill templates with placeholder replacements
- Convert documents to plain text

### Formatting & Styles (4 functions)

- Apply heading styles (Heading 1-9)
- Make paragraphs bold
- Set paragraph alignment (left, center, right, justify)
- Insert page breaks

## Usage Examples

### Reading Documents

```python
from basic_open_agent_tools.word import (
    extract_text_from_docx,
    get_docx_metadata,
    search_docx_text
)

# Extract all text
text = extract_text_from_docx("/path/to/document.docx")

# Get metadata
metadata = get_docx_metadata("/path/to/document.docx")
print(metadata["author"])

# Search for text
matches = search_docx_text("/path/to/document.docx", "Python", False)
for match in matches:
    print(f"Found in paragraph {match['paragraph_index']}")
```

### Creating Documents

```python
from basic_open_agent_tools.word import (
    create_simple_docx,
    create_docx_with_title,
    create_docx_with_headings
)

# Simple document
create_simple_docx("/tmp/simple.docx", "Hello, World!", False)

# Document with title
create_docx_with_title(
    "/tmp/report.docx",
    "Annual Report",
    "This is the report content...",
    False
)

# Structured document with headings
sections = [
    {"heading": "Introduction", "level": "1", "content": "Intro text..."},
    {"heading": "Methods", "level": "1", "content": "Method details..."}
]
create_docx_with_headings("/tmp/structured.docx", sections, False)
```

### Modifying Documents

```python
from basic_open_agent_tools.word import (
    add_paragraph_to_docx,
    add_table_to_docx,
    apply_heading_style
)

# Add paragraph
add_paragraph_to_docx("/tmp/doc.docx", "New paragraph text", True)

# Add table
table_data = [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]]
add_table_to_docx("/tmp/doc.docx", table_data, True)

# Apply heading style to first paragraph
apply_heading_style("/tmp/doc.docx", 0, 1, True)
```

### Template Filling

```python
from basic_open_agent_tools.word import create_docx_from_template

# Fill template with data
replacements = {
    "name": "John Doe",
    "date": "2024-01-15",
    "amount": "$1,000"
}
create_docx_from_template(
    "/templates/invoice.docx",
    "/output/filled_invoice.docx",
    replacements,
    False
)
```

## Function Reference

### Reading Functions

- `extract_text_from_docx(file_path: str) -> str`
- `get_docx_paragraphs(file_path: str) -> list[str]`
- `get_docx_tables(file_path: str) -> list[list[list[str]]]`
- `get_docx_metadata(file_path: str) -> dict[str, str]`
- `search_docx_text(file_path: str, search_term: str, case_sensitive: bool) -> list[dict[str, object]]`
- `get_docx_info(file_path: str) -> dict[str, object]`

### Writing Functions

- `create_simple_docx(file_path: str, content: str, skip_confirm: bool) -> str`
- `create_docx_from_paragraphs(file_path: str, paragraphs: list[str], skip_confirm: bool) -> str`
- `create_docx_with_title(file_path: str, title: str, content: str, skip_confirm: bool) -> str`
- `add_paragraph_to_docx(file_path: str, paragraph: str, skip_confirm: bool) -> str`
- `create_docx_with_headings(file_path: str, sections: list[dict[str, str]], skip_confirm: bool) -> str`
- `add_table_to_docx(file_path: str, table_data: list[list[str]], skip_confirm: bool) -> str`
- `create_docx_from_template(template_path: str, output_path: str, replacements: dict[str, str], skip_confirm: bool) -> str`
- `docx_to_text(file_path: str, output_path: str, skip_confirm: bool) -> str`

### Styling Functions

- `apply_heading_style(file_path: str, paragraph_index: int, heading_level: int, skip_confirm: bool) -> str`
- `apply_bold_to_paragraph(file_path: str, paragraph_index: int, skip_confirm: bool) -> str`
- `set_paragraph_alignment(file_path: str, paragraph_index: int, alignment: str, skip_confirm: bool) -> str`
- `add_page_break(file_path: str, after_paragraph: int, skip_confirm: bool) -> str`

## Safety Features

- **File size limits**: Maximum 50MB to prevent memory exhaustion
- **Permission checks**: Validates read/write permissions before operations
- **Overwrite protection**: `skip_confirm` parameter prevents accidental overwrites
- **Path validation**: Ensures parent directories exist
- **Error handling**: Clear, consistent exception messages

## Google ADK Compliance

All functions follow Google ADK Function Tool standards:
- ✅ JSON-serializable types only (str, int, bool, dict, list)
- ✅ No default parameter values
- ✅ Typed lists with item specifications
- ✅ Consistent exception patterns
- ✅ Comprehensive docstrings for LLM understanding

## Limitations

- Maximum file size: 50MB
- Paragraph/table indexing: 0-based
- Only supports .docx format (not .doc)
- Templates use {{placeholder}} syntax
- Image operations: Not currently supported (see TODO.md)
- Comments/tracked changes: Not currently supported (see TODO.md)

## Agent Framework Integration

Compatible with:
- Google ADK
- LangChain
- Strands Agents
- Custom agent frameworks

## Error Handling

Functions raise standard Python exceptions:
- `ImportError`: When python-docx not installed
- `FileNotFoundError`: When input files don't exist
- `ValueError`: For invalid parameters or malformed documents
- `TypeError`: For incorrect parameter types
- `PermissionError`: For read/write permission issues
- `IndexError`: For out-of-range paragraph indices

## Performance Considerations

- Large documents (>10MB) may take time to process
- Table extraction preserves full structure
- Text extraction is fast and efficient
- Template filling supports complex replacements

## Contributing

See TODO.md for planned enhancements and feature requests.
