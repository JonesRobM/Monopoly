"""
Quick test script to verify visualization works.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pygame
from engine.board import MonopolyBoard
from engine.state import GameState, PlayerState, PropertyState
from visualization.renderer import MonopolyRenderer


def test_basic_rendering():
    """Test that basic rendering works without errors."""
    print("Creating board...")
    board = MonopolyBoard()

    print("Creating renderer...")
    renderer = MonopolyRenderer(board, window_width=1200, enable_animation=False)

    print("Creating game state...")
    players = [
        PlayerState(
            player_id=0,
            name="Player 0",
            position=0,
            cash=1500,
            owned_properties={1, 3}
        ),
        PlayerState(
            player_id=1,
            name="Player 1",
            position=10,
            cash=1200,
            owned_properties={6, 8, 9}
        ),
    ]

    properties = {
        1: PropertyState(tile_id=1, owner=0, num_houses=2),
        3: PropertyState(tile_id=3, owner=0, num_houses=0),
        6: PropertyState(tile_id=6, owner=1, num_houses=1),
        8: PropertyState(tile_id=8, owner=1, num_houses=1),
        9: PropertyState(tile_id=9, owner=1, num_houses=1),
    }

    state = GameState(
        players=players,
        current_player_idx=0,
        turn_number=10,
        properties=properties,
        houses_remaining=28,
        hotels_remaining=12
    )

    print("Rendering frame...")
    renderer.render(state)

    print("Waiting 2 seconds...")
    pygame.time.wait(2000)

    print("Closing renderer...")
    renderer.close()

    print("SUCCESS: Visualization test passed!")


if __name__ == "__main__":
    test_basic_rendering()
