# PDF Tools

## Overview
Comprehensive PDF processing tools for AI agents including reading, creation, manipulation, and analysis with simplified type signatures.

## Current Status
**✅ FULLY IMPLEMENTED MODULE** - 8 functions available

This module provides complete PDF functionality for AI agents with agent-friendly signatures.

## Current Features
- ✅ **extract_text_from_pdf**: Extract text content from PDF files with page range support
- ✅ **get_pdf_info**: Get PDF metadata and document information
- ✅ **text_to_pdf**: Convert text to PDF with customizable formatting
- ✅ **merge_pdfs**: Combine multiple PDFs into single documents
- ✅ **split_pdf_by_pages**: Split PDFs into smaller files by page count
- ✅ **extract_pages_from_pdf**: Extract specific page ranges to new PDFs
- ✅ **rotate_pdf_pages**: Rotate pages with precise angle control
- ✅ **add_watermark_to_pdf**: Add text watermarks to all pages

## Function Reference

### PDF Reading Operations

#### extract_text_from_pdf
Extract text content from PDF files with flexible page range selection.

```python
def extract_text_from_pdf(
    file_path: str,
    page_range: str = "all"
) -> Dict[str, Union[str, int, List[str]]]
```

**Parameters:**
- `file_path`: Path to the PDF file
- `page_range`: Pages to extract ("all", "1", "1-3", "1,3,5")

**Returns:**
Dictionary with `file_path`, `total_pages`, `pages_extracted`, `page_range_requested`, `total_text`, `total_characters`, and `pages_detail`.

**Example:**
```python
result = extract_text_from_pdf("document.pdf", "1-5")
print(f"Extracted text: {result['total_text']}")
print(f"Character count: {result['total_characters']}")
```

#### get_pdf_info
Get comprehensive metadata and information about PDF files.

```python
def get_pdf_info(file_path: str) -> Dict[str, Union[str, int, bool]]
```

**Parameters:**
- `file_path`: Path to the PDF file

**Returns:**
Dictionary with `file_path`, `file_size_bytes`, `total_pages`, `is_encrypted`, `has_metadata`, plus metadata fields like `title`, `author`, `subject`, `creator`, `producer`, `creation_date`, and `modification_date`.

**Example:**
```python
info = get_pdf_info("document.pdf")
print(f"Title: {info['title']}")
print(f"Pages: {info['total_pages']}")
print(f"Author: {info['author']}")
```

### PDF Creation Operations

#### text_to_pdf
Convert plain text to PDF with customizable formatting options.

```python
def text_to_pdf(
    text: str,
    output_path: str,
    page_size: str = "letter",
    font_size: int = 12,
    margin_inches: float = 1.0
) -> Dict[str, Union[str, int, float]]
```

**Parameters:**
- `text`: Text content to convert
- `output_path`: Path for the output PDF file
- `page_size`: Page size ("letter" or "a4")
- `font_size`: Font size in points (8-72)
- `margin_inches`: Margin size in inches (0.5-2.0)

**Returns:**
Dictionary with `output_path`, `text_length`, `lines_count`, `pages_created`, `page_size`, `font_size`, `margin_inches`, `file_size_bytes`, and `creation_status`.

**Example:**
```python
result = text_to_pdf(
    "Hello World!\nThis is a test document.",
    "output.pdf",
    page_size="a4",
    font_size=14
)
print(f"Created {result['pages_created']} pages")
```

#### merge_pdfs
Combine multiple PDF files into a single document.

```python
def merge_pdfs(
    input_paths: List[str],
    output_path: str
) -> Dict[str, Union[str, int, List[str]]]
```

**Parameters:**
- `input_paths`: List of paths to PDF files to merge (minimum 2 files)
- `output_path`: Path for the merged output PDF

**Returns:**
Dictionary with `output_path`, `input_files_count`, `input_files`, `total_input_pages`, `total_input_size_bytes`, `output_size_bytes`, `compression_ratio`, and `merge_status`.

**Example:**
```python
result = merge_pdfs(
    ["file1.pdf", "file2.pdf", "file3.pdf"],
    "merged.pdf"
)
print(f"Merged {result['input_files_count']} files")
print(f"Total pages: {result['total_input_pages']}")
```

### PDF Manipulation Operations

#### split_pdf_by_pages
Split a large PDF into smaller files based on page count.

```python
def split_pdf_by_pages(
    input_path: str,
    pages_per_file: int,
    output_prefix: str = None
) -> Dict[str, Union[str, int, List[str]]]
```

**Parameters:**
- `input_path`: Path to input PDF
- `pages_per_file`: Number of pages per output file
- `output_prefix`: Prefix for output files (defaults to input filename)

**Returns:**
Dictionary with `input_path`, `total_pages`, `pages_per_file`, `files_created`, `output_files`, and `split_status`.

**Example:**
```python
result = split_pdf_by_pages("large_document.pdf", 10)
print(f"Created {result['files_created']} files")
for file in result['output_files']:
    print(f"Created: {file}")
```

#### extract_pages_from_pdf
Extract specific pages from a PDF to create a new document.

```python
def extract_pages_from_pdf(
    input_path: str,
    page_range: str,
    output_path: str
) -> Dict[str, Union[str, int]]
```

**Parameters:**
- `input_path`: Path to input PDF
- `page_range`: Page range to extract ("1-5", "1,3,5", "all")
- `output_path`: Path for extracted pages PDF

**Returns:**
Dictionary with `input_path`, `output_path`, `total_pages_in_input`, `pages_extracted`, `page_range_requested`, `output_file_size_bytes`, and `extraction_status`.

**Example:**
```python
result = extract_pages_from_pdf(
    "document.pdf",
    "1,5-10,15",
    "extracted.pdf"
)
print(f"Extracted {result['pages_extracted']} pages")
```

#### rotate_pdf_pages
Rotate specific pages or all pages in a PDF document.

```python
def rotate_pdf_pages(
    input_path: str,
    rotation_angle: int,
    page_range: str = "all",
    output_path: str = None
) -> Dict[str, Union[str, int]]
```

**Parameters:**
- `input_path`: Path to input PDF
- `rotation_angle`: Rotation angle (90, 180, 270, -90, -180, -270)
- `page_range`: Pages to rotate (defaults to "all")
- `output_path`: Path for rotated PDF (defaults to input_rotated.pdf)

**Returns:**
Dictionary with `input_path`, `output_path`, `total_pages`, `pages_rotated`, `rotation_angle`, `page_range`, `output_file_size_bytes`, and `rotation_status`.

**Example:**
```python
result = rotate_pdf_pages(
    "document.pdf",
    90,
    "1-5",
    "rotated.pdf"
)
print(f"Rotated {result['pages_rotated']} pages by {result['rotation_angle']}°")
```

#### add_watermark_to_pdf
Add a text watermark to all pages of a PDF document.

```python
def add_watermark_to_pdf(
    input_path: str,
    watermark_text: str,
    output_path: str = None,
    opacity: float = 0.3
) -> Dict[str, Union[str, int, float]]
```

**Parameters:**
- `input_path`: Path to input PDF
- `watermark_text`: Text to use as watermark
- `output_path`: Path for watermarked PDF (defaults to input_watermarked.pdf)
- `opacity`: Watermark opacity (0.0 to 1.0)

**Returns:**
Dictionary with `input_path`, `output_path`, `watermark_text`, `pages_watermarked`, `opacity`, `output_file_size_bytes`, and `watermarking_status`.

**Example:**
```python
result = add_watermark_to_pdf(
    "document.pdf",
    "CONFIDENTIAL",
    "watermarked.pdf",
    0.5
)
print(f"Added watermark to {result['pages_watermarked']} pages")
```

## Agent-Friendly Design Features

### Simplified Type Signatures
All functions use basic Python types (str, int, float, List, Dict) to prevent "signature too complex" errors in agent frameworks.

### Comprehensive Error Handling
- File existence and permission checking
- PDF format validation
- Page range validation
- Memory usage optimization
- Detailed error messages for debugging

### Dependency Management
- Optional dependencies with clear error messages
- Graceful fallback when libraries are missing
- Installation instructions in error messages

### Security Features
- Input sanitization and validation
- Safe file path handling
- Memory limits for large files
- No arbitrary code execution
- Safe error messages without information disclosure

## Dependencies

### Required Dependencies
This module requires optional dependencies to be installed:

```bash
# For PDF reading and manipulation
pip install basic-open-agent-tools[pdf]

# Or install manually
pip install PyPDF2>=3.0.0 reportlab>=4.0.0
```

### Library Usage
- **PyPDF2**: PDF reading, merging, splitting, rotation, page extraction
- **ReportLab**: PDF creation, watermarking, text-to-PDF conversion

## Common Use Cases

### Document Processing Pipeline
```python
# Extract text from multiple PDFs and create a summary
pdf_files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
all_text = ""

for pdf_file in pdf_files:
    result = extract_text_from_pdf(pdf_file)
    all_text += f"\n\n--- {pdf_file} ---\n{result['total_text']}"

# Create summary PDF
summary = text_to_pdf(
    all_text,
    "summary.pdf",
    font_size=10,
    page_size="a4"
)
print(f"Created summary with {summary['pages_created']} pages")
```

### PDF Security and Branding
```python
# Add watermark to sensitive documents
sensitive_docs = ["contract.pdf", "report.pdf"]

for doc in sensitive_docs:
    watermarked = add_watermark_to_pdf(
        doc,
        "CONFIDENTIAL - Internal Use Only",
        f"secure_{doc}",
        opacity=0.3
    )
    print(f"Secured: {watermarked['output_path']}")
```

### Large Document Management
```python
# Split large PDF into manageable chunks
large_pdf = "manual.pdf"
info = get_pdf_info(large_pdf)

if info['total_pages'] > 50:
    result = split_pdf_by_pages(large_pdf, 25)
    print(f"Split into {result['files_created']} smaller files")

    # Add watermark to each chunk
    for chunk_file in result['output_files']:
        add_watermark_to_pdf(
            chunk_file,
            f"Part of {large_pdf}",
            chunk_file.replace('.pdf', '_branded.pdf')
        )
```

### Page-Specific Operations
```python
# Rotate landscape pages to portrait orientation
pdf_file = "mixed_orientation.pdf"
info = get_pdf_info(pdf_file)

# First extract odd pages and rotate them
extract_result = extract_pages_from_pdf(
    pdf_file,
    "1,3,5,7,9",  # Assuming these are landscape
    "landscape_pages.pdf"
)

rotate_result = rotate_pdf_pages(
    "landscape_pages.pdf",
    90,
    "all",
    "rotated_landscape.pdf"
)

# Then merge back with even pages
merge_result = merge_pdfs(
    ["rotated_landscape.pdf", "even_pages.pdf"],
    "corrected_document.pdf"
)
```

## Agent Integration

### Google ADK
```python
from google.adk.agents import Agent
import basic_open_agent_tools as boat

pdf_tools = boat.load_all_pdf_tools()
agent = Agent(tools=pdf_tools)
```

### LangChain
```python
from langchain.tools import StructuredTool
from basic_open_agent_tools.pdf import extract_text_from_pdf

pdf_reader_tool = StructuredTool.from_function(
    func=extract_text_from_pdf,
    name="pdf_text_extractor",
    description="Extract text from PDF files with page range support"
)
```

### Strands Agents
All functions include the `@strands_tool` decorator for native compatibility:
```python
from basic_open_agent_tools.pdf import text_to_pdf
# Function is automatically compatible with Strands Agents
```

## Performance Considerations

### Memory Usage
- Large PDF files are processed in chunks
- Page-by-page processing for memory efficiency
- Automatic cleanup of temporary files
- Progress tracking for long operations

### File Size Limits
- No hard limits imposed by the library
- System memory is the practical constraint
- Recommended maximum: 100MB per PDF
- Use splitting for larger files

### Processing Speed
- Text extraction: ~10-50 pages/second
- PDF creation: ~100-500 pages/second
- Merging: ~50-200 pages/second
- Watermarking: ~20-100 pages/second

## Error Reference

### Common Error Types
- `BasicAgentToolsError`: Input validation and processing errors
- `FileNotFoundError`: File path issues
- `PermissionError`: File access problems
- `PyPDF2.errors.*`: PDF format or corruption issues

### Installation Errors
```python
# When dependencies are missing
BasicAgentToolsError: "PyPDF2 package required for PDF text extraction - install with: pip install PyPDF2"
BasicAgentToolsError: "reportlab package required for PDF creation - install with: pip install reportlab"
```

### Validation Errors
```python
# Common validation error messages
"File path must be a non-empty string"
"Input PDF not found: /path/to/file.pdf"
"Page range must be a string (e.g., '1-5', '1,3,5')"
"Font size must be an integer between 8 and 72"
"Rotation angle must be one of: 90, 180, 270, -90, -180, -270"
```

## Testing
Comprehensive test coverage includes:
- PDF reading with various formats and encodings
- Text extraction accuracy testing
- PDF creation with different parameters
- Manipulation operations with edge cases
- Error condition testing
- Memory usage testing with large files
- Cross-platform compatibility testing

**Test Coverage**: Individual function tests + integration tests + performance tests + memory tests + agent framework compatibility tests.