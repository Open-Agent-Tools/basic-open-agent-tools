"""Pytest configuration for Strands integration tests."""

import os

import pytest


def pytest_configure(config):
    """Configure pytest for Strands tests."""
    # Add custom markers
    config.addinivalue_line(
        "markers",
        "strands_integration: marks tests as requiring Strands integration (may require API keys)",
    )
    config.addinivalue_line(
        "markers",
        "strands_agent: marks tests that create and run actual Strands agents (requires API keys)",
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle Strands-specific markers."""
    # Auto-mark Strands tests
    for item in items:
        if "strands" in item.nodeid.lower():
            if not any(
                marker.name == "strands_integration" for marker in item.iter_markers()
            ):
                item.add_marker(pytest.mark.strands_integration)


@pytest.fixture
def strands_available():
    """Check if Strands framework is available."""
    try:
        import strands

        return True
    except ImportError:
        return False


@pytest.fixture
def anthropic_api_key():
    """Get Anthropic API key for testing."""
    return os.getenv("ANTHROPIC_API_KEY")


@pytest.fixture
def strands_integration_enabled():
    """Check if Strands integration tests are enabled."""
    return os.getenv("STRANDS_INTEGRATION_TEST") == "true"


@pytest.fixture
def basic_tools_sample():
    """Get a sample set of basic-open-agent-tools for testing."""
    import sys
    from pathlib import Path

    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

    import basic_open_agent_tools as boat

    # Return a manageable set of tools for testing
    return boat.merge_tool_lists(
        boat.load_all_filesystem_tools()[:5],
        boat.load_all_text_tools()[:3],
        boat.load_all_utilities_tools()[:2],
    )
