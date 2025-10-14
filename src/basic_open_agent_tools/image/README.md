# Image Tools

Image processing tools with reading, manipulation, and format conversion (12 functions).

## Features
- **Reading** (6): Get info, size, format, EXIF data, colors, verify
- **Manipulation** (6): Resize, crop, rotate, convert format, thumbnail, flip

## Dependencies
- Pillow >= 10.0.0

## Usage
```python
from basic_open_agent_tools.image import (
    get_image_info,
    resize_image,
    convert_image_format,
    create_thumbnail
)

# Get image info
info = get_image_info("/path/to/image.jpg")
print(f"Size: {info['width']}x{info['height']}")

# Resize image
resize_image("/path/to/input.jpg", "/path/to/output.jpg", 800, 600, True)

# Convert format
convert_image_format("/path/to/input.jpg", "/path/to/output.png", "PNG", True)

# Create thumbnail
create_thumbnail("/path/to/image.jpg", "/path/to/thumb.jpg", 200, True)
```
