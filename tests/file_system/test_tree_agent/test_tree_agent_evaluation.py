"""ADK evaluation tests for tree generation agent tools.

This test suite validates that tree generation functions work correctly
when called by AI agents in the Google ADK framework.
"""

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator


class TestTreeAgentEvaluation:
    """Agent evaluation tests for tree generation tools."""

    @pytest.mark.asyncio
    async def test_list_all_directory_contents_agent(self):
        """Test agent using list_all_directory_contents function."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_tree_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_tree_agent/tree_list_all.test.json",
        )

    @pytest.mark.asyncio
    async def test_generate_directory_tree_agent(self):
        """Test agent using generate_directory_tree function."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_tree_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_tree_agent/tree_generate.test.json",
        )

    @pytest.mark.asyncio
    async def test_tree_tools_comprehensive_agent(self):
        """Test agent using both tree functions in complex scenarios."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_tree_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_tree_agent/tree_comprehensive.test.json",
        )
