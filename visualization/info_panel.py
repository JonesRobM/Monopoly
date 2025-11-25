"""
Information panel for Monopoly visualization.

Displays game state information including player stats, turn number,
and other relevant game data.
"""

from typing import List, Optional, Tuple, Dict, TYPE_CHECKING
import pygame
from engine.state import GameState, PlayerState
from visualization.colors import (
    get_player_color, INFO_PANEL_BG, INFO_PANEL_BORDER, TEXT_COLOR
)

if TYPE_CHECKING:
    from engine.board import MonopolyBoard


class InfoPanel:
    """
    Renders game state information panel.

    Displays:
    - Turn number
    - Current player
    - Player cash
    - Player properties
    - Player status (in jail, bankrupt, etc.)
    - Clickable player details
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        font_size: int = 12,
        board: Optional['MonopolyBoard'] = None
    ):
        """
        Initialize info panel.

        Args:
            x: Panel x position
            y: Panel y position
            width: Panel width
            height: Panel height
            font_size: Font size for text
            board: Monopoly board for property name lookup
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.board = board

        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", font_size)
        self.small_font = pygame.font.SysFont("Arial", font_size )
        self.title_font = pygame.font.SysFont("Arial", font_size + 2, bold=True)

        # Interactive state
        self.selected_player: Optional[int] = None
        self.player_rects: Dict[int, pygame.Rect] = {}  # Track clickable areas

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
        # Clear player rects for click detection
        self.player_rects.clear()

        # Check if showing detailed view
        if self.selected_player is not None:
            self._render_player_details(surface, game_state)
            return

        # Draw panel background
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, INFO_PANEL_BG, panel_rect)
        pygame.draw.rect(surface, INFO_PANEL_BORDER, panel_rect, 2)

        # Starting y position for text
        text_y = self.y + 10

        # Board name (if provided) - smaller
        if board_name:
            # Truncate if too long
            display_name = board_name if len(board_name) <= 14 else board_name[:11] + "..."
            text = self.small_font.render(display_name, True, TEXT_COLOR)
            surface.blit(text, (self.x + 10, text_y))
            text_y += 20

        # Turn number
        turn_text = f"Turn: {game_state.turn_number}"
        text = self.small_font.render(turn_text, True, TEXT_COLOR)
        surface.blit(text, (self.x + 10, text_y))
        text_y += 20

        # Divider line
        pygame.draw.line(
            surface,
            INFO_PANEL_BORDER,
            (self.x + 10, text_y),
            (self.x + self.width - 10, text_y),
            1
        )
        text_y += 8

        # Player stats
        text = self.title_font.render("Players", True, TEXT_COLOR)
        surface.blit(text, (self.x + 10, text_y))
        text_y += 22

        # Hint text
        hint_text = "(click for details)"
        text = self.small_font.render(hint_text, True, (120, 120, 120))
        surface.blit(text, (self.x + 10, text_y))
        text_y += 18

        for player in game_state.players:
            text_y = self._render_player_info(surface, player, text_y, game_state)

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
                winner_text = f"WIN: P{game_state.winner}!"
                text = self.title_font.render(winner_text, True, get_player_color(game_state.winner))
                surface.blit(text, (self.x + 10, text_y))
            else:
                text = self.title_font.render("GAME OVER", True, TEXT_COLOR)
                surface.blit(text, (self.x + 10, text_y))

    def _render_player_info(
        self,
        surface: pygame.Surface,
        player: PlayerState,
        y_pos: int,
        game_state: GameState
    ) -> int:
        """
        Render information for a single player.

        Args:
            surface: Pygame surface to draw on
            player: Player state
            y_pos: Current y position
            game_state: Current game state

        Returns:
            Updated y position
        """
        start_y = y_pos

        # Player color indicator
        color = get_player_color(player.player_id)
        pygame.draw.circle(surface, color, (self.x + 15, y_pos + 8), 6)
        pygame.draw.circle(surface, (0, 0, 0), (self.x + 15, y_pos + 8), 6, 1)

        # Player ID and status
        if player.is_bankrupt:
            status = "BANK"
            status_color = (200, 0, 0)
        elif player.is_in_jail:
            status = f"JAIL({player.jail_turns})"
            status_color = (200, 100, 0)
        else:
            status = "Active"
            status_color = (0, 150, 0)

        player_text = f"P{player.player_id}: {status}"
        text = self.small_font.render(player_text, True, status_color)
        surface.blit(text, (self.x + 30, y_pos))
        y_pos += 16

        # Cash
        cash_text = f"${player.cash}"
        text = self.small_font.render(cash_text, True, TEXT_COLOR)
        surface.blit(text, (self.x + 30, y_pos))
        y_pos += 14

        # Properties
        prop_text = f"{len(player.owned_properties)} props"
        text = self.small_font.render(prop_text, True, TEXT_COLOR)
        surface.blit(text, (self.x + 30, y_pos))
        y_pos += 18

        # Store clickable rect for this player
        player_rect = pygame.Rect(self.x + 10, start_y, self.width - 20, y_pos - start_y)
        self.player_rects[player.player_id] = player_rect

        # Draw subtle hover indication
        mouse_pos = pygame.mouse.get_pos()
        if player_rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, (200, 200, 200, 50), player_rect, 1)

        return y_pos

    def handle_click(self, mouse_pos: Tuple[int, int], game_state: GameState) -> None:
        """
        Handle mouse click on info panel.

        Args:
            mouse_pos: (x, y) mouse position
            game_state: Current game state
        """
        # Check if clicking to close detailed view
        if self.selected_player is not None:
            # Close button area (top-right corner)
            close_rect = pygame.Rect(self.x + self.width - 30, self.y + 10, 20, 20)
            if close_rect.collidepoint(mouse_pos):
                self.selected_player = None
                return

            # Click anywhere else also closes
            panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            if panel_rect.collidepoint(mouse_pos):
                self.selected_player = None
            return

        # Check if clicking on a player
        for player_id, rect in self.player_rects.items():
            if rect.collidepoint(mouse_pos):
                self.selected_player = player_id
                return

    def _render_player_details(self, surface: pygame.Surface, game_state: GameState) -> None:
        """
        Render detailed view for selected player.

        Args:
            surface: Pygame surface to draw on
            game_state: Current game state
        """
        # Find the selected player
        player = None
        for p in game_state.players:
            if p.player_id == self.selected_player:
                player = p
                break

        if player is None:
            self.selected_player = None
            return

        # Draw panel background
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, INFO_PANEL_BG, panel_rect)
        pygame.draw.rect(surface, INFO_PANEL_BORDER, panel_rect, 2)

        text_y = self.y + 10

        # Header with player info
        color = get_player_color(player.player_id)
        pygame.draw.circle(surface, color, (self.x + 15, text_y + 8), 8)
        pygame.draw.circle(surface, (0, 0, 0), (self.x + 15, text_y + 8), 8, 1)

        header_text = f"Player {player.player_id}"
        text = self.title_font.render(header_text, True, TEXT_COLOR)
        surface.blit(text, (self.x + 30, text_y))

        # Close button (X)
        close_x = self.x + self.width - 20
        close_y = text_y + 5
        pygame.draw.line(surface, (200, 0, 0), (close_x - 5, close_y - 5), (close_x + 5, close_y + 5), 2)
        pygame.draw.line(surface, (200, 0, 0), (close_x - 5, close_y + 5), (close_x + 5, close_y - 5), 2)

        text_y += 25

        # Status
        if player.is_bankrupt:
            status_text = "Status: BANKRUPT"
            status_color = (200, 0, 0)
        elif player.is_in_jail:
            status_text = f"Status: In Jail ({player.jail_turns} turns)"
            status_color = (200, 100, 0)
        else:
            status_text = "Status: Active"
            status_color = (0, 150, 0)

        text = self.small_font.render(status_text, True, status_color)
        surface.blit(text, (self.x + 10, text_y))
        text_y += 18

        # Cash
        cash_text = f"Cash: ${player.cash}"
        text = self.small_font.render(cash_text, True, TEXT_COLOR)
        surface.blit(text, (self.x + 10, text_y))
        text_y += 18

        # Position
        pos_text = f"Position: Tile {player.position}"
        text = self.small_font.render(pos_text, True, TEXT_COLOR)
        surface.blit(text, (self.x + 10, text_y))
        text_y += 20

        # Divider
        pygame.draw.line(
            surface,
            INFO_PANEL_BORDER,
            (self.x + 10, text_y),
            (self.x + self.width - 10, text_y),
            1
        )
        text_y += 10

        # Properties section
        properties_header = f"Properties ({len(player.owned_properties)})"
        text = self.title_font.render(properties_header, True, TEXT_COLOR)
        surface.blit(text, (self.x + 10, text_y))
        text_y += 20

        if not player.owned_properties:
            no_props = "No properties owned"
            text = self.small_font.render(no_props, True, (128, 128, 128))
            surface.blit(text, (self.x + 15, text_y))
            text_y += 18
        else:
            # Render scrollable property list
            max_visible_height = self.height - (text_y - self.y) - 40
            self._render_property_list(surface, player, game_state, self.x + 10, text_y, self.width - 20, max_visible_height)
            text_y += max_visible_height

        # Cards section (at bottom if space)
        text_y = max(text_y + 15, self.y + self.height - 60)
        pygame.draw.line(
            surface,
            INFO_PANEL_BORDER,
            (self.x + 10, text_y),
            (self.x + self.width - 10, text_y),
            1
        )
        text_y += 10

        # Get Out of Jail Free cards
        jail_cards = player.get_out_of_jail_cards
        if jail_cards > 0:
            cards_text = f"Get Out of Jail Free: {jail_cards}"
            text = self.small_font.render(cards_text, True, TEXT_COLOR)
            surface.blit(text, (self.x + 10, text_y))

        # Close hint
        hint_y = self.y + self.height - 20
        hint_text = "(click to close)"
        text = self.small_font.render(hint_text, True, (120, 120, 120))
        text_rect = text.get_rect(center=(self.x + self.width // 2, hint_y))
        surface.blit(text, text_rect)

    def _render_property_list(
        self,
        surface: pygame.Surface,
        player: PlayerState,
        game_state: GameState,
        x: int,
        y: int,
        width: int,
        max_height: int
    ) -> None:
        """
        Render scrollable list of player's properties.

        Args:
            surface: Pygame surface to draw on
            player: Player state
            game_state: Current game state
            x: X position
            y: Y position
            width: Available width
            max_height: Maximum height for list
        """
        line_height = 15
        current_y = y

        for tile_id in sorted(player.owned_properties):
            if current_y - y + line_height > max_height:
                # Show "..." if more properties exist
                more_text = "... (more properties)"
                text = self.small_font.render(more_text, True, (100, 100, 100))
                surface.blit(text, (x + 5, current_y))
                break

            # Get property state
            prop_state = game_state.properties.get(tile_id)
            if prop_state is None:
                continue

            # Get property name from board
            prop_name = f"Tile {tile_id}"
            if self.board:
                try:
                    tile_info = self.board.get_tile(tile_id)
                    prop_name = tile_info.name
                    # Truncate long names
                    if len(prop_name) > 18:
                        prop_name = prop_name[:15] + "..."
                except:
                    pass

            # Build property text with indicators
            prop_text = f"• {prop_name}"

            # Add building indicator
            if prop_state.num_houses == 5:
                prop_text += " [HOTEL]"
            elif prop_state.num_houses > 0:
                prop_text += f" [{prop_state.num_houses}H]"

            # Add mortgage indicator
            if prop_state.is_mortgaged:
                prop_text += " (MORT)"

            # Render with appropriate color
            text_color = (128, 128, 128) if prop_state.is_mortgaged else TEXT_COLOR
            text = self.small_font.render(prop_text, True, text_color)
            surface.blit(text, (x + 5, current_y))

            current_y += line_height


class CenterPanel:
    """
    Renders information in the center of the board.

    Displays turn information and property ownership details for all players.
    """

    def __init__(self, board: Optional['MonopolyBoard'] = None, font_size: int = 12):
        """
        Initialize center panel.

        Args:
            board: Monopoly board for tile name lookup
            font_size: Font size for text
        """
        pygame.font.init()
        self.board = board
        self.title_font = pygame.font.SysFont("Arial", font_size + 4, bold=True)
        self.font = pygame.font.SysFont("Arial", font_size, bold=True)
        self.small_font = pygame.font.SysFont("Arial", font_size - 2)
        self.tiny_font = pygame.font.SysFont("Arial", font_size - 3)

    def render(
        self,
        surface: pygame.Surface,
        center_rect: tuple[int, int, int, int],
        board_name: str = "MONOPOLY",
        game_state: Optional[GameState] = None
    ) -> None:
        """
        Render center panel with turn and property information.

        Args:
            surface: Pygame surface to draw on
            center_rect: (x, y, width, height) of center area
            board_name: Board name to display
            game_state: Current game state (optional)
        """
        x, y, width, height = center_rect

        if game_state is None:
            # Fallback to simple board name display
            center_x = x + width // 2
            center_y = y + height // 2
            text = self.title_font.render(board_name, True, TEXT_COLOR)
            text_rect = text.get_rect(center=(center_x, center_y))
            surface.blit(text, text_rect)
            return

        # Draw subtle background for center panel
        background_rect = pygame.Rect(x + 5, y + 5, width - 10, height - 10)
        background_surface = pygame.Surface((background_rect.width, background_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            background_surface,
            (255, 255, 255, 200),  # Semi-transparent white
            background_surface.get_rect(),
            border_radius=10
        )
        surface.blit(background_surface, (background_rect.x, background_rect.y))

        # Draw border
        pygame.draw.rect(
            surface,
            INFO_PANEL_BORDER,
            background_rect,
            width=2,
            border_radius=10
        )

        # Calculate layout
        padding = 15
        current_y = y + padding

        # Draw turn indicator at the top
        current_y = self._render_turn_info(surface, x, current_y, width, game_state)
        current_y += 8

        # Draw divider line
        pygame.draw.line(
            surface,
            INFO_PANEL_BORDER,
            (x + padding, current_y),
            (x + width - padding, current_y),
            1
        )
        current_y += 10

        # Draw property ownership for each player
        self._render_property_ownership(surface, x, current_y, width, height - (current_y - y) - padding, game_state)

    def _render_turn_info(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        width: int,
        game_state: GameState
    ) -> int:
        """
        Render current turn information.

        Args:
            surface: Pygame surface to draw on
            x: X position
            y: Y position
            width: Available width
            game_state: Current game state

        Returns:
            Updated y position
        """
        center_x = x + width // 2

        # Current turn indicator
        current_player = game_state.current_player()
        player_color = get_player_color(current_player.player_id)

        turn_text = f"Turn {game_state.turn_number} - Player {current_player.player_id}'s Turn"
        text = self.font.render(turn_text, True, player_color)
        text_rect = text.get_rect(center=(center_x, y))
        surface.blit(text, text_rect)

        return y + text.get_height() + 2

    def _render_property_ownership(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        width: int,
        height: int,
        game_state: GameState
    ) -> None:
        """
        Render property ownership details for all players.

        Args:
            surface: Pygame surface to draw on
            x: X position
            y: Y position
            width: Available width
            height: Available height
            game_state: Current game state
        """
        padding = 8

        # Filter active players and organize properties
        active_players = [p for p in game_state.players if not p.is_bankrupt]

        if not active_players:
            return

        # Calculate available space per player
        player_height = (height - padding) // len(active_players)

        current_y = y

        for idx, player in enumerate(active_players):
            # Player header with color indicator
            player_color = get_player_color(player.player_id)

            # Draw player color circle
            circle_x = x + padding + 8
            circle_y = current_y + 8
            pygame.draw.circle(surface, player_color, (circle_x, circle_y), 6)
            pygame.draw.circle(surface, (0, 0, 0), (circle_x, circle_y), 6, 1)

            # Player name
            player_text = f"Player {player.player_id}"
            text = self.small_font.render(player_text, True, TEXT_COLOR)
            surface.blit(text, (circle_x + 12, current_y + 2))

            property_y = current_y + 18

            # Get player's properties
            player_properties = [
                (tile_id, game_state.properties[tile_id])
                for tile_id in player.owned_properties
                if tile_id in game_state.properties
            ]

            if not player_properties:
                # No properties
                no_props_text = self.tiny_font.render("No properties", True, (128, 128, 128))
                surface.blit(no_props_text, (x + padding + 20, property_y))
            else:
                # Render properties in a compact list
                self._render_player_properties(
                    surface,
                    x + padding,
                    property_y,
                    width - 2 * padding,
                    player_height - 22,
                    player_properties,
                    game_state
                )

            current_y += player_height

            # Draw divider between players (except after last player)
            if idx < len(active_players) - 1:
                divider_y = current_y - 3
                pygame.draw.line(
                    surface,
                    (200, 200, 200),  # Light gray
                    (x + padding + 10, divider_y),
                    (x + width - padding - 10, divider_y),
                    1
                )

    def _render_player_properties(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        width: int,
        height: int,
        properties: List[tuple[int, 'PropertyState']],
        game_state: GameState
    ) -> None:
        """
        Render a player's properties in a compact format.

        Args:
            surface: Pygame surface to draw on
            x: X position
            y: Y position
            width: Available width
            height: Available height
            properties: List of (tile_id, PropertyState) tuples
            game_state: Current game state
        """
        current_y = y
        line_height = 14
        max_lines = max(1, height // line_height)

        # Group properties for compact display
        # Show up to max_lines properties, then indicate if there are more
        properties_to_show = properties[:max_lines - 1] if len(properties) > max_lines else properties

        for tile_id, prop_state in properties_to_show:
            # Get tile name from board if available
            if self.board:
                try:
                    tile_info = self.board.get_tile(tile_id)
                    # Truncate long names
                    prop_name = tile_info.name
                    if len(prop_name) > 18:
                        prop_name = prop_name[:15] + "..."
                    prop_text = f"  {prop_name}"
                except:
                    prop_text = f"  T{tile_id}"
            else:
                prop_text = f"  T{tile_id}"

            # Add building indicator
            if prop_state.num_houses == 5:
                prop_text += " [H]"  # Hotel
            elif prop_state.num_houses > 0:
                prop_text += f" [{prop_state.num_houses}h]"  # Houses

            # Add mortgage indicator
            if prop_state.is_mortgaged:
                prop_text += " (M)"

            # Render with appropriate color
            color = (128, 128, 128) if prop_state.is_mortgaged else TEXT_COLOR
            text = self.tiny_font.render(prop_text, True, color)
            surface.blit(text, (x + 20, current_y))

            current_y += line_height

        # If there are more properties, show count
        if len(properties) > max_lines:
            remaining = len(properties) - len(properties_to_show)
            more_text = f"  ... +{remaining} more"
            text = self.tiny_font.render(more_text, True, (100, 100, 100))
            surface.blit(text, (x + 20, current_y))


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


class TransactionNotification:
    """
    Displays transaction pop-ups in the bottom-right corner.

    Shows transaction messages like purchases, rent payments, and trades
    in a styled notification box that appears in the bottom-right corner
    of the screen.
    """

    def __init__(self, font_size: int = 13):
        """
        Initialize transaction notification display.

        Args:
            font_size: Font size for notification text
        """
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", font_size, bold=False)
        self.title_font = pygame.font.SysFont("Arial", font_size + 2, bold=True)
        self.notifications: List[tuple[str, float]] = []  # (message, timestamp)
        self.notification_duration = 4.0  # seconds (longer than regular messages)

        # Styling
        self.bg_color = (40, 40, 40)  # Dark background
        self.border_color = (100, 100, 100)  # Gray border
        self.text_color = (255, 255, 255)  # White text
        self.padding = 12
        self.margin = 15
        self.notification_width = 320
        self.notification_spacing = 10

    def add_transaction(self, message: str) -> None:
        """
        Add a transaction notification.

        Args:
            message: Transaction message text
        """
        import time
        self.notifications.append((message, time.time()))

    def render(
        self,
        surface: pygame.Surface,
        max_notifications: int = 5
    ) -> None:
        """
        Render active transaction notifications in bottom-right corner.

        Args:
            surface: Pygame surface to draw on
            max_notifications: Maximum number of notifications to display
        """
        import time
        current_time = time.time()

        # Remove expired notifications
        self.notifications = [
            (msg, timestamp)
            for msg, timestamp in self.notifications
            if current_time - timestamp < self.notification_duration
        ]

        if not self.notifications:
            return

        # Get screen dimensions
        screen_width = surface.get_width()
        screen_height = surface.get_height()

        # Calculate starting position (bottom-right, working upwards)
        current_y = screen_height - self.margin

        # Render recent notifications (most recent at bottom)
        for message, timestamp in self.notifications[-max_notifications:]:
            # Calculate alpha based on age (fade in/out)
            age = current_time - timestamp
            if age < 0.3:
                # Fade in
                alpha = int(255 * (age / 0.3))
            elif age > self.notification_duration - 0.5:
                # Fade out
                remaining = self.notification_duration - age
                alpha = int(255 * (remaining / 0.5))
            else:
                # Full opacity
                alpha = 255

            # Wrap text if too long
            words = message.split()
            lines = []
            current_line = []

            for word in words:
                test_line = ' '.join(current_line + [word])
                text_surface = self.font.render(test_line, True, self.text_color)
                if text_surface.get_width() <= self.notification_width - 2 * self.padding:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)

            if current_line:
                lines.append(' '.join(current_line))

            # Limit to 3 lines
            if len(lines) > 3:
                lines = lines[:3]
                lines[-1] = lines[-1][:30] + "..."

            # Calculate notification height
            line_height = self.font.get_height()
            notification_height = 2 * self.padding + len(lines) * line_height + (len(lines) - 1) * 3

            # Position notification
            notification_y = current_y - notification_height
            notification_x = screen_width - self.notification_width - self.margin

            # Create notification surface with alpha
            notification_surface = pygame.Surface(
                (self.notification_width, notification_height),
                pygame.SRCALPHA
            )

            # Draw background with rounded corners
            bg_rect = notification_surface.get_rect()
            pygame.draw.rect(
                notification_surface,
                (*self.bg_color, alpha),
                bg_rect,
                border_radius=8
            )

            # Draw border
            pygame.draw.rect(
                notification_surface,
                (*self.border_color, alpha),
                bg_rect,
                width=2,
                border_radius=8
            )

            # Render text lines
            text_y = self.padding
            for line in lines:
                text = self.font.render(line, True, (*self.text_color, alpha))
                notification_surface.blit(text, (self.padding, text_y))
                text_y += line_height + 3

            # Blit notification to main surface
            surface.blit(notification_surface, (notification_x, notification_y))

            # Move up for next notification
            current_y = notification_y - self.notification_spacing
