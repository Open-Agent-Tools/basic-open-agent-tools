"""Random data and UUID generation utilities."""

import secrets
import string
import uuid
from typing import Any, Callable, Union

try:
    from strands import tool as strands_tool
except ImportError:

    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        """Fallback decorator when strands is not available."""
        return func


from ..exceptions import BasicAgentToolsError


@strands_tool
def generate_uuid(version: int = 4) -> dict[str, str]:
    """
    Generate a UUID (Universally Unique Identifier).

    Args:
        version: UUID version to generate (1 or 4)

    Returns:
        Dictionary with UUID information

    Raises:
        BasicAgentToolsError: If version is invalid
    """
    if not isinstance(version, int) or version not in [1, 4]:
        raise BasicAgentToolsError("Version must be 1 or 4")

    try:
        if version == 1:
            # UUID1 includes MAC address and timestamp
            generated_uuid = uuid.uuid1()
            uuid_type = "time-based (includes MAC address)"
        else:  # version == 4
            # UUID4 is random
            generated_uuid = uuid.uuid4()
            uuid_type = "random"

        uuid_string = str(generated_uuid)
        uuid_hex = generated_uuid.hex

        return {
            "uuid_version": version,
            "uuid_type": uuid_type,
            "uuid_string": uuid_string,
            "uuid_hex": uuid_hex,
            "uuid_bytes_length": 16,
            "uuid_string_length": len(uuid_string),
        }

    except Exception as e:
        raise BasicAgentToolsError(f"Failed to generate UUID: {str(e)}")


@strands_tool
def generate_random_string(
    length: int = 16, character_set: str = "alphanumeric"
) -> dict[str, Union[str, int]]:
    """
    Generate a cryptographically secure random string.

    Args:
        length: Length of the random string (1-1000)
        character_set: Character set to use (alphanumeric, letters, digits, ascii)

    Returns:
        Dictionary with random string information

    Raises:
        BasicAgentToolsError: If parameters are invalid
    """
    if not isinstance(length, int) or length < 1 or length > 1000:
        raise BasicAgentToolsError("Length must be an integer between 1 and 1000")

    if not isinstance(character_set, str):
        raise BasicAgentToolsError("Character set must be a string")

    character_set = character_set.lower().strip()

    try:
        # Define character sets
        if character_set == "alphanumeric":
            chars = string.ascii_letters + string.digits
        elif character_set == "letters":
            chars = string.ascii_letters
        elif character_set == "digits":
            chars = string.digits
        elif character_set == "ascii":
            chars = string.ascii_letters + string.digits + string.punctuation
        else:
            raise BasicAgentToolsError(
                "Character set must be one of: alphanumeric, letters, digits, ascii"
            )

        # Generate random string
        random_string = "".join(secrets.choice(chars) for _ in range(length))

        return {
            "random_string": random_string,
            "requested_length": length,
            "actual_length": len(random_string),
            "character_set": character_set,
            "character_set_size": len(chars),
            "entropy_bits": length * len(chars).bit_length(),
        }

    except Exception as e:
        raise BasicAgentToolsError(f"Failed to generate random string: {str(e)}")


@strands_tool
def generate_random_bytes(
    length: int = 16, encoding: str = "hex"
) -> dict[str, Union[str, int]]:
    """
    Generate cryptographically secure random bytes.

    Args:
        length: Number of random bytes to generate (1-1000)
        encoding: How to encode the bytes (hex, base64)

    Returns:
        Dictionary with random bytes information

    Raises:
        BasicAgentToolsError: If parameters are invalid
    """
    if not isinstance(length, int) or length < 1 or length > 1000:
        raise BasicAgentToolsError("Length must be an integer between 1 and 1000")

    if not isinstance(encoding, str):
        raise BasicAgentToolsError("Encoding must be a string")

    encoding = encoding.lower().strip()

    if encoding not in ["hex", "base64"]:
        raise BasicAgentToolsError("Encoding must be 'hex' or 'base64'")

    try:
        # Generate random bytes
        random_bytes = secrets.token_bytes(length)

        # Encode the bytes
        if encoding == "hex":
            encoded_data = random_bytes.hex()
        else:  # base64
            import base64

            encoded_data = base64.b64encode(random_bytes).decode("ascii")

        return {
            "random_bytes_length": length,
            "encoding": encoding,
            "encoded_data": encoded_data,
            "encoded_length": len(encoded_data),
            "entropy_bits": length * 8,
        }

    except Exception as e:
        raise BasicAgentToolsError(f"Failed to generate random bytes: {str(e)}")
