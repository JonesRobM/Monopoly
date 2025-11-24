"""
Quick test to generate a screenshot of the board for visual verification.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pygame
from engine.board import MonopolyBoard
from engine.state import GameState, PlayerState, PropertyState
from visualization.renderer import MonopolyRenderer


def create_test_state() -> GameState:
    """Create a test game state with some properties owned."""
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
        PlayerState(
            player_id=2,
            name="Player 2",
            position=24,
            cash=800,
            owned_properties={16, 18, 19}
        ),
        PlayerState(
            player_id=3,
            name="Player 3",
            position=37,
            cash=500,
            owned_properties={31, 32}
        ),
    ]

    properties = {
        1: PropertyState(tile_id=1, owner=0, num_houses=1),
        3: PropertyState(tile_id=3, owner=0, num_houses=0),
        6: PropertyState(tile_id=6, owner=1, num_houses=2),
        8: PropertyState(tile_id=8, owner=1, num_houses=1),
        9: PropertyState(tile_id=9, owner=1, num_houses=1),
        16: PropertyState(tile_id=16, owner=2, num_houses=3),
        18: PropertyState(tile_id=18, owner=2, num_houses=4),
        19: PropertyState(tile_id=19, owner=2, num_houses=5),
        31: PropertyState(tile_id=31, owner=3, num_houses=2),
        32: PropertyState(tile_id=32, owner=3, num_houses=1),
    }

    return GameState(
        players=players,
        current_player_idx=0,
        turn_number=25,
        properties=properties,
        houses_remaining=25,
        hotels_remaining=11
    )


def main():
    """Generate screenshot of the board."""
    print("Creating board and renderer...")
    board = MonopolyBoard()
    renderer = MonopolyRenderer(board, window_width=1200, enable_animation=False)

    print("Creating test game state...")
    state = create_test_state()

    print("Rendering board...")
    renderer.render(state)

    # Wait a moment for rendering to complete
    pygame.time.wait(500)

    # Save screenshot
    screenshot_path = "board_screenshot.png"
    print(f"Saving screenshot to {screenshot_path}...")
    renderer.save_screenshot(screenshot_path)

    print(f"Screenshot saved successfully!")
    print(f"\nCheck {screenshot_path} to verify:")
    print("  - Horizontal tiles are wide rectangles (2.5:1 ratio)")
    print("  - Vertical tiles are tall rectangles (2.5:1 ratio)")
    print("  - Corner tiles are square")
    print("  - Text is rotated correctly for each side")
    print("  - Color bands are positioned correctly")

    renderer.close()
    print("\nDone!")


if __name__ == "__main__":
    main()
