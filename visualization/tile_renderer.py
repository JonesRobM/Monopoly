"""
Tile rendering for Monopoly board visualization.

Handles rendering of individual tiles including properties, special tiles,
railroads, and utilities with a cartoony, poppy visual style.
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
from visualization.text_utils import format_display_name, truncate_name, wrap_text


class TileRenderer:
    """
    Renders individual Monopoly tiles with a modern, cartoony style.

    Features:
    - Rounded corners for a softer look
    - Drop shadows for depth
    - Gradient backgrounds on special tiles
    - Larger, bolder fonts
    - Icon-like symbols for special tiles
    """

    # Border radius for rounded corners (sized for 120×60 tiles)
    BORDER_RADIUS = 8
    CORNER_BORDER_RADIUS = 12

    # Shadow offset for depth effect
    SHADOW_OFFSET = 3

    def __init__(self, font_size: int = 12, corner_font_size: int = 18):
        """
        Initialize tile renderer with cartoonish fonts.

        Args:
            font_size: Font size for regular tiles
            corner_font_size: Font size for corner tiles
        """
        pygame.font.init()
        # Use Comic Sans MS for cartoonish, poppy look
        self.font = pygame.font.SysFont("Comic Sans MS", font_size, bold=True)
        self.small_font = pygame.font.SysFont("Comic Sans MS", font_size - 2, bold=False)
        self.corner_font = pygame.font.SysFont("Comic Sans MS", corner_font_size, bold=True)
        self.icon_font = pygame.font.SysFont("Comic Sans MS", font_size + 4, bold=True)

    def _draw_shadow(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        border_radius: int
    ) -> None:
        """Draw a subtle drop shadow for depth."""
        shadow_rect = rect.copy()
        shadow_rect.x += self.SHADOW_OFFSET
        shadow_rect.y += self.SHADOW_OFFSET

        # Create semi-transparent shadow surface
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            shadow_surface,
            (0, 0, 0, 40),  # Semi-transparent black
            shadow_surface.get_rect(),
            border_radius=border_radius
        )
        surface.blit(shadow_surface, (shadow_rect.x, shadow_rect.y))

    def _draw_rounded_rect(
        self,
        surface: pygame.Surface,
        color: Tuple[int, int, int],
        rect: pygame.Rect,
        border_radius: int,
        border_color: Optional[Tuple[int, int, int]] = None,
        border_width: int = 2
    ) -> None:
        """Draw a rounded rectangle with optional border."""
        # Fill
        pygame.draw.rect(surface, color, rect, border_radius=border_radius)

        # Border
        if border_color:
            pygame.draw.rect(
                surface,
                border_color,
                rect,
                width=border_width,
                border_radius=border_radius
            )

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
        """Render GO corner tile with vibrant styling."""
        # Draw shadow
        self._draw_shadow(surface, rect, self.CORNER_BORDER_RADIUS)

        # Draw rounded background
        self._draw_rounded_rect(
            surface, GO_COLOR, rect,
            self.CORNER_BORDER_RADIUS,
            TILE_BORDER, 3
        )

        # Draw arrow icon
        arrow_text = self.corner_font.render("→", True, TEXT_COLOR)
        arrow_rect = arrow_text.get_rect(center=(rect.centerx, rect.centery - 15))
        surface.blit(arrow_text, arrow_rect)

        # Draw GO text
        text = self.corner_font.render("GO", True, TEXT_COLOR)
        text_rect = text.get_rect(center=(rect.centerx, rect.centery + 10))
        surface.blit(text, text_rect)

        # Draw "Collect $200"
        subtext = self.small_font.render("Collect £200", True, TEXT_COLOR)
        subtext_rect = subtext.get_rect(center=(rect.centerx, rect.centery + 28))
        surface.blit(subtext, subtext_rect)

    def _render_jail(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Render JAIL corner tile - note: this is actually just visiting in standard Monopoly."""
        # Draw shadow
        self._draw_shadow(surface, rect, self.CORNER_BORDER_RADIUS)

        # Draw rounded background
        self._draw_rounded_rect(
            surface, JAIL_COLOR, rect,
            self.CORNER_BORDER_RADIUS,
            TILE_BORDER, 3
        )

        # Draw simple bars in center
        bar_spacing = 8
        bar_width = 3
        num_bars = 5
        start_x = rect.centerx - (num_bars * bar_spacing) // 2

        for i in range(num_bars):
            x = start_x + i * bar_spacing
            pygame.draw.line(
                surface, TILE_BORDER,
                (x, rect.centery - 15),
                (x, rect.centery + 15),
                bar_width
            )

        # Draw "JAIL" text
        text = self.small_font.render("Just", True, TEXT_COLOR)
        text_rect = text.get_rect(center=(rect.centerx, rect.centery - 25))
        surface.blit(text, text_rect)

        text2 = self.corner_font.render("VISITING", True, TEXT_COLOR)
        text2_rect = text2.get_rect(center=(rect.centerx, rect.centery + 25))
        surface.blit(text2, text2_rect)

    def _render_free_parking(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Render FREE PARKING corner tile."""
        # Draw shadow
        self._draw_shadow(surface, rect, self.CORNER_BORDER_RADIUS)

        # Draw rounded background
        self._draw_rounded_rect(
            surface, FREE_PARKING_COLOR, rect,
            self.CORNER_BORDER_RADIUS,
            TILE_BORDER, 3
        )

        # Draw parking "P" icon
        icon = self.corner_font.render("P", True, TEXT_COLOR)
        icon_rect = icon.get_rect(center=(rect.centerx, rect.centery - 12))
        surface.blit(icon, icon_rect)

        # Draw FREE text
        text = self.small_font.render("FREE", True, TEXT_COLOR)
        text_rect = text.get_rect(center=(rect.centerx, rect.centery + 8))
        surface.blit(text, text_rect)

        # Draw PARKING text
        subtext = self.small_font.render("PARKING", True, TEXT_COLOR)
        subtext_rect = subtext.get_rect(center=(rect.centerx, rect.centery + 22))
        surface.blit(subtext, subtext_rect)

    def _render_goto_jail(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Render GO TO JAIL corner tile."""
        # Draw shadow
        self._draw_shadow(surface, rect, self.CORNER_BORDER_RADIUS)

        # Draw rounded background
        self._draw_rounded_rect(
            surface, GO_TO_JAIL_COLOR, rect,
            self.CORNER_BORDER_RADIUS,
            TILE_BORDER, 3
        )

        # Draw warning icon
        icon = self.corner_font.render("!", True, TEXT_COLOR)
        icon_rect = icon.get_rect(center=(rect.centerx, rect.centery - 15))
        surface.blit(icon, icon_rect)

        # Draw GO TO text
        text = self.small_font.render("GO TO", True, TEXT_COLOR)
        text_rect = text.get_rect(center=(rect.centerx, rect.centery + 5))
        surface.blit(text, text_rect)

        # Draw JAIL text
        subtext = self.corner_font.render("JAIL", True, TEXT_COLOR)
        subtext_rect = subtext.get_rect(center=(rect.centerx, rect.centery + 20))
        surface.blit(subtext, subtext_rect)

    def _render_property(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        tile_info: TileInfo,
        side: str,
        is_mortgaged: bool
    ) -> None:
        """Render a property tile with modern styling."""
        # Draw shadow
        self._draw_shadow(surface, rect, self.BORDER_RADIUS)

        # Draw rounded background
        self._draw_rounded_rect(
            surface, TILE_BACKGROUND, rect,
            self.BORDER_RADIUS,
            TILE_BORDER, 2
        )

        if tile_info.property_info:
            # Color bar - prominent and visible
            color = get_property_color(tile_info.property_info.group)
            color_bar_height = 20

            if side == "bottom":
                color_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, color_bar_height)
                # Round only top corners
                pygame.draw.rect(surface, color, color_rect, border_top_left_radius=6, border_top_right_radius=6)
            elif side == "top":
                color_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, color_bar_height)
                # Round only top corners
                pygame.draw.rect(surface, color, color_rect, border_top_left_radius=6, border_top_right_radius=6)
            elif side == "left":
                color_rect = pygame.Rect(rect.x + 2, rect.y + 2, color_bar_height, rect.height - 4)
                # Round only left corners
                pygame.draw.rect(surface, color, color_rect, border_top_left_radius=6, border_bottom_left_radius=6)
            else:  # right
                color_rect = pygame.Rect(rect.x + rect.width - color_bar_height - 2, rect.y + 2,
                                        color_bar_height, rect.height - 4)
                # Round only right corners
                pygame.draw.rect(surface, color, color_rect, border_top_right_radius=6, border_bottom_right_radius=6)

            # Property name with text wrapping
            # Calculate available width for text (leave padding)
            if side in ["bottom", "top"]:
                max_text_width = rect.width - 8
            else:
                max_text_width = rect.height - 8

            # Wrap text to fit
            lines = wrap_text(tile_info.name, max_text_width, self.font)

            # Limit to 2 lines maximum
            if len(lines) > 2:
                lines = lines[:2]
                # Add ellipsis to last line if truncated
                if len(lines[-1]) > 10:
                    lines[-1] = lines[-1][:10] + "..."

            # Render text lines
            line_height = self.font.get_height()
            total_height = len(lines) * line_height
            start_y = rect.centery - total_height // 2

            for i, line in enumerate(lines):
                text = self.font.render(line, True, TEXT_COLOR)

                # Rotate text based on side
                if side == "top":
                    text = pygame.transform.rotate(text, 180)
                elif side in ["left", "right"]:
                    text = pygame.transform.rotate(text, 90 if side == "left" else -90)

                y_pos = start_y + i * line_height
                text_rect = text.get_rect(center=(rect.centerx, y_pos))
                surface.blit(text, text_rect)

    def _render_railroad(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        tile_info: TileInfo,
        side: str,
        is_mortgaged: bool
    ) -> None:
        """Render a railroad tile with modern styling."""
        # Draw shadow
        self._draw_shadow(surface, rect, self.BORDER_RADIUS)

        # Draw rounded background
        self._draw_rounded_rect(
            surface, TILE_BACKGROUND, rect,
            self.BORDER_RADIUS,
            TILE_BORDER, 2
        )

        # Draw railroad icon
        icon = self.icon_font.render("🚉", True, TEXT_COLOR)

        # Calculate available width for text
        if side in ["bottom", "top"]:
            max_text_width = rect.width - 8
        else:
            max_text_width = rect.height - 8

        # Wrap property name
        lines = wrap_text(tile_info.name, max_text_width, self.small_font)

        # Limit to 2 lines
        if len(lines) > 2:
            lines = lines[:2]

        # Rotate icon based on side
        if side == "top":
            icon = pygame.transform.rotate(icon, 180)
        elif side in ["left", "right"]:
            icon = pygame.transform.rotate(icon, 90 if side == "left" else -90)

        # Position icon and text
        if side in ["bottom", "top"]:
            icon_rect = icon.get_rect(center=(rect.centerx, rect.centery - 16))
            surface.blit(icon, icon_rect)

            # Render text lines below icon
            line_height = self.small_font.get_height()
            total_height = len(lines) * line_height
            start_y = rect.centery + 8

            for i, line in enumerate(lines):
                text = self.small_font.render(line, True, TEXT_COLOR)

                # Rotate text for top side
                if side == "top":
                    text = pygame.transform.rotate(text, 180)

                y_pos = start_y + i * line_height
                text_rect = text.get_rect(center=(rect.centerx, y_pos))
                surface.blit(text, text_rect)
        else:
            # For vertical sides, render icon in center
            icon_rect = icon.get_rect(center=rect.center)
            surface.blit(icon, icon_rect)

    def _render_utility(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        tile_info: TileInfo,
        side: str,
        is_mortgaged: bool
    ) -> None:
        """Render a utility tile with modern styling."""
        # Draw shadow
        self._draw_shadow(surface, rect, self.BORDER_RADIUS)

        # Draw rounded background
        self._draw_rounded_rect(
            surface, TILE_BACKGROUND, rect,
            self.BORDER_RADIUS,
            TILE_BORDER, 2
        )

        # Draw utility icon (lightbulb for electric, droplet for water)
        if "electric" in tile_info.name.lower():
            icon = self.icon_font.render("💡", True, TEXT_COLOR)
        elif "water" in tile_info.name.lower():
            icon = self.icon_font.render("💧", True, TEXT_COLOR)
        else:
            icon = self.icon_font.render("⚡", True, TEXT_COLOR)

        # Calculate available width for text
        if side in ["bottom", "top"]:
            max_text_width = rect.width - 8
        else:
            max_text_width = rect.height - 8

        # Wrap property name
        lines = wrap_text(tile_info.name, max_text_width, self.small_font)

        # Limit to 2 lines
        if len(lines) > 2:
            lines = lines[:2]

        # Rotate icon based on side
        if side == "top":
            icon = pygame.transform.rotate(icon, 180)
        elif side in ["left", "right"]:
            icon = pygame.transform.rotate(icon, 90 if side == "left" else -90)

        # Position icon and text
        if side in ["bottom", "top"]:
            icon_rect = icon.get_rect(center=(rect.centerx, rect.centery - 16))
            surface.blit(icon, icon_rect)

            # Render text lines below icon
            line_height = self.small_font.get_height()
            total_height = len(lines) * line_height
            start_y = rect.centery + 8

            for i, line in enumerate(lines):
                text = self.small_font.render(line, True, TEXT_COLOR)

                # Rotate text for top side
                if side == "top":
                    text = pygame.transform.rotate(text, 180)

                y_pos = start_y + i * line_height
                text_rect = text.get_rect(center=(rect.centerx, y_pos))
                surface.blit(text, text_rect)
        else:
            # For vertical sides, render icon in center
            icon_rect = icon.get_rect(center=rect.center)
            surface.blit(icon, icon_rect)

    def _render_chance(self, surface: pygame.Surface, rect: pygame.Rect, side: str) -> None:
        """Render a Chance tile with modern styling."""
        # Draw shadow
        self._draw_shadow(surface, rect, self.BORDER_RADIUS)

        # Draw rounded background
        self._draw_rounded_rect(
            surface, CHANCE_COLOR, rect,
            self.BORDER_RADIUS,
            TILE_BORDER, 2
        )

        # Draw question mark icon
        icon = self.icon_font.render("?", True, TEXT_COLOR)
        text = self.small_font.render("CHANCE", True, TEXT_COLOR)

        # Rotate based on side
        if side == "top":
            icon = pygame.transform.rotate(icon, 180)
            text = pygame.transform.rotate(text, 180)
        elif side in ["left", "right"]:
            icon = pygame.transform.rotate(icon, 90 if side == "left" else -90)
            text = pygame.transform.rotate(text, 90 if side == "left" else -90)

        icon_rect = icon.get_rect(center=(rect.centerx, rect.centery - 8))
        text_rect = text.get_rect(center=(rect.centerx, rect.centery + 10))

        surface.blit(icon, icon_rect)
        surface.blit(text, text_rect)

    def _render_community_chest(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        side: str
    ) -> None:
        """Render a Community Chest tile with modern styling."""
        # Draw shadow
        self._draw_shadow(surface, rect, self.BORDER_RADIUS)

        # Draw rounded background
        self._draw_rounded_rect(
            surface, COMMUNITY_CHEST_COLOR, rect,
            self.BORDER_RADIUS,
            TILE_BORDER, 2
        )

        # Draw chest icon
        icon = self.icon_font.render("📦", True, TEXT_COLOR)
        text = self.small_font.render("COMM.", True, TEXT_COLOR)

        # Rotate for vertical sides
        if side in ["left", "right"]:
            icon = pygame.transform.rotate(icon, 90 if side == "left" else -90)
            text = pygame.transform.rotate(text, 90 if side == "left" else -90)

        icon_rect = icon.get_rect(center=(rect.centerx, rect.centery - 8))
        text_rect = text.get_rect(center=(rect.centerx, rect.centery + 10))

        surface.blit(icon, icon_rect)
        surface.blit(text, text_rect)

    def _render_tax(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        tile_info: TileInfo,
        side: str
    ) -> None:
        """Render a tax tile with modern styling."""
        # Draw shadow
        self._draw_shadow(surface, rect, self.BORDER_RADIUS)

        # Draw rounded background
        self._draw_rounded_rect(
            surface, TAX_COLOR, rect,
            self.BORDER_RADIUS,
            TILE_BORDER, 2
        )

        # Tax icon and amount
        icon = self.icon_font.render("£", True, TEXT_COLOR)

        # Calculate available width for text
        if side in ["bottom", "top"]:
            max_text_width = rect.width - 8
        else:
            max_text_width = rect.height - 8

        # Format tax name
        tax_name = format_display_name(tile_info.name)

        # Wrap tax name if needed
        lines = wrap_text(tax_name, max_text_width, self.small_font)
        if len(lines) > 1:
            # If it wraps, just use "TAX"
            tax_name = "TAX"

        text = self.small_font.render(tax_name, True, TEXT_COLOR)

        if tile_info.tax_amount:
            amount_text = f"£{tile_info.tax_amount}"
        else:
            amount_text = ""

        amount = self.small_font.render(amount_text, True, TEXT_COLOR)

        # Rotate for vertical sides
        if side in ["left", "right"]:
            icon = pygame.transform.rotate(icon, 90 if side == "left" else -90)
            text = pygame.transform.rotate(text, 90 if side == "left" else -90)
            amount = pygame.transform.rotate(amount, 90 if side == "left" else -90)

        icon_rect = icon.get_rect(center=(rect.centerx, rect.centery - 12))
        text_rect = text.get_rect(center=(rect.centerx, rect.centery + 4))
        amount_rect = amount.get_rect(center=(rect.centerx, rect.centery + 16))

        surface.blit(icon, icon_rect)
        surface.blit(text, text_rect)
        surface.blit(amount, amount_rect)

    def _draw_mortgage_overlay(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw semi-transparent overlay for mortgaged properties."""
        # Create rounded overlay
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            overlay,
            (*MORTGAGE_OVERLAY, 160),  # Semi-transparent
            overlay.get_rect(),
            border_radius=self.BORDER_RADIUS
        )
        surface.blit(overlay, (rect.x, rect.y))

        # Draw "MORTGAGED" text with background
        text = self.small_font.render("MORTGAGED", True, (255, 255, 255))
        text_rect = text.get_rect(center=rect.center)

        # Draw text background
        bg_rect = text_rect.inflate(8, 4)
        pygame.draw.rect(surface, (180, 0, 0), bg_rect, border_radius=3)

        surface.blit(text, text_rect)
