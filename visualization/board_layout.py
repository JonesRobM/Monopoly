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
            board_size: Size of the board in pixels (square)
        """
        if num_tiles not in [40, 41]:
            raise ValueError(f"Unsupported number of tiles: {num_tiles}. Must be 40 or 41.")

        self.num_tiles = num_tiles
        self.board_size = board_size

        # Calculate tile dimensions
        # Corner tiles are square, edge tiles are rectangular
        self.tiles_per_side = self._calculate_tiles_per_side()
        self.corner_size = self._calculate_corner_size()
        self.edge_tile_width, self.edge_tile_height = self._calculate_edge_tile_size()

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

    def _calculate_corner_size(self) -> int:
        """Calculate size of corner tiles (square)."""
        # Corner tiles are about 1.5x the width of edge tiles
        # We'll use 12% of board size for corners
        return int(self.board_size * 0.12)

    def _calculate_edge_tile_size(self) -> Tuple[int, int]:
        """Calculate dimensions of edge tiles."""
        # Available space after corners
        available_space = self.board_size - (2 * self.corner_size)

        # Width of tiles on top/bottom edges
        # Subtract 2 for corners, divide by remaining tiles
        bottom_tiles = self.tiles_per_side["bottom"] - 2
        edge_width = available_space // bottom_tiles if bottom_tiles > 0 else 0

        # Height of tiles on left/right edges
        left_tiles = self.tiles_per_side["left"]
        edge_height = available_space // left_tiles if left_tiles > 0 else 0

        return edge_width, edge_height

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
        x = self.board_size - self.corner_size - self.edge_tile_width
        for i in range(self.tiles_per_side["bottom"] - 2):
            positions[current_tile] = TilePosition(
                tile_id=current_tile,
                x=x,
                y=y,
                width=self.edge_tile_width,
                height=self.corner_size,
                side="bottom",
                is_corner=False
            )
            current_tile += 1
            x -= self.edge_tile_width

        # Tile 10 (or bottom-left corner): Jail
        positions[current_tile] = TilePosition(
            tile_id=current_tile,
            x=0,
            y=y,
            width=self.corner_size,
            height=self.corner_size,
            side="bottom",
            is_corner=True
        )
        current_tile += 1

        # Left edge tiles (moving up)
        x = 0
        y = self.board_size - self.corner_size - self.edge_tile_height
        for i in range(self.tiles_per_side["left"]):
            positions[current_tile] = TilePosition(
                tile_id=current_tile,
                x=x,
                y=y,
                width=self.corner_size,
                height=self.edge_tile_height,
                side="left",
                is_corner=False
            )
            current_tile += 1
            y -= self.edge_tile_height

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
        x = self.corner_size
        y = 0
        for i in range(self.tiles_per_side["top"] - 2):
            positions[current_tile] = TilePosition(
                tile_id=current_tile,
                x=x,
                y=y,
                width=self.edge_tile_width,
                height=self.corner_size,
                side="top",
                is_corner=False
            )
            current_tile += 1
            x += self.edge_tile_width

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
        x = self.board_size - self.corner_size
        y = self.corner_size
        for i in range(self.tiles_per_side["right"]):
            positions[current_tile] = TilePosition(
                tile_id=current_tile,
                x=x,
                y=y,
                width=self.corner_size,
                height=self.edge_tile_height,
                side="right",
                is_corner=False
            )
            current_tile += 1
            y += self.edge_tile_height

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
