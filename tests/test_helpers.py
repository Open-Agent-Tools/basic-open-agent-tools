"""Tests for helper functions module.

This module provides comprehensive tests for the helper functions toolkit,
including unit tests, integration tests, and Google AI compatibility verification.
"""

import inspect
import logging
import warnings

import pytest
from dotenv import load_dotenv
from google.adk.agents import Agent

import basic_open_agent_tools as boat
from basic_open_agent_tools.helpers import (
    get_tool_info,
    list_all_available_tools,
    load_all_filesystem_tools,
    load_all_text_tools,
    merge_tool_lists,
)

# Initialize environment and logging
load_dotenv()
logging.basicConfig(level=logging.ERROR)
warnings.filterwarnings("ignore")


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


class TestADKAgentIntegration:
    """Test ADK Agent integration with helper functions and tool management."""

    @pytest.fixture
    def adk_agent_with_mixed_tools(self):
        """Create ADK agent configured with tools loaded via helper functions."""
        # Load tools using helper functions
        fs_tools = load_all_filesystem_tools()
        text_tools = load_all_text_tools()

        # Select a subset of tools for the agent
        selected_tools = []

        # Add some file system tools
        for tool in fs_tools:
            if tool.__name__ in [
                "read_file_to_string",
                "write_file_from_string",
                "file_exists",
            ]:
                selected_tools.append(tool)

        # Add some text tools
        for tool in text_tools:
            if tool.__name__ in [
                "clean_whitespace",
                "to_snake_case",
                "strip_html_tags",
            ]:
                selected_tools.append(tool)

        # Use merge_tool_lists to combine them
        final_tools = merge_tool_lists(selected_tools)

        agent = Agent(
            model="gemini-2.0-flash",
            name="ToolManagementAgent",
            instruction="You are a tool management agent. Use the available file system and text processing tools to perform various tasks.",
            description="An agent with tools loaded via helper functions, demonstrating tool management capabilities.",
            tools=final_tools,
        )
        return agent

    @pytest.fixture
    def adk_agent_with_all_tools(self):
        """Create ADK agent configured with all available tools via helpers."""
        # Load all available tools using helper functions
        fs_tools = load_all_filesystem_tools()
        text_tools = load_all_text_tools()

        # Merge all tools
        all_tools = merge_tool_lists(fs_tools, text_tools)

        agent = Agent(
            model="gemini-2.0-flash",
            name="ComprehensiveToolAgent",
            instruction="You are a comprehensive tool agent with access to all file system and text processing tools. Use them to perform complex workflows.",
            description="An agent with comprehensive tool access via helper function loading.",
            tools=all_tools,
        )
        return agent

    def test_load_all_filesystem_tools_basic_functionality(self):
        """Test load_all_filesystem_tools function directly (non-ADK)."""
        fs_tools = load_all_filesystem_tools()

        # Should return a list
        assert isinstance(fs_tools, list)
        assert len(fs_tools) > 0

        # All items should be callable
        for tool in fs_tools:
            assert callable(tool)

        # Should include key file system functions
        tool_names = [tool.__name__ for tool in fs_tools]
        assert "read_file_to_string" in tool_names
        assert "write_file_from_string" in tool_names
        assert "file_exists" in tool_names

    def test_load_all_text_tools_basic_functionality(self):
        """Test load_all_text_tools function directly (non-ADK)."""
        text_tools = load_all_text_tools()

        # Should return a list
        assert isinstance(text_tools, list)
        assert len(text_tools) > 0

        # All items should be callable
        for tool in text_tools:
            assert callable(tool)

        # Should include key text processing functions
        tool_names = [tool.__name__ for tool in text_tools]
        assert "clean_whitespace" in tool_names
        assert "to_snake_case" in tool_names
        assert "strip_html_tags" in tool_names

    def test_adk_agent_can_list_helper_loaded_tools(self, adk_agent_with_mixed_tools):
        """Test that ADK agent can list tools loaded via helper functions."""
        instruction = "List all your available tools"

        try:
            response = adk_agent_with_mixed_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Spot check for specific tools that should be available
            # Based on our fixture, we expect these file system and text tools
            expected_tools = ["read_file_to_string", "clean_whitespace"]
            found_tools = sum(1 for tool in expected_tools if tool in response_str)

            # We expect to find at least these 2 specific tool names
            assert found_tools >= 2, (
                f"Expected tool names {expected_tools} not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed to list helper-loaded tools: {e}")

    def test_adk_agent_can_use_helper_loaded_tools(self, adk_agent_with_mixed_tools):
        """Test that ADK agent can use tools loaded via helper functions."""
        instruction = (
            'Clean this text and convert to snake_case: "  Hello World Test  "'
        )

        try:
            response = adk_agent_with_mixed_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence that helper-loaded tools were used
            expected_elements = ["hello", "world", "test", "clean", "snake"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of successful tool usage
            assert found_elements >= 2, (
                f"Expected helper-loaded tool usage elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed to use helper-loaded tools: {e}")

    def test_merge_tool_lists_basic_functionality(self):
        """Test merge_tool_lists function directly (non-ADK)."""
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

        # Test with individual functions
        def custom_tool(x: str) -> str:
            return x.upper()

        merged_with_custom = merge_tool_lists(fs_tools, custom_tool)
        assert len(merged_with_custom) == len(fs_tools) + 1
        assert custom_tool in merged_with_custom

    def test_adk_agent_can_list_all_comprehensive_tools(self, adk_agent_with_all_tools):
        """Test that ADK agent can list all tools loaded via load_all functions."""
        instruction = "List all your available tools"

        try:
            response = adk_agent_with_all_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Spot check for specific tools from both file system and text categories
            # Based on our fixture that loads all fs and text tools
            expected_tools = ["write_file_from_string", "to_snake_case"]
            found_tools = sum(1 for tool in expected_tools if tool in response_str)

            # We expect to find at least these 2 specific tool names
            assert found_tools >= 2, (
                f"Expected tool names {expected_tools} not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed to list comprehensive tools: {e}")

    def test_adk_agent_with_comprehensive_tools(self, adk_agent_with_all_tools):
        """Test ADK agent with comprehensive tool set loaded via helpers."""
        instruction = 'Create a simple text file with cleaned content: write "  Hello World!  " to a file after cleaning whitespace'

        try:
            response = adk_agent_with_all_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of comprehensive tool usage
            expected_elements = ["hello world", "file", "write", "clean", "text"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of comprehensive tool usage
            assert found_elements >= 2, (
                f"Expected comprehensive tool usage elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed with comprehensive tools: {e}")

    def test_get_tool_info_basic_functionality(self):
        """Test get_tool_info function directly (non-ADK)."""
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

    def test_list_all_available_tools_basic_functionality(self):
        """Test list_all_available_tools function directly (non-ADK)."""
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

    def test_adk_agent_tool_discovery_workflow(self, adk_agent_with_mixed_tools):
        """Test ADK agent can work with dynamically discovered tools."""
        instruction = 'Use available text processing tools to process this text: "  HELLO-world_test  " - clean it and convert case formatting'

        try:
            response = adk_agent_with_mixed_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of tool discovery and usage
            expected_elements = ["hello", "world", "test", "process", "clean", "case"]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of tool discovery workflow
            assert found_elements >= 3, (
                f"Expected tool discovery elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed tool discovery workflow: {e}")

    def test_adk_agent_error_handling(self, adk_agent_with_mixed_tools):
        """Test ADK agent error handling with helper-loaded tools."""
        instruction = (
            "Try to use a tool that might not be available (testing error handling)"
        )

        try:
            response = adk_agent_with_mixed_tools.run(instruction)

            # The agent should handle the request gracefully
            assert response is not None

            response_str = str(response).lower()

            # Either the agent processed the request or provided some response
            assert len(response_str) > 0

        except Exception as e:
            # Some exceptions are acceptable as they indicate proper error handling
            acceptable_errors = ["tool", "available", "error", "not found"]
            error_msg = str(e).lower()

            is_acceptable = any(
                acceptable in error_msg for acceptable in acceptable_errors
            )

            if not is_acceptable:
                pytest.fail(f"Unexpected error type: {e}")

    def test_helper_workflow_integration(self):
        """Test complete helper workflow integration."""
        # Step 1: Load tools using helpers
        fs_tools = load_all_filesystem_tools()
        text_tools = load_all_text_tools()

        # Step 2: Create custom tools
        def custom_formatter(text: str) -> str:
            return f"[FORMATTED] {text} [/FORMATTED]"

        # Step 3: Merge all tools
        all_tools = merge_tool_lists(fs_tools, text_tools, custom_formatter)

        # Step 4: Verify integration
        assert len(all_tools) == len(fs_tools) + len(text_tools) + 1
        assert custom_formatter in all_tools

        # Step 5: Get tool information
        info = get_tool_info(custom_formatter)
        assert info["name"] == "custom_formatter"

        # Step 6: List all available tools
        available_tools = list_all_available_tools()
        assert isinstance(available_tools, dict)
        assert len(available_tools) >= 2


class TestHelperFunctionsCompatibility:
    """Test Google AI compatibility for helper functions."""

    def test_function_signatures_compatibility(self):
        """Test that all helper functions have Google AI compatible signatures."""
        functions_to_test = [
            load_all_filesystem_tools,
            load_all_text_tools,
            merge_tool_lists,
            get_tool_info,
            list_all_available_tools,
        ]

        for func in functions_to_test:
            sig = inspect.signature(func)

            # Check that return type is specified
            assert sig.return_annotation != inspect.Signature.empty, (
                f"Function {func.__name__} missing return type annotation"
            )

    def test_parameter_types_compatibility(self):
        """Test that parameter types are Google AI compatible."""
        # Test get_tool_info
        sig = inspect.signature(get_tool_info)

        # Should accept callable
        assert sig.return_annotation is dict

        # Test merge_tool_lists - accepts *args
        sig = inspect.signature(merge_tool_lists)
        assert sig.return_annotation.__origin__ is list

        # Test list_all_available_tools - no parameters
        sig = inspect.signature(list_all_available_tools)
        assert len(sig.parameters) == 0
        assert sig.return_annotation is dict

    def test_return_type_compatibility(self):
        """Test that return types are Google AI compatible."""
        # Test tool loaders return List[Callable]
        fs_tools = load_all_filesystem_tools()
        text_tools = load_all_text_tools()

        assert isinstance(fs_tools, list)
        assert isinstance(text_tools, list)

        for tool in fs_tools + text_tools:
            assert callable(tool)

        # Test merge_tool_lists returns List[Callable]
        merged = merge_tool_lists(fs_tools, text_tools)
        assert isinstance(merged, list)

        # Test get_tool_info returns dict
        if fs_tools:
            info = get_tool_info(fs_tools[0])
            assert isinstance(info, dict)

        # Test list_all_available_tools returns dict
        all_tools = list_all_available_tools()
        assert isinstance(all_tools, dict)


class TestHelperFunctionsIntegrationWithADK:
    """Integration tests combining helper functions with ADK agents."""

    @pytest.fixture
    def adk_agent_with_data_tools(self):
        """Create ADK agent with data processing tools loaded via helpers."""
        # Load data tools (since we have them available)
        try:
            from basic_open_agent_tools.data import json_tools, validation

            data_tools = []
            # Add validation tools
            data_tools.extend(
                [
                    validation.check_required_fields,
                    validation.validate_data_types_simple,
                    validation.create_validation_report,
                ]
            )

            # Add JSON tools
            data_tools.extend(
                [
                    json_tools.safe_json_serialize,
                    json_tools.safe_json_deserialize,
                    json_tools.validate_json_string,
                ]
            )

            # Merge with text tools for comprehensive processing
            text_tools = load_all_text_tools()
            all_tools = merge_tool_lists(data_tools, text_tools)

            agent = Agent(
                model="gemini-2.0-flash",
                name="DataProcessingAgent",
                instruction="You are a data processing agent with comprehensive tools for data validation, JSON processing, and text manipulation.",
                description="An agent with tools loaded via helper functions for data and text processing.",
                tools=all_tools,
            )
            return agent
        except ImportError:
            # Fallback to just text tools if data tools not available
            text_tools = load_all_text_tools()
            agent = Agent(
                model="gemini-2.0-flash",
                name="TextProcessingAgent",
                instruction="You are a text processing agent with tools loaded via helper functions.",
                description="An agent with text processing tools loaded via helpers.",
                tools=text_tools,
            )
            return agent

    def test_adk_agent_can_list_data_and_text_tools(self, adk_agent_with_data_tools):
        """Test that ADK agent can list data and text tools loaded via helper functions."""
        instruction = "List all your available tools"

        try:
            response = adk_agent_with_data_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Spot check for specific tools from data processing and text categories
            # Based on our fixture that loads data tools and all text tools
            expected_tools = ["safe_json_serialize", "clean_whitespace"]
            found_tools = sum(1 for tool in expected_tools if tool in response_str)

            # We expect to find at least these 2 specific tool names
            assert found_tools >= 2, (
                f"Expected tool names {expected_tools} not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed to list data and text tools: {e}")

    def test_adk_agent_helper_tool_management_workflow(self, adk_agent_with_data_tools):
        """Test ADK agent using tools loaded and managed via helper functions."""
        instruction = """Process this data using available tools: {"user_name": "  ALICE-JOHNSON  ", "age": 28}. Clean the username, convert to snake_case, validate the data structure, and create a JSON representation."""

        try:
            response = adk_agent_with_data_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of comprehensive tool usage
            expected_elements = [
                "alice",
                "johnson",
                "28",
                "clean",
                "snake",
                "json",
                "validate",
            ]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of tool management workflow
            assert found_elements >= 3, (
                f"Expected tool management workflow elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed helper tool management workflow: {e}")

    def test_adk_agent_dynamic_tool_composition(self, adk_agent_with_data_tools):
        """Test ADK agent with dynamically composed tool sets."""
        instruction = """Using your available tools, process this text data: "  Hello World Data Processing  " by: 1) Cleaning whitespace, 2) Converting to appropriate case format, 3) Creating a structured data representation"""

        try:
            response = adk_agent_with_data_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of dynamic tool composition
            expected_elements = [
                "hello world",
                "data processing",
                "clean",
                "case",
                "structured",
            ]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of dynamic tool composition
            assert found_elements >= 3, (
                f"Expected dynamic tool composition elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed dynamic tool composition: {e}")
