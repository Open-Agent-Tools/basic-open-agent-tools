"""Mermaid diagram generation and parsing functions for AI agents."""

import os
import re

from ..decorators import strands_tool

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit


@strands_tool
def create_mermaid_flowchart(
    nodes: list[dict[str, str]], edges: list[dict[str, str]], direction: str
) -> str:
    """Generate Mermaid flowchart syntax.


    Args:
        nodes: List of node dicts with keys: id, label, shape (optional)
        edges: List of edge dicts with keys: from, to, label (optional)
        direction: Flow direction ('TB', 'LR', 'BT', 'RL')

    Returns:
        Mermaid flowchart syntax

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If nodes empty or direction invalid

    Example:
        >>> nodes = [{'id': 'A', 'label': 'Start'}, {'id': 'B', 'label': 'Process'}]
        >>> edges = [{'from': 'A', 'to': 'B', 'label': ''}]
        >>> chart = create_mermaid_flowchart(nodes, edges, 'TB')
        >>> 'flowchart TB' in chart
        True
    """
    if not isinstance(nodes, list):
        raise TypeError("nodes must be a list")
    if not isinstance(edges, list):
        raise TypeError("edges must be a list")
    if not isinstance(direction, str):
        raise TypeError("direction must be a string")
    if not nodes:
        raise ValueError("nodes must not be empty")
    if direction not in ["TB", "LR", "BT", "RL"]:
        raise ValueError("direction must be one of: TB, LR, BT, RL")

    lines = [f"flowchart {direction}"]

    # Generate nodes
    for node in nodes:
        if not isinstance(node, dict):
            raise TypeError("each node must be a dict")

        node_id = node.get("id", "")
        label = node.get("label", node_id)
        shape = node.get("shape", "rect")  # rect, round, diamond, circle

        if not node_id:
            continue

        # Map shape to Mermaid syntax
        shape_syntax = {
            "rect": f"    {node_id}[{label}]",
            "round": f"    {node_id}({label})",
            "diamond": f"    {node_id}{{{{{label}}}}}",
            "circle": f"    {node_id}(({label}))",
        }
        lines.append(shape_syntax.get(shape, f"    {node_id}[{label}]"))

    # Generate edges
    for edge in edges:
        if not isinstance(edge, dict):
            raise TypeError("each edge must be a dict")

        from_node = edge.get("from", "")
        to_node = edge.get("to", "")
        label = edge.get("label", "")

        if from_node and to_node:
            if label:
                lines.append(f"    {from_node} -->|{label}| {to_node}")
            else:
                lines.append(f"    {from_node} --> {to_node}")

    return "\n".join(lines)


@strands_tool
def create_mermaid_sequence_diagram(
    participants: list[str], messages: list[dict[str, str]]
) -> str:
    """Generate Mermaid sequence diagram syntax.

    Args:
        participants: List of participant names
        messages: List of message dicts with keys: from, to, message, type

    Returns:
        Mermaid sequence diagram syntax

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If participants empty

    Example:
        >>> parts = ['Alice', 'Bob']
        >>> msgs = [{'from': 'Alice', 'to': 'Bob', 'message': 'Hello', 'type': 'sync'}]
        >>> diagram = create_mermaid_sequence_diagram(parts, msgs)
        >>> 'sequenceDiagram' in diagram
        True
    """
    if not isinstance(participants, list):
        raise TypeError("participants must be a list")
    if not isinstance(messages, list):
        raise TypeError("messages must be a list")
    if not participants:
        raise ValueError("participants must not be empty")

    lines = ["sequenceDiagram"]

    # Declare participants
    for participant in participants:
        if not isinstance(participant, str):
            raise TypeError("all participants must be strings")
        lines.append(f"    participant {participant}")

    # Generate messages
    for msg in messages:
        if not isinstance(msg, dict):
            raise TypeError("each message must be a dict")

        from_p = msg.get("from", "")
        to_p = msg.get("to", "")
        message = msg.get("message", "")
        msg_type = msg.get("type", "sync")  # sync, async, response

        if from_p and to_p and message:
            arrow = "->>" if msg_type == "async" else "->"
            if msg_type == "response":
                arrow = "-->>"
            lines.append(f"    {from_p}{arrow}{to_p}: {message}")

    return "\n".join(lines)


@strands_tool
def create_mermaid_gantt_chart(
    title: str, sections: list[dict[str, str]], tasks: list[dict[str, str]]
) -> str:
    """Generate Mermaid Gantt chart syntax.

    Args:
        title: Chart title
        sections: List of section dicts with keys: name
        tasks: List of task dicts with keys: name, section, start, duration, status

    Returns:
        Mermaid Gantt chart syntax

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If title empty or tasks empty

    Example:
        >>> title = "Project Schedule"
        >>> secs = [{'name': 'Development'}]
        >>> tasks = [{'name': 'Task 1', 'section': 'Development', 'start': '2024-01-01', 'duration': '5d', 'status': 'active'}]
        >>> chart = create_mermaid_gantt_chart(title, secs, tasks)
        >>> 'gantt' in chart
        True
    """
    if not isinstance(title, str):
        raise TypeError("title must be a string")
    if not isinstance(sections, list):
        raise TypeError("sections must be a list")
    if not isinstance(tasks, list):
        raise TypeError("tasks must be a list")
    if not title:
        raise ValueError("title must not be empty")
    if not tasks:
        raise ValueError("tasks must not be empty")

    lines = ["gantt", f"    title {title}", "    dateFormat YYYY-MM-DD"]

    # Generate sections and tasks
    current_section = ""
    for task in tasks:
        if not isinstance(task, dict):
            raise TypeError("each task must be a dict")

        section = task.get("section", "")
        name = task.get("name", "")
        start = task.get("start", "")
        duration = task.get("duration", "1d")
        status = task.get("status", "")

        # Add section header if changed
        if section and section != current_section:
            lines.append(f"    section {section}")
            current_section = section

        if name:
            status_str = f", {status}" if status else ""
            lines.append(f"    {name}: {status_str}, {start}, {duration}")

    return "\n".join(lines)


@strands_tool
def create_mermaid_er_diagram(
    entities: list[dict[str, str]], relationships: list[dict[str, str]]
) -> str:
    """Generate Mermaid ER (Entity-Relationship) diagram syntax.

    Args:
        entities: List of entity dicts with keys: name, attributes
        relationships: List of relationship dicts with keys: from, to, type, label

    Returns:
        Mermaid ER diagram syntax

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If entities empty

    Example:
        >>> entities = [{'name': 'User', 'attributes': 'id, name'}]
        >>> rels = [{'from': 'User', 'to': 'Order', 'type': 'one-to-many', 'label': 'places'}]
        >>> diagram = create_mermaid_er_diagram(entities, rels)
        >>> 'erDiagram' in diagram
        True
    """
    if not isinstance(entities, list):
        raise TypeError("entities must be a list")
    if not isinstance(relationships, list):
        raise TypeError("relationships must be a list")
    if not entities:
        raise ValueError("entities must not be empty")

    lines = ["erDiagram"]

    # Generate entities with attributes
    for entity in entities:
        if not isinstance(entity, dict):
            raise TypeError("each entity must be a dict")

        name = entity.get("name", "")
        attributes = entity.get("attributes", "")

        if name:
            lines.append(f"    {name} {{")
            if attributes:
                for attr in attributes.split(","):
                    attr = attr.strip()
                    if attr:
                        lines.append(f"        string {attr}")
            lines.append("    }")

    # Generate relationships
    for rel in relationships:
        if not isinstance(rel, dict):
            raise TypeError("each relationship must be a dict")

        from_entity = rel.get("from", "")
        to_entity = rel.get("to", "")
        rel_type = rel.get("type", "one-to-many")
        label = rel.get("label", "")

        if from_entity and to_entity:
            # Map relationship type to Mermaid syntax
            type_syntax = {
                "one-to-one": "||--||",
                "one-to-many": "||--o{",
                "many-to-one": "}o--||",
                "many-to-many": "}o--o{",
            }
            syntax = type_syntax.get(rel_type, "||--o{")

            label_str = f' : "{label}"' if label else ""
            lines.append(f"    {from_entity} {syntax} {to_entity}{label_str}")

    return "\n".join(lines)


@strands_tool
def parse_mermaid_file(file_path: str) -> dict[str, str]:
    """Parse Mermaid file to extract basic structure.

    Args:
        file_path: Path to Mermaid file

    Returns:
        Dictionary with keys: type, content, elements_count

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large

    Example:
        >>> data = parse_mermaid_file("/path/to/diagram.mmd")
        >>> data['type']
        'flowchart'
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Mermaid file not found: {file_path}")

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
        first_line = content.strip().split("\n")[0].lower()
        if "flowchart" in first_line or "graph" in first_line:
            diagram_type = "flowchart"
        elif "sequencediagram" in first_line:
            diagram_type = "sequence"
        elif "gantt" in first_line:
            diagram_type = "gantt"
        elif "erdiagram" in first_line:
            diagram_type = "er"

        # Count elements
        element_count = len([line for line in content.split("\n") if line.strip()])

        return {
            "type": diagram_type,
            "content": content,
            "elements_count": str(element_count),
        }

    except Exception as e:
        raise ValueError(f"Failed to parse Mermaid file: {e}")


@strands_tool
def write_mermaid_file(file_path: str, diagram_content: str, skip_confirm: bool) -> str:
    """Write Mermaid diagram to file.

    Args:
        file_path: Path for Mermaid file
        diagram_content: Mermaid diagram syntax
        skip_confirm: If False, raises error if file exists

    Returns:
        Success message

    Raises:
        TypeError: If parameters are wrong type
        ValueError: If file exists and skip_confirm is False

    Example:
        >>> content = "flowchart TB\\n    A[Start]"
        >>> msg = write_mermaid_file("/tmp/diagram.mmd", content, True)
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

        return f"Created Mermaid file at {file_path}"

    except PermissionError:
        raise PermissionError(f"Permission denied writing to: {file_path}")
    except Exception as e:
        raise ValueError(f"Failed to write Mermaid file: {e}")


@strands_tool
def embed_mermaid_in_markdown(
    md_file_path: str, diagram_content: str, skip_confirm: bool
) -> str:
    """Embed Mermaid diagram in markdown file.

    Args:
        md_file_path: Path to markdown file
        diagram_content: Mermaid diagram syntax
        skip_confirm: Required for consistency

    Returns:
        Success message

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large

    Example:
        >>> content = "flowchart TB\\n    A[Start]"
        >>> msg = embed_mermaid_in_markdown("/tmp/doc.md", content, True)
        >>> "Embedded" in msg
        True
    """
    if not isinstance(md_file_path, str):
        raise TypeError("md_file_path must be a string")
    if not isinstance(diagram_content, str):
        raise TypeError("diagram_content must be a string")
    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if not os.path.exists(md_file_path):
        raise FileNotFoundError(f"Markdown file not found: {md_file_path}")

    file_size = os.path.getsize(md_file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    try:
        with open(md_file_path, encoding="utf-8") as f:
            md_content = f.read()

        # Embed Mermaid in markdown code block
        mermaid_block = f"\n```mermaid\n{diagram_content}\n```\n"
        md_content += mermaid_block

        with open(md_file_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        return f"Embedded Mermaid diagram in {md_file_path}"

    except Exception as e:
        raise ValueError(f"Failed to embed Mermaid diagram: {e}")


@strands_tool
def extract_mermaid_from_markdown(md_file_path: str) -> list[str]:
    """Extract Mermaid diagrams from markdown file.

    Args:
        md_file_path: Path to markdown file

    Returns:
        List of Mermaid diagram contents

    Raises:
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large

    Example:
        >>> diagrams = extract_mermaid_from_markdown("/path/to/doc.md")
        >>> len(diagrams) > 0
        True
    """
    if not isinstance(md_file_path, str):
        raise TypeError("md_file_path must be a string")

    if not os.path.exists(md_file_path):
        raise FileNotFoundError(f"Markdown file not found: {md_file_path}")

    file_size = os.path.getsize(md_file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    try:
        with open(md_file_path, encoding="utf-8") as f:
            content = f.read()

        # Extract mermaid code blocks
        pattern = r"```mermaid\n(.*?)\n```"
        matches = re.findall(pattern, content, re.DOTALL)

        return matches

    except Exception as e:
        raise ValueError(f"Failed to extract Mermaid diagrams: {e}")
