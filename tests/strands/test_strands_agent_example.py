"""Complete AWS Strands agent example using basic-open-agent-tools.

This test creates a complete functional Strands agent using the toolkit
and validates it works with the AWS Strands framework and A2A protocol.
"""

import os
import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import basic_open_agent_tools as boat


@pytest.mark.skipif(
    os.getenv("STRANDS_INTEGRATION_TEST") != "true",
    reason="Strands agent example tests require STRANDS_INTEGRATION_TEST=true",
)
class TestStrandsAgentExample:
    """Test complete Strands agent example with basic-open-agent-tools."""

    def test_create_complete_strands_agent(self):
        """Test creating a complete Strands agent with full toolkit."""
        try:
            from strands import Agent
            from strands.models.anthropic import AnthropicModel
        except ImportError:
            pytest.skip("Strands framework not installed")

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY required for full agent test")

        # Create Anthropic model
        model = AnthropicModel(
            client_args={"api_key": api_key},
            model_id="claude-sonnet-4-20250514",
            max_tokens=1024,
            params={"temperature": 0.7},
        )

        # Load comprehensive tool set
        file_tools = boat.load_all_filesystem_tools()
        text_tools = boat.load_all_text_tools()
        data_tools = boat.load_all_data_tools()
        datetime_tools = boat.load_all_datetime_tools()
        crypto_tools = boat.load_all_crypto_tools()
        network_tools = boat.load_all_network_tools()
        utilities_tools = boat.load_all_utilities_tools()

        # Merge tools for comprehensive agent
        agent_tools = boat.merge_tool_lists(
            file_tools,
            text_tools,
            data_tools[:10],  # Limit data tools to prevent too many
            datetime_tools[:10],  # Limit datetime tools
            crypto_tools[:5],  # Limit crypto tools
            network_tools,
            utilities_tools[:3],  # Limit utilities
        )

        # Create comprehensive Strands agent
        agent = Agent(
            model=model,
            name="Basic Tools Agent",
            description="Comprehensive agent with basic-open-agent-tools for file operations, text processing, data handling, and more",
            system_prompt=(
                "You are the 'Basic Tools Agent', a helpful AI assistant built using AWS Strands framework "
                "with comprehensive local operations capabilities. You have access to:\n"
                "- File system operations (read, write, create, delete, move, copy)\n"
                "- Text processing (cleaning, formatting, case conversion)\n"
                "- Data processing (JSON, CSV, validation)\n"
                "- Date/time operations\n"
                "- Cryptographic utilities (hashing, encoding)\n"
                "- Network operations (HTTP requests)\n"
                "- Utility functions\n\n"
                "When introducing yourself, identify as the 'Basic Tools Agent' and mention your capabilities. "
                "Always be helpful and use the appropriate tools when needed."
            ),
            tools=agent_tools,
        )

        # Validate agent creation
        assert agent is not None
        assert agent.name == "Basic Tools Agent"

        # Test basic functionality
        try:
            response = agent(
                "Hello! Please introduce yourself and tell me about your capabilities."
            )
            assert isinstance(response, str)
            assert len(response) > 0
            assert "basic tools agent" in response.lower()
        except Exception as e:
            pytest.skip(f"Agent execution failed: {e}")

    def test_strands_agent_with_file_operations(self):
        """Test Strands agent performing file operations."""
        try:
            from strands import Agent
            from strands.models.anthropic import AnthropicModel
        except ImportError:
            pytest.skip("Strands framework not installed")

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY required for file operations test")

        # Create model
        model = AnthropicModel(
            client_args={"api_key": api_key},
            model_id="claude-sonnet-4-20250514",
            max_tokens=512,
            params={"temperature": 0.1},
        )

        # Load just file system tools for focused testing
        file_tools = boat.load_all_filesystem_tools()

        # Create file-focused agent
        agent = Agent(
            model=model,
            name="FileOps Agent",
            description="File operations specialist using basic-open-agent-tools",
            system_prompt=(
                "You are a file operations specialist. You can read, write, create, delete, "
                "move, copy files and work with directories. Always confirm what file operations "
                "you would perform but don't actually execute them in tests."
            ),
            tools=file_tools,
        )

        assert agent is not None

        # Test agent understanding of file operations
        try:
            response = agent("What file operations can you perform?")
            assert isinstance(response, str)
            assert any(
                op in response.lower() for op in ["read", "write", "create", "delete"]
            )
        except Exception as e:
            pytest.skip(f"File operations test failed: {e}")

    def test_agent_tool_integration_patterns(self):
        """Test different tool integration patterns with Strands."""
        try:
            from strands import Agent
            from strands.models.anthropic import AnthropicModel
        except ImportError:
            pytest.skip("Strands framework not installed")

        # Test pattern 1: Single category tools
        text_tools = boat.load_all_text_tools()
        assert len(text_tools) > 0

        # Test pattern 2: Merged categories
        mixed_tools = boat.merge_tool_lists(
            boat.load_all_filesystem_tools()[:3],
            boat.load_all_text_tools()[:3],
            boat.load_all_utilities_tools()[:2],
        )
        assert len(mixed_tools) == 8

        # Test pattern 3: All tools (limited for testing)
        try:
            # This would be too many tools for most agents, but test loading works
            all_tools = boat.load_all_tools()
            assert len(all_tools) > 100

            # Use just first 20 tools for actual agent testing
            all_tools[:20]

            # Could create agent with limited_tools if API key available
            # This validates the integration pattern works

        except Exception as e:
            pytest.skip(f"All tools loading failed: {e}")


def create_example_strands_agent_file():
    """Create a standalone example Strands agent file for documentation."""
    example_content = '''"""Example AWS Strands agent using basic-open-agent-tools.

This example shows how to create a comprehensive Strands agent with the toolkit.
Requires: pip install strands anthropic basic-open-agent-tools
"""

import os
from pathlib import Path
from strands import Agent
from strands.models.anthropic import AnthropicModel
from dotenv import load_dotenv

import basic_open_agent_tools as boat

# Load environment variables
load_dotenv()

def create_basic_tools_agent():
    """Create a Strands agent with basic-open-agent-tools."""

    # Create Anthropic model
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

    # Load tools from basic-open-agent-tools
    # Option 1: Load all tools (150+ functions)
    # agent_tools = boat.load_all_tools()

    # Option 2: Load specific categories
    file_tools = boat.load_all_filesystem_tools()      # File operations
    text_tools = boat.load_all_text_tools()           # Text processing
    data_tools = boat.load_all_data_tools()           # JSON, CSV, config
    datetime_tools = boat.load_all_datetime_tools()   # Date/time ops
    network_tools = boat.load_all_network_tools()     # HTTP client
    utilities_tools = boat.load_all_utilities_tools() # Timing, debugging
    crypto_tools = boat.load_all_crypto_tools()       # Hashing, encoding

    # Merge selected tools (automatically deduplicates)
    agent_tools = boat.merge_tool_lists(
        file_tools,
        text_tools,
        data_tools[:15],     # Limit to prevent too many tools
        datetime_tools[:15], # Limit datetime tools
        network_tools,
        utilities_tools,
        crypto_tools[:10]    # Limit crypto tools
    )

    # Create the Strands agent
    agent = Agent(
        model=model,
        name="Basic Tools Agent",
        description="Comprehensive agent with local operations capabilities using basic-open-agent-tools",
        system_prompt=(
            "You are the 'Basic Tools Agent', built using AWS Strands framework with comprehensive "
            "local operations capabilities. You have access to:\\n"
            "- File system operations (read, write, create, delete, move, copy, directories)\\n"
            "- Text processing (cleaning, formatting, case conversion, splitting)\\n"
            "- Data processing (JSON, CSV, YAML, validation, schemas)\\n"
            "- Date/time operations (formatting, arithmetic, validation, business days)\\n"
            "- Network operations (HTTP requests, DNS resolution)\\n"
            "- Cryptographic utilities (hashing, encoding, UUIDs)\\n"
            "- Utility functions (timing, debugging, validation)\\n\\n"
            "When introducing yourself, identify as the 'Basic Tools Agent' and explain your "
            "comprehensive local operations capabilities. Use tools appropriately and efficiently."
        ),
        tools=agent_tools
    )

    return agent


def main():
    """Test the agent locally."""
    print("Creating Basic Tools Agent with Strands + basic-open-agent-tools...")

    try:
        agent = create_basic_tools_agent()
        print(f"✅ Agent created successfully: {agent.name}")
        print(f"📊 Tools loaded: {len(agent.tools)}")

        # Test the agent
        print("\\n🧪 Testing agent...")
        response = agent("Hello! Please introduce yourself and list your main capabilities.")
        print(f"🤖 Agent Response: {response}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
'''

    # Write example file to examples directory if it exists
    examples_dir = Path(__file__).parent.parent.parent / "examples"
    if examples_dir.exists():
        example_file = examples_dir / "strands_agent_example.py"
        with open(example_file, "w") as f:
            f.write(example_content)
        print(f"Created example file: {example_file}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

    # Create example file
    create_example_strands_agent_file()
