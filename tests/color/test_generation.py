"""Tests for color generation functions."""

import pytest

from basic_open_agent_tools.color.conversion import hex_to_rgb, rgb_to_hsl
from basic_open_agent_tools.color.generation import (
    adjust_saturation,
    darken_color,
    generate_palette,
    lighten_color,
)
from basic_open_agent_tools.exceptions import BasicAgentToolsError


class TestLightenColor:
    """Test color lightening."""

    def test_basic_lighten(self) -> None:
        """Test basic lightening."""
        result = lighten_color("#808080", 20)
        # Should be lighter than original
        orig_rgb = hex_to_rgb("#808080")
        new_rgb = hex_to_rgb(result)
        assert new_rgb["r"] >= orig_rgb["r"]
        assert new_rgb["g"] >= orig_rgb["g"]
        assert new_rgb["b"] >= orig_rgb["b"]

    def test_lighten_to_white(self) -> None:
        """Test lightening near-white color."""
        result = lighten_color("#F0F0F0", 50)
        # Should cap at white
        assert result == "#FFFFFF"

    def test_zero_percent(self) -> None:
        """Test zero percent lightening."""
        original = "#FF5733"
        result = lighten_color(original, 0)
        # Should return same color
        orig_rgb = hex_to_rgb(original)
        result_rgb = hex_to_rgb(result)
        assert abs(orig_rgb["r"] - result_rgb["r"]) <= 1
        assert abs(orig_rgb["g"] - result_rgb["g"]) <= 1
        assert abs(orig_rgb["b"] - result_rgb["b"]) <= 1

    def test_without_hash(self) -> None:
        """Test works without # prefix."""
        result = lighten_color("808080", 20)
        assert result.startswith("#")

    def test_invalid_type(self) -> None:
        """Test with invalid types."""
        with pytest.raises(BasicAgentToolsError, match="Hex color must be a string"):
            lighten_color(123456, 20)  # type: ignore[arg-type]

        with pytest.raises(BasicAgentToolsError, match="Percent must be an integer"):
            lighten_color("#808080", 20.5)  # type: ignore[arg-type]

    def test_out_of_range(self) -> None:
        """Test with out of range percent."""
        with pytest.raises(
            BasicAgentToolsError, match="Percent must be between 0 and 100"
        ):
            lighten_color("#808080", 101)

        with pytest.raises(
            BasicAgentToolsError, match="Percent must be between 0 and 100"
        ):
            lighten_color("#808080", -1)


class TestDarkenColor:
    """Test color darkening."""

    def test_basic_darken(self) -> None:
        """Test basic darkening."""
        result = darken_color("#808080", 20)
        # Should be darker than original
        orig_rgb = hex_to_rgb("#808080")
        new_rgb = hex_to_rgb(result)
        assert new_rgb["r"] <= orig_rgb["r"]
        assert new_rgb["g"] <= orig_rgb["g"]
        assert new_rgb["b"] <= orig_rgb["b"]

    def test_darken_to_black(self) -> None:
        """Test darkening near-black color."""
        result = darken_color("#0F0F0F", 50)
        # Should cap at black
        assert result == "#000000"

    def test_zero_percent(self) -> None:
        """Test zero percent darkening."""
        original = "#FF5733"
        result = darken_color(original, 0)
        # Should return same color
        orig_rgb = hex_to_rgb(original)
        result_rgb = hex_to_rgb(result)
        assert abs(orig_rgb["r"] - result_rgb["r"]) <= 1
        assert abs(orig_rgb["g"] - result_rgb["g"]) <= 1
        assert abs(orig_rgb["b"] - result_rgb["b"]) <= 1

    def test_lighten_darken_roundtrip(self) -> None:
        """Test lightening then darkening."""
        original = "#808080"
        lighter = lighten_color(original, 20)
        back = darken_color(lighter, 20)

        orig_rgb = hex_to_rgb(original)
        back_rgb = hex_to_rgb(back)

        # Should be very close (allow small rounding)
        assert abs(orig_rgb["r"] - back_rgb["r"]) <= 2
        assert abs(orig_rgb["g"] - back_rgb["g"]) <= 2
        assert abs(orig_rgb["b"] - back_rgb["b"]) <= 2

    def test_invalid_type(self) -> None:
        """Test with invalid types."""
        with pytest.raises(BasicAgentToolsError, match="Hex color must be a string"):
            darken_color(123456, 20)  # type: ignore[arg-type]

    def test_out_of_range(self) -> None:
        """Test with out of range percent."""
        with pytest.raises(
            BasicAgentToolsError, match="Percent must be between 0 and 100"
        ):
            darken_color("#808080", 101)


class TestAdjustSaturation:
    """Test saturation adjustment."""

    def test_increase_saturation(self) -> None:
        """Test increasing saturation."""
        # Start with muted color
        original = "#808080"
        result = adjust_saturation(original, 50)

        orig_hsl = rgb_to_hsl(*hex_to_rgb(original).values())
        result_hsl = rgb_to_hsl(*hex_to_rgb(result).values())

        # Saturation should increase
        assert result_hsl["s"] >= orig_hsl["s"]

    def test_decrease_saturation(self) -> None:
        """Test decreasing saturation."""
        # Start with vivid color
        original = "#FF0000"
        result = adjust_saturation(original, -50)

        orig_hsl = rgb_to_hsl(*hex_to_rgb(original).values())
        result_hsl = rgb_to_hsl(*hex_to_rgb(result).values())

        # Saturation should decrease
        assert result_hsl["s"] <= orig_hsl["s"]

    def test_zero_saturation(self) -> None:
        """Test removing all saturation."""
        original = "#FF5733"
        result = adjust_saturation(original, -100)

        result_hsl = rgb_to_hsl(*hex_to_rgb(result).values())
        # Should be grayscale
        assert result_hsl["s"] == 0

    def test_maximum_saturation(self) -> None:
        """Test maximum saturation."""
        original = "#808080"
        result = adjust_saturation(original, 100)

        result_hsl = rgb_to_hsl(*hex_to_rgb(result).values())
        # Should be at or near maximum
        assert result_hsl["s"] >= 90

    def test_zero_percent(self) -> None:
        """Test zero percent adjustment."""
        original = "#FF5733"
        result = adjust_saturation(original, 0)

        orig_rgb = hex_to_rgb(original)
        result_rgb = hex_to_rgb(result)

        # Should be same color
        assert abs(orig_rgb["r"] - result_rgb["r"]) <= 1
        assert abs(orig_rgb["g"] - result_rgb["g"]) <= 1
        assert abs(orig_rgb["b"] - result_rgb["b"]) <= 1

    def test_invalid_type(self) -> None:
        """Test with invalid types."""
        with pytest.raises(BasicAgentToolsError, match="Hex color must be a string"):
            adjust_saturation(123456, 50)  # type: ignore[arg-type]

        with pytest.raises(BasicAgentToolsError, match="Percent must be an integer"):
            adjust_saturation("#808080", 50.5)  # type: ignore[arg-type]

    def test_out_of_range(self) -> None:
        """Test with out of range percent."""
        with pytest.raises(
            BasicAgentToolsError, match="Percent must be between -100 and 100"
        ):
            adjust_saturation("#808080", 101)

        with pytest.raises(
            BasicAgentToolsError, match="Percent must be between -100 and 100"
        ):
            adjust_saturation("#808080", -101)


class TestGeneratePalette:
    """Test palette generation."""

    def test_monochromatic(self) -> None:
        """Test monochromatic palette."""
        result = generate_palette("#FF5733", "monochromatic", 5)

        assert result["scheme"] == "monochromatic"
        assert result["count"] == 5
        assert len(result["colors"]) == 5

        # All colors should have same hue
        base_hsl = rgb_to_hsl(*hex_to_rgb("#FF5733").values())

        for color in result["colors"]:
            color_hsl = rgb_to_hsl(*hex_to_rgb(color).values())
            # Allow small hue variation due to rounding
            assert abs(color_hsl["h"] - base_hsl["h"]) <= 5

    def test_analogous(self) -> None:
        """Test analogous palette."""
        result = generate_palette("#FF5733", "analogous", 5)

        assert result["scheme"] == "analogous"
        assert len(result["colors"]) == 5

        # Colors should have similar hues (within ±30 degrees)
        base_hsl = rgb_to_hsl(*hex_to_rgb("#FF5733").values())

        for color in result["colors"]:
            color_hsl = rgb_to_hsl(*hex_to_rgb(color).values())
            hue_diff = abs(color_hsl["h"] - base_hsl["h"])
            # Account for wrap-around
            if hue_diff > 180:
                hue_diff = 360 - hue_diff
            assert hue_diff <= 35  # Allow some margin

    def test_complementary(self) -> None:
        """Test complementary palette."""
        result = generate_palette("#FF5733", "complementary", 4)

        assert result["scheme"] == "complementary"
        assert len(result["colors"]) >= 2

        # Should include base and its complement
        base_hsl = rgb_to_hsl(*hex_to_rgb("#FF5733").values())

        # Check that at least one color is ~180 degrees away
        found_complement = False
        for color in result["colors"]:
            color_hsl = rgb_to_hsl(*hex_to_rgb(color).values())
            hue_diff = abs(color_hsl["h"] - base_hsl["h"])
            if 170 <= hue_diff <= 190:
                found_complement = True
                break

        assert found_complement, "No complementary color found in palette"

    def test_triadic(self) -> None:
        """Test triadic palette."""
        result = generate_palette("#FF5733", "triadic", 6)

        assert result["scheme"] == "triadic"
        assert len(result["colors"]) == 6

        # Should have colors ~120 degrees apart
        hues = []
        for color in result["colors"][:3]:  # First 3 should be the triad
            color_hsl = rgb_to_hsl(*hex_to_rgb(color).values())
            hues.append(color_hsl["h"])

        # Check spacing (allowing for rounding and variations)
        base_hue = hues[0]
        for hue in hues[1:3]:
            diff = abs(hue - base_hue)
            # Should be ~120 or ~240 degrees away
            assert diff >= 100 or diff <= 20  # Account for wrap-around

    def test_split_complementary(self) -> None:
        """Test split complementary palette."""
        result = generate_palette("#FF5733", "split_complementary", 5)

        assert result["scheme"] == "split_complementary"
        assert len(result["colors"]) >= 3

        # Should have base plus two colors near the complement
        base_hsl = rgb_to_hsl(*hex_to_rgb(result["colors"][0]).values())

        # Check for colors near the complement (180° ± 30°)
        near_complement_count = 0
        for color in result["colors"][1:3]:
            color_hsl = rgb_to_hsl(*hex_to_rgb(color).values())
            hue_diff = abs(color_hsl["h"] - base_hsl["h"])
            if hue_diff > 180:
                hue_diff = 360 - hue_diff

            # Should be 150-210 degrees away (180° ± 30°)
            if 140 <= hue_diff <= 220:
                near_complement_count += 1

        assert near_complement_count >= 1, "No split complementary colors found"

    def test_minimum_count(self) -> None:
        """Test minimum palette count."""
        result = generate_palette("#FF5733", "monochromatic", 2)
        assert len(result["colors"]) == 2

    def test_maximum_count(self) -> None:
        """Test maximum palette count."""
        result = generate_palette("#FF5733", "monochromatic", 10)
        assert len(result["colors"]) == 10

    def test_scheme_normalization(self) -> None:
        """Test scheme name normalization."""
        # Should accept hyphenated
        result1 = generate_palette("#FF5733", "split-complementary", 5)
        assert result1["scheme"] == "split_complementary"

        # Should accept underscored
        result2 = generate_palette("#FF5733", "split_complementary", 5)
        assert result2["scheme"] == "split_complementary"

    def test_invalid_type(self) -> None:
        """Test with invalid types."""
        with pytest.raises(BasicAgentToolsError, match="Base color must be a string"):
            generate_palette(123456, "monochromatic", 5)  # type: ignore[arg-type]

        with pytest.raises(BasicAgentToolsError, match="Scheme must be a string"):
            generate_palette("#FF5733", 123, 5)  # type: ignore[arg-type]

        with pytest.raises(BasicAgentToolsError, match="Count must be an integer"):
            generate_palette("#FF5733", "monochromatic", 5.5)  # type: ignore[arg-type]

    def test_invalid_scheme(self) -> None:
        """Test with invalid scheme."""
        with pytest.raises(BasicAgentToolsError, match="Scheme must be one of"):
            generate_palette("#FF5733", "invalid", 5)

    def test_invalid_count(self) -> None:
        """Test with invalid count."""
        with pytest.raises(
            BasicAgentToolsError, match="Count must be between 2 and 10"
        ):
            generate_palette("#FF5733", "monochromatic", 1)

        with pytest.raises(
            BasicAgentToolsError, match="Count must be between 2 and 10"
        ):
            generate_palette("#FF5733", "monochromatic", 11)

    def test_invalid_color_format(self) -> None:
        """Test with invalid color format."""
        with pytest.raises(BasicAgentToolsError, match="Invalid color format"):
            generate_palette("#GGGGGG", "monochromatic", 5)
