"""Tests for DNS utilities."""

import socket
from unittest.mock import MagicMock, patch

import pytest

from basic_open_agent_tools.exceptions import BasicAgentToolsError
from basic_open_agent_tools.network.dns import (
    check_port_open,
    resolve_hostname,
    reverse_dns_lookup,
)


class TestResolveHostname:
    """Test cases for resolve_hostname function."""

    def test_invalid_hostname_type(self):
        """Test with invalid hostname type."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            resolve_hostname(123)
        assert "Hostname must be a non-empty string" in str(exc_info.value)

    def test_empty_hostname(self):
        """Test with empty hostname."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            resolve_hostname("")
        assert "Hostname must be a non-empty string" in str(exc_info.value)

    @patch("socket.getaddrinfo")
    def test_successful_resolution(self, mock_getaddrinfo):
        """Test successful hostname resolution."""
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, None, None, None, ("192.168.1.1", 80)),
            (socket.AF_INET, None, None, None, ("192.168.1.2", 80)),
            (socket.AF_INET6, None, None, None, ("2001:db8::1", 80)),
        ]

        result = resolve_hostname("example.com")

        assert result["hostname"] == "example.com"
        assert "192.168.1.1" in result["ipv4_addresses"]
        assert "192.168.1.2" in result["ipv4_addresses"]
        assert "2001:db8::1" in result["ipv6_addresses"]
        assert result["total_addresses"] == 3
        assert result["resolution_status"] == "success"

    @patch("socket.getaddrinfo")
    def test_dns_resolution_failure(self, mock_getaddrinfo):
        """Test DNS resolution failure."""
        mock_getaddrinfo.side_effect = socket.gaierror("Name resolution failed")

        with pytest.raises(BasicAgentToolsError) as exc_info:
            resolve_hostname("nonexistent.example")
        assert "Failed to resolve hostname" in str(exc_info.value)

    @patch("socket.getaddrinfo")
    def test_ipv4_only_resolution(self, mock_getaddrinfo):
        """Test resolution with IPv4 addresses only."""
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, None, None, None, ("192.168.1.1", 80)),
            (socket.AF_INET, None, None, None, ("192.168.1.1", 80)),  # Duplicate
        ]

        result = resolve_hostname("ipv4only.example")

        assert len(result["ipv4_addresses"]) == 1  # Duplicates removed
        assert len(result["ipv6_addresses"]) == 0
        assert result["total_addresses"] == 1


class TestReverseDnsLookup:
    """Test cases for reverse_dns_lookup function."""

    def test_invalid_ip_type(self):
        """Test with invalid IP address type."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            reverse_dns_lookup(123)
        assert "IP address must be a non-empty string" in str(exc_info.value)

    def test_empty_ip(self):
        """Test with empty IP address."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            reverse_dns_lookup("")
        assert "IP address must be a non-empty string" in str(exc_info.value)

    def test_invalid_ip_format(self):
        """Test with invalid IP address format."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            reverse_dns_lookup("not.an.ip.address")
        assert "Invalid IP address format" in str(exc_info.value)

    @patch("socket.inet_pton")
    @patch("socket.gethostbyaddr")
    def test_successful_ipv4_lookup(self, mock_gethostbyaddr, mock_inet_pton):
        """Test successful IPv4 reverse lookup."""
        # Mock IPv4 validation to succeed
        mock_inet_pton.side_effect = [
            None,
            OSError(),
        ]  # First call succeeds, second fails

        mock_gethostbyaddr.return_value = (
            "example.com",
            ["alias.example.com"],
            ["192.168.1.1"],
        )

        result = reverse_dns_lookup("192.168.1.1")

        assert result["ip_address"] == "192.168.1.1"
        assert result["ip_family"] == "IPv4"
        assert result["hostname"] == "example.com"
        assert result["lookup_successful"] is True
        assert result["lookup_status"] == "success"

    @patch("socket.inet_pton")
    @patch("socket.gethostbyaddr")
    def test_successful_ipv6_lookup(self, mock_gethostbyaddr, mock_inet_pton):
        """Test successful IPv6 reverse lookup."""
        # Mock IPv4 validation to fail, IPv6 to succeed
        mock_inet_pton.side_effect = [OSError(), None]

        mock_gethostbyaddr.return_value = ("ipv6.example.com", [], ["2001:db8::1"])

        result = reverse_dns_lookup("2001:db8::1")

        assert result["ip_address"] == "2001:db8::1"
        assert result["ip_family"] == "IPv6"
        assert result["hostname"] == "ipv6.example.com"
        assert result["lookup_successful"] is True

    @patch("socket.inet_pton")
    @patch("socket.gethostbyaddr")
    def test_no_reverse_dns_record(self, mock_gethostbyaddr, mock_inet_pton):
        """Test IP with no reverse DNS record."""
        mock_inet_pton.side_effect = [None, OSError()]  # IPv4
        mock_gethostbyaddr.side_effect = socket.herror("No reverse DNS record")

        result = reverse_dns_lookup("192.168.1.100")

        assert result["lookup_successful"] is False
        assert result["lookup_status"] == "no_reverse_dns_record"
        assert result["hostname"] == ""


class TestCheckPortOpen:
    """Test cases for check_port_open function."""

    def test_invalid_host_type(self):
        """Test with invalid host type."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            check_port_open(123, 80, 5)  # type: ignore[arg-type]
        assert "Host must be a non-empty string" in str(exc_info.value)

    def test_invalid_port_range(self):
        """Test with invalid port number."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            check_port_open("example.com", 70000, 5)
        assert "Port must be an integer between 1 and 65535" in str(exc_info.value)

    def test_invalid_timeout_range(self):
        """Test with invalid timeout value."""
        with pytest.raises(BasicAgentToolsError) as exc_info:
            check_port_open("example.com", 80, 50)
        assert "Timeout must be an integer between 1 and 30 seconds" in str(
            exc_info.value
        )

    @patch("socket.socket")
    @patch("time.time")
    def test_port_open_success(self, mock_time, mock_socket_class):
        """Test successful port connection."""
        # Mock timing
        mock_time.side_effect = [1000.0, 1000.05]  # 50ms response time

        # Mock socket
        mock_socket = MagicMock()
        mock_socket.connect_ex.return_value = 0  # Success
        mock_socket_class.return_value = mock_socket

        result = check_port_open("example.com", 80, 10)

        assert result["host"] == "example.com"
        assert result["port"] == 80
        assert result["is_open"] is True
        assert result["response_time_ms"] == 50.0
        assert result["check_status"] == "success"

    @patch("socket.socket")
    @patch("time.time")
    def test_port_closed(self, mock_time, mock_socket_class):
        """Test connection to closed port."""
        mock_time.side_effect = [1000.0, 1000.1]

        mock_socket = MagicMock()
        mock_socket.connect_ex.return_value = 1  # Connection refused
        mock_socket_class.return_value = mock_socket

        result = check_port_open("example.com", 81, 5)

        assert result["is_open"] is False
        assert result["check_status"] == "closed_or_filtered"

    @patch("socket.socket")
    @patch("time.time")
    def test_connection_timeout(self, mock_time, mock_socket_class):
        """Test connection timeout."""
        mock_time.side_effect = [1000.0, 1005.0]  # 5 second timeout

        mock_socket = MagicMock()
        mock_socket.connect_ex.side_effect = socket.timeout()
        mock_socket_class.return_value = mock_socket

        result = check_port_open("timeout.example", 80, 5)

        assert result["is_open"] is False
        assert result["check_status"] == "timeout"
        assert result["response_time_ms"] == 5000.0
