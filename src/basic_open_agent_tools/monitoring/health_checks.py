"""Health check utilities."""

import socket
import time
from typing import Any, Callable, Union

try:
    from strands import tool as strands_tool
except ImportError:

    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        return func


# Import HTTP client from our network module
try:
    from ..network.http_client import http_request

    HAS_HTTP_CLIENT = True
except ImportError:
    HAS_HTTP_CLIENT = False

from ..exceptions import BasicAgentToolsError


@strands_tool
def check_url_status(
    url: str, timeout: int = 10
) -> dict[str, Union[str, int, float, bool]]:
    """Check the status of a URL."""
    if not HAS_HTTP_CLIENT:
        raise BasicAgentToolsError("HTTP client not available for URL status checks")

    if not isinstance(url, str) or not url.strip():
        raise BasicAgentToolsError("URL must be a non-empty string")

    try:
        start_time = time.time()
        response = http_request("GET", url, timeout=timeout)
        end_time = time.time()

        response_time = end_time - start_time
        is_healthy = response["status_code"] < 400

        return {
            "url": url,
            "status_code": response["status_code"],
            "response_time_seconds": round(response_time, 3),
            "is_healthy": is_healthy,
            "check_timestamp": end_time,
            "timeout_seconds": timeout,
        }
    except Exception as e:
        return {
            "url": url,
            "status_code": 0,
            "response_time_seconds": 0.0,
            "is_healthy": False,
            "error": str(e),
            "check_timestamp": time.time(),
            "timeout_seconds": timeout,
        }


@strands_tool
def ping_host(
    hostname: str, port: int = 80, timeout: int = 5
) -> dict[str, Union[str, int, float, bool]]:
    """Ping a host to check connectivity."""
    if not isinstance(hostname, str) or not hostname.strip():
        raise BasicAgentToolsError("Hostname must be a non-empty string")

    if not isinstance(port, int) or port < 1 or port > 65535:
        raise BasicAgentToolsError("Port must be an integer between 1 and 65535")

    try:
        start_time = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        result = sock.connect_ex((hostname, port))
        sock.close()

        end_time = time.time()
        response_time = end_time - start_time
        is_reachable = result == 0

        return {
            "hostname": hostname,
            "port": port,
            "is_reachable": is_reachable,
            "response_time_seconds": round(response_time, 3),
            "timeout_seconds": timeout,
            "check_timestamp": end_time,
        }
    except Exception as e:
        return {
            "hostname": hostname,
            "port": port,
            "is_reachable": False,
            "response_time_seconds": 0.0,
            "error": str(e),
            "timeout_seconds": timeout,
            "check_timestamp": time.time(),
        }
