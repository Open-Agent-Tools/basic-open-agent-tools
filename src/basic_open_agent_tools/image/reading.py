"""Image reading and information extraction functions for AI agents."""

import os

from ..decorators import strands_tool

try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore[assignment,misc]

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit


@strands_tool
def get_image_info(file_path: str) -> dict[str, str]:
    """Get comprehensive image information and metadata.


    Args:
        file_path: Path to image file

    Returns:
        Dictionary with keys: width, height, format, mode, size_bytes

    Raises:
        ImportError: If Pillow is not installed
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or not a valid image

    Example:
        >>> info = get_image_info("/path/to/image.jpg")
        >>> info['format']
        'JPEG'
    """
    if Image is None:
        raise ImportError(
            "Pillow is required for image support. Install with: pip install Pillow"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    try:
        with Image.open(file_path) as img:
            return {
                "width": str(img.width),
                "height": str(img.height),
                "format": img.format or "Unknown",
                "mode": img.mode,
                "size_bytes": str(file_size),
            }

    except Exception as e:
        raise ValueError(f"Failed to read image info: {e}")


@strands_tool
def get_image_size(file_path: str) -> dict[str, int]:
    """Get image dimensions.

    Args:
        file_path: Path to image file

    Returns:
        Dictionary with keys: width, height

    Raises:
        ImportError: If Pillow is not installed
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or not a valid image

    Example:
        >>> size = get_image_size("/path/to/image.jpg")
        >>> size['width']
        1920
    """
    if Image is None:
        raise ImportError(
            "Pillow is required for image support. Install with: pip install Pillow"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    try:
        with Image.open(file_path) as img:
            return {"width": img.width, "height": img.height}

    except Exception as e:
        raise ValueError(f"Failed to get image size: {e}")


@strands_tool
def get_image_format(file_path: str) -> str:
    """Get image format (PNG, JPEG, GIF, etc.).

    Args:
        file_path: Path to image file

    Returns:
        Image format string (e.g., 'JPEG', 'PNG')

    Raises:
        ImportError: If Pillow is not installed
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or not a valid image

    Example:
        >>> fmt = get_image_format("/path/to/image.jpg")
        >>> fmt
        'JPEG'
    """
    if Image is None:
        raise ImportError(
            "Pillow is required for image support. Install with: pip install Pillow"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    try:
        with Image.open(file_path) as img:
            return img.format or "Unknown"

    except Exception as e:
        raise ValueError(f"Failed to get image format: {e}")


@strands_tool
def extract_image_exif(file_path: str) -> dict[str, str]:
    """Extract EXIF metadata from image.

    Args:
        file_path: Path to image file

    Returns:
        Dictionary of EXIF tag names and values

    Raises:
        ImportError: If Pillow is not installed
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or not a valid image

    Example:
        >>> exif = extract_image_exif("/path/to/photo.jpg")
        >>> exif.get('Make', '')
        'Canon'
    """
    if Image is None:
        raise ImportError(
            "Pillow is required for image support. Install with: pip install Pillow"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    try:
        with Image.open(file_path) as img:
            exif_data: dict[str, str] = {}

            # Get EXIF data if available
            if hasattr(img, "_getexif") and img._getexif():
                from PIL.ExifTags import TAGS

                exif = img._getexif()
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_data[str(tag)] = str(value)

            return exif_data

    except Exception as e:
        raise ValueError(f"Failed to extract EXIF data: {e}")


@strands_tool
def get_image_colors(file_path: str, num_colors: int) -> list[str]:
    """Get dominant colors from image.

    Args:
        file_path: Path to image file
        num_colors: Number of dominant colors to extract

    Returns:
        List of hex color strings (e.g., ['#FF0000', '#00FF00'])

    Raises:
        ImportError: If Pillow is not installed
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large, not valid image, or num_colors invalid

    Example:
        >>> colors = get_image_colors("/path/to/image.jpg", 3)
        >>> colors[0]
        '#1A2B3C'
    """
    if Image is None:
        raise ImportError(
            "Pillow is required for image support. Install with: pip install Pillow"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(num_colors, int):
        raise TypeError("num_colors must be an integer")

    if num_colors < 1 or num_colors > 256:
        raise ValueError("num_colors must be between 1 and 256")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    try:
        with Image.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Resize for faster processing
            img.thumbnail((200, 200))

            # Get colors using quantize
            palette = img.quantize(colors=num_colors).getpalette()

            if palette is None:
                return []

            # Convert palette to hex colors
            colors: list[str] = []
            for i in range(num_colors):
                r = palette[i * 3]
                g = palette[i * 3 + 1]
                b = palette[i * 3 + 2]
                colors.append(f"#{r:02X}{g:02X}{b:02X}")

            return colors

    except Exception as e:
        raise ValueError(f"Failed to extract image colors: {e}")


@strands_tool
def verify_image_file(file_path: str) -> bool:
    """Verify if file is a valid image.

    Args:
        file_path: Path to potential image file

    Returns:
        True if valid image, False otherwise

    Raises:
        ImportError: If Pillow is not installed
        TypeError: If parameters are wrong type
        FileNotFoundError: If file doesn't exist

    Example:
        >>> is_valid = verify_image_file("/path/to/file.jpg")
        >>> is_valid
        True
    """
    if Image is None:
        raise ImportError(
            "Pillow is required for image support. Install with: pip install Pillow"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False
