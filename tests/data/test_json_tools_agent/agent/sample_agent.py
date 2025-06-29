"""Agent module for JSON tools testing.

This module provides an AI agent that uses the basic_open_agent_tools
JSON utilities for ADK evaluation testing.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent

from src.basic_open_agent_tools.data.json_tools import (
    safe_json_deserialize,
    safe_json_serialize,
    validate_json_string,
)

# Load environment variables for API keys
load_dotenv()  # From current working directory (when pytest runs from root)
project_root = Path(__file__).parent.parent.parent.parent.parent
load_dotenv(project_root / ".env")  # From project root

root_agent = Agent(
    name="json_tools_agent",
    model=os.environ.get("GOOGLE_MODEL_NAME"),
    description="Agent that can process JSON data using the basic_open_agent_tools JSON utilities.",
    instruction="""You are a helpful agent that can work with JSON data.

You have access to tools for serializing, deserializing, and validating JSON data.

Always provide clear output showing the JSON processing results.""",
    tools=[
        safe_json_serialize,
        safe_json_deserialize,
        validate_json_string,
    ],
)
