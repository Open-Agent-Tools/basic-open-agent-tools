"""Test A2A (Agent-to-Agent) protocol compatibility with basic-open-agent-tools.

This tests the compatibility of the toolkit with AWS Strands A2A protocol,
including agent card generation, request handling, and tool execution.
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import basic_open_agent_tools as boat


@pytest.mark.skipif(
    os.getenv("STRANDS_INTEGRATION_TEST") != "true",
    reason="A2A compatibility tests require STRANDS_INTEGRATION_TEST=true",
)
class TestA2ACompatibility:
    """Test A2A protocol compatibility."""

    def test_agent_card_generation(self):
        """Test that we can generate proper A2A agent cards."""
        try:
            from a2a.types import AgentCapabilities, AgentCard, AgentSkill
        except ImportError:
            pytest.skip("A2A framework not installed")

        # Create agent card with basic-open-agent-tools
        capabilities = AgentCapabilities(streaming=True, pushNotifications=True)

        # Define skills based on our toolkit capabilities
        skills = [
            AgentSkill(
                id="file_operations",
                name="File Operations",
                description="Read, write, create, delete, move, copy files and directories",
                tags=["file", "filesystem", "io"],
                examples=[
                    "Read the contents of config.json",
                    "Create a new directory called 'output'",
                    "Copy file1.txt to file2.txt",
                ],
            ),
            AgentSkill(
                id="text_processing",
                name="Text Processing",
                description="Clean, format, and transform text content",
                tags=["text", "string", "formatting"],
                examples=[
                    "Clean whitespace from text",
                    "Convert text to snake_case",
                    "Extract sentences from paragraph",
                ],
            ),
            AgentSkill(
                id="data_processing",
                name="Data Processing",
                description="Process JSON, CSV, YAML and other data formats",
                tags=["data", "json", "csv", "yaml"],
                examples=[
                    "Parse and validate JSON data",
                    "Read CSV file and extract columns",
                    "Convert data between formats",
                ],
            ),
        ]

        # Create agent card
        card = AgentCard(
            name="Basic Tools Agent",
            description="Comprehensive agent with basic-open-agent-tools for local operations",
            url="http://localhost:8087/",
            version="1.0.0",
            defaultInputModes=["text"],
            defaultOutputModes=["text"],
            capabilities=capabilities,
            skills=skills,
        )

        assert card is not None
        assert card.name == "Basic Tools Agent"
        assert len(card.skills) == 3
        assert card.capabilities.streaming is True

    def test_a2a_request_structure_compatibility(self):
        """Test that our tools work with A2A request structures."""
        # Mock A2A request structure
        mock_request = {
            "id": "test-request-123",
            "input": {
                "text": "Read file contents",
                "parameters": {"file_path": "/tmp/test.txt"},
            },
            "metadata": {
                "session_id": "session-456",
                "timestamp": "2024-09-15T12:00:00Z",
            },
        }

        # Test that we can extract parameters for our tools
        assert "parameters" in mock_request["input"]
        params = mock_request["input"]["parameters"]
        assert "file_path" in params

        # Our tools should be able to handle these parameter patterns
        # The function signature should match expected parameter extraction
        import inspect

        from basic_open_agent_tools.file_system import read_file_to_string

        sig = inspect.signature(read_file_to_string)
        param_names = list(sig.parameters.keys())

        # Should have file_path parameter
        assert "file_path" in param_names

    def test_a2a_response_structure_compatibility(self):
        """Test that tool outputs are compatible with A2A response structures."""
        # Test various tool return types
        from basic_open_agent_tools.crypto import generate_uuid4
        from basic_open_agent_tools.datetime import get_current_date
        from basic_open_agent_tools.text import clean_whitespace

        # Execute tools and check return types
        result1 = clean_whitespace("  test  ")
        result2 = get_current_date()
        result3 = generate_uuid4()

        # All results should be JSON-serializable for A2A responses
        test_response = {
            "id": "response-123",
            "status": "success",
            "output": {
                "cleaned_text": result1,
                "current_date": result2,
                "generated_uuid": result3,
            },
            "metadata": {
                "execution_time": 0.1,
                "tools_used": [
                    "clean_whitespace",
                    "get_current_date",
                    "generate_uuid4",
                ],
            },
        }

        # Should be JSON-serializable
        json_str = json.dumps(test_response)
        parsed = json.loads(json_str)
        assert parsed["status"] == "success"
        assert parsed["output"]["cleaned_text"] == "test"

    def test_a2a_error_handling_compatibility(self):
        """Test that tool errors are compatible with A2A error handling."""
        from basic_open_agent_tools.file_system import read_file_to_string

        # Test error handling
        try:
            read_file_to_string("/nonexistent/file.txt")
        except Exception as e:
            # Error should be serializable for A2A error responses
            error_response = {
                "id": "response-456",
                "status": "error",
                "error": {
                    "type": type(e).__name__,
                    "message": str(e),
                    "code": "FILE_NOT_FOUND",
                },
                "metadata": {
                    "tool": "read_file_to_string",
                    "parameters": {"file_path": "/nonexistent/file.txt"},
                },
            }

            # Should be JSON-serializable
            json_str = json.dumps(error_response)
            parsed = json.loads(json_str)
            assert parsed["status"] == "error"
            assert "message" in parsed["error"]

    @patch("strands.Agent")
    def test_a2a_executor_mock_integration(self, mock_agent_class):
        """Test integration with A2A executor (mocked)."""
        # Mock the Strands agent
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        # Mock agent execution
        mock_agent.return_value = "Task completed successfully"

        # Load tools for the agent
        tools = boat.merge_tool_lists(
            boat.load_all_filesystem_tools()[:3], boat.load_all_text_tools()[:2]
        )

        # Simulate creating agent with tools
        try:
            from strands.models.anthropic import AnthropicModel

            # This should work even with mocks
            model = AnthropicModel(
                client_args={"api_key": "mock_key"}, model_id="claude-sonnet-4-20250514"
            )

            # Create agent (mocked)
            agent = mock_agent_class(model=model, name="Test Agent", tools=tools)

            assert agent is not None
            mock_agent_class.assert_called_once()

        except ImportError:
            pytest.skip("Strands framework not available for mocking test")

    def test_context_isolation_compatibility(self):
        """Test that tools work with A2A context isolation."""
        # Test that tools can be executed in isolated contexts
        # This simulates how A2A handles context isolation

        from basic_open_agent_tools.crypto import generate_uuid4
        from basic_open_agent_tools.text import clean_whitespace

        # Simulate context-isolated execution
        context_1 = {"session_id": "session-1", "user": "user-1"}
        context_2 = {"session_id": "session-2", "user": "user-2"}

        # Tools should work independently in different contexts
        with patch.dict(os.environ, {"SESSION_ID": context_1["session_id"]}):
            result1 = clean_whitespace("  text1  ")
            uuid1 = generate_uuid4()

        with patch.dict(os.environ, {"SESSION_ID": context_2["session_id"]}):
            result2 = clean_whitespace("  text2  ")
            uuid2 = generate_uuid4()

        # Results should be independent
        assert result1 == "text1"
        assert result2 == "text2"
        assert uuid1 != uuid2  # UUIDs should be unique

    def test_tool_metadata_for_a2a(self):
        """Test that tools provide proper metadata for A2A introspection."""
        import basic_open_agent_tools as boat

        # Get tool info
        all_tools_info = boat.list_all_available_tools()

        assert isinstance(all_tools_info, list)
        assert len(all_tools_info) > 0

        # Each tool should have metadata suitable for A2A
        for tool_info in all_tools_info[:5]:  # Check first 5
            assert "name" in tool_info
            assert "module" in tool_info
            assert "description" in tool_info

            # Description should be useful for A2A agent cards
            assert len(tool_info["description"]) > 10

    def test_streaming_compatibility(self):
        """Test that tools can work with A2A streaming responses."""
        # Test that tool outputs can be streamed
        from basic_open_agent_tools.text import extract_sentences

        text = "This is sentence one. This is sentence two. This is sentence three."
        sentences = extract_sentences(text)

        # Should be able to stream sentences one by one
        for i, sentence in enumerate(sentences):
            stream_chunk = {
                "id": f"chunk-{i}",
                "type": "text",
                "content": sentence,
                "is_final": i == len(sentences) - 1,
            }

            # Should be JSON-serializable for streaming
            json.dumps(stream_chunk)  # Should not raise exception


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
