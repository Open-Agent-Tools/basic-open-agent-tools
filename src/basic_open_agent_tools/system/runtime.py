"""Runtime inspection tools for agents to understand their environment."""

import os
import platform
import sys
import time
from pathlib import Path
from typing import Any, Callable, Union

try:
    from strands import tool as strands_tool
except ImportError:

    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        """Fallback decorator when strands is not available."""
        return func


from ..exceptions import BasicAgentToolsError


@strands_tool
def inspect_runtime_environment() -> dict[
    str, Union[str, int, float, list[str], dict, Any]
]:
    """
    Get comprehensive runtime environment information for the current agent.

    Returns:
        Dictionary with complete runtime details

    Raises:
        BasicAgentToolsError: If runtime information cannot be retrieved
    """
    try:
        # Get current working directory and script location
        cwd = os.getcwd()
        script_path = sys.argv[0] if sys.argv else "unknown"

        # Get Python environment details
        python_executable = sys.executable
        python_version = sys.version
        python_version_info = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

        # Get system and platform details
        system_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0],
            "platform": platform.platform(),
            "node": platform.node(),
        }

        # Get process information
        process_id = os.getpid()
        parent_process_id = os.getppid() if hasattr(os, "getppid") else None

        # Get user information
        try:
            username = os.getlogin()
        except Exception:
            username = os.environ.get("USER", os.environ.get("USERNAME", "unknown"))

        # Get important environment variables
        important_env_vars = {}
        env_var_names = [
            "PATH",
            "HOME",
            "USER",
            "USERNAME",
            "USERPROFILE",
            "TEMP",
            "TMP",
            "PYTHONPATH",
            "VIRTUAL_ENV",
            "CONDA_DEFAULT_ENV",
            "SHELL",
            "TERM",
            "LANG",
            "LC_ALL",
            "TZ",
        ]

        for var_name in env_var_names:
            value = os.environ.get(var_name)
            if value:
                important_env_vars[var_name] = value

        # Get Python path information
        python_paths = sys.path.copy()

        # Get command line arguments
        command_args = sys.argv.copy()

        return {
            # Basic runtime info
            "process_id": process_id,
            "parent_process_id": parent_process_id,
            "username": username,
            "current_working_directory": cwd,
            "script_path": script_path,
            "command_line_args": command_args,
            # Python environment
            "python_executable": python_executable,
            "python_version": python_version_info,
            "python_version_full": python_version.replace("\n", " "),
            "python_paths": python_paths,
            # System information
            "operating_system": system_info["system"],
            "os_release": system_info["release"],
            "os_version": system_info["version"],
            "machine_type": system_info["machine"],
            "processor": system_info["processor"],
            "architecture": system_info["architecture"],
            "platform_string": system_info["platform"],
            "hostname": system_info["node"],
            # Environment variables
            "important_environment_variables": important_env_vars,
            "total_environment_variables": len(os.environ),
            # Runtime state
            "timestamp": time.time(),
            "timestamp_iso": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "timezone": time.tzname[0] if time.tzname else "unknown",
        }

    except Exception as e:
        raise BasicAgentToolsError(f"Failed to inspect runtime environment: {str(e)}")


@strands_tool
def get_python_module_info() -> dict[str, Union[str, int, bool, list[str]]]:
    """
    Get information about loaded Python modules and packages.

    Returns:
        Dictionary with module information

    Raises:
        BasicAgentToolsError: If module information cannot be retrieved
    """
    try:
        # Get all loaded modules
        loaded_modules = list(sys.modules.keys())
        loaded_modules.sort()

        # Get builtin module names
        builtin_modules = list(sys.builtin_module_names)
        builtin_modules.sort()

        # Try to get installed packages (may not work in all environments)
        try:
            import pkg_resources

            installed_packages = [
                f"{pkg.project_name}=={pkg.version}"
                for pkg in pkg_resources.working_set
            ]
            installed_packages.sort()
            has_pkg_resources = True
        except ImportError:
            installed_packages = []
            has_pkg_resources = False

        return {
            "loaded_modules_count": len(loaded_modules),
            "loaded_modules": loaded_modules,
            "builtin_modules_count": len(builtin_modules),
            "builtin_modules": builtin_modules,
            "installed_packages_count": len(installed_packages),
            "installed_packages": installed_packages,
            "pkg_resources_available": has_pkg_resources,
        }

    except Exception as e:
        raise BasicAgentToolsError(f"Failed to get Python module information: {str(e)}")


@strands_tool
def get_file_system_context() -> dict[str, Union[str, list[str], bool, int]]:
    """
    Get file system context information for the current runtime.

    Returns:
        Dictionary with file system context

    Raises:
        BasicAgentToolsError: If file system information cannot be retrieved
    """
    try:
        cwd = Path(os.getcwd())

        # Get directory contents
        try:
            cwd_contents = [item.name for item in cwd.iterdir()]
            cwd_contents.sort()
        except PermissionError:
            cwd_contents = ["<permission denied>"]

        # Check for common project files
        common_files = [
            "requirements.txt",
            "setup.py",
            "pyproject.toml",
            "Pipfile",
            "package.json",
            "Makefile",
            "Dockerfile",
            ".gitignore",
            "README.md",
            "README.rst",
            "LICENSE",
            ".env",
        ]

        present_files = []
        for file_name in common_files:
            if (cwd / file_name).exists():
                present_files.append(file_name)

        # Check for common directories
        common_dirs = [
            "src",
            "lib",
            "bin",
            "tests",
            "test",
            "docs",
            "examples",
            ".git",
            ".github",
            "__pycache__",
            "venv",
            ".venv",
            "env",
        ]

        present_dirs = []
        for dir_name in common_dirs:
            if (cwd / dir_name).is_dir():
                present_dirs.append(dir_name)

        # Get parent directories
        parents = []
        try:
            current = cwd
            for _ in range(5):  # Limit to prevent infinite loops
                current = current.parent
                if current == current.parent:  # Reached root
                    break
                parents.append(str(current))
        except Exception:
            pass

        return {
            "current_directory": str(cwd),
            "current_directory_contents": cwd_contents,
            "current_directory_item_count": len(cwd_contents),
            "common_project_files_present": present_files,
            "common_directories_present": present_dirs,
            "parent_directories": parents,
            "is_git_repository": (cwd / ".git").exists(),
            "is_python_project": any(
                (cwd / f).exists()
                for f in ["setup.py", "pyproject.toml", "requirements.txt"]
            ),
            "has_virtual_environment": any(
                (cwd / d).exists() for d in ["venv", ".venv", "env"]
            ),
        }

    except Exception as e:
        raise BasicAgentToolsError(f"Failed to get file system context: {str(e)}")


@strands_tool
def get_network_environment() -> dict[str, Union[str, list[str], bool, int, dict]]:
    """
    Get basic network environment information (without external dependencies).

    Returns:
        Dictionary with network context

    Raises:
        BasicAgentToolsError: If network information cannot be retrieved
    """
    try:
        import socket

        # Get hostname and FQDN
        hostname = socket.gethostname()
        try:
            fqdn = socket.getfqdn()
        except Exception:
            fqdn = hostname

        # Try to get local IP address
        try:
            # Connect to a remote address to determine local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
        except Exception:
            local_ip = "unknown"

        # Check for common network environment variables
        network_env_vars = {}
        network_var_names = [
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "NO_PROXY",
            "http_proxy",
            "https_proxy",
            "no_proxy",
            "PROXY",
            "ALL_PROXY",
        ]

        for var_name in network_var_names:
            value = os.environ.get(var_name)
            if value:
                network_env_vars[var_name] = value

        return {
            "hostname": hostname,
            "fqdn": fqdn,
            "local_ip_address": local_ip,
            "has_proxy_configuration": len(network_env_vars) > 0,
            "proxy_environment_variables": network_env_vars,
            "socket_family_support": {
                "ipv4": hasattr(socket, "AF_INET"),
                "ipv6": hasattr(socket, "AF_INET6"),
                "unix": hasattr(socket, "AF_UNIX"),
            },
        }

    except Exception as e:
        raise BasicAgentToolsError(
            f"Failed to get network environment information: {str(e)}"
        )
