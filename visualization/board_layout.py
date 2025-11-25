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

    def __init__(self, num_tiles: int, board_size: int = 888):
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

        # Calculate tile dimensions based on desired board size
        # Base dimensions for 960px board: corner=102x102, edge_long=84px, edge_short=140px
        # Corners: 1:1 aspect ratio (square)
        # Edge tiles: 3:5 aspect ratio (width:height = parallel:perpendicular)
        # Scale factor = board_size / 960
        base_board_size = 888
        scale_factor = board_size / base_board_size

        # Scaled tile dimensions with proper aspect ratios
        self.corner_width = int(120 * scale_factor)  # Corner width (1:1 square)
        self.corner_height = int(120 * scale_factor)  # Corner height (1:1 square)
        self.edge_tile_long = int(72 * scale_factor)  # Long dimension (parallel to flow, 3 parts)
        self.edge_tile_short = int(120 * scale_factor)  # Short dimension (perpendicular, 5 parts, 3:5 ratio)

        # For horizontal tiles: width=long (84), height=short (140), aspect 3:5
        # For vertical tiles: width=short (140), height=long (84), aspect 3:5
        self.edge_tile_width = self.edge_tile_long
        self.edge_tile_height = self.edge_tile_short

        # Verify calculated board size matches target (within rounding)
        self.tiles_per_side = self._calculate_tiles_per_side()
        calculated_size = self.corner_width + (9 * self.edge_tile_long) + self.corner_width

        # Adjust if rounding caused mismatch
        if calculated_size != board_size:
            size_diff = board_size - calculated_size
            # Distribute difference across edge tiles
            self.edge_tile_long += size_diff // 18  # 18 edge tiles (9 per horizontal side)
            self.edge_tile_width = self.edge_tile_long
            self.corner_width += size_diff // 18

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
        x = self.board_size - self.corner_width
        y = self.board_size - self.corner_height

        # Tile 0: GO (bottom-right corner)
        positions[0] = TilePosition(
            tile_id=0,
            x=x,
            y=y,
            width=self.corner_width,
            height=self.corner_height,
            side="bottom",
            is_corner=True
        )
        current_tile = 1

        # Bottom edge tiles (moving left)
        # Horizontal tiles: rectangles (84px wide × 140px tall, 3:5 aspect)
        x = self.board_size - self.corner_width - self.edge_tile_long
        y_bottom_edge = self.board_size - self.edge_tile_short
        for i in range(self.tiles_per_side["bottom"] - 2):
            positions[current_tile] = TilePosition(
                tile_id=current_tile,
                x=x,
                y=y_bottom_edge,
                width=self.edge_tile_long,  # 84px
                height=self.edge_tile_short,  # 140px
                side="bottom",
                is_corner=False
            )
            current_tile += 1
            x -= self.edge_tile_long

        # Tile 10 (or bottom-left corner): Jail
        positions[current_tile] = TilePosition(
            tile_id=current_tile,
            x=0,
            y=self.board_size - self.corner_height,
            width=self.corner_width,
            height=self.corner_height,
            side="bottom",
            is_corner=True
        )
        current_tile += 1

        # Left edge tiles (moving up)
        # Vertical tiles: rectangles (160px wide × 80px tall, 2:1 aspect)
        x_left_edge = 0
        y = self.board_size - self.corner_height - self.edge_tile_long
        for i in range(self.tiles_per_side["left"]):
            positions[current_tile] = TilePosition(
                tile_id=current_tile,
                x=x_left_edge,
                y=y,
                width=self.edge_tile_short,  # 160px
                height=self.edge_tile_long,  # 80px
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
            width=self.corner_width,
            height=self.corner_height,
            side="top",
            is_corner=True
        )
        current_tile += 1

        # Top edge tiles (moving right)
        # Horizontal tiles: rectangles (80px wide × 160px tall, 2:1 aspect)
        x = self.corner_width
        y_top_edge = 0
        for i in range(self.tiles_per_side["top"] - 2):
            positions[current_tile] = TilePosition(
                tile_id=current_tile,
                x=x,
                y=y_top_edge,
                width=self.edge_tile_long,  # 80px
                height=self.edge_tile_short,  # 160px
                side="top",
                is_corner=False
            )
            current_tile += 1
            x += self.edge_tile_long

        # Top-right corner: Go To Jail
        positions[current_tile] = TilePosition(
            tile_id=current_tile,
            x=self.board_size - self.corner_width,
            y=0,
            width=self.corner_width,
            height=self.corner_height,
            side="top",
            is_corner=True
        )
        current_tile += 1

        # Right edge tiles (moving down)
        # Vertical tiles: rectangles (160px wide × 80px tall, 2:1 aspect)
        x_right_edge = self.board_size - self.edge_tile_short
        y = self.corner_height
        for i in range(self.tiles_per_side["right"]):
            positions[current_tile] = TilePosition(
                tile_id=current_tile,
                x=x_right_edge,
                y=y,
                width=self.edge_tile_short,  # 160px
                height=self.edge_tile_long,  # 80px
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
        The center panel is 75% of the available inner space and centered.

        Returns:
            Tuple of (x, y, width, height)
        """
        # Calculate the full inner area
        full_width = self.board_size - 2 * self.corner_width
        full_height = self.board_size - 2 * self.corner_height

        # Reduce to 75% of full size
        width = int(full_width * 0.75)
        height = int(full_height * 0.75)

        # Center the reduced panel
        offset_x = (full_width - width) // 2
        offset_y = (full_height - height) // 2

        x = self.corner_width + offset_x
        y = self.corner_height + offset_y

        return x, y, width, height
