# Logging Tools

## Overview
Comprehensive structured logging and log rotation utilities for AI agents with simplified type signatures and flexible configuration.

## Current Status
**✅ FULLY IMPLEMENTED MODULE** - 5 functions available

This module provides essential logging functionality for AI agents with agent-friendly signatures and production-ready features.

## Current Features
- ✅ **Structured Logging**: log_info, log_error with JSON formatting
- ✅ **Logger Configuration**: configure_logger with customizable settings
- ✅ **Log Rotation**: setup_rotating_log with automatic file management
- ✅ **Maintenance**: cleanup_old_logs for log file cleanup

## Function Reference

### Basic Logging Operations

#### log_info
Log informational messages with structured formatting.

```python
def log_info(message: str, context: Dict[str, str] = None) -> Dict[str, Union[str, bool]]
```

**Parameters:**
- `message`: The log message to record
- `context`: Optional dictionary of additional context fields

**Returns:**
Dictionary with `message`, `level`, `timestamp`, `log_status`, and optional `context` information.

**Example:**
```python
result = log_info("User login successful", {"user_id": "123", "ip": "192.168.1.1"})
print(f"Logged at: {result['timestamp']}")
```

#### log_error
Log error messages with structured formatting and optional exception details.

```python
def log_error(message: str, context: Dict[str, str] = None) -> Dict[str, Union[str, bool]]
```

**Parameters:**
- `message`: The error message to record
- `context`: Optional dictionary of additional context fields

**Returns:**
Dictionary with error logging information including message, level, timestamp, and context.

**Example:**
```python
try:
    # Some operation that might fail
    risky_operation()
except Exception as e:
    result = log_error(f"Operation failed: {str(e)}", {"operation": "data_processing"})
    print(f"Error logged: {result['log_status']}")
```

### Logger Configuration

#### configure_logger
Configure a logger with specified settings and output options.

```python
def configure_logger(
    logger_name: str,
    log_level: str = "INFO",
    log_format: str = "structured",
    output_file: str = None
) -> Dict[str, Union[str, bool]]
```

**Parameters:**
- `logger_name`: Name for the logger instance
- `log_level`: Logging level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
- `log_format`: Format type ("structured" for JSON, "simple" for plain text)
- `output_file`: Optional file path for log output

**Returns:**
Dictionary with logger configuration details and setup status.

**Example:**
```python
# Configure structured JSON logging to file
result = configure_logger(
    "agent_logger",
    log_level="DEBUG",
    log_format="structured",
    output_file="agent.log"
)
print(f"Logger configured: {result['configuration_status']}")
```

### Log Rotation and Management

#### setup_rotating_log
Set up automatic log file rotation with size and backup limits.

```python
def setup_rotating_log(
    log_file: str,
    max_size_mb: int = 10,
    backup_count: int = 5,
    log_level: str = "INFO"
) -> Dict[str, Union[str, int, bool]]
```

**Parameters:**
- `log_file`: Path to the log file
- `max_size_mb`: Maximum size per log file in MB (1-100)
- `backup_count`: Number of backup files to keep (1-20)
- `log_level`: Logging level for the rotating logger

**Returns:**
Dictionary with rotation setup details including file paths, size limits, and configuration status.

**Example:**
```python
# Set up log rotation: 10MB files, keep 5 backups
result = setup_rotating_log(
    "application.log",
    max_size_mb=10,
    backup_count=5,
    log_level="INFO"
)
print(f"Rotation setup: {result['rotation_status']}")
print(f"Max size: {result['max_size_mb']} MB")
```

#### cleanup_old_logs
Clean up old log files based on age or count criteria.

```python
def cleanup_old_logs(
    log_directory: str,
    max_age_days: int = 30,
    max_files: int = 50
) -> Dict[str, Union[str, int, List[str]]]
```

**Parameters:**
- `log_directory`: Directory containing log files
- `max_age_days`: Maximum age of log files in days (1-365)
- `max_files`: Maximum number of log files to keep (1-1000)

**Returns:**
Dictionary with cleanup results including files removed, files kept, and cleanup status.

**Example:**
```python
# Clean up logs older than 30 days, keep max 50 files
result = cleanup_old_logs(
    "/var/log/myapp/",
    max_age_days=30,
    max_files=50
)
print(f"Removed {result['files_removed']} old log files")
print(f"Kept {result['files_kept']} files")
```

## Agent-Friendly Design Features

### Structured Logging
- **JSON Format Support**: Machine-readable structured logs
- **Context Fields**: Flexible additional data inclusion
- **Timestamp Precision**: ISO format timestamps with timezone
- **Level Consistency**: Standard logging levels across all functions

### Simplified Type Signatures
All functions use basic Python types (str, int, Dict, List) to prevent "signature too complex" errors in agent frameworks.

### Production-Ready Features
- **Automatic Rotation**: Prevents disk space issues
- **Backup Management**: Configurable retention policies
- **Error Handling**: Graceful failure handling
- **Performance**: Minimal overhead logging

### Cross-Platform Compatibility
- **File Path Handling**: Cross-platform path resolution
- **Permission Management**: Safe file creation and rotation
- **Directory Creation**: Automatic log directory setup
- **Error Recovery**: Graceful handling of permission issues

## Common Use Cases

### Application Logging
```python
# Configure application logger with rotation
logger_result = configure_logger(
    "main_app",
    log_level="INFO",
    log_format="structured",
    output_file="app.log"
)

# Set up rotation for the log file
rotation_result = setup_rotating_log(
    "app.log",
    max_size_mb=5,
    backup_count=10,
    log_level="INFO"
)

# Log application events
log_info("Application started", {"version": "1.0.0", "environment": "production"})
log_info("User action", {"user": "john_doe", "action": "login", "success": True})
```

### Error Tracking
```python
# Configure error-specific logging
error_logger = configure_logger(
    "error_tracker",
    log_level="ERROR",
    log_format="structured",
    output_file="errors.log"
)

# Log errors with context
try:
    process_data(user_input)
except ValidationError as e:
    log_error("Input validation failed", {
        "error_type": "ValidationError",
        "input_size": len(user_input),
        "validation_rule": str(e)
    })
except ProcessingError as e:
    log_error("Data processing failed", {
        "error_type": "ProcessingError",
        "stage": e.stage,
        "data_id": e.data_id
    })
```

### Maintenance and Cleanup
```python
# Regular log maintenance
def maintain_logs():
    # Clean up old application logs
    app_cleanup = cleanup_old_logs(
        "/var/log/myapp/",
        max_age_days=14,
        max_files=100
    )

    # Clean up error logs (keep longer)
    error_cleanup = cleanup_old_logs(
        "/var/log/myapp/errors/",
        max_age_days=60,
        max_files=200
    )

    # Log maintenance results
    log_info("Log maintenance completed", {
        "app_files_removed": app_cleanup['files_removed'],
        "error_files_removed": error_cleanup['files_removed'],
        "maintenance_status": "completed"
    })

# Schedule maintenance (example with timing)
import time
maintain_logs()
```

### Agent Activity Logging
```python
# Set up agent-specific logging
agent_logger = configure_logger(
    "ai_agent",
    log_level="DEBUG",
    log_format="structured",
    output_file="agent_activity.log"
)

# Set up rotation for detailed logging
setup_rotating_log(
    "agent_activity.log",
    max_size_mb=20,
    backup_count=15,
    log_level="DEBUG"
)

# Log agent operations
log_info("Agent task started", {
    "task_id": "task_123",
    "task_type": "data_analysis",
    "input_size": 1024
})

log_info("Agent decision made", {
    "task_id": "task_123",
    "decision": "proceed_with_analysis",
    "confidence": 0.95
})

# Log completion
log_info("Agent task completed", {
    "task_id": "task_123",
    "duration_seconds": 45.6,
    "output_size": 2048,
    "success": True
})
```

## Agent Integration

### Google ADK
```python
import basic_open_agent_tools as boat
logging_tools = boat.load_all_logging_tools()
agent = Agent(tools=logging_tools)
```

### Strands Agents
All functions include the `@strands_tool` decorator for native compatibility:
```python
from basic_open_agent_tools.logging import log_info
# Function is automatically compatible with Strands Agents
```

### Integration with Other Modules
```python
# Combine with system monitoring
from basic_open_agent_tools.system import get_system_info
from basic_open_agent_tools.logging import log_info

# Log system status
system_info = get_system_info()
log_info("System status check", {
    "os": system_info['system'],
    "platform": system_info['platform'],
    "hostname": system_info['hostname']
})
```

## Configuration Examples

### Development Environment
```python
# Development: Verbose logging to console and file
configure_logger(
    "dev_logger",
    log_level="DEBUG",
    log_format="structured",
    output_file="development.log"
)

# Small rotation for development
setup_rotating_log(
    "development.log",
    max_size_mb=2,
    backup_count=3,
    log_level="DEBUG"
)
```

### Production Environment
```python
# Production: INFO level with efficient rotation
configure_logger(
    "prod_logger",
    log_level="INFO",
    log_format="structured",
    output_file="production.log"
)

# Larger rotation for production
setup_rotating_log(
    "production.log",
    max_size_mb=50,
    backup_count=20,
    log_level="INFO"
)

# Regular cleanup in production
cleanup_old_logs(
    "/var/log/production/",
    max_age_days=90,
    max_files=500
)
```

## Dependencies
All logging functions use Python standard library modules (logging, logging.handlers, os, time) - no additional dependencies required.

## Security Considerations

### Safe Logging Practices
- **No Sensitive Data**: Avoid logging passwords, tokens, or personal information
- **Context Validation**: Input validation for context fields
- **File Permissions**: Safe log file creation with appropriate permissions
- **Path Validation**: Prevention of directory traversal attacks

### Error Handling
- **Permission Errors**: Graceful handling of file permission issues
- **Disk Space**: Safe handling of disk full conditions
- **Rotation Failures**: Fallback logging when rotation fails
- **Configuration Errors**: Clear error messages for invalid settings

## Performance Notes

### Logging Overhead
- **Minimal Impact**: Efficient structured logging implementation
- **Async Support**: Compatible with asynchronous applications
- **Memory Usage**: Bounded memory usage with rotation
- **I/O Optimization**: Buffered writing for performance

### File Management
- **Rotation Efficiency**: Fast log file rotation
- **Cleanup Performance**: Efficient old file cleanup
- **Disk Usage**: Predictable disk space usage
- **Backup Management**: Automatic old backup removal

## Error Reference

### Common Error Types
- `BasicAgentToolsError`: Configuration and validation errors
- `PermissionError`: File system permission issues
- `OSError`: Disk space or file system errors
- `ValueError`: Invalid parameter values

### Error Messages
All errors include descriptive messages suitable for agent debugging:
- "Log directory does not exist and cannot be created"
- "Invalid log level specified: INVALID"
- "Log file rotation failed due to permission error"
- "Cleanup operation failed: insufficient permissions"

## Testing
Comprehensive test coverage includes:
- Structured logging format validation
- Log rotation functionality testing
- File cleanup operations testing
- Cross-platform file handling
- Error condition testing
- Performance impact testing

**Test Coverage**: Individual function tests + integration tests + file system tests + performance tests + agent framework compatibility tests.