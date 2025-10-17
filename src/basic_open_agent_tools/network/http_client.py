"""HTTP client tools for AI agents.

Provides simplified HTTP request functionality with agent-friendly type signatures
and comprehensive error handling.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
import warnings
from typing import Any, Union

from .._logging import get_logger
from ..decorators import strands_tool
from ..exceptions import BasicAgentToolsError

logger = get_logger("network.http_client")


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """HTTP handler that prevents automatic redirect following.

    This handler is used when follow_redirects=False to prevent urllib
    from automatically following 3xx redirect responses.
    """

    def redirect_request(
        self,
        req: Any,
        fp: Any,
        code: Any,
        msg: Any,
        headers: Any,
        newurl: Any,
    ) -> None:
        """Override redirect_request to prevent automatic redirects."""
        return None


@strands_tool
def http_request(
    method: str,
    url: str,
    headers: str,
    body: str,
    timeout: int,
    follow_redirects: bool,
    verify_ssl: bool,
) -> dict[str, Union[str, int]]:
    """Make an HTTP request with simplified parameters.

    This function makes HTTP requests and returns response information in a
    consistent dictionary format. HTTP errors (4xx, 5xx) are returned as
    responses rather than raising exceptions, allowing agents to handle
    error responses programmatically.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        url: Target URL for the request
        headers: HTTP headers as JSON string (use "{}" for no headers)
        body: Request body content (use "" for no body)
        timeout: Request timeout in seconds
        follow_redirects: Whether to follow HTTP redirects
        verify_ssl: Whether to verify SSL certificates

    Returns:
        Dictionary containing:
        - status_code: HTTP response status code (includes 4xx/5xx errors)
        - headers: Response headers as JSON string
        - body: Response body content (or error message for HTTP errors)
        - url: Final URL (after redirects if followed)

        Note: HTTP errors (404, 500, etc.) are returned as responses with
        status_code set to the error code. This allows agents to inspect
        and handle HTTP errors programmatically.

    Raises:
        BasicAgentToolsError: Only for network errors (connection failures,
        timeouts, DNS errors) or invalid parameters. HTTP errors (4xx, 5xx)
        are returned as responses, not raised as exceptions.

    Example:
        >>> # Successful request
        >>> response = http_request("GET", "https://api.github.com/user", "{}", "", 30, True, True)
        >>> print(response["status_code"])
        200

        >>> # HTTP error (404) returned as response
        >>> response = http_request("GET", "https://api.github.com/notfound", "{}", "", 30, True, True)
        >>> print(response["status_code"])
        404
    """
    # Parse headers from JSON string
    if not isinstance(headers, str):
        raise BasicAgentToolsError("headers must be a JSON string")

    try:
        headers_dict = json.loads(headers) if headers and headers != "{}" else {}
        if not isinstance(headers_dict, dict):
            raise BasicAgentToolsError("headers must be a JSON object")
    except json.JSONDecodeError as e:
        raise BasicAgentToolsError(f"Invalid JSON in headers: {e}")

    if not method or not isinstance(method, str):
        raise BasicAgentToolsError("Method must be a non-empty string")

    if not url or not isinstance(url, str):
        raise BasicAgentToolsError("URL must be a non-empty string")

    if not url.startswith(("http://", "https://")):
        raise BasicAgentToolsError("URL must start with http:// or https://")

    method = method.upper()

    # Log the HTTP request details
    body_info = f" ({len(body)} bytes)" if body else ""
    headers_info = f", {len(headers_dict)} headers" if headers_dict else ""
    logger.info(f"{method} {url}{body_info}")
    logger.debug(
        f"Timeout: {timeout}s{headers_info}, follow_redirects: {follow_redirects}, verify_ssl: {verify_ssl}"
    )

    # Prepare headers
    request_headers = dict(headers_dict)

    # Set default User-Agent if not provided
    if "User-Agent" not in request_headers:
        request_headers["User-Agent"] = "basic-open-agent-tools/0.9.1"

    # Prepare request body
    request_body = None
    if body is not None:
        if not isinstance(body, str):
            raise BasicAgentToolsError("Body must be a string")
        request_body = body.encode("utf-8")

        # Set Content-Type if not provided and body contains JSON-like content
        if "Content-Type" not in request_headers:
            try:
                json.loads(body)
                request_headers["Content-Type"] = "application/json"
            except (json.JSONDecodeError, ValueError):
                request_headers["Content-Type"] = "text/plain"

    try:
        # Create request object
        req = urllib.request.Request(
            url=url, data=request_body, headers=request_headers, method=method
        )

        # Configure SSL context if needed
        if not verify_ssl:
            import ssl

            warnings.warn(
                f"SSL certificate verification disabled for {url}. "
                "This connection is vulnerable to man-in-the-middle attacks. "
                "Only use verify_ssl=False for testing with trusted servers.",
                RuntimeWarning,
                stacklevel=2,
            )

            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        else:
            ssl_context = None

        # Configure redirects
        if not follow_redirects:
            opener = urllib.request.build_opener(_NoRedirectHandler)
            if ssl_context:
                https_handler = urllib.request.HTTPSHandler(context=ssl_context)
                opener.add_handler(https_handler)
        else:
            if ssl_context:
                https_handler = urllib.request.HTTPSHandler(context=ssl_context)
                opener = urllib.request.build_opener(https_handler)
            else:
                opener = urllib.request.build_opener()

        # Make the request
        start_time = time.time()
        if not follow_redirects or ssl_context:
            response = opener.open(req, timeout=timeout)
        else:
            response = urllib.request.urlopen(req, timeout=timeout)

        # Read response
        response_body = response.read()
        response_headers = dict(response.headers)
        end_time = time.time()
        request_time = end_time - start_time

        # Try to decode response body
        try:
            decoded_body = response_body.decode("utf-8")
        except UnicodeDecodeError:
            # If decoding fails, return as base64
            import base64

            decoded_body = f"[Binary content - base64]: {base64.b64encode(response_body).decode('ascii')}"

        result = {
            "status_code": response.getcode(),
            "headers": json.dumps(response_headers, indent=2),
            "body": decoded_body,
            "url": response.geturl(),
        }

        # Log response details
        body_size = len(decoded_body) if decoded_body else 0
        logger.info(
            f"Response: {result['status_code']} ({request_time:.3f}s, {body_size} bytes)"
        )
        logger.debug(
            f"Final URL: {result['url']}, Headers: {len(response_headers)} headers"
        )

        return result

    except urllib.error.HTTPError as e:
        # Handle HTTP errors (4xx, 5xx)
        error_body = ""
        try:
            error_body = e.read().decode("utf-8")
        except Exception:
            error_body = "[Could not decode error response]"

        return {
            "status_code": e.code,
            "headers": json.dumps(dict(e.headers) if e.headers else {}, indent=2),
            "body": error_body,
            "url": url,
        }

    except urllib.error.URLError as e:
        raise BasicAgentToolsError(f"Network error: {str(e)}")

    except Exception as e:
        raise BasicAgentToolsError(f"Request failed: {str(e)}")
