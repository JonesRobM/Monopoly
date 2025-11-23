"""
Demonstration of board configuration system.

Shows how to:
1. Load the default Stoke-on-Trent board
2. Load specific board by name
3. Use the hardcoded classic board
4. Access board metadata and tiles
"""

from engine.board import MonopolyBoard
from engine.board_config import list_available_boards
from engine.state import PropertyGroup


def demonstrate_default_board():
    """Load and display the default Stoke-on-Trent board."""
    print("=" * 70)
    print("DEFAULT BOARD (Stoke-on-Trent)")
    print("=" * 70)

    board = MonopolyBoard()

    print(f"\nBoard Name: {board.metadata.name}")
    print(f"Description: {board.metadata.description}")
    print(f"Currency: {board.metadata.currency_symbol}")
    print(f"GO Salary: {board.metadata.currency_symbol}{board.metadata.go_salary}")
    print(f"Number of Tiles: {board.num_tiles}")

    print(f"\nProperty Groups:")
    for group, tile_ids in sorted(board.property_groups.items(), key=lambda x: x[0].value):
        print(f"  {group.value:15s}: {len(tile_ids)} tiles - {tile_ids}")

    print(f"\nSample Tiles:")
    print(f"  Tile 0:  {board.tiles[0].name} ({board.tiles[0].tile_type.value})")
    print(f"  Tile 1:  {board.tiles[1].name} ({board.tiles[1].tile_type.value})")
    print(f"  Tile 4:  {board.tiles[4].name} ({board.tiles[4].tile_type.value})")
    print(f"  Tile 33: {board.tiles[33].name} ({board.tiles[33].tile_type.value})")
    print(f"  Tile 40: {board.tiles[40].name} ({board.tiles[40].tile_type.value})")

    print(f"\nSpecial Property Group (unique to this board):")
    special_tiles = board.property_groups[PropertyGroup.SPECIAL]
    for tile_id in special_tiles:
        tile = board.tiles[tile_id]
        print(f"  Tile {tile_id:2d}: {tile.name:40s} "
              f"({board.metadata.currency_symbol}{tile.property_info.purchase_price})")


def demonstrate_hardcoded_board():
    """Load and display the hardcoded classic board."""
    print("\n\n")
    print("=" * 70)
    print("HARDCODED CLASSIC BOARD")
    print("=" * 70)

    board = MonopolyBoard(use_hardcoded=True)

    print(f"\nNumber of Tiles: {board.num_tiles}")
    print(f"Metadata: {board.metadata}")

    print(f"\nProperty Groups:")
    for group, tile_ids in sorted(board.property_groups.items(), key=lambda x: x[0].value):
        print(f"  {group.value:15s}: {len(tile_ids)} tiles")

    print(f"\nSample Tiles:")
    print(f"  Tile 0:  {board.tiles[0].name}")
    print(f"  Tile 1:  {board.tiles[1].name}")
    print(f"  Tile 39: {board.tiles[39].name}")


def demonstrate_board_discovery():
    """Show how to discover available boards."""
    print("\n\n")
    print("=" * 70)
    print("AVAILABLE BOARDS")
    print("=" * 70)

    boards = list_available_boards()
    print(f"\nFound {len(boards)} board configuration(s):")
    for board_name in boards:
        print(f"  - {board_name}")


def demonstrate_property_details():
    """Show detailed property information."""
    print("\n\n")
    print("=" * 70)
    print("PROPERTY DETAILS EXAMPLE")
    print("=" * 70)

    board = MonopolyBoard()

    # Show a brown property
    brown_tile = board.tiles[1]
    print(f"\nBrown Property: {brown_tile.name}")
    print(f"  Purchase Price:    {board.metadata.currency_symbol}{brown_tile.property_info.purchase_price}")
    print(f"  Base Rent:         {board.metadata.currency_symbol}{brown_tile.property_info.base_rent}")
    print(f"  Rent (1 house):    {board.metadata.currency_symbol}{brown_tile.property_info.rent_with_1_house}")
    print(f"  Rent (2 houses):   {board.metadata.currency_symbol}{brown_tile.property_info.rent_with_2_houses}")
    print(f"  Rent (3 houses):   {board.metadata.currency_symbol}{brown_tile.property_info.rent_with_3_houses}")
    print(f"  Rent (4 houses):   {board.metadata.currency_symbol}{brown_tile.property_info.rent_with_4_houses}")
    print(f"  Rent (hotel):      {board.metadata.currency_symbol}{brown_tile.property_info.rent_with_hotel}")
    print(f"  House Cost:        {board.metadata.currency_symbol}{brown_tile.property_info.house_cost}")
    print(f"  Mortgage Value:    {board.metadata.currency_symbol}{brown_tile.property_info.mortgage_value}")

    # Show a station/railroad
    station_tile = board.tiles[4]
    print(f"\nStation: {station_tile.name}")
    print(f"  Purchase Price:    {board.metadata.currency_symbol}{station_tile.railroad_info.purchase_price}")
    print(f"  Mortgage Value:    {board.metadata.currency_symbol}{station_tile.railroad_info.mortgage_value}")
    print(f"  Rent (1 station):  {board.metadata.currency_symbol}{station_tile.railroad_info.get_rent(1)}")
    print(f"  Rent (2 stations): {board.metadata.currency_symbol}{station_tile.railroad_info.get_rent(2)}")
    print(f"  Rent (3 stations): {board.metadata.currency_symbol}{station_tile.railroad_info.get_rent(3)}")
    print(f"  Rent (4 stations): {board.metadata.currency_symbol}{station_tile.railroad_info.get_rent(4)}")

    # Show a utility
    utility_tile = board.tiles[16]
    print(f"\nUtility: {utility_tile.name}")
    print(f"  Purchase Price:    {board.metadata.currency_symbol}{utility_tile.utility_info.purchase_price}")
    print(f"  Mortgage Value:    {board.metadata.currency_symbol}{utility_tile.utility_info.mortgage_value}")
    print(f"  Rent multiplier:   4x dice roll (1 utility) or 10x (2 utilities)")


def main():
    """Run all demonstrations."""
    demonstrate_default_board()
    demonstrate_hardcoded_board()
    demonstrate_board_discovery()
    demonstrate_property_details()
    print("\n")


if __name__ == "__main__":
    main()
