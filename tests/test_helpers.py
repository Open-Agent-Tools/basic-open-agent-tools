"""Tests for helper functions module."""

import pytest

import basic_open_agent_tools as boat
from basic_open_agent_tools.helpers import (
    get_tool_info,
    list_all_available_tools,
    load_all_filesystem_tools,
    load_all_text_tools,
    merge_tool_lists,
)


class TestHelperFunctions:
    """Test cases for helper functions."""

    def test_load_all_filesystem_tools(self):
        """Test loading all file system tools."""
        fs_tools = load_all_filesystem_tools()

        # Should return a list
        assert isinstance(fs_tools, list)

        # Should have tools
        assert len(fs_tools) > 0

        # All items should be callable
        for tool in fs_tools:
            assert callable(tool)

        # Should include key file system functions
        tool_names = [tool.__name__ for tool in fs_tools]
        assert "read_file_to_string" in tool_names
        assert "write_file_from_string" in tool_names
        assert "file_exists" in tool_names

    def test_load_all_text_tools(self):
        """Test loading all text processing tools."""
        text_tools = load_all_text_tools()

        # Should return a list
        assert isinstance(text_tools, list)

        # Should have tools
        assert len(text_tools) > 0

        # All items should be callable
        for tool in text_tools:
            assert callable(tool)

        # Should include key text processing functions
        tool_names = [tool.__name__ for tool in text_tools]
        assert "clean_whitespace" in tool_names
        assert "to_snake_case" in tool_names
        assert "strip_html_tags" in tool_names

    def test_merge_tool_lists_with_lists(self):
        """Test merging multiple tool lists."""
        fs_tools = load_all_filesystem_tools()
        text_tools = load_all_text_tools()

        merged = merge_tool_lists(fs_tools, text_tools)

        # Should return a list
        assert isinstance(merged, list)

        # Should contain all tools from both lists
        assert len(merged) == len(fs_tools) + len(text_tools)

        # All items should be callable
        for tool in merged:
            assert callable(tool)

    def test_merge_tool_lists_with_individual_functions(self):
        """Test merging with individual functions."""

        def custom_tool_1(x: str) -> str:
            return x.upper()

        def custom_tool_2(x: str) -> str:
            return x.lower()

        fs_tools = load_all_filesystem_tools()

        merged = merge_tool_lists(fs_tools, custom_tool_1, custom_tool_2)

        # Should include all original tools plus custom ones
        assert len(merged) == len(fs_tools) + 2

        # Custom tools should be included
        assert custom_tool_1 in merged
        assert custom_tool_2 in merged

    def test_merge_tool_lists_mixed_args(self):
        """Test merging with mixed list and function arguments."""

        def custom_tool(x: str) -> str:
            return x + "_custom"

        fs_tools = load_all_filesystem_tools()
        text_tools = load_all_text_tools()

        merged = merge_tool_lists(fs_tools, custom_tool, text_tools)

        # Should include all tools
        expected_length = len(fs_tools) + 1 + len(text_tools)
        assert len(merged) == expected_length

        # Custom tool should be included
        assert custom_tool in merged

    def test_merge_tool_lists_empty_lists(self):
        """Test merging with empty lists."""

        def custom_tool(x: str) -> str:
            return x

        merged = merge_tool_lists([], custom_tool, [])

        assert len(merged) == 1
        assert custom_tool in merged

    def test_merge_tool_lists_invalid_arguments(self):
        """Test error handling for invalid arguments."""
        # Test with non-callable in list
        with pytest.raises(TypeError):
            merge_tool_lists(["not_callable"])

        # Test with invalid argument type
        with pytest.raises(TypeError):
            merge_tool_lists("not_a_list_or_function")

        # Test with mixed valid and invalid
        def valid_tool():
            pass

        with pytest.raises(TypeError):
            merge_tool_lists([valid_tool, "invalid"])

    def test_merge_tool_lists_deduplication(self):
        """Test that merge_tool_lists removes duplicate functions."""
        # Load the same tools multiple times
        fs_tools_1 = load_all_filesystem_tools()
        fs_tools_2 = load_all_filesystem_tools()

        # Merge with duplicates
        merged = merge_tool_lists(fs_tools_1, fs_tools_2)

        # Should have same length as single load (duplicates removed)
        assert len(merged) == len(fs_tools_1)

        # Check that no function name appears twice
        function_names = [tool.__name__ for tool in merged]
        unique_names = set(function_names)
        assert len(function_names) == len(unique_names), (
            "Found duplicate function names"
        )

        # Should still contain all expected functions
        expected_names = [tool.__name__ for tool in fs_tools_1]
        for name in expected_names:
            assert name in function_names, f"Missing function: {name}"

    def test_merge_tool_lists_different_modules_same_name(self):
        """Test handling of functions with same name from different modules."""

        # Create two functions with the same name but different modules
        def test_function():
            return "first"

        def another_test_function():
            return "second"

        # Manually set different module names to simulate different sources
        test_function.__module__ = "module1"
        another_test_function.__module__ = "module2"
        another_test_function.__name__ = "test_function"  # Same name as first

        merged = merge_tool_lists([test_function], [another_test_function])

        # Should keep both since they're from different modules
        assert len(merged) == 2
        assert test_function in merged
        assert another_test_function in merged

    def test_get_tool_info(self):
        """Test getting information about a tool."""
        from basic_open_agent_tools.text import clean_whitespace

        info = get_tool_info(clean_whitespace)

        # Should return a dictionary
        assert isinstance(info, dict)

        # Should contain expected keys
        expected_keys = ["name", "docstring", "signature", "module", "parameters"]
        for key in expected_keys:
            assert key in info

        # Should have correct name
        assert info["name"] == "clean_whitespace"

        # Should have docstring
        assert len(info["docstring"]) > 0

        # Should have parameters
        assert "text" in info["parameters"]

    def test_get_tool_info_invalid_input(self):
        """Test error handling for get_tool_info."""
        with pytest.raises(TypeError):
            get_tool_info("not_a_function")

        with pytest.raises(TypeError):
            get_tool_info(123)

    def test_list_all_available_tools(self):
        """Test listing all available tools."""
        tools = list_all_available_tools()

        # Should return a dictionary
        assert isinstance(tools, dict)

        # Should have expected categories
        assert "file_system" in tools
        assert "text" in tools
        assert "data" in tools

        # Each category should contain tool info
        for _category, category_tools in tools.items():
            assert isinstance(category_tools, list)
            for tool_info in category_tools:
                assert isinstance(tool_info, dict)
                assert "name" in tool_info
                assert "docstring" in tool_info
                assert "signature" in tool_info

    def test_top_level_imports(self):
        """Test that helper functions are available at top level."""
        # Test direct import from package
        assert hasattr(boat, "load_all_filesystem_tools")
        assert hasattr(boat, "load_all_text_tools")
        assert hasattr(boat, "merge_tool_lists")
        assert hasattr(boat, "get_tool_info")
        assert hasattr(boat, "list_all_available_tools")

        # Test that they're callable
        assert callable(boat.load_all_filesystem_tools)
        assert callable(boat.load_all_text_tools)
        assert callable(boat.merge_tool_lists)


class TestHelperFunctionsIntegration:
    """Integration tests for helper functions."""

    def test_complete_workflow(self):
        """Test the complete workflow as described in the user request."""
        # Load tool collections
        fs_tools = boat.load_all_filesystem_tools()
        text_tools = boat.load_all_text_tools()

        # Create custom tool
        def my_custom_tool(some_var: str) -> str:
            return some_var + some_var

        # Merge all tools
        agent_tools = boat.merge_tool_lists(fs_tools, text_tools, my_custom_tool)

        # Verify results
        assert isinstance(agent_tools, list)
        assert len(agent_tools) > 0

        # Should contain tools from all sources
        expected_min_length = len(fs_tools) + len(text_tools) + 1
        assert len(agent_tools) == expected_min_length

        # Custom tool should be included
        assert my_custom_tool in agent_tools

        # All should be callable
        for tool in agent_tools:
            assert callable(tool)

    def test_tool_discovery(self):
        """Test discovering tools and their capabilities."""
        # Get all available tools
        all_tools = boat.list_all_available_tools()

        # Should find both categories
        assert len(all_tools) >= 2

        # Each category should have tools
        for _category, tools in all_tools.items():
            assert len(tools) > 0

            # Each tool should have complete info
            for tool_info in tools:
                assert tool_info["name"]
                assert "signature" in tool_info
                assert "parameters" in tool_info

    def test_tool_inspection(self):
        """Test inspecting individual tools."""
        fs_tools = boat.load_all_filesystem_tools()

        # Pick a tool to inspect
        sample_tool = fs_tools[0]
        info = boat.get_tool_info(sample_tool)

        # Should have complete information
        assert info["name"]
        assert info["signature"]
        assert isinstance(info["parameters"], list)

        # Should be able to identify the tool's module
        assert "basic_open_agent_tools" in info["module"]
