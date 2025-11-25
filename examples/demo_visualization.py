"""
Demo script for Monopoly visualization.

Demonstrates the graphical board visualization with AI agents playing.
Shows player movement, property ownership, building, and game state updates.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame
from engine.board import MonopolyBoard
from engine.state import GameState, PlayerState, PropertyState
from visualization.renderer import MonopolyRenderer


def create_demo_game_state(num_players: int = 4) -> GameState:
    """
    Create a demo game state with some interesting properties.

    Args:
        num_players: Number of players

    Returns:
        GameState with demo data
    """
    # Create players with different positions and cash amounts
    players = [
        PlayerState(
            player_id=0,
            name="Player 0",
            position=0,  # GO
            cash=1500,
            owned_properties={1, 3}
        ),
        PlayerState(
            player_id=1,
            name="Player 1",
            position=10,  # Jail
            cash=1200,
            is_in_jail=True,
            jail_turns=1,
            owned_properties={6, 8, 9}
        ),
        PlayerState(
            player_id=2,
            name="Player 2",
            position=24,  # A property
            cash=800,
            owned_properties={16, 18, 19}
        ),
        PlayerState(
            player_id=3,
            name="Player 3",
            position=37,
            cash=500,
            owned_properties={31, 32, 34}
        ),
    ]

    # Trim to requested number
    players = players[:num_players]

    # Create property states
    properties = {
        1: PropertyState(tile_id=1, owner=0, num_houses=0),
        3: PropertyState(tile_id=3, owner=0, num_houses=0),
        6: PropertyState(tile_id=6, owner=1, num_houses=1),
        8: PropertyState(tile_id=8, owner=1, num_houses=1),
        9: PropertyState(tile_id=9, owner=1, num_houses=2),
        16: PropertyState(tile_id=16, owner=2, num_houses=3),
        18: PropertyState(tile_id=18, owner=2, num_houses=4),
        19: PropertyState(tile_id=19, owner=2, num_houses=5),  # Hotel
        31: PropertyState(tile_id=31, owner=3, num_houses=2),
        32: PropertyState(tile_id=32, owner=3, num_houses=1),
        34: PropertyState(tile_id=34, owner=3, num_houses=0, is_mortgaged=True),
    }

    game_state = GameState(
        players=players,
        current_player_idx=0,
        turn_number=42,
        properties=properties,
        last_dice_roll=(4, 3),
        houses_remaining=25,
        hotels_remaining=11
    )

    return game_state


def demo_static_board():
    """Demo 1: Display a static board with game state."""
    print("Demo 1: Static Board Display")
    print("This demo shows a static game state with multiple players,")
    print("properties, houses, and hotels.")
    print()
    print("Controls:")
    print("  - TAB or 'I' key: Toggle info panel")
    print("  - Click on players: View detailed properties")
    print("  - ESC: Close window")
    print()

    # Create board and renderer (windowed mode)
    board = MonopolyBoard()
    renderer = MonopolyRenderer(board, enable_animation=False, fullscreen=False)

    # Create demo game state
    game_state = create_demo_game_state(num_players=4)

    # Main loop
    running = True
    while running:
        # Handle events
        running = renderer.handle_events(game_state)

        # Render
        renderer.render(game_state)

    renderer.close()


def demo_animated_movement():
    """Demo 2: Animated player movement."""
    print("\nDemo 2: Animated Player Movement")
    print("This demo shows smooth player movement around the board.")
    print()
    print("Controls:")
    print("  - TAB or 'I' key: Toggle info panel")
    print("  - Click on players: View detailed properties")
    print("  - ESC: Close window")
    print()

    # Create board and renderer (windowed mode)
    board = MonopolyBoard()
    renderer = MonopolyRenderer(board, enable_animation=True, fullscreen=False)

    # Create initial game state
    game_state = create_demo_game_state(num_players=4)

    # Movement sequence for player 0
    positions = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

    running = True
    position_idx = 0
    last_move_time = time.time()
    move_interval = 1.0  # seconds between moves

    while running and position_idx < len(positions):
        # Handle events
        running = renderer.handle_events(game_state)

        # Update player position periodically
        current_time = time.time()
        if current_time - last_move_time >= move_interval:
            if position_idx < len(positions):
                game_state.players[0].position = positions[position_idx]
                position_idx += 1
                last_move_time = current_time

        # Render
        renderer.render(game_state)

    renderer.close()


def demo_with_messages():
    """Demo 3: Game with messages and transaction notifications."""
    print("\nDemo 3: Game with Messages and Transaction Notifications")
    print("This demo shows game events with message displays and transaction pop-ups.")
    print("Watch the bottom-right corner for transaction notifications!")
    print()
    print("Controls:")
    print("  - TAB or 'I' key: Toggle info panel")
    print("  - Click on players: View detailed properties")
    print("  - ESC: Close window")
    print()

    # Create board and renderer (windowed mode)
    board = MonopolyBoard()
    renderer = MonopolyRenderer(board, enable_animation=True, fullscreen=False)

    # Create initial game state
    game_state = create_demo_game_state(num_players=4)

    # Event sequence with both messages and transactions
    def add_transaction_buy():
        renderer.add_transaction("Player 0 bought Oriental Avenue for $100")

    def add_transaction_rent():
        renderer.add_transaction("Player 3 paid $200 rent to Player 2")

    def add_transaction_house():
        renderer.add_transaction("Player 2 built a house on New York Avenue")

    def add_transaction_mortgage():
        renderer.add_transaction("Player 1 mortgaged Baltic Avenue for $30")

    events = [
        (1.0, "Player 0 rolls 4, 3", lambda: None),
        (2.0, "Player 0 moves to position 7", lambda: setattr(game_state.players[0], 'position', 7)),
        (3.0, "", add_transaction_buy),
        (4.5, "Player 1 rolls doubles!", lambda: None),
        (5.5, "", add_transaction_mortgage),
        (6.5, "Player 2 builds a house", lambda: None),
        (7.0, "", add_transaction_house),
        (8.5, "Player 3 pays rent", lambda: None),
        (9.0, "", add_transaction_rent),
    ]

    running = True
    start_time = time.time()
    event_idx = 0

    while running and event_idx < len(events):
        # Handle events
        running = renderer.handle_events(game_state)

        # Check for timed events
        current_time = time.time() - start_time
        while event_idx < len(events) and current_time >= events[event_idx][0]:
            _, message, action = events[event_idx]
            if message:  # Only add message if not empty
                renderer.add_message(message)
            action()
            event_idx += 1

        # Render
        renderer.render(game_state)

    # Keep showing for a bit
    end_time = time.time() + 3.0
    while running and time.time() < end_time:
        running = renderer.handle_events(game_state)
        renderer.render(game_state)

    renderer.close()


def demo_interactive():
    """Demo 4: Interactive board with transaction notifications (press SPACE to advance turn)."""
    print("\nDemo 4: Interactive Board with Fullscreen Option")
    print()
    print("Controls:")
    print("  - SPACE: Advance to next turn")
    print("  - TAB or 'I' key: Toggle info panel")
    print("  - Click on players: View detailed properties")
    print("  - ESC: Exit")
    print()

    # Ask user for fullscreen preference
    use_fullscreen = input("Use fullscreen mode? (y/n, default=n): ").strip().lower() == 'y'

    # Create board and renderer
    board = MonopolyBoard()
    renderer = MonopolyRenderer(board, enable_animation=True, fullscreen=use_fullscreen)

    # Create initial game state
    game_state = create_demo_game_state(num_players=4)

    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Advance turn
                    game_state.turn_number += 1
                    current_player = game_state.current_player()

                    # Move current player forward
                    dice1 = (game_state.turn_number * 3) % 6 + 1
                    dice2 = (game_state.turn_number * 5) % 6 + 1
                    game_state.last_dice_roll = (dice1, dice2)

                    old_position = current_player.position
                    new_position = (current_player.position + dice1 + dice2) % board.num_tiles
                    current_player.position = new_position

                    # Message
                    renderer.add_message(f"Player {current_player.player_id} rolls {dice1}, {dice2}")

                    # Add transaction notification based on the tile
                    try:
                        tile_info = board.get_tile(new_position)
                        if tile_info.tile_type.name == "PROPERTY":
                            renderer.add_transaction(f"Player {current_player.player_id} landed on {tile_info.name}")
                        elif tile_info.tile_type.name == "RAILROAD":
                            renderer.add_transaction(f"Player {current_player.player_id} visited {tile_info.name}")
                        elif tile_info.tile_type.name == "UTILITY":
                            renderer.add_transaction(f"Player {current_player.player_id} landed on {tile_info.name}")
                    except:
                        pass

                    # Next player
                    game_state.current_player_idx = (game_state.current_player_idx + 1) % len(game_state.players)
                elif event.key == pygame.K_TAB or event.key == pygame.K_i:
                    # Toggle info panel
                    renderer.info_panel_visible = not renderer.info_panel_visible
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle clicks on info panel
                if renderer.info_panel_visible:
                    renderer.info_panel.handle_click(event.pos, game_state)

        # Render
        renderer.render(game_state)

    renderer.close()


def main():
    """Run all demos."""
    print("="*60)
    print("Monopoly AI - Visualization Demo")
    print("="*60)
    print()

    demos = [
        ("Static Board", demo_static_board),
        ("Animated Movement", demo_animated_movement),
        ("Messages", demo_with_messages),
        ("Interactive", demo_interactive),
    ]

    print("Available demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print(f"  {len(demos) + 1}. Run all demos")
    print()

    try:
        choice = input("Select demo (1-5) or press Enter for all: ").strip()

        if not choice:
            choice = str(len(demos) + 1)

        choice_num = int(choice)

        if 1 <= choice_num <= len(demos):
            # Run single demo
            name, demo_func = demos[choice_num - 1]
            print(f"\nRunning: {name}")
            print("-" * 60)
            demo_func()
        elif choice_num == len(demos) + 1:
            # Run all demos
            for name, demo_func in demos:
                print(f"\nRunning: {name}")
                print("-" * 60)
                demo_func()
        else:
            print("Invalid choice")
            return

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nError running demo: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()

    print("\n" + "="*60)
    print("Demo complete!")
    print("="*60)


if __name__ == "__main__":
    main()
