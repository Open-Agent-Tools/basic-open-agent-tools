"""Agent module for file system info tools testing.

This module provides an AI agent that uses the basic_open_agent_tools
file system info functions for ADK evaluation testing.
"""

from pathlib import Path
import os

from dotenv import load_dotenv
from google.adk.agents import Agent

from basic_open_agent_tools.file_system.info import (
    directory_exists,
    file_exists,
    get_file_info,
    get_file_size,
    is_empty_directory,
)

# Load environment variables for API keys
# Try multiple locations: current working directory and project root
load_dotenv()  # From current working directory (when pytest runs from root)
project_root = Path(__file__).parent.parent.parent.parent.parent
load_dotenv(project_root / ".env")  # From project root

root_agent = Agent(
    name="info_agent",
    model=os.environ.get("GOOGLE_MODEL_NAME"),
    description="Agent that can retrieve file and directory information using the basic_open_agent_tools file system utilities.",
    instruction="""You are a helpful agent that can retrieve file and directory information.

When asked to get file information, use the get_file_info function with the file_path parameter.
When asked to check if a file exists, use the file_exists function with the file_path parameter.
When asked to check if a directory exists, use the directory_exists function with the directory_path parameter.
When asked to get file size, use the get_file_size function with the file_path parameter.
When asked to check if a directory is empty, use the is_empty_directory function with the directory_path parameter.

Always provide clear, informative responses about the file or directory properties.""",
    tools=[
        get_file_info,
        file_exists,
        directory_exists,
        get_file_size,
        is_empty_directory,
    ],
)
