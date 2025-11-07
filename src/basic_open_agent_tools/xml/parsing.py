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


@strands_tool
def get_xml_structure(file_path: str, max_depth: int) -> dict[str, str]:
    """Get XML structure/hierarchy without loading element content.

    This function efficiently inspects XML structure by mapping paths
    to element types without loading text content, ideal for understanding
    large XML documents without token overhead.

    Args:
        file_path: Path to XML file
        max_depth: Maximum depth to traverse (0 for unlimited)

    Returns:
        Dictionary mapping element paths to types (e.g., {"root": "element",
        "root.child": "element", "root.child.@attr": "attribute"})

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is too large or XML is malformed
        PermissionError: If file cannot be read
        TypeError: If parameters are wrong type

    Example:
        >>> structure = get_xml_structure("/data/config.xml", 3)
        >>> structure
        {'root': 'element', 'root.settings': 'element', 'root.settings.item': 'element'}
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(max_depth, int) or max_depth < 0:
        raise TypeError("max_depth must be a non-negative integer")

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

        structure: dict[str, str] = {}

        def traverse(element: ET.Element, path: str, depth: int) -> None:
            if max_depth > 0 and depth > max_depth:
                return

            # Add element
            structure[path] = "element"

            # Add attributes
            for attr_name in element.attrib:
                structure[f"{path}.@{attr_name}"] = "attribute"

            # Traverse children
            for child in element:
                # Remove namespace from tag if present
                tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                child_path = f"{path}.{tag}"
                traverse(child, child_path, depth + 1)

        # Start traversal
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        traverse(root, root_tag, 1)

        return structure

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML in file {file_path}: {e}")


@strands_tool
def count_xml_elements(file_path: str, tag_name: str) -> int:
    """Count XML elements by tag name without loading content.

    This function efficiently counts elements without loading text content,
    ideal for getting counts in large XML documents.

    Args:
        file_path: Path to XML file
        tag_name: Tag name to count (empty string to count all elements)

    Returns:
        Count of matching elements

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is too large or XML is malformed
        PermissionError: If file cannot be read
        TypeError: If parameters are wrong type

    Example:
        >>> count = count_xml_elements("/data/items.xml", "item")
        >>> count
        1523
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(tag_name, str):
        raise TypeError("tag_name must be a string")

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

        # Count elements
        if not tag_name:
            # Count all elements
            count = 1  # Root
            for _ in root.iter():
                count += 1
            return count - 1  # Subtract root as iter() includes it
        else:
            # Count specific tag
            count = 0
            for element in root.iter():
                element_tag = (
                    element.tag.split("}")[-1] if "}" in element.tag else element.tag
                )
                if element_tag == tag_name:
                    count += 1
            return count

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML in file {file_path}: {e}")


@strands_tool
def get_xml_element_at_path(file_path: str, xpath: str) -> dict:
    """Extract specific XML element by XPath without loading entire document.

    This function uses XPath to extract a single element, avoiding
    loading the full XML structure into context.

    Args:
        file_path: Path to XML file
        xpath: XPath expression (e.g., "./settings/item[@id='1']")

    Returns:
        Dictionary with element structure (tag, attributes, text, children)

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is too large, XML is malformed, or XPath invalid
        PermissionError: If file cannot be read
        TypeError: If parameters are wrong type

    Example:
        >>> element = get_xml_element_at_path("/data/config.xml", ".//setting[@name='timeout']")
        >>> element['text']
        '30'
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(xpath, str):
        raise TypeError("xpath must be a string")

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

        # Find element using XPath
        element = root.find(xpath)

        if element is None:
            raise ValueError(f"No element found at XPath: {xpath}")

        # Convert to dict
        return _element_to_dict(element)

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML in file {file_path}: {e}")


@strands_tool
def get_xml_attributes(file_path: str, tag_name: str) -> list[str]:
    """List all unique attributes for elements of specific tag type.

    This function efficiently collects attribute names without loading
    element content, useful for schema discovery.

    Args:
        file_path: Path to XML file
        tag_name: Tag name to inspect for attributes

    Returns:
        List of unique attribute names found on elements with this tag

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is too large or XML is malformed
        PermissionError: If file cannot be read
        TypeError: If parameters are wrong type

    Example:
        >>> attrs = get_xml_attributes("/data/items.xml", "item")
        >>> attrs
        ['id', 'name', 'category', 'price']
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(tag_name, str):
        raise TypeError("tag_name must be a string")

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

        # Collect unique attributes
        attributes = set()
        for element in root.iter():
            element_tag = (
                element.tag.split("}")[-1] if "}" in element.tag else element.tag
            )
            if element_tag == tag_name:
                attributes.update(element.attrib.keys())

        return sorted(attributes)

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML in file {file_path}: {e}")


@strands_tool
def search_xml_tags(file_path: str, tag_pattern: str) -> list[str]:
    """Find all XML paths containing tags matching pattern.

    This function searches for tags by substring match (case-insensitive)
    and returns full paths to matching elements.

    Args:
        file_path: Path to XML file
        tag_pattern: Pattern to search for in tag names (case-insensitive)

    Returns:
        List of paths to elements with matching tags

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is too large or XML is malformed
        PermissionError: If file cannot be read
        TypeError: If parameters are wrong type

    Example:
        >>> paths = search_xml_tags("/data/config.xml", "setting")
        >>> paths
        ['root.settings.setting', 'root.advanced.setting']
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(tag_pattern, str):
        raise TypeError("tag_pattern must be a string")

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

        pattern_lower = tag_pattern.lower()
        matching_paths: list[str] = []

        def traverse(element: ET.Element, path: str) -> None:
            # Check if tag matches pattern
            element_tag = (
                element.tag.split("}")[-1] if "}" in element.tag else element.tag
            )
            if pattern_lower in element_tag.lower():
                matching_paths.append(path)

            # Traverse children
            for child in element:
                child_tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                child_path = f"{path}.{child_tag}"
                traverse(child, child_path)

        # Start traversal
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        traverse(root, root_tag)

        return matching_paths

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML in file {file_path}: {e}")


@strands_tool
def select_xml_elements(file_path: str, tag_name: str) -> list[dict]:
    """Get only specific elements by tag name, discarding others.

    This function extracts only elements matching the tag name,
    avoiding loading the entire XML structure.

    Args:
        file_path: Path to XML file
        tag_name: Tag name of elements to extract

    Returns:
        List of dictionaries representing matching elements

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is too large or XML is malformed
        PermissionError: If file cannot be read
        TypeError: If parameters are wrong type

    Example:
        >>> elements = select_xml_elements("/data/items.xml", "item")
        >>> elements[0]
        {'tag': 'item', 'attributes': {'id': '1'}, 'text': 'Product 1', 'children': []}
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(tag_name, str):
        raise TypeError("tag_name must be a string")

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

        # Extract matching elements
        result: list[dict] = []
        for element in root.iter():
            element_tag = (
                element.tag.split("}")[-1] if "}" in element.tag else element.tag
            )
            if element_tag == tag_name:
                result.append(_element_to_dict(element))

        return result

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML in file {file_path}: {e}")


@strands_tool
def filter_xml_elements(
    file_path: str, tag_name: str, attribute: str, value: str, operator: str
) -> list[dict]:
    """Filter XML elements by attribute/text criteria.

    This function filters elements based on criteria, returning only
    matching elements without loading the full XML structure.

    Args:
        file_path: Path to XML file
        tag_name: Tag name of elements to filter
        attribute: Attribute name to filter on (empty string to filter by text content)
        value: Value to compare against
        operator: Comparison operator (equals, contains, startswith, endswith,
                 greater_than, less_than)

    Returns:
        List of dictionaries representing matching elements

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is too large, XML is malformed, or invalid operator
        PermissionError: If file cannot be read
        TypeError: If parameters are wrong type

    Example:
        >>> elements = filter_xml_elements("/data/items.xml", "item", "category", "electronics", "equals")
        >>> elements[0]
        {'tag': 'item', 'attributes': {'id': '1', 'category': 'electronics'}, ...}
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(tag_name, str):
        raise TypeError("tag_name must be a string")

    if not isinstance(attribute, str):
        raise TypeError("attribute must be a string")

    if not isinstance(value, str):
        raise TypeError("value must be a string")

    if not isinstance(operator, str):
        raise TypeError("operator must be a string")

    valid_operators = [
        "equals",
        "contains",
        "startswith",
        "endswith",
        "greater_than",
        "less_than",
    ]
    if operator not in valid_operators:
        raise ValueError(f"operator must be one of: {valid_operators}")

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

        # Filter elements
        result: list[dict] = []
        for element in root.iter():
            element_tag = (
                element.tag.split("}")[-1] if "}" in element.tag else element.tag
            )
            if element_tag != tag_name:
                continue

            # Get comparison value
            if attribute:
                # Filter by attribute
                compare_value = element.get(attribute, "")
            else:
                # Filter by text content
                compare_value = element.text.strip() if element.text else ""

            # Apply filter
            matches = False
            if operator == "equals":
                matches = compare_value == value
            elif operator == "contains":
                matches = value in compare_value
            elif operator == "startswith":
                matches = compare_value.startswith(value)
            elif operator == "endswith":
                matches = compare_value.endswith(value)
            elif operator == "greater_than":
                try:
                    matches = float(compare_value) > float(value)
                except ValueError:
                    matches = False
            elif operator == "less_than":
                try:
                    matches = float(compare_value) < float(value)
                except ValueError:
                    matches = False

            if matches:
                result.append(_element_to_dict(element))

        return result

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML in file {file_path}: {e}")


@strands_tool
def preview_xml_elements(
    file_path: str, tag_name: str, num_elements: int
) -> list[dict]:
    """Get first N elements of a specific type for preview.

    This function extracts only the first N matching elements,
    ideal for previewing large XML documents.

    Args:
        file_path: Path to XML file
        tag_name: Tag name of elements to preview
        num_elements: Number of elements to return

    Returns:
        List of dictionaries for first N matching elements

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is too large or XML is malformed
        PermissionError: If file cannot be read
        TypeError: If parameters are wrong type

    Example:
        >>> elements = preview_xml_elements("/data/items.xml", "item", 5)
        >>> len(elements)
        5
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(tag_name, str):
        raise TypeError("tag_name must be a string")

    if not isinstance(num_elements, int) or num_elements < 1:
        raise TypeError("num_elements must be a positive integer")

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

        # Extract first N elements
        result: list[dict] = []
        count = 0

        for element in root.iter():
            if count >= num_elements:
                break

            element_tag = (
                element.tag.split("}")[-1] if "}" in element.tag else element.tag
            )
            if element_tag == tag_name:
                result.append(_element_to_dict(element))
                count += 1

        return result

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML in file {file_path}: {e}")


@strands_tool
def slice_xml_elements(
    file_path: str, tag_name: str, start: int, end: int
) -> list[dict]:
    """Get slice of XML elements for pagination (start to end).

    This function extracts a range of elements by tag name,
    ideal for implementing pagination over large XML documents.

    Args:
        file_path: Path to XML file
        tag_name: Tag name of elements to slice
        start: Starting index (0-based, inclusive)
        end: Ending index (0-based, exclusive)

    Returns:
        List of dictionaries for elements in the specified range

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is too large, XML is malformed, or invalid range
        PermissionError: If file cannot be read
        TypeError: If parameters are wrong type

    Example:
        >>> elements = slice_xml_elements("/data/items.xml", "item", 10, 20)
        >>> len(elements)
        10
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(tag_name, str):
        raise TypeError("tag_name must be a string")

    if not isinstance(start, int) or start < 0:
        raise TypeError("start must be a non-negative integer")

    if not isinstance(end, int) or end < start:
        raise TypeError("end must be an integer >= start")

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

        # Extract slice of elements
        result: list[dict] = []
        index = 0

        for element in root.iter():
            element_tag = (
                element.tag.split("}")[-1] if "}" in element.tag else element.tag
            )
            if element_tag == tag_name:
                if start <= index < end:
                    result.append(_element_to_dict(element))
                index += 1

                if index >= end:
                    break

        return result

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML in file {file_path}: {e}")


@strands_tool
def get_xml_namespace_info(file_path: str) -> dict[str, str]:
    """List all XML namespaces without loading element content.

    This function efficiently extracts namespace information
    from the XML document for schema understanding.

    Args:
        file_path: Path to XML file

    Returns:
        Dictionary mapping namespace prefixes to URIs

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is too large or XML is malformed
        PermissionError: If file cannot be read
        TypeError: If parameters are wrong type

    Example:
        >>> namespaces = get_xml_namespace_info("/data/config.xml")
        >>> namespaces
        {'xsi': 'http://www.w3.org/2001/XMLSchema-instance', 'app': 'http://example.com/app'}
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

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

        # Collect namespaces
        namespaces: dict[str, str] = {}

        # Get namespaces from root
        for prefix, uri in root.attrib.items():
            if prefix.startswith("{http://www.w3.org/2000/xmlns/}"):
                ns_prefix = prefix.split("}")[-1]
                namespaces[ns_prefix] = uri
            elif prefix == "xmlns":
                namespaces["default"] = uri

        # Scan all elements for namespace URIs in tags
        for element in root.iter():
            if "}" in element.tag:
                uri = element.tag.split("}")[0][1:]  # Remove leading {
                if uri and uri not in namespaces.values():
                    namespaces[f"ns{len(namespaces)}"] = uri

        return namespaces

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML in file {file_path}: {e}")


@strands_tool
def get_xml_element_stats(file_path: str, tag_name: str) -> dict[str, str]:
    """Get statistics for XML element type without loading content.

    This function efficiently computes statistics about elements
    with a specific tag name.

    Args:
        file_path: Path to XML file
        tag_name: Tag name to analyze

    Returns:
        Dictionary with statistics: count, unique_attributes, max_depth,
        has_text_content, has_children

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is too large or XML is malformed
        PermissionError: If file cannot be read
        TypeError: If parameters are wrong type

    Example:
        >>> stats = get_xml_element_stats("/data/items.xml", "item")
        >>> stats
        {'count': '1523', 'unique_attributes': '4', 'has_text_content': 'True', ...}
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(tag_name, str):
        raise TypeError("tag_name must be a string")

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

        # Collect statistics
        count = 0
        all_attributes = set()
        has_text = False
        has_children = False
        max_depth_seen = 0

        def get_depth(element: ET.Element) -> int:
            if not list(element):
                return 0
            return 1 + max(get_depth(child) for child in element)

        for element in root.iter():
            element_tag = (
                element.tag.split("}")[-1] if "}" in element.tag else element.tag
            )
            if element_tag == tag_name:
                count += 1
                all_attributes.update(element.attrib.keys())

                if element.text and element.text.strip():
                    has_text = True

                if list(element):
                    has_children = True
                    depth = get_depth(element)
                    max_depth_seen = max(max_depth_seen, depth)

        stats = {
            "count": str(count),
            "unique_attributes": str(len(all_attributes)),
            "attribute_names": ", ".join(sorted(all_attributes)),
            "has_text_content": str(has_text),
            "has_children": str(has_children),
            "max_depth": str(max_depth_seen),
        }

        return stats

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML in file {file_path}: {e}")


@strands_tool
def validate_xml_structure_simple(file_path: str) -> dict[str, str]:
    """Quick validation of XML structure without full parse.

    This function performs basic structural validation
    and returns summary information.

    Args:
        file_path: Path to XML file

    Returns:
        Dictionary with validation results: is_valid, error_message,
        root_tag, element_count, unique_tags_count

    Raises:
        FileNotFoundError: If file does not exist
        PermissionError: If file cannot be read
        TypeError: If parameters are wrong type

    Example:
        >>> result = validate_xml_structure_simple("/data/config.xml")
        >>> result['is_valid']
        'True'
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    # Validate file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"XML file not found: {file_path}")

    # Check read permission
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Cannot read XML file: {file_path}")

    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size > MAX_XML_FILE_SIZE:
        return {
            "is_valid": "False",
            "error_message": f"File too large: {file_size} bytes (max {MAX_XML_FILE_SIZE})",
            "root_tag": "",
            "element_count": "0",
            "unique_tags_count": "0",
        }

    try:
        # Parse XML
        if HAS_DEFUSEDXML:
            tree = defused_parse(file_path)
            root = tree.getroot()
        else:
            tree = ET.parse(file_path)
            root = tree.getroot()

        # Collect statistics
        element_count = sum(1 for _ in root.iter())
        unique_tags = {
            elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            for elem in root.iter()
        }

        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        return {
            "is_valid": "True",
            "error_message": "",
            "root_tag": root_tag,
            "element_count": str(element_count),
            "unique_tags_count": str(len(unique_tags)),
            "unique_tags": ", ".join(sorted(unique_tags)),
        }

    except ET.ParseError as e:
        return {
            "is_valid": "False",
            "error_message": f"Parse error: {e}",
            "root_tag": "",
            "element_count": "0",
            "unique_tags_count": "0",
        }
    except Exception as e:
        return {
            "is_valid": "False",
            "error_message": f"Unexpected error: {e}",
            "root_tag": "",
            "element_count": "0",
            "unique_tags_count": "0",
        }
