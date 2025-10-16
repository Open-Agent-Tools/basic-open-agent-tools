"""Color analysis and accessibility utilities."""

from typing import Any

from ..decorators import strands_tool
from ..exceptions import BasicAgentToolsError
from .conversion import hex_to_rgb


@strands_tool
def calculate_luminance(r: int, g: int, b: int) -> float:
    """Calculate relative luminance of an RGB color.

    Uses the WCAG formula for relative luminance.
    Higher values are lighter, lower values are darker.

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Returns:
        Relative luminance value (0.0 to 1.0)

    Raises:
        BasicAgentToolsError: If color values are out of valid range
    """
    if not isinstance(r, int) or not isinstance(g, int) or not isinstance(b, int):
        raise BasicAgentToolsError("RGB values must be integers")

    if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
        raise BasicAgentToolsError("RGB values must be between 0 and 255")

    # Normalize to 0-1
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0

    # Apply gamma correction
    def adjust_gamma(channel: float) -> float:
        if channel <= 0.03928:
            return channel / 12.92
        else:
            result: float = ((channel + 0.055) / 1.055) ** 2.4
            return result

    r_linear = adjust_gamma(r_norm)
    g_linear = adjust_gamma(g_norm)
    b_linear = adjust_gamma(b_norm)

    # Calculate luminance using WCAG formula
    luminance: float = 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear

    return luminance


@strands_tool
def calculate_contrast_ratio(color1: str, color2: str) -> dict[str, Any]:
    """Calculate WCAG contrast ratio between two colors.

    Args:
        color1: First color as hex code (e.g., "#FF5733" or "FF5733")
        color2: Second color as hex code (e.g., "#FFFFFF" or "FFFFFF")

    Returns:
        Dictionary with contrast_ratio (float), color1_luminance (float),
        color2_luminance (float), and wcag_rating (str)

    Raises:
        BasicAgentToolsError: If color format is invalid
    """
    if not isinstance(color1, str) or not isinstance(color2, str):
        raise BasicAgentToolsError("Colors must be hex strings")

    # Convert to RGB
    try:
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
    except BasicAgentToolsError as e:
        raise BasicAgentToolsError(f"Invalid color format: {e}")

    # Calculate luminance for both colors
    lum1 = calculate_luminance(rgb1["r"], rgb1["g"], rgb1["b"])
    lum2 = calculate_luminance(rgb2["r"], rgb2["g"], rgb2["b"])

    # Calculate contrast ratio (lighter / darker + 1)
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    ratio = (lighter + 0.05) / (darker + 0.05)

    # Determine WCAG rating
    if ratio >= 7.0:
        rating = "AAA"
    elif ratio >= 4.5:
        rating = "AA"
    elif ratio >= 3.0:
        rating = "AA Large"
    else:
        rating = "Fail"

    return {
        "contrast_ratio": round(ratio, 2),
        "color1_luminance": round(lum1, 4),
        "color2_luminance": round(lum2, 4),
        "wcag_rating": rating,
        "color1": color1,
        "color2": color2,
    }


@strands_tool
def check_wcag_compliance(
    foreground: str, background: str, level: str
) -> dict[str, Any]:
    """Check if color combination meets WCAG accessibility standards.

    Args:
        foreground: Foreground color as hex code (e.g., "#333333")
        background: Background color as hex code (e.g., "#FFFFFF")
        level: WCAG level to check ("AA", "AAA", "AA_LARGE")

    Returns:
        Dictionary with passes (bool), contrast_ratio (float),
        required_ratio (float), level (str), and recommendation (str)

    Raises:
        BasicAgentToolsError: If colors or level are invalid
    """
    if not isinstance(foreground, str) or not isinstance(background, str):
        raise BasicAgentToolsError("Foreground and background must be hex strings")

    if not isinstance(level, str):
        raise BasicAgentToolsError("Level must be a string")

    level = level.upper().replace("-", "_")
    if level not in ("AA", "AAA", "AA_LARGE"):
        raise BasicAgentToolsError('Level must be "AA", "AAA", or "AA_LARGE"')

    # Calculate contrast ratio
    result = calculate_contrast_ratio(foreground, background)
    ratio = result["contrast_ratio"]

    # Determine required ratio and check compliance
    if level == "AAA":
        required = 7.0
        passes = ratio >= required
    elif level == "AA":
        required = 4.5
        passes = ratio >= required
    else:  # AA_LARGE
        required = 3.0
        passes = ratio >= required

    # Generate recommendation
    if passes:
        recommendation = f"Color combination passes {level} standards"
    else:
        needed = required - ratio
        recommendation = (
            f"Contrast ratio {ratio} is below {level} requirement of {required}. "
            f"Increase contrast by {round(needed, 2)} to meet standards."
        )

    return {
        "passes": passes,
        "contrast_ratio": ratio,
        "required_ratio": required,
        "level": level,
        "foreground": foreground,
        "background": background,
        "recommendation": recommendation,
    }


@strands_tool
def get_complementary_color(hex_color: str) -> str:
    """Get the complementary color (opposite on color wheel).

    Args:
        hex_color: Hex color code (e.g., "#FF5733" or "FF5733")

    Returns:
        Complementary color as hex code (e.g., "#33DBFF")

    Raises:
        BasicAgentToolsError: If color format is invalid
    """
    if not isinstance(hex_color, str):
        raise BasicAgentToolsError("Hex color must be a string")

    # Import locally to avoid circular dependency
    from .conversion import hsl_to_rgb, rgb_to_hsl

    # Convert to RGB then HSL
    try:
        rgb = hex_to_rgb(hex_color)
    except BasicAgentToolsError as e:
        raise BasicAgentToolsError(f"Invalid color format: {e}")

    hsl = rgb_to_hsl(rgb["r"], rgb["g"], rgb["b"])

    # Rotate hue by 180 degrees for complementary color
    comp_h = (hsl["h"] + 180) % 360

    # Convert back to RGB then hex
    comp_rgb = hsl_to_rgb(comp_h, hsl["s"], hsl["l"])

    # Import locally to avoid circular dependency
    from .conversion import rgb_to_hex

    result: str = rgb_to_hex(comp_rgb["r"], comp_rgb["g"], comp_rgb["b"])
    return result
