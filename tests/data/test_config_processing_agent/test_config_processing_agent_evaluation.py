"""ADK evaluation tests for config processing agent.

This test suite validates that config processing functions work correctly
when called by AI agents in the Google ADK framework.
"""

import asyncio

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator


class TestConfigProcessingAgentEvaluation:
    """Agent evaluation tests for config processing tools."""

    @pytest.mark.agent_evaluation
    @pytest.mark.asyncio
    async def test_list_available_tools_agent(self):
        """Test agent listing available tools."""
        await AgentEvaluator.evaluate(
            agent_module="tests.data.test_config_processing_agent.agent",
            eval_dataset_file_path_or_dir="tests/data/test_config_processing_agent/list_available_tools.test.json",
        )
        await asyncio.sleep(2)  # Rate limiting delay
