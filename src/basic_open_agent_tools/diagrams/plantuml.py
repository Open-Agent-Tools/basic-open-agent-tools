"""PlantUML diagram generation and parsing functions for AI agents."""

import os
import re

from ..decorators import strands_tool

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit


@strands_tool
def create_plantuml_class_diagram(
    classes: list[dict[str, str]], relationships: list[dict[str, str]]
) -> str:
    """Generate PlantUML class diagram syntax.


    Args:
        classes: List of class dicts with keys: name, attributes, methods
        relationships: List of relationship dicts with keys: from, to, type

    Returns:
        PlantUML class diagram syntax

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If classes empty or structure invalid

    Example:
        >>> classes = [{'name': 'User', 'attributes': 'name: str', 'methods': 'login()'}]
        >>> rels = [{'from': 'User', 'to': 'Account', 'type': 'has'}]
        >>> diagram = create_plantuml_class_diagram(classes, rels)
        >>> '@startuml' in diagram
        True
    """
    if not isinstance(classes, list):
        raise TypeError("classes must be a list")
    if not isinstance(relationships, list):
        raise TypeError("relationships must be a list")
    if not classes:
        raise ValueError("classes must not be empty")

    for cls in classes:
        if not isinstance(cls, dict):
            raise TypeError("each class must be a dict")
        if "name" not in cls:
            raise ValueError("each class must have a 'name' key")

    lines = ["@startuml", ""]

    # Generate classes
    for cls in classes:
        name = cls.get("name", "Unknown")
        attributes = cls.get("attributes", "")
        methods = cls.get("methods", "")

        lines.append(f"class {name} {{")
        if attributes:
            for attr in attributes.split("\n"):
                if attr.strip():
                    lines.append(f"  {attr.strip()}")
        if attributes and methods:
            lines.append("  --")
        if methods:
            for method in methods.split("\n"):
                if method.strip():
                    lines.append(f"  {method.strip()}")
        lines.append("}")
        lines.append("")

    # Generate relationships
    for rel in relationships:
        if not isinstance(rel, dict):
            raise TypeError("each relationship must be a dict")

        from_class = rel.get("from", "")
        to_class = rel.get("to", "")
        rel_type = rel.get("type", "association")

        if not from_class or not to_class:
            continue

        # Map relationship types to PlantUML syntax
        rel_syntax = {
            "inheritance": "<|--",
            "composition": "*--",
            "aggregation": "o--",
            "association": "--",
            "dependency": "..>",
        }
        syntax = rel_syntax.get(rel_type, "--")
        lines.append(f"{from_class} {syntax} {to_class}")

    lines.append("")
    lines.append("@enduml")

    return "\n".join(lines)


@strands_tool
def create_plantuml_sequence_diagram(
    participants: list[str], interactions: list[dict[str, str]]
) -> str:
    """Generate PlantUML sequence diagram syntax.

    Args:
        participants: List of participant names
        interactions: List of interaction dicts with keys: from, to, message

    Returns:
        PlantUML sequence diagram syntax

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If participants empty

    Example:
        >>> parts = ['User', 'System']
        >>> inters = [{'from': 'User', 'to': 'System', 'message': 'login()'}]
        >>> diagram = create_plantuml_sequence_diagram(parts, inters)
        >>> '@startuml' in diagram
        True
    """
    if not isinstance(participants, list):
        raise TypeError("participants must be a list")
    if not isinstance(interactions, list):
        raise TypeError("interactions must be a list")
    if not participants:
        raise ValueError("participants must not be empty")

    for p in participants:
        if not isinstance(p, str):
            raise TypeError("all participants must be strings")

    lines = ["@startuml", ""]

    # Declare participants
    for participant in participants:
        lines.append(f"participant {participant}")

    lines.append("")

    # Generate interactions
    for inter in interactions:
        if not isinstance(inter, dict):
            raise TypeError("each interaction must be a dict")

        from_p = inter.get("from", "")
        to_p = inter.get("to", "")
        message = inter.get("message", "")
        arrow = inter.get("arrow", "->")  # Optional arrow style

        if from_p and to_p and message:
            lines.append(f"{from_p} {arrow} {to_p}: {message}")

    lines.append("")
    lines.append("@enduml")

    return "\n".join(lines)


@strands_tool
def create_plantuml_activity_diagram(
    activities: list[dict[str, str]], transitions: list[dict[str, str]]
) -> str:
    """Generate PlantUML activity diagram syntax.

    Args:
        activities: List of activity dicts with keys: name, type (start/end/activity)
        transitions: List of transition dicts with keys: from, to, condition

    Returns:
        PlantUML activity diagram syntax

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If activities empty

    Example:
        >>> acts = [{'name': 'Start', 'type': 'start'}, {'name': 'Process', 'type': 'activity'}]
        >>> trans = [{'from': 'Start', 'to': 'Process', 'condition': ''}]
        >>> diagram = create_plantuml_activity_diagram(acts, trans)
        >>> '@startuml' in diagram
        True
    """
    if not isinstance(activities, list):
        raise TypeError("activities must be a list")
    if not isinstance(transitions, list):
        raise TypeError("transitions must be a list")
    if not activities:
        raise ValueError("activities must not be empty")

    lines = ["@startuml", ""]

    # Generate activities
    for act in activities:
        if not isinstance(act, dict):
            raise TypeError("each activity must be a dict")

        name = act.get("name", "Unknown")
        act_type = act.get("type", "activity")

        if act_type == "start":
            lines.append("start")
        elif act_type == "end":
            lines.append("stop")
        elif act_type == "decision":
            lines.append(f"if ({name}) then (yes)")
        else:
            lines.append(f":{name};")

    lines.append("")
    lines.append("@enduml")

    return "\n".join(lines)


@strands_tool
def create_plantuml_component_diagram(
    components: list[dict[str, str]], connections: list[dict[str, str]]
) -> str:
    """Generate PlantUML component diagram syntax.

    Args:
        components: List of component dicts with keys: name, type (component/interface)
        connections: List of connection dicts with keys: from, to

    Returns:
        PlantUML component diagram syntax

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If components empty

    Example:
        >>> comps = [{'name': 'WebApp', 'type': 'component'}]
        >>> conns = [{'from': 'WebApp', 'to': 'Database'}]
        >>> diagram = create_plantuml_component_diagram(comps, conns)
        >>> '@startuml' in diagram
        True
    """
    if not isinstance(components, list):
        raise TypeError("components must be a list")
    if not isinstance(connections, list):
        raise TypeError("connections must be a list")
    if not components:
        raise ValueError("components must not be empty")

    lines = ["@startuml", ""]

    # Generate components
    for comp in components:
        if not isinstance(comp, dict):
            raise TypeError("each component must be a dict")

        name = comp.get("name", "Unknown")
        comp_type = comp.get("type", "component")

        if comp_type == "interface":
            lines.append(f"interface {name}")
        else:
            lines.append(f"component {name}")

    lines.append("")

    # Generate connections
    for conn in connections:
        if not isinstance(conn, dict):
            raise TypeError("each connection must be a dict")

        from_comp = conn.get("from", "")
        to_comp = conn.get("to", "")

        if from_comp and to_comp:
            lines.append(f"{from_comp} --> {to_comp}")

    lines.append("")
    lines.append("@enduml")

    return "\n".join(lines)


@strands_tool
def parse_plantuml_file(file_path: str) -> dict[str, str]:
    """Parse PlantUML file to extract basic structure.

    Args:
        file_path: Path to PlantUML file

    Returns:
        Dictionary with keys: type, content, elements

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or invalid format

    Example:
        >>> data = parse_plantuml_file("/path/to/diagram.puml")
        >>> data['type']
        'class'
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PlantUML file not found: {file_path}")

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Detect diagram type
        diagram_type = "unknown"
        if "class " in content:
            diagram_type = "class"
        elif "participant " in content or "actor " in content:
            diagram_type = "sequence"
        elif "component " in content:
            diagram_type = "component"
        elif "start" in content and "stop" in content:
            diagram_type = "activity"

        # Extract elements
        elements: list[str] = []
        for line in content.split("\n"):
            line = line.strip()
            if line and not line.startswith("@") and not line.startswith("'"):
                elements.append(line)

        return {
            "type": diagram_type,
            "content": content,
            "elements": str(len(elements)),
        }

    except Exception as e:
        raise ValueError(f"Failed to parse PlantUML file: {e}")


@strands_tool
def write_plantuml_file(
    file_path: str, diagram_content: str, skip_confirm: bool
) -> str:
    """Write PlantUML diagram to file.

    Args:
        file_path: Path for PlantUML file
        diagram_content: PlantUML diagram syntax
        skip_confirm: If False, raises error if file exists

    Returns:
        Success message

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If file exists and skip_confirm is False

    Example:
        >>> content = "@startuml\\nclass User\\n@enduml"
        >>> msg = write_plantuml_file("/tmp/diagram.puml", content, True)
        >>> "Created" in msg
        True
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(diagram_content, str):
        raise TypeError("diagram_content must be a string")
    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if os.path.exists(file_path) and not skip_confirm:
        raise ValueError(
            f"File already exists: {file_path}. Set skip_confirm=True to overwrite."
        )

    parent_dir = os.path.dirname(file_path)
    if parent_dir and not os.path.exists(parent_dir):
        raise ValueError(f"Parent directory does not exist: {parent_dir}")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(diagram_content)

        return f"Created PlantUML file at {file_path}"

    except PermissionError:
        raise PermissionError(f"Permission denied writing to: {file_path}")
    except Exception as e:
        raise ValueError(f"Failed to write PlantUML file: {e}")


@strands_tool
def validate_plantuml_syntax(diagram_content: str) -> bool:
    """Validate basic PlantUML syntax.

    Args:
        diagram_content: PlantUML diagram syntax

    Returns:
        True if valid basic syntax, False otherwise

    Raises:
        TypeError: If parameters are wrong type

    Example:
        >>> content = "@startuml\\nclass User\\n@enduml"
        >>> validate_plantuml_syntax(content)
        True
    """
    if not isinstance(diagram_content, str):
        raise TypeError("diagram_content must be a string")

    # Basic validation checks
    has_start = "@startuml" in diagram_content
    has_end = "@enduml" in diagram_content

    return has_start and has_end


@strands_tool
def extract_plantuml_elements(diagram_content: str) -> list[str]:
    """Extract elements from PlantUML diagram.

    Args:
        diagram_content: PlantUML diagram syntax

    Returns:
        List of element names found in diagram

    Raises:
        TypeError: If parameters are wrong type

    Example:
        >>> content = "@startuml\\nclass User\\nclass Account\\n@enduml"
        >>> elements = extract_plantuml_elements(content)
        >>> 'User' in elements
        True
    """
    if not isinstance(diagram_content, str):
        raise TypeError("diagram_content must be a string")

    elements: list[str] = []

    # Extract class names
    for match in re.finditer(r"class\s+(\w+)", diagram_content):
        elements.append(match.group(1))

    # Extract participant names
    for match in re.finditer(r"participant\s+(\w+)", diagram_content):
        elements.append(match.group(1))

    # Extract component names
    for match in re.finditer(r"component\s+(\w+)", diagram_content):
        elements.append(match.group(1))

    # Extract interface names
    for match in re.finditer(r"interface\s+(\w+)", diagram_content):
        elements.append(match.group(1))

    return elements
