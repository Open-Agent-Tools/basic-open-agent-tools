"""ADK evaluation tests for helpers agent.

This test suite validates that helper functions work correctly
when called by AI agents in the Google ADK framework.
"""

import asyncio

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator


class TestHelpersAgentEvaluation:
    """Agent evaluation tests for helpers tools."""

    @pytest.mark.asyncio
    async def test_list_available_tools_agent(self):
        """Test agent listing available tools."""
        await AgentEvaluator.evaluate(
            agent_module="tests.helpers.test_helpers_agent.agent",
            eval_dataset_file_path_or_dir="tests/helpers/test_helpers_agent/list_all_available_tools.test.json",
        )
        await asyncio.sleep(2)  # Rate limiting delay
