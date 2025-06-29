"""ADK evaluation tests for file system validation agent tools.

This test suite validates that file system validation functions work correctly
when called by AI agents in the Google ADK framework.
"""

import asyncio

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator


class TestValidationAgentEvaluation:
    """Agent evaluation tests for file system validation tools."""

    @pytest.mark.agent_evaluation
    @pytest.mark.asyncio
    async def test_list_available_tools_agent(self, agent_evaluation_sequential):
        """Test agent listing available tools."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_validation_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_validation_agent/list_available_tools.test.json",
        )
        await asyncio.sleep(2)  # Rate limiting delay
