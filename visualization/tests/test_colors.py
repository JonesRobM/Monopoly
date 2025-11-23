"""
Tests for color utilities.

Verifies color mappings and utility functions.
"""

import pytest
from engine.state import PropertyGroup
from visualization.colors import (
    get_property_color, get_player_color,
    PROPERTY_COLORS, PLAYER_COLORS
)


class TestColors:
    """Tests for color utilities."""

    def test_property_colors_all_groups(self):
        """Test all property groups have color mappings."""
        for group in PropertyGroup:
            color = get_property_color(group)
            assert isinstance(color, tuple)
            assert len(color) == 3
            assert all(0 <= c <= 255 for c in color)

    def test_property_colors_dict(self):
        """Test PROPERTY_COLORS dictionary is complete."""
        assert len(PROPERTY_COLORS) == len(PropertyGroup)

        for group in PropertyGroup:
            assert group in PROPERTY_COLORS

    def test_player_colors_valid(self):
        """Test player colors are valid RGB tuples."""
        for color in PLAYER_COLORS:
            assert isinstance(color, tuple)
            assert len(color) == 3
            assert all(0 <= c <= 255 for c in color)

    def test_player_colors_distinct(self):
        """Test player colors are all different."""
        assert len(PLAYER_COLORS) == len(set(PLAYER_COLORS))

    def test_get_player_color_valid(self):
        """Test get_player_color for valid player IDs."""
        for i in range(6):
            color = get_player_color(i)
            assert isinstance(color, tuple)
            assert len(color) == 3
            assert all(0 <= c <= 255 for c in color)

    def test_get_player_color_out_of_range(self):
        """Test get_player_color for player ID > 5 returns fallback."""
        color = get_player_color(10)
        assert isinstance(color, tuple)
        assert len(color) == 3
        assert color == (128, 128, 128)  # Fallback gray

    def test_colors_are_tuples(self):
        """Test all color constants are tuples (not lists)."""
        # This ensures compatibility with pygame
        for group, color in PROPERTY_COLORS.items():
            assert isinstance(color, tuple)

        for color in PLAYER_COLORS:
            assert isinstance(color, tuple)
