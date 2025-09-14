"""Agent module for file system validation testing.

This module provides an AI agent that uses the basic_open_agent_tools
file system validation functions for ADK evaluation testing.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent

from basic_open_agent_tools.file_system.validation import (
    validate_file_content,
    validate_path,
)

# Load environment variables for API keys
load_dotenv()  # From current working directory (when pytest runs from root)
project_root = Path(__file__).parent.parent.parent.parent.parent
load_dotenv(project_root / ".env")  # From project root

root_agent = Agent(
    name="validation_agent",
    model=os.environ.get("GOOGLE_MODEL_NAME", "gemini-1.5-flash"),
    description="Agent that can perform file system validation using the basic_open_agent_tools validation utilities.",
    instruction="""You are a helpful agent that can validate file paths and content.

You have access to tools for validating file paths and file content before operations.

Always provide clear output that shows the validation results.""",
    tools=[
        validate_path,
        validate_file_content,
    ],
)
