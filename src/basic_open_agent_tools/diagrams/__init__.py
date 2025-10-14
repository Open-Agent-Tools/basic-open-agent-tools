"""Diagram generation tools for AI agents (PlantUML and Mermaid)."""

from .mermaid import (
    create_mermaid_er_diagram,
    create_mermaid_flowchart,
    create_mermaid_gantt_chart,
    create_mermaid_sequence_diagram,
    embed_mermaid_in_markdown,
    extract_mermaid_from_markdown,
    parse_mermaid_file,
    write_mermaid_file,
)
from .plantuml import (
    create_plantuml_activity_diagram,
    create_plantuml_class_diagram,
    create_plantuml_component_diagram,
    create_plantuml_sequence_diagram,
    extract_plantuml_elements,
    parse_plantuml_file,
    validate_plantuml_syntax,
    write_plantuml_file,
)

__all__: list[str] = [
    # PlantUML functions (8)
    "create_plantuml_class_diagram",
    "create_plantuml_sequence_diagram",
    "create_plantuml_activity_diagram",
    "create_plantuml_component_diagram",
    "parse_plantuml_file",
    "write_plantuml_file",
    "validate_plantuml_syntax",
    "extract_plantuml_elements",
    # Mermaid functions (8)
    "create_mermaid_flowchart",
    "create_mermaid_sequence_diagram",
    "create_mermaid_gantt_chart",
    "create_mermaid_er_diagram",
    "parse_mermaid_file",
    "write_mermaid_file",
    "embed_mermaid_in_markdown",
    "extract_mermaid_from_markdown",
]
