"""Agent module for file system operations testing.

This module provides an AI agent that uses the basic_open_agent_tools
file system operations functions for ADK evaluation testing.
"""

from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent

from basic_open_agent_tools.file_system.operations import (
    append_to_file,
    copy_file,
    create_directory,
    delete_directory,
    delete_file,
    insert_at_line,
    list_directory_contents,
    move_file,
    read_file_to_string,
    replace_in_file,
    write_file_from_string,
)

# Load environment variables for API keys
load_dotenv()  # From current working directory (when pytest runs from root)
project_root = Path(__file__).parent.parent.parent.parent.parent
load_dotenv(project_root / ".env")  # From project root

root_agent = Agent(
    name="operations_agent",
    model="gemini-2.0-flash",
    description="Agent that can perform file system operations using the basic_open_agent_tools operations utilities.",
    instruction="""You are a helpful agent that can perform comprehensive file system operations.

You have access to tools for reading, writing, appending, listing, creating, deleting, moving, copying, and modifying files and directories.

Always provide clear output that shows the operation results.""",
    tools=[
        read_file_to_string,
        write_file_from_string,
        append_to_file,
        list_directory_contents,
        create_directory,
        delete_file,
        delete_directory,
        move_file,
        copy_file,
        replace_in_file,
        insert_at_line,
    ],
)
