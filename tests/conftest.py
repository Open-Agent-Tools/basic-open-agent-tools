"""Global pytest configuration for rate limiting."""

import os

import pytest


@pytest.fixture(autouse=True, scope="function")
def rate_limit_delay():
    """Add configurable delay between tests to prevent API rate limiting."""
    yield
    delay = float(os.getenv("PYTEST_API_DELAY", "0"))
    if delay > 0:
        import time

        time.sleep(delay)
