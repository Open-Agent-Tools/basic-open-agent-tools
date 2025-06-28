"""ADK evaluation tests for file system operations agent tools.

This test suite validates that file system operations functions work correctly
when called by AI agents in the Google ADK framework.
"""

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator


class TestOperationsAgentEvaluation:
    """Agent evaluation tests for file system operations tools."""

    @pytest.mark.asyncio
    async def test_read_file_to_string_agent(self):
        """Test agent using read_file_to_string function."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_operations_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_operations_agent/read_file_to_string.test.json",
        )

    @pytest.mark.asyncio
    async def test_write_file_from_string_agent(self):
        """Test agent using write_file_from_string function."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_operations_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_operations_agent/write_file_from_string.test.json",
        )

    @pytest.mark.asyncio
    async def test_append_to_file_agent(self):
        """Test agent using append_to_file function."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_operations_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_operations_agent/append_to_file.test.json",
        )

    @pytest.mark.asyncio
    async def test_list_directory_contents_agent(self):
        """Test agent using list_directory_contents function."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_operations_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_operations_agent/list_directory_contents.test.json",
        )

    @pytest.mark.asyncio
    async def test_create_directory_agent(self):
        """Test agent using create_directory function."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_operations_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_operations_agent/create_directory.test.json",
        )

    @pytest.mark.asyncio
    async def test_delete_file_agent(self):
        """Test agent using delete_file function."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_operations_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_operations_agent/delete_file.test.json",
        )

    @pytest.mark.asyncio
    async def test_delete_directory_agent(self):
        """Test agent using delete_directory function."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_operations_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_operations_agent/delete_directory.test.json",
        )

    @pytest.mark.asyncio
    async def test_move_file_agent(self):
        """Test agent using move_file function."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_operations_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_operations_agent/move_file.test.json",
        )

    @pytest.mark.asyncio
    async def test_copy_file_agent(self):
        """Test agent using copy_file function."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_operations_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_operations_agent/copy_file.test.json",
        )

    @pytest.mark.asyncio
    async def test_replace_in_file_agent(self):
        """Test agent using replace_in_file function."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_operations_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_operations_agent/replace_in_file.test.json",
        )

    @pytest.mark.asyncio
    async def test_insert_at_line_agent(self):
        """Test agent using insert_at_line function."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_operations_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_operations_agent/insert_at_line.test.json",
        )

    @pytest.mark.asyncio
    async def test_operations_comprehensive_workflows_agent(self):
        """Test agent using multiple operations functions in complex workflows."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_operations_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_operations_agent/operations_comprehensive.test.json",
        )
