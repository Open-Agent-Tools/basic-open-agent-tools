"""Image manipulation and transformation functions for AI agents."""

import os

from ..decorators import strands_tool

try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore[assignment,misc]

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit


@strands_tool
def resize_image(
    file_path: str, output_path: str, width: int, height: int, skip_confirm: bool
) -> str:
    """Resize image to specified dimensions.

    Args:
        file_path: Path to source image
        output_path: Path for resized image
        width: Target width in pixels
        height: Target height in pixels
        skip_confirm: If False, raises error if output file exists

    Returns:
        Success message

    Raises:
        ImportError: If Pillow is not installed
        TypeError: If parameters are wrong type
        FileNotFoundError: If source file doesn't exist
        ValueError: If file exists and skip_confirm is False, or dimensions invalid

    Example:
        >>> msg = resize_image("/tmp/input.jpg", "/tmp/output.jpg", 800, 600, True)
        >>> "Resized" in msg
        True
    """
    if Image is None:
        raise ImportError(
            "Pillow is required for image support. Install with: pip install Pillow"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(output_path, str):
        raise TypeError("output_path must be a string")
    if not isinstance(width, int):
        raise TypeError("width must be an integer")
    if not isinstance(height, int):
        raise TypeError("height must be an integer")
    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if width < 1 or height < 1:
        raise ValueError("width and height must be positive integers")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")

    if os.path.exists(output_path) and not skip_confirm:
        raise ValueError(
            f"Output file already exists: {output_path}. Set skip_confirm=True to overwrite."
        )

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    try:
        with Image.open(file_path) as img:
            resized = img.resize((width, height), Image.Resampling.LANCZOS)
            resized.save(output_path)

        return f"Resized image saved to {output_path}"

    except Exception as e:
        raise ValueError(f"Failed to resize image: {e}")


@strands_tool
def crop_image(
    file_path: str,
    output_path: str,
    left: int,
    top: int,
    right: int,
    bottom: int,
    skip_confirm: bool,
) -> str:
    """Crop image to specified box.

    Args:
        file_path: Path to source image
        output_path: Path for cropped image
        left: Left coordinate
        top: Top coordinate
        right: Right coordinate
        bottom: Bottom coordinate
        skip_confirm: If False, raises error if output file exists

    Returns:
        Success message

    Raises:
        ImportError: If Pillow is not installed
        TypeError: If parameters are wrong type
        FileNotFoundError: If source file doesn't exist
        ValueError: If file exists and skip_confirm is False, or coordinates invalid

    Example:
        >>> msg = crop_image("/tmp/input.jpg", "/tmp/output.jpg", 0, 0, 100, 100, True)
        >>> "Cropped" in msg
        True
    """
    if Image is None:
        raise ImportError(
            "Pillow is required for image support. Install with: pip install Pillow"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(output_path, str):
        raise TypeError("output_path must be a string")
    if not isinstance(left, int):
        raise TypeError("left must be an integer")
    if not isinstance(top, int):
        raise TypeError("top must be an integer")
    if not isinstance(right, int):
        raise TypeError("right must be an integer")
    if not isinstance(bottom, int):
        raise TypeError("bottom must be an integer")
    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if left < 0 or top < 0 or right <= left or bottom <= top:
        raise ValueError("Invalid crop coordinates")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")

    if os.path.exists(output_path) and not skip_confirm:
        raise ValueError(
            f"Output file already exists: {output_path}. Set skip_confirm=True to overwrite."
        )

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    try:
        with Image.open(file_path) as img:
            cropped = img.crop((left, top, right, bottom))
            cropped.save(output_path)

        return f"Cropped image saved to {output_path}"

    except Exception as e:
        raise ValueError(f"Failed to crop image: {e}")


@strands_tool
def rotate_image(
    file_path: str, output_path: str, degrees: int, skip_confirm: bool
) -> str:
    """Rotate image by specified degrees.

    Args:
        file_path: Path to source image
        output_path: Path for rotated image
        degrees: Rotation angle in degrees (positive = counter-clockwise)
        skip_confirm: If False, raises error if output file exists

    Returns:
        Success message

    Raises:
        ImportError: If Pillow is not installed
        TypeError: If parameters are wrong type
        FileNotFoundError: If source file doesn't exist
        ValueError: If file exists and skip_confirm is False

    Example:
        >>> msg = rotate_image("/tmp/input.jpg", "/tmp/output.jpg", 90, True)
        >>> "Rotated" in msg
        True
    """
    if Image is None:
        raise ImportError(
            "Pillow is required for image support. Install with: pip install Pillow"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(output_path, str):
        raise TypeError("output_path must be a string")
    if not isinstance(degrees, int):
        raise TypeError("degrees must be an integer")
    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")

    if os.path.exists(output_path) and not skip_confirm:
        raise ValueError(
            f"Output file already exists: {output_path}. Set skip_confirm=True to overwrite."
        )

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    try:
        with Image.open(file_path) as img:
            rotated = img.rotate(degrees, expand=True)
            rotated.save(output_path)

        return f"Rotated image saved to {output_path}"

    except Exception as e:
        raise ValueError(f"Failed to rotate image: {e}")


@strands_tool
def convert_image_format(
    file_path: str, output_path: str, output_format: str, skip_confirm: bool
) -> str:
    """Convert image to different format.

    Args:
        file_path: Path to source image
        output_path: Path for converted image
        output_format: Target format (e.g., 'PNG', 'JPEG', 'GIF', 'BMP')
        skip_confirm: If False, raises error if output file exists

    Returns:
        Success message

    Raises:
        ImportError: If Pillow is not installed
        TypeError: If parameters are wrong type
        FileNotFoundError: If source file doesn't exist
        ValueError: If file exists and skip_confirm is False, or format invalid

    Example:
        >>> msg = convert_image_format("/tmp/input.jpg", "/tmp/output.png", "PNG", True)
        >>> "Converted" in msg
        True
    """
    if Image is None:
        raise ImportError(
            "Pillow is required for image support. Install with: pip install Pillow"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(output_path, str):
        raise TypeError("output_path must be a string")
    if not isinstance(output_format, str):
        raise TypeError("output_format must be a string")
    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    valid_formats = ["PNG", "JPEG", "GIF", "BMP", "TIFF", "WEBP"]
    if output_format.upper() not in valid_formats:
        raise ValueError(
            f"Invalid output format: {output_format}. Must be one of {valid_formats}"
        )

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")

    if os.path.exists(output_path) and not skip_confirm:
        raise ValueError(
            f"Output file already exists: {output_path}. Set skip_confirm=True to overwrite."
        )

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    try:
        with Image.open(file_path) as img:
            # Convert RGBA to RGB for JPEG
            if output_format.upper() == "JPEG" and img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            img.save(output_path, format=output_format.upper())

        return f"Converted image saved to {output_path}"

    except Exception as e:
        raise ValueError(f"Failed to convert image format: {e}")


@strands_tool
def create_thumbnail(
    file_path: str, output_path: str, max_size: int, skip_confirm: bool
) -> str:
    """Create thumbnail preserving aspect ratio.

    Args:
        file_path: Path to source image
        output_path: Path for thumbnail
        max_size: Maximum dimension (width or height) in pixels
        skip_confirm: If False, raises error if output file exists

    Returns:
        Success message

    Raises:
        ImportError: If Pillow is not installed
        TypeError: If parameters are wrong type
        FileNotFoundError: If source file doesn't exist
        ValueError: If file exists and skip_confirm is False, or max_size invalid

    Example:
        >>> msg = create_thumbnail("/tmp/input.jpg", "/tmp/thumb.jpg", 200, True)
        >>> "Created" in msg
        True
    """
    if Image is None:
        raise ImportError(
            "Pillow is required for image support. Install with: pip install Pillow"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(output_path, str):
        raise TypeError("output_path must be a string")
    if not isinstance(max_size, int):
        raise TypeError("max_size must be an integer")
    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if max_size < 1:
        raise ValueError("max_size must be a positive integer")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")

    if os.path.exists(output_path) and not skip_confirm:
        raise ValueError(
            f"Output file already exists: {output_path}. Set skip_confirm=True to overwrite."
        )

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    try:
        with Image.open(file_path) as img:
            img.thumbnail((max_size, max_size))
            img.save(output_path)

        return f"Created thumbnail at {output_path}"

    except Exception as e:
        raise ValueError(f"Failed to create thumbnail: {e}")


@strands_tool
def flip_image(
    file_path: str, output_path: str, direction: str, skip_confirm: bool
) -> str:
    """Flip image horizontally or vertically.

    Args:
        file_path: Path to source image
        output_path: Path for flipped image
        direction: Flip direction ('horizontal' or 'vertical')
        skip_confirm: If False, raises error if output file exists

    Returns:
        Success message

    Raises:
        ImportError: If Pillow is not installed
        TypeError: If parameters are wrong type
        FileNotFoundError: If source file doesn't exist
        ValueError: If file exists and skip_confirm is False, or direction invalid

    Example:
        >>> msg = flip_image("/tmp/input.jpg", "/tmp/output.jpg", "horizontal", True)
        >>> "Flipped" in msg
        True
    """
    if Image is None:
        raise ImportError(
            "Pillow is required for image support. Install with: pip install Pillow"
        )

    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if not isinstance(output_path, str):
        raise TypeError("output_path must be a string")
    if not isinstance(direction, str):
        raise TypeError("direction must be a string")
    if not isinstance(skip_confirm, bool):
        raise TypeError("skip_confirm must be a boolean")

    if direction not in ["horizontal", "vertical"]:
        raise ValueError("direction must be 'horizontal' or 'vertical'")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")

    if os.path.exists(output_path) and not skip_confirm:
        raise ValueError(
            f"Output file already exists: {output_path}. Set skip_confirm=True to overwrite."
        )

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"
        )

    try:
        with Image.open(file_path) as img:
            if direction == "horizontal":
                flipped = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            else:  # vertical
                flipped = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

            flipped.save(output_path)

        return f"Flipped image saved to {output_path}"

    except Exception as e:
        raise ValueError(f"Failed to flip image: {e}")
