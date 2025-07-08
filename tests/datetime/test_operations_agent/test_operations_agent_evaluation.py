"""ADK evaluation tests for datetime operations agent.

This test suite validates that datetime operations functions work correctly
when called by AI agents in the Google ADK framework.
"""

import asyncio

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator


class TestDateTimeOperationsAgentEvaluation:
    """Agent evaluation tests for datetime operations."""

    @pytest.mark.agent_evaluation
    @pytest.mark.asyncio
    async def test_list_available_tools_agent(self, agent_evaluation_sequential):
        """Test agent listing available tools."""
        await AgentEvaluator.evaluate(
            agent_module="tests.datetime.test_operations_agent.agent",
            eval_dataset_file_path_or_dir="tests/datetime/test_operations_agent/list_available_tools.test.json",
        )
        await asyncio.sleep(2)  # Rate limiting delay
