"""
Board layout calculator for Monopoly visualization.

Calculates positions and dimensions for all tiles in a square board layout.
Supports both 40-tile classic and 41-tile custom boards.
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict
import math


@dataclass(frozen=True)
class TilePosition:
    """Position and dimensions of a tile on the rendered board."""
    tile_id: int
    x: int
    y: int
    width: int
    height: int
    side: str  # "bottom", "left", "top", "right"
    is_corner: bool


class BoardLayout:
    """
    Calculates layout for square Monopoly board.

    The board is arranged in a square with tiles along the edges.
    Corner tiles are larger than edge tiles.

    Layout for 40 tiles (classic):
    - Bottom: tiles 0-10 (11 tiles including corners)
    - Left: tiles 11-19 (9 tiles, corners not counted)
    - Top: tiles 20-30 (11 tiles including corners)
    - Right: tiles 31-39 (9 tiles, corners not counted)

    Layout for 41 tiles (custom):
    - Bottom: tiles 0-10 (11 tiles)
    - Left: tiles 11-20 (10 tiles)
    - Top: tiles 21-31 (11 tiles)
    - Right: tiles 32-40 (9 tiles)
    """

    def __init__(self, num_tiles: int, board_size: int = 800):
        """
        Initialize board layout calculator.

        Args:
            num_tiles: Total number of tiles (40 or 41)
            board_size: Size of the board in pixels (square) - IGNORED, uses fixed dimensions
        """
        if num_tiles not in [40, 41]:
            raise ValueError(f"Unsupported number of tiles: {num_tiles}. Must be 40 or 41.")

        self.num_tiles = num_tiles

        # Fixed tile dimensions for 2:1 aspect ratio that fits on screen
        # Board will be 1320×1320 pixels (easily visible)
        self.corner_size = 120  # Corner tiles: 120×120px (square)
        self.edge_tile_long = 120  # Long dimension: 120px
        self.edge_tile_short = 60  # Short dimension: 60px (2:1 ratio)

        # For horizontal tiles: width=120, height=60 (2:1 ratio)
        # For vertical tiles: width=60, height=120 (2:1 ratio)
        self.edge_tile_width = self.edge_tile_long
        self.edge_tile_height = self.edge_tile_short

        # Calculate actual board size based on fixed dimensions
        self.tiles_per_side = self._calculate_tiles_per_side()
        # Board size = corner + (9 edge tiles × edge_tile_long) + corner
        self.board_size = self.corner_size + (9 * self.edge_tile_long) + self.corner_size

        # Calculate all tile positions
        self.tile_positions = self._calculate_tile_positions()

    def _calculate_tiles_per_side(self) -> Dict[str, int]:
        """Calculate number of tiles on each side."""
        if self.num_tiles == 40:
            # Classic layout: 11, 9, 11, 9
            return {
                "bottom": 11,
                "left": 9,
                "top": 11,
                "right": 9
            }
        else:  # 41 tiles
            # Custom layout: distribute evenly
            return {
                "bottom": 11,
                "left": 10,
                "top": 11,
                "right": 9
            }


    def _calculate_tile_positions(self) -> Dict[int, TilePosition]:
        """Calculate positions for all tiles."""
        positions: Dict[int, TilePosition] = {}
        current_tile = 0

        # Bottom edge (right to left, starting from GO at bottom-right)
        x = self.board_size - self.corner_size
        y = self.board_size - self.corner_size

        # Tile 0: GO (bottom-right corner)
        positions[0] = TilePosition(
            tile_id=0,
            x=x,
            y=y,
            width=self.corner_size,
            height=self.corner_size,
            side="bottom",
            is_corner=True
        )
        current_tile = 1

        # Bottom edge tiles (moving left)
        # Horizontal tiles: wide rectangles (1024px wide × 256px tall)
        x = self.board_size - self.corner_size - self.edge_tile_long
        y_bottom_edge = self.board_size - self.edge_tile_short
        for i in range(self.tiles_per_side["bottom"] - 2):
            positions[current_tile] = TilePosition(
                tile_id=current_tile,
                x=x,
                y=y_bottom_edge,
                width=self.edge_tile_long,  # 1024px
                height=self.edge_tile_short,  # 256px
                side="bottom",
                is_corner=False
            )
            current_tile += 1
            x -= self.edge_tile_long

        # Tile 10 (or bottom-left corner): Jail
        positions[current_tile] = TilePosition(
            tile_id=current_tile,
            x=0,
            y=self.board_size - self.corner_size,
            width=self.corner_size,
            height=self.corner_size,
            side="bottom",
            is_corner=True
        )
        current_tile += 1

        # Left edge tiles (moving up)
        # Vertical tiles: tall rectangles (256px wide × 1024px tall)
        x_left_edge = 0
        y = self.board_size - self.corner_size - self.edge_tile_long
        for i in range(self.tiles_per_side["left"]):
            positions[current_tile] = TilePosition(
                tile_id=current_tile,
                x=x_left_edge,
                y=y,
                width=self.edge_tile_short,  # 256px
                height=self.edge_tile_long,  # 1024px
                side="left",
                is_corner=False
            )
            current_tile += 1
            y -= self.edge_tile_long

        # Top-left corner: Free Parking
        positions[current_tile] = TilePosition(
            tile_id=current_tile,
            x=0,
            y=0,
            width=self.corner_size,
            height=self.corner_size,
            side="top",
            is_corner=True
        )
        current_tile += 1

        # Top edge tiles (moving right)
        # Horizontal tiles: wide rectangles (1024px wide × 256px tall)
        x = self.corner_size
        y_top_edge = 0
        for i in range(self.tiles_per_side["top"] - 2):
            positions[current_tile] = TilePosition(
                tile_id=current_tile,
                x=x,
                y=y_top_edge,
                width=self.edge_tile_long,  # 1024px
                height=self.edge_tile_short,  # 256px
                side="top",
                is_corner=False
            )
            current_tile += 1
            x += self.edge_tile_long

        # Top-right corner: Go To Jail
        positions[current_tile] = TilePosition(
            tile_id=current_tile,
            x=self.board_size - self.corner_size,
            y=0,
            width=self.corner_size,
            height=self.corner_size,
            side="top",
            is_corner=True
        )
        current_tile += 1

        # Right edge tiles (moving down)
        # Vertical tiles: tall rectangles (256px wide × 1024px tall)
        x_right_edge = self.board_size - self.edge_tile_short
        y = self.corner_size
        for i in range(self.tiles_per_side["right"]):
            positions[current_tile] = TilePosition(
                tile_id=current_tile,
                x=x_right_edge,
                y=y,
                width=self.edge_tile_short,  # 256px
                height=self.edge_tile_long,  # 1024px
                side="right",
                is_corner=False
            )
            current_tile += 1
            y += self.edge_tile_long

        return positions

    def get_tile_position(self, tile_id: int) -> TilePosition:
        """
        Get position information for a tile.

        Args:
            tile_id: Tile ID

        Returns:
            TilePosition object with coordinates and dimensions
        """
        if tile_id not in self.tile_positions:
            raise ValueError(f"Invalid tile ID: {tile_id}")
        return self.tile_positions[tile_id]

    def get_tile_center(self, tile_id: int) -> Tuple[int, int]:
        """
        Get center coordinates of a tile.

        Args:
            tile_id: Tile ID

        Returns:
            Tuple of (x, y) center coordinates
        """
        pos = self.get_tile_position(tile_id)
        center_x = pos.x + pos.width // 2
        center_y = pos.y + pos.height // 2
        return center_x, center_y

    def get_player_offset(self, tile_id: int, player_idx: int, num_players: int) -> Tuple[int, int]:
        """
        Get offset for a player piece on a tile.

        When multiple players are on the same tile, they need to be
        positioned slightly differently to be visible.

        Args:
            tile_id: Tile ID
            player_idx: Player index (0-5)
            num_players: Total number of players on this tile

        Returns:
            Tuple of (offset_x, offset_y) from tile center
        """
        if num_players == 1:
            return (0, 0)

        # Arrange players in a small circle around the tile center
        angle = (2 * math.pi * player_idx) / num_players
        radius = 15  # pixels from center

        offset_x = int(radius * math.cos(angle))
        offset_y = int(radius * math.sin(angle))

        return offset_x, offset_y

    def get_center_area(self) -> Tuple[int, int, int, int]:
        """
        Get the center area of the board (where the board name/logo goes).

        Returns:
            Tuple of (x, y, width, height)
        """
        x = self.corner_size
        y = self.corner_size
        width = self.board_size - 2 * self.corner_size
        height = self.board_size - 2 * self.corner_size

        return x, y, width, height
