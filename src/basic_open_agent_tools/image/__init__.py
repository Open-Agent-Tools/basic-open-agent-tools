"""Image processing tools for AI agents."""

from .manipulation import (
    convert_image_format,
    create_thumbnail,
    crop_image,
    flip_image,
    resize_image,
    rotate_image,
)
from .reading import (
    extract_image_exif,
    get_image_colors,
    get_image_format,
    get_image_info,
    get_image_size,
    verify_image_file,
)

__all__: list[str] = [
    # Reading functions (6)
    "get_image_info",
    "get_image_size",
    "get_image_format",
    "extract_image_exif",
    "get_image_colors",
    "verify_image_file",
    # Manipulation functions (6)
    "resize_image",
    "crop_image",
    "rotate_image",
    "convert_image_format",
    "create_thumbnail",
    "flip_image",
]
