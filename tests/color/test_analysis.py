"""Tests for color analysis functions."""

import pytest

from basic_open_agent_tools.color.analysis import (
    calculate_contrast_ratio,
    calculate_luminance,
    check_wcag_compliance,
    get_complementary_color,
)
from basic_open_agent_tools.exceptions import BasicAgentToolsError


class TestCalculateLuminance:
    """Test luminance calculation."""

    def test_white(self) -> None:
        """Test white has maximum luminance."""
        lum = calculate_luminance(255, 255, 255)
        assert lum == pytest.approx(1.0, abs=0.01)

    def test_black(self) -> None:
        """Test black has minimum luminance."""
        lum = calculate_luminance(0, 0, 0)
        assert lum == pytest.approx(0.0, abs=0.01)

    def test_gray(self) -> None:
        """Test gray has intermediate luminance."""
        lum = calculate_luminance(128, 128, 128)
        assert 0.2 < lum < 0.3  # Gray is darker than you'd think

    def test_various_colors(self) -> None:
        """Test various color luminances."""
        # Red, green, blue have different perceptual luminance
        red_lum = calculate_luminance(255, 0, 0)
        green_lum = calculate_luminance(0, 255, 0)
        blue_lum = calculate_luminance(0, 0, 255)

        # Green appears brightest to human eye
        assert green_lum > red_lum
        assert green_lum > blue_lum

    def test_invalid_type(self) -> None:
        """Test with invalid types."""
        with pytest.raises(BasicAgentToolsError, match="RGB values must be integers"):
            calculate_luminance(255.5, 255, 255)  # type: ignore[arg-type]

    def test_out_of_range(self) -> None:
        """Test with out of range values."""
        with pytest.raises(
            BasicAgentToolsError, match="RGB values must be between 0 and 255"
        ):
            calculate_luminance(256, 255, 255)


class TestCalculateContrastRatio:
    """Test contrast ratio calculation."""

    def test_maximum_contrast(self) -> None:
        """Test black and white has maximum contrast."""
        result = calculate_contrast_ratio("#000000", "#FFFFFF")
        assert result["contrast_ratio"] == pytest.approx(21.0, abs=0.1)
        assert result["wcag_rating"] == "AAA"

    def test_reverse_order(self) -> None:
        """Test that order doesn't matter."""
        result1 = calculate_contrast_ratio("#000000", "#FFFFFF")
        result2 = calculate_contrast_ratio("#FFFFFF", "#000000")
        assert result1["contrast_ratio"] == result2["contrast_ratio"]

    def test_same_color(self) -> None:
        """Test same color has minimum contrast."""
        result = calculate_contrast_ratio("#808080", "#808080")
        assert result["contrast_ratio"] == pytest.approx(1.0, abs=0.1)
        assert result["wcag_rating"] == "Fail"

    def test_wcag_ratings(self) -> None:
        """Test WCAG rating classifications."""
        # AAA: >= 7.0
        result = calculate_contrast_ratio("#000000", "#FFFFFF")
        assert result["wcag_rating"] == "AAA"

        # AA: >= 4.5
        result = calculate_contrast_ratio("#767676", "#FFFFFF")
        assert result["wcag_rating"] in ["AA", "AAA"]

        # Fail: < 3.0
        result = calculate_contrast_ratio("#CCCCCC", "#FFFFFF")
        assert result["wcag_rating"] in ["Fail", "AA Large"]

    def test_with_and_without_hash(self) -> None:
        """Test hex codes work with and without #."""
        result1 = calculate_contrast_ratio("#FF5733", "#FFFFFF")
        result2 = calculate_contrast_ratio("FF5733", "FFFFFF")
        assert result1["contrast_ratio"] == result2["contrast_ratio"]

    def test_invalid_type(self) -> None:
        """Test with invalid types."""
        with pytest.raises(BasicAgentToolsError, match="Colors must be hex strings"):
            calculate_contrast_ratio(123, "#FFFFFF")  # type: ignore[arg-type]

    def test_invalid_hex(self) -> None:
        """Test with invalid hex format."""
        with pytest.raises(BasicAgentToolsError, match="Invalid color format"):
            calculate_contrast_ratio("#GGGGGG", "#FFFFFF")


class TestCheckWcagCompliance:
    """Test WCAG compliance checking."""

    def test_aaa_pass(self) -> None:
        """Test passing AAA standard."""
        result = check_wcag_compliance("#000000", "#FFFFFF", "AAA")
        assert result["passes"] is True
        assert result["contrast_ratio"] >= 7.0
        assert result["required_ratio"] == 7.0
        assert "passes AAA standards" in result["recommendation"]

    def test_aa_pass(self) -> None:
        """Test passing AA standard."""
        result = check_wcag_compliance("#767676", "#FFFFFF", "AA")
        assert result["passes"] is True
        assert result["required_ratio"] == 4.5

    def test_aa_large_pass(self) -> None:
        """Test passing AA Large standard."""
        result = check_wcag_compliance("#959595", "#FFFFFF", "AA_LARGE")
        assert result["passes"] is True
        assert result["required_ratio"] == 3.0

    def test_fail(self) -> None:
        """Test failing standards."""
        result = check_wcag_compliance("#CCCCCC", "#FFFFFF", "AA")
        assert result["passes"] is False
        assert "below" in result["recommendation"]
        assert "Increase contrast" in result["recommendation"]

    def test_level_normalization(self) -> None:
        """Test level string normalization."""
        # Accepts various formats
        result1 = check_wcag_compliance("#000000", "#FFFFFF", "aa")
        result2 = check_wcag_compliance("#000000", "#FFFFFF", "AA")
        result3 = check_wcag_compliance("#000000", "#FFFFFF", "aa-large")

        assert result1["level"] == "AA"
        assert result2["level"] == "AA"
        assert result3["level"] == "AA_LARGE"

    def test_invalid_type(self) -> None:
        """Test with invalid types."""
        with pytest.raises(
            BasicAgentToolsError,
            match="Foreground and background must be hex strings",
        ):
            check_wcag_compliance(123, "#FFFFFF", "AA")  # type: ignore[arg-type]

        with pytest.raises(BasicAgentToolsError, match="Level must be a string"):
            check_wcag_compliance("#000000", "#FFFFFF", 123)  # type: ignore[arg-type]

    def test_invalid_level(self) -> None:
        """Test with invalid level."""
        with pytest.raises(
            BasicAgentToolsError, match='Level must be "AA", "AAA", or "AA_LARGE"'
        ):
            check_wcag_compliance("#000000", "#FFFFFF", "INVALID")


class TestGetComplementaryColor:
    """Test complementary color calculation."""

    def test_basic_complement(self) -> None:
        """Test basic complementary color."""
        comp = get_complementary_color("#FF5733")
        # Complementary should be 180 degrees opposite
        assert comp.startswith("#")
        assert len(comp) == 7

    def test_red_complement(self) -> None:
        """Test red's complement is cyan."""
        comp = get_complementary_color("#FF0000")
        # Red (0°) complement should be cyan (180°)
        result = comp.upper()
        assert result == "#00FFFF"

    def test_green_complement(self) -> None:
        """Test green's complement is magenta."""
        comp = get_complementary_color("#00FF00")
        # Green (120°) complement should be magenta (300°)
        result = comp.upper()
        assert result == "#FF00FF"

    def test_blue_complement(self) -> None:
        """Test blue's complement is yellow."""
        comp = get_complementary_color("#0000FF")
        # Blue (240°) complement should be yellow (60°)
        result = comp.upper()
        assert result == "#FFFF00"

    def test_roundtrip(self) -> None:
        """Test that complement of complement returns original."""
        original = "#FF5733"
        comp1 = get_complementary_color(original)
        comp2 = get_complementary_color(comp1)

        # Should be very close to original (allow small rounding)
        from basic_open_agent_tools.color.conversion import hex_to_rgb

        orig_rgb = hex_to_rgb(original)
        comp2_rgb = hex_to_rgb(comp2)

        assert abs(orig_rgb["r"] - comp2_rgb["r"]) <= 2
        assert abs(orig_rgb["g"] - comp2_rgb["g"]) <= 2
        assert abs(orig_rgb["b"] - comp2_rgb["b"]) <= 2

    def test_without_hash(self) -> None:
        """Test works without # prefix."""
        comp = get_complementary_color("FF5733")
        assert comp.startswith("#")

    def test_invalid_type(self) -> None:
        """Test with invalid type."""
        with pytest.raises(BasicAgentToolsError, match="Hex color must be a string"):
            get_complementary_color(123456)  # type: ignore[arg-type]

    def test_invalid_hex(self) -> None:
        """Test with invalid hex format."""
        with pytest.raises(BasicAgentToolsError, match="Invalid color format"):
            get_complementary_color("#GGGGGG")
