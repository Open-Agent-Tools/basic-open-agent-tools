"""XML tools for AI agents.

This module provides XML processing capabilities organized into logical submodules:

- parsing: XML reading, parsing, and element extraction
- authoring: XML creation and writing from dictionary structures
- validation: Well-formedness checking and schema validation
- transformation: XML/JSON conversion, formatting, and XSLT transforms
"""

# Import all functions from submodules
from .authoring import (
    add_xml_child_element,
    build_simple_xml,
    create_xml_element,
    create_xml_from_dict,
    set_xml_element_attribute,
    write_xml_file,
    xml_from_csv,
)
from .parsing import (
    extract_xml_elements_by_tag,
    get_xml_element_attribute,
    get_xml_element_text,
    list_xml_element_tags,
    parse_xml_string,
    read_xml_file,
)
from .transformation import (
    extract_xml_to_csv,
    format_xml,
    json_to_xml,
    strip_xml_namespaces,
    transform_xml_with_xslt,
    xml_to_json,
)
from .validation import (
    check_xml_has_required_elements,
    create_xml_validation_report,
    validate_xml_against_dtd,
    validate_xml_against_xsd,
    validate_xml_well_formed,
)

# Re-export all functions at module level for convenience
__all__: list[str] = [
    # Parsing functions
    "read_xml_file",
    "parse_xml_string",
    "extract_xml_elements_by_tag",
    "get_xml_element_text",
    "get_xml_element_attribute",
    "list_xml_element_tags",
    # Authoring functions
    "create_xml_from_dict",
    "write_xml_file",
    "create_xml_element",
    "add_xml_child_element",
    "set_xml_element_attribute",
    "build_simple_xml",
    "xml_from_csv",
    # Validation functions
    "validate_xml_well_formed",
    "validate_xml_against_dtd",
    "validate_xml_against_xsd",
    "check_xml_has_required_elements",
    "create_xml_validation_report",
    # Transformation functions
    "xml_to_json",
    "json_to_xml",
    "format_xml",
    "strip_xml_namespaces",
    "transform_xml_with_xslt",
    "extract_xml_to_csv",
]
