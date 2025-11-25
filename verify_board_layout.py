"""
Verification script to confirm the board layout matches the correct Monopoly order.
"""

from engine.board import MonopolyBoard
from engine.state import TileType

# Expected layout
EXPECTED_LAYOUT = [
    (0, "GO", TileType.GO),
    (1, "Mediterranean Avenue", TileType.PROPERTY),
    (2, "Community Chest", TileType.COMMUNITY_CHEST),
    (3, "Baltic Avenue", TileType.PROPERTY),
    (4, "Income Tax", TileType.TAX),
    (5, "Reading Railroad", TileType.RAILROAD),
    (6, "Oriental Avenue", TileType.PROPERTY),
    (7, "Chance", TileType.CHANCE),
    (8, "Vermont Avenue", TileType.PROPERTY),
    (9, "Connecticut Avenue", TileType.PROPERTY),
    (10, "Jail / Just Visiting", TileType.JAIL),
    (11, "St. Charles Place", TileType.PROPERTY),
    (12, "Electric Company", TileType.UTILITY),
    (13, "States Avenue", TileType.PROPERTY),
    (14, "Virginia Avenue", TileType.PROPERTY),
    (15, "Pennsylvania Railroad", TileType.RAILROAD),
    (16, "St. James Place", TileType.PROPERTY),
    (17, "Community Chest", TileType.COMMUNITY_CHEST),
    (18, "Tennessee Avenue", TileType.PROPERTY),
    (19, "New York Avenue", TileType.PROPERTY),
    (20, "Free Parking", TileType.FREE_PARKING),
    (21, "Kentucky Avenue", TileType.PROPERTY),
    (22, "Chance", TileType.CHANCE),
    (23, "Indiana Avenue", TileType.PROPERTY),
    (24, "Illinois Avenue", TileType.PROPERTY),
    (25, "B&O Railroad", TileType.RAILROAD),
    (26, "Atlantic Avenue", TileType.PROPERTY),
    (27, "Ventnor Avenue", TileType.PROPERTY),
    (28, "Water Works", TileType.UTILITY),
    (29, "Marvin Gardens", TileType.PROPERTY),
    (30, "Go To Jail", TileType.GOTO_JAIL),
    (31, "Pacific Avenue", TileType.PROPERTY),
    (32, "North Carolina Avenue", TileType.PROPERTY),
    (33, "Community Chest", TileType.COMMUNITY_CHEST),
    (34, "Pennsylvania Avenue", TileType.PROPERTY),
    (35, "Short Line", TileType.RAILROAD),
    (36, "Chance", TileType.CHANCE),
    (37, "Park Place", TileType.PROPERTY),
    (38, "Luxury Tax", TileType.TAX),
    (39, "Boardwalk", TileType.PROPERTY),
]

def verify_board():
    """Verify the board matches the expected layout."""
    print("Verifying Monopoly board layout...\n")

    # Load default board (should be US Standard now)
    board = MonopolyBoard()

    print(f"Board metadata:")
    print(f"  Name: {board.metadata.name}")
    print(f"  Tiles: {board.metadata.num_tiles}")
    print(f"  Currency: {board.metadata.currency_symbol}")
    print(f"  GO salary: {board.metadata.go_salary}")
    print()

    all_correct = True
    errors = []

    for expected_id, expected_name, expected_type in EXPECTED_LAYOUT:
        tile = board.get_tile(expected_id)

        if tile.name != expected_name or tile.tile_type != expected_type:
            all_correct = False
            errors.append(
                f"  Tile {expected_id}: Expected '{expected_name}' ({expected_type}), "
                f"got '{tile.name}' ({tile.tile_type})"
            )
        else:
            print(f"  Tile {expected_id:2d}: {tile.name:30s} [{tile.tile_type.value}] OK")

    print()

    if all_correct:
        print("SUCCESS: All tiles match the correct Monopoly board layout!")
        print()
        print("Corner tiles verification:")
        print(f"  Tile 0  (GO): {board.get_tile(0).name}")
        print(f"  Tile 10 (Jail): {board.get_tile(10).name}")
        print(f"  Tile 20 (Free Parking): {board.get_tile(20).name}")
        print(f"  Tile 30 (Go To Jail): {board.get_tile(30).name}")
        print()
        print("Property groups:")
        for group_name in ["BROWN", "LIGHT_BLUE", "PINK", "ORANGE", "RED",
                          "YELLOW", "GREEN", "DARK_BLUE", "RAILROAD", "UTILITY"]:
            from engine.state import PropertyGroup
            group = PropertyGroup[group_name]
            tiles = board.get_group_tiles(group)
            print(f"  {group_name:12s}: {tiles}")
    else:
        print("ERRORS FOUND:")
        for error in errors:
            print(error)
        return False

    return True


if __name__ == "__main__":
    success = verify_board()
    exit(0 if success else 1)
