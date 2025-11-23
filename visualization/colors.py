"""
Color definitions for Monopoly visualization.

Defines all colors used for properties, UI elements, and player pieces.
Uses RGB tuples compatible with pygame.
"""

from typing import Dict, Tuple
from engine.state import PropertyGroup

# Type alias for RGB color
Color = Tuple[int, int, int]

# Property group colors (matching classic Monopoly)
PROPERTY_COLORS: Dict[PropertyGroup, Color] = {
    PropertyGroup.BROWN: (139, 69, 19),
    PropertyGroup.LIGHT_BLUE: (173, 216, 230),
    PropertyGroup.PINK: (255, 192, 203),
    PropertyGroup.PURPLE: (147, 112, 219),
    PropertyGroup.ORANGE: (255, 165, 0),
    PropertyGroup.RED: (220, 20, 60),
    PropertyGroup.YELLOW: (255, 255, 0),
    PropertyGroup.GREEN: (34, 139, 34),
    PropertyGroup.DARK_BLUE: (0, 0, 139),
    PropertyGroup.RAILROAD: (0, 0, 0),
    PropertyGroup.UTILITY: (200, 200, 200),
    PropertyGroup.SPECIAL: (200, 200, 200),
}

# Player colors (distinct colors for up to 6 players)
PLAYER_COLORS: list[Color] = [
    (255, 0, 0),      # Red
    (0, 0, 255),      # Blue
    (0, 200, 0),      # Green
    (255, 255, 0),    # Yellow
    (255, 0, 255),    # Magenta
    (0, 255, 255),    # Cyan
]

# UI colors
BOARD_BACKGROUND: Color = (240, 240, 220)
TILE_BACKGROUND: Color = (255, 255, 255)
TILE_BORDER: Color = (0, 0, 0)
TEXT_COLOR: Color = (0, 0, 0)
INFO_PANEL_BG: Color = (240, 240, 240)
INFO_PANEL_BORDER: Color = (100, 100, 100)

# Special tile colors
GO_COLOR: Color = (255, 100, 100)
JAIL_COLOR: Color = (200, 200, 200)
FREE_PARKING_COLOR: Color = (150, 200, 150)
GO_TO_JAIL_COLOR: Color = (255, 150, 150)
CHANCE_COLOR: Color = (255, 200, 100)
COMMUNITY_CHEST_COLOR: Color = (150, 200, 255)
TAX_COLOR: Color = (180, 180, 180)

# Building colors
HOUSE_COLOR: Color = (0, 150, 0)
HOTEL_COLOR: Color = (200, 0, 0)

# Mortgage indicator
MORTGAGE_OVERLAY: Color = (100, 100, 100)


def get_property_color(group: PropertyGroup) -> Color:
    """
    Get the display color for a property group.

    Args:
        group: Property group

    Returns:
        RGB color tuple
    """
    return PROPERTY_COLORS.get(group, TILE_BACKGROUND)


def get_player_color(player_id: int) -> Color:
    """
    Get the display color for a player.

    Args:
        player_id: Player ID (0-5)

    Returns:
        RGB color tuple
    """
    if 0 <= player_id < len(PLAYER_COLORS):
        return PLAYER_COLORS[player_id]
    # Fallback for more than 6 players
    return (128, 128, 128)
