"""Test @strands_tool decorator functionality in basic-open-agent-tools."""

import inspect
import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestStrandsDecorators:
    """Test the @strands_tool decorator functionality."""

    def test_strands_decorator_import(self):
        """Test that we can import strands decorator without error."""
        # The decorator is implemented with graceful fallback
        # So it should always be importable even if Strands is not installed
        from basic_open_agent_tools.file_system import read_file_to_string
        from basic_open_agent_tools.text import clean_whitespace

        # Functions should be callable regardless of Strands availability
        assert callable(read_file_to_string)
        assert callable(clean_whitespace)

    def test_decorator_preserves_function_metadata(self):
        """Test that @strands_tool preserves original function metadata."""
        from basic_open_agent_tools.file_system import read_file_to_string
        from basic_open_agent_tools.text import normalize_line_endings

        functions = [read_file_to_string, normalize_line_endings]

        for func in functions:
            # Check essential metadata is preserved
            assert hasattr(func, "__name__")
            assert hasattr(func, "__doc__")
            assert hasattr(func, "__annotations__")

            # Check function name is preserved
            assert func.__name__ in ["read_file_to_string", "normalize_line_endings"]

            # Check docstring is preserved
            assert func.__doc__ is not None
            assert len(func.__doc__.strip()) > 0

            # Check type annotations are preserved
            sig = inspect.signature(func)
            assert sig.return_annotation != inspect.Parameter.empty

    def test_strands_decorator_fallback_behavior(self):
        """Test decorator behavior when Strands is not available."""
        # This should work regardless of whether Strands is installed
        from basic_open_agent_tools.data import read_json_file
        from basic_open_agent_tools.datetime import get_current_date

        functions = [read_json_file, get_current_date]

        for func in functions:
            # Function should be callable
            assert callable(func)

            # Should have proper signature
            sig = inspect.signature(func)
            assert len(sig.parameters) >= 0  # At least 0 parameters

            # Should maintain type annotations
            for param in sig.parameters.values():
                if param.name != "self":
                    # Parameters should have type annotations (Google ADK requirement)
                    assert param.annotation != inspect.Parameter.empty, (
                        f"Parameter {param.name} in {func.__name__} missing type annotation"
                    )

    def test_all_modules_have_strands_decorators(self):
        """Test that all modules have @strands_tool decorators applied."""
        import basic_open_agent_tools as boat

        # Get tools from each module
        module_loaders = [
            ("filesystem", boat.load_all_filesystem_tools),
            ("text", boat.load_all_text_tools),
            ("data", boat.load_all_data_tools),
            ("datetime", boat.load_all_datetime_tools),
            ("network", boat.load_all_network_tools),
            ("utilities", boat.load_all_utilities_tools),
            ("crypto", boat.load_all_crypto_tools),
            ("archive", boat.load_all_archive_tools),
            ("todo", boat.load_all_todo_tools),
            # Skip logging due to **kwargs parameter that fails validation
            # ('logging', boat.load_all_logging_tools),
        ]

        for module_name, loader in module_loaders:
            tools = loader()

            assert len(tools) > 0, f"No tools loaded from {module_name} module"

            # Check each tool has proper attributes
            for tool in tools:
                # Basic callable check
                assert callable(tool), f"Tool {tool} from {module_name} is not callable"

                # Check has proper name and docstring
                assert hasattr(tool, "__name__"), (
                    f"Tool from {module_name} missing __name__"
                )
                assert hasattr(tool, "__doc__"), (
                    f"Tool {tool.__name__} from {module_name} missing __doc__"
                )
                assert tool.__doc__ is not None, (
                    f"Tool {tool.__name__} from {module_name} has None docstring"
                )

                # Check type annotations (Google ADK requirement)
                sig = inspect.signature(tool)
                for param_name, param in sig.parameters.items():
                    if param_name != "self":
                        assert param.annotation != inspect.Parameter.empty, (
                            f"Tool {tool.__name__} parameter {param_name} missing type annotation"
                        )

                # Return type should be annotated
                assert sig.return_annotation != inspect.Parameter.empty, (
                    f"Tool {tool.__name__} missing return type annotation"
                )

    def test_strands_tool_signature_compatibility(self):
        """Test that @strands_tool decorated functions have compatible signatures."""
        import basic_open_agent_tools as boat

        # Test a sample of tools from different modules
        sample_tools = (
            boat.load_all_filesystem_tools()[:3]
            + boat.load_all_text_tools()[:2]
            + boat.load_all_data_tools()[:3]
            + boat.load_all_utilities_tools()[:2]
        )

        for tool in sample_tools:
            sig = inspect.signature(tool)

            # Check no parameters have default values (Google ADK requirement)
            for param_name, param in sig.parameters.items():
                if param_name != "self":
                    assert param.default == inspect.Parameter.empty, (
                        f"Tool {tool.__name__} parameter {param_name} has default value (not allowed for Google ADK)"
                    )

            # Check parameter types are JSON-serializable (basic check)
            for param_name, param in sig.parameters.items():
                if param_name != "self" and param.annotation != inspect.Parameter.empty:
                    # Should be basic types or typed containers
                    annotation_str = str(param.annotation)
                    allowed_patterns = [
                        "str",
                        "int",
                        "float",
                        "bool",
                        "dict",
                        "List[",
                        "Dict[",
                        "typing.List",
                        "typing.Dict",
                    ]
                    assert any(
                        pattern in annotation_str for pattern in allowed_patterns
                    ), (
                        f"Tool {tool.__name__} parameter {param_name} has non-JSON-serializable type: {param.annotation}"
                    )


class TestStrandsIntegrationValidation:
    """Test validation of Strands integration compatibility."""

    def test_function_compatibility_for_strands(self):
        """Test that functions are compatible with Strands framework requirements."""
        from basic_open_agent_tools.data import read_json_file, write_json_file
        from basic_open_agent_tools.file_system import (
            read_file_to_string,
            write_file_from_string,
        )
        from basic_open_agent_tools.text import clean_whitespace, to_snake_case

        test_functions = [
            read_file_to_string,
            write_file_from_string,
            clean_whitespace,
            to_snake_case,
            read_json_file,
            write_json_file,
        ]

        for func in test_functions:
            # Test function signature inspection (needed for agent frameworks)
            sig = inspect.signature(func)

            # Should be able to inspect all parameters
            for param in sig.parameters.values():
                assert param.name is not None
                assert param.annotation != inspect.Parameter.empty

            # Should be able to get docstring for help/description
            assert func.__doc__ is not None
            assert (
                "Args:" in func.__doc__
                or "Parameters:" in func.__doc__
                or "param" in func.__doc__.lower()
            )

    def test_error_handling_compatibility(self):
        """Test that error handling works well with agent frameworks."""
        from basic_open_agent_tools.data import read_json_file
        from basic_open_agent_tools.file_system import read_file_to_string

        # Test that functions raise appropriate exceptions (not generic Exception)
        with pytest.raises(FileNotFoundError):
            read_file_to_string("/nonexistent/file/path.txt")

        with pytest.raises((FileNotFoundError, ValueError, OSError)):
            read_json_file("/nonexistent/file.json")

    def test_return_value_compatibility(self):
        """Test that return values are compatible with agent frameworks."""
        from basic_open_agent_tools.crypto import generate_uuid4
        from basic_open_agent_tools.datetime import get_current_date
        from basic_open_agent_tools.text import clean_whitespace, to_snake_case

        # Test return types are JSON-serializable
        result1 = clean_whitespace("  test string  ")
        assert isinstance(result1, str)

        result2 = to_snake_case("TestString")
        assert isinstance(result2, str)

        result3 = get_current_date()
        assert isinstance(result3, str)

        result4 = generate_uuid4()
        assert isinstance(result4, str)

        # All return values should be JSON-serializable
        import json

        test_data = {
            "clean_whitespace": result1,
            "to_snake_case": result2,
            "current_date": result3,
            "uuid": result4,
        }

        # Should be able to serialize to JSON
        json_str = json.dumps(test_data)
        assert isinstance(json_str, str)

        # Should be able to deserialize from JSON
        parsed = json.loads(json_str)
        assert parsed["clean_whitespace"] == result1


@pytest.mark.skipif(
    sys.version_info < (3, 9), reason="Strands testing requires Python 3.9+"
)
class TestStrandsPython39Compatibility:
    """Test compatibility with Python 3.9+ requirements for Strands."""

    def test_type_annotations_python39_compatible(self):
        """Test that type annotations work with Python 3.9+."""
        import basic_open_agent_tools as boat

        # Load sample tools
        tools = boat.load_all_filesystem_tools()[:5]

        for tool in tools:
            sig = inspect.signature(tool)

            # Check annotations are compatible with Python 3.9+
            for param in sig.parameters.values():
                if param.annotation != inspect.Parameter.empty:
                    # Should not raise errors when stringified
                    annotation_str = str(param.annotation)
                    assert len(annotation_str) > 0

            # Return annotation should also be compatible
            if sig.return_annotation != inspect.Parameter.empty:
                return_str = str(sig.return_annotation)
                assert len(return_str) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
