"""PowerPoint presentation processing tools for AI agents."""

from .reading import (
    extract_pptx_notes,
    extract_pptx_text,
    get_pptx_metadata,
    get_pptx_slide_count,
    get_pptx_slide_text,
    get_pptx_slide_titles,
)
from .writing import (
    add_pptx_blank_slide,
    add_pptx_content_slide,
    add_pptx_title_slide,
    create_simple_pptx,
)

__all__: list[str] = [
    # Reading functions (6)
    "get_pptx_metadata",
    "get_pptx_slide_count",
    "extract_pptx_text",
    "get_pptx_slide_text",
    "get_pptx_slide_titles",
    "extract_pptx_notes",
    # Writing functions (4)
    "create_simple_pptx",
    "add_pptx_title_slide",
    "add_pptx_content_slide",
    "add_pptx_blank_slide",
]
