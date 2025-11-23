"""
Player piece and building rendering for Monopoly visualization.

Handles rendering of player pieces, houses, and hotels on the board.
"""

from typing import List, Dict, Tuple
import pygame
from engine.state import PlayerState, PropertyState
from visualization.colors import (
    get_player_color, HOUSE_COLOR, HOTEL_COLOR, TEXT_COLOR
)
from visualization.board_layout import BoardLayout


class PlayerRenderer:
    """
    Renders player pieces on the board.

    Draws colored circles for players at their current positions,
    with automatic spacing when multiple players are on the same tile.
    """

    def __init__(self, piece_radius: int = 8):
        """
        Initialize player renderer.

        Args:
            piece_radius: Radius of player pieces in pixels
        """
        self.piece_radius = piece_radius
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 10, bold=True)

    def render_players(
        self,
        surface: pygame.Surface,
        players: List[PlayerState],
        layout: BoardLayout
    ) -> None:
        """
        Render all player pieces.

        Args:
            surface: Pygame surface to draw on
            players: List of player states
            layout: Board layout calculator
        """
        # Group players by position
        position_groups: Dict[int, List[PlayerState]] = {}
        for player in players:
            if not player.is_bankrupt:
                pos = player.position
                if pos not in position_groups:
                    position_groups[pos] = []
                position_groups[pos].append(player)

        # Render each group
        for position, players_at_pos in position_groups.items():
            self._render_player_group(surface, players_at_pos, position, layout)

    def _render_player_group(
        self,
        surface: pygame.Surface,
        players: List[PlayerState],
        position: int,
        layout: BoardLayout
    ) -> None:
        """
        Render a group of players on the same tile.

        Args:
            surface: Pygame surface to draw on
            players: Players at this position
            position: Tile position
            layout: Board layout calculator
        """
        tile_center = layout.get_tile_center(position)

        for idx, player in enumerate(players):
            # Get offset for this player
            offset_x, offset_y = layout.get_player_offset(
                position, idx, len(players)
            )

            # Calculate final position
            x = tile_center[0] + offset_x
            y = tile_center[1] + offset_y

            # Draw player piece
            color = get_player_color(player.player_id)
            pygame.draw.circle(surface, color, (x, y), self.piece_radius)
            pygame.draw.circle(surface, (0, 0, 0), (x, y), self.piece_radius, 2)

            # Draw player number on piece
            text = self.font.render(str(player.player_id), True, (255, 255, 255))
            text_rect = text.get_rect(center=(x, y))
            surface.blit(text, text_rect)


class BuildingRenderer:
    """
    Renders houses and hotels on properties.

    Houses are small green rectangles, hotels are larger red rectangles.
    Arranged along the edge of property tiles.
    """

    def __init__(self, house_size: int = 8, hotel_width: int = 12, hotel_height: int = 10):
        """
        Initialize building renderer.

        Args:
            house_size: Size of house squares in pixels
            hotel_width: Width of hotel rectangles
            hotel_height: Height of hotel rectangles
        """
        self.house_size = house_size
        self.hotel_width = hotel_width
        self.hotel_height = hotel_height

    def render_buildings(
        self,
        surface: pygame.Surface,
        tile_id: int,
        num_houses: int,
        layout: BoardLayout
    ) -> None:
        """
        Render houses or hotel on a property.

        Args:
            surface: Pygame surface to draw on
            tile_id: Tile ID of the property
            num_houses: Number of houses (0-4) or 5 for hotel
            layout: Board layout calculator
        """
        if num_houses == 0:
            return

        tile_pos = layout.get_tile_position(tile_id)

        if num_houses == 5:
            # Render hotel
            self._render_hotel(surface, tile_pos)
        else:
            # Render houses
            self._render_houses(surface, tile_pos, num_houses)

    def _render_houses(
        self,
        surface: pygame.Surface,
        tile_pos,
        num_houses: int
    ) -> None:
        """Render individual houses on a property."""
        # Position houses along the color bar edge
        side = tile_pos.side
        spacing = self.house_size + 2

        if side == "bottom":
            # Houses along top edge of tile
            start_x = tile_pos.x + (tile_pos.width - num_houses * spacing) // 2
            y = tile_pos.y + 22

            for i in range(num_houses):
                x = start_x + i * spacing
                pygame.draw.rect(
                    surface,
                    HOUSE_COLOR,
                    (x, y, self.house_size, self.house_size)
                )
                pygame.draw.rect(
                    surface,
                    (0, 0, 0),
                    (x, y, self.house_size, self.house_size),
                    1
                )

        elif side == "top":
            # Houses along bottom edge of tile
            start_x = tile_pos.x + (tile_pos.width - num_houses * spacing) // 2
            y = tile_pos.y + tile_pos.height - 22 - self.house_size

            for i in range(num_houses):
                x = start_x + i * spacing
                pygame.draw.rect(
                    surface,
                    HOUSE_COLOR,
                    (x, y, self.house_size, self.house_size)
                )
                pygame.draw.rect(
                    surface,
                    (0, 0, 0),
                    (x, y, self.house_size, self.house_size),
                    1
                )

        elif side == "left":
            # Houses along right edge of tile
            x = tile_pos.x + tile_pos.width - 22 - self.house_size
            start_y = tile_pos.y + (tile_pos.height - num_houses * spacing) // 2

            for i in range(num_houses):
                y = start_y + i * spacing
                pygame.draw.rect(
                    surface,
                    HOUSE_COLOR,
                    (x, y, self.house_size, self.house_size)
                )
                pygame.draw.rect(
                    surface,
                    (0, 0, 0),
                    (x, y, self.house_size, self.house_size),
                    1
                )

        else:  # right
            # Houses along left edge of tile
            x = tile_pos.x + 22
            start_y = tile_pos.y + (tile_pos.height - num_houses * spacing) // 2

            for i in range(num_houses):
                y = start_y + i * spacing
                pygame.draw.rect(
                    surface,
                    HOUSE_COLOR,
                    (x, y, self.house_size, self.house_size)
                )
                pygame.draw.rect(
                    surface,
                    (0, 0, 0),
                    (x, y, self.house_size, self.house_size),
                    1
                )

    def _render_hotel(self, surface: pygame.Surface, tile_pos) -> None:
        """Render a hotel on a property."""
        side = tile_pos.side

        if side == "bottom":
            x = tile_pos.x + (tile_pos.width - self.hotel_width) // 2
            y = tile_pos.y + 22
            pygame.draw.rect(
                surface,
                HOTEL_COLOR,
                (x, y, self.hotel_width, self.hotel_height)
            )
            pygame.draw.rect(
                surface,
                (0, 0, 0),
                (x, y, self.hotel_width, self.hotel_height),
                1
            )

        elif side == "top":
            x = tile_pos.x + (tile_pos.width - self.hotel_width) // 2
            y = tile_pos.y + tile_pos.height - 22 - self.hotel_height
            pygame.draw.rect(
                surface,
                HOTEL_COLOR,
                (x, y, self.hotel_width, self.hotel_height)
            )
            pygame.draw.rect(
                surface,
                (0, 0, 0),
                (x, y, self.hotel_width, self.hotel_height),
                1
            )

        elif side == "left":
            x = tile_pos.x + tile_pos.width - 22 - self.hotel_height
            y = tile_pos.y + (tile_pos.height - self.hotel_width) // 2
            pygame.draw.rect(
                surface,
                HOTEL_COLOR,
                (x, y, self.hotel_height, self.hotel_width)
            )
            pygame.draw.rect(
                surface,
                (0, 0, 0),
                (x, y, self.hotel_height, self.hotel_width),
                1
            )

        else:  # right
            x = tile_pos.x + 22
            y = tile_pos.y + (tile_pos.height - self.hotel_width) // 2
            pygame.draw.rect(
                surface,
                HOTEL_COLOR,
                (x, y, self.hotel_height, self.hotel_width)
            )
            pygame.draw.rect(
                surface,
                (0, 0, 0),
                (x, y, self.hotel_height, self.hotel_width),
                1
            )


class OwnershipIndicator:
    """
    Renders ownership indicators on properties.

    Shows which player owns each property with a small colored marker.
    """

    def __init__(self, indicator_size: int = 6):
        """
        Initialize ownership indicator renderer.

        Args:
            indicator_size: Size of ownership indicators in pixels
        """
        self.indicator_size = indicator_size

    def render_ownership(
        self,
        surface: pygame.Surface,
        tile_id: int,
        owner_id: int,
        layout: BoardLayout
    ) -> None:
        """
        Render ownership indicator on a property.

        Args:
            surface: Pygame surface to draw on
            tile_id: Tile ID of the property
            owner_id: ID of the owning player
            layout: Board layout calculator
        """
        tile_pos = layout.get_tile_position(tile_id)
        color = get_player_color(owner_id)

        # Position indicator in corner of tile
        side = tile_pos.side

        if side == "bottom":
            x = tile_pos.x + 2
            y = tile_pos.y + 2
        elif side == "top":
            x = tile_pos.x + 2
            y = tile_pos.y + tile_pos.height - self.indicator_size - 2
        elif side == "left":
            x = tile_pos.x + 2
            y = tile_pos.y + 2
        else:  # right
            x = tile_pos.x + tile_pos.width - self.indicator_size - 2
            y = tile_pos.y + 2

        # Draw colored circle
        center_x = x + self.indicator_size // 2
        center_y = y + self.indicator_size // 2
        pygame.draw.circle(surface, color, (center_x, center_y), self.indicator_size // 2)
        pygame.draw.circle(surface, (0, 0, 0), (center_x, center_y), self.indicator_size // 2, 1)
