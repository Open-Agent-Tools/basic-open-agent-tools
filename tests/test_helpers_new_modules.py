"""Tests for new module helper functions."""

from basic_open_agent_tools.helpers import (
    load_all_network_tools,
    load_all_utilities_tools,
    merge_tool_lists,
)
from basic_open_agent_tools.network.http_client import http_request
from basic_open_agent_tools.utilities.timing import sleep_seconds


class TestNetworkToolsLoader:
    """Test loading network tools."""

    def test_load_all_network_tools_returns_list(self):
        """Test that load_all_network_tools returns a list."""
        tools = load_all_network_tools()
        assert isinstance(tools, list)

    def test_load_all_network_tools_contains_http_request(self):
        """Test that network tools include http_request function."""
        tools = load_all_network_tools()
        assert http_request in tools

    def test_network_tools_are_callable(self):
        """Test that all network tools are callable."""
        tools = load_all_network_tools()
        for tool in tools:
            assert callable(tool)

    def test_network_tools_have_proper_signatures(self):
        """Test that network tools have the expected function signatures."""
        tools = load_all_network_tools()

        # Find http_request function
        http_request_func = None
        for tool in tools:
            if tool.__name__ == "http_request":
                http_request_func = tool
                break

        assert http_request_func is not None
        assert http_request_func.__name__ == "http_request"


class TestUtilitiesToolsLoader:
    """Test loading utilities tools."""

    def test_load_all_utilities_tools_returns_list(self):
        """Test that load_all_utilities_tools returns a list."""
        tools = load_all_utilities_tools()
        assert isinstance(tools, list)

    def test_load_all_utilities_tools_contains_sleep_seconds(self):
        """Test that utilities tools include sleep_seconds function."""
        tools = load_all_utilities_tools()
        assert sleep_seconds in tools

    def test_utilities_tools_are_callable(self):
        """Test that all utilities tools are callable."""
        tools = load_all_utilities_tools()
        for tool in tools:
            assert callable(tool)

    def test_utilities_tools_have_proper_signatures(self):
        """Test that utilities tools have the expected function signatures."""
        tools = load_all_utilities_tools()

        # Find sleep_seconds function
        sleep_seconds_func = None
        for tool in tools:
            if tool.__name__ == "sleep_seconds":
                sleep_seconds_func = tool
                break

        assert sleep_seconds_func is not None
        assert sleep_seconds_func.__name__ == "sleep_seconds"


class TestToolMerging:
    """Test merging tools from different modules."""

    def test_merge_network_and_utilities_tools(self):
        """Test merging network and utilities tools."""
        network_tools = load_all_network_tools()
        utilities_tools = load_all_utilities_tools()

        merged_tools = merge_tool_lists(network_tools, utilities_tools)

        assert len(merged_tools) == len(network_tools) + len(utilities_tools)
        assert http_request in merged_tools
        assert sleep_seconds in merged_tools

    def test_merge_handles_duplicates(self):
        """Test that merge_tool_lists handles duplicate functions."""
        network_tools = load_all_network_tools()

        # Try to merge with itself (should deduplicate)
        merged_tools = merge_tool_lists(network_tools, network_tools)

        assert len(merged_tools) == len(network_tools)

    def test_merge_empty_lists(self):
        """Test merging with empty lists."""
        network_tools = load_all_network_tools()

        merged_with_empty = merge_tool_lists(network_tools, [])
        assert len(merged_with_empty) == len(network_tools)

        merged_empty_with_tools = merge_tool_lists([], network_tools)
        assert len(merged_empty_with_tools) == len(network_tools)
