# Crypto Tools

## Overview
Comprehensive cryptographic utilities, hashing, and encoding tools for AI agents (non-security critical operations).

## Current Status
**✅ FULLY IMPLEMENTED MODULE** - 14 functions available

This module provides essential cryptographic and encoding utilities for AI agents with agent-friendly signatures.

## Current Features
- ✅ **Hashing**: hash_string_md5, hash_string_sha256, hash_string_sha512, hash_file_sha256, verify_hash
- ✅ **Encoding**: base64_encode, base64_decode, url_encode, url_decode, hex_encode, hex_decode
- ✅ **Generation**: generate_uuid4, generate_random_string, generate_random_bytes

## Function Reference

### Hashing Operations

#### hash_string_md5, hash_string_sha256, hash_string_sha512
Generate hash digests for strings using various algorithms.

```python
def hash_string_md5(data: str) -> Dict[str, str]
def hash_string_sha256(data: str) -> Dict[str, str]
def hash_string_sha512(data: str) -> Dict[str, str]
```

**Parameters:**
- `data`: String to hash

**Returns:**
Dictionary with `input_data`, `hash_algorithm`, `hash_value`, `input_length`, and `hash_status`.

**Example:**
```python
result = hash_string_sha256("Hello World")
print(f"SHA-256: {result['hash_value']}")
print(f"Algorithm: {result['hash_algorithm']}")
```

#### hash_file_sha256
Generate SHA-256 hash of a file's contents.

```python
def hash_file_sha256(file_path: str) -> Dict[str, Union[str, int]]
```

**Parameters:**
- `file_path`: Path to file to hash

**Returns:**
Dictionary with `file_path`, `hash_algorithm`, `hash_value`, `file_size_bytes`, and `hash_status`.

**Example:**
```python
result = hash_file_sha256("document.pdf")
print(f"File hash: {result['hash_value']}")
print(f"File size: {result['file_size_bytes']} bytes")
```

#### verify_hash
Verify if a hash value matches the expected value.

```python
def verify_hash(data: str, expected_hash: str, algorithm: str) -> Dict[str, Union[str, bool]]
```

**Parameters:**
- `data`: Data to verify
- `expected_hash`: Expected hash value
- `algorithm`: Hash algorithm ("md5", "sha256", "sha512")

**Returns:**
Dictionary with `verification_result`, `algorithm`, `calculated_hash`, `expected_hash`, and `verification_status`.

### Encoding Operations

#### base64_encode, base64_decode
Encode and decode data using Base64 encoding.

```python
def base64_encode(data: str) -> Dict[str, str]
def base64_decode(encoded_data: str) -> Dict[str, str]
```

**Parameters:**
- `data`: String to encode (for encode)
- `encoded_data`: Base64 string to decode (for decode)

**Returns:**
Dictionary with encoding/decoding results and status information.

**Example:**
```python
encoded = base64_encode("Hello World")
print(f"Encoded: {encoded['encoded_data']}")

decoded = base64_decode(encoded['encoded_data'])
print(f"Decoded: {decoded['decoded_data']}")
```

#### url_encode, url_decode
URL encode and decode strings for safe URL transmission.

```python
def url_encode(data: str) -> Dict[str, str]
def url_decode(encoded_data: str) -> Dict[str, str]
```

#### hex_encode, hex_decode
Convert data to/from hexadecimal representation.

```python
def hex_encode(data: str) -> Dict[str, str]
def hex_decode(encoded_data: str) -> Dict[str, str]
```

### Generation Operations

#### generate_uuid4
Generate a random UUID (version 4).

```python
def generate_uuid4() -> Dict[str, str]
```

**Returns:**
Dictionary with `uuid`, `version`, `variant`, and `generation_status`.

**Example:**
```python
result = generate_uuid4()
print(f"UUID: {result['uuid']}")
print(f"Version: {result['version']}")
```

#### generate_random_string
Generate a random string with specified length and character set.

```python
def generate_random_string(length: int, character_set: str = "alphanumeric") -> Dict[str, Union[str, int]]
```

**Parameters:**
- `length`: Length of string to generate (1-1000)
- `character_set`: Character set ("alphanumeric", "alphabetic", "numeric", "hex")

**Returns:**
Dictionary with `random_string`, `length`, `character_set`, and `generation_status`.

#### generate_random_bytes
Generate random bytes and return as hex string.

```python
def generate_random_bytes(byte_count: int) -> Dict[str, Union[str, int]]
```

**Parameters:**
- `byte_count`: Number of random bytes to generate (1-1000)

**Returns:**
Dictionary with `random_bytes_hex`, `byte_count`, and `generation_status`.

## Agent-Friendly Design Features

### Simplified Type Signatures
All functions use basic Python types (str, int, Dict) to prevent "signature too complex" errors in agent frameworks.

### Security Focus
- **Data integrity focus, not confidentiality** - These tools are for checksums and encoding, not security
- No key management or encryption/decryption
- Standard algorithm implementations only
- Input validation for all operations
- Safe error handling without information leakage

### Comprehensive Error Handling
- Input validation with clear error messages
- Hash verification with detailed results
- Encoding error handling
- Structured error responses

## Common Use Cases

### Data Integrity Verification
```python
# Hash a file and verify later
original_hash = hash_file_sha256("important_file.txt")
print(f"Original hash: {original_hash['hash_value']}")

# Later, verify file hasn't changed
current_hash = hash_file_sha256("important_file.txt")
if current_hash['hash_value'] == original_hash['hash_value']:
    print("File integrity verified")
else:
    print("File has been modified")
```

### Data Encoding for Transmission
```python
# Encode data for safe transmission
sensitive_data = "User: john_doe, Password: secret123"
encoded = base64_encode(sensitive_data)
print(f"Encoded for transmission: {encoded['encoded_data']}")

# URL encode for query parameters
search_query = "name with spaces & special chars"
url_safe = url_encode(search_query)
print(f"URL safe: {url_safe['encoded_data']}")
```

### Unique Identifier Generation
```python
# Generate unique IDs for records
record_id = generate_uuid4()
print(f"Record ID: {record_id['uuid']}")

# Generate random tokens
token = generate_random_string(32, "hex")
print(f"Access token: {token['random_string']}")
```

## Agent Integration

### Google ADK
```python
import basic_open_agent_tools as boat
crypto_tools = boat.load_all_crypto_tools()
agent = Agent(tools=crypto_tools)
```

### Strands Agents
All functions include the `@strands_tool` decorator for native compatibility:
```python
from basic_open_agent_tools.crypto import hash_string_sha256
# Function is automatically compatible with Strands Agents
```

## Important Security Notes

⚠️ **Not for Security Applications**: This module is designed for data integrity and basic encoding needs, not for security-critical applications.

**Excluded Operations:**
- Encryption/Decryption (use specialized libraries)
- Key Generation/Management (security-critical)
- Digital Signatures (use cryptographic libraries)
- Password Hashing (use bcrypt, scrypt, or Argon2)
- Certificate Handling (use specialized libraries)

**Appropriate Use Cases:**
- Data integrity verification
- Basic encoding/decoding operations
- Unique identifier generation
- Checksum validation
- Non-security data transformation

## Dependencies
All cryptographic functions use Python standard library modules (hashlib, base64, urllib, uuid, secrets) - no additional dependencies required.

## Testing
Comprehensive test coverage includes hash accuracy verification, encoding/decoding round-trip testing, UUID format validation, and cross-platform compatibility testing.