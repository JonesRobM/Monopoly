"""
Color definitions for Monopoly visualization.

Defines all colors used for properties, UI elements, and player pieces.
Uses RGB tuples compatible with pygame.
"""

from typing import Dict, Tuple
from engine.state import PropertyGroup

# Type alias for RGB color
Color = Tuple[int, int, int]

# Property group colors (brighter, more saturated for cartoony look)
PROPERTY_COLORS: Dict[PropertyGroup, Color] = {
    PropertyGroup.BROWN: (165, 85, 40),        # Brighter brown
    PropertyGroup.LIGHT_BLUE: (100, 200, 255), # More vibrant light blue
    PropertyGroup.PINK: (255, 105, 180),       # Hot pink
    PropertyGroup.PURPLE: (160, 70, 255),      # Brighter purple
    PropertyGroup.ORANGE: (255, 140, 0),       # Vivid orange
    PropertyGroup.RED: (255, 30, 70),          # Bright red
    PropertyGroup.YELLOW: (255, 220, 0),       # Golden yellow
    PropertyGroup.GREEN: (50, 205, 50),        # Lime green
    PropertyGroup.DARK_BLUE: (30, 60, 255),    # Royal blue
    PropertyGroup.RAILROAD: (40, 40, 40),      # Dark gray instead of black
    PropertyGroup.UTILITY: (160, 220, 255),    # Light sky blue
    PropertyGroup.SPECIAL: (255, 180, 255),    # Lavender
}

# Player colors (bright, saturated colors for up to 6 players)
PLAYER_COLORS: list[Color] = [
    (255, 50, 50),    # Bright red
    (50, 100, 255),   # Bright blue
    (50, 220, 50),    # Bright green
    (255, 200, 20),   # Golden yellow
    (255, 50, 255),   # Bright magenta
    (20, 220, 255),   # Bright cyan
]

# UI colors (brighter, more vibrant)
BOARD_BACKGROUND: Color = (245, 250, 235)      # Soft cream
TILE_BACKGROUND: Color = (255, 255, 255)       # Pure white
TILE_BORDER: Color = (30, 30, 30)              # Slightly softer black
TEXT_COLOR: Color = (20, 20, 20)               # Dark gray for better contrast
INFO_PANEL_BG: Color = (250, 250, 250)         # Bright white
INFO_PANEL_BORDER: Color = (120, 120, 120)     # Medium gray

# Special tile colors (more vibrant and playful)
GO_COLOR: Color = (100, 255, 100)              # Bright green (money!)
JAIL_COLOR: Color = (180, 180, 180)            # Medium gray
FREE_PARKING_COLOR: Color = (100, 200, 255)    # Sky blue
GO_TO_JAIL_COLOR: Color = (255, 100, 100)      # Bright red
CHANCE_COLOR: Color = (255, 180, 50)           # Bright orange
COMMUNITY_CHEST_COLOR: Color = (100, 180, 255) # Light blue
TAX_COLOR: Color = (255, 220, 100)             # Yellow (warning color)

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
