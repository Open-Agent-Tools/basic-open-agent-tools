"""Example AWS Strands agent using basic-open-agent-tools.

This example shows how to create a comprehensive Strands agent with the toolkit.
Requires: pip install strands anthropic basic-open-agent-tools[all]
"""

import os

from dotenv import load_dotenv
from strands import Agent
from strands.models.anthropic import AnthropicModel

import basic_open_agent_tools as boat

load_dotenv()


def create_basic_tools_agent():
    """Create a Strands agent with basic-open-agent-tools."""

    model = AnthropicModel(
        client_args={
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
        },
        model_id="claude-sonnet-4-20250514",
        max_tokens=1024,
        params={
            "temperature": 0.7,
        },
    )

    file_tools = boat.load_all_filesystem_tools()
    text_tools = boat.load_all_text_tools()
    data_tools = boat.load_all_data_tools()
    datetime_tools = boat.load_all_datetime_tools()
    network_tools = boat.load_all_network_tools()
    utilities_tools = boat.load_all_utilities_tools()
    crypto_tools = boat.load_all_crypto_tools()

    try:
        system_tools = boat.load_all_system_tools()
    except ImportError:
        system_tools = []
        print(
            "⚠️  System tools not available (install with: pip install basic-open-agent-tools[system])"
        )

    agent_tools = boat.merge_tool_lists(
        file_tools,
        text_tools,
        data_tools[:15],
        datetime_tools[:15],
        network_tools,
        utilities_tools,
        crypto_tools[:10],
        system_tools[:10],
    )

    agent = Agent(
        model=model,
        name="Basic Tools Agent",
        description="Comprehensive agent with local operations capabilities using basic-open-agent-tools",
        system_prompt=(
            "You are the 'Basic Tools Agent', built using AWS Strands framework with comprehensive "
            "local operations capabilities. You have access to:\n"
            "- File system operations (read, write, create, delete, move, copy, directories)\n"
            "- Text processing (cleaning, formatting, case conversion, splitting)\n"
            "- Data processing (JSON, CSV, YAML, validation, schemas)\n"
            "- Date/time operations (formatting, arithmetic, validation, business days)\n"
            "- Network operations (HTTP requests, DNS resolution)\n"
            "- Cryptographic utilities (hashing, encoding, UUIDs)\n"
            "- System operations (processes, environment, shell commands)\n"
            "- Utility functions (timing, debugging, validation)\n\n"
            "When introducing yourself, identify as the 'Basic Tools Agent' and explain your "
            "comprehensive local operations capabilities. Use tools appropriately and efficiently. "
            "Always be helpful and explain what you're doing when using tools."
        ),
        tools=agent_tools,
    )

    return agent


def create_specialized_agents():
    """Create specialized agents for different use cases."""

    file_agent = Agent(
        model=AnthropicModel(
            client_args={"api_key": os.getenv("ANTHROPIC_API_KEY")},
            model_id="claude-sonnet-4-20250514",
            max_tokens=512,
        ),
        name="FileOps Agent",
        description="Specialized file operations agent",
        system_prompt=(
            "You are a file operations specialist. You excel at reading, writing, "
            "organizing, and managing files and directories efficiently."
        ),
        tools=boat.load_all_filesystem_tools(),
    )

    data_agent = Agent(
        model=AnthropicModel(
            client_args={"api_key": os.getenv("ANTHROPIC_API_KEY")},
            model_id="claude-sonnet-4-20250514",
            max_tokens=512,
        ),
        name="DataOps Agent",
        description="Specialized data processing agent",
        system_prompt=(
            "You are a data processing specialist. You excel at working with JSON, CSV, "
            "YAML, and other data formats, including validation and transformation."
        ),
        tools=boat.merge_tool_lists(
            boat.load_all_data_tools(),
            boat.load_all_text_tools(),
        ),
    )

    return file_agent, data_agent


def main():
    """Test the agent locally."""
    print("🚀 Creating Basic Tools Agent with Strands + basic-open-agent-tools...")

    try:
        agent = create_basic_tools_agent()
        print(f"✅ Agent created successfully: {agent.name}")
        print(f"📊 Tools loaded: {len(agent.tools)}")

        print("\n📋 Available tool categories:")
        print(f"  • File System: {len(boat.load_all_filesystem_tools())} tools")
        print(f"  • Text Processing: {len(boat.load_all_text_tools())} tools")
        print(f"  • Data Processing: {len(boat.load_all_data_tools())} tools")
        print(f"  • Date/Time: {len(boat.load_all_datetime_tools())} tools")
        print(f"  • Network: {len(boat.load_all_network_tools())} tools")
        print(f"  • Utilities: {len(boat.load_all_utilities_tools())} tools")
        print(f"  • Crypto: {len(boat.load_all_crypto_tools())} tools")

        print("\n🧪 Testing agent...")
        test_questions = [
            "Hello! Please introduce yourself and list your main capabilities.",
            "What file operations can you perform?",
            "How can you help with data processing tasks?",
            "What text processing capabilities do you have?",
        ]

        for question in test_questions:
            print(f"\n❓ Question: {question}")
            try:
                response = agent(question)
                print(
                    f"🤖 Response: {response[:200]}{'...' if len(response) > 200 else ''}"
                )
            except Exception as e:
                print(f"❌ Error: {e}")
                break

    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you have ANTHROPIC_API_KEY in your .env file")
        print(
            "2. Install required packages: pip install strands anthropic python-dotenv"
        )
        print(
            "3. Install basic-open-agent-tools: pip install basic-open-agent-tools[all]"
        )


if __name__ == "__main__":
    main()
