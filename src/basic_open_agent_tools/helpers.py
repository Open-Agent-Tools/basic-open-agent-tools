"""Helper functions for loading and managing tool collections."""

import inspect
from typing import Any, Callable, Union

from . import (
    archive,
    color,
    crypto,
    data,
    datetime,
    diagrams,
    excel,
    file_system,
    html,
    image,
    markdown,
    network,
    pdf,
    powerpoint,
    system,
    text,
    todo,
    utilities,
    word,
    xml,
)
from . import logging as log_module


def load_all_filesystem_tools() -> list[Callable[..., Any]]:
    """Load all file system tools as a list of callable functions.

    Returns:
        List of all file system tool functions

    Example:
        >>> fs_tools = load_all_filesystem_tools()
        >>> len(fs_tools) > 0
        True
    """
    tools = []

    for name in file_system.__all__:
        func = getattr(file_system, name)
        if callable(func):
            tools.append(func)

    return tools


def load_all_text_tools() -> list[Callable[..., Any]]:
    """Load all text processing tools as a list of callable functions.

    Returns:
        List of all text processing tool functions

    Example:
        >>> text_tools = load_all_text_tools()
        >>> len(text_tools) > 0
        True
    """
    tools = []

    for name in text.__all__:
        func = getattr(text, name)
        if callable(func):
            tools.append(func)

    return tools


def load_all_data_tools() -> list[Callable[..., Any]]:
    """Load all data processing tools as a list of callable functions.

    Returns:
        List of all data processing tool functions

    Example:
        >>> data_tools = load_all_data_tools()
        >>> len(data_tools) > 0
        True
    """
    tools = []

    for name in data.__all__:
        func = getattr(data, name)
        if callable(func):
            tools.append(func)

    return tools


def load_all_datetime_tools() -> list[Callable[..., Any]]:
    """Load all datetime tools as a list of callable functions.

    Returns:
        List of all datetime tool functions

    Example:
        >>> datetime_tools = load_all_datetime_tools()
        >>> len(datetime_tools) > 0
        True
    """
    tools = []

    for name in datetime.__all__:
        func = getattr(datetime, name)
        if callable(func):
            tools.append(func)

    return tools


def load_datetime_essential() -> list[Callable[..., Any]]:
    """Load essential datetime tools for common date/time operations.

    Returns a curated list of 13 most commonly needed datetime functions for
    agents that need basic date/time operations without all 40+ datetime tools.

    Includes (13 essential tools):
    - Current values: get_current_date, get_current_datetime, get_current_time
    - Date math: add_days, add_hours, subtract_days, calculate_days_between
    - Validation: is_valid_iso_date
    - Formatting: format_date_human_readable, format_time_human_readable, format_duration
    - Parsing: parse_date_string
    - Timezone: convert_timezone

    Returns:
        List of 13 essential datetime tools

    Example:
        >>> datetime_tools = load_datetime_essential()
        >>> len(datetime_tools) == 13
        True
        >>> # Use for a date-aware agent
        >>> agent = Agent(
        ...     tools=load_datetime_essential(),
        ...     instructions="Help with date and time tasks"
        ... )
    """
    from .datetime import (
        add_days,
        add_hours,
        calculate_days_between,
        convert_timezone,
        format_date_human_readable,
        format_duration,
        format_time_human_readable,
        get_current_date,
        get_current_datetime,
        get_current_time,
        is_valid_iso_date,
        parse_date_string,
        subtract_days,
    )

    return [
        get_current_date,
        get_current_datetime,
        get_current_time,
        add_days,
        add_hours,
        subtract_days,
        calculate_days_between,
        is_valid_iso_date,
        format_date_human_readable,
        format_time_human_readable,
        format_duration,
        parse_date_string,
        convert_timezone,
    ]


def load_all_network_tools() -> list[Callable[..., Any]]:
    """Load all network tools as a list of callable functions.

    Returns:
        List of all network tool functions

    Example:
        >>> network_tools = load_all_network_tools()
        >>> len(network_tools) > 0
        True
    """
    tools = []

    for name in network.__all__:
        func = getattr(network, name)
        if callable(func):
            tools.append(func)

    return tools


def load_all_utilities_tools() -> list[Callable[..., Any]]:
    """Load all utilities tools as a list of callable functions.

    Returns:
        List of all utilities tool functions

    Example:
        >>> utilities_tools = load_all_utilities_tools()
        >>> len(utilities_tools) > 0
        True
    """
    tools = []

    for name in utilities.__all__:
        func = getattr(utilities, name)
        if callable(func):
            tools.append(func)

    return tools


def load_all_system_tools() -> list[Callable[..., Any]]:
    """Load all system tools as a list of callable functions."""
    tools = []
    for name in system.__all__:
        func = getattr(system, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_crypto_tools() -> list[Callable[..., Any]]:
    """Load all crypto tools as a list of callable functions."""
    tools = []
    for name in crypto.__all__:
        func = getattr(crypto, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_archive_tools() -> list[Callable[..., Any]]:
    """Load all archive tools as a list of callable functions."""
    tools = []
    for name in archive.__all__:
        func = getattr(archive, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_logging_tools() -> list[Callable[..., Any]]:
    """Load all logging tools as a list of callable functions."""
    tools = []
    for name in log_module.__all__:
        func = getattr(log_module, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_todo_tools() -> list[Callable[..., Any]]:
    """Load all todo tools as a list of callable functions."""
    tools = []
    for name in todo.__all__:
        func = getattr(todo, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_xml_tools() -> list[Callable[..., Any]]:
    """Load all XML processing tools as a list of callable functions.

    Returns:
        List of all XML tool functions

    Example:
        >>> xml_tools = load_all_xml_tools()
        >>> len(xml_tools) == 24
        True
    """
    tools = []
    for name in xml.__all__:
        func = getattr(xml, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_pdf_tools() -> list[Callable[..., Any]]:
    """Load all PDF processing tools as a list of callable functions.

    Returns:
        List of all PDF tool functions

    Example:
        >>> pdf_tools = load_all_pdf_tools()
        >>> len(pdf_tools) == 20
        True
    """
    tools = []
    for name in pdf.__all__:
        func = getattr(pdf, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_word_tools() -> list[Callable[..., Any]]:
    """Load all Word document processing tools as a list of callable functions.

    Returns:
        List of all Word tool functions

    Example:
        >>> word_tools = load_all_word_tools()
        >>> len(word_tools) == 18
        True
    """
    tools = []
    for name in word.__all__:
        func = getattr(word, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_excel_tools() -> list[Callable[..., Any]]:
    """Load all Excel spreadsheet processing tools as a list of callable functions.

    Returns:
        List of all Excel tool functions

    Example:
        >>> excel_tools = load_all_excel_tools()
        >>> len(excel_tools) == 24
        True
    """
    tools = []
    for name in excel.__all__:
        func = getattr(excel, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_markdown_tools() -> list[Callable[..., Any]]:
    """Load all Markdown processing tools as a list of callable functions.

    Returns:
        List of all Markdown tool functions

    Example:
        >>> markdown_tools = load_all_markdown_tools()
        >>> len(markdown_tools) == 12
        True
    """
    tools = []
    for name in markdown.__all__:
        func = getattr(markdown, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_html_tools() -> list[Callable[..., Any]]:
    """Load all HTML processing tools as a list of callable functions.

    Returns:
        List of all HTML tool functions

    Example:
        >>> html_tools = load_all_html_tools()
        >>> len(html_tools) == 17
        True
    """
    tools = []
    for name in html.__all__:
        func = getattr(html, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_powerpoint_tools() -> list[Callable[..., Any]]:
    """Load all PowerPoint presentation processing tools as a list of callable functions.

    Returns:
        List of all PowerPoint tool functions

    Example:
        >>> powerpoint_tools = load_all_powerpoint_tools()
        >>> len(powerpoint_tools) == 10
        True
    """
    tools = []
    for name in powerpoint.__all__:
        func = getattr(powerpoint, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_image_tools() -> list[Callable[..., Any]]:
    """Load all image processing tools as a list of callable functions.

    Returns:
        List of all image tool functions

    Example:
        >>> image_tools = load_all_image_tools()
        >>> len(image_tools) == 12
        True
    """
    tools = []
    for name in image.__all__:
        func = getattr(image, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_diagrams_tools() -> list[Callable[..., Any]]:
    """Load all diagram generation tools as a list of callable functions.

    Returns:
        List of all diagram tool functions

    Example:
        >>> diagram_tools = load_all_diagrams_tools()
        >>> len(diagram_tools) == 16
        True
    """
    tools = []
    for name in diagrams.__all__:
        func = getattr(diagrams, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_color_tools() -> list[Callable[..., Any]]:
    """Load all color manipulation tools as a list of callable functions.

    Returns:
        List of all color tool functions

    Example:
        >>> color_tools = load_all_color_tools()
        >>> len(color_tools) == 14
        True
    """
    tools = []
    for name in color.__all__:
        func = getattr(color, name)
        if callable(func):
            tools.append(func)
    return tools


def load_all_tools() -> list[Callable[..., Any]]:
    """Load all tools from all modules as a single list of callable functions.

    This is a convenience function that loads and combines tools from all
    implemented modules.

    Returns:
        List of all tool functions from all modules (automatically deduplicated)

    Example:
        >>> all_tools = load_all_tools()
        >>> len(all_tools) >= 170  # Total with all modules including Phase 3
        True
        >>> # Use with agent frameworks
        >>> agent = Agent(tools=load_all_tools())
    """
    return merge_tool_lists(
        load_all_filesystem_tools(),
        load_all_text_tools(),
        load_all_data_tools(),
        load_all_datetime_tools(),
        load_all_network_tools(),
        load_all_utilities_tools(),
        load_all_system_tools(),
        load_all_crypto_tools(),
        load_all_archive_tools(),
        load_all_logging_tools(),
        load_all_todo_tools(),
        load_all_xml_tools(),
        load_all_pdf_tools(),
        load_all_word_tools(),
        load_all_excel_tools(),
        load_all_markdown_tools(),
        load_all_html_tools(),
        load_all_powerpoint_tools(),
        load_all_image_tools(),
        load_all_diagrams_tools(),
        load_all_color_tools(),
    )


def load_data_json_tools() -> list[Callable[..., Any]]:
    """Load JSON processing tools as a list of callable functions.

    Returns:
        List of JSON processing tool functions

    Example:
        >>> json_tools = load_data_json_tools()
        >>> len(json_tools) == 3
        True
    """
    from .data import json_tools

    tools = []
    json_function_names = [
        "safe_json_serialize",
        "safe_json_deserialize",
        "validate_json_string",
    ]

    for name in json_function_names:
        func = getattr(json_tools, name)
        if callable(func):
            tools.append(func)

    return tools


def load_data_csv_tools() -> list[Callable[..., Any]]:
    """Load CSV processing tools as a list of callable functions.

    Returns:
        List of CSV processing tool functions

    Example:
        >>> csv_tools = load_data_csv_tools()
        >>> len(csv_tools) == 7
        True
    """
    from .data import csv_tools

    tools = []
    csv_function_names = [
        "read_csv_simple",
        "write_csv_simple",
        "csv_to_dict_list",
        "dict_list_to_csv",
        "detect_csv_delimiter",
        "validate_csv_structure",
        "clean_csv_data",
    ]

    for name in csv_function_names:
        func = getattr(csv_tools, name)
        if callable(func):
            tools.append(func)

    return tools


def load_data_validation_tools() -> list[Callable[..., Any]]:
    """Load data validation tools as a list of callable functions.

    Returns:
        List of data validation tool functions

    Example:
        >>> validation_tools = load_data_validation_tools()
        >>> len(validation_tools) == 5
        True
    """
    from .data import validation

    tools = []
    validation_function_names = [
        "validate_schema_simple",
        "check_required_fields",
        "validate_data_types_simple",
        "validate_range_simple",
        "create_validation_report",
    ]

    for name in validation_function_names:
        func = getattr(validation, name)
        if callable(func):
            tools.append(func)

    return tools


def load_data_config_tools() -> list[Callable[..., Any]]:
    """Load configuration file processing tools as a list of callable functions.

    Returns:
        List of configuration file processing tool functions

    Example:
        >>> config_tools = load_data_config_tools()
        >>> len(config_tools) == 8
        True
    """
    from .data import config_processing

    tools = []
    config_function_names = [
        "read_yaml_file",
        "write_yaml_file",
        "read_toml_file",
        "write_toml_file",
        "read_ini_file",
        "write_ini_file",
        "validate_config_schema",
        "merge_config_files",
    ]

    for name in config_function_names:
        func = getattr(config_processing, name)
        if callable(func):
            tools.append(func)

    return tools


def load_core_readonly() -> list[Callable[..., Any]]:
    """Load core read-only tools for safe file and text operations.

    Perfect for agents that need to read files, process text, and parse
    common data formats without any ability to modify the file system.

    Includes (~30 tools):
    - File system: read files, list directories, check existence (9 tools)
    - Text processing: clean, normalize, transform text (10 tools)
    - Data parsing: CSV, JSON, YAML, TOML, INI (8 tools)
    - Validation: CSV structure, JSON validation (included in data tools)

    Returns:
        List of core read-only tools

    Example:
        >>> core_tools = load_core_readonly()
        >>> len(core_tools) >= 27
        True
        >>> # Use for a read-only agent
        >>> agent = Agent(
        ...     tools=load_core_readonly(),
        ...     instructions="Analyze files but never modify them"
        ... )
    """
    from .data import config_processing, csv_tools, json_tools

    tools: list[Callable[..., Any]] = []

    from .file_system import (
        directory_exists,
        file_exists,
        generate_directory_tree,
        get_file_info,
        get_file_size,
        is_empty_directory,
        list_all_directory_contents,
        list_directory_contents,
        read_file_to_string,
    )

    tools.extend(
        [
            read_file_to_string,
            list_directory_contents,
            list_all_directory_contents,
            file_exists,
            directory_exists,
            get_file_info,
            get_file_size,
            generate_directory_tree,
            is_empty_directory,
        ]
    )

    tools.extend(load_all_text_tools())

    tools.append(csv_tools.read_csv_simple)
    tools.append(csv_tools.csv_to_dict_list)
    tools.append(csv_tools.detect_csv_delimiter)
    tools.append(csv_tools.validate_csv_structure)

    tools.append(json_tools.safe_json_deserialize)
    tools.append(json_tools.validate_json_string)

    tools.append(config_processing.read_yaml_file)
    tools.append(config_processing.read_toml_file)
    tools.append(config_processing.read_ini_file)

    return tools


def load_converters() -> list[Callable[..., Any]]:
    """Load pure transformation tools with no I/O operations.

    Perfect for agents that need to transform data without touching the
    file system. All functions take input and return transformed output
    without side effects.

    Includes (~78 tools):
    - Text processing: case conversion, whitespace, formatting (10 tools)
    - Date/time: parsing, formatting, calculations (40 tools)
    - Crypto: hashing, encoding, UUID/token generation (14 tools)
    - Color: conversion, palette generation, analysis (14 tools)

    Returns:
        List of pure transformation tools

    Example:
        >>> converter_tools = load_converters()
        >>> len(converter_tools) >= 78
        True
        >>> # Use for a data transformation agent
        >>> agent = Agent(
        ...     tools=load_converters(),
        ...     instructions="Transform and convert data formats"
        ... )
    """
    tools: list[Callable[..., Any]] = []

    tools.extend(load_all_text_tools())

    tools.extend(load_all_datetime_tools())

    tools.extend(load_all_crypto_tools())

    tools.extend(load_all_color_tools())

    return tools


def load_document_readers() -> list[Callable[..., Any]]:
    """Load tools for reading and extracting content from documents.

    Perfect for agents that need to analyze document content across
    multiple formats (PDF, Word, Excel, PowerPoint, images).

    Includes reading functions from:
    - PDF: text extraction, metadata, page info
    - Word: content extraction, structure analysis
    - Excel: spreadsheet reading, cell data extraction
    - PowerPoint: slide content, notes extraction
    - Image: metadata reading, EXIF data

    Returns:
        List of document reading tools

    Example:
        >>> reader_tools = load_document_readers()
        >>> # Use for a document analysis agent
        >>> agent = Agent(
        ...     tools=load_document_readers(),
        ...     instructions="Extract and analyze content from documents"
        ... )
    """
    from .excel import (
        excel_to_csv,
        get_excel_cell_range,
        get_excel_cell_value,
        get_excel_metadata,
        get_excel_sheet_names,
    )
    from .image import extract_image_exif, get_image_info
    from .pdf import (
        extract_text_from_page,
        extract_text_from_pdf,
        get_pdf_metadata,
        get_pdf_page_count,
    )
    from .powerpoint import (
        extract_pptx_notes,
        get_pptx_metadata,
        get_pptx_slide_count,
        get_pptx_slide_text,
    )
    from .word import (
        extract_text_from_docx,
        get_docx_metadata,
        get_docx_paragraphs,
    )

    tools: list[Callable[..., Any]] = []

    tools.extend(
        [
            extract_text_from_pdf,
            extract_text_from_page,
            get_pdf_metadata,
            get_pdf_page_count,
        ]
    )

    tools.extend(
        [
            extract_text_from_docx,
            get_docx_paragraphs,
            get_docx_metadata,
        ]
    )

    tools.extend(
        [
            get_excel_sheet_names,
            get_excel_cell_range,
            get_excel_cell_value,
            get_excel_metadata,
            excel_to_csv,
        ]
    )

    tools.extend(
        [
            get_pptx_slide_count,
            get_pptx_slide_text,
            extract_pptx_notes,
            get_pptx_metadata,
        ]
    )

    tools.extend([get_image_info, extract_image_exif])

    return tools


def load_writers() -> list[Callable[..., Any]]:
    """Load all tools that create or modify files.

    Perfect for agents that need to generate output files across
    various formats. Includes all write, create, and modify operations.

    SAFETY: All tools include skip_confirm parameter for user approval.

    Includes:
    - File system: write files, create directories, move/copy
    - Data formats: CSV, JSON, YAML, TOML, INI writers
    - Documents: PDF, Word, Excel, PowerPoint creation
    - Archives: ZIP, TAR, compression operations
    - Markup: HTML, Markdown, XML generation

    Returns:
        List of file creation/modification tools

    Example:
        >>> writer_tools = load_writers()
        >>> # Use for a content generation agent
        >>> agent = Agent(
        ...     tools=load_writers(),
        ...     instructions="Create output files as requested by user"
        ... )
    """
    from .data import config_processing, csv_tools, json_tools
    from .file_system import (
        append_to_file,
        copy_file,
        create_directory,
        delete_directory,
        delete_file,
        insert_at_line,
        move_file,
        replace_in_file,
        write_file_from_string,
    )

    tools: list[Callable[..., Any]] = []

    tools.extend(
        [
            write_file_from_string,
            append_to_file,
            insert_at_line,
            create_directory,
            delete_file,
            delete_directory,
            move_file,
            copy_file,
            replace_in_file,
        ]
    )

    tools.append(csv_tools.write_csv_simple)
    tools.append(csv_tools.dict_list_to_csv)
    tools.append(json_tools.safe_json_serialize)
    tools.append(config_processing.write_yaml_file)
    tools.append(config_processing.write_toml_file)
    tools.append(config_processing.write_ini_file)
    tools.append(config_processing.merge_config_files)

    tools.extend(load_all_pdf_tools())
    tools.extend(load_all_word_tools())
    tools.extend(load_all_excel_tools())
    tools.extend(load_all_powerpoint_tools())

    tools.extend(load_all_html_tools())
    tools.extend(load_all_markdown_tools())
    tools.extend(load_all_xml_tools())

    tools.extend(load_all_archive_tools())

    tools.extend(load_all_image_tools())

    tools.extend(load_all_diagrams_tools())

    return tools


def load_analyst_tools() -> list[Callable[..., Any]]:
    """Load tools focused on data analysis and validation.

    Perfect for agents that analyze data quality, validate schemas,
    and work with structured data formats.

    Includes:
    - Data validation: schema validation, type checking, range validation
    - CSV analysis: structure validation, delimiter detection, cleaning
    - JSON processing: serialization, validation, parsing
    - Statistics and reporting: validation reports, data summaries

    Returns:
        List of data analysis tools

    Example:
        >>> analyst_tools = load_analyst_tools()
        >>> # Use for a data quality agent
        >>> agent = Agent(
        ...     tools=load_analyst_tools(),
        ...     instructions="Analyze and validate data quality"
        ... )
    """
    tools = []

    tools.extend(load_data_validation_tools())

    tools.extend(load_data_csv_tools())

    tools.extend(load_data_json_tools())

    tools.extend(load_data_config_tools())

    return tools


def load_web_tools() -> list[Callable[..., Any]]:
    """Load tools for web content processing and network operations.

    Perfect for agents that work with web content, make HTTP requests,
    and process HTML/Markdown for web publishing.

    Includes:
    - HTML: generation, parsing, manipulation (17 tools)
    - Markdown: generation, parsing, conversion (12 tools)
    - Network: HTTP client, DNS lookup, port checking (4 tools)

    Returns:
        List of web-related tools

    Example:
        >>> web_tools = load_web_tools()
        >>> # Use for a web scraping/generation agent
        >>> agent = Agent(
        ...     tools=load_web_tools(),
        ...     instructions="Process web content and make HTTP requests"
        ... )
    """
    tools = []

    tools.extend(load_all_html_tools())

    tools.extend(load_all_markdown_tools())

    tools.extend(load_all_network_tools())

    return tools


def load_devtools() -> list[Callable[..., Any]]:
    """Load debugging, logging, and development utilities.

    Perfect for agents that need to debug issues, measure performance,
    and provide detailed logging.

    Includes:
    - Utilities: timing, performance measurement, debugging (8 tools)
    - Logging: structured logging, log rotation (5 tools)
    - System info: environment variables, process info (subset of system tools)

    Returns:
        List of development and debugging tools

    Example:
        >>> dev_tools = load_devtools()
        >>> # Use for a debugging agent
        >>> agent = Agent(
        ...     tools=load_devtools(),
        ...     instructions="Debug issues and measure performance"
        ... )
    """
    tools = []

    tools.extend(load_all_utilities_tools())

    tools.extend(load_all_logging_tools())

    from .system import get_env_var, list_env_vars

    tools.extend([get_env_var, list_env_vars])

    return tools


def load_structured_data_tools() -> list[Callable[..., Any]]:
    """Load tools for working with structured data formats.

    Perfect for agents that process configuration files and structured
    data in CSV, JSON, XML, YAML, TOML, and INI formats.

    Includes:
    - CSV: reading, writing, validation (7 tools)
    - JSON: serialization, parsing, validation (3 tools)
    - XML: parsing, generation, validation, transformation (24 tools)
    - Config files: YAML, TOML, INI read/write (8 tools)

    Returns:
        List of structured data processing tools

    Example:
        >>> data_tools = load_structured_data_tools()
        >>> # Use for a config management agent
        >>> agent = Agent(
        ...     tools=load_structured_data_tools(),
        ...     instructions="Process and manage configuration files"
        ... )
    """
    tools = []

    tools.extend(load_data_csv_tools())

    tools.extend(load_data_json_tools())

    tools.extend(load_all_xml_tools())

    tools.extend(load_data_config_tools())

    return tools


def load_office_suite() -> list[Callable[..., Any]]:
    """Load Microsoft Office document processing tools.

    Perfect for agents that work with business documents across
    Excel, Word, and PowerPoint formats.

    Includes:
    - Excel: spreadsheet operations, formulas, charts (24 tools)
    - Word: document creation, formatting, content extraction (18 tools)
    - PowerPoint: presentation creation, slide management (10 tools)

    Returns:
        List of Office suite tools

    Example:
        >>> office_tools = load_office_suite()
        >>> # Use for a business document agent
        >>> agent = Agent(
        ...     tools=load_office_suite(),
        ...     instructions="Create and analyze Office documents"
        ... )
    """
    tools = []

    tools.extend(load_all_excel_tools())

    tools.extend(load_all_word_tools())

    tools.extend(load_all_powerpoint_tools())

    return tools


def load_markup_tools() -> list[Callable[..., Any]]:
    """Load markup language processing tools.

    Perfect for agents that work with markup languages for documentation,
    web content, and structured text.

    Includes:
    - HTML: generation, parsing, manipulation (17 tools)
    - Markdown: generation, parsing, conversion (12 tools)
    - XML: parsing, generation, validation, XSLT (24 tools)

    Returns:
        List of markup language tools

    Example:
        >>> markup_tools = load_markup_tools()
        >>> # Use for a documentation agent
        >>> agent = Agent(
        ...     tools=load_markup_tools(),
        ...     instructions="Generate and process markup documents"
        ... )
    """
    tools = []

    tools.extend(load_all_html_tools())

    tools.extend(load_all_markdown_tools())

    tools.extend(load_all_xml_tools())

    return tools


def load_essential() -> list[Callable[..., Any]]:
    """Load the most commonly needed tools for general-purpose agents.

    Perfect for agents that need basic file operations, data processing,
    and common utilities without overwhelming them with specialized tools.

    Includes (~24 essential tools):
    - File I/O: read, write, list, check existence, cwd (8 tools)
    - Shell: execute shell commands (1 tool)
    - Data: JSON/CSV/YAML read/write (6 tools)
    - Text: whitespace cleaning (1 tool)
    - Time: current date and datetime (2 tools)
    - Crypto: hashing, UUIDs (2 tools)
    - Network: HTTP requests (1 tool)
    - Logging: basic logging (1 tool)
    - Directories: create, list contents (2 tools)

    Returns:
        List of essential general-purpose tools

    Example:
        >>> essential_tools = load_essential()
        >>> len(essential_tools) >= 22
        True
        >>> # Use for a general-purpose agent
        >>> agent = Agent(
        ...     tools=load_essential(),
        ...     instructions="Help with common file and data tasks"
        ... )
    """
    from .crypto import generate_uuid, hash_sha256
    from .data import config_processing, csv_tools, json_tools
    from .datetime import get_current_date, get_current_datetime
    from .file_system import (
        create_directory,
        delete_file,
        directory_exists,
        file_exists,
        list_directory_contents,
        read_file_to_string,
        write_file_from_string,
    )
    from .network import http_request
    from .system import execute_shell_command, get_current_directory
    from .text import clean_whitespace

    tools: list[Callable[..., Any]] = []

    tools.extend(
        [
            read_file_to_string,
            write_file_from_string,
            list_directory_contents,
            create_directory,
            file_exists,
            directory_exists,
            delete_file,
            get_current_directory,
        ]
    )

    tools.extend(
        [
            json_tools.safe_json_serialize,
            json_tools.safe_json_deserialize,
            csv_tools.read_csv_simple,
            csv_tools.write_csv_simple,
            config_processing.read_yaml_file,
            config_processing.write_yaml_file,
        ]
    )

    tools.append(clean_whitespace)

    tools.extend([get_current_date, get_current_datetime])

    tools.extend([hash_sha256, generate_uuid])

    tools.append(execute_shell_command)

    tools.append(http_request)

    from .logging import log_info

    tools.append(log_info)

    return tools


def load_coder_loadout() -> list[Callable[..., Any]]:
    """Load tools optimized for software development, DevOps, and automation tasks.

    Perfect for agents that write code, manage configurations, automate deployments,
    or handle development workflows. Includes all tools needed for technical work.

    Includes (~105 tools):
    - File system: All operations (18 tools)
    - System: Process, environment, platform operations (20 tools)
    - Network: HTTP requests, DNS, connectivity (3 tools)
    - Data config: YAML, TOML, JSON, INI parsing (11 tools)
    - Text processing: String manipulation (10 tools)
    - Utilities: Timing, debugging, performance (8 tools)
    - Logging: Structured logging with rotation (5 tools)
    - Crypto: Hashing, UUIDs, encoding (13 tools)
    - Archive: Compression, extraction (5 tools)
    - Datetime: Date/time essentials (13 tools)

    Returns:
        List of development-focused tools

    Example:
        >>> coder_tools = load_coder_loadout()
        >>> len(coder_tools) >= 100
        True
        >>> # Use for a DevOps agent
        >>> from google.adk.agents import Agent
        >>> agent = Agent(
        ...     tools=load_coder_loadout(),
        ...     name="DevOpsAssistant",
        ...     instruction="Manage deployments and server configurations"
        ... )
    """
    tools = []

    tools.extend(load_all_filesystem_tools())
    tools.extend(load_all_system_tools())
    tools.extend(load_all_network_tools())
    tools.extend(load_all_utilities_tools())
    tools.extend(load_all_logging_tools())
    tools.extend(load_all_crypto_tools())
    tools.extend(load_all_archive_tools())
    tools.extend(load_all_text_tools())
    tools.extend(load_datetime_essential())
    tools.extend(load_data_config_tools())

    return tools


def load_docs_loadout() -> list[Callable[..., Any]]:
    """Load tools for document creation across all formats.

    Perfect for agents that create technical documentation, reports, research papers,
    user guides, or any written content. Covers all major document formats.

    Includes (~130 tools):
    - Word: Document creation and formatting (18 tools)
    - PDF: Generation, manipulation, reading (20 tools)
    - Markdown: Parsing, generation, conversion (12 tools)
    - HTML: Generation and manipulation (17 tools)
    - File system: All operations (18 tools)
    - Text processing: String manipulation (10 tools)
    - Diagrams: Flowcharts, graphs, visualizations (16 tools)
    - Datetime: Date/time essentials (13 tools)
    - Image: Basic image operations (12 tools)

    Returns:
        List of document creation tools

    Example:
        >>> docs_tools = load_docs_loadout()
        >>> len(docs_tools) >= 125
        True
        >>> # Use for a technical writer agent
        >>> from google.adk.agents import Agent
        >>> agent = Agent(
        ...     tools=load_docs_loadout(),
        ...     name="TechnicalWriter",
        ...     instruction="Create comprehensive API documentation"
        ... )
    """
    tools = []

    tools.extend(load_all_word_tools())
    tools.extend(load_all_pdf_tools())
    tools.extend(load_all_markdown_tools())
    tools.extend(load_all_html_tools())

    tools.extend(load_all_filesystem_tools())
    tools.extend(load_all_text_tools())
    tools.extend(load_all_diagrams_tools())
    tools.extend(load_datetime_essential())
    tools.extend(load_all_image_tools())

    return tools


def load_data_analyst_loadout() -> list[Callable[..., Any]]:
    """Load tools for data analysis, validation, and Excel operations.

    Perfect for agents that analyze datasets, create financial models, validate data,
    or generate analytical visualizations. Excel and CSV focused.

    Includes (~115 tools):
    - Excel: Spreadsheet operations, formulas, charts (24 tools)
    - CSV: Reading, writing, validation (7 tools)
    - Data validation: Schema checking, type validation (5 tools)
    - Diagrams: Charts, graphs, visualizations (16 tools)
    - Structured data: JSON, YAML, TOML, XML (42 tools)
    - File system: All operations (18 tools)
    - Datetime: Date/time essentials (13 tools)

    Returns:
        List of data analysis tools

    Example:
        >>> analyst_tools = load_data_analyst_loadout()
        >>> len(analyst_tools) >= 110
        True
        >>> # Use for a financial analysis agent
        >>> from google.adk.agents import Agent
        >>> agent = Agent(
        ...     tools=load_data_analyst_loadout(),
        ...     name="FinancialAnalyst",
        ...     instruction="Analyze quarterly financial data and create reports"
        ... )
    """
    tools = []

    tools.extend(load_all_excel_tools())
    tools.extend(load_data_csv_tools())
    tools.extend(load_data_validation_tools())
    tools.extend(load_all_diagrams_tools())

    tools.extend(load_structured_data_tools())

    tools.extend(load_all_filesystem_tools())
    tools.extend(load_datetime_essential())

    return tools


def load_web_publisher_loadout() -> list[Callable[..., Any]]:
    """Load tools for web content creation and publishing.

    Perfect for agents that create websites, blogs, manage HTML/XML content,
    or work with static site generators. Web-focused markup languages.

    Includes (~90 tools):
    - HTML: Generation, parsing, manipulation (17 tools)
    - XML: Parsing, generation, validation, XSLT (24 tools)
    - Markdown: Parsing, generation, conversion (12 tools)
    - Network: HTTP requests, connectivity (3 tools)
    - File system: All operations (18 tools)
    - Text processing: String manipulation (10 tools)
    - Datetime: Date/time essentials (13 tools)

    Returns:
        List of web publishing tools

    Example:
        >>> web_tools = load_web_publisher_loadout()
        >>> len(web_tools) >= 85
        True
        >>> # Use for a blog publisher agent
        >>> from google.adk.agents import Agent
        >>> agent = Agent(
        ...     tools=load_web_publisher_loadout(),
        ...     name="BlogPublisher",
        ...     instruction="Convert markdown drafts to HTML and publish"
        ... )
    """
    tools = []

    tools.extend(load_all_html_tools())
    tools.extend(load_all_xml_tools())
    tools.extend(load_all_markdown_tools())

    tools.extend(load_all_network_tools())
    tools.extend(load_all_filesystem_tools())
    tools.extend(load_all_text_tools())
    tools.extend(load_datetime_essential())

    return tools


def load_visual_designer_loadout() -> list[Callable[..., Any]]:
    """Load tools for visual design, graphics, and color work.

    Perfect for agents that create infographics, manage color palettes,
    process images, or generate diagrams and visualizations.

    Includes (~60 tools):
    - Image: Processing, metadata, transformations (12 tools)
    - Diagrams: Flowcharts, graphs, charts (16 tools)
    - Color: Palettes, conversions, analysis (14 tools)
    - File system: All operations (18 tools)

    Returns:
        List of visual design tools

    Example:
        >>> designer_tools = load_visual_designer_loadout()
        >>> len(designer_tools) >= 55
        True
        >>> # Use for an infographic creator agent
        >>> from google.adk.agents import Agent
        >>> agent = Agent(
        ...     tools=load_visual_designer_loadout(),
        ...     name="InfographicCreator",
        ...     instruction="Create data visualizations and color schemes"
        ... )
    """
    tools = []

    tools.extend(load_all_image_tools())
    tools.extend(load_all_diagrams_tools())
    tools.extend(load_all_color_tools())

    tools.extend(load_all_filesystem_tools())

    return tools


def load_office_suite_loadout() -> list[Callable[..., Any]]:
    """Load Microsoft Office suite tools for business productivity.

    Perfect for agents that work with business documents across Excel, Word,
    and PowerPoint. Comprehensive Office productivity tools.

    Includes (~80 tools):
    - Excel: Spreadsheet operations, formulas, charts (24 tools)
    - Word: Document creation and formatting (18 tools)
    - PowerPoint: Presentation creation and management (10 tools)
    - File system: All operations (18 tools)
    - Datetime: Date/time essentials (13 tools)

    Returns:
        List of Office suite tools

    Example:
        >>> office_tools = load_office_suite_loadout()
        >>> len(office_tools) >= 75
        True
        >>> # Use for a business productivity agent
        >>> from google.adk.agents import Agent
        >>> agent = Agent(
        ...     tools=load_office_suite_loadout(),
        ...     name="OfficeAssistant",
        ...     instruction="Create business reports and presentations"
        ... )
    """
    tools = []

    tools.extend(load_all_excel_tools())
    tools.extend(load_all_word_tools())
    tools.extend(load_all_powerpoint_tools())

    tools.extend(load_all_filesystem_tools())
    tools.extend(load_datetime_essential())

    return tools


def merge_tool_lists(
    *args: Union[list[Callable[..., Any]], Callable[..., Any]],
) -> list[Callable[..., Any]]:
    """Merge multiple tool lists and individual functions into a single list.

    This function automatically deduplicates tools based on their function name and module.
    If the same function appears multiple times, only the first occurrence is kept.

    Args:
        *args: Tool lists (List[Callable]) and/or individual functions (Callable)

    Returns:
        Combined list of all tools with duplicates removed

    Raises:
        TypeError: If any argument is not a list of callables or a callable

    Example:
        >>> def custom_tool(x): return x
        >>> fs_tools = load_all_filesystem_tools()
        >>> text_tools = load_all_text_tools()
        >>> all_tools = merge_tool_lists(fs_tools, text_tools, custom_tool)
        >>> custom_tool in all_tools
        True
    """
    merged = []
    seen = set()

    for arg in args:
        if callable(arg):
            func_key = (arg.__name__, getattr(arg, "__module__", ""))
            if func_key not in seen:
                merged.append(arg)
                seen.add(func_key)
        elif isinstance(arg, list):
            for item in arg:
                if not callable(item):
                    raise TypeError(
                        f"All items in tool lists must be callable, got {type(item)}"
                    )
                func_key = (item.__name__, getattr(item, "__module__", ""))
                if func_key not in seen:
                    merged.append(item)
                    seen.add(func_key)
        else:
            raise TypeError(
                f"Arguments must be callable or list of callables, got {type(arg)}"
            )

    return merged


def get_tool_info(tool: Callable[..., Any]) -> dict[str, Any]:
    """Get information about a tool function.

    Args:
        tool: The tool function to inspect

    Returns:
        Dictionary containing tool information (name, docstring, signature)

    Example:
        >>> from basic_open_agent_tools.text import clean_whitespace
        >>> info = get_tool_info(clean_whitespace)
        >>> info['name']
        'clean_whitespace'
    """
    if not callable(tool):
        raise TypeError("Tool must be callable")

    sig = inspect.signature(tool)

    return {
        "name": tool.__name__,
        "docstring": tool.__doc__ or "",
        "signature": str(sig),
        "module": getattr(tool, "__module__", "unknown"),
        "parameters": list(sig.parameters.keys()),
    }


def list_all_available_tools() -> dict[str, list[dict[str, Any]]]:
    """List all available tools organized by category.

    Returns:
        Dictionary with tool categories as keys and lists of tool info as values

    Example:
        >>> tools = list_all_available_tools()
        >>> 'file_system' in tools
        True
        >>> 'text' in tools
        True
    """
    return {
        "file_system": [get_tool_info(tool) for tool in load_all_filesystem_tools()],
        "text": [get_tool_info(tool) for tool in load_all_text_tools()],
        "data": [get_tool_info(tool) for tool in load_all_data_tools()],
        "datetime": [get_tool_info(tool) for tool in load_all_datetime_tools()],
    }


__all__ = [
    "load_all_filesystem_tools",
    "load_all_text_tools",
    "load_all_data_tools",
    "load_all_datetime_tools",
    "load_all_network_tools",
    "load_all_utilities_tools",
    "load_all_system_tools",
    "load_all_crypto_tools",
    "load_all_archive_tools",
    "load_all_logging_tools",
    "load_all_todo_tools",
    "load_all_xml_tools",
    "load_all_pdf_tools",
    "load_all_word_tools",
    "load_all_excel_tools",
    "load_all_markdown_tools",
    "load_all_html_tools",
    "load_all_powerpoint_tools",
    "load_all_image_tools",
    "load_all_diagrams_tools",
    "load_all_color_tools",
    "load_all_tools",
    "load_data_json_tools",
    "load_data_csv_tools",
    "load_data_validation_tools",
    "load_data_config_tools",
    "load_core_readonly",
    "load_converters",
    "load_document_readers",
    "load_writers",
    "load_analyst_tools",
    "load_web_tools",
    "load_devtools",
    "load_structured_data_tools",
    "load_office_suite",
    "load_markup_tools",
    "load_essential",
    "load_datetime_essential",
    "load_coder_loadout",
    "load_docs_loadout",
    "load_data_analyst_loadout",
    "load_web_publisher_loadout",
    "load_visual_designer_loadout",
    "load_office_suite_loadout",
    "merge_tool_lists",
    "get_tool_info",
    "list_all_available_tools",
]
