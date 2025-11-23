"""
Tile rendering for Monopoly board visualization.

Handles rendering of individual tiles including properties, special tiles,
railroads, and utilities.
"""

from typing import Optional, Tuple
import pygame
from engine.state import TileInfo, TileType, PropertyGroup
from visualization.colors import (
    get_property_color, TILE_BACKGROUND, TILE_BORDER, TEXT_COLOR,
    GO_COLOR, JAIL_COLOR, FREE_PARKING_COLOR, GO_TO_JAIL_COLOR,
    CHANCE_COLOR, COMMUNITY_CHEST_COLOR, TAX_COLOR, MORTGAGE_OVERLAY
)
from visualization.board_layout import TilePosition


class TileRenderer:
    """
    Renders individual Monopoly tiles.

    Handles different tile types with appropriate colors, labels,
    and visual styling.
    """

    def __init__(self, font_size: int = 10, corner_font_size: int = 14):
        """
        Initialize tile renderer.

        Args:
            font_size: Font size for regular tiles
            corner_font_size: Font size for corner tiles
        """
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", font_size, bold=True)
        self.small_font = pygame.font.SysFont("Arial", font_size - 2)
        self.corner_font = pygame.font.SysFont("Arial", corner_font_size, bold=True)

    def render_tile(
        self,
        surface: pygame.Surface,
        tile_info: TileInfo,
        position: TilePosition,
        is_mortgaged: bool = False,
        owner_id: Optional[int] = None,
        num_houses: int = 0
    ) -> None:
        """
        Render a single tile.

        Args:
            surface: Pygame surface to draw on
            tile_info: Tile information
            position: Tile position and dimensions
            is_mortgaged: Whether the property is mortgaged
            owner_id: ID of owning player (None if unowned)
            num_houses: Number of houses (0-4) or 5 for hotel
        """
        rect = pygame.Rect(position.x, position.y, position.width, position.height)

        # Draw based on tile type
        if tile_info.tile_type == TileType.GO:
            self._render_go(surface, rect)
        elif tile_info.tile_type == TileType.JAIL:
            self._render_jail(surface, rect)
        elif tile_info.tile_type == TileType.FREE_PARKING:
            self._render_free_parking(surface, rect)
        elif tile_info.tile_type == TileType.GOTO_JAIL:
            self._render_goto_jail(surface, rect)
        elif tile_info.tile_type == TileType.PROPERTY:
            self._render_property(surface, rect, tile_info, position.side, is_mortgaged)
        elif tile_info.tile_type == TileType.RAILROAD:
            self._render_railroad(surface, rect, tile_info, position.side, is_mortgaged)
        elif tile_info.tile_type == TileType.UTILITY:
            self._render_utility(surface, rect, tile_info, position.side, is_mortgaged)
        elif tile_info.tile_type == TileType.CHANCE:
            self._render_chance(surface, rect, position.side)
        elif tile_info.tile_type == TileType.COMMUNITY_CHEST:
            self._render_community_chest(surface, rect, position.side)
        elif tile_info.tile_type == TileType.TAX:
            self._render_tax(surface, rect, tile_info, position.side)

        # Draw mortgage overlay if mortgaged
        if is_mortgaged:
            self._draw_mortgage_overlay(surface, rect)

    def _render_go(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Render GO corner tile."""
        pygame.draw.rect(surface, GO_COLOR, rect)
        pygame.draw.rect(surface, TILE_BORDER, rect, 2)

        # Draw arrow and text
        text = self.corner_font.render("GO", True, TEXT_COLOR)
        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)

        # Draw "Collect $200"
        subtext = self.small_font.render("Collect", True, TEXT_COLOR)
        subtext_rect = subtext.get_rect(center=(rect.centerx, rect.centery + 20))
        surface.blit(subtext, subtext_rect)

    def _render_jail(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Render JAIL corner tile."""
        pygame.draw.rect(surface, JAIL_COLOR, rect)
        pygame.draw.rect(surface, TILE_BORDER, rect, 2)

        # Draw bars pattern
        bar_width = 3
        for i in range(0, rect.width, 10):
            pygame.draw.line(
                surface, TILE_BORDER,
                (rect.x + i, rect.y),
                (rect.x + i, rect.y + rect.height),
                bar_width
            )

        text = self.corner_font.render("JAIL", True, TEXT_COLOR)
        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)

    def _render_free_parking(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Render FREE PARKING corner tile."""
        pygame.draw.rect(surface, FREE_PARKING_COLOR, rect)
        pygame.draw.rect(surface, TILE_BORDER, rect, 2)

        text = self.corner_font.render("FREE", True, TEXT_COLOR)
        text_rect = text.get_rect(center=(rect.centerx, rect.centery - 10))
        surface.blit(text, text_rect)

        subtext = self.corner_font.render("PARKING", True, TEXT_COLOR)
        subtext_rect = subtext.get_rect(center=(rect.centerx, rect.centery + 10))
        surface.blit(subtext, subtext_rect)

    def _render_goto_jail(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Render GO TO JAIL corner tile."""
        pygame.draw.rect(surface, GO_TO_JAIL_COLOR, rect)
        pygame.draw.rect(surface, TILE_BORDER, rect, 2)

        text = self.corner_font.render("GO TO", True, TEXT_COLOR)
        text_rect = text.get_rect(center=(rect.centerx, rect.centery - 10))
        surface.blit(text, text_rect)

        subtext = self.corner_font.render("JAIL", True, TEXT_COLOR)
        subtext_rect = subtext.get_rect(center=(rect.centerx, rect.centery + 10))
        surface.blit(subtext, subtext_rect)

    def _render_property(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        tile_info: TileInfo,
        side: str,
        is_mortgaged: bool
    ) -> None:
        """Render a property tile."""
        # Background
        pygame.draw.rect(surface, TILE_BACKGROUND, rect)
        pygame.draw.rect(surface, TILE_BORDER, rect, 2)

        if tile_info.property_info:
            # Color bar
            color = get_property_color(tile_info.property_info.group)
            color_bar_height = 20

            if side == "bottom":
                color_rect = pygame.Rect(rect.x, rect.y, rect.width, color_bar_height)
            elif side == "top":
                color_rect = pygame.Rect(rect.x, rect.y + rect.height - color_bar_height,
                                        rect.width, color_bar_height)
            elif side == "left":
                color_rect = pygame.Rect(rect.x + rect.width - color_bar_height, rect.y,
                                        color_bar_height, rect.height)
            else:  # right
                color_rect = pygame.Rect(rect.x, rect.y, color_bar_height, rect.height)

            pygame.draw.rect(surface, color, color_rect)

            # Property name (shortened if too long)
            name = tile_info.name
            if len(name) > 15:
                name = name[:12] + "..."

            text = self.font.render(name, True, TEXT_COLOR)

            # Rotate text for vertical sides
            if side in ["left", "right"]:
                text = pygame.transform.rotate(text, 90 if side == "left" else -90)

            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)

    def _render_railroad(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        tile_info: TileInfo,
        side: str,
        is_mortgaged: bool
    ) -> None:
        """Render a railroad tile."""
        pygame.draw.rect(surface, TILE_BACKGROUND, rect)
        pygame.draw.rect(surface, TILE_BORDER, rect, 2)

        # Draw railroad icon (simple tracks)
        center_x, center_y = rect.center

        # Property name
        name = tile_info.name
        if len(name) > 15:
            name = name[:12] + "..."

        text = self.font.render(name, True, TEXT_COLOR)

        # Rotate text for vertical sides
        if side in ["left", "right"]:
            text = pygame.transform.rotate(text, 90 if side == "left" else -90)

        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)

    def _render_utility(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        tile_info: TileInfo,
        side: str,
        is_mortgaged: bool
    ) -> None:
        """Render a utility tile."""
        pygame.draw.rect(surface, TILE_BACKGROUND, rect)
        pygame.draw.rect(surface, TILE_BORDER, rect, 2)

        # Property name
        name = tile_info.name
        if len(name) > 15:
            name = name[:12] + "..."

        text = self.font.render(name, True, TEXT_COLOR)

        # Rotate text for vertical sides
        if side in ["left", "right"]:
            text = pygame.transform.rotate(text, 90 if side == "left" else -90)

        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)

    def _render_chance(self, surface: pygame.Surface, rect: pygame.Rect, side: str) -> None:
        """Render a Chance tile."""
        pygame.draw.rect(surface, CHANCE_COLOR, rect)
        pygame.draw.rect(surface, TILE_BORDER, rect, 2)

        text = self.font.render("?", True, TEXT_COLOR)

        # Rotate text for vertical sides
        if side in ["left", "right"]:
            text = pygame.transform.rotate(text, 90 if side == "left" else -90)

        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)

    def _render_community_chest(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        side: str
    ) -> None:
        """Render a Community Chest tile."""
        pygame.draw.rect(surface, COMMUNITY_CHEST_COLOR, rect)
        pygame.draw.rect(surface, TILE_BORDER, rect, 2)

        text = self.font.render("CC", True, TEXT_COLOR)

        # Rotate text for vertical sides
        if side in ["left", "right"]:
            text = pygame.transform.rotate(text, 90 if side == "left" else -90)

        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)

    def _render_tax(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        tile_info: TileInfo,
        side: str
    ) -> None:
        """Render a tax tile."""
        pygame.draw.rect(surface, TAX_COLOR, rect)
        pygame.draw.rect(surface, TILE_BORDER, rect, 2)

        # Tax name and amount
        name = "TAX"
        if tile_info.tax_amount:
            amount_text = f"${tile_info.tax_amount}"
        else:
            amount_text = ""

        text = self.font.render(name, True, TEXT_COLOR)
        amount = self.small_font.render(amount_text, True, TEXT_COLOR)

        # Rotate text for vertical sides
        if side in ["left", "right"]:
            text = pygame.transform.rotate(text, 90 if side == "left" else -90)
            amount = pygame.transform.rotate(amount, 90 if side == "left" else -90)

        text_rect = text.get_rect(center=(rect.centerx, rect.centery - 8))
        amount_rect = amount.get_rect(center=(rect.centerx, rect.centery + 8))

        surface.blit(text, text_rect)
        surface.blit(amount, amount_rect)

    def _draw_mortgage_overlay(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw semi-transparent overlay for mortgaged properties."""
        overlay = pygame.Surface((rect.width, rect.height))
        overlay.set_alpha(128)
        overlay.fill(MORTGAGE_OVERLAY)
        surface.blit(overlay, (rect.x, rect.y))

        # Draw "MORTGAGED" text
        text = self.small_font.render("M", True, (255, 255, 255))
        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)
