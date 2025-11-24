"""
Save full-resolution board image (11,264×11,264 pixels).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pygame
from engine.board import MonopolyBoard
from engine.state import GameState, PlayerState, PropertyState
from visualization.board_layout import BoardLayout
from visualization.tile_renderer import TileRenderer


def create_test_state() -> GameState:
    """Create a test game state with some properties owned."""
    players = [
        PlayerState(player_id=0, name="Player 0", position=0, cash=1500, owned_properties={1, 3}),
        PlayerState(player_id=1, name="Player 1", position=10, cash=1200, owned_properties={6, 8, 9}),
        PlayerState(player_id=2, name="Player 2", position=24, cash=800, owned_properties={16, 18, 19}),
        PlayerState(player_id=3, name="Player 3", position=37, cash=500, owned_properties={31, 32}),
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
    """Generate full-resolution board image."""
    print("Creating board components...")
    board = MonopolyBoard()
    layout = BoardLayout(num_tiles=40)
    tile_renderer = TileRenderer()

    print(f"Board size: {layout.board_size}×{layout.board_size} pixels")

    # Initialize pygame
    pygame.init()

    # Create surface for the full board
    print("Creating full-resolution surface (this may take a moment)...")
    board_surface = pygame.Surface((layout.board_size, layout.board_size))
    board_surface.fill((240, 240, 230))  # Light beige background

    print("Creating test game state...")
    state = create_test_state()

    print("Rendering all tiles...")
    for tile_id in range(board.num_tiles):
        tile_info = board.get_tile(tile_id)
        position = layout.get_tile_position(tile_id)

        # Check if property is mortgaged
        is_mortgaged = False
        if tile_id in state.properties:
            prop_state = state.properties[tile_id]
            is_mortgaged = prop_state.is_mortgaged

        tile_renderer.render_tile(
            board_surface,
            tile_info,
            position,
            is_mortgaged=is_mortgaged
        )

        if (tile_id + 1) % 10 == 0:
            print(f"  Rendered {tile_id + 1}/{board.num_tiles} tiles...")

    # Save full-resolution image
    output_path = "full_board_11264px.png"
    print(f"\nSaving full-resolution image to {output_path}...")
    pygame.image.save(board_surface, output_path)

    print(f"✓ Saved successfully!")
    print(f"\nBoard specifications:")
    print(f"  Total size: {layout.board_size}×{layout.board_size} pixels")
    print(f"  Corner tiles: {layout.corner_size}×{layout.corner_size} pixels")
    print(f"  Horizontal tiles: {layout.edge_tile_long}×{layout.edge_tile_short} pixels (4:1 ratio)")
    print(f"  Vertical tiles: {layout.edge_tile_short}×{layout.edge_tile_long} pixels (4:1 ratio)")
    print(f"  Font: Comic Sans MS (cartoonish style)")

    pygame.quit()
    print("\nDone!")


if __name__ == "__main__":
    main()
