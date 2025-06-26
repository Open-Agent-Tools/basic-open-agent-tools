"""Tests for the load_all_read_only_tools helper function."""

import basic_open_agent_tools as boat


class TestReadOnlyTools:
    """Test the read-only tools helper function."""

    def test_load_all_read_only_tools_returns_list(self):
        """Test that load_all_read_only_tools returns a list."""
        tools = boat.load_all_read_only_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_load_all_read_only_tools_count(self):
        """Test that we get the expected number of read-only tools."""
        tools = boat.load_all_read_only_tools()
        # Should have 55 read-only tools total:
        # 11 file system + 10 text + 34 data = 55
        assert len(tools) == 55

    def test_all_returned_items_are_callable(self):
        """Test that all returned items are callable functions."""
        tools = boat.load_all_read_only_tools()
        for tool in tools:
            assert callable(tool), f"Tool {tool} is not callable"

    def test_read_only_tools_have_expected_categories(self):
        """Test that read-only tools include expected categories."""
        tools = boat.load_all_read_only_tools()

        # Count tools by module
        fs_tools = [t for t in tools if "file_system" in t.__module__]
        text_tools = [t for t in tools if "text" in t.__module__]
        data_tools = [t for t in tools if "data" in t.__module__]

        # Verify counts
        assert len(fs_tools) == 11  # File system read-only tools
        assert len(text_tools) == 10  # All text tools are read-only
        assert len(data_tools) == 34  # Data read-only tools

    def test_read_only_tools_exclude_write_operations(self):
        """Test that read-only tools exclude write/modify operations."""
        tools = boat.load_all_read_only_tools()
        tool_names = [tool.__name__ for tool in tools]

        # Should NOT include write operations
        write_operations = [
            "write_file_from_string",
            "append_to_file",
            "create_directory",
            "delete_file",
            "delete_directory",
            "move_file",
            "copy_file",
            "write_csv_file",
            "write_yaml_file",
            "write_toml_file",
            "write_ini_file",
            "write_binary_file",
            "create_zip_archive",
            "create_tar_archive",
            "serialize_object",
            "compress_json_data",
        ]

        for write_op in write_operations:
            assert write_op not in tool_names, (
                f"Write operation {write_op} found in read-only tools"
            )

    def test_read_only_tools_include_expected_functions(self):
        """Test that read-only tools include key expected functions."""
        tools = boat.load_all_read_only_tools()
        tool_names = [tool.__name__ for tool in tools]

        # Should include these key read-only operations
        expected_read_only = [
            "file_exists",
            "directory_exists",
            "read_file_to_string",
            "list_directory_contents",
            "validate_json_string",
            "read_csv_simple",
            "read_yaml_file",
            "validate_schema_simple",
            "clean_whitespace",
            "extract_sentences",
            "flatten_dict_simple",
            "validate_binary_format",
            "list_archive_contents",
        ]

        for expected in expected_read_only:
            assert expected in tool_names, (
                f"Expected read-only tool {expected} not found"
            )

    def test_load_all_read_only_tools_can_be_merged(self):
        """Test that read-only tools can be merged with other tool lists."""
        read_only_tools = boat.load_all_read_only_tools()
        all_fs_tools = boat.load_all_filesystem_tools()

        # Merge should work without errors
        merged = boat.merge_tool_lists(read_only_tools, all_fs_tools)

        assert isinstance(merged, list)
        assert len(merged) > len(
            read_only_tools
        )  # Should be larger due to additional write tools

    def test_read_only_tools_have_docstrings(self):
        """Test that read-only tools have proper docstrings."""
        tools = boat.load_all_read_only_tools()

        for tool in tools[:5]:  # Check first 5 tools
            assert tool.__doc__ is not None, f"Tool {tool.__name__} has no docstring"
            assert len(tool.__doc__.strip()) > 0, (
                f"Tool {tool.__name__} has empty docstring"
            )

    def test_list_all_available_tools_includes_read_only(self):
        """Test that the list_all_available_tools includes read_only category."""
        all_tools = boat.list_all_available_tools()

        assert "read_only" in all_tools
        assert isinstance(all_tools["read_only"], list)
        assert (
            len(all_tools["read_only"]) == 55
        )  # Should match our read-only tool count
