"""Debugging and development workflow utilities for AI agents."""

import inspect
import sys
import traceback
from typing import Any, Union

from ..decorators import strands_tool
from ..exceptions import BasicAgentToolsError


@strands_tool
def inspect_function_signature(
    function_name: str, module_name: str
) -> dict[str, Union[str, int, list, dict, Any]]:
    """
    Inspect a function's signature, parameters, and documentation.

    Args:
        function_name: Name of the function to inspect
        module_name: Optional module name (if None, searches current globals)

    Returns:
        Dictionary with function inspection details

    Raises:
        BasicAgentToolsError: If function cannot be found or inspected
    """
    if not isinstance(function_name, str) or not function_name.strip():
        raise BasicAgentToolsError("Function name must be a non-empty string")

    function_name = function_name.strip()

    try:
        # Try to get the function
        if module_name:
            if not isinstance(module_name, str) or not module_name.strip():
                raise BasicAgentToolsError("Module name must be a non-empty string")

            module_name = module_name.strip()

            # Import the module
            if module_name in sys.modules:
                module = sys.modules[module_name]
            else:
                module = __import__(module_name)

            if not hasattr(module, function_name):
                raise BasicAgentToolsError(
                    f"Function '{function_name}' not found in module '{module_name}'"
                )

            func = getattr(module, function_name)
        else:
            # Search in current frame's globals/locals and builtins
            # Start from the caller's frame and walk up the stack to find the function
            current_frame = inspect.currentframe()
            func = None

            # Walk up the frame stack to find the function
            frame = current_frame.f_back if current_frame else None
            while frame is not None:
                # Check locals first, then globals
                if function_name in frame.f_locals:
                    func = frame.f_locals[function_name]
                    break
                elif function_name in frame.f_globals:
                    func = frame.f_globals[function_name]
                    break
                frame = frame.f_back

            # If not found in any frame, check builtins
            if func is None:
                import builtins

                if hasattr(builtins, function_name):
                    func = getattr(builtins, function_name)
                else:
                    raise BasicAgentToolsError(
                        f"Function '{function_name}' not found in current scope"
                    )

        if not callable(func):
            raise BasicAgentToolsError(f"'{function_name}' is not a callable function")

        # Get function signature
        sig = inspect.signature(func)

        # Extract parameter information
        parameters = []
        for param_name, param in sig.parameters.items():
            param_info = {
                "name": param_name,
                "kind": param.kind.name,
                "has_default": param.default != param.empty,
                "default_value": str(param.default)
                if param.default != param.empty
                else None,
                "annotation": str(param.annotation)
                if param.annotation != param.empty
                else None,
            }
            parameters.append(param_info)

        # Get return annotation
        return_annotation = (
            str(sig.return_annotation) if sig.return_annotation != sig.empty else None
        )

        # Get docstring
        docstring = inspect.getdoc(func) or ""

        # Get source info if possible
        source_info = {}
        try:
            source_file = inspect.getfile(func)
            source_lines = inspect.getsourcelines(func)
            source_info = {
                "file": source_file,
                "line_number": source_lines[1],
                "source_available": True,
            }
        except (OSError, TypeError):
            source_info = {"file": None, "line_number": None, "source_available": False}

        return {
            "function_name": function_name,
            "module_name": module_name or "current_scope",
            "signature": str(sig),
            "parameters": parameters,
            "parameter_count": len(parameters),
            "return_annotation": return_annotation,
            "docstring": docstring,
            "docstring_length": len(docstring),
            "source_info": source_info,
            "inspection_status": "success",
        }

    except Exception as e:
        raise BasicAgentToolsError(
            f"Failed to inspect function '{function_name}': {str(e)}"
        )


@strands_tool
def get_call_stack_info() -> dict[str, Union[list, int, str, Any]]:
    """
    Get detailed information about the current call stack.

    Returns:
        Dictionary with call stack information

    Raises:
        BasicAgentToolsError: If call stack cannot be retrieved
    """
    try:
        # Get the current frame and stack
        current_frame = inspect.currentframe()
        stack_frames = inspect.getouterframes(current_frame)

        stack_info = []
        for i, frame_info in enumerate(stack_frames):
            frame_dict = {
                "level": i,
                "filename": frame_info.filename,
                "function_name": frame_info.function,
                "line_number": frame_info.lineno,
                "code_context": frame_info.code_context[0].strip()
                if frame_info.code_context
                else "",
                "is_current_function": i == 0,
            }
            stack_info.append(frame_dict)

        return {
            "stack_depth": len(stack_info),
            "current_function": stack_info[0]["function_name"]
            if stack_info
            else "unknown",
            "current_file": stack_info[0]["filename"] if stack_info else "unknown",
            "current_line": stack_info[0]["line_number"] if stack_info else 0,
            "call_stack": stack_info,
            "stack_retrieval_status": "success",
        }

    except Exception as e:
        raise BasicAgentToolsError(f"Failed to get call stack info: {str(e)}")


@strands_tool
def format_exception_details(
    exception_info: str,
) -> dict[str, Union[str, list, bool, Any]]:
    """
    Format detailed exception information from the last exception or provided info.

    Args:
        exception_info: Exception info string (use empty string to get last exception)

    Returns:
        Dictionary with formatted exception details

    Raises:
        BasicAgentToolsError: If no exception information available
    """
    try:
        if not isinstance(exception_info, str):
            raise BasicAgentToolsError("Exception info must be a string")

        if not exception_info or exception_info.strip() == "":
            # Get the last exception
            exc_type, exc_value, exc_traceback = sys.exc_info()

            if exc_type is None:
                raise BasicAgentToolsError("No exception information available")

        else:
            # Parse provided exception info
            return {
                "exception_source": "provided_string",
                "exception_info": exception_info,
                "formatted_details": exception_info,
                "parsing_status": "string_provided_as_is",
            }

        # Format the exception
        exception_details = {
            "exception_type": exc_type.__name__,
            "exception_message": str(exc_value),
            "has_traceback": exc_traceback is not None,
        }

        # Format traceback if available
        if exc_traceback:
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            exception_details.update(
                {
                    "traceback_lines": tb_lines,
                    "traceback_formatted": "".join(tb_lines),
                    "traceback_summary": traceback.format_exception_only(
                        exc_type, exc_value
                    ),
                }
            )

            # Extract frame information
            frames = []
            tb = exc_traceback
            while tb is not None:
                frame = tb.tb_frame
                frames.append(
                    {
                        "filename": frame.f_code.co_filename,
                        "function_name": frame.f_code.co_name,
                        "line_number": tb.tb_lineno,
                        "local_variables_count": len(frame.f_locals),
                    }
                )
                tb = tb.tb_next  # type: ignore[assignment]

            exception_details["frames"] = frames  # type: ignore[unreachable]  # False positive - this is reachable
            exception_details["frame_count"] = len(frames)
        else:
            exception_details.update(
                {
                    "traceback_lines": [],
                    "traceback_formatted": "",
                    "traceback_summary": [],
                    "frames": [],
                    "frame_count": 0,
                }
            )

        exception_details["formatting_status"] = "success"
        return exception_details

    except Exception as e:
        raise BasicAgentToolsError(f"Failed to format exception details: {str(e)}")


@strands_tool
def validate_function_call(
    function_name: str, arguments: dict[str, str], module_name: str
) -> dict[str, Union[str, bool, list, Any]]:
    """
    Validate if a function call would succeed with given arguments.

    Args:
        function_name: Name of function to validate
        arguments: Dictionary of argument names and values
        module_name: Optional module name

    Returns:
        Dictionary with validation results

    Raises:
        BasicAgentToolsError: If validation cannot be performed
    """
    if not isinstance(function_name, str) or not function_name.strip():
        raise BasicAgentToolsError("Function name must be a non-empty string")

    if not isinstance(arguments, dict):
        raise BasicAgentToolsError("Arguments must be a dictionary")

    function_name = function_name.strip()

    try:
        # Get the function (similar logic to inspect_function_signature)
        if module_name:
            if not isinstance(module_name, str) or not module_name.strip():
                raise BasicAgentToolsError("Module name must be a non-empty string")

            module_name = module_name.strip()

            if module_name in sys.modules:
                module = sys.modules[module_name]
            else:
                module = __import__(module_name)

            if not hasattr(module, function_name):
                raise BasicAgentToolsError(
                    f"Function '{function_name}' not found in module '{module_name}'"
                )

            func = getattr(module, function_name)
        else:
            # Walk up the frame stack to find the function
            current_frame = inspect.currentframe()
            func = None

            frame = current_frame.f_back if current_frame else None
            while frame is not None:
                if function_name in frame.f_locals:
                    func = frame.f_locals[function_name]
                    break
                elif function_name in frame.f_globals:
                    func = frame.f_globals[function_name]
                    break
                frame = frame.f_back

            # If not found in any frame, check builtins
            if func is None:
                import builtins

                if hasattr(builtins, function_name):
                    func = getattr(builtins, function_name)
                else:
                    raise BasicAgentToolsError(
                        f"Function '{function_name}' not found in current scope"
                    )

        if not callable(func):
            raise BasicAgentToolsError(f"'{function_name}' is not callable")

        # Get function signature
        sig = inspect.signature(func)

        # Validate arguments against signature
        validation_results = {
            "function_name": function_name,
            "module_name": module_name or "current_scope",
            "provided_arguments": list(arguments.keys()),
            "validation_issues": [],
            "is_valid": True,
            "can_call": False,
        }

        try:
            # Try to bind arguments to signature
            bound_args = sig.bind(**arguments)
            bound_args.apply_defaults()

            validation_results["can_call"] = True
            validation_results["bound_arguments"] = dict(bound_args.arguments)
            validation_results["binding_status"] = "success"

        except TypeError as e:
            validation_results["is_valid"] = False
            validation_results["can_call"] = False
            validation_results["binding_error"] = str(e)
            issues = validation_results["validation_issues"]
            if not isinstance(issues, list):
                raise TypeError(
                    f"validation_issues should be list, got {type(issues).__name__}"
                )
            issues.append(f"Binding failed: {str(e)}")

        # Additional parameter analysis
        required_params = []
        optional_params = []

        for param_name, param in sig.parameters.items():
            if param.default == param.empty and param.kind not in (
                param.VAR_POSITIONAL,
                param.VAR_KEYWORD,
            ):
                required_params.append(param_name)
            else:
                optional_params.append(param_name)

        validation_results.update(
            {
                "required_parameters": required_params,
                "optional_parameters": optional_params,
                "missing_required": [p for p in required_params if p not in arguments],
                "extra_arguments": [k for k in arguments if k not in sig.parameters],
                "validation_status": "completed",
            }
        )

        return validation_results

    except Exception as e:
        raise BasicAgentToolsError(f"Failed to validate function call: {str(e)}")


@strands_tool
def trace_variable_changes(
    variable_name: str, initial_value: str, operations: list[str]
) -> dict[str, Union[str, Any, list]]:
    """
    Trace how a variable changes through a series of operations.

    Args:
        variable_name: Name of the variable to trace
        initial_value: Starting value of the variable
        operations: List of Python operations to apply

    Returns:
        Dictionary with variable tracing results

    Raises:
        BasicAgentToolsError: If tracing fails
    """
    if not isinstance(variable_name, str) or not variable_name.strip():
        raise BasicAgentToolsError("Variable name must be a non-empty string")

    if not isinstance(operations, list):
        raise BasicAgentToolsError("Operations must be a list of strings")

    variable_name = variable_name.strip()

    # Basic validation of variable name
    if not variable_name.isidentifier():
        raise BasicAgentToolsError(
            f"'{variable_name}' is not a valid Python identifier"
        )

    try:
        # Create execution context
        context = {variable_name: initial_value, "__builtins__": {}}

        trace_steps = [
            {
                "step": 0,
                "operation": "initialization",
                "value": initial_value,
                "value_type": type(initial_value).__name__,
                "status": "success",
            }
        ]

        # Execute each operation and trace changes
        for i, operation in enumerate(operations):
            if not isinstance(operation, str):
                trace_steps.append(  # type: ignore[unreachable]  # False positive - this is reachable
                    {
                        "step": i + 1,
                        "operation": str(operation),
                        "value": context.get(variable_name),
                        "value_type": type(context.get(variable_name)).__name__
                        if variable_name in context
                        else "unknown",
                        "status": "error",
                        "error": "Operation must be a string",
                    }
                )
                continue

            operation = operation.strip()
            if not operation:
                continue

            # Security check - prevent dangerous operations (check before try block)
            dangerous_keywords = ["import", "exec", "eval", "__", "open", "file"]
            if any(keyword in operation.lower() for keyword in dangerous_keywords):
                raise BasicAgentToolsError(
                    "Operation contains potentially dangerous keyword"
                )

            try:
                # Execute the operation
                exec(operation, {"__builtins__": {}}, context)

                trace_steps.append(
                    {
                        "step": i + 1,
                        "operation": operation,
                        "value": context.get(variable_name),
                        "value_type": type(context.get(variable_name)).__name__
                        if variable_name in context
                        else "unknown",
                        "status": "success",
                    }
                )

            except Exception as e:
                trace_steps.append(
                    {
                        "step": i + 1,
                        "operation": operation,
                        "value": context.get(variable_name),
                        "value_type": type(context.get(variable_name)).__name__
                        if variable_name in context
                        else "unknown",
                        "status": "error",
                        "error": str(e),
                    }
                )

        return {
            "variable_name": variable_name,
            "initial_value": initial_value,
            "final_value": context.get(variable_name),
            "operations_count": len(operations),
            "trace_steps": trace_steps,
            "successful_operations": len(
                [s for s in trace_steps if s["status"] == "success"]
            )
            - 1,  # Exclude initialization
            "failed_operations": len(
                [s for s in trace_steps if s["status"] == "error"]
            ),
            "tracing_status": "completed",
        }

    except Exception as e:
        raise BasicAgentToolsError(f"Failed to trace variable changes: {str(e)}")
