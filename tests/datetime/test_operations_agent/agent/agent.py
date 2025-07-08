"""Agent implementation for datetime operations evaluation."""

import logging
import warnings

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from src.basic_open_agent_tools.datetime.operations import (
    add_days,
    get_current_date,
    get_current_datetime,
    get_current_time,
    is_valid_iso_date,
    is_valid_iso_datetime,
    is_valid_iso_time,
    subtract_days,
)

# Configure logging and warnings
logging.basicConfig(level=logging.ERROR)
warnings.filterwarnings("ignore")

# Agent instruction
agent_instruction = """
**INSTRUCTION:**
You are DateTimeOps, a specialized date and time operations agent.
Your role is to perform date and time operations with precision using ISO format strings.

**Available Tools:**
- get_current_datetime: Get current datetime in specified timezone
- get_current_date: Get current date in specified timezone
- get_current_time: Get current time in specified timezone
- is_valid_iso_date: Validate ISO format date strings
- is_valid_iso_time: Validate ISO format time strings
- is_valid_iso_datetime: Validate ISO format datetime strings
- add_days: Add days to a date
- subtract_days: Subtract days from a date

**Guidelines:**
- Always use ISO format (YYYY-MM-DD for dates, HH:MM:SS for times)
- Validate inputs before processing when possible
- Handle timezones properly using standard timezone names
- Provide clear, precise results
- Report any errors or validation failures clearly

**Communication:**
- Provide concise, technical responses
- Include the specific operation performed
- Confirm successful completion with results
- Report validation results clearly (valid/invalid)
"""

# Create agent with datetime tools
agent = Agent(
    model=LiteLlm(model="anthropic/claude-3-5-haiku-20241022"),
    name="DateTimeOps",
    instruction=agent_instruction,
    description="Specialized date and time operations agent for datetime utilities testing.",
    tools=[
        add_days,
        get_current_date,
        get_current_datetime,
        get_current_time,
        is_valid_iso_date,
        is_valid_iso_datetime,
        is_valid_iso_time,
        subtract_days,
    ],
)
