"""Pytest configuration and fixtures for the project."""

import asyncio
import pytest


def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Ensure agent evaluation tests run sequentially
    config.addinivalue_line(
        "markers", "agent_evaluation: marks tests as agent evaluation tests (run sequentially)"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle agent evaluation tests specially."""
    agent_tests = []
    other_tests = []
    
    for item in items:
        if item.get_closest_marker("agent_evaluation"):
            agent_tests.append(item)
        else:
            other_tests.append(item)
    
    # Run regular tests first, then agent tests sequentially
    items[:] = other_tests + agent_tests


@pytest.fixture(scope="session")
def agent_evaluation_lock():
    """Provide a lock to ensure agent evaluation tests run sequentially."""
    return asyncio.Lock()


@pytest.fixture(autouse=True)
async def agent_evaluation_sequential(request, agent_evaluation_lock):
    """Ensure agent evaluation tests run one at a time."""
    if request.node.get_closest_marker("agent_evaluation"):
        async with agent_evaluation_lock:
            # Add extra delay between agent tests to prevent API rate limiting
            await asyncio.sleep(1)
            yield
            await asyncio.sleep(2)  # Extra delay after test completion
    else:
        yield