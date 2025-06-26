"""Binary data processing tools for AI agents.

This module provides functions for handling binary data, including reading and
writing binary files, encoding and decoding binary data, and extracting metadata
from binary files.
"""

import base64
import binascii
import imghdr
import mimetypes
import os
import struct
from typing import Any, Dict, Optional

from ..exceptions import DataError


def read_binary_file(file_path: str, max_size: Optional[int] = None) -> bytes:
    """Read binary data from a file.

    Args:
        file_path: Path to the binary file
        max_size: Maximum file size in bytes to read (None for no limit)

    Returns:
        Binary data as bytes

    Raises:
        FileNotFoundError: If the file does not exist
        DataError: If the file exceeds the maximum size or cannot be read

    Example:
        >>> data = read_binary_file("image.jpg")
        >>> isinstance(data, bytes)
        True
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Check file size if max_size is specified
    if max_size is not None:
        file_size = os.path.getsize(file_path)
        if file_size > max_size:
            raise DataError(
                f"File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)"
            )

    try:
        with open(file_path, "rb") as file:
            return file.read()
    except Exception as e:
        raise DataError(f"Failed to read binary file: {str(e)}")


def write_binary_file(data: bytes, file_path: str) -> None:
    """Write binary data to a file.

    Args:
        data: Binary data to write
        file_path: Path where the file will be written

    Raises:
        TypeError: If data is not bytes
        DataError: If the file cannot be written

    Example:
        >>> data = b"Binary data"
        >>> write_binary_file(data, "output.bin")
    """
    if not isinstance(data, bytes):
        raise TypeError("Data must be bytes")

    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

        with open(file_path, "wb") as file:
            file.write(data)
    except Exception as e:
        raise DataError(f"Failed to write binary file: {str(e)}")


def encode_binary_data(data: bytes, encoding: str = "base64") -> str:
    """Encode binary data to a string representation.

    Args:
        data: Binary data to encode
        encoding: Encoding method ("base64", "hex")

    Returns:
        Encoded data as a string

    Raises:
        TypeError: If data is not bytes
        ValueError: If the encoding method is not supported

    Example:
        >>> data = b"Binary data"
        >>> encoded = encode_binary_data(data, encoding="base64")
        >>> isinstance(encoded, str)
        True
    """
    if not isinstance(data, bytes):
        raise TypeError("Data must be bytes")

    if encoding == "base64":
        return base64.b64encode(data).decode("ascii")
    elif encoding == "hex":
        return data.hex()
    else:
        raise ValueError(f"Unsupported encoding method: {encoding}")


def decode_binary_data(encoded_data: str, encoding: str = "base64") -> bytes:
    """Decode a string representation back to binary data.

    Args:
        encoded_data: Encoded data as a string
        encoding: Encoding method ("base64", "hex")

    Returns:
        Decoded binary data

    Raises:
        TypeError: If encoded_data is not a string
        ValueError: If the encoding method is not supported or the data is invalid

    Example:
        >>> encoded = "QmluYXJ5IGRhdGE="  # "Binary data" in base64
        >>> decoded = decode_binary_data(encoded, encoding="base64")
        >>> decoded
        b'Binary data'
    """
    if not isinstance(encoded_data, str):
        raise TypeError("Encoded data must be a string")

    try:
        if encoding == "base64":
            return base64.b64decode(encoded_data)
        elif encoding == "hex":
            return bytes.fromhex(encoded_data)
        else:
            raise ValueError(f"Unsupported encoding method: {encoding}")
    except (binascii.Error, ValueError) as e:
        raise ValueError(f"Invalid {encoding} data: {str(e)}")


def validate_binary_format(data: Any, expected_format: str) -> bool:
    """Validate that binary data matches an expected format.

    Args:
        data: Binary data to validate
        expected_format: Expected format ("png", "jpeg", "gif", "pdf", etc.)

    Returns:
        True if the data matches the expected format, False otherwise

    Example:
        >>> with open("image.png", "rb") as f:
        ...     data = f.read()
        >>> validate_binary_format(data, "png")
        True
    """
    if not isinstance(data, bytes):
        return False

    # For image formats, use imghdr
    if expected_format.lower() in ("png", "jpeg", "jpg", "gif", "bmp", "tiff"):
        detected = imghdr.what(None, data)
        if detected == "jpeg" and expected_format.lower() in ("jpeg", "jpg"):
            return True
        return detected == expected_format.lower()

    # Check file signatures (magic numbers)
    signatures = {
        "pdf": b"%PDF",
        "zip": b"PK\x03\x04",
        "gzip": b"\x1f\x8b",
        "rar": b"Rar!\x1a\x07",
        "7z": b"7z\xbc\xaf\x27\x1c",
        "tar": b"ustar" in data[257:262] if len(data) >= 262 else False,
        "mp3": b"ID3" == data[:3] or b"\xff\xfb" == data[:2],
        "mp4": b"ftyp" in data[4:8] if len(data) >= 8 else False,
        "avi": b"RIFF" == data[:4] and b"AVI " == data[8:12]
        if len(data) >= 12
        else False,
        "wav": b"RIFF" == data[:4] and b"WAVE" == data[8:12]
        if len(data) >= 12
        else False,
    }

    if expected_format.lower() in signatures:
        signature = signatures[expected_format.lower()]
        if isinstance(signature, bool):
            return signature
        elif isinstance(signature, bytes):
            return signature == data[: len(signature)]
        return False

    # If no specific validation is available, return False
    return False


def extract_binary_metadata(file_path: str) -> Dict[str, Any]:
    """Extract metadata from a binary file.

    Args:
        file_path: Path to the binary file

    Returns:
        Dictionary containing metadata (size, type, etc.)

    Raises:
        FileNotFoundError: If the file does not exist
        DataError: If metadata cannot be extracted

    Example:
        >>> metadata = extract_binary_metadata("image.jpg")
        >>> "size" in metadata
        True
        >>> "mime_type" in metadata
        True
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        # Basic file metadata
        stat_info = os.stat(file_path)

        metadata: Dict[str, Any] = {
            "size": stat_info.st_size,
            "created": stat_info.st_ctime,
            "modified": stat_info.st_mtime,
            "accessed": stat_info.st_atime,
        }

        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            metadata["mime_type"] = mime_type

        # For images, try to get dimensions
        image_format = imghdr.what(file_path)
        if image_format:
            metadata["image_format"] = image_format
            try:
                with open(file_path, "rb") as f:
                    # Read a small portion of the file to determine dimensions
                    header = f.read(24)

                    if image_format == "png":
                        if len(header) >= 24:
                            width, height = struct.unpack(">II", header[16:24])
                            metadata["width"] = width
                            metadata["height"] = height

                    elif image_format in ("jpeg", "jpg"):
                        # JPEG is more complex, we need to scan through markers
                        f.seek(0)
                        size = 2
                        ftype = 0
                        while not 0xC0 <= ftype <= 0xCF or ftype in (0xC4, 0xC8, 0xCC):
                            f.seek(size, 1)
                            byte = f.read(1)
                            while byte and ord(byte) == 0xFF:
                                byte = f.read(1)
                            ftype = ord(byte)
                            size = struct.unpack(">H", f.read(2))[0] - 2

                        # We are at a SOFn marker, extract dimensions
                        f.seek(1, 1)
                        height, width = struct.unpack(">HH", f.read(4))
                        metadata["width"] = width
                        metadata["height"] = height

                    elif image_format == "gif":
                        if len(header) >= 10:
                            width, height = struct.unpack("<HH", header[6:10])
                            metadata["width"] = width
                            metadata["height"] = height
            except Exception:
                # If we can't get dimensions, just continue
                pass

        return metadata

    except Exception as e:
        raise DataError(f"Failed to extract metadata: {str(e)}")
