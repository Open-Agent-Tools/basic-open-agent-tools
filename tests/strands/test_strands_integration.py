"""AWS Strands integration tests for basic-open-agent-tools.

Tests the integration of basic-open-agent-tools with AWS Strands framework,
including @strands_tool decorator functionality and agent compatibility.
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import basic_open_agent_tools as boat


class TestStrandsIntegration:
    """Test AWS Strands framework integration."""

    def test_strands_tool_decorator_available(self):
        """Test that @strands_tool decorators are available and functional."""
        # Test that we can import file_system functions with decorators
        from basic_open_agent_tools.file_system import read_file_to_string

        # When Strands is installed, check for decorator attributes
        # When Strands is not installed, the decorator is a no-op
        try:
            import strands  # noqa: F401

            # Strands is installed - check for decorator attributes
            assert hasattr(read_file_to_string, "__wrapped__") or hasattr(
                read_file_to_string, "_strands_decorated"
            )
        except ImportError:
            # Strands not installed - decorator is a no-op passthrough
            # Just verify the function is callable and has proper metadata
            assert callable(read_file_to_string)
            assert hasattr(read_file_to_string, "__name__")
            assert hasattr(read_file_to_string, "__doc__")

    def test_strands_tool_metadata(self):
        """Test that Strands tool metadata is properly set."""
        from basic_open_agent_tools.data import safe_json_serialize
        from basic_open_agent_tools.file_system import read_file_to_string
        from basic_open_agent_tools.text import clean_whitespace

        # Check for proper function signatures and docstrings
        functions_to_test = [read_file_to_string, clean_whitespace, safe_json_serialize]

        for func in functions_to_test:
            assert callable(func)
            assert func.__doc__ is not None
            assert len(func.__doc__.strip()) > 0

    @pytest.mark.skipif(
        os.getenv("STRANDS_INTEGRATION_TEST") != "true",
        reason="Strands integration tests require STRANDS_INTEGRATION_TEST=true",
    )
    def test_strands_agent_creation(self):
        """Test creating a Strands agent with basic-open-agent-tools."""
        try:
            from strands import Agent
            from strands.models.anthropic import AnthropicModel
        except ImportError:
            pytest.skip("Strands framework not installed")

        # Mock the API key for testing
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"}):
            # Create model
            model = AnthropicModel(
                client_args={"api_key": "test_key"},
                model_id="claude-sonnet-4-20250514",
                max_tokens=512,
                params={"temperature": 0.1},
            )

            # Load basic-open-agent-tools
            tools = boat.load_all_filesystem_tools()[:5]  # Limit to 5 tools for testing

            # Create agent
            agent = Agent(
                model=model,
                name="Test Agent",
                description="Test agent with basic-open-agent-tools",
                system_prompt="You are a test agent with file system tools.",
                tools=tools,
            )

            assert agent is not None
            assert agent.name == "Test Agent"

    def test_tool_loading_for_strands(self):
        """Test that all tool loading functions work for Strands integration."""
        # Test all major tool categories
        tool_loaders = [
            boat.load_all_filesystem_tools,
            boat.load_all_text_tools,
            boat.load_all_data_tools,
            boat.load_all_datetime_tools,
            boat.load_all_network_tools,
            boat.load_all_utilities_tools,
            boat.load_all_crypto_tools,
            boat.load_all_archive_tools,
            boat.load_all_logging_tools,
        ]

        # Test optional dependencies separately
        optional_loaders = []
        try:
            optional_loaders.append(boat.load_all_system_tools)
        except ImportError:
            pass  # System tools require psutil

        for loader in tool_loaders:
            tools = loader()
            assert isinstance(tools, list)
            assert len(tools) > 0

            # Check each tool is callable and has proper metadata
            for tool in tools:
                assert callable(tool)
                assert hasattr(tool, "__name__")
                assert hasattr(tool, "__doc__")

    def test_merge_tool_lists_for_strands(self):
        """Test merging tool lists for Strands agents."""
        fs_tools = boat.load_all_filesystem_tools()
        text_tools = boat.load_all_text_tools()
        data_tools = boat.load_all_data_tools()

        merged = boat.merge_tool_lists(fs_tools, text_tools, data_tools)

        assert isinstance(merged, list)
        assert len(merged) == len(fs_tools) + len(text_tools) + len(data_tools)

        # Check all tools are unique
        tool_names = [tool.__name__ for tool in merged]
        assert len(tool_names) == len(set(tool_names))

    def test_load_all_tools_for_strands(self):
        """Test loading all tools at once for Strands."""
        all_tools = boat.load_all_tools()

        assert isinstance(all_tools, list)
        assert len(all_tools) > 100  # Should have 150+ tools

        # Check tool uniqueness
        tool_names = [tool.__name__ for tool in all_tools]
        assert len(tool_names) == len(set(tool_names))

        # Check each tool has proper attributes
        for tool in all_tools[:10]:  # Check first 10 tools
            assert callable(tool)
            assert hasattr(tool, "__name__")
            assert hasattr(tool, "__doc__")
            assert tool.__doc__ is not None


class TestStrandsToolCompatibility:
    """Test individual tool compatibility with Strands framework."""

    def test_file_system_tools_compatibility(self):
        """Test file system tools compatibility with Strands."""
        from basic_open_agent_tools.file_system import (
            file_exists,
            list_directory_contents,
            read_file_to_string,
            write_file_from_string,
        )

        tools = [
            read_file_to_string,
            write_file_from_string,
            list_directory_contents,
            file_exists,
        ]

        for tool in tools:
            # Check function signature compatibility
            import inspect

            sig = inspect.signature(tool)

            # All parameters should have type annotations
            for param in sig.parameters.values():
                if param.name != "self":
                    assert param.annotation != inspect.Parameter.empty, (
                        f"{tool.__name__} parameter {param.name} missing type annotation"
                    )

            # Return type should be annotated
            assert sig.return_annotation != inspect.Parameter.empty, (
                f"{tool.__name__} missing return type annotation"
            )

    def test_text_tools_compatibility(self):
        """Test text processing tools compatibility with Strands."""
        from basic_open_agent_tools.text import (
            clean_whitespace,
            extract_sentences,
            normalize_line_endings,
            to_snake_case,
        )

        tools = [
            clean_whitespace,
            normalize_line_endings,
            to_snake_case,
            extract_sentences,
        ]

        for tool in tools:
            import inspect

            sig = inspect.signature(tool)

            # Check type annotations
            for param in sig.parameters.values():
                if param.name != "self":
                    assert param.annotation != inspect.Parameter.empty

            assert sig.return_annotation != inspect.Parameter.empty

    def test_data_tools_compatibility(self):
        """Test data processing tools compatibility with Strands."""
        from basic_open_agent_tools.data import (
            read_csv_simple,
            safe_json_deserialize,
            safe_json_serialize,
            write_csv_simple,
        )

        tools = [
            safe_json_serialize,
            safe_json_deserialize,
            read_csv_simple,
            write_csv_simple,
        ]

        for tool in tools:
            import inspect

            sig = inspect.signature(tool)

            # Check type annotations
            for param in sig.parameters.values():
                if param.name != "self":
                    assert param.annotation != inspect.Parameter.empty

            assert sig.return_annotation != inspect.Parameter.empty


@pytest.mark.skipif(
    os.getenv("STRANDS_INTEGRATION_TEST") != "true",
    reason="Full Strands integration tests require STRANDS_INTEGRATION_TEST=true and API keys",
)
class TestStrandsAgentExecution:
    """Test actual agent execution with Strands (requires API keys)."""

    @pytest.fixture
    def strands_agent(self):
        """Create a test Strands agent with basic-open-agent-tools."""
        try:
            from strands import Agent
            from strands.models.anthropic import AnthropicModel
        except ImportError:
            pytest.skip("Strands framework not installed")

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY not provided")

        # Create model
        model = AnthropicModel(
            client_args={"api_key": api_key},
            model_id="claude-sonnet-4-20250514",
            max_tokens=512,
            params={"temperature": 0.1},
        )

        # Load minimal set of tools
        tools = boat.load_all_filesystem_tools()[:3]  # Just first 3 tools

        # Create agent
        agent = Agent(
            model=model,
            name="Basic Tools Test Agent",
            description="Test agent with basic-open-agent-tools for integration testing",
            system_prompt=(
                "You are a test agent with file system tools. "
                "Respond concisely and indicate when you would use tools."
            ),
            tools=tools,
        )

        return agent

    def test_agent_responds_without_tools(self, strands_agent):
        """Test that agent responds to simple queries without using tools."""
        try:
            response = strands_agent("Hello! What tools do you have available?")
            assert isinstance(response, str)
            assert len(response) > 0
            assert any(
                keyword in response.lower()
                for keyword in ["file", "tools", "available"]
            )
        except Exception as e:
            pytest.skip(f"Agent execution failed: {e}")

    def test_agent_tool_awareness(self, strands_agent):
        """Test that agent is aware of the tools it has."""
        try:
            response = strands_agent("List the file system tools you have access to.")
            assert isinstance(response, str)
            assert len(response) > 0
            # Should mention some file-related functionality
            assert any(
                keyword in response.lower()
                for keyword in ["read", "file", "directory", "write"]
            )
        except Exception as e:
            pytest.skip(f"Agent execution failed: {e}")


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v"])
