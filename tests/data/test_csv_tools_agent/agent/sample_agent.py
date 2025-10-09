"""Agent module for CSV tools testing.

This module provides an AI agent that uses the basic_open_agent_tools
CSV utilities for ADK evaluation testing.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent

from src.basic_open_agent_tools.data.csv_tools import (
    clean_csv_data,
    csv_to_dict_list,
    detect_csv_delimiter,
    dict_list_to_csv,
    read_csv_simple,
    validate_csv_structure,
    write_csv_simple,
)

# Load environment variables for API keys
load_dotenv()  # From current working directory (when pytest runs from root)
project_root = Path(__file__).parent.parent.parent.parent.parent
load_dotenv(project_root / ".env")  # From project root

root_agent = Agent(
    name="csv_tools_agent",
    model=os.environ.get("GOOGLE_MODEL_NAME", "gemini-1.5-flash"),
    description="Agent that can process CSV files using the basic_open_agent_tools CSV utilities.",
    instruction="""You are a helpful agent that can work with CSV data.

You have access to tools for reading, writing, parsing, validating, and cleaning CSV files. You can detect delimiters, convert between formats, and process CSV data structures.

IMPORTANT: The write_csv_simple function now requires a 'skip_confirm' parameter:
- write_csv_simple: requires skip_confirm=True to overwrite existing files

Always use skip_confirm=True when writing CSV files to avoid permission errors.
The tool now returns detailed feedback strings describing the file created (rows, columns, file size).

Always provide clear output showing the CSV processing results.""",
    tools=[
        read_csv_simple,
        write_csv_simple,
        csv_to_dict_list,
        dict_list_to_csv,
        detect_csv_delimiter,
        validate_csv_structure,
        clean_csv_data,
    ],
)
