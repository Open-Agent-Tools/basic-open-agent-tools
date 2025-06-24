# Network Tools TODO

## Overview
Local network utilities and validation tools (no HTTP/API operations).

## Planned Modules

### High Priority
- [ ] **Validation** (`validation.py`)
  - URL format validation
  - IP address validation (IPv4/IPv6)
  - Port number validation
  - Domain name validation
  - Email format validation
  - Network address validation

- [ ] **Local Utilities** (`local.py`)
  - Local network interface enumeration
  - Available port checking
  - Local IP address discovery
  - Network connectivity testing (ping-like)
  - Local hostname resolution
  - MAC address utilities

### Medium Priority
- [ ] **Discovery** (`discovery.py`)
  - Local service discovery
  - Network scanning (local subnet only)
  - Port scanning (local only)
  - Device discovery on local network
  - Network topology detection

- [ ] **Address Utilities** (`addresses.py`)
  - IP address manipulation
  - Subnet calculations
  - CIDR notation handling
  - Network range operations
  - IP address sorting and comparison

### Low Priority
- [ ] **Protocol Utilities** (`protocols.py`)
  - Basic protocol detection
  - Port-to-service mapping
  - Network protocol validation
  - Common port definitions

## Design Considerations
- No external HTTP/API calls (follows project principle)
- Focus on local network operations only
- Cross-platform network interface handling
- Security considerations (no unauthorized scanning)
- IPv6 compatibility
- Proper error handling for network operations
- Timeout handling for network checks
- Permission awareness for network operations