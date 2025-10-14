# HTML Tools

HTML processing tools with parsing, generation, and conversion (17 functions).

## Features
- **Parsing** (8): Extract structure, text, links, images, tables, headings, metadata
- **Generation** (9): Create pages, tables, lists, convert Markdown/HTML, prettify

## Dependencies
- None (stdlib only)

## Usage
```python
from basic_open_agent_tools.html import parse_html_to_dict, create_simple_html

# Parse HTML
data = parse_html_to_dict("/path/to/file.html")

# Create HTML
create_simple_html("/tmp/page.html", "Title", "<p>Content</p>", True)
```
