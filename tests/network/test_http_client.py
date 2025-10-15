"""Tests for HTTP client tools."""

from unittest.mock import Mock, patch

import pytest

from basic_open_agent_tools.exceptions import BasicAgentToolsError
from basic_open_agent_tools.network.http_client import http_request


class TestHttpRequest:
    """Test the http_request function."""

    def test_invalid_method(self):
        """Test error handling for invalid method."""
        with pytest.raises(
            BasicAgentToolsError, match="Method must be a non-empty string"
        ):
            http_request("", "https://example.com", "{}", "", 30, True, True)

    def test_invalid_url(self):
        """Test error handling for invalid URL."""
        with pytest.raises(
            BasicAgentToolsError, match="URL must be a non-empty string"
        ):
            http_request("GET", "", "{}", "", 30, True, True)

        with pytest.raises(BasicAgentToolsError, match="URL must start with http"):
            http_request("GET", "ftp://example.com", "{}", "", 30, True, True)

    def test_invalid_headers(self):
        """Test error handling for invalid headers."""
        with pytest.raises(BasicAgentToolsError, match="headers must be a JSON string"):
            http_request("GET", "https://example.com", 123, "", 30, True, True)

    @patch("urllib.request.urlopen")
    def test_successful_get_request(self, mock_urlopen):
        """Test successful GET request."""
        # Mock response
        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.read.return_value = b'{"message": "success"}'
        mock_response.geturl.return_value = "https://example.com"
        mock_urlopen.return_value = mock_response

        result = http_request("GET", "https://example.com", "{}", "", 30, True, True)

        assert result["status_code"] == 200
        assert result["body"] == '{"message": "success"}'
        assert result["url"] == "https://example.com"

    @patch("urllib.request.urlopen")
    def test_successful_post_request_with_json(self, mock_urlopen):
        """Test successful POST request with JSON body."""
        mock_response = Mock()
        mock_response.getcode.return_value = 201
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.read.return_value = b'{"id": 123}'
        mock_response.geturl.return_value = "https://example.com/users"
        mock_urlopen.return_value = mock_response

        json_data = '{"name": "test"}'
        result = http_request(
            "POST", "https://example.com/users", "{}", json_data, 30, True, True
        )

        assert result["status_code"] == 201
        assert result["body"] == '{"id": 123}'

    @patch("urllib.request.urlopen")
    def test_custom_headers(self, mock_urlopen):
        """Test request with custom headers."""
        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_response.headers = {}
        mock_response.read.return_value = b"OK"
        mock_response.geturl.return_value = "https://example.com"
        mock_urlopen.return_value = mock_response

        custom_headers = (
            '{"Authorization": "Bearer token123", "X-Custom-Header": "custom-value"}'
        )

        http_request("GET", "https://example.com", custom_headers, "", 30, True, True)

        # The function should parse the JSON headers
        assert mock_urlopen.called

    @patch("urllib.request.urlopen")
    def test_http_error_response(self, mock_urlopen):
        """Test handling of HTTP error responses."""
        from urllib.error import HTTPError

        error_response = HTTPError(
            url="https://example.com",
            code=404,
            msg="Not Found",
            hdrs={"Content-Type": "text/plain"},
            fp=None,
        )
        error_response.read = Mock(return_value=b"Not found")
        mock_urlopen.side_effect = error_response

        result = http_request("GET", "https://example.com", "{}", "", 30, True, True)

        assert result["status_code"] == 404
        assert result["body"] == "Not found"

    @patch("urllib.request.urlopen")
    def test_network_error(self, mock_urlopen):
        """Test handling of network errors."""
        from urllib.error import URLError

        mock_urlopen.side_effect = URLError("Connection failed")

        with pytest.raises(BasicAgentToolsError, match="Network error"):
            http_request("GET", "https://example.com", "{}", "", 30, True, True)

    @patch("urllib.request.urlopen")
    def test_binary_response(self, mock_urlopen):
        """Test handling of binary response data."""
        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_response.headers = {"Content-Type": "image/png"}
        mock_response.read.return_value = b"\x89PNG\r\n\x1a\n"  # PNG header
        mock_response.geturl.return_value = "https://example.com/image.png"
        mock_urlopen.return_value = mock_response

        result = http_request(
            "GET", "https://example.com/image.png", "{}", "", 30, True, True
        )

        assert result["status_code"] == 200
        assert result["body"].startswith("[Binary content - base64]:")

    @patch("urllib.request.urlopen")
    def test_timeout_parameter(self, mock_urlopen):
        """Test that timeout parameter is passed correctly."""
        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_response.headers = {}
        mock_response.read.return_value = b"OK"
        mock_response.geturl.return_value = "https://example.com"
        mock_urlopen.return_value = mock_response

        http_request("GET", "https://example.com", "{}", "", 60, True, True)

        # Check that timeout was passed
        call_kwargs = mock_urlopen.call_args[1]
        assert call_kwargs.get("timeout") == 60
