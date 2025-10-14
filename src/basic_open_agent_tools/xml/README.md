# XML Tools

## Overview
XML parsing, authoring, validation, and transformation utilities for AI agents.

## Current Status
All planned XML modules have been implemented:
- ✅ XML parsing and reading with security protections
- ✅ XML authoring and creation from dict structures
- ✅ XML validation (well-formedness and schema validation)
- ✅ XML transformation (JSON conversion, formatting, XSLT)

## Design Considerations for Agent Tools
- Security-first approach with defusedxml protection against XML bombs and XXE attacks
- Simple dict-based representation for easy LLM understanding
- Functions designed as individual agent tools
- Type safety and validation
- Clear error messages and handling
- Consistent API design across modules
- Functions suitable for agent framework integration
- Clear function signatures optimized for AI tool usage
- Safe XML processing without code execution risks
- Optional dependencies for advanced features (lxml for XSD/XSLT)
- File size limits to prevent memory exhaustion
- **Focus on practical XML operations** (no complex XQuery or advanced DOM manipulation)

## Installation

### Core XML Support (stdlib only)
```bash
pip install basic-open-agent-tools
```
Includes: Basic parsing, authoring, well-formedness validation, JSON conversion

### Advanced XML Features (with lxml)
```bash
pip install basic-open-agent-tools[xml]
```
Adds: XSD/DTD validation, XSLT transformations, advanced XPath queries

### All Optional Features
```bash
pip install basic-open-agent-tools[all]
```

## Function Signatures

### XML Parsing (6 functions)
- `read_xml_file(file_path: str) -> dict` - Read XML file to nested dict
- `parse_xml_string(xml_content: str) -> dict` - Parse XML string to dict
- `extract_xml_elements_by_tag(file_path: str, tag_name: str) -> List[dict]` - Get all elements with tag
- `get_xml_element_text(xml_content: str, xpath: str) -> str` - Get text at XPath
- `get_xml_element_attribute(xml_content: str, xpath: str, attribute_name: str) -> str` - Get attribute value
- `list_xml_element_tags(file_path: str) -> List[str]` - List all unique tag names

### XML Authoring (7 functions)
- `create_xml_from_dict(data: dict, root_tag: str, encoding: str, indent: bool) -> str` - Create XML from dict
- `write_xml_file(data: dict, file_path: str, root_tag: str, encoding: str, skip_confirm: bool) -> str` - Write XML to file
- `create_xml_element(tag: str, text: str, attributes: Dict[str, str]) -> dict` - Create element dict
- `add_xml_child_element(parent: dict, child: dict) -> dict` - Add child to parent
- `set_xml_element_attribute(element: dict, attribute_name: str, attribute_value: str) -> dict` - Set attribute
- `build_simple_xml(root_tag: str, elements: List[dict]) -> str` - Build flat XML from list
- `xml_from_csv(csv_data: List[dict], root_tag: str, row_tag: str) -> str` - Convert CSV to XML

### XML Validation (5 functions)
- `validate_xml_well_formed(xml_content: str) -> bool` - Check XML syntax validity
- `validate_xml_against_dtd(xml_content: str, dtd_path: str) -> bool` - Validate against DTD (requires lxml)
- `validate_xml_against_xsd(xml_content: str, xsd_path: str) -> bool` - Validate against XSD (requires lxml)
- `check_xml_has_required_elements(xml_content: str, required_tags: List[str]) -> dict` - Check for required tags
- `create_xml_validation_report(xml_content: str, schema_path: str) -> dict` - Generate validation report (requires lxml)

### XML Transformation (6 functions)
- `xml_to_json(xml_content: str) -> str` - Convert XML to JSON
- `json_to_xml(json_content: str, root_tag: str) -> str` - Convert JSON to XML
- `format_xml(xml_content: str, indent_size: int) -> str` - Format with indentation
- `strip_xml_namespaces(xml_content: str) -> str` - Remove namespaces
- `transform_xml_with_xslt(xml_content: str, xslt_path: str) -> str` - Apply XSLT (requires lxml)
- `extract_xml_to_csv(xml_content: str, element_tag: str) -> List[dict]` - Extract to CSV format

## Security Features
- Safe XML parsing with defusedxml when available (prevents XML bombs)
- XXE (XML External Entity) attack prevention
- File size limits for read operations (default 10MB)
- No code execution or eval operations
- Input validation for all functions
- Protection against algorithmic complexity attacks
- DTD processing disabled by default

## Dict Structure Format

XML elements are represented as dictionaries with this structure:
```python
{
    "tag": "element_name",           # Required: element tag name
    "attributes": {"key": "value"},  # Optional: element attributes
    "text": "content",               # Optional: text content
    "children": [...]                # Optional: list of child elements
}
```

## Agent Integration
Compatible with:
- **Google ADK**: Direct function imports as tools
- **LangChain**: Wrappable with StructuredTool
- **Strands Agents**: Native @strands_tool decorator support (coming soon)
- **Custom Agents**: Simple function-based API

## Example Usage

### Reading and Parsing XML
```python
import basic_open_agent_tools as boat

# Load XML processing tools
xml_tools = boat.load_all_xml_tools()

# Individual function usage
from basic_open_agent_tools.xml import read_xml_file, parse_xml_string

# Read XML file to dict structure
xml_data = read_xml_file("/data/config.xml")
print(xml_data['tag'])  # 'configuration'
print(xml_data['children'][0])  # First child element

# Parse XML string
xml_str = '<root><item id="1">Test</item></root>'
data = parse_xml_string(xml_str)
```

### Creating and Writing XML
```python
from basic_open_agent_tools.xml import (
    create_xml_element,
    add_xml_child_element,
    write_xml_file
)

# Create elements
root = create_xml_element("books", "", {})
book1 = create_xml_element("book", "Python Guide", {"isbn": "123-456"})
book2 = create_xml_element("book", "AI Agents", {"isbn": "789-012"})

# Build structure
root = add_xml_child_element(root, book1)
root = add_xml_child_element(root, book2)

# Write to file
result = write_xml_file(root, "/tmp/catalog.xml", "books", "UTF-8", skip_confirm=False)
print(result)  # "Created XML file /tmp/catalog.xml (234 bytes)"
```

### Converting Between XML and JSON
```python
from basic_open_agent_tools.xml import xml_to_json, json_to_xml

# XML to JSON
xml = '<root><item id="1">test</item></root>'
json_str = xml_to_json(xml)

# JSON to XML
xml_str = json_to_xml(json_str, "root")
```

### Validating XML
```python
from basic_open_agent_tools.xml import (
    validate_xml_well_formed,
    check_xml_has_required_elements,
    validate_xml_against_xsd  # Requires lxml
)

# Check well-formedness
xml = '<root><item>test</item></root>'
is_valid = validate_xml_well_formed(xml)  # True

# Check for required elements
result = check_xml_has_required_elements(xml, ["root", "item"])
print(result['valid'])  # True

# Validate against schema (requires lxml)
is_valid = validate_xml_against_xsd(xml, "/schemas/document.xsd")
```

### Extracting Data to CSV Format
```python
from basic_open_agent_tools.xml import extract_xml_to_csv

xml = '''<root>
  <person name="Alice" age="30">Engineer</person>
  <person name="Bob" age="25">Designer</person>
</root>'''

csv_data = extract_xml_to_csv(xml, "person")
# Returns: [
#   {"name": "Alice", "age": "30", "_text": "Engineer"},
#   {"name": "Bob", "age": "25", "_text": "Designer"}
# ]
```

## Module Structure
- **parsing.py** - XML reading and parsing functions (6 functions)
- **authoring.py** - XML creation and writing functions (7 functions)
- **validation.py** - XML validation functions (5 functions)
- **transformation.py** - XML conversion and formatting functions (6 functions)

**Total Functions**: 24 agent-ready tools with Google ADK compatibility

## Common Use Cases
- **Configuration Files**: Parse and create XML config files
- **Data Exchange**: Convert between XML and JSON formats
- **API Integration**: Process XML responses from APIs
- **Data Validation**: Validate XML against schemas
- **Document Processing**: Transform and format XML documents
- **Data Extraction**: Convert XML to CSV for analysis
- **Content Management**: Create and manage XML-based content

## XML Processing Pipeline
Common workflow patterns:
1. `read_xml_file()` - Load XML from file
2. `validate_xml_well_formed()` - Verify syntax
3. `check_xml_has_required_elements()` - Validate structure
4. `extract_xml_elements_by_tag()` - Extract relevant data
5. `xml_to_json()` or `extract_xml_to_csv()` - Convert for processing

## Limitations
- XPath support limited to simple expressions (use lxml for advanced XPath)
- XSLT transformations require lxml
- Schema validation (XSD/DTD) requires lxml
- No support for XML signatures or encryption (security features)
- No DOM manipulation (use dict structure modification instead)

## Performance Considerations
- File size limits prevent memory exhaustion (configurable)
- Efficient parsing using ElementTree
- Memory-conscious dict representation
- Optional streaming for large files (future enhancement)

## Dependencies
- **Core**: Python stdlib only (xml.etree.ElementTree)
- **Security**: defusedxml (optional but recommended)
- **Advanced**: lxml (optional, for XSD/XSLT/advanced XPath)
