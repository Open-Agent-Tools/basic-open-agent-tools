# PowerPoint Tools

PowerPoint presentation processing tools with reading, creation, and modification (10 functions).

## Features
- **Reading** (6): Extract metadata, slide count, text, titles, notes
- **Writing** (4): Create presentations, add title/content/blank slides

## Dependencies
- python-pptx >= 0.6.21

## Usage
```python
from basic_open_agent_tools.powerpoint import (
    create_simple_pptx,
    add_pptx_content_slide,
    extract_pptx_text,
    get_pptx_slide_titles
)

# Create presentation
create_simple_pptx("/tmp/pres.pptx", "My Title", "Subtitle", True)

# Add content slide
add_pptx_content_slide("/tmp/pres.pptx", "Agenda", ["Point 1", "Point 2"])

# Extract text
text = extract_pptx_text("/tmp/pres.pptx")

# Get slide titles
titles = get_pptx_slide_titles("/tmp/pres.pptx")
```
