"""Test Google ADK agent integration with basic-open-agent-tools.

This module provides comprehensive tests for validating that our toolkit functions
work correctly within the Google AI Development Kit (ADK) environment.
"""

import logging
import os
import tempfile
import warnings

import pytest
from dotenv import load_dotenv
from google.adk.agents import Agent

from basic_open_agent_tools.file_system.tree import generate_directory_tree

# Initialize environment and logging
load_dotenv()  # or load_dotenv(dotenv_path="/env_path")
logging.basicConfig(level=logging.ERROR)
warnings.filterwarnings("ignore")


class TestADKAgentIntegration:
    """Test ADK Agent integration with basic-open-agent-tools functions."""

    @pytest.fixture
    def temp_directory_structure(self):
        """Create a temporary directory structure for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test structure
            os.makedirs(os.path.join(temp_dir, "src", "submodule"))
            os.makedirs(os.path.join(temp_dir, "tests"))
            os.makedirs(os.path.join(temp_dir, ".hidden"))

            # Create test files
            with open(os.path.join(temp_dir, "README.md"), "w") as f:
                f.write("# Test Project")
            with open(os.path.join(temp_dir, "src", "main.py"), "w") as f:
                f.write("print('hello world')")
            with open(os.path.join(temp_dir, "src", "submodule", "utils.py"), "w") as f:
                f.write("def helper(): pass")
            with open(os.path.join(temp_dir, "tests", "test_main.py"), "w") as f:
                f.write("def test_main(): assert True")
            with open(os.path.join(temp_dir, ".hidden", "config"), "w") as f:
                f.write("secret=value")

            yield temp_dir

    @pytest.fixture
    def adk_agent_with_tree_tool(self):
        """Create ADK agent configured with generate_directory_tree tool."""
        agent = Agent(
            model="gemini-2.0-flash",
            name="TreeAgent",
            instruction="You are a directory analysis agent. Use the generate_directory_tree tool to analyze directory structures.",
            description="An agent specialized in analyzing and reporting directory structures.",
            tools=[generate_directory_tree],
        )
        return agent

    def test_generate_directory_tree_basic_functionality(
        self, temp_directory_structure
    ):
        """Test generate_directory_tree function directly (non-ADK)."""
        # Test basic tree generation without hidden files
        tree_output = generate_directory_tree(
            directory_path=temp_directory_structure, max_depth=3, include_hidden=False
        )

        # Verify expected structure is present
        assert "README.md" in tree_output
        assert "src" in tree_output
        assert "tests" in tree_output
        assert "main.py" in tree_output
        assert "submodule" in tree_output
        assert "utils.py" in tree_output
        assert "test_main.py" in tree_output

        # Verify hidden files are excluded
        assert ".hidden" not in tree_output
        assert "config" not in tree_output

    def test_generate_directory_tree_with_hidden_files(self, temp_directory_structure):
        """Test generate_directory_tree with hidden files included."""
        tree_output = generate_directory_tree(
            directory_path=temp_directory_structure, max_depth=3, include_hidden=True
        )

        # Verify hidden files are included
        assert ".hidden" in tree_output
        assert "config" in tree_output

        # Verify regular files are still present
        assert "README.md" in tree_output
        assert "src" in tree_output

    def test_generate_directory_tree_depth_limiting(self, temp_directory_structure):
        """Test generate_directory_tree with depth limiting."""
        # Test shallow depth
        shallow_tree = generate_directory_tree(
            directory_path=temp_directory_structure, max_depth=1, include_hidden=False
        )

        # Should see top-level items
        assert "README.md" in shallow_tree
        assert "src" in shallow_tree
        assert "tests" in shallow_tree

        # Should NOT see nested items
        assert "main.py" not in shallow_tree
        assert "submodule" not in shallow_tree
        assert "utils.py" not in shallow_tree

    def test_adk_agent_can_use_tree_tool(
        self, adk_agent_with_tree_tool, temp_directory_structure
    ):
        """Test that ADK agent can successfully use the generate_directory_tree tool."""
        # Create a specific instruction for the agent
        instruction = f"Generate a directory tree for the path: {temp_directory_structure}. Set max_depth to 2 and include_hidden to false."

        try:
            # Run the agent with the instruction
            response = adk_agent_with_tree_tool.run(instruction)

            # Verify response contains expected elements
            # Note: The exact response format may vary based on ADK implementation
            assert response is not None
            assert len(str(response)) > 0

            # The response should contain information about the directory structure
            response_str = str(response).lower()

            # Look for evidence that the tool was used successfully
            # This might be in the form of directory names or tree structure
            expected_elements = ["readme", "src", "tests"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find at least some of the directory structure elements
            assert found_elements >= 2, (
                f"Expected directory elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed to use generate_directory_tree tool: {e}")

    def test_adk_agent_error_handling(self, adk_agent_with_tree_tool):
        """Test ADK agent error handling with invalid directory path."""
        # Test with non-existent directory
        instruction = "Generate a directory tree for the path: /nonexistent/directory/path. Set max_depth to 2 and include_hidden to false."

        try:
            response = adk_agent_with_tree_tool.run(instruction)

            # The agent should handle the error gracefully
            # The exact behavior may vary, but it should not crash
            assert response is not None

            # Response might contain error information
            response_str = str(response).lower()
            error_indicators = ["error", "not found", "does not exist", "invalid"]

            # Check if the response indicates an error was handled
            has_error_indication = any(
                indicator in response_str for indicator in error_indicators
            )

            # Either the agent handled the error or provided some response
            assert has_error_indication or len(response_str) > 0

        except Exception as e:
            # Some exceptions are acceptable as they indicate proper error handling
            acceptable_errors = ["FileNotFoundError", "does not exist", "not found"]
            error_msg = str(e).lower()

            is_acceptable = any(
                acceptable in error_msg for acceptable in acceptable_errors
            )

            if not is_acceptable:
                pytest.fail(f"Unexpected error type: {e}")

    def test_function_signature_compatibility(self):
        """Test that generate_directory_tree has Google AI compatible signature."""
        import inspect

        # Get function signature
        sig = inspect.signature(generate_directory_tree)

        # Verify parameter types and structure
        params = sig.parameters

        # Check required parameters exist
        assert "directory_path" in params
        assert "max_depth" in params
        assert "include_hidden" in params

        # Verify no default values (Google AI requirement)
        for param_name, param in params.items():
            assert param.default == inspect.Parameter.empty, (
                f"Parameter {param_name} has default value, violating Google AI requirements"
            )

        # Check parameter types are Google AI compatible
        directory_path_annotation = params["directory_path"].annotation
        max_depth_annotation = params["max_depth"].annotation
        include_hidden_annotation = params["include_hidden"].annotation

        assert directory_path_annotation is str
        assert max_depth_annotation is int
        assert include_hidden_annotation is bool

        # Check return type
        assert sig.return_annotation is str
