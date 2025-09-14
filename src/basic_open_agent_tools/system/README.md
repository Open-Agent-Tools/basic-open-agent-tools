# System Tools

## Overview
Comprehensive cross-platform system information, process management, and system utilities for AI agents with simplified type signatures.

## Current Status
**✅ FULLY IMPLEMENTED MODULE** - 19 functions available

This module provides essential system-level operations for AI agents with agent-friendly signatures and cross-platform compatibility.

## Current Features
- ✅ **Shell Operations**: execute_shell_command, run_bash, run_powershell
- ✅ **Process Management**: get_current_process_info, list_running_processes, get_process_info, is_process_running
- ✅ **Environment Variables**: get_env_var, set_env_var, list_env_vars
- ✅ **System Information**: get_system_info, get_cpu_info, get_memory_info, get_disk_usage, get_uptime
- ✅ **Runtime Environment**: inspect_runtime_environment, get_python_module_info, get_file_system_context, get_network_environment

## Function Reference

### Shell Operations

#### execute_shell_command
Execute shell commands with comprehensive error handling and output capture.

```python
def execute_shell_command(
    command: str,
    timeout_seconds: int = 30,
    working_directory: str = None
) -> Dict[str, Union[str, int, bool]]
```

**Parameters:**
- `command`: Shell command to execute
- `timeout_seconds`: Command timeout (1-300 seconds)
- `working_directory`: Working directory for command execution

**Returns:**
Dictionary with `command`, `exit_code`, `stdout`, `stderr`, `execution_time_seconds`, `success`, `timeout_occurred`, and `execution_status`.

**Example:**
```python
result = execute_shell_command("ls -la", timeout_seconds=10)
print(f"Exit code: {result['exit_code']}")
print(f"Output: {result['stdout']}")
```

#### run_bash, run_powershell
Platform-specific shell command execution.

```python
def run_bash(command: str, timeout_seconds: int = 30) -> Dict[str, Union[str, int, bool]]
def run_powershell(command: str, timeout_seconds: int = 30) -> Dict[str, Union[str, int, bool]]
```

### Process Management

#### get_current_process_info
Get comprehensive information about the current process.

```python
def get_current_process_info() -> Dict[str, Union[str, int, float]]
```

**Returns:**
Dictionary with process details including PID, name, status, memory usage, CPU times, and creation time.

**Example:**
```python
info = get_current_process_info()
print(f"PID: {info['pid']}")
print(f"Memory: {info['memory_usage_mb']} MB")
```

#### list_running_processes
List currently running processes with basic information.

```python
def list_running_processes(limit: int = 20) -> List[Dict[str, Union[str, int, float]]]
```

**Parameters:**
- `limit`: Maximum number of processes to return (1-100)

**Returns:**
List of dictionaries with process information including PID, name, CPU usage, and memory usage.

#### get_process_info
Get detailed information about a specific process by PID.

```python
def get_process_info(process_id: int) -> Dict[str, Union[str, int, float, None]]
```

#### is_process_running
Check if a process with a given name is currently running.

```python
def is_process_running(process_name: str) -> Dict[str, Union[str, bool, List[int]]]
```

### Environment Variables

#### get_env_var, set_env_var, list_env_vars
Manage environment variables safely.

```python
def get_env_var(variable_name: str) -> Dict[str, Union[str, bool]]
def set_env_var(variable_name: str, value: str) -> Dict[str, Union[str, bool]]
def list_env_vars() -> Dict[str, Union[Dict[str, str], int]]
```

**Example:**
```python
# Get environment variable
result = get_env_var("PATH")
if result['variable_exists']:
    print(f"PATH: {result['value']}")

# Set environment variable
set_result = set_env_var("MY_VAR", "test_value")
print(f"Set success: {set_result['success']}")
```

### System Information

#### get_system_info
Get comprehensive system information.

```python
def get_system_info() -> Dict[str, Union[str, bool]]
```

**Returns:**
Dictionary with OS information, platform details, architecture, and hostname.

#### get_cpu_info
Get CPU information and current usage statistics.

```python
def get_cpu_info() -> Dict[str, Union[str, int, float, List[float]]]
```

**Returns:**
CPU details including core count, usage percentages, and load averages.

#### get_memory_info
Get system memory usage information.

```python
def get_memory_info() -> Dict[str, Union[int, float]]
```

**Returns:**
Memory statistics including total, available, used memory and percentages.

#### get_disk_usage
Get disk usage information for a specific path.

```python
def get_disk_usage(path: str = ".") -> Dict[str, Union[str, int, float]]
```

#### get_uptime
Get system uptime in seconds.

```python
def get_uptime() -> Dict[str, Union[int, float, str]]
```

### Runtime Environment

#### inspect_runtime_environment
Comprehensive runtime environment inspection.

```python
def inspect_runtime_environment() -> Dict[str, Union[str, int, float, List[str], Dict]]
```

**Returns:**
Detailed information about Python runtime, system context, and environment configuration.

#### get_python_module_info
Get information about Python modules and packages.

```python
def get_python_module_info() -> Dict[str, Union[str, int, bool, List[str]]]
```

#### get_file_system_context
Get file system context and permissions.

```python
def get_file_system_context() -> Dict[str, Union[str, List[str], bool, int]]
```

#### get_network_environment
Get network environment and configuration details.

```python
def get_network_environment() -> Dict[str, Union[str, List[str], bool, int, Dict]]
```

## Agent-Friendly Design Features

### Cross-Platform Compatibility
- Windows, macOS, and Linux support
- Platform-specific command handling
- Consistent behavior across operating systems
- Safe error handling for missing features

### Security Features
- **Read-only operations preferred** for safety
- No system modification operations (avoid potential damage)
- No privileged operations (no admin/root required)
- Input validation and sanitization
- Safe error messages without sensitive information

### Simplified Type Signatures
All functions use basic Python types (str, int, float, bool, Dict, List) to prevent "signature too complex" errors in agent frameworks.

### Comprehensive Error Handling
- System operation error handling
- Permission error handling
- Process not found handling
- Timeout handling for long operations
- Structured error responses

## Common Use Cases

### System Monitoring
```python
# Get comprehensive system status
system_info = get_system_info()
cpu_info = get_cpu_info()
memory_info = get_memory_info()

print(f"OS: {system_info['system']} {system_info['release']}")
print(f"CPU Usage: {cpu_info['cpu_usage_percent']}%")
print(f"Memory Usage: {memory_info['memory_usage_percent']}%")
```

### Process Management
```python
# Check if a service is running
service_check = is_process_running("nginx")
if service_check['is_running']:
    print(f"Service running with PIDs: {service_check['process_ids']}")
else:
    print("Service not running")

# Get detailed process information
processes = list_running_processes(10)
for proc in processes:
    print(f"PID {proc['pid']}: {proc['name']} - CPU: {proc['cpu_percent']}%")
```

### Environment Management
```python
# Check important environment variables
important_vars = ["PATH", "HOME", "USER", "PYTHONPATH"]
for var in important_vars:
    result = get_env_var(var)
    if result['variable_exists']:
        print(f"{var}: {result['value'][:50]}...")  # Truncate long values
    else:
        print(f"{var}: Not set")
```

### Command Execution
```python
# Execute system commands safely
result = execute_shell_command("python --version", timeout_seconds=5)
if result['success']:
    print(f"Python version: {result['stdout'].strip()}")
else:
    print(f"Command failed: {result['stderr']}")
```

### Runtime Analysis
```python
# Analyze runtime environment for debugging
runtime_info = inspect_runtime_environment()
python_info = get_python_module_info()

print(f"Python version: {runtime_info['python_version']}")
print(f"Working directory: {runtime_info['current_working_directory']}")
print(f"Installed packages: {python_info['total_packages']}")
```

## Agent Integration

### Google ADK
```python
import basic_open_agent_tools as boat
system_tools = boat.load_all_system_tools()
agent = Agent(tools=system_tools)
```

### Strands Agents
All functions include the `@strands_tool` decorator for native compatibility:
```python
from basic_open_agent_tools.system import get_system_info
# Function is automatically compatible with Strands Agents
```

## Dependencies

### Required Dependencies
System monitoring requires psutil:
```bash
pip install basic-open-agent-tools[system]
```

### Optional Dependencies
- **psutil**: Advanced system monitoring and process management
- **platform**: Built-in Python module for system information
- **subprocess**: Built-in Python module for command execution

## Security Considerations

### Safe Operations Only
- **Information gathering focus** - Read-only operations preferred
- **No system modification** - No registry changes, service management
- **No privileged operations** - No admin/root requirements
- **Process monitoring only** - No process termination or control
- **Environment variable safety** - Validation and safe setting

### Input Validation
- Command injection prevention
- Path traversal protection
- Process ID validation
- Environment variable name validation
- Timeout bounds checking

### Error Handling
- System operation failures handled gracefully
- Permission errors reported safely
- Process access errors handled appropriately
- Command execution errors logged without sensitive details

## Performance Notes

### System Information Caching
- CPU and memory info collected efficiently
- Process lists optimized for performance
- Environment variable access cached when possible
- Minimal system overhead

### Command Execution
- Configurable timeouts prevent hanging
- Output buffering for large command outputs
- Memory-efficient subprocess handling
- Proper resource cleanup

### Cross-Platform Optimization
- Platform-specific optimizations
- Efficient system call usage
- Minimal dependencies for core functions
- Graceful degradation on limited systems

## Error Reference

### Common Error Types
- `BasicAgentToolsError`: Input validation and system operation errors
- `subprocess.TimeoutExpired`: Command execution timeouts
- `psutil.NoSuchProcess`: Process not found errors
- `PermissionError`: System access permission issues

### Error Messages
All errors include descriptive messages suitable for agent debugging:
- "Command execution timed out after 30 seconds"
- "Process with PID 1234 not found or access denied"
- "Environment variable name must be non-empty string"
- "Working directory does not exist: /invalid/path"

## Testing
Comprehensive test coverage includes:
- Cross-platform compatibility testing
- Command execution with various scenarios
- Process management error conditions
- Environment variable manipulation
- System information accuracy
- Memory and performance testing

**Test Coverage**: Individual function tests + integration tests + cross-platform tests + security tests + agent framework compatibility tests.