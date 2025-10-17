"""ADK evaluation test for tree generation agent.

This test demonstrates the simplest possible ADK evaluation using the
basic_open_agent_tools file system utilities.
"""

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator


class TestTreeAgentEvaluation:
    """Test cases for tree generation agent evaluation."""

    @pytest.mark.asyncio
    async def test_with_single_test_file(self):
        """Test the agent's basic ability via a session file."""
        await AgentEvaluator.evaluate(
            agent_module="examples.adk_evaluation.tree_agent",
            eval_dataset_file_path_or_dir="examples/adk_evaluation/tree_generation.test.json",
        )
