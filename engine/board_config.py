"""
Board configuration system for Monopoly variants.

Supports loading custom boards from JSON files, validating structure,
and converting to the engine's internal TileInfo representation.

All boards must be deterministic and follow strict validation rules.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from engine.state import (
    TileType, PropertyGroup, TileInfo, PropertyInfo,
    RailroadInfo, UtilityInfo
)


@dataclass(frozen=True)
class BoardValidationError(Exception):
    """Raised when board configuration validation fails."""
    message: str
    tile_id: Optional[int] = None
    field: Optional[str] = None


@dataclass(frozen=True)
class BoardMetadata:
    """Metadata about a board configuration."""
    name: str
    description: str
    currency_symbol: str
    go_salary: int
    num_tiles: int


class BoardConfigLoader:
    """
    Loads and validates board configurations from JSON files.

    JSON Structure:
    {
        "name": "Board Name",
        "description": "Board description",
        "currency_symbol": "$",
        "go_salary": 200,
        "num_tiles": 40,
        "tiles": [
            {"id": 0, "type": "go", "name": "GO"},
            {"id": 1, "type": "property", "name": "...", "colour": "brown", ...},
            ...
        ],
        "property_groups": {
            "brown": [1, 3],
            "light_blue": [6, 8, 9],
            ...
        }
    }
    """

    # Valid tile types from the JSON schema
    VALID_TILE_TYPES = {
        "go", "property", "railroad", "station", "utility",
        "chance", "community_chest", "tax", "jail", "go_to_jail", "goto_jail",
        "free_parking"
    }

    # Map JSON color names to PropertyGroup enum
    COLOR_MAP = {
        "brown": PropertyGroup.BROWN,
        "light_blue": PropertyGroup.LIGHT_BLUE,
        "pink": PropertyGroup.PINK,
        "purple": PropertyGroup.PURPLE,
        "orange": PropertyGroup.ORANGE,
        "red": PropertyGroup.RED,
        "yellow": PropertyGroup.YELLOW,
        "green": PropertyGroup.GREEN,
        "dark_blue": PropertyGroup.DARK_BLUE,
        "special": PropertyGroup.SPECIAL,
    }

    @staticmethod
    def load_from_json(json_path: Path) -> tuple[Dict[int, TileInfo], Dict[PropertyGroup, List[int]], BoardMetadata]:
        """
        Load board configuration from JSON file.

        Args:
            json_path: Path to JSON configuration file

        Returns:
            Tuple of (tiles dict, property_groups dict, metadata)

        Raises:
            BoardValidationError: If validation fails
            FileNotFoundError: If JSON file doesn't exist
            json.JSONDecodeError: If JSON is malformed
        """
        if not json_path.exists():
            raise FileNotFoundError(f"Board configuration not found: {json_path}")

        with open(json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Validate and extract metadata
        metadata = BoardConfigLoader._validate_metadata(config)

        # Validate and parse tiles
        tiles = BoardConfigLoader._parse_tiles(config.get("tiles", []), metadata.num_tiles)

        # Validate and parse property groups
        property_groups = BoardConfigLoader._parse_property_groups(
            config.get("property_groups", {}),
            tiles
        )

        return tiles, property_groups, metadata

    @staticmethod
    def _validate_metadata(config: Dict[str, Any]) -> BoardMetadata:
        """Validate and extract board metadata."""
        required_fields = ["name", "description", "currency_symbol", "go_salary", "num_tiles"]
        for field in required_fields:
            if field not in config:
                raise BoardValidationError(f"Missing required field: {field}")

        num_tiles = config["num_tiles"]
        if not isinstance(num_tiles, int) or num_tiles < 4:
            raise BoardValidationError(
                f"num_tiles must be an integer >= 4, got {num_tiles}"
            )

        go_salary = config["go_salary"]
        if not isinstance(go_salary, int) or go_salary <= 0:
            raise BoardValidationError(
                f"go_salary must be a positive integer, got {go_salary}"
            )

        return BoardMetadata(
            name=config["name"],
            description=config["description"],
            currency_symbol=config["currency_symbol"],
            go_salary=go_salary,
            num_tiles=num_tiles
        )

    @staticmethod
    def _parse_tiles(tiles_config: List[Dict[str, Any]], expected_count: int) -> Dict[int, TileInfo]:
        """
        Parse and validate tile configurations.

        Validates:
        - Consecutive tile IDs from 0 to num_tiles-1
        - Required fields for each tile type
        - Property/railroad/utility purchase prices and rent values
        """
        if len(tiles_config) != expected_count:
            raise BoardValidationError(
                f"Expected {expected_count} tiles, found {len(tiles_config)}"
            )

        tiles: Dict[int, TileInfo] = {}

        for tile_config in tiles_config:
            tile_id = tile_config.get("id")
            if not isinstance(tile_id, int) or tile_id < 0:
                raise BoardValidationError(
                    f"Invalid tile ID: {tile_id}",
                    tile_id=tile_id
                )

            if tile_id in tiles:
                raise BoardValidationError(
                    f"Duplicate tile ID: {tile_id}",
                    tile_id=tile_id
                )

            tile = BoardConfigLoader._parse_single_tile(tile_config)
            tiles[tile_id] = tile

        # Validate consecutive IDs
        expected_ids = set(range(expected_count))
        actual_ids = set(tiles.keys())
        if expected_ids != actual_ids:
            missing = expected_ids - actual_ids
            extra = actual_ids - expected_ids
            msg = []
            if missing:
                msg.append(f"Missing tile IDs: {sorted(missing)}")
            if extra:
                msg.append(f"Extra tile IDs: {sorted(extra)}")
            raise BoardValidationError("; ".join(msg))

        return tiles

    @staticmethod
    def _parse_single_tile(config: Dict[str, Any]) -> TileInfo:
        """Parse a single tile configuration."""
        tile_id = config["id"]
        tile_name = config.get("name", "")
        tile_type_str = config.get("type", "").lower()

        if tile_type_str not in BoardConfigLoader.VALID_TILE_TYPES:
            raise BoardValidationError(
                f"Invalid tile type: {tile_type_str}",
                tile_id=tile_id,
                field="type"
            )

        # Map tile type strings to TileType enum
        # Note: "station" is an alias for "railroad"
        # Note: "go_to_jail" should be normalized to "goto_jail"
        if tile_type_str == "station":
            tile_type_str = "railroad"
        elif tile_type_str == "go_to_jail":
            tile_type_str = "goto_jail"

        tile_type = TileType(tile_type_str)

        # Parse type-specific information
        property_info = None
        railroad_info = None
        utility_info = None
        tax_amount = None

        if tile_type == TileType.PROPERTY:
            property_info = BoardConfigLoader._parse_property_info(config, tile_id)
        elif tile_type == TileType.RAILROAD:
            railroad_info = BoardConfigLoader._parse_railroad_info(config, tile_id)
        elif tile_type == TileType.UTILITY:
            utility_info = BoardConfigLoader._parse_utility_info(config, tile_id)
        elif tile_type == TileType.TAX:
            tax_amount = BoardConfigLoader._parse_tax_amount(config, tile_id)

        return TileInfo(
            tile_id=tile_id,
            name=tile_name,
            tile_type=tile_type,
            property_info=property_info,
            railroad_info=railroad_info,
            utility_info=utility_info,
            tax_amount=tax_amount
        )

    @staticmethod
    def _parse_property_info(config: Dict[str, Any], tile_id: int) -> PropertyInfo:
        """Parse property-specific configuration."""
        required_fields = [
            "colour", "purchase_price", "base_rent",
            "rent_1_house", "rent_2_houses", "rent_3_houses",
            "rent_4_houses", "rent_hotel", "house_cost", "mortgage_value"
        ]

        for field in required_fields:
            if field not in config:
                raise BoardValidationError(
                    f"Property missing required field: {field}",
                    tile_id=tile_id,
                    field=field
                )

        colour_str = config["colour"].lower()
        if colour_str not in BoardConfigLoader.COLOR_MAP:
            raise BoardValidationError(
                f"Invalid property colour: {colour_str}",
                tile_id=tile_id,
                field="colour"
            )

        group = BoardConfigLoader.COLOR_MAP[colour_str]

        return PropertyInfo(
            tile_id=tile_id,
            name=config["name"],
            group=group,
            purchase_price=config["purchase_price"],
            base_rent=config["base_rent"],
            rent_with_1_house=config["rent_1_house"],
            rent_with_2_houses=config["rent_2_houses"],
            rent_with_3_houses=config["rent_3_houses"],
            rent_with_4_houses=config["rent_4_houses"],
            rent_with_hotel=config["rent_hotel"],
            house_cost=config["house_cost"],
            mortgage_value=config["mortgage_value"]
        )

    @staticmethod
    def _parse_railroad_info(config: Dict[str, Any], tile_id: int) -> RailroadInfo:
        """Parse railroad/station configuration."""
        required_fields = ["purchase_price", "mortgage_value"]

        for field in required_fields:
            if field not in config:
                raise BoardValidationError(
                    f"Railroad missing required field: {field}",
                    tile_id=tile_id,
                    field=field
                )

        return RailroadInfo(
            tile_id=tile_id,
            name=config["name"],
            purchase_price=config["purchase_price"],
            mortgage_value=config["mortgage_value"]
        )

    @staticmethod
    def _parse_utility_info(config: Dict[str, Any], tile_id: int) -> UtilityInfo:
        """Parse utility configuration."""
        required_fields = ["purchase_price", "mortgage_value"]

        for field in required_fields:
            if field not in config:
                raise BoardValidationError(
                    f"Utility missing required field: {field}",
                    tile_id=tile_id,
                    field=field
                )

        return UtilityInfo(
            tile_id=tile_id,
            name=config["name"],
            purchase_price=config["purchase_price"],
            mortgage_value=config["mortgage_value"]
        )

    @staticmethod
    def _parse_tax_amount(config: Dict[str, Any], tile_id: int) -> int:
        """Parse tax tile amount."""
        if "amount" not in config:
            raise BoardValidationError(
                "Tax tile missing 'amount' field",
                tile_id=tile_id,
                field="amount"
            )

        amount = config["amount"]
        if not isinstance(amount, int) or amount < 0:
            raise BoardValidationError(
                f"Tax amount must be non-negative integer, got {amount}",
                tile_id=tile_id,
                field="amount"
            )

        return amount

    @staticmethod
    def _parse_property_groups(
        groups_config: Dict[str, List[int]],
        tiles: Dict[int, TileInfo]
    ) -> Dict[PropertyGroup, List[int]]:
        """
        Parse and validate property group mappings.

        Validates:
        - All tile IDs in groups exist
        - Tile IDs match their declared color group
        - No duplicate tile IDs across groups
        """
        property_groups: Dict[PropertyGroup, List[int]] = {}
        all_grouped_tiles: Set[int] = set()

        for color_str, tile_ids in groups_config.items():
            color_lower = color_str.lower()

            # Handle railroad and utility as special cases
            if color_lower == "railroad":
                group = PropertyGroup.RAILROAD
            elif color_lower == "utility":
                group = PropertyGroup.UTILITY
            elif color_lower not in BoardConfigLoader.COLOR_MAP:
                raise BoardValidationError(
                    f"Invalid property group color: {color_str}"
                )
            else:
                group = BoardConfigLoader.COLOR_MAP[color_lower]

            # Validate all tile IDs exist
            for tile_id in tile_ids:
                if tile_id not in tiles:
                    raise BoardValidationError(
                        f"Property group '{color_str}' references non-existent tile: {tile_id}"
                    )

                if tile_id in all_grouped_tiles:
                    raise BoardValidationError(
                        f"Tile {tile_id} appears in multiple property groups"
                    )

                all_grouped_tiles.add(tile_id)

                # Validate tile matches group
                tile = tiles[tile_id]
                if tile.tile_type == TileType.PROPERTY:
                    if tile.property_info and tile.property_info.group != group:
                        raise BoardValidationError(
                            f"Tile {tile_id} property group mismatch: "
                            f"declared as {tile.property_info.group}, "
                            f"grouped as {group}"
                        )
                elif tile.tile_type == TileType.RAILROAD:
                    if group != PropertyGroup.RAILROAD:
                        raise BoardValidationError(
                            f"Railroad tile {tile_id} must be in RAILROAD group"
                        )
                elif tile.tile_type == TileType.UTILITY:
                    if group != PropertyGroup.UTILITY:
                        raise BoardValidationError(
                            f"Utility tile {tile_id} must be in UTILITY group"
                        )

            property_groups[group] = tile_ids

        return property_groups


def load_board_config(board_name: str = "stoke_on_trent") -> tuple[Dict[int, TileInfo], Dict[PropertyGroup, List[int]], BoardMetadata]:
    """
    Load a board configuration by name.

    Args:
        board_name: Name of the board (without .json extension)

    Returns:
        Tuple of (tiles dict, property_groups dict, metadata)

    Example:
        >>> tiles, groups, meta = load_board_config("stoke_on_trent")
        >>> print(f"Loaded {meta.name} with {meta.num_tiles} tiles")
    """
    boards_dir = Path(__file__).parent / "boards"
    json_path = boards_dir / f"{board_name}.json"

    return BoardConfigLoader.load_from_json(json_path)


def get_default_board() -> tuple[Dict[int, TileInfo], Dict[PropertyGroup, List[int]], BoardMetadata]:
    """
    Load the default board configuration (Stoke-on-Trent).

    Returns:
        Tuple of (tiles dict, property_groups dict, metadata)
    """
    return load_board_config("stoke_on_trent")


def list_available_boards() -> List[str]:
    """
    List all available board configurations.

    Returns:
        List of board names (without .json extension)
    """
    boards_dir = Path(__file__).parent / "boards"
    if not boards_dir.exists():
        return []

    return [p.stem for p in boards_dir.glob("*.json")]
