"""Agent module for text processing tools testing.

This module provides an AI agent that uses the basic_open_agent_tools
text processing utilities for ADK evaluation testing.
"""

from pathlib import Path
import os

from dotenv import load_dotenv
from google.adk.agents import Agent

from basic_open_agent_tools.text.processing import (
    clean_whitespace,
    extract_sentences,
    join_with_oxford_comma,
    normalize_line_endings,
    normalize_unicode,
    smart_split_lines,
    strip_html_tags,
    to_camel_case,
    to_snake_case,
    to_title_case,
)

# Load environment variables for API keys
load_dotenv()  # From current working directory (when pytest runs from root)
project_root = Path(__file__).parent.parent.parent.parent.parent
load_dotenv(project_root / ".env")  # From project root

root_agent = Agent(
    name="text_processing_agent",
    model=os.environ.get("GOOGLE_MODEL_NAME"),
    description="Agent that can process and manipulate text using the basic_open_agent_tools text processing utilities.",
    instruction="""You are a helpful agent that can work with text processing tasks.

You have access to tools for cleaning whitespace, normalizing text, converting between case formats, extracting content, and manipulating text structure.

Always provide clear output showing the text processing results.""",
    tools=[
        clean_whitespace,
        normalize_line_endings,
        strip_html_tags,
        normalize_unicode,
        to_snake_case,
        to_camel_case,
        to_title_case,
        smart_split_lines,
        extract_sentences,
        join_with_oxford_comma,
    ],
)
