"""
Information panel for Monopoly visualization.

Displays game state information including player stats, turn number,
and other relevant game data.
"""

from typing import List, Optional
import pygame
from engine.state import GameState, PlayerState
from visualization.colors import (
    get_player_color, INFO_PANEL_BG, INFO_PANEL_BORDER, TEXT_COLOR
)


class InfoPanel:
    """
    Renders game state information panel.

    Displays:
    - Turn number
    - Current player
    - Player cash
    - Player properties
    - Player status (in jail, bankrupt, etc.)
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        font_size: int = 12
    ):
        """
        Initialize info panel.

        Args:
            x: Panel x position
            y: Panel y position
            width: Panel width
            height: Panel height
            font_size: Font size for text
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", font_size)
        self.small_font = pygame.font.SysFont("Arial", font_size - 2)
        self.title_font = pygame.font.SysFont("Arial", font_size + 2, bold=True)

    def render(
        self,
        surface: pygame.Surface,
        game_state: GameState,
        board_name: Optional[str] = None
    ) -> None:
        """
        Render the info panel.

        Args:
            surface: Pygame surface to draw on
            game_state: Current game state
            board_name: Name of the board (optional)
        """
        # Draw panel background
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, INFO_PANEL_BG, panel_rect)
        pygame.draw.rect(surface, INFO_PANEL_BORDER, panel_rect, 2)

        # Starting y position for text
        text_y = self.y + 10

        # Board name (if provided)
        if board_name:
            text = self.title_font.render(board_name, True, TEXT_COLOR)
            surface.blit(text, (self.x + 10, text_y))
            text_y += 25

        # Turn number
        turn_text = f"Turn: {game_state.turn_number}"
        text = self.font.render(turn_text, True, TEXT_COLOR)
        surface.blit(text, (self.x + 10, text_y))
        text_y += 20

        # Current player
        current_player = game_state.current_player()
        current_text = f"Current: Player {current_player.player_id}"
        text = self.font.render(current_text, True, get_player_color(current_player.player_id))
        surface.blit(text, (self.x + 10, text_y))
        text_y += 25

        # Divider line
        pygame.draw.line(
            surface,
            INFO_PANEL_BORDER,
            (self.x + 10, text_y),
            (self.x + self.width - 10, text_y),
            1
        )
        text_y += 10

        # Player stats
        text = self.title_font.render("Players:", True, TEXT_COLOR)
        surface.blit(text, (self.x + 10, text_y))
        text_y += 25

        for player in game_state.players:
            text_y = self._render_player_info(surface, player, text_y)

        # Game status
        if game_state.game_over:
            text_y += 10
            pygame.draw.line(
                surface,
                INFO_PANEL_BORDER,
                (self.x + 10, text_y),
                (self.x + self.width - 10, text_y),
                1
            )
            text_y += 10

            if game_state.winner is not None:
                winner_text = f"WINNER: Player {game_state.winner}!"
                text = self.title_font.render(winner_text, True, get_player_color(game_state.winner))
                surface.blit(text, (self.x + 10, text_y))
            else:
                text = self.title_font.render("GAME OVER", True, TEXT_COLOR)
                surface.blit(text, (self.x + 10, text_y))

    def _render_player_info(
        self,
        surface: pygame.Surface,
        player: PlayerState,
        y_pos: int
    ) -> int:
        """
        Render information for a single player.

        Args:
            surface: Pygame surface to draw on
            player: Player state
            y_pos: Current y position

        Returns:
            Updated y position
        """
        # Player color indicator
        color = get_player_color(player.player_id)
        pygame.draw.circle(surface, color, (self.x + 15, y_pos + 8), 6)
        pygame.draw.circle(surface, (0, 0, 0), (self.x + 15, y_pos + 8), 6, 1)

        # Player ID and status
        if player.is_bankrupt:
            status = "BANKRUPT"
            status_color = (200, 0, 0)
        elif player.is_in_jail:
            status = f"IN JAIL ({player.jail_turns})"
            status_color = (200, 100, 0)
        else:
            status = "Active"
            status_color = (0, 150, 0)

        player_text = f"P{player.player_id}: {status}"
        text = self.font.render(player_text, True, status_color)
        surface.blit(text, (self.x + 30, y_pos))
        y_pos += 18

        # Cash
        cash_text = f"  Cash: ${player.cash}"
        text = self.small_font.render(cash_text, True, TEXT_COLOR)
        surface.blit(text, (self.x + 30, y_pos))
        y_pos += 16

        # Properties
        prop_text = f"  Props: {len(player.owned_properties)}"
        text = self.small_font.render(prop_text, True, TEXT_COLOR)
        surface.blit(text, (self.x + 30, y_pos))
        y_pos += 20

        return y_pos


class CenterPanel:
    """
    Renders information in the center of the board.

    Displays board name, logo, and key game information.
    """

    def __init__(self, font_size: int = 16):
        """
        Initialize center panel.

        Args:
            font_size: Font size for text
        """
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", font_size, bold=True)
        self.small_font = pygame.font.SysFont("Arial", font_size - 4)

    def render(
        self,
        surface: pygame.Surface,
        center_rect: tuple[int, int, int, int],
        board_name: str = "MONOPOLY",
        subtitle: Optional[str] = None
    ) -> None:
        """
        Render center panel.

        Args:
            surface: Pygame surface to draw on
            center_rect: (x, y, width, height) of center area
            board_name: Board name to display
            subtitle: Optional subtitle text
        """
        x, y, width, height = center_rect

        # Center coordinates
        center_x = x + width // 2
        center_y = y + height // 2

        # Render board name
        text = self.font.render(board_name, True, TEXT_COLOR)
        text_rect = text.get_rect(center=(center_x, center_y - 20))
        surface.blit(text, text_rect)

        # Render subtitle if provided
        if subtitle:
            subtext = self.small_font.render(subtitle, True, TEXT_COLOR)
            subtext_rect = subtext.get_rect(center=(center_x, center_y + 10))
            surface.blit(subtext, subtext_rect)


class MessageDisplay:
    """
    Displays temporary messages and notifications.

    Shows dice rolls, card draws, and other game events.
    """

    def __init__(self, font_size: int = 14):
        """
        Initialize message display.

        Args:
            font_size: Font size for messages
        """
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", font_size, bold=True)
        self.messages: List[tuple[str, float]] = []  # (message, timestamp)
        self.message_duration = 2.0  # seconds

    def add_message(self, message: str) -> None:
        """
        Add a temporary message.

        Args:
            message: Message text
        """
        import time
        self.messages.append((message, time.time()))

    def render(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        max_messages: int = 3
    ) -> None:
        """
        Render active messages.

        Args:
            surface: Pygame surface to draw on
            x: X position for messages
            y: Y position for messages
            max_messages: Maximum number of messages to display
        """
        import time
        current_time = time.time()

        # Remove expired messages
        self.messages = [
            (msg, timestamp)
            for msg, timestamp in self.messages
            if current_time - timestamp < self.message_duration
        ]

        # Render recent messages
        for idx, (message, timestamp) in enumerate(self.messages[-max_messages:]):
            # Calculate alpha based on age
            age = current_time - timestamp
            alpha = int(255 * (1 - age / self.message_duration))

            # Render message
            text = self.font.render(message, True, TEXT_COLOR)
            text.set_alpha(alpha)

            message_y = y + idx * 25
            surface.blit(text, (x, message_y))
