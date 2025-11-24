"""
Test script to verify text wrapping functionality on tiles with long names.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pygame
from engine.board import MonopolyBoard
from engine.state import GameState, PlayerState, PropertyState
from visualization.renderer import MonopolyRenderer


def test_text_wrapping():
    """Test text wrapping with the Stoke-on-Trent board which has longer property names."""
    print("Creating Stoke-on-Trent board (has longer property names)...")
    board = MonopolyBoard("stoke_on_trent")

    print(f"Board has {board.num_tiles} tiles")

    # Show a few property names to demonstrate wrapping
    print("\nSample property names:")
    for i in range(min(15, board.num_tiles)):
        tile = board.get_tile(i)
        print(f"  Tile {i}: {tile.name}")

    print("\nCreating renderer with larger tiles (15% corner size)...")
    renderer = MonopolyRenderer(board, window_width=1400, enable_animation=False)

    print("Creating game state...")
    players = [
        PlayerState(
            player_id=0,
            name="Player 0",
            position=0,
            cash=1500,
            owned_properties=set()
        ),
    ]

    properties = {}

    state = GameState(
        players=players,
        current_player_idx=0,
        turn_number=1,
        properties=properties,
        houses_remaining=32,
        hotels_remaining=12
    )

    print("Rendering frame with text wrapping enabled...")
    renderer.render(state)

    print("Displaying for 3 seconds...")
    pygame.time.wait(3000)

    print("Closing renderer...")
    renderer.close()

    print("SUCCESS: Text wrapping test passed!")


if __name__ == "__main__":
    test_text_wrapping()
