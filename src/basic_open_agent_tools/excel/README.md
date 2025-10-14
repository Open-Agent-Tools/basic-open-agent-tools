# Excel Tools

Comprehensive Excel spreadsheet processing tools for AI agents with reading, creation, and formatting capabilities.

## Installation

```bash
# Install with Excel support
pip install basic-open-agent-tools[excel]

# Or install all features
pip install basic-open-agent-tools[all]
```

## Dependencies

- **openpyxl**: Required for reading and creating Excel spreadsheets (.xlsx format)

## Features

### Reading & Extraction (8 functions)

- Read sheets as 2D lists or dictionaries
- Get sheet names and cell values/ranges
- Extract metadata and comprehensive workbook info
- Search text across all sheets

### Spreadsheet Creation & Modification (8 functions)

- Create workbooks from lists, headers, or dictionaries
- Add/delete sheets and append rows
- Update individual cells
- Export sheets to CSV format

### Formatting & Styles (8 functions)

- Apply bold, font sizes, and colors
- Set cell alignment and column/row dimensions
- Freeze panes for easier navigation
- Add formulas to cells

## Usage Examples

### Reading Spreadsheets

```python
from basic_open_agent_tools.excel import (
    read_excel_sheet,
    get_excel_sheet_names,
    read_excel_as_dicts
)

# Read sheet as 2D list
data = read_excel_sheet("/path/to/file.xlsx", "Sheet1")

# Get all sheet names
sheets = get_excel_sheet_names("/path/to/file.xlsx")

# Read with headers as dict keys
records = read_excel_as_dicts("/path/to/file.xlsx", "Sheet1", 1)
```

### Creating Spreadsheets

```python
from basic_open_agent_tools.excel import (
    create_simple_excel,
    create_excel_with_headers,
    create_excel_from_dicts
)

# Simple workbook
data = [['Name', 'Age'], ['Alice', '30'], ['Bob', '25']]
create_simple_excel("/tmp/data.xlsx", data, False)

# With headers
headers = ['Name', 'Age', 'City']
rows = [['Alice', '30', 'NYC'], ['Bob', '25', 'LA']]
create_excel_with_headers("/tmp/data.xlsx", headers, rows, False)

# From dictionaries
records = [{'Name': 'Alice', 'Age': '30'}, {'Name': 'Bob', 'Age': '25'}]
create_excel_from_dicts("/tmp/data.xlsx", records, False)
```

### Modifying Spreadsheets

```python
from basic_open_agent_tools.excel import (
    add_sheet_to_excel,
    append_rows_to_excel,
    update_excel_cell
)

# Add new sheet
data = [['Product', 'Price'], ['Apple', '1.00']]
add_sheet_to_excel("/tmp/data.xlsx", "Products", data, True)

# Append rows
rows = [['Charlie', '35', 'SF']]
append_rows_to_excel("/tmp/data.xlsx", "Sheet1", rows, True)

# Update single cell
update_excel_cell("/tmp/data.xlsx", "Sheet1", "B5", "Updated", True)
```

### Formatting

```python
from basic_open_agent_tools.excel import (
    apply_excel_bold,
    apply_excel_alignment,
    set_excel_column_width,
    add_excel_formula
)

# Apply bold to range
apply_excel_bold("/tmp/data.xlsx", "Sheet1", "A1:A10", True)

# Center align cells
apply_excel_alignment("/tmp/data.xlsx", "Sheet1", "A1", "center", "center", True)

# Set column width
set_excel_column_width("/tmp/data.xlsx", "Sheet1", "A", 20, True)

# Add formula
add_excel_formula("/tmp/data.xlsx", "Sheet1", "C10", "=SUM(C1:C9)", True)
```

## Function Reference

### Reading Functions
- `read_excel_sheet(file_path, sheet_name)`
- `get_excel_sheet_names(file_path)`
- `read_excel_as_dicts(file_path, sheet_name, header_row)`
- `get_excel_cell_value(file_path, sheet_name, cell_reference)`
- `get_excel_cell_range(file_path, sheet_name, start_cell, end_cell)`
- `search_excel_text(file_path, search_term, case_sensitive)`
- `get_excel_metadata(file_path)`
- `get_excel_info(file_path)`

### Writing Functions
- `create_simple_excel(file_path, data, skip_confirm)`
- `create_excel_with_headers(file_path, headers, data, skip_confirm)`
- `create_excel_from_dicts(file_path, data, skip_confirm)`
- `add_sheet_to_excel(file_path, sheet_name, data, skip_confirm)`
- `append_rows_to_excel(file_path, sheet_name, rows, skip_confirm)`
- `update_excel_cell(file_path, sheet_name, cell_reference, value, skip_confirm)`
- `delete_excel_sheet(file_path, sheet_name, skip_confirm)`
- `excel_to_csv(file_path, sheet_name, output_path, skip_confirm)`

### Formatting Functions
- `apply_excel_bold(file_path, sheet_name, cell_range, skip_confirm)`
- `apply_excel_font_size(file_path, sheet_name, cell_range, font_size, skip_confirm)`
- `apply_excel_alignment(file_path, sheet_name, cell_range, horizontal, vertical, skip_confirm)`
- `set_excel_column_width(file_path, sheet_name, column_letter, width, skip_confirm)`
- `set_excel_row_height(file_path, sheet_name, row_number, height, skip_confirm)`
- `apply_excel_cell_color(file_path, sheet_name, cell_range, color_hex, skip_confirm)`
- `freeze_excel_panes(file_path, sheet_name, cell_reference, skip_confirm)`
- `add_excel_formula(file_path, sheet_name, cell_reference, formula, skip_confirm)`

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
- Only supports .xlsx format (not .xls)
- Cell references use A1 notation (e.g., "A1", "B5", "AA10")
- Row numbers are 1-indexed, header rows are 1-indexed
- Charts/images: Not currently supported (see TODO.md)
- Pivot tables: Not currently supported (see TODO.md)

## Agent Framework Integration

Compatible with:
- Google ADK
- LangChain
- Strands Agents
- Custom agent frameworks

## Error Handling

Functions raise standard Python exceptions:
- `ImportError`: When openpyxl not installed
- `FileNotFoundError`: When input files don't exist
- `ValueError`: For invalid parameters or malformed spreadsheets
- `TypeError`: For incorrect parameter types
- `PermissionError`: For read/write permission issues
- `IndexError`: For out-of-range indices

## Performance Considerations

- Large files (>10MB) may take time to process
- Read-only mode used where possible for better performance
- Formula evaluation: Formulas are evaluated on Excel open (data_only=True)
- Use cell ranges efficiently for bulk operations

## Contributing

See TODO.md for planned enhancements and feature requests.
