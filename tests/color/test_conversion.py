"""Tests for color conversion functions."""

import pytest

from basic_open_agent_tools.color.conversion import (
    cmyk_to_rgb,
    hex_to_rgb,
    hsl_to_rgb,
    rgb_to_cmyk,
    rgb_to_hex,
    rgb_to_hsl,
)
from basic_open_agent_tools.exceptions import BasicAgentToolsError


class TestRgbToHex:
    """Test RGB to hexadecimal conversion."""

    def test_basic_conversion(self) -> None:
        """Test basic RGB to hex conversion."""
        assert rgb_to_hex(255, 87, 51) == "#FF5733"
        assert rgb_to_hex(0, 0, 0) == "#000000"
        assert rgb_to_hex(255, 255, 255) == "#FFFFFF"

    def test_various_colors(self) -> None:
        """Test various color conversions."""
        assert rgb_to_hex(255, 0, 0) == "#FF0000"  # Red
        assert rgb_to_hex(0, 255, 0) == "#00FF00"  # Green
        assert rgb_to_hex(0, 0, 255) == "#0000FF"  # Blue
        assert rgb_to_hex(128, 128, 128) == "#808080"  # Gray

    def test_invalid_type(self) -> None:
        """Test with invalid types."""
        with pytest.raises(BasicAgentToolsError, match="RGB values must be integers"):
            rgb_to_hex(255.5, 87, 51)  # type: ignore[arg-type]
        with pytest.raises(BasicAgentToolsError, match="RGB values must be integers"):
            rgb_to_hex("255", 87, 51)  # type: ignore[arg-type]

    def test_out_of_range(self) -> None:
        """Test with out of range values."""
        with pytest.raises(
            BasicAgentToolsError, match="RGB values must be between 0 and 255"
        ):
            rgb_to_hex(256, 87, 51)
        with pytest.raises(
            BasicAgentToolsError, match="RGB values must be between 0 and 255"
        ):
            rgb_to_hex(-1, 87, 51)


class TestHexToRgb:
    """Test hexadecimal to RGB conversion."""

    def test_basic_conversion(self) -> None:
        """Test basic hex to RGB conversion."""
        result = hex_to_rgb("#FF5733")
        assert result == {"r": 255, "g": 87, "b": 51}

    def test_without_hash(self) -> None:
        """Test hex conversion without # prefix."""
        result = hex_to_rgb("FF5733")
        assert result == {"r": 255, "g": 87, "b": 51}

    def test_three_character_format(self) -> None:
        """Test 3-character hex format expansion."""
        result = hex_to_rgb("#F73")
        assert result == {"r": 255, "g": 119, "b": 51}

        result = hex_to_rgb("ABC")
        assert result == {"r": 170, "g": 187, "b": 204}

    def test_black_and_white(self) -> None:
        """Test black and white conversions."""
        assert hex_to_rgb("#000000") == {"r": 0, "g": 0, "b": 0}
        assert hex_to_rgb("#FFFFFF") == {"r": 255, "g": 255, "b": 255}

    def test_invalid_type(self) -> None:
        """Test with invalid type."""
        with pytest.raises(BasicAgentToolsError, match="Hex color must be a string"):
            hex_to_rgb(123456)  # type: ignore[arg-type]

    def test_invalid_length(self) -> None:
        """Test with invalid hex length."""
        with pytest.raises(
            BasicAgentToolsError, match="Hex color must be 3 or 6 characters"
        ):
            hex_to_rgb("#FF")
        with pytest.raises(
            BasicAgentToolsError, match="Hex color must be 3 or 6 characters"
        ):
            hex_to_rgb("#FF57331")

    def test_invalid_characters(self) -> None:
        """Test with invalid hex characters."""
        with pytest.raises(
            BasicAgentToolsError, match="Invalid hexadecimal color.*Must contain only"
        ):
            hex_to_rgb("#GGGGGG")
        with pytest.raises(
            BasicAgentToolsError, match="Invalid hexadecimal color.*Must contain only"
        ):
            hex_to_rgb("#ZZZ")


class TestRgbToHsl:
    """Test RGB to HSL conversion."""

    def test_basic_conversion(self) -> None:
        """Test basic RGB to HSL conversion."""
        result = rgb_to_hsl(255, 87, 51)
        assert result["h"] == 11
        assert result["s"] == 100
        assert result["l"] == 60

    def test_pure_colors(self) -> None:
        """Test pure color conversions."""
        # Red
        result = rgb_to_hsl(255, 0, 0)
        assert result["h"] == 0
        assert result["s"] == 100

        # Green
        result = rgb_to_hsl(0, 255, 0)
        assert result["h"] == 120
        assert result["s"] == 100

        # Blue
        result = rgb_to_hsl(0, 0, 255)
        assert result["h"] == 240
        assert result["s"] == 100

    def test_grayscale(self) -> None:
        """Test grayscale (no saturation)."""
        result = rgb_to_hsl(128, 128, 128)
        assert result["h"] == 0
        assert result["s"] == 0
        assert 49 <= result["l"] <= 51  # Allow rounding

    def test_black_and_white(self) -> None:
        """Test black and white."""
        # Black
        result = rgb_to_hsl(0, 0, 0)
        assert result["l"] == 0

        # White
        result = rgb_to_hsl(255, 255, 255)
        assert result["l"] == 100

    def test_invalid_type(self) -> None:
        """Test with invalid types."""
        with pytest.raises(BasicAgentToolsError, match="RGB values must be integers"):
            rgb_to_hsl(255.5, 87, 51)  # type: ignore[arg-type]

    def test_out_of_range(self) -> None:
        """Test with out of range values."""
        with pytest.raises(
            BasicAgentToolsError, match="RGB values must be between 0 and 255"
        ):
            rgb_to_hsl(256, 87, 51)


class TestHslToRgb:
    """Test HSL to RGB conversion."""

    def test_basic_conversion(self) -> None:
        """Test basic HSL to RGB conversion."""
        result = hsl_to_rgb(11, 100, 60)
        # Allow small rounding differences
        assert result["r"] == 255
        assert 86 <= result["g"] <= 88
        assert 50 <= result["b"] <= 52

    def test_pure_colors(self) -> None:
        """Test pure color conversions."""
        # Red
        result = hsl_to_rgb(0, 100, 50)
        assert result["r"] == 255
        assert result["g"] == 0
        assert result["b"] == 0

        # Green
        result = hsl_to_rgb(120, 100, 50)
        assert result["r"] == 0
        assert result["g"] == 255
        assert result["b"] == 0

        # Blue
        result = hsl_to_rgb(240, 100, 50)
        assert result["r"] == 0
        assert result["g"] == 0
        assert result["b"] == 255

    def test_grayscale(self) -> None:
        """Test grayscale (no saturation)."""
        result = hsl_to_rgb(0, 0, 50)
        assert result["r"] == result["g"] == result["b"]
        assert 127 <= result["r"] <= 128  # Allow rounding

    def test_roundtrip(self) -> None:
        """Test RGB -> HSL -> RGB roundtrip."""
        original = (128, 64, 192)
        hsl = rgb_to_hsl(*original)
        result = hsl_to_rgb(hsl["h"], hsl["s"], hsl["l"])

        # Allow small rounding differences
        assert abs(result["r"] - original[0]) <= 1
        assert abs(result["g"] - original[1]) <= 1
        assert abs(result["b"] - original[2]) <= 1

    def test_invalid_type(self) -> None:
        """Test with invalid types."""
        with pytest.raises(BasicAgentToolsError, match="HSL values must be integers"):
            hsl_to_rgb(11.5, 100, 60)  # type: ignore[arg-type]

    def test_out_of_range(self) -> None:
        """Test with out of range values."""
        with pytest.raises(BasicAgentToolsError, match="Hue must be between 0 and 360"):
            hsl_to_rgb(361, 100, 60)

        with pytest.raises(
            BasicAgentToolsError,
            match="Saturation and Lightness must be between 0 and 100",
        ):
            hsl_to_rgb(11, 101, 60)


class TestRgbToCmyk:
    """Test RGB to CMYK conversion."""

    def test_basic_conversion(self) -> None:
        """Test basic RGB to CMYK conversion."""
        result = rgb_to_cmyk(255, 87, 51)
        assert result["c"] == 0
        assert result["m"] == 66
        assert result["y"] == 80
        assert result["k"] == 0

    def test_black(self) -> None:
        """Test black color."""
        result = rgb_to_cmyk(0, 0, 0)
        assert result["c"] == 0
        assert result["m"] == 0
        assert result["y"] == 0
        assert result["k"] == 100

    def test_white(self) -> None:
        """Test white color."""
        result = rgb_to_cmyk(255, 255, 255)
        assert result["c"] == 0
        assert result["m"] == 0
        assert result["y"] == 0
        assert result["k"] == 0

    def test_pure_colors(self) -> None:
        """Test pure colors."""
        # Pure cyan (subtract red from white)
        result = rgb_to_cmyk(0, 255, 255)
        assert result["c"] == 100
        assert result["m"] == 0
        assert result["y"] == 0

        # Pure magenta
        result = rgb_to_cmyk(255, 0, 255)
        assert result["c"] == 0
        assert result["m"] == 100
        assert result["y"] == 0

        # Pure yellow
        result = rgb_to_cmyk(255, 255, 0)
        assert result["c"] == 0
        assert result["m"] == 0
        assert result["y"] == 100

    def test_invalid_type(self) -> None:
        """Test with invalid types."""
        with pytest.raises(BasicAgentToolsError, match="RGB values must be integers"):
            rgb_to_cmyk(255.5, 87, 51)  # type: ignore[arg-type]

    def test_out_of_range(self) -> None:
        """Test with out of range values."""
        with pytest.raises(
            BasicAgentToolsError, match="RGB values must be between 0 and 255"
        ):
            rgb_to_cmyk(256, 87, 51)


class TestCmykToRgb:
    """Test CMYK to RGB conversion."""

    def test_basic_conversion(self) -> None:
        """Test basic CMYK to RGB conversion."""
        result = cmyk_to_rgb(0, 66, 80, 0)
        assert result["r"] == 255
        assert result["g"] == 87
        assert result["b"] == 51

    def test_black(self) -> None:
        """Test black color."""
        result = cmyk_to_rgb(0, 0, 0, 100)
        assert result["r"] == 0
        assert result["g"] == 0
        assert result["b"] == 0

    def test_white(self) -> None:
        """Test white color."""
        result = cmyk_to_rgb(0, 0, 0, 0)
        assert result["r"] == 255
        assert result["g"] == 255
        assert result["b"] == 255

    def test_roundtrip(self) -> None:
        """Test RGB -> CMYK -> RGB roundtrip."""
        original = (128, 64, 192)
        cmyk = rgb_to_cmyk(*original)
        result = cmyk_to_rgb(cmyk["c"], cmyk["m"], cmyk["y"], cmyk["k"])

        # Allow small rounding differences
        assert abs(result["r"] - original[0]) <= 1
        assert abs(result["g"] - original[1]) <= 1
        assert abs(result["b"] - original[2]) <= 1

    def test_invalid_type(self) -> None:
        """Test with invalid types."""
        with pytest.raises(BasicAgentToolsError, match="CMYK values must be integers"):
            cmyk_to_rgb(0.5, 66, 80, 0)  # type: ignore[arg-type]

    def test_out_of_range(self) -> None:
        """Test with out of range values."""
        with pytest.raises(
            BasicAgentToolsError, match="CMYK values must be between 0 and 100"
        ):
            cmyk_to_rgb(101, 66, 80, 0)
