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
    count_sheet_rows,
    filter_sheet_rows,
    get_excel_cell_range,
    get_excel_cell_value,
    get_excel_info,
    get_excel_metadata,
    get_excel_sheet_names,
    get_sheet_column_stats,
    get_sheet_info,
    get_sheet_row_range,
    get_sheet_schema,
    get_sheet_value_counts,
    preview_sheet_rows,
    read_excel_as_dicts,
    read_excel_sheet,
    sample_sheet_rows,
    search_excel_text,
    select_sheet_columns,
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
    # Reading functions (18 - includes 10 token-saving inspection tools)
    "read_excel_sheet",
    "get_excel_sheet_names",
    "read_excel_as_dicts",
    "get_excel_cell_value",
    "get_excel_cell_range",
    "search_excel_text",
    "get_excel_metadata",
    "get_excel_info",
    # Token-saving inspection tools
    "get_sheet_info",
    "get_sheet_schema",
    "preview_sheet_rows",
    "select_sheet_columns",
    "filter_sheet_rows",
    "get_sheet_row_range",
    "sample_sheet_rows",
    "get_sheet_column_stats",
    "count_sheet_rows",
    "get_sheet_value_counts",
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
