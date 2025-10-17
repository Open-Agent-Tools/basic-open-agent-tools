"""Agent module for tree generation."""

from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent

from basic_open_agent_tools.file_system.tree import generate_directory_tree

# Load environment variables for API keys
# Try multiple locations: current working directory and project root
load_dotenv()  # From current working directory (when pytest runs from root)
project_root = Path(__file__).parent.parent.parent.parent
load_dotenv(project_root / ".env")  # From project root

root_agent = Agent(
    name="tree_agent",
    model="gemini-2.0-flash",
    description="Simple agent that can generate directory trees using the basic_open_agent_tools filesystem utilities.",
    instruction="You are a helpful agent that can generate directory trees. When asked to generate a tree, use the generate_directory_tree function with appropriate parameters.",
    tools=[generate_directory_tree],
)
