"""ADK evaluation tests for file system validation agent tools.

This test suite validates that file system validation functions work correctly
when called by AI agents in the Google ADK framework.
"""

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator


class TestValidationAgentEvaluation:
    """Agent evaluation tests for file system validation tools."""

    @pytest.mark.asyncio
    async def test_validate_path_agent(self):
        """Test agent using validate_path function."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_validation_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_validation_agent/validate_path.test.json",
        )

    @pytest.mark.asyncio
    async def test_validate_file_content_agent(self):
        """Test agent using validate_file_content function."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_validation_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_validation_agent/validate_file_content.test.json",
        )

    @pytest.mark.asyncio
    async def test_validation_comprehensive_workflows_agent(self):
        """Test agent using multiple validation functions in workflows."""
        await AgentEvaluator.evaluate(
            agent_module="tests.file_system.test_validation_agent.agent",
            eval_dataset_file_path_or_dir="tests/file_system/test_validation_agent/validation_comprehensive.test.json",
        )
