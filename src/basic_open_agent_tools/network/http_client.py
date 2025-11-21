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
from typing import Any, Optional, Union, cast

from .._logging import get_logger
from ..decorators import strands_tool
from ..exceptions import BasicAgentToolsError

logger = get_logger("network.http_client")


def _parse_headers_json(headers: str) -> dict[str, str]:
    """Parse headers from JSON string format.

    Args:
        headers: JSON string containing headers

    Returns:
        Dictionary of header name-value pairs

    Raises:
        BasicAgentToolsError: If headers invalid or not JSON object
    """
    if not isinstance(headers, str):
        raise BasicAgentToolsError("headers must be a JSON string")

    try:
        headers_dict = json.loads(headers) if headers and headers != "{}" else {}
        if not isinstance(headers_dict, dict):
            raise BasicAgentToolsError("headers must be a JSON object")
        return headers_dict
    except json.JSONDecodeError as e:
        raise BasicAgentToolsError(f"Invalid JSON in headers: {e}")


def _validate_http_method(method: str) -> str:
    """Validate and normalize HTTP method.

    Args:
        method: HTTP method string

    Returns:
        Uppercase normalized method

    Raises:
        BasicAgentToolsError: If method invalid
    """
    if not method or not isinstance(method, str):
        raise BasicAgentToolsError("Method must be a non-empty string")
    return method.upper()


def _validate_http_url(url: str) -> None:
    """Validate URL format.

    Args:
        url: URL string to validate

    Raises:
        BasicAgentToolsError: If URL invalid
    """
    if not url or not isinstance(url, str):
        raise BasicAgentToolsError("URL must be a non-empty string")

    if not url.startswith(("http://", "https://")):
        raise BasicAgentToolsError("URL must start with http:// or https://")


def _prepare_request_headers(headers_dict: dict[str, str]) -> dict[str, str]:
    """Prepare request headers with defaults.

    Args:
        headers_dict: Initial headers dictionary

    Returns:
        Headers with defaults added
    """
    request_headers = dict(headers_dict)

    # Set default User-Agent if not provided
    if "User-Agent" not in request_headers:
        request_headers["User-Agent"] = "basic-open-agent-tools/0.9.1"

    return request_headers


def _prepare_request_body(
    body: str, headers: dict[str, str]
) -> tuple[Optional[bytes], dict[str, str]]:
    """Prepare request body and update Content-Type header.

    Args:
        body: Request body string
        headers: Request headers (will be copied and updated)

    Returns:
        Tuple of (encoded body bytes, updated headers dict)

    Raises:
        BasicAgentToolsError: If body invalid type
    """
    request_body = None
    updated_headers = dict(headers)

    if body is not None:
        if not isinstance(body, str):
            raise BasicAgentToolsError("Body must be a string")
        request_body = body.encode("utf-8")

        # Set Content-Type if not provided and body contains JSON-like content
        if "Content-Type" not in updated_headers:
            try:
                json.loads(body)
                updated_headers["Content-Type"] = "application/json"
            except (json.JSONDecodeError, ValueError):
                updated_headers["Content-Type"] = "text/plain"

    return request_body, updated_headers


def _create_ssl_context(verify_ssl: bool, url: str) -> Any:
    """Create SSL context if SSL verification disabled.

    Args:
        verify_ssl: Whether to verify SSL certificates
        url: URL being requested (for warning message)

    Returns:
        SSL context if verify_ssl=False, None otherwise
    """
    if not verify_ssl:
        import ssl

        warnings.warn(
            f"SSL certificate verification disabled for {url}. "
            "This connection is vulnerable to man-in-the-middle attacks. "
            "Only use verify_ssl=False for testing with trusted servers.",
            RuntimeWarning,
            stacklevel=3,
        )

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        return ssl_context

    return None


def _create_url_opener(
    follow_redirects: bool, ssl_context: Any
) -> urllib.request.OpenerDirector:
    """Create URL opener with redirect and SSL configuration.

    Args:
        follow_redirects: Whether to follow HTTP redirects
        ssl_context: SSL context or None

    Returns:
        Configured URL opener
    """
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

    return opener


def _decode_response_body(response_body: bytes) -> str:
    """Decode response body to string.

    Args:
        response_body: Raw response bytes

    Returns:
        Decoded string (UTF-8 or base64 for binary)
    """
    try:
        return response_body.decode("utf-8")
    except UnicodeDecodeError:
        # If decoding fails, return as base64
        import base64

        return f"[Binary content - base64]: {base64.b64encode(response_body).decode('ascii')}"


def _build_response_dict(
    response: Any, decoded_body: str
) -> dict[str, Union[str, int]]:
    """Build response dictionary from HTTP response.

    Args:
        response: urllib HTTP response object
        decoded_body: Decoded response body string

    Returns:
        Dictionary with status_code, headers, body, url
    """
    response_headers = dict(response.headers)

    return {
        "status_code": response.getcode(),
        "headers": json.dumps(response_headers, indent=2),
        "body": decoded_body,
        "url": response.geturl(),
    }


def _handle_http_error(
    e: urllib.error.HTTPError, url: str
) -> dict[str, Union[str, int]]:
    """Handle HTTP error and return as response dictionary.

    Args:
        e: HTTPError exception
        url: Original request URL

    Returns:
        Response dictionary with error details
    """
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
    # Validate and parse input parameters
    headers_dict = _parse_headers_json(headers)
    method = _validate_http_method(method)
    _validate_http_url(url)

    # Log request details
    body_info = f" ({len(body)} bytes)" if body else ""
    headers_info = f", {len(headers_dict)} headers" if headers_dict else ""
    logger.info(f"{method} {url}{body_info}")
    logger.debug(
        f"Timeout: {timeout}s{headers_info}, follow_redirects: {follow_redirects}, verify_ssl: {verify_ssl}"
    )

    # Prepare request components
    request_headers = _prepare_request_headers(headers_dict)
    request_body, request_headers = _prepare_request_body(body, request_headers)

    try:
        # Create request object
        req = urllib.request.Request(
            url=url, data=request_body, headers=request_headers, method=method
        )

        # Configure SSL and redirects
        ssl_context = _create_ssl_context(verify_ssl, url)
        opener = _create_url_opener(follow_redirects, ssl_context)

        # Execute request
        start_time = time.time()
        if not follow_redirects or ssl_context:
            response = opener.open(req, timeout=timeout)
        else:
            response = urllib.request.urlopen(req, timeout=timeout)

        # Process response
        response_body = response.read()
        request_time = time.time() - start_time

        decoded_body = _decode_response_body(response_body)
        result = _build_response_dict(response, decoded_body)

        # Log response details
        body_size = len(decoded_body) if decoded_body else 0
        response_headers = json.loads(cast(str, result["headers"]))
        logger.info(
            f"Response: {result['status_code']} ({request_time:.3f}s, {body_size} bytes)"
        )
        logger.debug(
            f"Final URL: {result['url']}, Headers: {len(response_headers)} headers"
        )

        return result

    except urllib.error.HTTPError as e:
        return _handle_http_error(e, url)

    except urllib.error.URLError as e:
        raise BasicAgentToolsError(f"Network error: {str(e)}")

    except Exception as e:
        raise BasicAgentToolsError(f"Request failed: {str(e)}")
