# Cryptographic Tools TODO

## Overview
Hashing, encoding, and basic cryptographic utilities (no encryption/decryption).

## Planned Modules

### High Priority
- [ ] **Hashing** (`hashing.py`)
  - File content hashing (MD5, SHA1, SHA256, SHA512)
  - String hashing utilities
  - Hash verification and comparison
  - Checksum generation and validation
  - Hash-based file integrity checking
  - Bulk file hashing operations

- [ ] **Encoding** (`encoding.py`)
  - Base64 encoding/decoding
  - URL-safe base64 operations
  - Hexadecimal encoding/decoding
  - URL encoding/decoding
  - HTML entity encoding/decoding
  - Percent encoding utilities

### Medium Priority
- [ ] **Utilities** (`utilities.py`)
  - Random string generation
  - UUID generation and validation
  - Token generation (non-cryptographic)
  - Data fingerprinting
  - Simple obfuscation (not security)

- [ ] **Validation** (`validation.py`)
  - Hash format validation
  - Checksum verification
  - Integrity checking utilities
  - Format validation for encoded data

### Low Priority
- [ ] **File Integrity** (`integrity.py`)
  - File signature verification
  - Batch integrity checking
  - Integrity report generation
  - File corruption detection

## Important Notes
- **NO ENCRYPTION/DECRYPTION** - This violates the project's security principles
- Focus on data integrity and encoding only
- Use only well-established, standard algorithms
- Provide secure defaults
- Clear documentation about security limitations

## Design Considerations
- Use standard library implementations where possible
- Clear separation between secure and non-secure operations
- Consistent error handling
- Performance considerations for large files
- Cross-platform compatibility
- Clear documentation of security properties
- Warning messages for deprecated hash algorithms