"""Agent module for validation tools testing.

This module provides an AI agent that uses the basic_open_agent_tools
validation utilities for ADK evaluation testing.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent

from basic_open_agent_tools.data.validation import (
    check_required_fields,
    check_required_fields_simple,
    create_validation_report,
    create_validation_report_simple,
    validate_data_types_simple,
    validate_range_simple,
    validate_schema_simple,
)

# Load environment variables for API keys
load_dotenv()  # From current working directory (when pytest runs from root)
project_root = Path(__file__).parent.parent.parent.parent.parent
load_dotenv(project_root / ".env")  # From project root

root_agent = Agent(
    name="validation_agent",
    model=os.environ.get("GOOGLE_MODEL_NAME", "gemini-1.5-flash"),
    description="Agent that can validate data using the basic_open_agent_tools validation utilities.",
    instruction="""You are a helpful agent that can work with data validation.

You have access to tools for validating data schemas, checking required fields, validating data types, and creating validation reports.

Always provide clear output showing the validation results.""",
    tools=[
        validate_schema_simple,
        check_required_fields,
        check_required_fields_simple,
        validate_data_types_simple,
        validate_range_simple,
        create_validation_report,
        create_validation_report_simple,
    ],
)
