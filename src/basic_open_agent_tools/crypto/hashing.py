"""Hashing and checksum utilities."""

import hashlib
import os
from typing import Any, Callable, Union

try:
    from strands import tool as strands_tool
except ImportError:

    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        """Fallback decorator when strands is not available."""
        return func


from ..exceptions import BasicAgentToolsError


@strands_tool
def hash_md5(data: str) -> dict[str, str]:
    """
    Generate MD5 hash of a string.

    Args:
        data: String to hash

    Returns:
        Dictionary with hash information

    Raises:
        BasicAgentToolsError: If data is invalid
    """
    print(f"[CRYPTO] Hashing {len(data)} chars with MD5")

    if not isinstance(data, str):
        raise BasicAgentToolsError("Data must be a string")

    try:
        hash_obj = hashlib.md5(data.encode("utf-8"))
        hex_hash = hash_obj.hexdigest()

        result = {
            "algorithm": "md5",
            "input_data": data,
            "input_length": len(data),
            "hash_hex": hex_hash,
            "hash_length": len(hex_hash),
        }

        print(f"[CRYPTO] MD5 hash generated: {hex_hash[:16]}...")
        return result

    except Exception as e:
        print(f"[CRYPTO] MD5 hash failed: {e}")
        raise BasicAgentToolsError(f"Failed to generate MD5 hash: {str(e)}")


@strands_tool
def hash_sha256(data: str) -> dict[str, str]:
    """
    Generate SHA-256 hash of a string.

    Args:
        data: String to hash

    Returns:
        Dictionary with hash information

    Raises:
        BasicAgentToolsError: If data is invalid
    """
    print(f"[CRYPTO] Hashing {len(data)} chars with SHA-256")

    if not isinstance(data, str):
        raise BasicAgentToolsError("Data must be a string")

    try:
        hash_obj = hashlib.sha256(data.encode("utf-8"))
        hex_hash = hash_obj.hexdigest()

        result = {
            "algorithm": "sha256",
            "input_data": data,
            "input_length": len(data),
            "hash_hex": hex_hash,
            "hash_length": len(hex_hash),
        }

        print(f"[CRYPTO] SHA-256 hash generated: {hex_hash[:16]}...")
        return result

    except Exception as e:
        print(f"[CRYPTO] SHA-256 hash failed: {e}")
        raise BasicAgentToolsError(f"Failed to generate SHA-256 hash: {str(e)}")


@strands_tool
def hash_sha512(data: str) -> dict[str, str]:
    """
    Generate SHA-512 hash of a string.

    Args:
        data: String to hash

    Returns:
        Dictionary with hash information

    Raises:
        BasicAgentToolsError: If data is invalid
    """
    if not isinstance(data, str):
        raise BasicAgentToolsError("Data must be a string")

    try:
        hash_obj = hashlib.sha512(data.encode("utf-8"))
        hex_hash = hash_obj.hexdigest()

        return {
            "algorithm": "sha512",
            "input_data": data,
            "input_length": len(data),
            "hash_hex": hex_hash,
            "hash_length": len(hex_hash),
        }

    except Exception as e:
        raise BasicAgentToolsError(f"Failed to generate SHA-512 hash: {str(e)}")


@strands_tool
def hash_file(file_path: str, algorithm: str = "sha256") -> dict[str, Union[str, int]]:
    """
    Generate hash of a file's contents.

    Args:
        file_path: Path to the file to hash
        algorithm: Hash algorithm to use (md5, sha256, sha512)

    Returns:
        Dictionary with file hash information

    Raises:
        BasicAgentToolsError: If file path is invalid or algorithm is unsupported
    """
    print(f"[CRYPTO] Hashing file: {file_path} with {algorithm}")

    if not isinstance(file_path, str) or not file_path.strip():
        raise BasicAgentToolsError("File path must be a non-empty string")

    if not isinstance(algorithm, str) or algorithm.lower() not in [
        "md5",
        "sha256",
        "sha512",
    ]:
        raise BasicAgentToolsError("Algorithm must be one of: md5, sha256, sha512")

    algorithm = algorithm.lower()
    file_path = file_path.strip()

    try:
        # Check if file exists and is readable
        if not os.path.exists(file_path):
            raise BasicAgentToolsError(f"File not found: {file_path}")

        if not os.path.isfile(file_path):
            raise BasicAgentToolsError(f"Path is not a file: {file_path}")

        # Get file size
        file_size = os.path.getsize(file_path)

        # Create hash object
        if algorithm == "md5":
            hash_obj = hashlib.md5()
        elif algorithm == "sha256":
            hash_obj = hashlib.sha256()
        elif algorithm == "sha512":
            hash_obj = hashlib.sha512()

        # Read and hash file in chunks to handle large files
        chunk_size = 64 * 1024  # 64KB chunks

        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                hash_obj.update(chunk)

        hex_hash = hash_obj.hexdigest()

        result = {
            "algorithm": algorithm,
            "file_path": file_path,
            "file_size_bytes": file_size,
            "hash_hex": hex_hash,
            "hash_length": len(hex_hash),
        }

        print(f"[CRYPTO] File hash ({file_size} bytes): {hex_hash[:16]}...")
        return result

    except FileNotFoundError:
        raise BasicAgentToolsError(f"File not found: {file_path}")
    except PermissionError:
        raise BasicAgentToolsError(f"Permission denied accessing file: {file_path}")
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to hash file {file_path}: {str(e)}")


@strands_tool
def verify_checksum(
    data: str, expected_hash: str, algorithm: str = "sha256"
) -> dict[str, Union[str, bool]]:
    """
    Verify data against an expected hash.

    Args:
        data: Data to verify
        expected_hash: Expected hash value (hex string)
        algorithm: Hash algorithm used (md5, sha256, sha512)

    Returns:
        Dictionary with verification results

    Raises:
        BasicAgentToolsError: If parameters are invalid
    """
    if not isinstance(data, str):
        raise BasicAgentToolsError("Data must be a string")

    if not isinstance(expected_hash, str) or not expected_hash.strip():
        raise BasicAgentToolsError("Expected hash must be a non-empty string")

    if not isinstance(algorithm, str) or algorithm.lower() not in [
        "md5",
        "sha256",
        "sha512",
    ]:
        raise BasicAgentToolsError("Algorithm must be one of: md5, sha256, sha512")

    algorithm = algorithm.lower()
    expected_hash = expected_hash.strip().lower()

    try:
        # Validate expected hash format (should be hex)
        int(expected_hash, 16)  # This will raise ValueError if not valid hex

        # Generate hash of the data
        if algorithm == "md5":
            hash_result = hash_md5(data)
        elif algorithm == "sha256":
            hash_result = hash_sha256(data)
        elif algorithm == "sha512":
            hash_result = hash_sha512(data)

        calculated_hash = hash_result["hash_hex"].lower()
        matches = calculated_hash == expected_hash

        return {
            "algorithm": algorithm,
            "data_length": len(data),
            "expected_hash": expected_hash,
            "calculated_hash": calculated_hash,
            "matches": matches,
            "verification_result": "valid" if matches else "invalid",
        }

    except ValueError:
        raise BasicAgentToolsError("Expected hash must be a valid hexadecimal string")
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to verify checksum: {str(e)}")
