"""HTTP client tools for AI agents.

Provides simplified HTTP request functionality with agent-friendly type signatures
and comprehensive error handling.
"""

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable, Optional, Union

try:
    from strands import tool as strands_tool
except ImportError:
    # Create a no-op decorator if strands is not installed
    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        return func


from ..exceptions import BasicAgentToolsError


@strands_tool
def http_request(
    method: str,
    url: str,
    headers: Optional[dict[str, str]] = None,
    body: Optional[str] = None,
    timeout: int = 30,
    follow_redirects: bool = True,
    verify_ssl: bool = True,
) -> dict[str, Union[str, int]]:
    """Make an HTTP request with simplified parameters.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        url: Target URL for the request
        headers: Optional HTTP headers as key-value pairs
        body: Optional request body (for POST, PUT, etc.)
        timeout: Request timeout in seconds (default: 30)
        follow_redirects: Whether to follow HTTP redirects (default: True)
        verify_ssl: Whether to verify SSL certificates (default: True)

    Returns:
        Dictionary containing:
        - status_code: HTTP response status code
        - headers: Response headers as string
        - body: Response body content
        - url: Final URL (after redirects)

    Raises:
        BasicAgentToolsError: If request fails or invalid parameters

    Example:
        >>> response = http_request("GET", "https://api.github.com/user")
        >>> print(response["status_code"])
        200
    """
    # Log the HTTP request details for security auditing
    body_info = f" with {len(body)} char body" if body else ""
    headers_info = f" with {len(headers)} headers" if headers else ""
    print(f"[HTTP] {method} {url}{body_info}{headers_info} (timeout={timeout}s)")

    if not method or not isinstance(method, str):
        raise BasicAgentToolsError("Method must be a non-empty string")

    if not url or not isinstance(url, str):
        raise BasicAgentToolsError("URL must be a non-empty string")

    if not url.startswith(("http://", "https://")):
        raise BasicAgentToolsError("URL must start with http:// or https://")

    method = method.upper()

    # Prepare headers
    request_headers = {}
    if headers:
        if not isinstance(headers, dict):
            raise BasicAgentToolsError("Headers must be a dictionary")
        request_headers.update(headers)

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

            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        else:
            ssl_context = None

        # Configure redirects
        if not follow_redirects:

            class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
                def redirect_request(
                    self,
                    req: Any,
                    fp: Any,
                    code: Any,
                    msg: Any,
                    headers: Any,
                    newurl: Any,
                ) -> None:
                    return None

            opener = urllib.request.build_opener(NoRedirectHandler)
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
        if not follow_redirects or ssl_context:
            response = opener.open(req, timeout=timeout)
        else:
            response = urllib.request.urlopen(req, timeout=timeout)

        # Read response
        response_body = response.read()
        response_headers = dict(response.headers)

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
        print(f"[HTTP] Response: {result['status_code']} ({body_size} chars)")

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


@strands_tool
def http_get(
    url: str, headers: Optional[dict[str, str]] = None, timeout: int = 30
) -> dict[str, Union[str, int]]:
    """Convenience function for HTTP GET requests.

    Args:
        url: Target URL for the request
        headers: Optional HTTP headers
        timeout: Request timeout in seconds

    Returns:
        Dictionary with response data (same as http_request)

    Example:
        >>> response = http_get("https://api.github.com/user")
        >>> print(response["status_code"])
        200
    """
    return http_request("GET", url, headers=headers, timeout=timeout)  # type: ignore[no-any-return]


@strands_tool
def http_post(
    url: str,
    body: Optional[str] = None,
    headers: Optional[dict[str, str]] = None,
    timeout: int = 30,
) -> dict[str, Union[str, int]]:
    """Convenience function for HTTP POST requests.

    Args:
        url: Target URL for the request
        body: Request body content
        headers: Optional HTTP headers
        timeout: Request timeout in seconds

    Returns:
        Dictionary with response data (same as http_request)

    Example:
        >>> data = '{"name": "test"}'
        >>> response = http_post("https://api.example.com/users", body=data)
        >>> print(response["status_code"])
        201
    """
    return http_request("POST", url, headers=headers, body=body, timeout=timeout)  # type: ignore[no-any-return]
