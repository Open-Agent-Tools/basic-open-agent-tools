"""DNS resolution and network utilities."""

import socket
from typing import Any, Callable, Union

try:
    from strands import tool as strands_tool
except ImportError:

    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        """Fallback decorator when strands is not available."""
        return func


from ..exceptions import BasicAgentToolsError


@strands_tool
def resolve_hostname(
    hostname: str,
) -> dict[str, Union[str, int, list[str], list[Union[str, int]]]]:
    """
    Resolve a hostname to IP addresses.

    Args:
        hostname: Hostname to resolve

    Returns:
        Dictionary with resolution results

    Raises:
        BasicAgentToolsError: If resolution fails
    """
    if not isinstance(hostname, str) or not hostname.strip():
        raise BasicAgentToolsError("Hostname must be a non-empty string")

    hostname = hostname.strip()

    try:
        # Get all IP addresses for the hostname
        addr_info = socket.getaddrinfo(hostname, None)

        # Extract unique IP addresses
        ipv4_addresses = []
        ipv6_addresses = []

        for info in addr_info:
            family, _, _, _, sockaddr = info
            ip = sockaddr[0]

            if family == socket.AF_INET:
                if ip not in ipv4_addresses:
                    ipv4_addresses.append(ip)
            elif family == socket.AF_INET6:
                if ip not in ipv6_addresses:
                    ipv6_addresses.append(ip)

        return {
            "hostname": hostname,
            "ipv4_addresses": ipv4_addresses,
            "ipv6_addresses": ipv6_addresses,
            "total_addresses": len(ipv4_addresses) + len(ipv6_addresses),
            "resolution_status": "success",
        }

    except socket.gaierror as e:
        raise BasicAgentToolsError(f"Failed to resolve hostname '{hostname}': {str(e)}")
    except Exception as e:
        raise BasicAgentToolsError(f"DNS resolution error: {str(e)}")


@strands_tool
def reverse_dns_lookup(ip_address: str) -> dict[str, Union[str, bool]]:
    """
    Perform reverse DNS lookup for an IP address.

    Args:
        ip_address: IP address to lookup

    Returns:
        Dictionary with reverse lookup results

    Raises:
        BasicAgentToolsError: If lookup fails
    """
    if not isinstance(ip_address, str) or not ip_address.strip():
        raise BasicAgentToolsError("IP address must be a non-empty string")

    ip_address = ip_address.strip()

    try:
        # Validate IP address format
        socket.inet_pton(socket.AF_INET, ip_address)
        ip_family = "IPv4"
    except OSError:
        try:
            socket.inet_pton(socket.AF_INET6, ip_address)
            ip_family = "IPv6"
        except OSError:
            raise BasicAgentToolsError(f"Invalid IP address format: {ip_address}")

    try:
        # Perform reverse DNS lookup
        hostname, _, _ = socket.gethostbyaddr(ip_address)

        return {
            "ip_address": ip_address,
            "ip_family": ip_family,
            "hostname": hostname,
            "lookup_successful": True,
            "lookup_status": "success",
        }

    except socket.herror:
        return {
            "ip_address": ip_address,
            "ip_family": ip_family,
            "hostname": "",
            "lookup_successful": False,
            "lookup_status": "no_reverse_dns_record",
        }
    except Exception as e:
        raise BasicAgentToolsError(f"Reverse DNS lookup error: {str(e)}")


@strands_tool
def check_port_open(
    host: str, port: int, timeout: int = 5
) -> dict[str, Union[str, int, bool, float]]:
    """
    Check if a port is open on a host.

    Args:
        host: Hostname or IP address
        port: Port number to check
        timeout: Connection timeout in seconds

    Returns:
        Dictionary with port check results

    Raises:
        BasicAgentToolsError: If parameters are invalid
    """
    if not isinstance(host, str) or not host.strip():
        raise BasicAgentToolsError("Host must be a non-empty string")

    if not isinstance(port, int) or port < 1 or port > 65535:
        raise BasicAgentToolsError("Port must be an integer between 1 and 65535")

    if not isinstance(timeout, int) or timeout < 1 or timeout > 30:
        raise BasicAgentToolsError(
            "Timeout must be an integer between 1 and 30 seconds"
        )

    host = host.strip()

    import time

    start_time = time.time()

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        result = sock.connect_ex((host, port))
        sock.close()

        end_time = time.time()
        response_time = round(
            (end_time - start_time) * 1000, 2
        )  # Convert to milliseconds

        is_open = result == 0

        return {
            "host": host,
            "port": port,
            "is_open": is_open,
            "response_time_ms": response_time,
            "timeout_seconds": timeout,
            "check_status": "success" if is_open else "closed_or_filtered",
        }

    except socket.timeout:
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)

        return {
            "host": host,
            "port": port,
            "is_open": False,
            "response_time_ms": response_time,
            "timeout_seconds": timeout,
            "check_status": "timeout",
        }
    except Exception as e:
        raise BasicAgentToolsError(f"Port check error: {str(e)}")
