# Diagram Tools

PlantUML and Mermaid diagram generation and parsing tools (16 functions).

## Features
- **PlantUML** (8): Class, sequence, activity, component diagrams
- **Mermaid** (8): Flowcharts, sequence, Gantt, ER diagrams

## Dependencies
- None (stdlib only)

## Usage

### PlantUML
```python
from basic_open_agent_tools.diagrams import (
    create_plantuml_class_diagram,
    create_plantuml_sequence_diagram,
    write_plantuml_file
)

# Create class diagram
classes = [
    {'name': 'User', 'attributes': 'name: str', 'methods': 'login()'},
    {'name': 'Account', 'attributes': 'balance: float', 'methods': 'deposit()'}
]
relationships = [{'from': 'User', 'to': 'Account', 'type': 'has'}]
diagram = create_plantuml_class_diagram(classes, relationships)
write_plantuml_file("/tmp/classes.puml", diagram, True)
```

### Mermaid
```python
from basic_open_agent_tools.diagrams import (
    create_mermaid_flowchart,
    create_mermaid_sequence_diagram,
    embed_mermaid_in_markdown
)

# Create flowchart
nodes = [
    {'id': 'A', 'label': 'Start', 'shape': 'round'},
    {'id': 'B', 'label': 'Process', 'shape': 'rect'},
    {'id': 'C', 'label': 'End', 'shape': 'round'}
]
edges = [
    {'from': 'A', 'to': 'B', 'label': ''},
    {'from': 'B', 'to': 'C', 'label': 'done'}
]
flowchart = create_mermaid_flowchart(nodes, edges, 'TB')

# Embed in markdown
embed_mermaid_in_markdown("/tmp/doc.md", flowchart, True)
```

## Diagram Types

### PlantUML
- Class diagrams (UML)
- Sequence diagrams
- Activity diagrams
- Component diagrams

### Mermaid
- Flowcharts (with various shapes)
- Sequence diagrams
- Gantt charts
- ER (Entity-Relationship) diagrams
