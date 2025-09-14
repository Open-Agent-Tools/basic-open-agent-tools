"""Tests for HTTP client tools."""

import json
import pytest
from unittest.mock import patch, Mock, mock_open

from basic_open_agent_tools.network.http_client import (
    http_request,
    http_get,
    http_post,
)
from basic_open_agent_tools.exceptions import BasicAgentToolsError


class TestHttpRequest:
    """Test the http_request function."""

    def test_invalid_method(self):
        """Test error handling for invalid method."""
        with pytest.raises(BasicAgentToolsError, match="Method must be a non-empty string"):
            http_request("", "https://example.com")

        with pytest.raises(BasicAgentToolsError, match="Method must be a non-empty string"):
            http_request(None, "https://example.com")

    def test_invalid_url(self):
        """Test error handling for invalid URL."""
        with pytest.raises(BasicAgentToolsError, match="URL must be a non-empty string"):
            http_request("GET", "")

        with pytest.raises(BasicAgentToolsError, match="URL must start with http"):
            http_request("GET", "ftp://example.com")

    def test_invalid_headers(self):
        """Test error handling for invalid headers."""
        with pytest.raises(BasicAgentToolsError, match="Headers must be a dictionary"):
            http_request("GET", "https://example.com", headers="invalid")

    def test_invalid_body(self):
        """Test error handling for invalid body."""
        with pytest.raises(BasicAgentToolsError, match="Body must be a string"):
            http_request("POST", "https://example.com", body=123)

    @patch('urllib.request.urlopen')
    def test_successful_get_request(self, mock_urlopen):
        """Test successful GET request."""
        # Mock response
        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.read.return_value = b'{"message": "success"}'
        mock_response.geturl.return_value = "https://example.com"
        mock_urlopen.return_value = mock_response

        result = http_request("GET", "https://example.com")

        assert result["status_code"] == 200
        assert '"Content-Type": "application/json"' in result["headers"]
        assert result["body"] == '{"message": "success"}'
        assert result["url"] == "https://example.com"

    @patch('urllib.request.urlopen')
    def test_successful_post_request_with_json(self, mock_urlopen):
        """Test successful POST request with JSON body."""
        mock_response = Mock()
        mock_response.getcode.return_value = 201
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.read.return_value = b'{"id": 123}'
        mock_response.geturl.return_value = "https://example.com/users"
        mock_urlopen.return_value = mock_response

        json_data = '{"name": "test"}'
        result = http_request("POST", "https://example.com/users", body=json_data)

        assert result["status_code"] == 201
        assert result["body"] == '{"id": 123}'

        # Check that the request was made correctly
        call_args = mock_urlopen.call_args[0]
        request = call_args[0]
        assert request.data == json_data.encode('utf-8')
        assert 'application/json' in request.headers.get('Content-type', '')

    @patch('urllib.request.urlopen')
    def test_custom_headers(self, mock_urlopen):
        """Test request with custom headers."""
        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_response.headers = {}
        mock_response.read.return_value = b'OK'
        mock_response.geturl.return_value = "https://example.com"
        mock_urlopen.return_value = mock_response

        custom_headers = {
            "Authorization": "Bearer token123",
            "X-Custom-Header": "custom-value"
        }

        result = http_request("GET", "https://example.com", headers=custom_headers)

        # Check that the request was made with custom headers
        call_args = mock_urlopen.call_args[0]
        request = call_args[0]
        assert request.headers.get('Authorization') == 'Bearer token123'
        assert request.headers.get('X-custom-header') == 'custom-value'

    @patch('urllib.request.urlopen')
    def test_http_error_response(self, mock_urlopen):
        """Test handling of HTTP error responses."""
        from urllib.error import HTTPError

        error_response = HTTPError(
            url="https://example.com",
            code=404,
            msg="Not Found",
            hdrs={"Content-Type": "text/plain"},
            fp=None
        )
        error_response.read = Mock(return_value=b'Not found')
        mock_urlopen.side_effect = error_response

        result = http_request("GET", "https://example.com")

        assert result["status_code"] == 404
        assert result["body"] == "Not found"
        assert '"Content-Type": "text/plain"' in result["headers"]

    @patch('urllib.request.urlopen')
    def test_network_error(self, mock_urlopen):
        """Test handling of network errors."""
        from urllib.error import URLError

        mock_urlopen.side_effect = URLError("Connection failed")

        with pytest.raises(BasicAgentToolsError, match="Network error"):
            http_request("GET", "https://example.com")

    @patch('urllib.request.urlopen')
    def test_binary_response(self, mock_urlopen):
        """Test handling of binary response data."""
        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_response.headers = {"Content-Type": "image/png"}
        mock_response.read.return_value = b'\x89PNG\r\n\x1a\n'  # PNG header
        mock_response.geturl.return_value = "https://example.com/image.png"
        mock_urlopen.return_value = mock_response

        result = http_request("GET", "https://example.com/image.png")

        assert result["status_code"] == 200
        assert result["body"].startswith("[Binary content - base64]:")

    @patch('urllib.request.urlopen')
    def test_timeout_parameter(self, mock_urlopen):
        """Test that timeout parameter is passed correctly."""
        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_response.headers = {}
        mock_response.read.return_value = b'OK'
        mock_response.geturl.return_value = "https://example.com"
        mock_urlopen.return_value = mock_response

        http_request("GET", "https://example.com", timeout=60)

        # Check that timeout was passed
        call_kwargs = mock_urlopen.call_args[1]
        assert call_kwargs.get('timeout') == 60


class TestHttpGet:
    """Test the http_get convenience function."""

    @patch('basic_open_agent_tools.network.http_client.http_request')
    def test_http_get_calls_http_request(self, mock_http_request):
        """Test that http_get calls http_request with correct parameters."""
        mock_http_request.return_value = {"status_code": 200}

        http_get("https://example.com", headers={"Accept": "application/json"}, timeout=30)

        mock_http_request.assert_called_once_with(
            "GET",
            "https://example.com",
            headers={"Accept": "application/json"},
            timeout=30
        )


class TestHttpPost:
    """Test the http_post convenience function."""

    @patch('basic_open_agent_tools.network.http_client.http_request')
    def test_http_post_calls_http_request(self, mock_http_request):
        """Test that http_post calls http_request with correct parameters."""
        mock_http_request.return_value = {"status_code": 201}

        http_post(
            "https://example.com",
            body='{"name": "test"}',
            headers={"Content-Type": "application/json"},
            timeout=45
        )

        mock_http_request.assert_called_once_with(
            "POST",
            "https://example.com",
            headers={"Content-Type": "application/json"},
            body='{"name": "test"}',
            timeout=45
        )