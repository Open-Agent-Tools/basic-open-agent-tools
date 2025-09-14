# Utilities Tools

## Overview
Comprehensive timing controls, debugging utilities, and development tools for AI agents with simplified type signatures.

## Current Status
**✅ FULLY IMPLEMENTED MODULE** - 8 functions available

This module provides essential timing, debugging, and development utilities for AI agents with agent-friendly signatures.

## Current Features
- ✅ **sleep_seconds**: Pause execution with interrupt handling
- ✅ **sleep_milliseconds**: Sleep for millisecond durations
- ✅ **precise_sleep**: High-precision sleep using busy-waiting
- ✅ **inspect_function_signature**: Function signature analysis and inspection
- ✅ **get_call_stack_info**: Call stack debugging information
- ✅ **format_exception_details**: Exception formatting and analysis
- ✅ **validate_function_call**: Pre-validate function calls before execution
- ✅ **trace_variable_changes**: Variable state tracing through operations

## Function Reference

### Timing Utilities

#### sleep_seconds
Pause execution for the specified number of seconds with interrupt handling.

```python
def sleep_seconds(seconds: Union[int, float]) -> Dict[str, Union[str, float]]
```

**Parameters:**
- `seconds`: Number of seconds to sleep (can be fractional, max 3600)

**Returns:**
Dictionary with `status`, `requested_seconds`, `actual_seconds`, and `message`.

**Features:**
- Interruptible with Ctrl+C (SIGINT)
- Returns actual sleep duration
- Maximum duration: 1 hour for safety

**Example:**
```python
result = sleep_seconds(2.5)
print(f"Status: {result['status']}")
print(f"Actual sleep time: {result['actual_seconds']} seconds")
```

#### sleep_milliseconds
Convenience function for sleeping in milliseconds.

```python
def sleep_milliseconds(milliseconds: Union[int, float]) -> Dict[str, Union[str, float]]
```

**Parameters:**
- `milliseconds`: Number of milliseconds to sleep

**Returns:**
Dictionary similar to sleep_seconds but with additional `requested_milliseconds` and `actual_milliseconds` fields.

**Example:**
```python
result = sleep_milliseconds(500)  # Sleep for 0.5 seconds
print(f"Slept for {result['actual_milliseconds']}ms")
```

#### precise_sleep
High-precision sleep using a combination of sleep() and busy-waiting.

```python
def precise_sleep(seconds: Union[int, float]) -> Dict[str, Union[str, float]]
```

**Parameters:**
- `seconds`: Number of seconds to sleep precisely (max 60 seconds)

**Returns:**
Dictionary with `status`, `requested_seconds`, `actual_seconds`, `precision`, and `message`.

**Features:**
- Uses sleep() for bulk duration + busy-waiting for final 10ms
- More precise than regular sleep for timing-critical applications
- Reports precision level in response

**Example:**
```python
result = precise_sleep(0.001)  # 1ms precise sleep
print(f"Precision: {result['precision']}")
print(f"Actual time: {result['actual_seconds']:.6f} seconds")
```

### Debugging Utilities

#### inspect_function_signature
Inspect a function's signature, parameters, and documentation.

```python
def inspect_function_signature(
    function_name: str,
    module_name: str = None
) -> Dict[str, Union[str, List, Dict]]
```

**Parameters:**
- `function_name`: Name of the function to inspect
- `module_name`: Optional module name (searches current scope if None)

**Returns:**
Dictionary with `function_name`, `module_name`, `signature`, `parameters`, `parameter_count`, `return_annotation`, `docstring`, `docstring_length`, `source_info`, and `inspection_status`.

**Example:**
```python
info = inspect_function_signature("print")
print(f"Signature: {info['signature']}")
print(f"Parameters: {len(info['parameters'])}")
print(f"Docstring length: {info['docstring_length']}")
```

#### get_call_stack_info
Get detailed information about the current call stack.

```python
def get_call_stack_info() -> Dict[str, Union[List, int, str]]
```

**Returns:**
Dictionary with `stack_depth`, `current_function`, `current_file`, `current_line`, `call_stack`, and `stack_retrieval_status`.

**Example:**
```python
stack_info = get_call_stack_info()
print(f"Current function: {stack_info['current_function']}")
print(f"Stack depth: {stack_info['stack_depth']}")

for level, frame in enumerate(stack_info['call_stack'][:3]):
    print(f"Level {level}: {frame['function_name']} at line {frame['line_number']}")
```

#### format_exception_details
Format detailed exception information from the last exception or provided info.

```python
def format_exception_details(exception_info: str = None) -> Dict[str, Union[str, List, bool]]
```

**Parameters:**
- `exception_info`: Optional exception info string (uses last exception if None)

**Returns:**
Dictionary with `exception_type`, `exception_message`, `has_traceback`, `traceback_lines`, `traceback_formatted`, `traceback_summary`, `frames`, `frame_count`, and `formatting_status`.

**Example:**
```python
try:
    1 / 0
except:
    details = format_exception_details()
    print(f"Exception: {details['exception_type']}")
    print(f"Message: {details['exception_message']}")
    print(f"Traceback has {details['frame_count']} frames")
```

#### validate_function_call
Validate if a function call would succeed with given arguments.

```python
def validate_function_call(
    function_name: str,
    arguments: Dict[str, Any],
    module_name: str = None
) -> Dict[str, Union[str, bool, List]]
```

**Parameters:**
- `function_name`: Name of function to validate
- `arguments`: Dictionary of argument names and values
- `module_name`: Optional module name

**Returns:**
Dictionary with `function_name`, `module_name`, `provided_arguments`, `validation_issues`, `is_valid`, `can_call`, `required_parameters`, `optional_parameters`, `missing_required`, `extra_arguments`, and `validation_status`.

**Example:**
```python
validation = validate_function_call(
    "print",
    {"value": "Hello", "sep": " ", "end": "\n"}
)

print(f"Can call: {validation['can_call']}")
print(f"Issues: {validation['validation_issues']}")
print(f"Missing required: {validation['missing_required']}")
```

#### trace_variable_changes
Trace how a variable changes through a series of operations.

```python
def trace_variable_changes(
    variable_name: str,
    initial_value: Any,
    operations: List[str]
) -> Dict[str, Union[str, Any, List]]
```

**Parameters:**
- `variable_name`: Name of the variable to trace
- `initial_value`: Starting value of the variable
- `operations`: List of Python operations to apply

**Returns:**
Dictionary with `variable_name`, `initial_value`, `final_value`, `operations_count`, `trace_steps`, `successful_operations`, `failed_operations`, and `tracing_status`.

**Security:** Operations are executed in a restricted namespace to prevent dangerous code execution.

**Example:**
```python
trace = trace_variable_changes(
    "counter",
    0,
    ["counter = counter + 1", "counter = counter * 2", "counter = counter - 1"]
)

print(f"Initial: {trace['initial_value']}")
print(f"Final: {trace['final_value']}")
print(f"Successful operations: {trace['successful_operations']}")

for step in trace['trace_steps']:
    print(f"Step {step['step']}: {step['operation']} -> {step['value']} ({step['status']})")
```

## Agent-Friendly Design Features

### Simplified Type Signatures
All functions use basic Python types (str, int, float, bool, Dict, List) to prevent "signature too complex" errors in agent frameworks.

### Comprehensive Error Handling
- Input validation with clear error messages
- Safe execution environments for code inspection
- Graceful handling of missing modules or functions
- Structured error responses with debugging information

### Security Features
- Code execution in restricted namespaces
- Input sanitization for function names and operations
- Dangerous operation detection and blocking
- Safe error messages without information disclosure

### Development Workflow Integration
- Stack trace analysis for debugging agent behavior
- Function signature inspection for dynamic tool discovery
- Variable state tracking for algorithm debugging
- Exception analysis for error handling improvement

## Common Use Cases

### Agent Development and Debugging
```python
# Debug agent function calls
def debug_agent_call(func_name, args):
    # Validate the call first
    validation = validate_function_call(func_name, args)

    if not validation['can_call']:
        print(f"Invalid call to {func_name}:")
        for issue in validation['validation_issues']:
            print(f"  - {issue}")
        return None

    # Inspect function details
    func_info = inspect_function_signature(func_name)
    print(f"Calling {func_name} with {len(args)} arguments")
    print(f"Function has {func_info['parameter_count']} parameters")

    return "Ready to call"
```

### Algorithm Analysis
```python
# Trace algorithm execution
def trace_sorting_algorithm():
    arr = [64, 34, 25, 12, 22, 11, 90]
    operations = [
        "arr[0], arr[1] = (arr[1], arr[0]) if arr[0] > arr[1] else (arr[0], arr[1])",
        "arr[1], arr[2] = (arr[2], arr[1]) if arr[1] > arr[2] else (arr[1], arr[2])"
    ]

    trace = trace_variable_changes("arr", arr, operations)

    print("Array sorting trace:")
    for step in trace['trace_steps']:
        if step['status'] == 'success':
            print(f"  After: {step['operation']}")
            print(f"  Array: {step['value']}")
```

### Performance Monitoring
```python
# Monitor agent task timing
def monitor_task_performance():
    # Start timing
    start_result = sleep_seconds(0)  # Just get timestamp

    # Simulate work with precise timing
    work_result = precise_sleep(0.1)

    print(f"Task precision: {work_result['precision']}")
    print(f"Actual duration: {work_result['actual_seconds']:.6f}s")
```

### Error Analysis
```python
# Analyze agent errors
def analyze_agent_error():
    try:
        # Simulate agent operation
        result = some_agent_function()
    except Exception as e:
        # Get detailed error information
        error_details = format_exception_details()
        stack_info = get_call_stack_info()

        print(f"Error in {stack_info['current_function']}:")
        print(f"  Type: {error_details['exception_type']}")
        print(f"  Message: {error_details['exception_message']}")
        print(f"  Frames: {error_details['frame_count']}")

        return error_details
```

## Agent Integration

### Google ADK
```python
from google.adk.agents import Agent
import basic_open_agent_tools as boat

utilities_tools = boat.load_all_utilities_tools()
agent = Agent(tools=utilities_tools)
```

### LangChain
```python
from langchain.tools import StructuredTool
from basic_open_agent_tools.utilities import inspect_function_signature

inspector_tool = StructuredTool.from_function(
    func=inspect_function_signature,
    name="function_inspector",
    description="Inspect function signatures and documentation"
)
```

### Strands Agents
All functions include the `@strands_tool` decorator for native compatibility:
```python
from basic_open_agent_tools.utilities import trace_variable_changes
# Function is automatically compatible with Strands Agents
```

## Performance Considerations

### Timing Precision
- `sleep_seconds`: Standard OS sleep precision (~1-15ms accuracy)
- `sleep_milliseconds`: Same precision as sleep_seconds
- `precise_sleep`: High precision using busy-waiting (~0.1ms accuracy)

### Memory Usage
- Function inspection uses minimal memory
- Call stack inspection limited to current stack depth
- Variable tracing uses restricted execution contexts
- Exception formatting processes existing traceback data

### Security Limitations
- Variable tracing blocks dangerous operations (`import`, `exec`, `eval`, etc.)
- Function inspection only works with accessible functions
- No file system access during code execution
- All operations use safe execution environments

## Error Reference

### Common Error Types
- `BasicAgentToolsError`: Input validation and processing errors
- `ValueError`: Invalid function names or variable names
- `TypeError`: Type mismatches in arguments or operations
- `ImportError`: Missing modules during function inspection

### Validation Errors
```python
# Common validation error messages
"Function name must be a non-empty string"
"Variable name must be a non-empty string"
"Arguments must be a dictionary"
"Operations must be a list of strings"
"Seconds cannot be negative"
"Maximum sleep duration is 3600 seconds (1 hour)"
"Operation contains potentially dangerous keyword"
```

### Security Errors
```python
# Security-related error messages
"'variable_name' is not a valid Python identifier"
"Operation contains potentially dangerous keyword: import"
"Function 'function_name' not found in current scope"
"Code execution in restricted environment only"
```

## Testing
Comprehensive test coverage includes:
- Timing accuracy testing with various durations
- Function inspection with built-in and custom functions
- Call stack analysis in different execution contexts
- Exception handling with various error types
- Variable tracing with different operations and data types
- Security testing for dangerous operations
- Agent framework compatibility testing

**Test Coverage**: Individual function tests + integration tests + security tests + timing accuracy tests + agent framework compatibility tests.