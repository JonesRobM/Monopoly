"""
Test script to demonstrate the enhanced center panel visualization.

Shows turn indicator and property ownership with houses/hotels and mortgage status.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pygame
from engine.board import MonopolyBoard
from engine.state import GameState, PlayerState, PropertyState
from visualization.renderer import MonopolyRenderer


def test_center_panel():
    """Test the enhanced center panel with property details."""
    print("Creating board...")
    board = MonopolyBoard()

    print("Creating renderer...")
    renderer = MonopolyRenderer(board, window_width=1200, enable_animation=False)

    print("Creating game state with multiple players and properties...")

    # Create 4 players with various properties
    players = [
        PlayerState(
            player_id=0,
            name="Player 0",
            position=5,
            cash=1500,
            owned_properties={1, 3, 6, 8, 9}  # Multiple properties
        ),
        PlayerState(
            player_id=1,
            name="Player 1",
            position=15,
            cash=2000,
            owned_properties={11, 13, 14}
        ),
        PlayerState(
            player_id=2,
            name="Player 2",
            position=25,
            cash=800,
            owned_properties={16, 18, 19}
        ),
        PlayerState(
            player_id=3,
            name="Player 3",
            position=35,
            cash=1200,
            owned_properties={21, 23, 24}
        ),
    ]

    # Create properties with various states
    properties = {
        # Player 0 properties
        1: PropertyState(tile_id=1, owner=0, num_houses=2),  # 2 houses
        3: PropertyState(tile_id=3, owner=0, num_houses=0),  # No development
        6: PropertyState(tile_id=6, owner=0, num_houses=4),  # 4 houses
        8: PropertyState(tile_id=8, owner=0, num_houses=5),  # Hotel!
        9: PropertyState(tile_id=9, owner=0, num_houses=1, is_mortgaged=True),  # Mortgaged

        # Player 1 properties
        11: PropertyState(tile_id=11, owner=1, num_houses=0),
        13: PropertyState(tile_id=13, owner=1, num_houses=3),
        14: PropertyState(tile_id=14, owner=1, num_houses=0, is_mortgaged=True),

        # Player 2 properties
        16: PropertyState(tile_id=16, owner=2, num_houses=1),
        18: PropertyState(tile_id=18, owner=2, num_houses=2),
        19: PropertyState(tile_id=19, owner=2, num_houses=5),  # Hotel

        # Player 3 properties
        21: PropertyState(tile_id=21, owner=3, num_houses=0),
        23: PropertyState(tile_id=23, owner=3, num_houses=1),
        24: PropertyState(tile_id=24, owner=3, num_houses=0),
    }

    state = GameState(
        players=players,
        current_player_idx=1,  # Player 1's turn
        turn_number=42,  # Show a higher turn number
        properties=properties,
        houses_remaining=18,
        hotels_remaining=8
    )

    print("Rendering enhanced center panel...")
    print("- Turn indicator should show: 'Turn 42 - Player 1's Turn' in center")
    print("- Each player's properties should be listed with:")
    print("  * Property names (not just IDs)")
    print("  * Houses: [1h], [2h], [3h], [4h]")
    print("  * Hotels: [H]")
    print("  * Mortgaged: (M)")

    renderer.render(state)

    print("\nVisualization displayed! Press any key or wait 10 seconds...")

    # Wait for user input or timeout
    running = True
    clock = pygame.time.Clock()
    timeout = 10000  # 10 seconds
    start_time = pygame.time.get_ticks()

    while running and (pygame.time.get_ticks() - start_time) < timeout:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                running = False

        clock.tick(30)

    print("Closing renderer...")
    renderer.close()

    print("\nSUCCESS: Center panel visualization test completed!")
    print("\nExpected features:")
    print("1. Turn indicator in center showing current player")
    print("2. Property lists for each player")
    print("3. Building indicators: [1h]-[4h] for houses, [H] for hotels")
    print("4. Mortgage indicator: (M) for mortgaged properties")


if __name__ == "__main__":
    test_center_panel()
