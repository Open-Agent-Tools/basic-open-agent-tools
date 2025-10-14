"""Excel spreadsheet processing tools for AI agents.

This module provides comprehensive Excel (.xlsx) operations including:
- Reading and extracting data, tables, and metadata
- Creating new Excel workbooks
- Modifying existing spreadsheets
- Applying formatting and styles

All functions are designed for LLM agent compatibility with:
- JSON-serializable types only
- No default parameter values
- Consistent exception handling
- Comprehensive docstrings
"""

# Formatting functions
from .formatting import (
    add_excel_formula,
    apply_excel_alignment,
    apply_excel_bold,
    apply_excel_cell_color,
    apply_excel_font_size,
    freeze_excel_panes,
    set_excel_column_width,
    set_excel_row_height,
)

# Reading functions
from .reading import (
    get_excel_cell_range,
    get_excel_cell_value,
    get_excel_info,
    get_excel_metadata,
    get_excel_sheet_names,
    read_excel_as_dicts,
    read_excel_sheet,
    search_excel_text,
)

# Writing functions
from .writing import (
    add_sheet_to_excel,
    append_rows_to_excel,
    create_excel_from_dicts,
    create_excel_with_headers,
    create_simple_excel,
    delete_excel_sheet,
    excel_to_csv,
    update_excel_cell,
)

__all__: list[str] = [
    # Reading functions (8)
    "read_excel_sheet",
    "get_excel_sheet_names",
    "read_excel_as_dicts",
    "get_excel_cell_value",
    "get_excel_cell_range",
    "search_excel_text",
    "get_excel_metadata",
    "get_excel_info",
    # Writing functions (8)
    "create_simple_excel",
    "create_excel_with_headers",
    "create_excel_from_dicts",
    "add_sheet_to_excel",
    "append_rows_to_excel",
    "update_excel_cell",
    "delete_excel_sheet",
    "excel_to_csv",
    # Formatting functions (8)
    "apply_excel_bold",
    "apply_excel_font_size",
    "apply_excel_alignment",
    "set_excel_column_width",
    "set_excel_row_height",
    "apply_excel_cell_color",
    "freeze_excel_panes",
    "add_excel_formula",
]
