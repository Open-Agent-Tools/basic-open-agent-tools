"""Color conversion and manipulation tools.

This module provides pure Python utilities for color operations including:
- Format conversion (RGB, HEX, HSL, CMYK)
- Color analysis (luminance, contrast, accessibility)
- Color generation (palettes, adjustments)

All functions use zero external dependencies.
"""

from .analysis import (
    calculate_contrast_ratio,
    calculate_luminance,
    check_wcag_compliance,
    get_complementary_color,
)
from .conversion import (
    cmyk_to_rgb,
    hex_to_rgb,
    hsl_to_rgb,
    rgb_to_cmyk,
    rgb_to_hex,
    rgb_to_hsl,
)
from .generation import (
    adjust_saturation,
    darken_color,
    generate_palette,
    lighten_color,
)

__all__ = [
    # Conversion functions
    "rgb_to_hex",
    "hex_to_rgb",
    "rgb_to_hsl",
    "hsl_to_rgb",
    "rgb_to_cmyk",
    "cmyk_to_rgb",
    # Analysis functions
    "calculate_luminance",
    "calculate_contrast_ratio",
    "check_wcag_compliance",
    "get_complementary_color",
    # Generation functions
    "generate_palette",
    "lighten_color",
    "darken_color",
    "adjust_saturation",
]
