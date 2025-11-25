"""
Analyze tile aspect ratios in the current board layout.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from visualization.board_layout import BoardLayout


def analyze_aspect_ratios(board_size: int = 800):
    """Analyze the aspect ratios of tiles in the current layout."""

    # Create layout for 40-tile board
    layout = BoardLayout(num_tiles=40, board_size=board_size)

    print("="*70)
    print(f"ASPECT RATIO ANALYSIS (Board Size: {board_size}px)")
    print("="*70)
    print()

    print(f"Corner size: {layout.corner_size}px")
    print(f"Edge tile width: {layout.edge_tile_width}px")
    print(f"Edge tile height: {layout.edge_tile_height}px")
    print()

    # Calculate ratios (using actual tile dimensions)
    horizontal_ratio = layout.edge_tile_width / layout.edge_tile_height
    vertical_ratio = layout.edge_tile_width / layout.edge_tile_height  # Same ratio, just rotated

    print("HORIZONTAL TILES (Top/Bottom edges):")
    print(f"  Dimensions: {layout.edge_tile_width}px (width) × {layout.edge_tile_height}px (height)")
    print(f"  Aspect Ratio: {horizontal_ratio:.2f}:1")
    print(f"  Target: 2.5:1")
    print(f"  Difference: {horizontal_ratio - 2.5:+.2f}")
    if abs(horizontal_ratio - 2.5) < 0.1:
        print(f"  [OK] Within acceptable range!")
    print()

    print("VERTICAL TILES (Left/Right edges):")
    print(f"  Dimensions: {layout.edge_tile_height}px (width) × {layout.edge_tile_width}px (height)")
    print(f"  Aspect Ratio: 1:{vertical_ratio:.2f} (height/width = {vertical_ratio:.2f}:1)")
    print(f"  Target: 1:2.5 (height/width = 2.5:1)")
    print(f"  Difference: {vertical_ratio - 2.5:+.2f}")
    if abs(vertical_ratio - 2.5) < 0.1:
        print(f"  [OK] Within acceptable range!")
    print()

    # Check corner tiles
    print("CORNER TILES:")
    print(f"  Dimensions: {layout.corner_size}px × {layout.corner_size}px")
    print(f"  Aspect Ratio: 1:1 (square) [OK]")
    print()

    # Calculate what the dimensions should be for 2.5:1 ratio
    print("="*70)
    print("RECOMMENDED ADJUSTMENTS FOR 2.5:1 RATIO")
    print("="*70)
    print()

    # Available space after corners
    available_space = board_size - (2 * layout.corner_size)

    # For 2.5:1 ratio on horizontal tiles
    # width / height = 2.5
    # height = corner_size
    # So width = 2.5 * corner_size
    ideal_horizontal_width = 2.5 * layout.corner_size

    # For 2.5:1 ratio on vertical tiles
    # height / width = 2.5
    # width = corner_size
    # So height = 2.5 * corner_size
    ideal_vertical_height = 2.5 * layout.corner_size

    print(f"For 2.5:1 ratio with corner_size = {layout.corner_size}px:")
    print(f"  Horizontal tiles should be: {ideal_horizontal_width:.1f}px × {layout.corner_size}px")
    print(f"  Vertical tiles should be: {layout.corner_size}px × {ideal_vertical_height:.1f}px")
    print()

    # Check if this fits
    num_horizontal_edges = 9  # Between corners on top/bottom
    total_horizontal_space_needed = num_horizontal_edges * ideal_horizontal_width

    num_vertical_edges = 9  # On left/right
    total_vertical_space_needed = num_vertical_edges * ideal_vertical_height

    print(f"Space check:")
    print(f"  Horizontal: Need {total_horizontal_space_needed:.1f}px, Have {available_space}px")
    if total_horizontal_space_needed <= available_space:
        print(f"  [OK] Fits! ({available_space - total_horizontal_space_needed:.1f}px spare)")
    else:
        print(f"  [X] Too large by {total_horizontal_space_needed - available_space:.1f}px")

    print(f"  Vertical: Need {total_vertical_space_needed:.1f}px, Have {available_space}px")
    if total_vertical_space_needed <= available_space:
        print(f"  [OK] Fits! ({available_space - total_vertical_space_needed:.1f}px spare)")
    else:
        print(f"  [X] Too large by {total_vertical_space_needed - available_space:.1f}px")
    print()

    # Suggest optimal corner size
    # For horizontal: 9 * (2.5 * corner) <= board_size - 2*corner
    # 22.5 * corner <= board_size - 2*corner
    # 24.5 * corner <= board_size
    # corner <= board_size / 24.5

    # For vertical: 9 * (2.5 * corner) <= board_size - 2*corner
    # Same calculation

    max_corner_for_25_ratio = board_size / 24.5

    print(f"OPTIMAL CORNER SIZE for 2.5:1 ratio:")
    print(f"  Maximum corner size: {max_corner_for_25_ratio:.1f}px ({max_corner_for_25_ratio/board_size*100:.1f}% of board)")
    print(f"  Current corner size: {layout.corner_size}px ({layout.corner_size/board_size*100:.1f}% of board)")
    print()

    if layout.corner_size > max_corner_for_25_ratio:
        print(f"  [WARNING] Current corner size is too large for 2.5:1 ratio!")
        print(f"  Recommended: {int(max_corner_for_25_ratio)}px")
    else:
        print(f"  [OK] Corner size is appropriate")

    print()
    print("="*70)

    # Sample a few tile positions
    print("\nSAMPLE TILE DIMENSIONS:")
    print("="*70)

    sample_tiles = [
        (0, "GO - Bottom-right corner"),
        (1, "First property - Bottom edge"),
        (10, "Jail - Bottom-left corner"),
        (11, "First property - Left edge"),
        (20, "Free Parking - Top-left corner"),
        (21, "First property - Top edge"),
        (30, "Go to Jail - Top-right corner"),
        (31, "First property - Right edge"),
    ]

    for tile_id, description in sample_tiles:
        pos = layout.get_tile_position(tile_id)
        ratio = pos.width / pos.height if pos.height > 0 else 0
        print(f"Tile {tile_id:2d} ({pos.side:6s}): {int(pos.width):3d}×{int(pos.height):3d}px, ratio {ratio:.2f}:1 - {description}")

    print()


if __name__ == "__main__":
    analyze_aspect_ratios(800)
