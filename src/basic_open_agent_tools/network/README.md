# Network Tools

## Overview
Complete network utilities for AI agents including HTTP client, DNS resolution, and connectivity testing with simplified type signatures.

## Current Status
**✅ FULLY IMPLEMENTED MODULE** - 4 functions available

This module provides comprehensive network functionality for AI agents with agent-friendly signatures.

## Current Features
- ✅ **http_request**: Make HTTP requests with comprehensive error handling
- ✅ **resolve_hostname**: Resolve hostnames to IP addresses with IPv4/IPv6 support
- ✅ **reverse_dns_lookup**: Perform reverse DNS lookups for IP addresses
- ✅ **check_port_open**: Check if ports are open on remote hosts with timeout controls

## Function Reference

### HTTP Client Operations

#### http_request
Make HTTP requests with comprehensive error handling and security controls.

```python
def http_request(
    method: str,
    url: str,
    headers: Dict[str, str] = None,
    body: str = None,
    timeout: int = 30,
    follow_redirects: bool = True,
    verify_ssl: bool = True
) -> Dict[str, Union[str, int]]
```

**Parameters:**
- `method`: HTTP method (GET, POST, PUT, DELETE, etc.)
- `url`: Target URL for the request
- `headers`: Optional HTTP headers dictionary
- `body`: Optional request body content
- `timeout`: Request timeout in seconds (1-300)
- `follow_redirects`: Whether to follow HTTP redirects
- `verify_ssl`: Whether to verify SSL certificates

**Returns:**
Dictionary with `status_code`, `headers`, `body`, `url`, `is_success`, `content_type`, and `response_size_bytes`.

**Example:**
```python
result = http_request("GET", "https://api.github.com/users/octocat")
print(f"Status: {result['status_code']}")
print(f"Response: {result['body']}")
```

### DNS Operations

#### resolve_hostname
Resolve a hostname to IP addresses with support for both IPv4 and IPv6.

```python
def resolve_hostname(hostname: str) -> Dict[str, Union[str, List[str]]]
```

**Parameters:**
- `hostname`: Hostname to resolve (e.g., "github.com")

**Returns:**
Dictionary with `hostname`, `ipv4_addresses`, `ipv6_addresses`, `total_addresses`, and `resolution_status`.

**Example:**
```python
result = resolve_hostname("github.com")
print(f"IPv4 addresses: {result['ipv4_addresses']}")
print(f"IPv6 addresses: {result['ipv6_addresses']}")
```

#### reverse_dns_lookup
Perform reverse DNS lookup for an IP address to get the hostname.

```python
def reverse_dns_lookup(ip_address: str) -> Dict[str, Union[str, bool]]
```

**Parameters:**
- `ip_address`: IP address to lookup (IPv4 or IPv6)

**Returns:**
Dictionary with `ip_address`, `ip_family`, `hostname`, `lookup_successful`, and `lookup_status`.

**Example:**
```python
result = reverse_dns_lookup("8.8.8.8")
print(f"Hostname: {result['hostname']}")
print(f"Successful: {result['lookup_successful']}")
```

### Connectivity Testing

#### check_port_open
Check if a specific port is open on a remote host with timeout control.

```python
def check_port_open(
    host: str,
    port: int,
    timeout: int = 5
) -> Dict[str, Union[str, int, bool, float]]
```

**Parameters:**
- `host`: Hostname or IP address to check
- `port`: Port number to check (1-65535)
- `timeout`: Connection timeout in seconds (1-30)

**Returns:**
Dictionary with `host`, `port`, `is_open`, `response_time_ms`, `timeout_seconds`, and `check_status`.

**Example:**
```python
result = check_port_open("google.com", 443, 5)
print(f"Port 443 open: {result['is_open']}")
print(f"Response time: {result['response_time_ms']}ms")
```

## Agent-Friendly Design Features

### Simplified Type Signatures
All functions use basic Python types (str, int, bool, Dict, List) to prevent "signature too complex" errors in agent frameworks.

### Comprehensive Error Handling
- Input validation with clear error messages
- Network timeout handling
- SSL/TLS error handling
- DNS resolution error handling
- Structured error responses

### Security Features
- SSL certificate verification (configurable)
- Request timeout controls
- Input sanitization and validation
- No credential storage or management
- Safe error messages without information disclosure

### Cross-Platform Compatibility
- Windows, macOS, and Linux support
- IPv4 and IPv6 support
- Platform-specific DNS resolution
- Consistent behavior across operating systems

## Common Use Cases

### API Integration
```python
# Make API calls with error handling
api_response = http_request(
    "GET",
    "https://api.example.com/data",
    headers={"Authorization": "Bearer token"},
    timeout=10
)

if api_response['is_success']:
    data = api_response['body']
else:
    print(f"API call failed: {api_response['status_code']}")
```

### Network Diagnostics
```python
# Check if a service is accessible
dns_result = resolve_hostname("service.example.com")
if dns_result['total_addresses'] > 0:
    port_result = check_port_open("service.example.com", 443)
    if port_result['is_open']:
        print("Service is accessible")
    else:
        print("Service port is blocked")
else:
    print("DNS resolution failed")
```

### Reverse Engineering
```python
# Identify servers from IP addresses
ip_addresses = ["192.168.1.1", "8.8.8.8", "1.1.1.1"]
for ip in ip_addresses:
    result = reverse_dns_lookup(ip)
    if result['lookup_successful']:
        print(f"{ip} -> {result['hostname']}")
    else:
        print(f"{ip} -> No reverse DNS record")
```

## Agent Integration

### Google ADK
```python
from google.adk.agents import Agent
import basic_open_agent_tools as boat

network_tools = boat.load_all_network_tools()
agent = Agent(tools=network_tools)
```

### LangChain
```python
from langchain.tools import StructuredTool
from basic_open_agent_tools.network import resolve_hostname

dns_tool = StructuredTool.from_function(
    func=resolve_hostname,
    name="resolve_hostname",
    description="Resolve hostnames to IP addresses"
)
```

### Strands Agents
All functions include the `@strands_tool` decorator for native compatibility:
```python
from basic_open_agent_tools.network import resolve_hostname
# Function is automatically compatible with Strands Agents
```

## Security Considerations

### Safe Operations Only
- No network scanning capabilities (ethical concerns)
- No port discovery or enumeration
- Individual host/port checks only
- No credential handling or storage

### Input Validation
- Hostname format validation
- IP address format validation
- Port number range validation
- URL scheme validation
- Timeout bounds checking

### Error Handling
- Network timeouts handled gracefully
- DNS resolution failures handled safely
- SSL/TLS errors reported without sensitive details
- Connection failures logged appropriately

## Performance Notes

### DNS Caching
- System DNS cache is used automatically
- No custom caching implemented
- DNS resolution performance depends on system configuration

### Connection Timeouts
- Default timeouts are conservative (5-30 seconds)
- Configurable per operation
- Prevents hanging operations in agent workflows

### Concurrent Operations
- Functions are thread-safe
- No shared state between calls
- Suitable for concurrent agent operations

## Error Reference

### Common Error Types
- `BasicAgentToolsError`: Input validation failures
- `socket.gaierror`: DNS resolution failures
- `socket.timeout`: Network timeout errors
- `requests.exceptions.*`: HTTP request failures

### Error Messages
All errors include descriptive messages suitable for agent debugging:
- "Invalid hostname format: example"
- "DNS resolution failed for hostname"
- "Connection timeout after 5 seconds"
- "Port number must be between 1 and 65535"

## Testing
Comprehensive test coverage includes:
- DNS resolution testing with mock responses
- HTTP client testing with mock servers
- Port connectivity testing with mock sockets
- Error condition testing
- Cross-platform compatibility testing

**Test Coverage**: Individual function tests + integration tests + agent framework compatibility tests.