"""Agent module for helpers tools testing.

This module provides an AI agent that uses the basic_open_agent_tools
helper utilities for ADK evaluation testing.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent

from basic_open_agent_tools.helpers import (
    load_all_data_tools,
    load_all_filesystem_tools,
    load_all_text_tools,
    merge_tool_lists,
)

# Load environment variables for API keys
load_dotenv()  # From current working directory (when pytest runs from root)
project_root = Path(__file__).parent.parent.parent.parent.parent
load_dotenv(project_root / ".env")  # From project root

agent_tools = merge_tool_lists(
    load_all_filesystem_tools(),
    load_all_text_tools(),
    load_all_data_tools(),
)

root_agent = Agent(
    name="helpers_agent",
    model=os.environ.get("GOOGLE_MODEL_NAME"),
    description="Agent that can discover and manage available tools using the basic_open_agent_tools helper utilities.",
    instruction="""You are a helpful agent that can discover and work with tools.

You have access to functions for loading tools by category, listing available tools, getting tool information, and merging tool collections.

When asked to list tools, always provide clear output showing the tools that are available. Focus on tool discovery and organization.""",
    tools=agent_tools,
)
