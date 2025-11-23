"""
Board Configuration Demo - No NumPy Required
Demonstrates the board selector system without environment dependencies.
"""

from engine import MonopolyBoard
from engine.board_config import list_available_boards
from engine.state import PropertyGroup


def main():
    print("\n" + "="*70)
    print("MONOPOLY BOARD SELECTOR DEMONSTRATION")
    print("="*70)

    # List available boards
    available = list_available_boards()
    print(f"\nAvailable board configurations: {available}")

    # Load default board (Stoke-on-Trent)
    print("\n" + "-"*70)
    print("DEFAULT BOARD: STOKE-ON-TRENT")
    print("-"*70)

    board = MonopolyBoard()
    print(f"\nBoard Name: {board.metadata.name}")
    print(f"Description: {board.metadata.description}")
    print(f"Total Tiles: {board.num_tiles}")
    print(f"GO Salary: {board.metadata.currency_symbol}{board.metadata.go_salary}")

    # Show sample properties
    print(f"\n{'Tile':<6} {'Type':<20} {'Name':<45}")
    print("-"*70)
    sample_tiles = [0, 1, 4, 12, 20, 25, 32, 33, 36, 40]
    for tile_id in sample_tiles:
        tile = board.get_tile(tile_id)
        print(f"{tile_id:<6} {tile.tile_type.value:<20} {tile.name:<45}")

    # Show property groups
    print(f"\n{'='*70}")
    print("PROPERTY GROUPS")
    print("="*70)

    groups = [
        PropertyGroup.BROWN, PropertyGroup.LIGHT_BLUE, PropertyGroup.PURPLE,
        PropertyGroup.ORANGE, PropertyGroup.RED, PropertyGroup.YELLOW,
        PropertyGroup.GREEN, PropertyGroup.DARK_BLUE, PropertyGroup.SPECIAL
    ]

    for group in groups:
        tiles = board.get_group_tiles(group)
        if tiles:
            print(f"\n{group.value.upper()} ({len(tiles)} properties):")
            for tile_id in tiles:
                tile = board.get_tile(tile_id)
                price = board.get_purchase_price(tile_id)
                print(f"  • {tile.name:<50} (£{price})")

    # Compare with classic board
    print(f"\n{'='*70}")
    print("CLASSIC BOARD COMPARISON")
    print("="*70)

    classic_board = MonopolyBoard(use_hardcoded=True)
    print(f"\nStoke-on-Trent Board: {board.num_tiles} tiles")
    print(f"Classic Board:        {classic_board.num_tiles} tiles")
    print(f"Difference:           +{board.num_tiles - classic_board.num_tiles} tile")

    print(f"\nStoke-on-Trent Tile 1:  {board.get_tile(1).name}")
    print(f"Classic Tile 1:         {classic_board.get_tile(1).name}")

    print(f"\nStoke-on-Trent Tile 25: {board.get_tile(25).name}")
    print(f"Classic Tile 25:        {classic_board.get_tile(25).name}")

    # Show special group (unique to Stoke board)
    special = board.get_group_tiles(PropertyGroup.SPECIAL)
    print(f"\n{'='*70}")
    print(f"SPECIAL GROUP - Unique to Stoke-on-Trent ({len(special)} properties)")
    print("="*70)
    print("\nThis group doesn't exist in the classic board!")
    for tile_id in special:
        tile = board.get_tile(tile_id)
        print(f"  • {tile.name}")

    print("\n" + "="*70)
    print("Board selector demonstration complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
