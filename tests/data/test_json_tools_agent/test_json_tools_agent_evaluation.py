"""ADK evaluation tests for JSON tools agent.

This test suite validates that JSON tools functions work correctly
when called by AI agents in the Google ADK framework.
"""

import asyncio

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator


class TestJsonToolsAgentEvaluation:
    """Agent evaluation tests for JSON tools."""

    @pytest.mark.agent_evaluation
    @pytest.mark.asyncio
    async def test_list_available_tools_agent(self, agent_evaluation_sequential):
        """Test agent listing available tools."""
        await AgentEvaluator.evaluate(
            agent_module="tests.data.test_json_tools_agent.agent",
            eval_dataset_file_path_or_dir="tests/data/test_json_tools_agent/list_available_tools.test.json",
        )
        await asyncio.sleep(2)  # Rate limiting delay
