"""
Unit tests for Monopoly board.
"""

import pytest
from engine.board import MonopolyBoard
from engine.state import PropertyGroup, TileType


class TestMonopolyBoard:
    """Tests for MonopolyBoard class."""

    @pytest.fixture
    def board(self):
        """Create a board instance for testing."""
        return MonopolyBoard()

    def test_board_has_40_tiles(self, board):
        """Test board has exactly 40 tiles."""
        assert len(board.tiles) == 40

    def test_go_tile(self, board):
        """Test GO tile properties."""
        go_tile = board.get_tile(0)

        assert go_tile.tile_id == 0
        assert go_tile.name == "GO"
        assert go_tile.tile_type == TileType.GO

    def test_mediterranean_avenue(self, board):
        """Test Mediterranean Avenue properties."""
        med_ave = board.get_tile(1)

        assert med_ave.tile_id == 1
        assert med_ave.name == "Mediterranean Avenue"
        assert med_ave.tile_type == TileType.PROPERTY
        assert med_ave.property_info is not None
        assert med_ave.property_info.group == PropertyGroup.BROWN
        assert med_ave.property_info.purchase_price == 60
        assert med_ave.property_info.base_rent == 2
        assert med_ave.property_info.mortgage_value == 30

    def test_boardwalk(self, board):
        """Test Boardwalk properties."""
        boardwalk = board.get_tile(39)

        assert boardwalk.tile_id == 39
        assert boardwalk.name == "Boardwalk"
        assert boardwalk.tile_type == TileType.PROPERTY
        assert boardwalk.property_info is not None
        assert boardwalk.property_info.group == PropertyGroup.DARK_BLUE
        assert boardwalk.property_info.purchase_price == 400
        assert boardwalk.property_info.base_rent == 50

    def test_railroads(self, board):
        """Test railroad tiles."""
        railroad_ids = [5, 15, 25, 35]

        for rail_id in railroad_ids:
            tile = board.get_tile(rail_id)
            assert tile.tile_type == TileType.RAILROAD
            assert tile.railroad_info is not None
            assert tile.railroad_info.purchase_price == 200
            assert tile.railroad_info.mortgage_value == 100

    def test_utilities(self, board):
        """Test utility tiles."""
        electric = board.get_tile(12)
        water = board.get_tile(28)

        assert electric.tile_type == TileType.UTILITY
        assert electric.name == "Electric Company"
        assert electric.utility_info is not None
        assert electric.utility_info.purchase_price == 150

        assert water.tile_type == TileType.UTILITY
        assert water.name == "Water Works"
        assert water.utility_info is not None
        assert water.utility_info.purchase_price == 150

    def test_special_tiles(self, board):
        """Test special tiles (Chance, Community Chest, etc.)."""
        # Jail
        jail = board.get_tile(10)
        assert jail.tile_type == TileType.JAIL

        # Free Parking
        free_parking = board.get_tile(20)
        assert free_parking.tile_type == TileType.FREE_PARKING

        # Go To Jail
        goto_jail = board.get_tile(30)
        assert goto_jail.tile_type == TileType.GOTO_JAIL

        # Chance tiles
        chance_tiles = [7, 22, 36]
        for chance_id in chance_tiles:
            tile = board.get_tile(chance_id)
            assert tile.tile_type == TileType.CHANCE

        # Community Chest tiles
        cc_tiles = [2, 17, 33]
        for cc_id in cc_tiles:
            tile = board.get_tile(cc_id)
            assert tile.tile_type == TileType.COMMUNITY_CHEST

    def test_tax_tiles(self, board):
        """Test tax tiles."""
        income_tax = board.get_tile(4)
        assert income_tax.tile_type == TileType.TAX
        assert income_tax.tax_amount == 200

        luxury_tax = board.get_tile(38)
        assert luxury_tax.tile_type == TileType.TAX
        assert luxury_tax.tax_amount == 100

    def test_get_property_group(self, board):
        """Test getting property group."""
        # Brown properties
        assert board.get_property_group(1) == PropertyGroup.BROWN
        assert board.get_property_group(3) == PropertyGroup.BROWN

        # Light blue
        assert board.get_property_group(6) == PropertyGroup.LIGHT_BLUE
        assert board.get_property_group(8) == PropertyGroup.LIGHT_BLUE
        assert board.get_property_group(9) == PropertyGroup.LIGHT_BLUE

        # Railroads
        assert board.get_property_group(5) == PropertyGroup.RAILROAD
        assert board.get_property_group(15) == PropertyGroup.RAILROAD

        # Utilities
        assert board.get_property_group(12) == PropertyGroup.UTILITY
        assert board.get_property_group(28) == PropertyGroup.UTILITY

    def test_get_group_tiles(self, board):
        """Test getting all tiles in a group."""
        # Brown group
        brown = board.get_group_tiles(PropertyGroup.BROWN)
        assert brown == [1, 3]

        # Light blue group
        light_blue = board.get_group_tiles(PropertyGroup.LIGHT_BLUE)
        assert light_blue == [6, 8, 9]

        # Dark blue group
        dark_blue = board.get_group_tiles(PropertyGroup.DARK_BLUE)
        assert dark_blue == [37, 39]

        # Railroads
        railroads = board.get_group_tiles(PropertyGroup.RAILROAD)
        assert railroads == [5, 15, 25, 35]

        # Utilities
        utilities = board.get_group_tiles(PropertyGroup.UTILITY)
        assert utilities == [12, 28]

    def test_has_monopoly(self, board):
        """Test monopoly detection."""
        # Own both brown properties
        owned = {1, 3}
        assert board.has_monopoly(owned, PropertyGroup.BROWN)

        # Own only one brown property
        owned = {1}
        assert not board.has_monopoly(owned, PropertyGroup.BROWN)

        # Own all railroads
        owned = {5, 15, 25, 35}
        assert board.has_monopoly(owned, PropertyGroup.RAILROAD)

        # Own 3 of 4 railroads
        owned = {5, 15, 25}
        assert not board.has_monopoly(owned, PropertyGroup.RAILROAD)

        # Own all utilities
        owned = {12, 28}
        assert board.has_monopoly(owned, PropertyGroup.UTILITY)

    def test_is_purchasable(self, board):
        """Test if tiles are purchasable."""
        # Properties
        assert board.is_purchasable(1)  # Mediterranean
        assert board.is_purchasable(39)  # Boardwalk

        # Railroads
        assert board.is_purchasable(5)
        assert board.is_purchasable(15)

        # Utilities
        assert board.is_purchasable(12)
        assert board.is_purchasable(28)

        # Non-purchasable
        assert not board.is_purchasable(0)  # GO
        assert not board.is_purchasable(10)  # Jail
        assert not board.is_purchasable(20)  # Free Parking
        assert not board.is_purchasable(7)  # Chance
        assert not board.is_purchasable(2)  # Community Chest
        assert not board.is_purchasable(4)  # Income Tax

    def test_get_purchase_price(self, board):
        """Test getting purchase prices."""
        assert board.get_purchase_price(1) == 60  # Mediterranean
        assert board.get_purchase_price(39) == 400  # Boardwalk
        assert board.get_purchase_price(5) == 200  # Railroad
        assert board.get_purchase_price(12) == 150  # Electric Company

        with pytest.raises(ValueError):
            board.get_purchase_price(0)  # GO is not purchasable

    def test_get_mortgage_value(self, board):
        """Test getting mortgage values."""
        assert board.get_mortgage_value(1) == 30  # Mediterranean
        assert board.get_mortgage_value(39) == 200  # Boardwalk
        assert board.get_mortgage_value(5) == 100  # Railroad
        assert board.get_mortgage_value(12) == 75  # Electric Company

    def test_invalid_tile_id(self, board):
        """Test invalid tile IDs raise errors."""
        with pytest.raises(ValueError):
            board.get_tile(40)

        with pytest.raises(ValueError):
            board.get_tile(-1)

        with pytest.raises(ValueError):
            board.get_tile(100)

    def test_property_groups_complete(self, board):
        """Test all property groups are defined."""
        groups = board.property_groups

        assert PropertyGroup.BROWN in groups
        assert PropertyGroup.LIGHT_BLUE in groups
        assert PropertyGroup.PINK in groups
        assert PropertyGroup.ORANGE in groups
        assert PropertyGroup.RED in groups
        assert PropertyGroup.YELLOW in groups
        assert PropertyGroup.GREEN in groups
        assert PropertyGroup.DARK_BLUE in groups
        assert PropertyGroup.RAILROAD in groups
        assert PropertyGroup.UTILITY in groups

    def test_rent_calculation_property(self, board):
        """Test rent calculation for properties."""
        med_ave = board.get_tile(1)
        prop_info = med_ave.property_info

        # Base rent
        assert prop_info.get_rent(0) == 2

        # With houses
        assert prop_info.get_rent(1) == 10
        assert prop_info.get_rent(2) == 30
        assert prop_info.get_rent(3) == 90
        assert prop_info.get_rent(4) == 160

        # With hotel
        assert prop_info.get_rent(5) == 250

    def test_rent_calculation_railroad(self, board):
        """Test rent calculation for railroads."""
        railroad = board.get_tile(5)
        rail_info = railroad.railroad_info

        # 1 railroad: $25
        assert rail_info.get_rent(1) == 25

        # 2 railroads: $50
        assert rail_info.get_rent(2) == 50

        # 3 railroads: $100
        assert rail_info.get_rent(3) == 100

        # 4 railroads: $200
        assert rail_info.get_rent(4) == 200

    def test_rent_calculation_utility(self, board):
        """Test rent calculation for utilities."""
        utility = board.get_tile(12)
        util_info = utility.utility_info

        # 1 utility: 4x dice roll
        assert util_info.get_rent(dice_roll=7, num_utilities_owned=1) == 28

        # 2 utilities: 10x dice roll
        assert util_info.get_rent(dice_roll=7, num_utilities_owned=2) == 70
