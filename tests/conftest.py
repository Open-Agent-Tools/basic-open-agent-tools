"""Global pytest configuration for rate limiting."""

import os

import pytest


@pytest.fixture(autouse=True, scope="function")
def rate_limit_delay(request):
    """Add configurable delay only for agent evaluation tests to prevent API rate limiting."""
    yield
    # Only add delay for agent evaluation tests, not regular unit tests
    if request.node.get_closest_marker("agent_evaluation"):
        delay = float(os.getenv("PYTEST_API_DELAY", "5"))
        if delay > 0:
            import time
            time.sleep(delay)
