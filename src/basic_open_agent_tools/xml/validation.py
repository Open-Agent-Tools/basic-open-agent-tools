"""XML validation functions for AI agents.

This module provides XML validation including well-formedness checking,
required element validation, and schema validation (when lxml is available).
"""

import warnings
import xml.etree.ElementTree as ET

from ..decorators import strands_tool

try:
    from defusedxml.ElementTree import (
        fromstring as defused_fromstring,  # type: ignore[import-untyped]
    )

    HAS_DEFUSEDXML = True
except ImportError:
    HAS_DEFUSEDXML = False
    warnings.warn(
        "defusedxml is not installed. XML parsing may be vulnerable to XXE attacks "
        "and XML bombs. For production use, install with: "
        "pip install basic-open-agent-tools[xml]",
        RuntimeWarning,
        stacklevel=2,
    )

try:
    from lxml import etree as lxml_etree  # type: ignore[import-untyped]

    HAS_LXML = True
except ImportError:
    HAS_LXML = False


@strands_tool
def validate_xml_well_formed(xml_content: str) -> bool:
    """Check if XML is well-formed (valid syntax).

    This function validates that XML content has proper syntax including
    balanced tags, proper nesting, valid character encoding, and correct
    structure.

    Args:
        xml_content: XML content as string to validate

    Returns:
        True if XML is well-formed

    Raises:
        ValueError: With detailed error message about syntax issues
        TypeError: If xml_content is not a string

    Example:
        >>> valid_xml = '<root><item>test</item></root>'
        >>> validate_xml_well_formed(valid_xml)
        True
        >>> invalid_xml = '<root><item>test</root>'
        >>> try:
        ...     validate_xml_well_formed(invalid_xml)
        ... except ValueError as e:
        ...     'mismatched tag' in str(e).lower()
        True
    """
    if not isinstance(xml_content, str):
        raise TypeError("xml_content must be a string")

    if not xml_content.strip():
        raise ValueError("XML content cannot be empty")

    try:
        # Use defusedxml if available for security
        if HAS_DEFUSEDXML:
            defused_fromstring(xml_content)
        else:
            ET.fromstring(xml_content)

        return True

    except ET.ParseError as e:
        raise ValueError(f"XML is not well-formed: {e}")


@strands_tool
def validate_xml_against_dtd(xml_content: str, dtd_path: str) -> bool:
    """Validate XML against DTD schema.

    This function requires lxml to be installed. It validates XML content
    against a Document Type Definition (DTD) schema file.

    Args:
        xml_content: XML content as string to validate
        dtd_path: Path to DTD file

    Returns:
        True if XML is valid against DTD

    Raises:
        ValueError: If XML doesn't validate or DTD has errors
        TypeError: If parameters are not strings
        ImportError: If lxml is not installed
        FileNotFoundError: If DTD file not found

    Example:
        >>> xml = '<!DOCTYPE root SYSTEM "test.dtd"><root><item/></root>'
        >>> # Requires lxml installed
        >>> validate_xml_against_dtd(xml, "/path/to/schema.dtd")  # doctest: +SKIP
        True
    """
    if not HAS_LXML:
        raise ImportError(
            "lxml is required for DTD validation. "
            "Install with: pip install basic-open-agent-tools[xml]"
        )

    if not isinstance(xml_content, str):
        raise TypeError("xml_content must be a string")

    if not isinstance(dtd_path, str):
        raise TypeError("dtd_path must be a string")

    if not xml_content.strip():
        raise ValueError("xml_content cannot be empty")

    if not dtd_path.strip():
        raise ValueError("dtd_path cannot be empty")

    try:
        # Parse DTD
        with open(dtd_path, "rb") as f:
            dtd = lxml_etree.DTD(f)

        # Parse XML
        doc = lxml_etree.fromstring(xml_content.encode("utf-8"))

        # Validate
        if not dtd.validate(doc):
            error_log = dtd.error_log.filter_from_errors()
            errors = [str(error) for error in error_log]
            raise ValueError(f"DTD validation failed: {'; '.join(errors)}")

        return True

    except FileNotFoundError:
        raise FileNotFoundError(f"DTD file not found: {dtd_path}")
    except lxml_etree.DTDParseError as e:
        raise ValueError(f"Invalid DTD schema: {e}")
    except lxml_etree.XMLSyntaxError as e:
        raise ValueError(f"Invalid XML syntax: {e}")


@strands_tool
def validate_xml_against_xsd(xml_content: str, xsd_path: str) -> bool:
    """Validate XML against XSD schema.

    This function requires lxml to be installed. It validates XML content
    against an XML Schema Definition (XSD) file.

    Args:
        xml_content: XML content as string to validate
        xsd_path: Path to XSD schema file

    Returns:
        True if XML is valid against XSD

    Raises:
        ValueError: If XML doesn't validate or XSD has errors
        TypeError: If parameters are not strings
        ImportError: If lxml is not installed
        FileNotFoundError: If XSD file not found

    Example:
        >>> xml = '<root><item type="test">content</item></root>'
        >>> # Requires lxml installed
        >>> validate_xml_against_xsd(xml, "/path/to/schema.xsd")  # doctest: +SKIP
        True
    """
    if not HAS_LXML:
        raise ImportError(
            "lxml is required for XSD validation. "
            "Install with: pip install basic-open-agent-tools[xml]"
        )

    if not isinstance(xml_content, str):
        raise TypeError("xml_content must be a string")

    if not isinstance(xsd_path, str):
        raise TypeError("xsd_path must be a string")

    if not xml_content.strip():
        raise ValueError("xml_content cannot be empty")

    if not xsd_path.strip():
        raise ValueError("xsd_path cannot be empty")

    try:
        # Parse XSD schema
        with open(xsd_path, "rb") as f:
            schema_doc = lxml_etree.parse(f)
            schema = lxml_etree.XMLSchema(schema_doc)

        # Parse XML
        doc = lxml_etree.fromstring(xml_content.encode("utf-8"))

        # Validate
        if not schema.validate(doc):
            error_log = schema.error_log.filter_from_errors()
            errors = [str(error) for error in error_log]
            raise ValueError(f"XSD validation failed: {'; '.join(errors)}")

        return True

    except FileNotFoundError:
        raise FileNotFoundError(f"XSD file not found: {xsd_path}")
    except lxml_etree.XMLSchemaParseError as e:
        raise ValueError(f"Invalid XSD schema: {e}")
    except lxml_etree.XMLSyntaxError as e:
        raise ValueError(f"Invalid XML syntax: {e}")


@strands_tool
def check_xml_has_required_elements(xml_content: str, required_tags: list[str]) -> dict:
    """Verify XML contains all required element tags.

    This function checks that an XML document contains all elements
    with the specified tag names, useful for validating document structure.

    Args:
        xml_content: XML content as string to check
        required_tags: List of tag names that must be present

    Returns:
        Dictionary with validation results:
        - 'valid': bool - True if all required tags found
        - 'missing': List[str] - Tags not found in document
        - 'found': List[str] - Tags that were found

    Raises:
        ValueError: If XML is malformed
        TypeError: If parameters are wrong type

    Example:
        >>> xml = '<root><title>Test</title><author>John</author></root>'
        >>> result = check_xml_has_required_elements(xml, ["title", "author"])
        >>> result['valid']
        True
        >>> result['missing']
        []
        >>> result = check_xml_has_required_elements(xml, ["title", "date"])
        >>> result['valid']
        False
        >>> 'date' in result['missing']
        True
    """
    if not isinstance(xml_content, str):
        raise TypeError("xml_content must be a string")

    if not isinstance(required_tags, list):
        raise TypeError("required_tags must be a list")

    if not xml_content.strip():
        raise ValueError("xml_content cannot be empty")

    # Validate required_tags items are strings
    for i, tag in enumerate(required_tags):
        if not isinstance(tag, str):
            raise TypeError(f"Tag at index {i} must be a string")

    try:
        # Parse XML
        if HAS_DEFUSEDXML:
            root = defused_fromstring(xml_content)
        else:
            root = ET.fromstring(xml_content)

        # Collect all tag names in document
        found_tags = set()
        found_tags.add(root.tag)
        for element in root.iter():
            found_tags.add(element.tag)

        # Check which required tags are present
        found = []
        missing = []
        for tag in required_tags:
            if tag in found_tags:
                found.append(tag)
            else:
                missing.append(tag)

        return {
            "valid": len(missing) == 0,
            "missing": missing,
            "found": found,
        }

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML content: {e}")


@strands_tool
def create_xml_validation_report(xml_content: str, schema_path: str) -> dict:
    """Generate detailed validation report against schema.

    This function validates XML against an XSD schema and provides
    a detailed report of validation results. Requires lxml to be installed.

    Args:
        xml_content: XML content as string to validate
        schema_path: Path to XSD schema file

    Returns:
        Dictionary with validation report:
        - 'valid': bool - True if validation passed
        - 'errors': List[str] - List of validation error messages
        - 'warnings': List[str] - List of validation warnings
        - 'error_count': int - Number of errors found
        - 'warning_count': int - Number of warnings found

    Raises:
        ValueError: If XML or schema has syntax errors
        TypeError: If parameters are wrong type
        ImportError: If lxml is not installed
        FileNotFoundError: If schema file not found

    Example:
        >>> xml = '<root><item>test</item></root>'
        >>> # Requires lxml installed
        >>> report = create_xml_validation_report(xml, "/path/to/schema.xsd")  # doctest: +SKIP
        >>> report['valid']  # doctest: +SKIP
        True
        >>> report['error_count']  # doctest: +SKIP
        0
    """
    if not HAS_LXML:
        raise ImportError(
            "lxml is required for schema validation. "
            "Install with: pip install basic-open-agent-tools[xml]"
        )

    if not isinstance(xml_content, str):
        raise TypeError("xml_content must be a string")

    if not isinstance(schema_path, str):
        raise TypeError("schema_path must be a string")

    if not xml_content.strip():
        raise ValueError("xml_content cannot be empty")

    if not schema_path.strip():
        raise ValueError("schema_path cannot be empty")

    try:
        # Parse XSD schema
        with open(schema_path, "rb") as f:
            schema_doc = lxml_etree.parse(f)
            schema = lxml_etree.XMLSchema(schema_doc)

        # Parse XML
        doc = lxml_etree.fromstring(xml_content.encode("utf-8"))

        # Validate and collect errors
        is_valid = schema.validate(doc)

        # Extract errors and warnings from log
        errors = []
        warnings = []

        if not is_valid:
            for error in schema.error_log:
                error_msg = f"Line {error.line}: {error.message}"
                if error.level_name == "ERROR":
                    errors.append(error_msg)
                elif error.level_name == "WARNING":
                    warnings.append(error_msg)
                else:
                    errors.append(error_msg)

        return {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "error_count": len(errors),
            "warning_count": len(warnings),
        }

    except FileNotFoundError:
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    except lxml_etree.XMLSchemaParseError as e:
        raise ValueError(f"Invalid XSD schema: {e}")
    except lxml_etree.XMLSyntaxError as e:
        raise ValueError(f"Invalid XML syntax: {e}")
