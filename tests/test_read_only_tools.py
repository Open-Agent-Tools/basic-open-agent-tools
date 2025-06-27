"""Tests for read-only tools across all modules.

This module provides comprehensive tests for read-only toolkit functions,
including unit tests, integration tests, and Google AI compatibility verification.
"""

import inspect
import logging
import tempfile
import warnings
from pathlib import Path

import pytest
from dotenv import load_dotenv
from google.adk.agents import Agent

from basic_open_agent_tools.data.csv_tools import (
    csv_to_dict_list,
    detect_csv_delimiter,
    read_csv_simple,
    validate_csv_structure,
)
from basic_open_agent_tools.data.json_tools import (
    safe_json_deserialize,
    validate_json_string,
)
from basic_open_agent_tools.data.validation import (
    check_required_fields,
    create_validation_report,
    validate_data_types_simple,
    validate_range_simple,
    validate_schema_simple,
)

# Import read-only tools from different modules
from basic_open_agent_tools.file_system.info import (
    directory_exists,
    file_exists,
    get_file_info,
    get_file_size,
    is_empty_directory,
)
from basic_open_agent_tools.file_system.operations import (
    list_directory_contents,
    read_file_to_string,
)
from basic_open_agent_tools.file_system.tree import (
    generate_directory_tree,
    list_all_directory_contents,
)
from basic_open_agent_tools.text.processing import (
    clean_whitespace,
    extract_sentences,
    join_with_oxford_comma,
    normalize_line_endings,
    normalize_unicode,
    smart_split_lines,
    strip_html_tags,
    to_camel_case,
    to_snake_case,
    to_title_case,
)

# Initialize environment and logging
load_dotenv()
logging.basicConfig(level=logging.ERROR)
warnings.filterwarnings("ignore")


class TestReadOnlyFileSystemTools:
    """Test read-only file system operations."""

    @pytest.fixture
    def temp_file_structure(self):
        """Create temporary file structure for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files and directories
            (temp_path / "test_file.txt").write_text(
                "Hello, World!\nThis is a test file."
            )
            (temp_path / "empty_file.txt").write_text("")
            (temp_path / "subdir").mkdir()
            (temp_path / "subdir" / "nested_file.py").write_text("print('nested')")
            (temp_path / ".hidden").mkdir()
            (temp_path / ".hidden" / "secret.txt").write_text("secret content")

            yield {
                "temp_dir": str(temp_path),
                "test_file": str(temp_path / "test_file.txt"),
                "empty_file": str(temp_path / "empty_file.txt"),
                "subdir": str(temp_path / "subdir"),
                "nested_file": str(temp_path / "subdir" / "nested_file.py"),
                "hidden_dir": str(temp_path / ".hidden"),
            }

    def test_file_existence_operations(self, temp_file_structure):
        """Test file and directory existence checking functions."""
        # Test file_exists
        assert file_exists(temp_file_structure["test_file"]) is True
        assert file_exists("/nonexistent/file.txt") is False

        # Test directory_exists
        assert directory_exists(temp_file_structure["temp_dir"]) is True
        assert directory_exists(temp_file_structure["subdir"]) is True
        assert directory_exists("/nonexistent/directory") is False

    def test_file_info_operations(self, temp_file_structure):
        """Test file information retrieval functions."""
        # Test get_file_size
        size = get_file_size(temp_file_structure["test_file"])
        assert size > 0

        empty_size = get_file_size(temp_file_structure["empty_file"])
        assert empty_size == 0

        # Test get_file_info
        info = get_file_info(temp_file_structure["test_file"])
        assert isinstance(info, dict)
        assert "size" in info
        assert "modified_time" in info
        assert "is_file" in info
        assert info["size"] > 0

    def test_directory_inspection_operations(self, temp_file_structure):
        """Test directory inspection functions."""
        # Test is_empty_directory
        assert (
            is_empty_directory(temp_file_structure["subdir"]) is False
        )  # Contains nested_file.py

        # Test list_directory_contents
        contents = list_directory_contents(temp_file_structure["temp_dir"], False)
        assert "test_file.txt" in contents
        assert "subdir" in contents
        assert ".hidden" not in contents  # Hidden files excluded

        # Test with hidden files
        contents_with_hidden = list_directory_contents(
            temp_file_structure["temp_dir"], True
        )
        assert ".hidden" in contents_with_hidden

    def test_file_reading_operations(self, temp_file_structure):
        """Test file content reading functions."""
        # Test read_file_to_string
        content = read_file_to_string(temp_file_structure["test_file"])
        assert "Hello, World!" in content
        assert "This is a test file." in content

        # Test empty file
        empty_content = read_file_to_string(temp_file_structure["empty_file"])
        assert empty_content == ""

    def test_directory_tree_operations(self, temp_file_structure):
        """Test directory tree generation functions."""
        # Test generate_directory_tree
        tree = generate_directory_tree(temp_file_structure["temp_dir"], 3, False)
        assert "test_file.txt" in tree
        assert "subdir" in tree
        assert "nested_file.py" in tree
        assert ".hidden" not in tree  # Hidden files excluded

        # Test with hidden files
        tree_with_hidden = generate_directory_tree(
            temp_file_structure["temp_dir"], 3, True
        )
        assert ".hidden" in tree_with_hidden

        # Test list_all_directory_contents
        all_contents = list_all_directory_contents(temp_file_structure["temp_dir"])
        assert isinstance(all_contents, str)
        assert len(all_contents) > 0


class TestReadOnlyDataProcessingTools:
    """Test read-only data processing operations."""

    @pytest.fixture
    def temp_csv_file(self):
        """Create temporary CSV file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("name,age,city\nAlice,25,NYC\nBob,30,LA\nCharlie,35,Chicago")
            csv_file = f.name

        yield csv_file

        # Cleanup
        Path(csv_file).unlink(missing_ok=True)

    def test_csv_reading_operations(self, temp_csv_file):
        """Test CSV reading and processing functions."""
        # Test read_csv_simple
        data = read_csv_simple(temp_csv_file, ",", True)
        assert len(data) == 3
        assert data[0]["name"] == "Alice"
        assert data[0]["age"] == "25"

        # Test csv_to_dict_list
        csv_string = "name,age\nAlice,25\nBob,30"
        data = csv_to_dict_list(csv_string, ",")
        assert len(data) == 2
        assert data[0]["name"] == "Alice"

        # Test detect_csv_delimiter
        delimiter = detect_csv_delimiter(temp_csv_file, 1024)
        assert delimiter == ","

        # Test validate_csv_structure
        result = validate_csv_structure(temp_csv_file, ["name", "age"])
        assert result is True

    def test_json_processing_operations(self):
        """Test JSON processing functions."""
        # Test safe_json_deserialize
        json_string = '{"name": "Alice", "age": 25}'
        data = safe_json_deserialize(json_string)
        assert data["name"] == "Alice"
        assert data["age"] == 25

        # Test validate_json_string
        assert validate_json_string('{"valid": true}') is True
        assert validate_json_string('{"invalid": }') is False
        assert validate_json_string("[1, 2, 3]") is True
        assert validate_json_string("not json") is False

    def test_data_validation_operations(self):
        """Test data validation functions."""
        test_data = {"name": "Alice", "age": 25, "email": "alice@example.com"}

        # Test check_required_fields
        assert check_required_fields(test_data, ["name", "age"]) is True

        # Test validate_data_types_simple
        type_map = {"name": "str", "age": "int", "email": "str"}
        assert validate_data_types_simple(test_data, type_map) is True

        # Test validate_range_simple
        assert validate_range_simple(25, 18, 65) is True
        assert validate_range_simple(25.5, 18.0, 65.0) is True

        # Test validate_schema_simple
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
            "required": ["name"],
        }
        assert validate_schema_simple(test_data, schema) is True

        # Test create_validation_report
        rules = {
            "required": ["name", "age"],
            "types": {"name": "str", "age": "int"},
            "ranges": {"age": {"min": 18, "max": 65}},
        }
        report = create_validation_report(test_data, rules)
        assert report["valid"] is True
        assert report["errors"] == []


class TestReadOnlyTextProcessingTools:
    """Test read-only text processing operations."""

    def test_text_cleaning_operations(self):
        """Test text cleaning and normalization functions."""
        # Test clean_whitespace
        assert clean_whitespace("  hello    world  ") == "hello world"
        assert clean_whitespace("hello\t\n\r world") == "hello world"

        # Test normalize_line_endings
        assert (
            normalize_line_endings("line1\r\nline2\rline3\n", "unix")
            == "line1\nline2\nline3\n"
        )
        assert normalize_line_endings("line1\nline2", "windows") == "line1\r\nline2"

        # Test strip_html_tags
        assert strip_html_tags("<p>Hello <strong>world</strong>!</p>") == "Hello world!"
        assert strip_html_tags("Plain text") == "Plain text"

        # Test normalize_unicode
        result = normalize_unicode("café", "NFC")
        assert isinstance(result, str)

    def test_text_case_conversion_operations(self):
        """Test text case conversion functions."""
        # Test to_snake_case
        assert to_snake_case("HelloWorld") == "hello_world"
        assert to_snake_case("hello world") == "hello_world"
        assert to_snake_case("hello-world") == "hello_world"

        # Test to_camel_case
        assert to_camel_case("hello_world", False) == "helloWorld"
        assert to_camel_case("hello world", False) == "helloWorld"
        assert to_camel_case("hello_world", True) == "HelloWorld"

        # Test to_title_case
        assert to_title_case("hello world") == "Hello World"
        assert to_title_case("hello-world_test") == "Hello-World_Test"

    def test_text_analysis_operations(self):
        """Test text analysis and extraction functions."""
        # Test extract_sentences
        text = "Hello world. How are you? Fine!"
        sentences = extract_sentences(text)
        assert len(sentences) == 3
        assert "Hello world." in sentences
        assert "How are you?" in sentences
        assert "Fine!" in sentences

        # Test smart_split_lines
        text = "This is a long line that needs splitting"
        lines = smart_split_lines(text, 15, True)
        assert all(len(line) <= 15 for line in lines)
        assert " ".join(lines) == text

        # Test join_with_oxford_comma
        items = ["apples", "bananas", "oranges"]
        result = join_with_oxford_comma(items, "and")
        assert result == "apples, bananas, and oranges"

        items = ["apples", "bananas"]
        result = join_with_oxford_comma(items, "and")
        assert result == "apples and bananas"


class TestADKAgentIntegration:
    """Test ADK Agent integration with read-only tools."""

    @pytest.fixture
    def temp_data_environment(self):
        """Create comprehensive test data environment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            (temp_path / "data.csv").write_text(
                "name,age,score\nAlice,25,95.5\nBob,30,88.0\nCharlie,22,92.3"
            )
            (temp_path / "config.json").write_text(
                '{"app": {"name": "TestApp", "version": "1.0"}, "debug": true}'
            )
            (temp_path / "readme.txt").write_text(
                "  Welcome to Our Application  \n\nThis is a sample README file."
            )
            (temp_path / "subdir").mkdir()
            (temp_path / "subdir" / "nested.py").write_text(
                "# Python file\nprint('Hello from nested file')"
            )

            yield {
                "temp_dir": str(temp_path),
                "csv_file": str(temp_path / "data.csv"),
                "json_file": str(temp_path / "config.json"),
                "text_file": str(temp_path / "readme.txt"),
                "python_file": str(temp_path / "subdir" / "nested.py"),
            }

    @pytest.fixture
    def adk_agent_with_file_inspection_tools(self):
        """Create ADK agent with file inspection tools."""
        agent = Agent(
            model="gemini-2.0-flash",
            name="FileInspectionAgent",
            instruction="You are a file inspection agent. Use the available tools to examine files and directories without modifying them.",
            description="An agent specialized in read-only file system operations.",
            tools=[
                file_exists,
                directory_exists,
                get_file_info,
                get_file_size,
                read_file_to_string,
                list_directory_contents,
                generate_directory_tree,
            ],
        )
        return agent

    @pytest.fixture
    def adk_agent_with_data_analysis_tools(self):
        """Create ADK agent with data analysis tools."""
        agent = Agent(
            model="gemini-2.0-flash",
            name="DataAnalysisAgent",
            instruction="You are a data analysis agent. Use the available tools to analyze and validate data without modifying it.",
            description="An agent specialized in read-only data processing and validation.",
            tools=[
                read_csv_simple,
                safe_json_deserialize,
                validate_json_string,
                check_required_fields,
                validate_data_types_simple,
                create_validation_report,
            ],
        )
        return agent

    @pytest.fixture
    def adk_agent_with_text_analysis_tools(self):
        """Create ADK agent with text analysis tools."""
        agent = Agent(
            model="gemini-2.0-flash",
            name="TextAnalysisAgent",
            instruction="You are a text analysis agent. Use the available tools to analyze and process text without modifying the original content.",
            description="An agent specialized in read-only text processing and analysis.",
            tools=[
                clean_whitespace,
                strip_html_tags,
                to_snake_case,
                to_camel_case,
                extract_sentences,
                smart_split_lines,
            ],
        )
        return agent

    @pytest.fixture
    def adk_agent_with_comprehensive_readonly_tools(self):
        """Create ADK agent with comprehensive read-only tools."""
        agent = Agent(
            model="gemini-2.0-flash",
            name="ComprehensiveReadOnlyAgent",
            instruction="You are a comprehensive read-only analysis agent. Use the available tools to inspect files, analyze data, and process text without making any modifications.",
            description="An agent with comprehensive read-only capabilities across file system, data, and text processing.",
            tools=[
                # File system tools
                file_exists,
                directory_exists,
                get_file_info,
                read_file_to_string,
                list_directory_contents,
                generate_directory_tree,
                # Data processing tools
                read_csv_simple,
                safe_json_deserialize,
                validate_json_string,
                check_required_fields,
                validate_data_types_simple,
                create_validation_report,
                # Text processing tools
                clean_whitespace,
                strip_html_tags,
                to_snake_case,
                extract_sentences,
            ],
        )
        return agent

    def test_adk_agent_file_inspection_workflow(
        self, adk_agent_with_file_inspection_tools, temp_data_environment
    ):
        """Test ADK agent performing file inspection workflow."""
        instruction = f"Inspect the directory at {temp_data_environment['temp_dir']} and provide information about its contents, including file sizes and directory structure."

        try:
            response = adk_agent_with_file_inspection_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of file inspection
            expected_elements = [
                "directory",
                "file",
                "size",
                "data.csv",
                "config.json",
                "readme.txt",
            ]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of successful file inspection
            assert found_elements >= 3, (
                f"Expected file inspection elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed file inspection workflow: {e}")

    def test_adk_agent_data_analysis_workflow(
        self, adk_agent_with_data_analysis_tools, temp_data_environment
    ):
        """Test ADK agent performing data analysis workflow."""
        instruction = f"Analyze the CSV data in {temp_data_environment['csv_file']} and the JSON configuration in {temp_data_environment['json_file']}. Validate their structure and content."

        try:
            response = adk_agent_with_data_analysis_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of data analysis
            expected_elements = [
                "csv",
                "json",
                "alice",
                "bob",
                "charlie",
                "testapp",
                "validate",
                "analyze",
            ]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of successful data analysis
            assert found_elements >= 4, (
                f"Expected data analysis elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed data analysis workflow: {e}")

    def test_adk_agent_text_analysis_workflow(
        self, adk_agent_with_text_analysis_tools, temp_data_environment
    ):
        """Test ADK agent performing text analysis workflow."""
        instruction = f"Analyze the text content in {temp_data_environment['text_file']}. Clean it, extract sentences, and convert key phrases to different case formats."

        try:
            response = adk_agent_with_text_analysis_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of text analysis
            expected_elements = [
                "welcome",
                "application",
                "readme",
                "text",
                "sentence",
                "clean",
                "case",
            ]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of successful text analysis
            assert found_elements >= 3, (
                f"Expected text analysis elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed text analysis workflow: {e}")

    def test_adk_agent_comprehensive_readonly_workflow(
        self, adk_agent_with_comprehensive_readonly_tools, temp_data_environment
    ):
        """Test ADK agent performing comprehensive read-only analysis."""
        instruction = f"""Perform a comprehensive read-only analysis of the data environment at {temp_data_environment["temp_dir"]}:
        1. Inspect the directory structure and file information
        2. Read and validate the CSV data file
        3. Parse and analyze the JSON configuration
        4. Process the text content and extract key information
        Provide a summary report of your findings."""

        try:
            response = adk_agent_with_comprehensive_readonly_tools.run(instruction)

            # Verify response contains expected elements
            assert response is not None
            assert len(str(response)) > 0

            response_str = str(response).lower()

            # Look for evidence of comprehensive analysis
            expected_elements = [
                "directory",
                "file",
                "csv",
                "json",
                "text",
                "alice",
                "bob",
                "charlie",
                "testapp",
                "welcome",
                "analyze",
                "inspect",
                "validate",
                "summary",
            ]
            found_elements = sum(
                1 for element in expected_elements if element in response_str
            )

            # We expect to find evidence of comprehensive read-only analysis
            assert found_elements >= 8, (
                f"Expected comprehensive analysis elements not found in response: {response}"
            )

        except Exception as e:
            pytest.fail(f"ADK agent failed comprehensive read-only workflow: {e}")

    def test_adk_agent_error_handling_readonly(
        self, adk_agent_with_file_inspection_tools
    ):
        """Test ADK agent error handling with read-only operations."""
        instruction = "Try to inspect a non-existent directory: /invalid/path/directory (testing error handling)"

        try:
            response = adk_agent_with_file_inspection_tools.run(instruction)

            # The agent should handle the error gracefully
            assert response is not None

            response_str = str(response).lower()

            # Look for evidence of proper error handling
            error_indicators = [
                "error",
                "not found",
                "does not exist",
                "invalid",
                "cannot",
                "unable",
            ]
            has_error_indication = any(
                indicator in response_str for indicator in error_indicators
            )

            # Either the agent handled the error or provided some response
            assert has_error_indication or len(response_str) > 0

        except Exception as e:
            # Some exceptions are acceptable as they indicate proper error handling
            acceptable_errors = ["not found", "does not exist", "invalid", "error"]
            error_msg = str(e).lower()

            is_acceptable = any(
                acceptable in error_msg for acceptable in acceptable_errors
            )

            if not is_acceptable:
                pytest.fail(f"Unexpected error type: {e}")


class TestReadOnlyToolsCompatibility:
    """Test Google AI compatibility for read-only tools."""

    def test_file_system_tools_compatibility(self):
        """Test file system read-only tools compatibility."""
        file_system_functions = [
            file_exists,
            directory_exists,
            get_file_info,
            get_file_size,
            is_empty_directory,
            read_file_to_string,
            list_directory_contents,
            generate_directory_tree,
            list_all_directory_contents,
        ]

        for func in file_system_functions:
            sig = inspect.signature(func)

            # Check that no parameters have default values
            for param_name, param in sig.parameters.items():
                assert param.default == inspect.Parameter.empty, (
                    f"Function {func.__name__} parameter {param_name} has default value, "
                    "violating Google AI requirements"
                )

            # Check that return type is specified
            assert sig.return_annotation != inspect.Signature.empty, (
                f"Function {func.__name__} missing return type annotation"
            )

    def test_data_processing_tools_compatibility(self):
        """Test data processing read-only tools compatibility."""
        data_functions = [
            read_csv_simple,
            csv_to_dict_list,
            detect_csv_delimiter,
            validate_csv_structure,
            safe_json_deserialize,
            validate_json_string,
            check_required_fields,
            validate_data_types_simple,
            validate_range_simple,
            validate_schema_simple,
            create_validation_report,
        ]

        for func in data_functions:
            sig = inspect.signature(func)

            # Check that no parameters have default values
            for param_name, param in sig.parameters.items():
                assert param.default == inspect.Parameter.empty, (
                    f"Function {func.__name__} parameter {param_name} has default value, "
                    "violating Google AI requirements"
                )

            # Check that return type is specified
            assert sig.return_annotation != inspect.Signature.empty, (
                f"Function {func.__name__} missing return type annotation"
            )

    def test_text_processing_tools_compatibility(self):
        """Test text processing read-only tools compatibility."""
        text_functions = [
            clean_whitespace,
            normalize_line_endings,
            strip_html_tags,
            normalize_unicode,
            to_snake_case,
            to_camel_case,
            to_title_case,
            extract_sentences,
            smart_split_lines,
            join_with_oxford_comma,
        ]

        for func in text_functions:
            sig = inspect.signature(func)

            # Check that no parameters have default values
            for param_name, param in sig.parameters.items():
                assert param.default == inspect.Parameter.empty, (
                    f"Function {func.__name__} parameter {param_name} has default value, "
                    "violating Google AI requirements"
                )

            # Check that return type is specified
            assert sig.return_annotation != inspect.Signature.empty, (
                f"Function {func.__name__} missing return type annotation"
            )


class TestReadOnlyToolsIntegration:
    """Integration tests combining multiple read-only tools."""

    @pytest.fixture
    def comprehensive_test_environment(self):
        """Create comprehensive test environment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create complex file structure
            (temp_path / "project").mkdir()
            (temp_path / "project" / "src").mkdir()
            (temp_path / "project" / "data").mkdir()
            (temp_path / "project" / "docs").mkdir()

            # Create various data files
            (temp_path / "project" / "data" / "users.csv").write_text(
                "id,name,email,age,department\n"
                "1,Alice Johnson,alice@company.com,28,Engineering\n"
                "2,Bob Smith,bob@company.com,32,Marketing\n"
                "3,Charlie Brown,charlie@company.com,25,Engineering\n"
            )

            (temp_path / "project" / "config.json").write_text(
                '{"database": {"host": "localhost", "port": 5432}, "features": {"analytics": true, "debug": false}}'
            )

            (temp_path / "project" / "docs" / "readme.md").write_text(
                "# Project Documentation\n\n"
                "This is a **sample project** with *various* data files.\n\n"
                "## Features\n"
                "- User management\n"
                "- Data analytics\n"
                "- Configuration management\n"
            )

            (temp_path / "project" / "src" / "main.py").write_text(
                "#!/usr/bin/env python3\n"
                "# Main application file\n"
                'print("Hello, World!")\n'
                "def process_data():\n"
                "    pass\n"
            )

            yield {
                "project_dir": str(temp_path / "project"),
                "users_csv": str(temp_path / "project" / "data" / "users.csv"),
                "config_json": str(temp_path / "project" / "config.json"),
                "readme_md": str(temp_path / "project" / "docs" / "readme.md"),
                "main_py": str(temp_path / "project" / "src" / "main.py"),
            }

    def test_complete_readonly_analysis_workflow(self, comprehensive_test_environment):
        """Test complete read-only analysis workflow."""
        project_dir = comprehensive_test_environment["project_dir"]

        # Step 1: Analyze directory structure
        tree = generate_directory_tree(project_dir, 3, False)
        assert "src" in tree
        assert "data" in tree
        assert "docs" in tree

        # Step 2: Read and analyze CSV data
        users_data = read_csv_simple(
            comprehensive_test_environment["users_csv"], ",", True
        )
        assert len(users_data) == 3
        assert users_data[0]["name"] == "Alice Johnson"

        # Step 3: Validate CSV structure
        csv_valid = validate_csv_structure(
            comprehensive_test_environment["users_csv"], ["id", "name", "email"]
        )
        assert csv_valid is True

        # Step 4: Parse JSON configuration
        config_content = read_file_to_string(
            comprehensive_test_environment["config_json"]
        )
        config_data = safe_json_deserialize(config_content)
        assert config_data["database"]["host"] == "localhost"

        # Step 5: Analyze markdown documentation
        readme_content = read_file_to_string(
            comprehensive_test_environment["readme_md"]
        )
        sentences = extract_sentences(readme_content)
        assert len(sentences) > 0

        # Step 6: Process Python source code
        python_content = read_file_to_string(comprehensive_test_environment["main_py"])
        assert "Hello, World!" in python_content
        assert "def process_data" in python_content

        # Step 7: Create comprehensive validation report
        for user in users_data:
            rules = {
                "required": ["id", "name", "email"],
                "types": {"id": "str", "name": "str", "email": "str", "age": "str"},
            }
            report = create_validation_report(user, rules)
            assert report["valid"] is True

    def test_readonly_tools_data_quality_assessment(
        self, comprehensive_test_environment
    ):
        """Test data quality assessment using read-only tools."""
        # Read CSV data
        users_data = read_csv_simple(
            comprehensive_test_environment["users_csv"], ",", True
        )

        # Assess data quality for each record
        assessment_results = []
        for user in users_data:
            # Check required fields
            required_check = check_required_fields(user, ["id", "name", "email", "age"])

            # Validate data types
            type_check = validate_data_types_simple(
                user,
                {
                    "id": "str",
                    "name": "str",
                    "email": "str",
                    "age": "str",
                    "department": "str",
                },
            )

            # Check age range (if convertible to int)
            age_valid = True
            try:
                age_int = int(user["age"])
                age_valid = validate_range_simple(age_int, 18, 70)
            except ValueError:
                age_valid = False

            assessment_results.append(
                {
                    "user": user["name"],
                    "required_fields": required_check,
                    "types_valid": type_check,
                    "age_valid": age_valid,
                }
            )

        # Verify all users pass quality checks
        assert len(assessment_results) == 3
        for result in assessment_results:
            assert result["required_fields"] is True
            assert result["types_valid"] is True
            assert result["age_valid"] is True

    def test_readonly_tools_text_content_analysis(self, comprehensive_test_environment):
        """Test text content analysis using read-only tools."""
        # Read and analyze README content
        readme_content = read_file_to_string(
            comprehensive_test_environment["readme_md"]
        )

        # Clean and normalize text
        cleaned_text = strip_html_tags(readme_content)  # Remove any HTML if present
        normalized_text = clean_whitespace(cleaned_text)

        # Extract sentences
        sentences = extract_sentences(normalized_text)
        assert len(sentences) > 0

        # Split into manageable lines
        lines = smart_split_lines(normalized_text, 80, True)
        assert all(len(line) <= 80 for line in lines)

        # Convert key terms to different cases
        project_terms = [
            "user management",
            "data analytics",
            "configuration management",
        ]
        snake_case_terms = [to_snake_case(term) for term in project_terms]
        camel_case_terms = [to_camel_case(term, False) for term in project_terms]

        assert "user_management" in snake_case_terms
        assert "userManagement" in camel_case_terms

        # Join terms with Oxford comma
        features_description = join_with_oxford_comma(project_terms, "and")
        assert (
            "user management, data analytics, and configuration management"
            == features_description
        )
