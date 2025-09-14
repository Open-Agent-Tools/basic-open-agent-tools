"""Network tools for AI agents.

This module provides essential network utilities for AI agents, focusing on HTTP requests
and basic connectivity operations. All functions use simplified type signatures to prevent
"signature too complex" errors when used with AI agent frameworks.
"""

from .http_client import http_request
from .dns import resolve_hostname, reverse_dns_lookup, check_port_open

__all__ = ["http_request", "resolve_hostname", "reverse_dns_lookup", "check_port_open"]
