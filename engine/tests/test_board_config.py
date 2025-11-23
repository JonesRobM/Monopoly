"""
Unit tests for board configuration loading and validation.

Tests cover:
- JSON loading from files
- Validation of tile structures
- Property group mappings
- Error handling for malformed configurations
"""

import pytest
import json
import tempfile
from pathlib import Path
from engine.board_config import (
    BoardConfigLoader, BoardValidationError, BoardMetadata,
    load_board_config, get_default_board, list_available_boards
)
from engine.state import TileType, PropertyGroup


class TestBoardConfigLoader:
    """Tests for BoardConfigLoader class."""

    def test_load_default_stoke_board(self):
        """Test loading the default Stoke-on-Trent board."""
        tiles, groups, meta = get_default_board()

        # Check metadata
        assert meta.name == "Stoke-on-Trent"
        assert meta.num_tiles == 41
        assert meta.currency_symbol == "£"
        assert meta.go_salary == 200

        # Check tiles
        assert len(tiles) == 41
        assert all(i in tiles for i in range(41))

        # Check first tile is GO
        assert tiles[0].tile_type == TileType.GO
        assert tiles[0].name == "GO"

        # Check property groups exist
        assert PropertyGroup.BROWN in groups
        assert PropertyGroup.LIGHT_BLUE in groups
        assert PropertyGroup.SPECIAL in groups
        assert PropertyGroup.RAILROAD in groups
        assert PropertyGroup.UTILITY in groups

    def test_brown_properties(self):
        """Test brown property group configuration."""
        tiles, groups, meta = get_default_board()

        brown_tiles = groups[PropertyGroup.BROWN]
        assert len(brown_tiles) == 2
        assert 1 in brown_tiles  # The Potteries Museum
        assert 2 in brown_tiles  # Stoke Minster

        # Verify tile 1
        tile1 = tiles[1]
        assert tile1.tile_type == TileType.PROPERTY
        assert tile1.name == "The Potteries Museum & Art Gallery"
        assert tile1.property_info is not None
        assert tile1.property_info.group == PropertyGroup.BROWN
        assert tile1.property_info.purchase_price == 60
        assert tile1.property_info.base_rent == 2

    def test_special_property_group(self):
        """Test the custom 'special' property group."""
        tiles, groups, meta = get_default_board()

        special_tiles = groups[PropertyGroup.SPECIAL]
        assert len(special_tiles) == 5
        expected_ids = [33, 35, 37, 38, 40]
        assert special_tiles == expected_ids

        # Verify all special tiles are properties
        for tile_id in special_tiles:
            tile = tiles[tile_id]
            assert tile.tile_type == TileType.PROPERTY
            assert tile.property_info.group == PropertyGroup.SPECIAL

    def test_railroad_stations(self):
        """Test railroad/station tiles."""
        tiles, groups, meta = get_default_board()

        railroad_tiles = groups[PropertyGroup.RAILROAD]
        assert len(railroad_tiles) == 4

        # Verify tile 4 (Hanley Bus Station)
        tile4 = tiles[4]
        assert tile4.tile_type == TileType.RAILROAD
        assert tile4.name == "Hanley Bus Station"
        assert tile4.railroad_info is not None
        assert tile4.railroad_info.purchase_price == 200
        assert tile4.railroad_info.mortgage_value == 100

    def test_utilities(self):
        """Test utility tiles."""
        tiles, groups, meta = get_default_board()

        utility_tiles = groups[PropertyGroup.UTILITY]
        assert len(utility_tiles) == 2

        # Verify tile 16 (Electric Company)
        tile16 = tiles[16]
        assert tile16.tile_type == TileType.UTILITY
        assert tile16.name == "Electric Company"
        assert tile16.utility_info is not None
        assert tile16.utility_info.purchase_price == 150

    def test_tax_tiles(self):
        """Test tax tiles."""
        tiles, groups, meta = get_default_board()

        # Tile 8: Income Tax
        tile8 = tiles[8]
        assert tile8.tile_type == TileType.TAX
        assert tile8.name == "Income Tax"
        assert tile8.tax_amount == 200

        # Tile 34: Super Tax
        tile34 = tiles[34]
        assert tile34.tile_type == TileType.TAX
        assert tile34.name == "Super Tax"
        assert tile34.tax_amount == 100

    def test_special_tiles(self):
        """Test special tiles (GO, Jail, etc.)."""
        tiles, groups, meta = get_default_board()

        # GO tile
        assert tiles[0].tile_type == TileType.GO

        # Community Chest
        assert tiles[3].tile_type == TileType.COMMUNITY_CHEST
        assert tiles[26].tile_type == TileType.COMMUNITY_CHEST
        assert tiles[39].tile_type == TileType.COMMUNITY_CHEST

        # Chance
        assert tiles[11].tile_type == TileType.CHANCE
        assert tiles[19].tile_type == TileType.CHANCE
        assert tiles[31].tile_type == TileType.CHANCE

        # Go To Jail
        assert tiles[36].tile_type == TileType.GOTO_JAIL

    def test_list_available_boards(self):
        """Test listing available board configurations."""
        boards = list_available_boards()
        assert "stoke_on_trent" in boards


class TestBoardValidation:
    """Tests for board configuration validation."""

    def test_missing_metadata_field(self):
        """Test that missing metadata fields raise errors."""
        config = {
            "name": "Test",
            "description": "Test board",
            # Missing currency_symbol, go_salary, num_tiles
            "tiles": []
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(BoardValidationError) as exc_info:
                BoardConfigLoader.load_from_json(temp_path)
            assert "Missing required field" in str(exc_info.value.message)
        finally:
            temp_path.unlink()

    def test_invalid_num_tiles(self):
        """Test that invalid num_tiles raises error."""
        config = {
            "name": "Test",
            "description": "Test",
            "currency_symbol": "$",
            "go_salary": 200,
            "num_tiles": 2,  # Too few
            "tiles": []
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(BoardValidationError) as exc_info:
                BoardConfigLoader.load_from_json(temp_path)
            assert "num_tiles" in str(exc_info.value.message)
        finally:
            temp_path.unlink()

    def test_missing_tiles(self):
        """Test that missing tiles raise validation error."""
        config = {
            "name": "Test",
            "description": "Test",
            "currency_symbol": "$",
            "go_salary": 200,
            "num_tiles": 5,
            "tiles": [
                {"id": 0, "type": "go", "name": "GO"},
                {"id": 1, "type": "chance", "name": "Chance"},
                {"id": 2, "type": "jail", "name": "Jail"}
                # Missing tiles 3 and 4
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(BoardValidationError) as exc_info:
                BoardConfigLoader.load_from_json(temp_path)
            assert "Expected 5 tiles" in str(exc_info.value.message)
        finally:
            temp_path.unlink()

    def test_duplicate_tile_ids(self):
        """Test that duplicate tile IDs raise error."""
        config = {
            "name": "Test",
            "description": "Test",
            "currency_symbol": "$",
            "go_salary": 200,
            "num_tiles": 4,
            "tiles": [
                {"id": 0, "type": "go", "name": "GO"},
                {"id": 1, "type": "chance", "name": "Chance"},
                {"id": 1, "type": "jail", "name": "Jail"},  # Duplicate ID
                {"id": 2, "type": "community_chest", "name": "CC"}
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(BoardValidationError) as exc_info:
                BoardConfigLoader.load_from_json(temp_path)
            assert "Duplicate tile ID" in str(exc_info.value.message)
        finally:
            temp_path.unlink()

    def test_non_consecutive_tile_ids(self):
        """Test that non-consecutive tile IDs raise error."""
        config = {
            "name": "Test",
            "description": "Test",
            "currency_symbol": "$",
            "go_salary": 200,
            "num_tiles": 4,
            "tiles": [
                {"id": 0, "type": "go", "name": "GO"},
                {"id": 1, "type": "chance", "name": "Chance"},
                {"id": 3, "type": "jail", "name": "Jail"},  # Skipped 2
                {"id": 4, "type": "community_chest", "name": "CC"}  # Extra tile
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(BoardValidationError) as exc_info:
                BoardConfigLoader.load_from_json(temp_path)
            assert "Missing tile IDs" in str(exc_info.value.message) or \
                   "Extra tile IDs" in str(exc_info.value.message)
        finally:
            temp_path.unlink()

    def test_invalid_tile_type(self):
        """Test that invalid tile types raise error."""
        config = {
            "name": "Test",
            "description": "Test",
            "currency_symbol": "$",
            "go_salary": 200,
            "num_tiles": 4,
            "tiles": [
                {"id": 0, "type": "go", "name": "GO"},
                {"id": 1, "type": "invalid_type", "name": "Bad"},  # Invalid
                {"id": 2, "type": "jail", "name": "Jail"},
                {"id": 3, "type": "chance", "name": "Chance"}
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(BoardValidationError) as exc_info:
                BoardConfigLoader.load_from_json(temp_path)
            assert "Invalid tile type" in str(exc_info.value.message)
        finally:
            temp_path.unlink()

    def test_property_missing_required_fields(self):
        """Test that properties missing required fields raise error."""
        config = {
            "name": "Test",
            "description": "Test",
            "currency_symbol": "$",
            "go_salary": 200,
            "num_tiles": 4,
            "tiles": [
                {"id": 0, "type": "go", "name": "GO"},
                {
                    "id": 1,
                    "type": "property",
                    "name": "Test Property",
                    "colour": "brown"
                    # Missing purchase_price, rents, etc.
                },
                {"id": 2, "type": "jail", "name": "Jail"},
                {"id": 3, "type": "chance", "name": "Chance"}
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(BoardValidationError) as exc_info:
                BoardConfigLoader.load_from_json(temp_path)
            assert "missing required field" in str(exc_info.value.message).lower()
        finally:
            temp_path.unlink()

    def test_invalid_property_colour(self):
        """Test that invalid property colours raise error."""
        config = {
            "name": "Test",
            "description": "Test",
            "currency_symbol": "$",
            "go_salary": 200,
            "num_tiles": 4,
            "tiles": [
                {"id": 0, "type": "go", "name": "GO"},
                {
                    "id": 1,
                    "type": "property",
                    "name": "Test Property",
                    "colour": "rainbow",  # Invalid colour
                    "purchase_price": 60,
                    "base_rent": 2,
                    "rent_1_house": 10,
                    "rent_2_houses": 30,
                    "rent_3_houses": 90,
                    "rent_4_houses": 160,
                    "rent_hotel": 250,
                    "house_cost": 50,
                    "mortgage_value": 30
                },
                {"id": 2, "type": "jail", "name": "Jail"},
                {"id": 3, "type": "chance", "name": "Chance"}
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(BoardValidationError) as exc_info:
                BoardConfigLoader.load_from_json(temp_path)
            assert "Invalid property colour" in str(exc_info.value.message)
        finally:
            temp_path.unlink()


class TestPropertyGroups:
    """Tests for property group validation."""

    def test_property_group_tile_mismatch(self):
        """Test that mismatched property groups raise error."""
        config = {
            "name": "Test",
            "description": "Test",
            "currency_symbol": "$",
            "go_salary": 200,
            "num_tiles": 5,
            "tiles": [
                {"id": 0, "type": "go", "name": "GO"},
                {
                    "id": 1,
                    "type": "property",
                    "name": "Brown Property",
                    "colour": "brown",
                    "purchase_price": 60,
                    "base_rent": 2,
                    "rent_1_house": 10,
                    "rent_2_houses": 30,
                    "rent_3_houses": 90,
                    "rent_4_houses": 160,
                    "rent_hotel": 250,
                    "house_cost": 50,
                    "mortgage_value": 30
                },
                {"id": 2, "type": "jail", "name": "Jail"},
                {"id": 3, "type": "chance", "name": "Chance"},
                {"id": 4, "type": "community_chest", "name": "CC"}
            ],
            "property_groups": {
                "light_blue": [1]  # Property 1 is actually brown!
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(BoardValidationError) as exc_info:
                BoardConfigLoader.load_from_json(temp_path)
            assert "mismatch" in str(exc_info.value.message).lower()
        finally:
            temp_path.unlink()

    def test_property_group_nonexistent_tile(self):
        """Test that property groups referencing nonexistent tiles raise error."""
        config = {
            "name": "Test",
            "description": "Test",
            "currency_symbol": "$",
            "go_salary": 200,
            "num_tiles": 4,
            "tiles": [
                {"id": 0, "type": "go", "name": "GO"},
                {"id": 1, "type": "jail", "name": "Jail"},
                {"id": 2, "type": "chance", "name": "Chance"},
                {"id": 3, "type": "community_chest", "name": "CC"}
            ],
            "property_groups": {
                "brown": [99]  # Tile 99 doesn't exist
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(BoardValidationError) as exc_info:
                BoardConfigLoader.load_from_json(temp_path)
            assert "non-existent tile" in str(exc_info.value.message).lower()
        finally:
            temp_path.unlink()


class TestTileTypeAliases:
    """Tests for tile type aliases (e.g., 'station' for 'railroad')."""

    def test_station_alias(self):
        """Test that 'station' is correctly mapped to 'railroad'."""
        tiles, groups, meta = get_default_board()

        # Verify stations are loaded as railroads
        station_tile = tiles[4]  # Hanley Bus Station
        assert station_tile.tile_type == TileType.RAILROAD
        assert station_tile.railroad_info is not None

    def test_go_to_jail_normalization(self):
        """Test that 'go_to_jail' is normalized to 'goto_jail'."""
        tiles, groups, meta = get_default_board()

        # Tile 36 should be GOTO_JAIL
        gotojail_tile = tiles[36]
        assert gotojail_tile.tile_type == TileType.GOTO_JAIL


class TestBoardMetadata:
    """Tests for board metadata handling."""

    def test_metadata_extraction(self):
        """Test that metadata is correctly extracted."""
        tiles, groups, meta = get_default_board()

        assert isinstance(meta, BoardMetadata)
        assert meta.name == "Stoke-on-Trent"
        assert meta.description == "Custom Stoke-on-Trent themed Monopoly board with 41 tiles"
        assert meta.currency_symbol == "£"
        assert meta.go_salary == 200
        assert meta.num_tiles == 41

    def test_metadata_immutability(self):
        """Test that BoardMetadata is immutable."""
        tiles, groups, meta = get_default_board()

        # Should raise error when trying to modify frozen dataclass
        with pytest.raises(Exception):  # FrozenInstanceError or similar
            meta.name = "Modified"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
