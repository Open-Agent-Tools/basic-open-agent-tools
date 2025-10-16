"""XML parsing and reading functions for AI agents.

This module provides safe XML parsing with security protections against
XML bombs, XXE attacks, and other vulnerabilities.
"""

import os
import warnings
import xml.etree.ElementTree as ET

from ..decorators import strands_tool

try:
    from defusedxml.ElementTree import (
        fromstring as defused_fromstring,  # type: ignore[import-untyped]
    )
    from defusedxml.ElementTree import (
        parse as defused_parse,  # type: ignore[import-untyped]
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


# Maximum file size to prevent memory exhaustion (10MB default)
MAX_XML_FILE_SIZE = 10 * 1024 * 1024


def _element_to_dict(element: ET.Element) -> dict:
    """Convert XML Element to dictionary structure.

    Args:
        element: XML Element to convert

    Returns:
        Dictionary with 'tag', 'attributes', 'text', and 'children' keys
    """
    result: dict[str, object] = {
        "tag": element.tag,
        "attributes": dict(element.attrib),
        "text": element.text.strip() if element.text else "",
        "children": [],
    }

    # Convert children recursively
    children: list[dict] = []
    for child in element:
        children.append(_element_to_dict(child))
    result["children"] = children

    return result


@strands_tool
def read_xml_file(file_path: str) -> dict:
    """Read XML file and convert to nested dict structure.

    This function safely parses XML files with protection against XML bombs
    and XXE attacks when defusedxml is installed. The XML structure is
    converted to a simple nested dictionary format that LLMs can easily
    understand and manipulate.

    Args:
        file_path: Path to XML file to read

    Returns:
        Nested dictionary representing XML structure with keys:
        - 'tag': Element tag name (str)
        - 'attributes': Dict of attributes (Dict[str, str])
        - 'text': Element text content (str)
        - 'children': List of child elements (List[dict])

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is too large or XML is malformed
        PermissionError: If file cannot be read

    Example:
        >>> xml_data = read_xml_file("/data/config.xml")
        >>> xml_data['tag']
        'configuration'
        >>> xml_data['children'][0]['tag']
        'setting'
    """
    # Validate file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"XML file not found: {file_path}")

    # Check file size to prevent memory exhaustion
    file_size = os.path.getsize(file_path)
    if file_size > MAX_XML_FILE_SIZE:
        raise ValueError(
            f"XML file too large: {file_size} bytes "
            f"(maximum: {MAX_XML_FILE_SIZE} bytes)"
        )

    # Check read permission
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Cannot read XML file: {file_path}")

    try:
        # Use defusedxml if available for security
        if HAS_DEFUSEDXML:
            tree = defused_parse(file_path)
            root = tree.getroot()
        else:
            tree = ET.parse(file_path)
            root = tree.getroot()

        return _element_to_dict(root)

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML in file {file_path}: {e}")


@strands_tool
def parse_xml_string(xml_content: str) -> dict:
    """Parse XML string into nested dict structure.

    This function safely parses XML strings with protection against XML bombs
    and XXE attacks when defusedxml is installed.

    Args:
        xml_content: XML content as string

    Returns:
        Nested dictionary representing XML structure with keys:
        - 'tag': Element tag name (str)
        - 'attributes': Dict of attributes (Dict[str, str])
        - 'text': Element text content (str)
        - 'children': List of child elements (List[dict])

    Raises:
        ValueError: If XML is malformed or content is too large
        TypeError: If xml_content is not a string

    Example:
        >>> xml_str = '<root><item id="1">Test</item></root>'
        >>> result = parse_xml_string(xml_str)
        >>> result['tag']
        'root'
        >>> result['children'][0]['text']
        'Test'
    """
    if not isinstance(xml_content, str):
        raise TypeError("xml_content must be a string")

    # Check content size
    content_size = len(xml_content.encode("utf-8"))
    if content_size > MAX_XML_FILE_SIZE:
        raise ValueError(
            f"XML content too large: {content_size} bytes "
            f"(maximum: {MAX_XML_FILE_SIZE} bytes)"
        )

    if not xml_content.strip():
        raise ValueError("XML content cannot be empty")

    try:
        # Use defusedxml if available for security
        if HAS_DEFUSEDXML:
            root = defused_fromstring(xml_content)
        else:
            root = ET.fromstring(xml_content)

        return _element_to_dict(root)

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML content: {e}")


@strands_tool
def extract_xml_elements_by_tag(file_path: str, tag_name: str) -> list[dict]:
    """Extract all elements with specific tag name from XML file.

    This function finds all elements matching the specified tag name
    throughout the XML document, regardless of their position in the
    hierarchy.

    Args:
        file_path: Path to XML file to search
        tag_name: Tag name to search for (case-sensitive)

    Returns:
        List of dictionaries, each representing a matching element with:
        - 'tag': Element tag name (str)
        - 'attributes': Dict of attributes (Dict[str, str])
        - 'text': Element text content (str)
        - 'children': List of child elements (List[dict])

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is too large, XML is malformed, or tag_name is invalid
        TypeError: If tag_name is not a string

    Example:
        >>> books = extract_xml_elements_by_tag("/data/catalog.xml", "book")
        >>> len(books)
        5
        >>> books[0]['attributes']['isbn']
        '123-456'
    """
    if not isinstance(tag_name, str):
        raise TypeError("tag_name must be a string")

    if not tag_name.strip():
        raise ValueError("tag_name cannot be empty")

    # Validate file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"XML file not found: {file_path}")

    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size > MAX_XML_FILE_SIZE:
        raise ValueError(
            f"XML file too large: {file_size} bytes "
            f"(maximum: {MAX_XML_FILE_SIZE} bytes)"
        )

    try:
        # Use defusedxml if available
        if HAS_DEFUSEDXML:
            tree = defused_parse(file_path)
            root = tree.getroot()
        else:
            tree = ET.parse(file_path)
            root = tree.getroot()

        # Find all matching elements
        elements = root.findall(f".//{tag_name}")
        return [_element_to_dict(elem) for elem in elements]

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML in file {file_path}: {e}")


@strands_tool
def get_xml_element_text(xml_content: str, xpath: str) -> str:
    """Get text content of element at XPath location.

    This function retrieves the text content of the first element matching
    the given XPath expression. Supports simple XPath expressions only.

    Args:
        xml_content: XML content as string
        xpath: XPath expression to locate element (e.g., "./items/item")

    Returns:
        Text content of the element, or empty string if no text

    Raises:
        ValueError: If XML is malformed or XPath is invalid
        TypeError: If parameters are not strings
        LookupError: If no element found at XPath location

    Example:
        >>> xml = '<root><config><name>MyApp</name></config></root>'
        >>> name = get_xml_element_text(xml, "./config/name")
        >>> name
        'MyApp'
    """
    if not isinstance(xml_content, str):
        raise TypeError("xml_content must be a string")

    if not isinstance(xpath, str):
        raise TypeError("xpath must be a string")

    if not xml_content.strip():
        raise ValueError("xml_content cannot be empty")

    if not xpath.strip():
        raise ValueError("xpath cannot be empty")

    try:
        # Parse XML
        if HAS_DEFUSEDXML:
            root = defused_fromstring(xml_content)
        else:
            root = ET.fromstring(xml_content)

        # Find element
        element = root.find(xpath)
        if element is None:
            raise LookupError(f"No element found at XPath: {xpath}")

        return element.text.strip() if element.text else ""

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML content: {e}")


@strands_tool
def get_xml_element_attribute(xml_content: str, xpath: str, attribute_name: str) -> str:
    """Get attribute value from element at XPath location.

    This function retrieves an attribute value from the first element
    matching the given XPath expression.

    Args:
        xml_content: XML content as string
        xpath: XPath expression to locate element
        attribute_name: Name of attribute to retrieve

    Returns:
        Attribute value as string

    Raises:
        ValueError: If XML is malformed or XPath is invalid
        TypeError: If parameters are not strings
        LookupError: If element not found or attribute doesn't exist
        KeyError: If attribute name not found on element

    Example:
        >>> xml = '<root><book isbn="123">Title</book></root>'
        >>> isbn = get_xml_element_attribute(xml, "./book", "isbn")
        >>> isbn
        '123'
    """
    if not isinstance(xml_content, str):
        raise TypeError("xml_content must be a string")

    if not isinstance(xpath, str):
        raise TypeError("xpath must be a string")

    if not isinstance(attribute_name, str):
        raise TypeError("attribute_name must be a string")

    if not xml_content.strip():
        raise ValueError("xml_content cannot be empty")

    if not xpath.strip():
        raise ValueError("xpath cannot be empty")

    if not attribute_name.strip():
        raise ValueError("attribute_name cannot be empty")

    try:
        # Parse XML
        if HAS_DEFUSEDXML:
            root = defused_fromstring(xml_content)
        else:
            root = ET.fromstring(xml_content)

        # Find element
        element = root.find(xpath)
        if element is None:
            raise LookupError(f"No element found at XPath: {xpath}")

        # Get attribute
        if attribute_name not in element.attrib:
            raise KeyError(
                f"Attribute '{attribute_name}' not found on element at {xpath}"
            )

        return str(element.attrib[attribute_name])

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML content: {e}")


@strands_tool
def list_xml_element_tags(file_path: str) -> list[str]:
    """Get unique list of all element tag names in XML document.

    This function scans the entire XML document and returns a sorted list
    of all unique tag names found. Useful for understanding document structure.

    Args:
        file_path: Path to XML file to analyze

    Returns:
        Sorted list of unique tag names found in document

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is too large or XML is malformed
        PermissionError: If file cannot be read

    Example:
        >>> tags = list_xml_element_tags("/data/document.xml")
        >>> tags
        ['book', 'catalog', 'title', 'author', 'price']
    """
    # Validate file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"XML file not found: {file_path}")

    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size > MAX_XML_FILE_SIZE:
        raise ValueError(
            f"XML file too large: {file_size} bytes "
            f"(maximum: {MAX_XML_FILE_SIZE} bytes)"
        )

    # Check read permission
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Cannot read XML file: {file_path}")

    try:
        # Parse XML
        if HAS_DEFUSEDXML:
            tree = defused_parse(file_path)
            root = tree.getroot()
        else:
            tree = ET.parse(file_path)
            root = tree.getroot()

        # Collect all unique tags
        tags = set()
        tags.add(root.tag)

        for element in root.iter():
            tags.add(element.tag)

        return sorted(tags)

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML in file {file_path}: {e}")
