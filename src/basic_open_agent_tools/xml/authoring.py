"""XML authoring and creation functions for AI agents.

This module provides functions for creating and writing XML documents
from simple dictionary structures.
"""

import os
import xml.etree.ElementTree as ET
from typing import Optional

from ..decorators import strands_tool


def _dict_to_element(data: dict, parent: Optional[ET.Element] = None) -> ET.Element:
    """Convert dictionary structure to XML Element.

    Args:
        data: Dictionary with 'tag', 'attributes', 'text', and 'children' keys
        parent: Parent element to attach to (optional)

    Returns:
        Created XML Element
    """
    if parent is None:
        element = ET.Element(data["tag"], data.get("attributes", {}))
    else:
        element = ET.SubElement(parent, data["tag"], data.get("attributes", {}))

    # Set text content
    text = data.get("text", "")
    if text:
        element.text = text

    # Add children recursively
    for child_data in data.get("children", []):
        _dict_to_element(child_data, element)

    return element


@strands_tool
def create_xml_from_dict(data: dict, root_tag: str, encoding: str, indent: bool) -> str:
    """Create XML string from nested dictionary structure.

    This function converts a simple nested dictionary representation
    into a formatted XML string with proper declaration and encoding.

    Args:
        data: Nested dict with 'tag', 'attributes', 'text', 'children' keys
        root_tag: Root element tag name
        encoding: XML encoding (e.g., 'UTF-8', 'ISO-8859-1')
        indent: Whether to format with indentation for readability

    Returns:
        Formatted XML string with declaration

    Raises:
        TypeError: If data is not a dict or required fields are wrong type
        ValueError: If required fields are missing or encoding is invalid

    Example:
        >>> data = {
        ...     "tag": "books",
        ...     "attributes": {},
        ...     "text": "",
        ...     "children": [{
        ...         "tag": "book",
        ...         "attributes": {"isbn": "123"},
        ...         "text": "Python Guide",
        ...         "children": []
        ...     }]
        ... }
        >>> xml_str = create_xml_from_dict(data, "books", "UTF-8", True)
        >>> '<?xml version' in xml_str
        True
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")

    if not isinstance(root_tag, str):
        raise TypeError("root_tag must be a string")

    if not isinstance(encoding, str):
        raise TypeError("encoding must be a string")

    if not isinstance(indent, bool):
        raise TypeError("indent must be a boolean")

    if not root_tag.strip():
        raise ValueError("root_tag cannot be empty")

    if not encoding.strip():
        raise ValueError("encoding cannot be empty")

    # Validate data structure
    if "tag" not in data:
        raise ValueError("data must contain 'tag' key")

    # Validate data tag matches root_tag
    if data["tag"] != root_tag:
        raise ValueError(f"data tag '{data['tag']}' must match root_tag '{root_tag}'")

    # Create root element
    root = _dict_to_element(data)

    # Format with indentation if requested
    if indent:
        ET.indent(root, space="  ")

    # Create tree and convert to string
    ET.ElementTree(root)

    # Use ET.tostring for proper encoding support
    xml_bytes_result = ET.tostring(root, encoding=encoding, xml_declaration=True)
    decoded_str = xml_bytes_result.decode(encoding)
    if not isinstance(decoded_str, str):
        raise TypeError(
            f"XML decoding produced {type(decoded_str).__name__}, expected str"
        )
    return decoded_str


@strands_tool
def write_xml_file(
    data: dict, file_path: str, root_tag: str, encoding: str, skip_confirm: bool
) -> str:
    """Write XML data to file from nested dict structure.

    This function creates an XML file from a dictionary representation,
    with optional confirmation before overwriting existing files.

    Args:
        data: Nested dict with 'tag', 'attributes', 'text', 'children'
        file_path: Path where XML file will be written
        root_tag: Root element tag name
        encoding: XML encoding (e.g., 'UTF-8')
        skip_confirm: If False, raises error if file exists; if True, overwrites

    Returns:
        Success message with file path and size

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If data structure is invalid or file exists (when skip_confirm=False)
        PermissionError: If file location is not writable

    Example:
        >>> data = {"tag": "root", "attributes": {}, "text": "test", "children": []}
        >>> result = write_xml_file(data, "/tmp/test.xml", "root", "UTF-8", False)
        >>> "Created XML file" in result
        True
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(root_tag, str):
        raise TypeError("root_tag must be a string")

    if not isinstance(encoding, str):
        raise TypeError("encoding must be a string")

    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if not file_path.strip():
        raise ValueError("file_path cannot be empty")

    # Check if file exists and handle based on skip_confirm
    if os.path.exists(file_path) and not skip_confirm:
        raise ValueError(
            f"File already exists: {file_path}. Set skip_confirm=True to overwrite."
        )

    # Check parent directory is writable
    parent_dir = os.path.dirname(file_path) or "."
    if not os.path.exists(parent_dir):
        raise FileNotFoundError(f"Parent directory does not exist: {parent_dir}")

    if not os.access(parent_dir, os.W_OK):
        raise PermissionError(f"Cannot write to directory: {parent_dir}")

    # Generate XML content with indentation
    xml_content = create_xml_from_dict(data, root_tag, encoding, indent=True)

    # Write to file
    with open(file_path, "w", encoding=encoding) as f:
        f.write(xml_content)

    # Get file size for feedback
    file_size = os.path.getsize(file_path)

    return f"Created XML file {file_path} ({file_size} bytes)"


@strands_tool
def create_xml_element(tag: str, text: str, attributes: dict[str, str]) -> dict:
    """Create a single XML element as dict structure.

    This function creates a simple dictionary representation of an XML
    element that can be used with other authoring functions.

    Args:
        tag: Element tag name
        text: Element text content
        attributes: Dictionary of attribute name-value pairs

    Returns:
        Dictionary with 'tag', 'attributes', 'text', and 'children' keys

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If tag is empty

    Example:
        >>> book = create_xml_element(
        ...     "book",
        ...     "Python Guide",
        ...     {"isbn": "123-456", "year": "2024"}
        ... )
        >>> book['tag']
        'book'
        >>> book['attributes']['isbn']
        '123-456'
    """
    if not isinstance(tag, str):
        raise TypeError("tag must be a string")

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    if not isinstance(attributes, dict):
        raise TypeError("attributes must be a dictionary")

    if not tag.strip():
        raise ValueError("tag cannot be empty")

    # Validate attributes are all strings
    for key, value in attributes.items():
        if not isinstance(key, str):
            raise TypeError(f"Attribute key must be string, got {type(key)}")
        if not isinstance(value, str):
            raise TypeError(f"Attribute value must be string, got {type(value)}")

    return {
        "tag": tag,
        "attributes": attributes,
        "text": text,
        "children": [],
    }


@strands_tool
def add_xml_child_element(parent: dict, child: dict) -> dict:
    """Add child element to parent element structure.

    This function adds a child element to a parent's children list
    and returns the modified parent structure.

    Args:
        parent: Parent element dict with 'children' key
        child: Child element dict to add

    Returns:
        Updated parent dict with child added to children list

    Raises:
        TypeError: If parent or child are not dicts
        ValueError: If parent missing required keys

    Example:
        >>> parent = create_xml_element("books", "", {})
        >>> child = create_xml_element("book", "Title", {"isbn": "123"})
        >>> updated = add_xml_child_element(parent, child)
        >>> len(updated['children'])
        1
    """
    if not isinstance(parent, dict):
        raise TypeError("parent must be a dictionary")

    if not isinstance(child, dict):
        raise TypeError("child must be a dictionary")

    # Validate parent structure
    if "tag" not in parent:
        raise ValueError("parent must contain 'tag' key")

    if "children" not in parent:
        raise ValueError("parent must contain 'children' key")

    # Validate child structure
    if "tag" not in child:
        raise ValueError("child must contain 'tag' key")

    # Add child to parent's children list
    parent["children"].append(child)

    return parent


@strands_tool
def set_xml_element_attribute(
    element: dict, attribute_name: str, attribute_value: str
) -> dict:
    """Set or update attribute on XML element.

    This function sets or updates an attribute value on an XML element
    dictionary structure.

    Args:
        element: Element dict with 'attributes' key
        attribute_name: Name of attribute to set
        attribute_value: Value to set for attribute

    Returns:
        Updated element dict with attribute set

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If element missing required keys or attribute_name is empty

    Example:
        >>> elem = create_xml_element("book", "Title", {})
        >>> updated = set_xml_element_attribute(elem, "isbn", "123-456")
        >>> updated['attributes']['isbn']
        '123-456'
    """
    if not isinstance(element, dict):
        raise TypeError("element must be a dictionary")

    if not isinstance(attribute_name, str):
        raise TypeError("attribute_name must be a string")

    if not isinstance(attribute_value, str):
        raise TypeError("attribute_value must be a string")

    if not attribute_name.strip():
        raise ValueError("attribute_name cannot be empty")

    # Validate element structure
    if "tag" not in element:
        raise ValueError("element must contain 'tag' key")

    if "attributes" not in element:
        raise ValueError("element must contain 'attributes' key")

    # Set attribute
    element["attributes"][attribute_name] = attribute_value

    return element


@strands_tool
def build_simple_xml(root_tag: str, elements: list[dict]) -> str:
    """Build simple flat XML document from list of elements.

    This function creates a basic XML document with a root element
    containing a flat list of child elements. All elements become
    direct children of the root.

    Args:
        root_tag: Tag name for root element
        elements: List of element dicts to add as children

    Returns:
        Formatted XML string with UTF-8 encoding

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If root_tag is empty

    Example:
        >>> items = [
        ...     create_xml_element("item", "First", {"id": "1"}),
        ...     create_xml_element("item", "Second", {"id": "2"})
        ... ]
        >>> xml = build_simple_xml("items", items)
        >>> '<items>' in xml
        True
    """
    if not isinstance(root_tag, str):
        raise TypeError("root_tag must be a string")

    if not isinstance(elements, list):
        raise TypeError("elements must be a list")

    if not root_tag.strip():
        raise ValueError("root_tag cannot be empty")

    # Validate all elements are dicts with required keys
    for i, elem in enumerate(elements):
        if not isinstance(elem, dict):
            raise TypeError(f"Element at index {i} must be a dictionary")
        if "tag" not in elem:
            raise ValueError(f"Element at index {i} missing 'tag' key")

    # Create root element with children
    root_data = {
        "tag": root_tag,
        "attributes": {},
        "text": "",
        "children": elements,
    }

    return create_xml_from_dict(root_data, root_tag, "UTF-8", indent=True)


@strands_tool
def xml_from_csv(csv_data: list[dict], root_tag: str, row_tag: str) -> str:
    """Convert CSV data (list of dicts) to XML format.

    This function converts tabular data represented as a list of dictionaries
    into XML format, where each row becomes an element with fields as attributes.

    Args:
        csv_data: List of dicts representing rows (e.g., from CSV)
        root_tag: Tag name for root element
        row_tag: Tag name for each row element

    Returns:
        Formatted XML string with UTF-8 encoding

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If root_tag or row_tag is empty

    Example:
        >>> data = [
        ...     {"name": "Alice", "age": "30"},
        ...     {"name": "Bob", "age": "25"}
        ... ]
        >>> xml = xml_from_csv(data, "people", "person")
        >>> '<people>' in xml and '<person' in xml
        True
    """
    if not isinstance(csv_data, list):
        raise TypeError("csv_data must be a list")

    if not isinstance(root_tag, str):
        raise TypeError("root_tag must be a string")

    if not isinstance(row_tag, str):
        raise TypeError("row_tag must be a string")

    if not root_tag.strip():
        raise ValueError("root_tag cannot be empty")

    if not row_tag.strip():
        raise ValueError("row_tag cannot be empty")

    # Validate csv_data items are dicts
    for i, row in enumerate(csv_data):
        if not isinstance(row, dict):
            raise TypeError(f"Row at index {i} must be a dictionary")

        # Validate all keys and values are strings
        for key, value in row.items():
            if not isinstance(key, str):
                raise TypeError(f"Row {i} key must be string, got {type(key)}")
            if not isinstance(value, str):
                raise TypeError(f"Row {i} value must be string, got {type(value)}")

    # Convert each row to an element with attributes
    elements = []
    for row in csv_data:
        element = create_xml_element(row_tag, "", row)
        elements.append(element)

    return build_simple_xml(root_tag, elements)
