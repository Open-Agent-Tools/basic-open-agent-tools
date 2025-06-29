"""Agent module for config processing tools testing.

This module provides an AI agent that uses the basic_open_agent_tools
configuration processing utilities for ADK evaluation testing.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent

from basic_open_agent_tools.data.config_processing import (
    merge_config_files,
    read_ini_file,
    read_toml_file,
    read_yaml_file,
    validate_config_schema,
    write_ini_file,
    write_toml_file,
    write_yaml_file,
)

# Load environment variables for API keys
load_dotenv()  # From current working directory (when pytest runs from root)
project_root = Path(__file__).parent.parent.parent.parent.parent
load_dotenv(project_root / ".env")  # From project root

root_agent = Agent(
    name="config_processing_agent",
    model=os.environ.get("GOOGLE_MODEL_NAME"),
    description="Agent that can process configuration files using the basic_open_agent_tools config utilities.",
    instruction="""You are a helpful agent that can work with configuration files.

You have access to tools for reading, writing, validating, and merging configuration files in YAML, TOML, and INI formats. You can convert between formats and validate configurations against schemas.

Always provide clear output showing the configuration processing results.""",
    tools=[
        read_yaml_file,
        write_yaml_file,
        read_toml_file,
        write_toml_file,
        read_ini_file,
        write_ini_file,
        validate_config_schema,
        merge_config_files,
    ],
)
