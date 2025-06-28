"""ADK evaluation tests for file system info agent tools.

This test suite validates that file system info functions work correctly
when called by AI agents in the Google ADK framework.
"""

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator


class TestInfoAgentEvaluation:
    """Agent evaluation tests for file system info tools."""

    @pytest.mark.asyncio
    async def test_info_basic_agent(self):
        """Test agent using basic info functions."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_info_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_info_agent/info_basic.test.json",
        )

    @pytest.mark.asyncio
    async def test_info_advanced_agent(self):
        """Test agent using advanced info scenarios."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_info_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_info_agent/info_advanced.test.json",
        )

    @pytest.mark.asyncio
    async def test_info_comprehensive_agent(self):
        """Test agent using comprehensive info workflows."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_info_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_info_agent/info_comprehensive.test.json",
        )
