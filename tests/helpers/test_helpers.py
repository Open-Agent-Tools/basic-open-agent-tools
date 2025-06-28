"""Tests for basic_open_agent_tools.helpers module."""

import pytest

from basic_open_agent_tools.helpers import (
    get_tool_info,
    list_all_available_tools,
    load_all_data_tools,
    load_all_filesystem_tools,
    load_all_text_tools,
    load_data_config_tools,
    load_data_csv_tools,
    load_data_json_tools,
    load_data_validation_tools,
    merge_tool_lists,
)


class TestLoadAllFilesystemTools:
    """Test cases for load_all_filesystem_tools function."""

    def test_load_filesystem_tools_returns_list(self) -> None:
        """Test that function returns a list."""
        tools = load_all_filesystem_tools()
        assert isinstance(tools, list)

    def test_load_filesystem_tools_not_empty(self) -> None:
        """Test that returned list is not empty."""
        tools = load_all_filesystem_tools()
        assert len(tools) > 0

    def test_load_filesystem_tools_all_callable(self) -> None:
        """Test that all returned items are callable."""
        tools = load_all_filesystem_tools()
        for tool in tools:
            assert callable(tool)

    def test_load_filesystem_tools_expected_count(self) -> None:
        """Test that expected number of tools are loaded."""
        tools = load_all_filesystem_tools()
        # Expected: 18 file system functions (module complete)
        assert len(tools) >= 15  # Allow some flexibility

    def test_load_filesystem_tools_function_names(self) -> None:
        """Test that expected function names are present."""
        tools = load_all_filesystem_tools()
        tool_names = [tool.__name__ for tool in tools]

        # Check for some known file system functions
        expected_functions = [
            "read_file_to_string",
            "write_file_from_string",
            "copy_file",
            "delete_file",
            "list_directory_contents",
        ]

        for func_name in expected_functions:
            assert func_name in tool_names, f"Missing expected function: {func_name}"


class TestLoadAllTextTools:
    """Test cases for load_all_text_tools function."""

    def test_load_text_tools_returns_list(self) -> None:
        """Test that function returns a list."""
        tools = load_all_text_tools()
        assert isinstance(tools, list)

    def test_load_text_tools_not_empty(self) -> None:
        """Test that returned list is not empty."""
        tools = load_all_text_tools()
        assert len(tools) > 0

    def test_load_text_tools_all_callable(self) -> None:
        """Test that all returned items are callable."""
        tools = load_all_text_tools()
        for tool in tools:
            assert callable(tool)

    def test_load_text_tools_expected_count(self) -> None:
        """Test that expected number of tools are loaded."""
        tools = load_all_text_tools()
        # Expected: 10 text processing functions
        assert len(tools) == 10

    def test_load_text_tools_function_names(self) -> None:
        """Test that expected function names are present."""
        tools = load_all_text_tools()
        tool_names = [tool.__name__ for tool in tools]

        # Check for all known text processing functions
        expected_functions = [
            "clean_whitespace",
            "normalize_line_endings",
            "strip_html_tags",
            "normalize_unicode",
            "to_snake_case",
            "to_camel_case",
            "to_title_case",
            "smart_split_lines",
            "extract_sentences",
            "join_with_oxford_comma",
        ]

        for func_name in expected_functions:
            assert func_name in tool_names, f"Missing expected function: {func_name}"


class TestLoadAllDataTools:
    """Test cases for load_all_data_tools function."""

    def test_load_data_tools_returns_list(self) -> None:
        """Test that function returns a list."""
        tools = load_all_data_tools()
        assert isinstance(tools, list)

    def test_load_data_tools_not_empty(self) -> None:
        """Test that returned list is not empty."""
        tools = load_all_data_tools()
        assert len(tools) > 0

    def test_load_data_tools_all_callable(self) -> None:
        """Test that all returned items are callable."""
        tools = load_all_data_tools()
        for tool in tools:
            assert callable(tool)

    def test_load_data_tools_expected_count(self) -> None:
        """Test that expected number of tools are loaded."""
        tools = load_all_data_tools()
        # Expected: 23 data processing functions
        assert len(tools) == 23

    def test_load_data_tools_function_names(self) -> None:
        """Test that expected function names are present."""
        tools = load_all_data_tools()
        tool_names = [tool.__name__ for tool in tools]

        # Check for some known data processing functions
        expected_functions = [
            "safe_json_serialize",
            "safe_json_deserialize",
            "validate_json_string",
            "read_csv_simple",
            "write_csv_simple",
            "validate_schema_simple",
            "read_yaml_file",
            "write_yaml_file",
        ]

        for func_name in expected_functions:
            assert func_name in tool_names, f"Missing expected function: {func_name}"


class TestLoadDataJsonTools:
    """Test cases for load_data_json_tools function."""

    def test_load_json_tools_returns_list(self) -> None:
        """Test that function returns a list."""
        tools = load_data_json_tools()
        assert isinstance(tools, list)

    def test_load_json_tools_expected_count(self) -> None:
        """Test that expected number of tools are loaded."""
        tools = load_data_json_tools()
        assert len(tools) == 3

    def test_load_json_tools_all_callable(self) -> None:
        """Test that all returned items are callable."""
        tools = load_data_json_tools()
        for tool in tools:
            assert callable(tool)

    def test_load_json_tools_function_names(self) -> None:
        """Test that expected function names are present."""
        tools = load_data_json_tools()
        tool_names = [tool.__name__ for tool in tools]

        expected_functions = [
            "safe_json_serialize",
            "safe_json_deserialize",
            "validate_json_string",
        ]

        assert set(tool_names) == set(expected_functions)


class TestLoadDataCsvTools:
    """Test cases for load_data_csv_tools function."""

    def test_load_csv_tools_returns_list(self) -> None:
        """Test that function returns a list."""
        tools = load_data_csv_tools()
        assert isinstance(tools, list)

    def test_load_csv_tools_expected_count(self) -> None:
        """Test that expected number of tools are loaded."""
        tools = load_data_csv_tools()
        assert len(tools) == 7

    def test_load_csv_tools_all_callable(self) -> None:
        """Test that all returned items are callable."""
        tools = load_data_csv_tools()
        for tool in tools:
            assert callable(tool)

    def test_load_csv_tools_function_names(self) -> None:
        """Test that expected function names are present."""
        tools = load_data_csv_tools()
        tool_names = [tool.__name__ for tool in tools]

        expected_functions = [
            "read_csv_simple",
            "write_csv_simple",
            "csv_to_dict_list",
            "dict_list_to_csv",
            "detect_csv_delimiter",
            "validate_csv_structure",
            "clean_csv_data",
        ]

        assert set(tool_names) == set(expected_functions)


class TestLoadDataValidationTools:
    """Test cases for load_data_validation_tools function."""

    def test_load_validation_tools_returns_list(self) -> None:
        """Test that function returns a list."""
        tools = load_data_validation_tools()
        assert isinstance(tools, list)

    def test_load_validation_tools_expected_count(self) -> None:
        """Test that expected number of tools are loaded."""
        tools = load_data_validation_tools()
        assert len(tools) == 5

    def test_load_validation_tools_all_callable(self) -> None:
        """Test that all returned items are callable."""
        tools = load_data_validation_tools()
        for tool in tools:
            assert callable(tool)

    def test_load_validation_tools_function_names(self) -> None:
        """Test that expected function names are present."""
        tools = load_data_validation_tools()
        tool_names = [tool.__name__ for tool in tools]

        expected_functions = [
            "validate_schema_simple",
            "check_required_fields",
            "validate_data_types_simple",
            "validate_range_simple",
            "create_validation_report",
        ]

        assert set(tool_names) == set(expected_functions)


class TestLoadDataConfigTools:
    """Test cases for load_data_config_tools function."""

    def test_load_config_tools_returns_list(self) -> None:
        """Test that function returns a list."""
        tools = load_data_config_tools()
        assert isinstance(tools, list)

    def test_load_config_tools_expected_count(self) -> None:
        """Test that expected number of tools are loaded."""
        tools = load_data_config_tools()
        assert len(tools) == 8

    def test_load_config_tools_all_callable(self) -> None:
        """Test that all returned items are callable."""
        tools = load_data_config_tools()
        for tool in tools:
            assert callable(tool)

    def test_load_config_tools_function_names(self) -> None:
        """Test that expected function names are present."""
        tools = load_data_config_tools()
        tool_names = [tool.__name__ for tool in tools]

        expected_functions = [
            "read_yaml_file",
            "write_yaml_file",
            "read_toml_file",
            "write_toml_file",
            "read_ini_file",
            "write_ini_file",
            "validate_config_schema",
            "merge_config_files",
        ]

        assert set(tool_names) == set(expected_functions)


class TestMergeToolLists:
    """Test cases for merge_tool_lists function."""

    def test_merge_empty_lists(self) -> None:
        """Test merging empty lists."""
        result = merge_tool_lists([], [])
        assert result == []

    def test_merge_single_list(self) -> None:
        """Test merging a single list."""
        tools = load_data_json_tools()
        result = merge_tool_lists(tools)
        assert len(result) == len(tools)
        assert all(tool in result for tool in tools)

    def test_merge_multiple_lists(self) -> None:
        """Test merging multiple tool lists."""
        json_tools = load_data_json_tools()
        csv_tools = load_data_csv_tools()

        result = merge_tool_lists(json_tools, csv_tools)

        # Should contain all tools from both lists
        assert len(result) == len(json_tools) + len(csv_tools)
        assert all(tool in result for tool in json_tools)
        assert all(tool in result for tool in csv_tools)

    def test_merge_with_duplicates(self) -> None:
        """Test merging lists with duplicate functions."""
        json_tools = load_data_json_tools()

        # Merge the same list twice - should deduplicate
        result = merge_tool_lists(json_tools, json_tools)

        assert len(result) == len(json_tools)  # No duplicates
        assert all(tool in result for tool in json_tools)

    def test_merge_with_individual_functions(self) -> None:
        """Test merging lists with individual functions."""

        def custom_tool(x: str) -> str:
            return x

        json_tools = load_data_json_tools()
        result = merge_tool_lists(json_tools, custom_tool)

        assert len(result) == len(json_tools) + 1
        assert custom_tool in result
        assert all(tool in result for tool in json_tools)

    def test_merge_only_individual_functions(self) -> None:
        """Test merging only individual functions."""

        def tool1(x: str) -> str:
            return x

        def tool2(x: int) -> int:
            return x

        result = merge_tool_lists(tool1, tool2)
        assert len(result) == 2
        assert tool1 in result
        assert tool2 in result

    def test_merge_invalid_list_contents(self) -> None:
        """Test error handling for invalid list contents."""
        with pytest.raises(TypeError, match="All items in tool lists must be callable"):
            merge_tool_lists([lambda x: x, "not_callable", lambda y: y])

    def test_merge_invalid_argument_type(self) -> None:
        """Test error handling for invalid argument types."""
        with pytest.raises(
            TypeError, match="Arguments must be callable or list of callables"
        ):
            merge_tool_lists("not_a_list_or_function")  # type: ignore[arg-type]

    def test_merge_mixed_arguments(self) -> None:
        """Test merging with mixed argument types."""

        def custom_tool(x: str) -> str:
            return x

        json_tools = load_data_json_tools()
        csv_tools = load_data_csv_tools()

        result = merge_tool_lists(json_tools, custom_tool, csv_tools)

        expected_count = len(json_tools) + 1 + len(csv_tools)
        assert len(result) == expected_count
        assert custom_tool in result


class TestGetToolInfo:
    """Test cases for get_tool_info function."""

    def test_get_tool_info_basic(self) -> None:
        """Test getting basic tool information."""
        from basic_open_agent_tools.text import clean_whitespace

        info = get_tool_info(clean_whitespace)

        assert isinstance(info, dict)
        assert info["name"] == "clean_whitespace"
        assert "docstring" in info
        assert "signature" in info
        assert "module" in info
        assert "parameters" in info

    def test_get_tool_info_parameters(self) -> None:
        """Test that tool info includes correct parameters."""
        from basic_open_agent_tools.text import normalize_line_endings

        info = get_tool_info(normalize_line_endings)

        assert "text" in info["parameters"]
        assert "style" in info["parameters"]
        assert len(info["parameters"]) == 2

    def test_get_tool_info_docstring(self) -> None:
        """Test that tool info includes docstring."""
        from basic_open_agent_tools.text import clean_whitespace

        info = get_tool_info(clean_whitespace)

        assert len(info["docstring"]) > 0
        assert "whitespace" in info["docstring"].lower()

    def test_get_tool_info_signature(self) -> None:
        """Test that tool info includes function signature."""
        from basic_open_agent_tools.text import to_camel_case

        info = get_tool_info(to_camel_case)

        assert "text" in info["signature"]
        assert "upper_first" in info["signature"]

    def test_get_tool_info_module(self) -> None:
        """Test that tool info includes module information."""
        from basic_open_agent_tools.text import clean_whitespace

        info = get_tool_info(clean_whitespace)

        assert "text.processing" in info["module"]

    def test_get_tool_info_invalid_input(self) -> None:
        """Test error handling for invalid input."""
        with pytest.raises(TypeError, match="Tool must be callable"):
            get_tool_info("not_callable")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="Tool must be callable"):
            get_tool_info(123)  # type: ignore[arg-type]

    def test_get_tool_info_lambda_function(self) -> None:
        """Test getting info for lambda functions."""
        lambda_func = lambda x: x  # noqa: E731

        info = get_tool_info(lambda_func)

        assert info["name"] == "<lambda>"
        assert "parameters" in info
        assert "x" in info["parameters"]

    def test_get_tool_info_custom_function(self) -> None:
        """Test getting info for custom functions."""

        def custom_function(arg1: str, arg2: int) -> bool:
            """Custom function docstring."""
            return True

        info = get_tool_info(custom_function)

        assert info["name"] == "custom_function"
        assert info["docstring"] == "Custom function docstring."
        assert "arg1" in info["parameters"]
        assert "arg2" in info["parameters"]
        assert len(info["parameters"]) == 2


class TestListAllAvailableTools:
    """Test cases for list_all_available_tools function."""

    def test_list_tools_returns_dict(self) -> None:
        """Test that function returns a dictionary."""
        tools = list_all_available_tools()
        assert isinstance(tools, dict)

    def test_list_tools_has_expected_categories(self) -> None:
        """Test that expected tool categories are present."""
        tools = list_all_available_tools()

        expected_categories = ["file_system", "text", "data"]
        for category in expected_categories:
            assert category in tools

    def test_list_tools_category_structure(self) -> None:
        """Test that each category contains list of tool info dicts."""
        tools = list_all_available_tools()

        for _category, tool_list in tools.items():
            assert isinstance(tool_list, list)
            for tool_info in tool_list:
                assert isinstance(tool_info, dict)
                assert "name" in tool_info
                assert "docstring" in tool_info
                assert "signature" in tool_info
                assert "module" in tool_info
                assert "parameters" in tool_info

    def test_list_tools_file_system_count(self) -> None:
        """Test file system tools count."""
        tools = list_all_available_tools()

        fs_tools = tools["file_system"]
        assert len(fs_tools) >= 15  # Allow some flexibility

    def test_list_tools_text_count(self) -> None:
        """Test text tools count."""
        tools = list_all_available_tools()

        text_tools = tools["text"]
        assert len(text_tools) == 10

    def test_list_tools_data_count(self) -> None:
        """Test data tools count."""
        tools = list_all_available_tools()

        data_tools = tools["data"]
        assert len(data_tools) == 23

    def test_list_tools_function_names(self) -> None:
        """Test that expected function names are present in categories."""
        tools = list_all_available_tools()

        # Check text category
        text_names = [tool["name"] for tool in tools["text"]]
        assert "clean_whitespace" in text_names
        assert "to_snake_case" in text_names

        # Check data category
        data_names = [tool["name"] for tool in tools["data"]]
        assert "safe_json_serialize" in data_names
        assert "read_csv_simple" in data_names
        assert "validate_schema_simple" in data_names

    def test_list_tools_info_completeness(self) -> None:
        """Test that tool info is complete and useful."""
        tools = list_all_available_tools()

        # Check a specific tool
        text_tools = tools["text"]
        clean_whitespace_info = next(
            tool for tool in text_tools if tool["name"] == "clean_whitespace"
        )

        assert len(clean_whitespace_info["docstring"]) > 0
        assert "text" in clean_whitespace_info["parameters"]
        assert "whitespace" in clean_whitespace_info["docstring"].lower()


class TestHelpersIntegration:
    """Integration tests for helpers module functions working together."""

    def test_load_and_merge_all_tools(self) -> None:
        """Test loading and merging all tool categories."""
        fs_tools = load_all_filesystem_tools()
        text_tools = load_all_text_tools()
        data_tools = load_all_data_tools()

        all_tools = merge_tool_lists(fs_tools, text_tools, data_tools)

        expected_count = len(fs_tools) + len(text_tools) + len(data_tools)
        assert len(all_tools) == expected_count

        # All tools should be callable
        assert all(callable(tool) for tool in all_tools)

    def test_load_specific_data_tools_and_merge(self) -> None:
        """Test loading specific data tool categories and merging."""
        json_tools = load_data_json_tools()
        csv_tools = load_data_csv_tools()
        validation_tools = load_data_validation_tools()
        config_tools = load_data_config_tools()

        specific_data_tools = merge_tool_lists(
            json_tools, csv_tools, validation_tools, config_tools
        )

        # Should equal the count from load_all_data_tools
        all_data_tools = load_all_data_tools()
        assert len(specific_data_tools) == len(all_data_tools)

    def test_list_and_get_tool_info_consistency(self) -> None:
        """Test consistency between list_all_available_tools and get_tool_info."""
        all_tools_info = list_all_available_tools()

        # Get actual tools for comparison
        text_tools = load_all_text_tools()

        # Check that listed info matches actual tool info
        for tool in text_tools:
            tool_info = get_tool_info(tool)

            # Find matching tool in list
            listed_tool = next(
                t for t in all_tools_info["text"] if t["name"] == tool.__name__
            )

            assert listed_tool["name"] == tool_info["name"]
            assert listed_tool["docstring"] == tool_info["docstring"]
            assert listed_tool["signature"] == tool_info["signature"]
            assert listed_tool["module"] == tool_info["module"]
            assert listed_tool["parameters"] == tool_info["parameters"]

    def test_comprehensive_tool_loading_workflow(self) -> None:
        """Test a comprehensive tool loading workflow."""
        # Step 1: Load all tools by category
        all_categories = {
            "file_system": load_all_filesystem_tools(),
            "text": load_all_text_tools(),
            "data": load_all_data_tools(),
        }

        # Step 2: Merge all tools
        all_tools = merge_tool_lists(*all_categories.values())

        # Step 3: Get info for all tools
        all_tools_info = [get_tool_info(tool) for tool in all_tools]

        # Step 4: Verify against list_all_available_tools
        listed_tools = list_all_available_tools()

        # Total count should match
        total_listed = sum(len(tools) for tools in listed_tools.values())
        assert len(all_tools_info) == total_listed

        # All tools should have complete info
        for tool_info in all_tools_info:
            assert len(tool_info["name"]) > 0
            assert "parameters" in tool_info
            assert "signature" in tool_info
