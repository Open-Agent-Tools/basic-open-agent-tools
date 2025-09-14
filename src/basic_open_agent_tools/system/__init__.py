"""System tools for cross-platform system operations."""

from .shell import execute_shell_command, run_bash, run_powershell
from .info import get_system_info, get_cpu_info, get_memory_info, get_disk_usage, get_uptime
from .processes import get_current_process_info, list_running_processes, get_process_info, is_process_running
from .environment import get_env_var, set_env_var, list_env_vars
from .runtime import inspect_runtime_environment, get_python_module_info, get_file_system_context, get_network_environment

__all__ = [
    # Shell execution
    "execute_shell_command",
    "run_bash",
    "run_powershell",
    # System information
    "get_system_info",
    "get_cpu_info",
    "get_memory_info",
    "get_disk_usage",
    "get_uptime",
    # Process management
    "get_current_process_info",
    "list_running_processes",
    "get_process_info",
    "is_process_running",
    # Environment variables
    "get_env_var",
    "set_env_var",
    "list_env_vars",
    # Runtime inspection
    "inspect_runtime_environment",
    "get_python_module_info",
    "get_file_system_context",
    "get_network_environment",
]