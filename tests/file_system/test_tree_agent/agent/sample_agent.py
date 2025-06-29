"""Agent module for tree generation tools testing.

This module provides an AI agent that uses the basic_open_agent_tools
tree generation functions for ADK evaluation testing.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent

from basic_open_agent_tools.file_system.tree import (
    generate_directory_tree,
    list_all_directory_contents,
)

# Load environment variables for API keys
# Try multiple locations: current working directory and project root
load_dotenv()  # From current working directory (when pytest runs from root)
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / ".env")  # From project root

root_agent = Agent(
    name="tree_agent",
    model=os.environ.get("GOOGLE_MODEL_NAME"),
    description="Agent that can generate directory trees and list directory contents using the basic_open_agent_tools filesystem utilities.",
    instruction="""You are a helpful agent it directory skills.""",
    tools=[generate_directory_tree, list_all_directory_contents],
)
