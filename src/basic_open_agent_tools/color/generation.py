"""Color palette generation and adjustment utilities."""

from typing import Any

from ..decorators import strands_tool
from ..exceptions import BasicAgentToolsError
from .conversion import hex_to_rgb, hsl_to_rgb, rgb_to_hex, rgb_to_hsl


@strands_tool
def lighten_color(hex_color: str, percent: int) -> str:
    """Lighten a color by increasing its lightness.

    Args:
        hex_color: Hex color code (e.g., "#FF5733" or "FF5733")
        percent: Percentage to lighten (0-100)

    Returns:
        Lightened color as hex code

    Raises:
        BasicAgentToolsError: If color format or percent is invalid
    """
    if not isinstance(hex_color, str):
        raise BasicAgentToolsError("Hex color must be a string")

    if not isinstance(percent, int):
        raise BasicAgentToolsError("Percent must be an integer")

    if not (0 <= percent <= 100):
        raise BasicAgentToolsError("Percent must be between 0 and 100")

    # Convert to HSL
    try:
        rgb = hex_to_rgb(hex_color)
    except BasicAgentToolsError as e:
        raise BasicAgentToolsError(f"Invalid color format: {e}")

    hsl = rgb_to_hsl(rgb["r"], rgb["g"], rgb["b"])

    # Increase lightness
    new_l = min(100, hsl["l"] + percent)

    # Convert back to RGB and hex
    new_rgb = hsl_to_rgb(hsl["h"], hsl["s"], new_l)
    result: str = rgb_to_hex(new_rgb["r"], new_rgb["g"], new_rgb["b"])
    return result


@strands_tool
def darken_color(hex_color: str, percent: int) -> str:
    """Darken a color by decreasing its lightness.

    Args:
        hex_color: Hex color code (e.g., "#FF5733" or "FF5733")
        percent: Percentage to darken (0-100)

    Returns:
        Darkened color as hex code

    Raises:
        BasicAgentToolsError: If color format or percent is invalid
    """
    if not isinstance(hex_color, str):
        raise BasicAgentToolsError("Hex color must be a string")

    if not isinstance(percent, int):
        raise BasicAgentToolsError("Percent must be an integer")

    if not (0 <= percent <= 100):
        raise BasicAgentToolsError("Percent must be between 0 and 100")

    # Convert to HSL
    try:
        rgb = hex_to_rgb(hex_color)
    except BasicAgentToolsError as e:
        raise BasicAgentToolsError(f"Invalid color format: {e}")

    hsl = rgb_to_hsl(rgb["r"], rgb["g"], rgb["b"])

    # Decrease lightness
    new_l = max(0, hsl["l"] - percent)

    # Convert back to RGB and hex
    new_rgb = hsl_to_rgb(hsl["h"], hsl["s"], new_l)
    result: str = rgb_to_hex(new_rgb["r"], new_rgb["g"], new_rgb["b"])
    return result


@strands_tool
def adjust_saturation(hex_color: str, percent: int) -> str:
    """Adjust color saturation by a percentage.

    Positive values increase saturation (more vivid).
    Negative values decrease saturation (more gray).

    Args:
        hex_color: Hex color code (e.g., "#FF5733" or "FF5733")
        percent: Percentage to adjust saturation (-100 to 100)

    Returns:
        Adjusted color as hex code

    Raises:
        BasicAgentToolsError: If color format or percent is invalid
    """
    if not isinstance(hex_color, str):
        raise BasicAgentToolsError("Hex color must be a string")

    if not isinstance(percent, int):
        raise BasicAgentToolsError("Percent must be an integer")

    if not (-100 <= percent <= 100):
        raise BasicAgentToolsError("Percent must be between -100 and 100")

    # Convert to HSL
    try:
        rgb = hex_to_rgb(hex_color)
    except BasicAgentToolsError as e:
        raise BasicAgentToolsError(f"Invalid color format: {e}")

    hsl = rgb_to_hsl(rgb["r"], rgb["g"], rgb["b"])

    # Adjust saturation
    new_s = max(0, min(100, hsl["s"] + percent))

    # Convert back to RGB and hex
    new_rgb = hsl_to_rgb(hsl["h"], new_s, hsl["l"])
    result: str = rgb_to_hex(new_rgb["r"], new_rgb["g"], new_rgb["b"])
    return result


@strands_tool
def generate_palette(base_color: str, scheme: str, count: int) -> dict[str, Any]:
    """Generate a color palette based on color theory schemes.

    Args:
        base_color: Base hex color code (e.g., "#FF5733" or "FF5733")
        scheme: Color scheme type ("monochromatic", "analogous", "complementary",
                "triadic", "split_complementary")
        count: Number of colors to generate (2-10)

    Returns:
        Dictionary with scheme, base_color, count, and colors (list of hex codes)

    Raises:
        BasicAgentToolsError: If parameters are invalid
    """
    if not isinstance(base_color, str):
        raise BasicAgentToolsError("Base color must be a string")

    if not isinstance(scheme, str):
        raise BasicAgentToolsError("Scheme must be a string")

    if not isinstance(count, int):
        raise BasicAgentToolsError("Count must be an integer")

    scheme = scheme.lower().replace("-", "_")
    valid_schemes = [
        "monochromatic",
        "analogous",
        "complementary",
        "triadic",
        "split_complementary",
    ]
    if scheme not in valid_schemes:
        raise BasicAgentToolsError(f"Scheme must be one of: {', '.join(valid_schemes)}")

    if not (2 <= count <= 10):
        raise BasicAgentToolsError("Count must be between 2 and 10")

    # Convert base color to HSL
    try:
        rgb = hex_to_rgb(base_color)
    except BasicAgentToolsError as e:
        raise BasicAgentToolsError(f"Invalid color format: {e}")

    hsl = rgb_to_hsl(rgb["r"], rgb["g"], rgb["b"])
    base_h = hsl["h"]
    base_s = hsl["s"]
    base_l = hsl["l"]

    colors: list[str] = []

    if scheme == "monochromatic":
        # Vary lightness, keep hue and saturation
        for i in range(count):
            # Generate colors from dark to light
            l_value = int(20 + (60 * i / (count - 1)))
            new_rgb = hsl_to_rgb(base_h, base_s, l_value)
            colors.append(rgb_to_hex(new_rgb["r"], new_rgb["g"], new_rgb["b"]))

    elif scheme == "analogous":
        # Colors adjacent on the color wheel (±30 degrees)
        step = 60 // (count - 1) if count > 1 else 0
        for i in range(count):
            offset = -30 + (i * step)
            new_h = (base_h + offset) % 360
            new_rgb = hsl_to_rgb(new_h, base_s, base_l)
            colors.append(rgb_to_hex(new_rgb["r"], new_rgb["g"], new_rgb["b"]))

    elif scheme == "complementary":
        # Base color and its complement (180 degrees opposite)
        colors.append(base_color)
        comp_h = (base_h + 180) % 360
        comp_rgb = hsl_to_rgb(comp_h, base_s, base_l)
        colors.append(rgb_to_hex(comp_rgb["r"], comp_rgb["g"], comp_rgb["b"]))

        # Fill remaining with variations
        remaining = count - 2
        for i in range(remaining):
            if i % 2 == 0:
                # Lighter variation of base
                l_value = min(100, base_l + 20)
                new_rgb = hsl_to_rgb(base_h, base_s, l_value)
            else:
                # Darker variation of complement
                l_value = max(0, base_l - 20)
                new_rgb = hsl_to_rgb(comp_h, base_s, l_value)
            colors.append(rgb_to_hex(new_rgb["r"], new_rgb["g"], new_rgb["b"]))

    elif scheme == "triadic":
        # Three colors evenly spaced (120 degrees apart)
        for i in range(min(3, count)):
            new_h = (base_h + (i * 120)) % 360
            new_rgb = hsl_to_rgb(new_h, base_s, base_l)
            colors.append(rgb_to_hex(new_rgb["r"], new_rgb["g"], new_rgb["b"]))

        # Fill remaining with variations
        for i in range(count - 3):
            idx = i % 3
            h_value = (base_h + (idx * 120)) % 360
            l_value = base_l + (20 if i % 2 == 0 else -20)
            l_value = max(0, min(100, l_value))
            new_rgb = hsl_to_rgb(h_value, base_s, l_value)
            colors.append(rgb_to_hex(new_rgb["r"], new_rgb["g"], new_rgb["b"]))

    elif scheme == "split_complementary":
        # Base color and two colors adjacent to complement
        colors.append(base_color)
        comp_h = (base_h + 180) % 360
        split1_h = (comp_h - 30) % 360
        split2_h = (comp_h + 30) % 360

        split1_rgb = hsl_to_rgb(split1_h, base_s, base_l)
        split2_rgb = hsl_to_rgb(split2_h, base_s, base_l)
        colors.append(rgb_to_hex(split1_rgb["r"], split1_rgb["g"], split1_rgb["b"]))
        colors.append(rgb_to_hex(split2_rgb["r"], split2_rgb["g"], split2_rgb["b"]))

        # Fill remaining with variations
        for i in range(count - 3):
            if i % 3 == 0:
                h_value = base_h
            elif i % 3 == 1:
                h_value = split1_h
            else:
                h_value = split2_h

            l_value = base_l + (20 if i % 2 == 0 else -20)
            l_value = max(0, min(100, l_value))
            new_rgb = hsl_to_rgb(h_value, base_s, l_value)
            colors.append(rgb_to_hex(new_rgb["r"], new_rgb["g"], new_rgb["b"]))

    return {
        "scheme": scheme,
        "base_color": base_color,
        "count": len(colors),
        "colors": colors,
    }
