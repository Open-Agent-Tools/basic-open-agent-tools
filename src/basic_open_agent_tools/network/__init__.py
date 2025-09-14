"""Network tools for AI agents.

This module provides essential network utilities for AI agents, focusing on HTTP requests
and basic connectivity operations. All functions use simplified type signatures to prevent
"signature too complex" errors when used with AI agent frameworks.
"""

from .dns import check_port_open, resolve_hostname, reverse_dns_lookup
from .http_client import http_request

__all__ = ["http_request", "resolve_hostname", "reverse_dns_lookup", "check_port_open"]
