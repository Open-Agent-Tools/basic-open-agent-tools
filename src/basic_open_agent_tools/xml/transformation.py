"""XML transformation and conversion functions for AI agents.

This module provides functions for converting between XML and other formats,
formatting XML, and transforming XML documents.
"""

import json
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


def _element_to_json_dict(element: ET.Element) -> dict:
    """Convert XML Element to JSON-friendly dictionary.

    Args:
        element: XML Element to convert

    Returns:
        Dictionary suitable for JSON serialization
    """
    result: dict[str, object] = {"_tag": element.tag}

    # Add attributes
    if element.attrib:
        result["_attributes"] = dict(element.attrib)

    # Add text content
    if element.text and element.text.strip():
        result["_text"] = element.text.strip()

    # Add children
    for child in element:
        child_dict = _element_to_json_dict(child)
        tag = child.tag

        # Handle multiple children with same tag
        if tag in result:
            # Convert to list if not already
            existing = result[tag]
            if not isinstance(existing, list):
                result[tag] = [existing]
            # Type cast to list before appending
            children_list = result[tag]
            if not isinstance(children_list, list):
                raise TypeError(
                    f"Expected list for tag '{tag}', got {type(children_list).__name__}"
                )
            children_list.append(child_dict)
        else:
            result[tag] = child_dict

    return result


@strands_tool
def xml_to_json(xml_content: str) -> str:
    """Convert XML to JSON format preserving structure.

    This function converts XML content to JSON while preserving the
    document structure. Element tags become keys, attributes are stored
    with '_attributes' key, and text content with '_text' key.

    Args:
        xml_content: XML content as string to convert

    Returns:
        JSON string representation of XML structure

    Raises:
        ValueError: If XML is malformed
        TypeError: If xml_content is not a string

    Example:
        >>> xml = '<root><item id="1">test</item></root>'
        >>> json_str = xml_to_json(xml)
        >>> '_tag' in json_str and 'root' in json_str
        True
    """
    if not isinstance(xml_content, str):
        raise TypeError("xml_content must be a string")

    if not xml_content.strip():
        raise ValueError("xml_content cannot be empty")

    try:
        # Parse XML
        if HAS_DEFUSEDXML:
            root = defused_fromstring(xml_content)
        else:
            root = ET.fromstring(xml_content)

        # Convert to JSON-friendly dict
        result = _element_to_json_dict(root)

        # Serialize to JSON with indentation
        return json.dumps(result, indent=2, ensure_ascii=False)

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML content: {e}")


@strands_tool
def json_to_xml(json_content: str, root_tag: str) -> str:
    """Convert JSON to XML format.

    This function converts JSON content to XML. The JSON structure should
    contain dictionaries where keys become element tags. Special keys
    '_attributes', '_text', and '_tag' control element properties.

    Args:
        json_content: JSON content as string to convert
        root_tag: Tag name for root element

    Returns:
        Formatted XML string with declaration

    Raises:
        ValueError: If JSON is malformed
        TypeError: If parameters are not strings

    Example:
        >>> json_str = '{"item": {"_text": "test", "_attributes": {"id": "1"}}}'
        >>> xml = json_to_xml(json_str, "root")
        >>> '<root>' in xml and '<item' in xml
        True
    """
    if not isinstance(json_content, str):
        raise TypeError("json_content must be a string")

    if not isinstance(root_tag, str):
        raise TypeError("root_tag must be a string")

    if not json_content.strip():
        raise ValueError("json_content cannot be empty")

    if not root_tag.strip():
        raise ValueError("root_tag cannot be empty")

    try:
        # Parse JSON
        data = json.loads(json_content)

        if not isinstance(data, dict):
            raise ValueError("JSON content must be an object/dictionary")

        # Create root element
        root = ET.Element(root_tag)

        # Convert dict to XML elements
        def dict_to_element(parent: ET.Element, data: dict) -> None:
            """Recursively convert dict to XML elements."""
            for key, value in data.items():
                # Skip special keys
                if key in ("_tag", "_attributes", "_text"):
                    continue

                if isinstance(value, dict):
                    # Handle single element
                    attrs = value.get("_attributes", {})
                    child = ET.SubElement(parent, key, attrs)

                    if "_text" in value:
                        child.text = str(value["_text"])

                    dict_to_element(child, value)

                elif isinstance(value, list):
                    # Handle multiple elements with same tag
                    for item in value:
                        if isinstance(item, dict):
                            attrs = item.get("_attributes", {})
                            child = ET.SubElement(parent, key, attrs)

                            if "_text" in item:
                                child.text = str(item["_text"])

                            dict_to_element(child, item)
                        else:
                            # Simple value
                            child = ET.SubElement(parent, key)
                            child.text = str(item)
                else:
                    # Simple value
                    child = ET.SubElement(parent, key)
                    child.text = str(value)

        dict_to_element(root, data)

        # Format with indentation
        ET.indent(root, space="  ")

        # Convert to string with XML declaration
        xml_bytes = ET.tostring(root, encoding="UTF-8", xml_declaration=True)
        decoded_str = xml_bytes.decode("UTF-8")
        if not isinstance(decoded_str, str):
            raise TypeError(
                f"XML decoding produced {type(decoded_str).__name__}, expected str"
            )
        return decoded_str

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON content: {e}")


@strands_tool
def format_xml(xml_content: str, indent_size: int) -> str:
    """Format XML with proper indentation and line breaks.

    This function reformats XML content with consistent indentation
    and line breaks for improved readability.

    Args:
        xml_content: XML content as string to format
        indent_size: Number of spaces per indentation level

    Returns:
        Formatted XML string with proper indentation

    Raises:
        ValueError: If XML is malformed or indent_size is invalid
        TypeError: If parameters are wrong type

    Example:
        >>> xml = '<root><item>test</item></root>'
        >>> formatted = format_xml(xml, 2)
        >>> '  <item>' in formatted
        True
    """
    if not isinstance(xml_content, str):
        raise TypeError("xml_content must be a string")

    if not isinstance(indent_size, int):
        raise TypeError("indent_size must be an integer")

    if not xml_content.strip():
        raise ValueError("xml_content cannot be empty")

    if indent_size < 0:
        raise ValueError("indent_size must be non-negative")

    try:
        # Parse XML
        if HAS_DEFUSEDXML:
            root = defused_fromstring(xml_content)
        else:
            root = ET.fromstring(xml_content)

        # Format with indentation
        indent_str = " " * indent_size
        ET.indent(root, space=indent_str)

        # Convert to string
        xml_bytes_result = ET.tostring(root, encoding="UTF-8", xml_declaration=True)
        decoded_str = xml_bytes_result.decode("UTF-8")
        if not isinstance(decoded_str, str):
            raise TypeError(
                f"XML decoding produced {type(decoded_str).__name__}, expected str"
            )
        return decoded_str

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML content: {e}")


@strands_tool
def strip_xml_namespaces(xml_content: str) -> str:
    """Remove namespace declarations and prefixes from XML.

    This function removes all XML namespace declarations and prefixes,
    simplifying the XML structure for processing when namespaces are
    not needed.

    Args:
        xml_content: XML content as string

    Returns:
        XML string with namespaces removed

    Raises:
        ValueError: If XML is malformed
        TypeError: If xml_content is not a string

    Example:
        >>> xml = '<ns:root xmlns:ns="http://example.com"><ns:item/></ns:root>'
        >>> clean = strip_xml_namespaces(xml)
        >>> 'ns:' not in clean and 'xmlns' not in clean
        True
    """
    if not isinstance(xml_content, str):
        raise TypeError("xml_content must be a string")

    if not xml_content.strip():
        raise ValueError("xml_content cannot be empty")

    try:
        # Parse XML
        if HAS_DEFUSEDXML:
            root = defused_fromstring(xml_content)
        else:
            root = ET.fromstring(xml_content)

        # Strip namespaces from all elements
        def strip_ns(element: ET.Element) -> None:
            """Remove namespace from element and descendants."""
            # Remove namespace from tag
            if "}" in element.tag:
                element.tag = element.tag.split("}", 1)[1]

            # Remove xmlns attributes
            attribs_to_remove = []
            for key in element.attrib:
                if key.startswith("{") or key.startswith("xmlns"):
                    attribs_to_remove.append(key)

            for key in attribs_to_remove:
                del element.attrib[key]

            # Process children
            for child in element:
                strip_ns(child)

        strip_ns(root)

        # Format and return
        ET.indent(root, space="  ")
        xml_bytes_result = ET.tostring(root, encoding="UTF-8", xml_declaration=True)
        decoded_str = xml_bytes_result.decode("UTF-8")
        if not isinstance(decoded_str, str):
            raise TypeError(
                f"XML decoding produced {type(decoded_str).__name__}, expected str"
            )
        return decoded_str

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML content: {e}")


@strands_tool
def transform_xml_with_xslt(xml_content: str, xslt_path: str) -> str:
    """Apply XSLT transformation to XML.

    This function requires lxml to be installed. It applies an XSLT
    stylesheet to transform XML content.

    Args:
        xml_content: XML content as string to transform
        xslt_path: Path to XSLT stylesheet file

    Returns:
        Transformed XML as string

    Raises:
        ValueError: If XML or XSLT has errors
        TypeError: If parameters are not strings
        ImportError: If lxml is not installed
        FileNotFoundError: If XSLT file not found

    Example:
        >>> xml = '<root><item>test</item></root>'
        >>> # Requires lxml installed
        >>> result = transform_xml_with_xslt(xml, "/path/to/transform.xslt")  # doctest: +SKIP
        >>> isinstance(result, str)  # doctest: +SKIP
        True
    """
    if not HAS_LXML:
        raise ImportError(
            "lxml is required for XSLT transformations. "
            "Install with: pip install basic-open-agent-tools[xml]"
        )

    if not isinstance(xml_content, str):
        raise TypeError("xml_content must be a string")

    if not isinstance(xslt_path, str):
        raise TypeError("xslt_path must be a string")

    if not xml_content.strip():
        raise ValueError("xml_content cannot be empty")

    if not xslt_path.strip():
        raise ValueError("xslt_path cannot be empty")

    try:
        # Parse XSLT stylesheet
        with open(xslt_path, "rb") as f:
            xslt_doc = lxml_etree.parse(f)
            transform = lxml_etree.XSLT(xslt_doc)

        # Parse XML
        doc = lxml_etree.fromstring(xml_content.encode("utf-8"))

        # Apply transformation
        result_tree = transform(doc)

        # Convert result to string
        result_str = str(result_tree)
        if not isinstance(result_str, str):
            raise TypeError(
                f"XSLT transformation produced {type(result_str).__name__}, expected str"
            )
        return result_str

    except FileNotFoundError:
        raise FileNotFoundError(f"XSLT file not found: {xslt_path}")
    except lxml_etree.XSLTParseError as e:
        raise ValueError(f"Invalid XSLT stylesheet: {e}")
    except lxml_etree.XMLSyntaxError as e:
        raise ValueError(f"Invalid XML syntax: {e}")


@strands_tool
def extract_xml_to_csv(xml_content: str, element_tag: str) -> list[dict]:
    """Extract repeating elements to CSV-style list of dicts.

    This function extracts all elements with a specific tag and converts
    them to a list of dictionaries suitable for CSV export. Each element's
    attributes and text content become dictionary fields.

    Args:
        xml_content: XML content as string
        element_tag: Tag name of elements to extract

    Returns:
        List of dictionaries, one per matching element, with fields:
        - Attribute names as keys with attribute values
        - '_text' key with element text content if present

    Raises:
        ValueError: If XML is malformed
        TypeError: If parameters are not strings

    Example:
        >>> xml = '''<root>
        ...   <person name="Alice" age="30">Engineer</person>
        ...   <person name="Bob" age="25">Designer</person>
        ... </root>'''
        >>> result = extract_xml_to_csv(xml, "person")
        >>> len(result)
        2
        >>> result[0]['name']
        'Alice'
        >>> result[0]['_text']
        'Engineer'
    """
    if not isinstance(xml_content, str):
        raise TypeError("xml_content must be a string")

    if not isinstance(element_tag, str):
        raise TypeError("element_tag must be a string")

    if not xml_content.strip():
        raise ValueError("xml_content cannot be empty")

    if not element_tag.strip():
        raise ValueError("element_tag cannot be empty")

    try:
        # Parse XML
        if HAS_DEFUSEDXML:
            root = defused_fromstring(xml_content)
        else:
            root = ET.fromstring(xml_content)

        # Find all matching elements
        elements = root.findall(f".//{element_tag}")

        # Convert to list of dicts
        result = []
        for element in elements:
            row = dict(element.attrib)

            # Add text content if present
            if element.text and element.text.strip():
                row["_text"] = element.text.strip()

            result.append(row)

        return result

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML content: {e}")
