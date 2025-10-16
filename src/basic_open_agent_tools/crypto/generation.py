"""Random data and UUID generation utilities."""

import secrets
import string
import uuid
from typing import Union

from .._logging import get_logger
from ..decorators import strands_tool
from ..exceptions import BasicAgentToolsError

logger = get_logger("crypto.generation")


@strands_tool
def generate_uuid(version: int) -> dict[str, Union[str, int]]:
    """
    Generate a UUID (Universally Unique Identifier).

    Args:
        version: UUID version to generate (1 or 4)

    Returns:
        Dictionary with UUID information

    Raises:
        BasicAgentToolsError: If version is invalid
    """
    logger.debug(f"Generating UUID version {version}")

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

        logger.debug(f"UUID generated: {uuid_string}")

        return {
            "uuid_version": version,
            "uuid_type": uuid_type,
            "uuid_string": uuid_string,
            "uuid_hex": uuid_hex,
            "uuid_bytes_length": 16,
            "uuid_string_length": len(uuid_string),
        }

    except Exception as e:
        logger.error(f"UUID generation failed: {e}")
        raise BasicAgentToolsError(f"Failed to generate UUID: {str(e)}")


@strands_tool
def generate_random_string(
    length: int, character_set: str
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
    logger.debug(f"Generating random string: length={length}, charset={character_set}")

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

        logger.debug(
            f"Random string generated: {length} chars, {length * len(chars).bit_length()} bits entropy"
        )

        return {
            "random_string": random_string,
            "requested_length": length,
            "actual_length": len(random_string),
            "character_set": character_set,
            "character_set_size": len(chars),
            "entropy_bits": length * len(chars).bit_length(),
        }

    except Exception as e:
        logger.error(f"Random string generation failed: {e}")
        raise BasicAgentToolsError(f"Failed to generate random string: {str(e)}")


@strands_tool
def generate_random_bytes(length: int, encoding: str) -> dict[str, Union[str, int]]:
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
    logger.debug(f"Generating random bytes: length={length}, encoding={encoding}")

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

        logger.debug(
            f"Random bytes generated: {length} bytes, {length * 8} bits entropy, encoded as {encoding}"
        )

        return {
            "random_bytes_length": length,
            "encoding": encoding,
            "encoded_data": encoded_data,
            "encoded_length": len(encoded_data),
            "entropy_bits": length * 8,
        }

    except Exception as e:
        logger.error(f"Random bytes generation failed: {e}")
        raise BasicAgentToolsError(f"Failed to generate random bytes: {str(e)}")
