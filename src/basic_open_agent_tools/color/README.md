# Color Tools

Pure Python color manipulation utilities with zero dependencies. Perfect for design systems, accessibility checking, and theme generation in AI agents.

## Features

- **14 Functions** across 3 categories
- **Zero Dependencies** - Pure Python math
- **Google ADK Compatible** - Agent-friendly signatures
- **WCAG Compliant** - Built-in accessibility checking

## Quick Start

```python
import basic_open_agent_tools as boat

# Load color tools
color_tools = boat.load_all_color_tools()

# Or import directly
from basic_open_agent_tools.color import (
    rgb_to_hex,
    hex_to_rgb,
    calculate_contrast_ratio,
    generate_palette,
)
```

## Color Conversion (6 functions)

### RGB ↔ Hex
```python
from basic_open_agent_tools.color import rgb_to_hex, hex_to_rgb

# RGB to Hex
hex_color = rgb_to_hex(255, 87, 51)  # "#FF5733"

# Hex to RGB
rgb = hex_to_rgb("#FF5733")  # {"r": 255, "g": 87, "b": 51}
rgb = hex_to_rgb("FF5733")   # Also accepts without #
rgb = hex_to_rgb("F73")      # Expands 3-character format
```

### RGB ↔ HSL
```python
from basic_open_agent_tools.color import rgb_to_hsl, hsl_to_rgb

# RGB to HSL (Hue, Saturation, Lightness)
hsl = rgb_to_hsl(255, 87, 51)
# {"h": 11, "s": 100, "l": 60}

# HSL to RGB
rgb = hsl_to_rgb(11, 100, 60)
# {"r": 255, "g": 87, "b": 51}
```

### RGB ↔ CMYK
```python
from basic_open_agent_tools.color import rgb_to_cmyk, cmyk_to_rgb

# RGB to CMYK (print colors)
cmyk = rgb_to_cmyk(255, 87, 51)
# {"c": 0, "m": 66, "y": 80, "k": 0}

# CMYK to RGB
rgb = cmyk_to_rgb(0, 66, 80, 0)
# {"r": 255, "g": 87, "b": 51}
```

## Color Analysis (4 functions)

### Luminance Calculation
```python
from basic_open_agent_tools.color import calculate_luminance

# Calculate relative luminance (0.0 = black, 1.0 = white)
lum = calculate_luminance(255, 255, 255)  # 1.0 (white)
lum = calculate_luminance(0, 0, 0)        # 0.0 (black)
lum = calculate_luminance(128, 128, 128)  # ~0.22 (mid gray)
```

### Contrast Ratio (WCAG)
```python
from basic_open_agent_tools.color import calculate_contrast_ratio

result = calculate_contrast_ratio("#000000", "#FFFFFF")
# {
#     "contrast_ratio": 21.0,
#     "color1_luminance": 0.0,
#     "color2_luminance": 1.0,
#     "wcag_rating": "AAA",  # AAA, AA, AA Large, or Fail
#     "color1": "#000000",
#     "color2": "#FFFFFF"
# }
```

### WCAG Compliance Check
```python
from basic_open_agent_tools.color import check_wcag_compliance

# Check if color combo meets accessibility standards
result = check_wcag_compliance("#333333", "#FFFFFF", "AA")
# {
#     "passes": True,
#     "contrast_ratio": 12.63,
#     "required_ratio": 4.5,
#     "level": "AA",
#     "foreground": "#333333",
#     "background": "#FFFFFF",
#     "recommendation": "Color combination passes AA standards"
# }

# Levels: "AA" (4.5:1), "AAA" (7:1), "AA_LARGE" (3:1 for large text)
```

### Complementary Color
```python
from basic_open_agent_tools.color import get_complementary_color

# Get opposite color on color wheel (180° rotation)
comp = get_complementary_color("#FF5733")  # "#33DBFF"
```

## Color Generation (4 functions)

### Lighten / Darken
```python
from basic_open_agent_tools.color import lighten_color, darken_color

# Lighten by 20%
lighter = lighten_color("#FF5733", 20)  # "#FF8566"

# Darken by 20%
darker = darken_color("#FF5733", 20)    # "#CC2400"
```

### Adjust Saturation
```python
from basic_open_agent_tools.color import adjust_saturation

# Increase saturation (more vivid)
vivid = adjust_saturation("#808080", 50)  # More colorful

# Decrease saturation (more gray)
muted = adjust_saturation("#FF5733", -50)  # Less saturated
```

### Generate Color Palettes
```python
from basic_open_agent_tools.color import generate_palette

# Monochromatic (same hue, different lightness)
palette = generate_palette("#FF5733", "monochromatic", 5)
# {
#     "scheme": "monochromatic",
#     "base_color": "#FF5733",
#     "count": 5,
#     "colors": ["#331100", "#663322", "#995544", "#CC7766", "#FF9988"]
# }

# Analogous (adjacent colors on wheel, ±30°)
palette = generate_palette("#FF5733", "analogous", 5)

# Complementary (opposite colors)
palette = generate_palette("#FF5733", "complementary", 4)

# Triadic (3 colors evenly spaced, 120° apart)
palette = generate_palette("#FF5733", "triadic", 6)

# Split Complementary (base + 2 colors near complement)
palette = generate_palette("#FF5733", "split_complementary", 5)
```

## Use Cases

### Design Systems
```python
# Generate theme from brand color
base = "#FF5733"
palette = generate_palette(base, "analogous", 5)
primary = palette["colors"][2]  # Base color
secondary = get_complementary_color(primary)
accent = lighten_color(primary, 30)
```

### Accessibility Checking
```python
# Ensure text meets WCAG standards
foreground = "#333333"
background = "#FFFFFF"

check = check_wcag_compliance(foreground, background, "AA")
if not check["passes"]:
    print(check["recommendation"])
    # Adjust colors until passing
```

### Color Conversion Workflows
```python
# Designer provides CMYK values for web
cmyk = cmyk_to_rgb(0, 66, 80, 0)
hex_color = rgb_to_hex(cmyk["r"], cmyk["g"], cmyk["b"])
# Use hex_color in CSS/HTML
```

## Function Reference

### Conversion
- `rgb_to_hex(r, g, b)` - RGB to hexadecimal
- `hex_to_rgb(hex_color)` - Hexadecimal to RGB
- `rgb_to_hsl(r, g, b)` - RGB to HSL
- `hsl_to_rgb(h, s, l)` - HSL to RGB
- `rgb_to_cmyk(r, g, b)` - RGB to CMYK
- `cmyk_to_rgb(c, m, y, k)` - CMYK to RGB

### Analysis
- `calculate_luminance(r, g, b)` - Relative luminance (0.0-1.0)
- `calculate_contrast_ratio(color1, color2)` - WCAG contrast ratio
- `check_wcag_compliance(fg, bg, level)` - Accessibility check
- `get_complementary_color(hex_color)` - Opposite on color wheel

### Generation
- `lighten_color(hex_color, percent)` - Increase lightness
- `darken_color(hex_color, percent)` - Decrease lightness
- `adjust_saturation(hex_color, percent)` - Adjust color intensity
- `generate_palette(base, scheme, count)` - Color theory palettes

## Dependencies

**None!** All functions use pure Python math.

## See Also

- [Main README](../../../../README.md) - Package overview
- [API Reference](../../../../docs/api-reference.md) - All functions
- [Examples](../../../../docs/examples.md) - Usage patterns
