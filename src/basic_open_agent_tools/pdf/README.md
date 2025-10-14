# PDF Tools

Comprehensive PDF processing tools for AI agents with reading, creation, and manipulation capabilities.

## Installation

```bash
# Install with PDF support
pip install basic-open-agent-tools[pdf]

# Or install all features
pip install basic-open-agent-tools[all]
```

## Dependencies

- **PyPDF2**: Required for reading and manipulating PDFs
- **reportlab**: Required for creating PDFs

## Features

### Reading & Extraction (7 functions)

- Extract text from entire PDF or specific pages
- Search text within PDFs
- Get metadata (author, title, creation date, etc.)
- Get page count and document information
- Extract page ranges to text

### PDF Creation (6 functions)

- Create simple PDFs from text
- Create multi-paragraph PDFs
- Add titles and metadata
- Create multi-page documents
- Convert plain text to PDF with custom font sizes

### PDF Manipulation (7 functions)

- Merge multiple PDFs
- Split PDFs into individual pages
- Extract specific pages
- Rotate pages
- Remove pages
- Add page numbers
- Add watermarks

## Usage Examples

### Reading PDFs

```python
from basic_open_agent_tools.pdf import (
    extract_text_from_pdf,
    get_pdf_metadata,
    search_pdf_text
)

# Extract all text
text = extract_text_from_pdf("/path/to/document.pdf")

# Get metadata
metadata = get_pdf_metadata("/path/to/document.pdf")
print(metadata["author"])

# Search for text
matches = search_pdf_text("/path/to/document.pdf", "Python", False)
for match in matches:
    print(f"Found on page {match['page_number']}")
```

### Creating PDFs

```python
from basic_open_agent_tools.pdf import (
    create_simple_pdf,
    create_pdf_with_title,
    create_multi_page_pdf
)

# Simple PDF
create_simple_pdf("/tmp/simple.pdf", "Hello, World!", False)

# PDF with title
create_pdf_with_title(
    "/tmp/report.pdf",
    "Annual Report",
    "This is the report content...",
    False
)

# Multi-page PDF
pages = [
    {"title": "Chapter 1", "content": "Introduction..."},
    {"title": "Chapter 2", "content": "Analysis..."}
]
create_multi_page_pdf("/tmp/book.pdf", pages, False)
```

### Manipulating PDFs

```python
from basic_open_agent_tools.pdf import (
    merge_pdfs,
    split_pdf,
    watermark_pdf
)

# Merge PDFs
merge_pdfs(
    ["/tmp/part1.pdf", "/tmp/part2.pdf"],
    "/tmp/combined.pdf",
    False
)

# Split into pages
split_pdf("/tmp/document.pdf", "/tmp/pages", False)

# Add watermark
watermark_pdf(
    "/tmp/document.pdf",
    "/tmp/watermarked.pdf",
    "CONFIDENTIAL",
    False
)
```

## Function Reference

### Parsing Functions

- `extract_text_from_pdf(file_path: str) -> str`
- `extract_text_from_page(file_path: str, page_number: int) -> str`
- `get_pdf_metadata(file_path: str) -> dict[str, str]`
- `get_pdf_page_count(file_path: str) -> int`
- `extract_pdf_pages_to_text(file_path: str, start_page: int, end_page: int) -> list[str]`
- `search_pdf_text(file_path: str, search_term: str, case_sensitive: bool) -> list[dict[str, object]]`
- `get_pdf_info(file_path: str) -> dict[str, object]`

### Creation Functions

- `create_simple_pdf(file_path: str, content: str, skip_confirm: bool) -> str`
- `create_pdf_from_text_list(file_path: str, paragraphs: list[str], skip_confirm: bool) -> str`
- `create_pdf_with_title(file_path: str, title: str, content: str, skip_confirm: bool) -> str`
- `create_pdf_with_metadata(file_path: str, content: str, metadata: dict[str, str], skip_confirm: bool) -> str`
- `create_multi_page_pdf(file_path: str, pages: list[dict[str, str]], skip_confirm: bool) -> str`
- `text_to_pdf(text_content: str, output_path: str, font_size: int, skip_confirm: bool) -> str`

### Manipulation Functions

- `merge_pdfs(input_paths: list[str], output_path: str, skip_confirm: bool) -> str`
- `split_pdf(input_path: str, output_dir: str, skip_confirm: bool) -> str`
- `extract_pdf_pages(input_path: str, output_path: str, page_numbers: list[int], skip_confirm: bool) -> str`
- `rotate_pdf_pages(input_path: str, output_path: str, rotation: int, page_numbers: list[int], skip_confirm: bool) -> str`
- `remove_pdf_pages(input_path: str, output_path: str, page_numbers: list[int], skip_confirm: bool) -> str`
- `add_page_numbers(input_path: str, output_path: str, skip_confirm: bool) -> str`
- `watermark_pdf(input_path: str, output_path: str, watermark_text: str, skip_confirm: bool) -> str`

## Safety Features

- **File size limits**: Maximum 100MB to prevent memory exhaustion
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

- Maximum file size: 100MB
- Page indexing: 0-based (first page is page 0)
- Encrypted PDFs: May require passwords (not currently supported)
- Image extraction: Not currently supported (see TODO.md)
- Form filling: Not currently supported (see TODO.md)

## Agent Framework Integration

Compatible with:
- Google ADK
- LangChain
- Strands Agents
- Custom agent frameworks

## Error Handling

Functions raise standard Python exceptions:
- `ImportError`: When required dependencies not installed
- `FileNotFoundError`: When input files don't exist
- `ValueError`: For invalid parameters or malformed PDFs
- `TypeError`: For incorrect parameter types
- `PermissionError`: For read/write permission issues

## Performance Considerations

- Large PDFs (>10MB) may take time to process
- Text extraction quality depends on PDF structure
- Scanned PDFs require OCR (not included, see TODO.md)
- Memory usage scales with file size

## Contributing

See TODO.md for planned enhancements and feature requests.
