"""ADK evaluation tests for tree generation agent tools.

This test suite validates that tree generation functions work correctly
when called by AI agents in the Google ADK framework.
"""

import asyncio

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator


class TestTreeAgentEvaluation:
    """Agent evaluation tests for tree generation tools."""

    @pytest.mark.asyncio
    async def test_list_available_tools_agent(self):
        """Test agent listing available tools."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_tree_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_tree_agent/list_available_tools.test.json",
        )
        await asyncio.sleep(2)  # Rate limiting delay
