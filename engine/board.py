"""
Board representation for Monopoly.

Defines the standard 40-tile Monopoly board with all properties, railroads,
utilities, and special tiles.
"""

from typing import Dict, List, Set
from engine.state import (
    TileInfo, TileType, PropertyInfo, RailroadInfo, UtilityInfo,
    PropertyGroup
)


class MonopolyBoard:
    """
    Standard Monopoly board with 40 tiles.

    Tile numbering: 0 (GO) to 39 (Boardwalk)
    """

    def __init__(self):
        """Initialize the standard Monopoly board."""
        self.tiles: Dict[int, TileInfo] = self._create_board()
        self.property_groups: Dict[PropertyGroup, List[int]] = self._create_property_groups()

    def _create_board(self) -> Dict[int, TileInfo]:
        """Create all 40 tiles of the standard Monopoly board."""
        tiles = {}

        # Tile 0: GO
        tiles[0] = TileInfo(
            tile_id=0,
            name="GO",
            tile_type=TileType.GO
        )

        # Tile 1: Mediterranean Avenue (Brown)
        tiles[1] = TileInfo(
            tile_id=1,
            name="Mediterranean Avenue",
            tile_type=TileType.PROPERTY,
            property_info=PropertyInfo(
                tile_id=1,
                name="Mediterranean Avenue",
                group=PropertyGroup.BROWN,
                purchase_price=60,
                base_rent=2,
                rent_with_1_house=10,
                rent_with_2_houses=30,
                rent_with_3_houses=90,
                rent_with_4_houses=160,
                rent_with_hotel=250,
                house_cost=50,
                mortgage_value=30
            )
        )

        # Tile 2: Community Chest
        tiles[2] = TileInfo(
            tile_id=2,
            name="Community Chest",
            tile_type=TileType.COMMUNITY_CHEST
        )

        # Tile 3: Baltic Avenue (Brown)
        tiles[3] = TileInfo(
            tile_id=3,
            name="Baltic Avenue",
            tile_type=TileType.PROPERTY,
            property_info=PropertyInfo(
                tile_id=3,
                name="Baltic Avenue",
                group=PropertyGroup.BROWN,
                purchase_price=60,
                base_rent=4,
                rent_with_1_house=20,
                rent_with_2_houses=60,
                rent_with_3_houses=180,
                rent_with_4_houses=320,
                rent_with_hotel=450,
                house_cost=50,
                mortgage_value=30
            )
        )

        # Tile 4: Income Tax
        tiles[4] = TileInfo(
            tile_id=4,
            name="Income Tax",
            tile_type=TileType.TAX,
            tax_amount=200
        )

        # Tile 5: Reading Railroad
        tiles[5] = TileInfo(
            tile_id=5,
            name="Reading Railroad",
            tile_type=TileType.RAILROAD,
            railroad_info=RailroadInfo(
                tile_id=5,
                name="Reading Railroad",
                purchase_price=200,
                mortgage_value=100
            )
        )

        # Tile 6: Oriental Avenue (Light Blue)
        tiles[6] = TileInfo(
            tile_id=6,
            name="Oriental Avenue",
            tile_type=TileType.PROPERTY,
            property_info=PropertyInfo(
                tile_id=6,
                name="Oriental Avenue",
                group=PropertyGroup.LIGHT_BLUE,
                purchase_price=100,
                base_rent=6,
                rent_with_1_house=30,
                rent_with_2_houses=90,
                rent_with_3_houses=270,
                rent_with_4_houses=400,
                rent_with_hotel=550,
                house_cost=50,
                mortgage_value=50
            )
        )

        # Tile 7: Chance
        tiles[7] = TileInfo(
            tile_id=7,
            name="Chance",
            tile_type=TileType.CHANCE
        )

        # Tile 8: Vermont Avenue (Light Blue)
        tiles[8] = TileInfo(
            tile_id=8,
            name="Vermont Avenue",
            tile_type=TileType.PROPERTY,
            property_info=PropertyInfo(
                tile_id=8,
                name="Vermont Avenue",
                group=PropertyGroup.LIGHT_BLUE,
                purchase_price=100,
                base_rent=6,
                rent_with_1_house=30,
                rent_with_2_houses=90,
                rent_with_3_houses=270,
                rent_with_4_houses=400,
                rent_with_hotel=550,
                house_cost=50,
                mortgage_value=50
            )
        )

        # Tile 9: Connecticut Avenue (Light Blue)
        tiles[9] = TileInfo(
            tile_id=9,
            name="Connecticut Avenue",
            tile_type=TileType.PROPERTY,
            property_info=PropertyInfo(
                tile_id=9,
                name="Connecticut Avenue",
                group=PropertyGroup.LIGHT_BLUE,
                purchase_price=120,
                base_rent=8,
                rent_with_1_house=40,
                rent_with_2_houses=100,
                rent_with_3_houses=300,
                rent_with_4_houses=450,
                rent_with_hotel=600,
                house_cost=50,
                mortgage_value=60
            )
        )

        # Tile 10: Jail (Just Visiting)
        tiles[10] = TileInfo(
            tile_id=10,
            name="Jail",
            tile_type=TileType.JAIL
        )

        # Tile 11: St. Charles Place (Pink)
        tiles[11] = TileInfo(
            tile_id=11,
            name="St. Charles Place",
            tile_type=TileType.PROPERTY,
            property_info=PropertyInfo(
                tile_id=11,
                name="St. Charles Place",
                group=PropertyGroup.PINK,
                purchase_price=140,
                base_rent=10,
                rent_with_1_house=50,
                rent_with_2_houses=150,
                rent_with_3_houses=450,
                rent_with_4_houses=625,
                rent_with_hotel=750,
                house_cost=100,
                mortgage_value=70
            )
        )

        # Tile 12: Electric Company (Utility)
        tiles[12] = TileInfo(
            tile_id=12,
            name="Electric Company",
            tile_type=TileType.UTILITY,
            utility_info=UtilityInfo(
                tile_id=12,
                name="Electric Company",
                purchase_price=150,
                mortgage_value=75
            )
        )

        # Tile 13: States Avenue (Pink)
        tiles[13] = TileInfo(
            tile_id=13,
            name="States Avenue",
            tile_type=TileType.PROPERTY,
            property_info=PropertyInfo(
                tile_id=13,
                name="States Avenue",
                group=PropertyGroup.PINK,
                purchase_price=140,
                base_rent=10,
                rent_with_1_house=50,
                rent_with_2_houses=150,
                rent_with_3_houses=450,
                rent_with_4_houses=625,
                rent_with_hotel=750,
                house_cost=100,
                mortgage_value=70
            )
        )

        # Tile 14: Virginia Avenue (Pink)
        tiles[14] = TileInfo(
            tile_id=14,
            name="Virginia Avenue",
            tile_type=TileType.PROPERTY,
            property_info=PropertyInfo(
                tile_id=14,
                name="Virginia Avenue",
                group=PropertyGroup.PINK,
                purchase_price=160,
                base_rent=12,
                rent_with_1_house=60,
                rent_with_2_houses=180,
                rent_with_3_houses=500,
                rent_with_4_houses=700,
                rent_with_hotel=900,
                house_cost=100,
                mortgage_value=80
            )
        )

        # Tile 15: Pennsylvania Railroad
        tiles[15] = TileInfo(
            tile_id=15,
            name="Pennsylvania Railroad",
            tile_type=TileType.RAILROAD,
            railroad_info=RailroadInfo(
                tile_id=15,
                name="Pennsylvania Railroad",
                purchase_price=200,
                mortgage_value=100
            )
        )

        # Tile 16: St. James Place (Orange)
        tiles[16] = TileInfo(
            tile_id=16,
            name="St. James Place",
            tile_type=TileType.PROPERTY,
            property_info=PropertyInfo(
                tile_id=16,
                name="St. James Place",
                group=PropertyGroup.ORANGE,
                purchase_price=180,
                base_rent=14,
                rent_with_1_house=70,
                rent_with_2_houses=200,
                rent_with_3_houses=550,
                rent_with_4_houses=750,
                rent_with_hotel=950,
                house_cost=100,
                mortgage_value=90
            )
        )

        # Tile 17: Community Chest
        tiles[17] = TileInfo(
            tile_id=17,
            name="Community Chest",
            tile_type=TileType.COMMUNITY_CHEST
        )

        # Tile 18: Tennessee Avenue (Orange)
        tiles[18] = TileInfo(
            tile_id=18,
            name="Tennessee Avenue",
            tile_type=TileType.PROPERTY,
            property_info=PropertyInfo(
                tile_id=18,
                name="Tennessee Avenue",
                group=PropertyGroup.ORANGE,
                purchase_price=180,
                base_rent=14,
                rent_with_1_house=70,
                rent_with_2_houses=200,
                rent_with_3_houses=550,
                rent_with_4_houses=750,
                rent_with_hotel=950,
                house_cost=100,
                mortgage_value=90
            )
        )

        # Tile 19: New York Avenue (Orange)
        tiles[19] = TileInfo(
            tile_id=19,
            name="New York Avenue",
            tile_type=TileType.PROPERTY,
            property_info=PropertyInfo(
                tile_id=19,
                name="New York Avenue",
                group=PropertyGroup.ORANGE,
                purchase_price=200,
                base_rent=16,
                rent_with_1_house=80,
                rent_with_2_houses=220,
                rent_with_3_houses=600,
                rent_with_4_houses=800,
                rent_with_hotel=1000,
                house_cost=100,
                mortgage_value=100
            )
        )

        # Tile 20: Free Parking
        tiles[20] = TileInfo(
            tile_id=20,
            name="Free Parking",
            tile_type=TileType.FREE_PARKING
        )

        # Tile 21: Kentucky Avenue (Red)
        tiles[21] = TileInfo(
            tile_id=21,
            name="Kentucky Avenue",
            tile_type=TileType.PROPERTY,
            property_info=PropertyInfo(
                tile_id=21,
                name="Kentucky Avenue",
                group=PropertyGroup.RED,
                purchase_price=220,
                base_rent=18,
                rent_with_1_house=90,
                rent_with_2_houses=250,
                rent_with_3_houses=700,
                rent_with_4_houses=875,
                rent_with_hotel=1050,
                house_cost=150,
                mortgage_value=110
            )
        )

        # Tile 22: Chance
        tiles[22] = TileInfo(
            tile_id=22,
            name="Chance",
            tile_type=TileType.CHANCE
        )

        # Tile 23: Indiana Avenue (Red)
        tiles[23] = TileInfo(
            tile_id=23,
            name="Indiana Avenue",
            tile_type=TileType.PROPERTY,
            property_info=PropertyInfo(
                tile_id=23,
                name="Indiana Avenue",
                group=PropertyGroup.RED,
                purchase_price=220,
                base_rent=18,
                rent_with_1_house=90,
                rent_with_2_houses=250,
                rent_with_3_houses=700,
                rent_with_4_houses=875,
                rent_with_hotel=1050,
                house_cost=150,
                mortgage_value=110
            )
        )

        # Tile 24: Illinois Avenue (Red)
        tiles[24] = TileInfo(
            tile_id=24,
            name="Illinois Avenue",
            tile_type=TileType.PROPERTY,
            property_info=PropertyInfo(
                tile_id=24,
                name="Illinois Avenue",
                group=PropertyGroup.RED,
                purchase_price=240,
                base_rent=20,
                rent_with_1_house=100,
                rent_with_2_houses=300,
                rent_with_3_houses=750,
                rent_with_4_houses=925,
                rent_with_hotel=1100,
                house_cost=150,
                mortgage_value=120
            )
        )

        # Tile 25: B&O Railroad
        tiles[25] = TileInfo(
            tile_id=25,
            name="B&O Railroad",
            tile_type=TileType.RAILROAD,
            railroad_info=RailroadInfo(
                tile_id=25,
                name="B&O Railroad",
                purchase_price=200,
                mortgage_value=100
            )
        )

        # Tile 26: Atlantic Avenue (Yellow)
        tiles[26] = TileInfo(
            tile_id=26,
            name="Atlantic Avenue",
            tile_type=TileType.PROPERTY,
            property_info=PropertyInfo(
                tile_id=26,
                name="Atlantic Avenue",
                group=PropertyGroup.YELLOW,
                purchase_price=260,
                base_rent=22,
                rent_with_1_house=110,
                rent_with_2_houses=330,
                rent_with_3_houses=800,
                rent_with_4_houses=975,
                rent_with_hotel=1150,
                house_cost=150,
                mortgage_value=130
            )
        )

        # Tile 27: Ventnor Avenue (Yellow)
        tiles[27] = TileInfo(
            tile_id=27,
            name="Ventnor Avenue",
            tile_type=TileType.PROPERTY,
            property_info=PropertyInfo(
                tile_id=27,
                name="Ventnor Avenue",
                group=PropertyGroup.YELLOW,
                purchase_price=260,
                base_rent=22,
                rent_with_1_house=110,
                rent_with_2_houses=330,
                rent_with_3_houses=800,
                rent_with_4_houses=975,
                rent_with_hotel=1150,
                house_cost=150,
                mortgage_value=130
            )
        )

        # Tile 28: Water Works (Utility)
        tiles[28] = TileInfo(
            tile_id=28,
            name="Water Works",
            tile_type=TileType.UTILITY,
            utility_info=UtilityInfo(
                tile_id=28,
                name="Water Works",
                purchase_price=150,
                mortgage_value=75
            )
        )

        # Tile 29: Marvin Gardens (Yellow)
        tiles[29] = TileInfo(
            tile_id=29,
            name="Marvin Gardens",
            tile_type=TileType.PROPERTY,
            property_info=PropertyInfo(
                tile_id=29,
                name="Marvin Gardens",
                group=PropertyGroup.YELLOW,
                purchase_price=280,
                base_rent=24,
                rent_with_1_house=120,
                rent_with_2_houses=360,
                rent_with_3_houses=850,
                rent_with_4_houses=1025,
                rent_with_hotel=1200,
                house_cost=150,
                mortgage_value=140
            )
        )

        # Tile 30: Go To Jail
        tiles[30] = TileInfo(
            tile_id=30,
            name="Go To Jail",
            tile_type=TileType.GOTO_JAIL
        )

        # Tile 31: Pacific Avenue (Green)
        tiles[31] = TileInfo(
            tile_id=31,
            name="Pacific Avenue",
            tile_type=TileType.PROPERTY,
            property_info=PropertyInfo(
                tile_id=31,
                name="Pacific Avenue",
                group=PropertyGroup.GREEN,
                purchase_price=300,
                base_rent=26,
                rent_with_1_house=130,
                rent_with_2_houses=390,
                rent_with_3_houses=900,
                rent_with_4_houses=1100,
                rent_with_hotel=1275,
                house_cost=200,
                mortgage_value=150
            )
        )

        # Tile 32: North Carolina Avenue (Green)
        tiles[32] = TileInfo(
            tile_id=32,
            name="North Carolina Avenue",
            tile_type=TileType.PROPERTY,
            property_info=PropertyInfo(
                tile_id=32,
                name="North Carolina Avenue",
                group=PropertyGroup.GREEN,
                purchase_price=300,
                base_rent=26,
                rent_with_1_house=130,
                rent_with_2_houses=390,
                rent_with_3_houses=900,
                rent_with_4_houses=1100,
                rent_with_hotel=1275,
                house_cost=200,
                mortgage_value=150
            )
        )

        # Tile 33: Community Chest
        tiles[33] = TileInfo(
            tile_id=33,
            name="Community Chest",
            tile_type=TileType.COMMUNITY_CHEST
        )

        # Tile 34: Pennsylvania Avenue (Green)
        tiles[34] = TileInfo(
            tile_id=34,
            name="Pennsylvania Avenue",
            tile_type=TileType.PROPERTY,
            property_info=PropertyInfo(
                tile_id=34,
                name="Pennsylvania Avenue",
                group=PropertyGroup.GREEN,
                purchase_price=320,
                base_rent=28,
                rent_with_1_house=150,
                rent_with_2_houses=450,
                rent_with_3_houses=1000,
                rent_with_4_houses=1200,
                rent_with_hotel=1400,
                house_cost=200,
                mortgage_value=160
            )
        )

        # Tile 35: Short Line Railroad
        tiles[35] = TileInfo(
            tile_id=35,
            name="Short Line",
            tile_type=TileType.RAILROAD,
            railroad_info=RailroadInfo(
                tile_id=35,
                name="Short Line",
                purchase_price=200,
                mortgage_value=100
            )
        )

        # Tile 36: Chance
        tiles[36] = TileInfo(
            tile_id=36,
            name="Chance",
            tile_type=TileType.CHANCE
        )

        # Tile 37: Park Place (Dark Blue)
        tiles[37] = TileInfo(
            tile_id=37,
            name="Park Place",
            tile_type=TileType.PROPERTY,
            property_info=PropertyInfo(
                tile_id=37,
                name="Park Place",
                group=PropertyGroup.DARK_BLUE,
                purchase_price=350,
                base_rent=35,
                rent_with_1_house=175,
                rent_with_2_houses=500,
                rent_with_3_houses=1100,
                rent_with_4_houses=1300,
                rent_with_hotel=1500,
                house_cost=200,
                mortgage_value=175
            )
        )

        # Tile 38: Luxury Tax
        tiles[38] = TileInfo(
            tile_id=38,
            name="Luxury Tax",
            tile_type=TileType.TAX,
            tax_amount=100
        )

        # Tile 39: Boardwalk (Dark Blue)
        tiles[39] = TileInfo(
            tile_id=39,
            name="Boardwalk",
            tile_type=TileType.PROPERTY,
            property_info=PropertyInfo(
                tile_id=39,
                name="Boardwalk",
                group=PropertyGroup.DARK_BLUE,
                purchase_price=400,
                base_rent=50,
                rent_with_1_house=200,
                rent_with_2_houses=600,
                rent_with_3_houses=1400,
                rent_with_4_houses=1700,
                rent_with_hotel=2000,
                house_cost=200,
                mortgage_value=200
            )
        )

        return tiles

    def _create_property_groups(self) -> Dict[PropertyGroup, List[int]]:
        """Create mapping from property groups to tile IDs."""
        groups: Dict[PropertyGroup, List[int]] = {
            PropertyGroup.BROWN: [1, 3],
            PropertyGroup.LIGHT_BLUE: [6, 8, 9],
            PropertyGroup.PINK: [11, 13, 14],
            PropertyGroup.ORANGE: [16, 18, 19],
            PropertyGroup.RED: [21, 23, 24],
            PropertyGroup.YELLOW: [26, 27, 29],
            PropertyGroup.GREEN: [31, 32, 34],
            PropertyGroup.DARK_BLUE: [37, 39],
            PropertyGroup.RAILROAD: [5, 15, 25, 35],
            PropertyGroup.UTILITY: [12, 28],
        }
        return groups

    def get_tile(self, tile_id: int) -> TileInfo:
        """Get tile information by ID."""
        if tile_id not in self.tiles:
            raise ValueError(f"Invalid tile ID: {tile_id}")
        return self.tiles[tile_id]

    def get_property_group(self, tile_id: int) -> PropertyGroup:
        """Get the property group for a tile."""
        tile = self.get_tile(tile_id)
        if tile.property_info:
            return tile.property_info.group
        elif tile.railroad_info:
            return PropertyGroup.RAILROAD
        elif tile.utility_info:
            return PropertyGroup.UTILITY
        else:
            raise ValueError(f"Tile {tile_id} is not a property")

    def get_group_tiles(self, group: PropertyGroup) -> List[int]:
        """Get all tile IDs in a property group."""
        return self.property_groups[group]

    def has_monopoly(self, owned_tiles: Set[int], group: PropertyGroup) -> bool:
        """Check if a player owns all properties in a group."""
        group_tiles = set(self.get_group_tiles(group))
        return group_tiles.issubset(owned_tiles)

    def is_purchasable(self, tile_id: int) -> bool:
        """Check if a tile can be purchased."""
        tile = self.get_tile(tile_id)
        return tile.tile_type in [TileType.PROPERTY, TileType.RAILROAD, TileType.UTILITY]

    def get_purchase_price(self, tile_id: int) -> int:
        """Get the purchase price of a tile."""
        tile = self.get_tile(tile_id)
        if tile.property_info:
            return tile.property_info.purchase_price
        elif tile.railroad_info:
            return tile.railroad_info.purchase_price
        elif tile.utility_info:
            return tile.utility_info.purchase_price
        else:
            raise ValueError(f"Tile {tile_id} cannot be purchased")

    def get_mortgage_value(self, tile_id: int) -> int:
        """Get the mortgage value of a tile."""
        tile = self.get_tile(tile_id)
        if tile.property_info:
            return tile.property_info.mortgage_value
        elif tile.railroad_info:
            return tile.railroad_info.mortgage_value
        elif tile.utility_info:
            return tile.utility_info.mortgage_value
        else:
            raise ValueError(f"Tile {tile_id} cannot be mortgaged")
