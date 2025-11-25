"""
Main Monopoly board renderer.

Coordinates all visualization components to render the complete game state.
Integrates with PettingZoo environment for real-time visualization.
"""

from typing import Optional, Dict
import pygame
from engine.state import GameState, PropertyState
from engine.board import MonopolyBoard
from visualization.board_layout import BoardLayout
from visualization.tile_renderer import TileRenderer
from visualization.player_renderer import PlayerRenderer, BuildingRenderer, OwnershipIndicator
from visualization.animation import AnimationManager
from visualization.info_panel import InfoPanel, CenterPanel, MessageDisplay, TransactionNotification
from visualization.colors import BOARD_BACKGROUND


class MonopolyRenderer:
    """
    Main renderer for Monopoly game visualization.

    Coordinates all rendering components and handles pygame window management.
    Supports both headless mode and interactive visualization.

    Usage:
        # Create renderer
        renderer = MonopolyRenderer(board, window_width=1200)

        # Render game state
        renderer.render(game_state)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                renderer.close()
                break

        # Update display
        pygame.display.flip()
    """

    def __init__(
        self,
        board: MonopolyBoard,
        window_width: int = 1400,
        window_height: int = 980,
        enable_animation: bool = True,
        fps: int = 60,
        fullscreen: bool = False
    ):
        """
        Initialize Monopoly renderer.

        Args:
            board: Monopoly board configuration
            window_width: Window width in pixels (used if not fullscreen)
            window_height: Window height in pixels (used if not fullscreen)
            enable_animation: Enable smooth animations
            fps: Target frames per second
            fullscreen: Enable fullscreen mode
        """
        self.board = board
        self.enable_animation = enable_animation
        self.fps = fps
        self.fullscreen = fullscreen

        # Initialize pygame
        pygame.init()
        pygame.display.set_caption("Monopoly")

        # Create window and surfaces
        if fullscreen:
            # Get display info for fullscreen resolution
            display_info = pygame.display.Info()
            self.window_width = display_info.current_w
            self.window_height = display_info.current_h
            self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.FULLSCREEN)
        else:
            self.window_width = window_width
            self.window_height = window_height
            self.screen = pygame.display.set_mode((window_width, window_height))

        self.board_surface = pygame.Surface((self.window_width, self.window_height))

        # Calculate board layout with proper padding
        # Reserve space for info panel (200px) + padding (40px) = 240px
        # Add padding around board (15px on all sides for tighter fit)
        info_panel_width = 200
        padding = 15
        gap_between = 10  # Gap between board and info panel

        # Calculate available space
        available_width = self.window_width - info_panel_width - 2 * padding - gap_between
        available_height = self.window_height - 2 * padding

        # Use the smaller dimension to ensure board fits
        board_size = min(available_width, available_height)
        self.board_padding = padding

        self.layout = BoardLayout(board.num_tiles, board_size)

        # Create rendering components
        self.tile_renderer = TileRenderer()
        self.player_renderer = PlayerRenderer()
        self.building_renderer = BuildingRenderer()
        self.ownership_indicator = OwnershipIndicator()

        # Create info panel (smaller, toggleable)
        # Position info panel right after the board with gap
        info_panel_x = padding + board_size + gap_between
        info_panel_y = padding
        info_panel_height = self.window_height - 2 * padding

        self.info_panel_visible = True  # Toggle state
        self.info_panel = InfoPanel(
            info_panel_x,
            info_panel_y,
            info_panel_width,
            info_panel_height,
            board=board
        )

        # Create center panel with board reference
        self.center_panel = CenterPanel(board=board)

        # Create message display
        self.message_display = MessageDisplay()

        # Create transaction notification display
        self.transaction_notification = TransactionNotification()

        # Animation manager
        self.animation_manager = AnimationManager() if enable_animation else None

        # Clock for FPS control
        self.clock = pygame.time.Clock()

        # Track previous player positions for animation
        self.previous_positions: Dict[int, int] = {}

        # Flag to track if pygame is initialized
        self.initialized = True

    def render(self, game_state: GameState) -> None:
        """
        Render the current game state.

        Args:
            game_state: Current game state to render
        """
        if not self.initialized:
            return

        # Update animations
        if self.animation_manager:
            self.animation_manager.update()

        # Clear screen
        self.screen.fill(BOARD_BACKGROUND)
        self.board_surface.fill(BOARD_BACKGROUND)

        # Render board tiles
        self._render_tiles(game_state)

        # Render buildings on properties
        self._render_buildings(game_state)

        # Render ownership indicators
        self._render_ownership(game_state)

        # Render center panel with game state
        board_name = self.board.metadata.name if self.board.metadata else "MONOPOLY"
        center_rect = self.layout.get_center_area()
        self.center_panel.render(self.board_surface, center_rect, board_name, game_state)

        # Render player pieces
        self._render_players(game_state)

        # Blit board surface to screen with padding
        self.screen.blit(self.board_surface, (self.board_padding, self.board_padding))

        # Render info panel (if visible)
        if self.info_panel_visible:
            self.info_panel.render(
                self.screen,
                game_state,
                board_name
            )

        # Render messages
        self.message_display.render(self.screen, 10, 10)

        # Render transaction notifications (bottom-right corner)
        self.transaction_notification.render(self.screen)

        # Update display
        pygame.display.flip()

        # Control frame rate
        self.clock.tick(self.fps)

    def _render_tiles(self, game_state: GameState) -> None:
        """Render all board tiles."""
        for tile_id in range(self.board.num_tiles):
            tile_info = self.board.get_tile(tile_id)
            position = self.layout.get_tile_position(tile_id)

            # Check if property is mortgaged
            is_mortgaged = False
            if tile_id in game_state.properties:
                prop_state = game_state.properties[tile_id]
                is_mortgaged = prop_state.is_mortgaged

            self.tile_renderer.render_tile(
                self.board_surface,
                tile_info,
                position,
                is_mortgaged=is_mortgaged
            )

    def _render_buildings(self, game_state: GameState) -> None:
        """Render houses and hotels on properties."""
        for tile_id, prop_state in game_state.properties.items():
            if prop_state.num_houses > 0:
                self.building_renderer.render_buildings(
                    self.board_surface,
                    tile_id,
                    prop_state.num_houses,
                    self.layout
                )

    def _render_ownership(self, game_state: GameState) -> None:
        """Render ownership indicators on properties."""
        for tile_id, prop_state in game_state.properties.items():
            if prop_state.owner is not None:
                self.ownership_indicator.render_ownership(
                    self.board_surface,
                    tile_id,
                    prop_state.owner,
                    self.layout
                )

    def _render_players(self, game_state: GameState) -> None:
        """Render player pieces with animation support."""
        # Check for position changes and create animations
        if self.animation_manager:
            for player in game_state.players:
                if not player.is_bankrupt:
                    player_id = player.player_id
                    current_pos = player.position

                    # Check if player moved
                    if player_id in self.previous_positions:
                        prev_pos = self.previous_positions[player_id]
                        if prev_pos != current_pos:
                            # Player moved - create animation
                            from_coords = self.layout.get_tile_center(prev_pos)
                            to_coords = self.layout.get_tile_center(current_pos)

                            self.animation_manager.add_player_move(
                                player_id,
                                prev_pos,
                                current_pos,
                                from_coords,
                                to_coords
                            )

                    # Update previous position
                    self.previous_positions[player_id] = current_pos

        # Render players (with or without animation)
        if self.animation_manager and self.animation_manager.is_animating():
            # Render with animation
            self._render_players_animated(game_state)
        else:
            # Render at fixed positions
            self.player_renderer.render_players(
                self.board_surface,
                game_state.players,
                self.layout
            )

    def _render_players_animated(self, game_state: GameState) -> None:
        """Render players with active animations."""
        # Group players by position for non-animated players
        position_groups: Dict[int, list] = {}
        animated_players = set()

        for player in game_state.players:
            if not player.is_bankrupt:
                if player.player_id in self.animation_manager.player_move_animations:
                    animated_players.add(player.player_id)
                else:
                    pos = player.position
                    if pos not in position_groups:
                        position_groups[pos] = []
                    position_groups[pos].append(player)

        # Render non-animated players
        for position, players_at_pos in position_groups.items():
            tile_center = self.layout.get_tile_center(position)

            for idx, player in enumerate(players_at_pos):
                offset_x, offset_y = self.layout.get_player_offset(
                    position, idx, len(players_at_pos)
                )

                x = tile_center[0] + offset_x
                y = tile_center[1] + offset_y

                # Draw player piece
                color = self.player_renderer.piece_radius
                from visualization.colors import get_player_color

                player_color = get_player_color(player.player_id)
                pygame.draw.circle(
                    self.board_surface,
                    player_color,
                    (x, y),
                    self.player_renderer.piece_radius
                )
                pygame.draw.circle(
                    self.board_surface,
                    (0, 0, 0),
                    (x, y),
                    self.player_renderer.piece_radius,
                    2
                )

                # Draw player number
                text = self.player_renderer.font.render(
                    str(player.player_id),
                    True,
                    (255, 255, 255)
                )
                text_rect = text.get_rect(center=(x, y))
                self.board_surface.blit(text, text_rect)

        # Render animated players
        for player_id in animated_players:
            # Get current animated position
            default_coords = self.layout.get_tile_center(
                game_state.players[player_id].position
            )
            x, y = self.animation_manager.get_player_position(
                player_id,
                default_coords
            )

            from visualization.colors import get_player_color

            # Draw player piece
            player_color = get_player_color(player_id)
            pygame.draw.circle(
                self.board_surface,
                player_color,
                (x, y),
                self.player_renderer.piece_radius
            )
            pygame.draw.circle(
                self.board_surface,
                (0, 0, 0),
                (x, y),
                self.player_renderer.piece_radius,
                2
            )

            # Draw player number
            text = self.player_renderer.font.render(
                str(player_id),
                True,
                (255, 255, 255)
            )
            text_rect = text.get_rect(center=(x, y))
            self.board_surface.blit(text, text_rect)

    def add_message(self, message: str) -> None:
        """
        Add a temporary message to display.

        Args:
            message: Message text
        """
        self.message_display.add_message(message)

    def add_transaction(self, message: str) -> None:
        """
        Add a transaction notification (displayed in bottom-right corner).

        Args:
            message: Transaction message text

        Examples:
            renderer.add_transaction("Player 0 bought Mediterranean Avenue for $60")
            renderer.add_transaction("Player 1 paid $200 rent to Player 2")
            renderer.add_transaction("Player 3 built a house on Baltic Avenue")
        """
        self.transaction_notification.add_transaction(message)

    def handle_events(self, game_state: Optional[GameState] = None) -> bool:
        """
        Handle pygame events.

        Args:
            game_state: Optional game state for interactive features

        Returns:
            True if window should stay open, False if closed
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_TAB or event.key == pygame.K_i:
                    # Toggle info panel visibility
                    self.info_panel_visible = not self.info_panel_visible
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle mouse clicks for info panel interaction
                if self.info_panel_visible and game_state is not None:
                    self.info_panel.handle_click(event.pos, game_state)

        return True

    def close(self) -> None:
        """Close the renderer and cleanup pygame resources."""
        if self.initialized:
            pygame.quit()
            self.initialized = False

    def get_surface(self) -> Optional[pygame.Surface]:
        """
        Get the current rendered surface.

        Returns:
            Pygame surface with current rendering
        """
        if self.initialized:
            return self.screen.copy()
        return None

    def save_screenshot(self, filename: str) -> None:
        """
        Save current rendering to an image file.

        Args:
            filename: Output filename (e.g., "screenshot.png")
        """
        if self.initialized:
            pygame.image.save(self.screen, filename)

    def __del__(self):
        """Destructor to ensure pygame is cleaned up."""
        if hasattr(self, 'initialized') and self.initialized:
            self.close()
