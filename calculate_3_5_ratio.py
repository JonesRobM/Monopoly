"""Calculate tile dimensions for 1:1 corners and 3:5 edge tiles."""

# For a 960px board:
# Requirements:
# - Corners: 1:1 (square) -> corner_width = corner_height
# - Edge tiles: 3:5 (parallel:perpendicular) -> width:height = 3:5
#   If width = 3x, then height = 5x

# Let's denote:
# - corner size = c (square, so c × c)
# - edge_tile_long = 3x (parallel to flow)
# - edge_tile_short = 5x (perpendicular to flow)

# Board dimensions:
# Width = 2c + 9(3x) = 2c + 27x = 960
# Height = 2c + 9(3x) = 2c + 27x = 960 (board is square)

# Let's try x = 28:
# 2c + 27(28) = 960
# 2c + 756 = 960
# 2c = 204
# c = 102

board_size = 960
x = 28
corner_size = 102
edge_long = 3 * x  # 84
edge_short = 5 * x  # 140

print("Tile Dimension Calculation (3:5 Aspect Ratio)")
print("=" * 50)
print(f"Board size: {board_size}px")
print()
print("Corner tiles (1:1 aspect ratio):")
print(f"  Size: {corner_size} × {corner_size}")
print(f"  Aspect ratio: {corner_size/corner_size:.2f}:1")
print()
print("Edge tiles (3:5 aspect ratio):")
print(f"  Parallel (width): {edge_long}px")
print(f"  Perpendicular (height): {edge_short}px")
print(f"  Aspect ratio: {edge_long}:{edge_short} = 3:5")
print(f"  Decimal ratio: {edge_short/edge_long:.2f}:1")
print()

# Verify board dimensions
board_width = corner_size + 9 * edge_long + corner_size
board_height = corner_size + 9 * edge_long + corner_size

print("Board dimensions:")
print(f"  Width: {board_width}px (expected {board_size}px)")
print(f"  Height: {board_height}px (expected {board_size}px)")
print()

# Verify the 3:5 ratio
if edge_long * 5 == edge_short * 3:
    print("[OK] Edge tiles have exact 3:5 ratio!")
else:
    print(f"[X] Ratio not exact: {edge_long}:{edge_short}")

if board_width == board_size and board_height == board_size:
    print("[OK] Board dimensions match target!")
    print()
    print("Summary:")
    print(f"  corner_width = {corner_size}")
    print(f"  corner_height = {corner_size}")
    print(f"  edge_tile_long = {edge_long}")
    print(f"  edge_tile_short = {edge_short}")
else:
    print("[X] Board dimensions don't match!")
