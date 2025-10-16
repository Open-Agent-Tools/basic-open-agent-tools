"""Color format conversion utilities."""

from ..decorators import strands_tool
from ..exceptions import BasicAgentToolsError


def _hue_to_rgb(p: float, q: float, t: float) -> float:
    """Convert hue component to RGB value.

    Helper function for HSL to RGB conversion. Calculates the RGB component
    value for a given hue position using the HSL color model.

    Args:
        p: Lower RGB component bound
        q: Upper RGB component bound
        t: Hue position (normalized 0-1)

    Returns:
        RGB component value (0-1 range)
    """
    if t < 0:
        t += 1
    if t > 1:
        t -= 1
    if t < 1 / 6:
        return p + (q - p) * 6 * t
    if t < 1 / 2:
        return q
    if t < 2 / 3:
        return p + (q - p) * (2 / 3 - t) * 6
    return p


@strands_tool
def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB color values to hexadecimal color code.

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Returns:
        Hexadecimal color code (e.g., "#FF5733")

    Raises:
        BasicAgentToolsError: If color values are out of valid range
    """
    if not isinstance(r, int) or not isinstance(g, int) or not isinstance(b, int):
        raise BasicAgentToolsError("RGB values must be integers")

    if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
        raise BasicAgentToolsError("RGB values must be between 0 and 255")

    return f"#{r:02X}{g:02X}{b:02X}"


@strands_tool
def hex_to_rgb(hex_color: str) -> dict[str, int]:
    """Convert hexadecimal color code to RGB values.

    Args:
        hex_color: Hexadecimal color code (e.g., "#FF5733" or "FF5733")

    Returns:
        Dictionary with r, g, b integer values (0-255)

    Raises:
        BasicAgentToolsError: If hex color format is invalid
    """
    if not isinstance(hex_color, str):
        raise BasicAgentToolsError("Hex color must be a string")

    # Remove # if present
    hex_color = hex_color.strip()
    if hex_color.startswith("#"):
        hex_color = hex_color[1:]

    # Validate length
    if len(hex_color) not in (3, 6):
        raise BasicAgentToolsError("Hex color must be 3 or 6 characters (excluding #)")

    # Expand 3-character format to 6
    if len(hex_color) == 3:
        hex_color = "".join([c * 2 for c in hex_color])

    # Validate hex characters
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    except ValueError:
        raise BasicAgentToolsError(
            f"Invalid hexadecimal color: {hex_color}. Must contain only 0-9, A-F"
        )

    return {"r": r, "g": g, "b": b}


@strands_tool
def rgb_to_hsl(r: int, g: int, b: int) -> dict[str, int]:
    """Convert RGB color values to HSL (Hue, Saturation, Lightness).

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Returns:
        Dictionary with h (0-360), s (0-100), l (0-100) integer values

    Raises:
        BasicAgentToolsError: If color values are out of valid range
    """
    if not isinstance(r, int) or not isinstance(g, int) or not isinstance(b, int):
        raise BasicAgentToolsError("RGB values must be integers")

    if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
        raise BasicAgentToolsError("RGB values must be between 0 and 255")

    # Normalize RGB values to 0-1
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0

    max_val = max(r_norm, g_norm, b_norm)
    min_val = min(r_norm, g_norm, b_norm)
    diff = max_val - min_val

    # Calculate lightness
    lightness_value = (max_val + min_val) / 2.0

    # Calculate saturation
    h_value: float
    s_value: float

    if diff == 0:
        h_value = 0.0
        s_value = 0.0
    else:
        # Calculate saturation
        if lightness_value < 0.5:
            s_value = diff / (max_val + min_val)
        else:
            s_value = diff / (2.0 - max_val - min_val)

        # Calculate hue
        if max_val == r_norm:
            h_value = ((g_norm - b_norm) / diff) % 6
        elif max_val == g_norm:
            h_value = ((b_norm - r_norm) / diff) + 2
        else:
            h_value = ((r_norm - g_norm) / diff) + 4

        h_value = h_value * 60

    return {
        "h": int(round(h_value)),
        "s": int(round(s_value * 100)),
        "l": int(round(lightness_value * 100)),
    }


@strands_tool
def hsl_to_rgb(h: int, s: int, lightness: int) -> dict[str, int]:
    """Convert HSL (Hue, Saturation, Lightness) to RGB color values.

    Args:
        h: Hue (0-360 degrees)
        s: Saturation (0-100 percent)
        lightness: Lightness (0-100 percent)

    Returns:
        Dictionary with r, g, b integer values (0-255)

    Raises:
        BasicAgentToolsError: If HSL values are out of valid range
    """
    if (
        not isinstance(h, int)
        or not isinstance(s, int)
        or not isinstance(lightness, int)
    ):
        raise BasicAgentToolsError("HSL values must be integers")

    if not (0 <= h <= 360):
        raise BasicAgentToolsError("Hue must be between 0 and 360")

    if not (0 <= s <= 100 and 0 <= lightness <= 100):
        raise BasicAgentToolsError("Saturation and Lightness must be between 0 and 100")

    # Normalize s and lightness to 0-1
    s_norm = s / 100.0
    l_norm = lightness / 100.0

    if s == 0:
        # Achromatic (gray)
        r = g = b = int(round(l_norm * 255))
    else:
        if l_norm < 0.5:
            q = l_norm * (1 + s_norm)
        else:
            q = l_norm + s_norm - l_norm * s_norm
        p = 2 * l_norm - q

        h_norm = h / 360.0
        r = int(round(_hue_to_rgb(p, q, h_norm + 1 / 3) * 255))
        g = int(round(_hue_to_rgb(p, q, h_norm) * 255))
        b = int(round(_hue_to_rgb(p, q, h_norm - 1 / 3) * 255))

    return {"r": r, "g": g, "b": b}


@strands_tool
def rgb_to_cmyk(r: int, g: int, b: int) -> dict[str, int]:
    """Convert RGB color values to CMYK (Cyan, Magenta, Yellow, Key/Black).

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Returns:
        Dictionary with c, m, y, k integer values (0-100 percent)

    Raises:
        BasicAgentToolsError: If color values are out of valid range
    """
    if not isinstance(r, int) or not isinstance(g, int) or not isinstance(b, int):
        raise BasicAgentToolsError("RGB values must be integers")

    if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
        raise BasicAgentToolsError("RGB values must be between 0 and 255")

    # Handle black specially
    if r == 0 and g == 0 and b == 0:
        return {"c": 0, "m": 0, "y": 0, "k": 100}

    # Normalize RGB to 0-1
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0

    # Calculate K (black)
    k = 1 - max(r_norm, g_norm, b_norm)

    # Calculate CMY
    c = (1 - r_norm - k) / (1 - k)
    m = (1 - g_norm - k) / (1 - k)
    y = (1 - b_norm - k) / (1 - k)

    return {
        "c": int(round(c * 100)),
        "m": int(round(m * 100)),
        "y": int(round(y * 100)),
        "k": int(round(k * 100)),
    }


@strands_tool
def cmyk_to_rgb(c: int, m: int, y: int, k: int) -> dict[str, int]:
    """Convert CMYK (Cyan, Magenta, Yellow, Key/Black) to RGB color values.

    Args:
        c: Cyan (0-100 percent)
        m: Magenta (0-100 percent)
        y: Yellow (0-100 percent)
        k: Key/Black (0-100 percent)

    Returns:
        Dictionary with r, g, b integer values (0-255)

    Raises:
        BasicAgentToolsError: If CMYK values are out of valid range
    """
    if (
        not isinstance(c, int)
        or not isinstance(m, int)
        or not isinstance(y, int)
        or not isinstance(k, int)
    ):
        raise BasicAgentToolsError("CMYK values must be integers")

    if not (0 <= c <= 100 and 0 <= m <= 100 and 0 <= y <= 100 and 0 <= k <= 100):
        raise BasicAgentToolsError("CMYK values must be between 0 and 100")

    # Normalize to 0-1
    c_norm = c / 100.0
    m_norm = m / 100.0
    y_norm = y / 100.0
    k_norm = k / 100.0

    # Convert to RGB
    r = int(round(255 * (1 - c_norm) * (1 - k_norm)))
    g = int(round(255 * (1 - m_norm) * (1 - k_norm)))
    b = int(round(255 * (1 - y_norm) * (1 - k_norm)))

    return {"r": r, "g": g, "b": b}
