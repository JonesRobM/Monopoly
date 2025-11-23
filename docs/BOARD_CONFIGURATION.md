# Board Configuration System

## Overview

The Monopoly AI project supports custom board configurations through a JSON-based system. This allows you to create themed boards (like the Stoke-on-Trent variant) while maintaining the same game engine and AI agents.

## Key Features

- **JSON-based configuration**: Define boards in human-readable JSON files
- **Comprehensive validation**: Strict validation ensures boards are well-formed and consistent
- **Type safety**: Full Python type hints throughout the codebase
- **Flexible board sizes**: Support for non-standard board sizes (default: 41 tiles for Stoke-on-Trent)
- **Custom property groups**: Define new color groups beyond the standard 8
- **Backward compatibility**: Hardcoded classic 40-tile board still available

## Architecture

### File Structure

```
engine/
├── board.py              # MonopolyBoard class with config loading
├── board_config.py       # JSON loading and validation
├── state.py              # Data structures (TileInfo, PropertyGroup, etc.)
└── boards/               # JSON board configurations
    └── stoke_on_trent.json
```

### Key Components

1. **BoardConfigLoader**: Static class that loads and validates JSON configurations
2. **BoardMetadata**: Immutable dataclass containing board metadata
3. **MonopolyBoard**: Main board class with three initialization modes:
   - Default: Loads Stoke-on-Trent board
   - Named: Loads specific board by name
   - Hardcoded: Uses classic 40-tile board

## JSON Schema

### Board Configuration Structure

```json
{
  "name": "Board Name",
  "description": "Detailed description",
  "currency_symbol": "£",
  "go_salary": 200,
  "num_tiles": 41,
  "tiles": [
    // Array of tile objects (see below)
  ],
  "property_groups": {
    "brown": [1, 2],
    "light_blue": [5, 6, 7],
    // ... more groups
  },
  "special_tiles": {
    "go": 0,
    "jail": 10,
    "free_parking": 20,
    "go_to_jail": 36
  }
}
```

### Tile Types

#### 1. GO Tile
```json
{
  "id": 0,
  "type": "go",
  "name": "GO"
}
```

#### 2. Property Tile
```json
{
  "id": 1,
  "type": "property",
  "name": "Property Name",
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
}
```

**Valid Colours**:
- `brown`, `light_blue`, `pink`, `purple`, `orange`
- `red`, `yellow`, `green`, `dark_blue`, `special`

#### 3. Railroad/Station Tile
```json
{
  "id": 4,
  "type": "station",  // or "railroad"
  "name": "Station Name",
  "purchase_price": 200,
  "mortgage_value": 100
}
```

#### 4. Utility Tile
```json
{
  "id": 16,
  "type": "utility",
  "name": "Electric Company",
  "purchase_price": 150,
  "mortgage_value": 75
}
```

#### 5. Tax Tile
```json
{
  "id": 8,
  "type": "tax",
  "name": "Income Tax",
  "amount": 200
}
```

#### 6. Other Tile Types
```json
// Chance
{"id": 11, "type": "chance", "name": "Chance"}

// Community Chest
{"id": 3, "type": "community_chest", "name": "Community Chest"}

// Jail
{"id": 10, "type": "jail", "name": "Just Visiting"}

// Go To Jail
{"id": 36, "type": "go_to_jail", "name": "Go To Jail"}

// Free Parking
{"id": 20, "type": "free_parking", "name": "Free Parking"}
```

### Property Groups

The `property_groups` object maps color names to arrays of tile IDs:

```json
"property_groups": {
  "brown": [1, 2],
  "light_blue": [5, 6, 7],
  "purple": [9, 10],
  "orange": [13, 14, 15],
  "red": [17, 18],
  "yellow": [21, 22, 23],
  "green": [24, 25, 27],
  "dark_blue": [29, 30],
  "special": [33, 35, 37, 38, 40],
  "railroad": [4, 12, 20, 32],
  "utility": [16, 28]
}
```

## Validation Rules

The board configuration system enforces strict validation:

### Metadata Validation
- All required fields must be present: `name`, `description`, `currency_symbol`, `go_salary`, `num_tiles`
- `num_tiles` must be ≥ 4
- `go_salary` must be > 0

### Tile Validation
- Tile IDs must be consecutive integers from 0 to `num_tiles - 1`
- No duplicate tile IDs
- No missing tile IDs
- Each tile must have a valid `type`
- Type-specific fields must be present (e.g., properties need rent values)

### Property Group Validation
- All tile IDs in groups must exist
- Tiles cannot appear in multiple groups
- Tile color must match its group
- Railroads must be in `railroad` group
- Utilities must be in `utility` group

## Usage Examples

### Loading Boards in Python

```python
from engine.board import MonopolyBoard

# Load default board (Stoke-on-Trent)
board = MonopolyBoard()

# Load specific board by name
board = MonopolyBoard(board_name="stoke_on_trent")

# Use hardcoded classic board
board = MonopolyBoard(use_hardcoded=True)

# Access board information
print(f"Board: {board.metadata.name}")
print(f"Tiles: {board.num_tiles}")
print(f"Currency: {board.metadata.currency_symbol}")

# Access tiles
go_tile = board.tiles[0]
property_tile = board.tiles[1]

# Access property groups
brown_properties = board.property_groups[PropertyGroup.BROWN]
```

### Discovering Available Boards

```python
from engine.board_config import list_available_boards

boards = list_available_boards()
print(f"Available boards: {boards}")
```

### Direct Configuration Loading

```python
from engine.board_config import load_board_config

tiles, groups, metadata = load_board_config("stoke_on_trent")
```

## Stoke-on-Trent Board

The default board is a custom Stoke-on-Trent themed variant with **41 tiles** (vs standard 40).

### Key Differences from Classic Monopoly

1. **41 tiles instead of 40**: Additional property added at position 40
2. **New "special" property group**: 5 properties representing local institutions
3. **Local theming**: All properties renamed to Stoke landmarks
4. **Stations renamed**: Bus stations and railway stations instead of generic railroads
5. **Reduced red properties**: Only 2 instead of 3 (to accommodate special group)

### Property Groups

| Group       | Tiles | Examples                              |
|-------------|-------|---------------------------------------|
| Brown       | 2     | Potteries Museum, Stoke Minster       |
| Light Blue  | 3     | Etruria Museum, Hanley Park           |
| Purple      | 2     | Gladstone Pottery, Longton Park       |
| Orange      | 3     | Burslem School, Middleport Pottery    |
| Red         | 2     | Trentham Gardens, Monkey Forest       |
| Yellow      | 3     | Waterworld, Festival Park, Regent     |
| Green       | 3     | Potteries Centre, Bet365, Staffs Uni  |
| Dark Blue   | 2     | Trentham Estate, Wedgwood Centre      |
| **Special** | 5     | Royal Stoke, Keele, Cobridge, etc.    |
| Railroad    | 4     | Bus stations and railway stations     |
| Utility     | 2     | Electric Company, Water Works         |

### Special Property Group Economics

The special group has varied pricing to maintain game balance:

- Royal Stoke University Hospital: £100 (low value)
- Keele University: £140
- Cobridge: £180
- Tunstall Market: £220
- Hanley City Centre: £300 (high value)

This creates an asymmetric monopoly where completing all 5 properties is challenging but rewarding.

## Creating Custom Boards

### Step 1: Create JSON File

Create a new file in `engine/boards/your_board_name.json`:

```json
{
  "name": "Your Board Name",
  "description": "Description of your custom board",
  "currency_symbol": "$",
  "go_salary": 200,
  "num_tiles": 40,
  "tiles": [
    // Define all tiles here
  ],
  "property_groups": {
    // Define property groups
  }
}
```

### Step 2: Validate

The system will automatically validate your board on load. Common errors:

- **Missing tiles**: Ensure IDs are consecutive from 0 to `num_tiles - 1`
- **Invalid colors**: Use only supported color names
- **Group mismatches**: Ensure tile colors match their property group
- **Missing fields**: All required fields must be present for each tile type

### Step 3: Load and Test

```python
from engine.board import MonopolyBoard

# Load your custom board
board = MonopolyBoard(board_name="your_board_name")

# Run validation tests
from engine.tests.test_board_config import TestBoardConfigLoader
# pytest engine/tests/test_board_config.py
```

## Integration with Game Engine

The board configuration integrates seamlessly with the game engine:

### Position Modulo Operations

The engine uses modulo arithmetic for wrapping positions:

```python
new_position = (current_position + dice_roll) % board.num_tiles
```

This automatically handles boards of any size.

### Rent Calculations

Rent calculations use the PropertyInfo directly:

```python
tile = board.tiles[position]
if tile.property_info:
    rent = tile.property_info.get_rent(num_houses)
```

### Monopoly Detection

The engine checks if a player owns all properties in a group:

```python
def has_monopoly(self, owned_tiles: Set[int], group: PropertyGroup) -> bool:
    group_tiles = set(self.get_group_tiles(group))
    return group_tiles.issubset(owned_tiles)
```

This works for any property group size.

## Testing

Comprehensive unit tests ensure board configurations are valid:

```bash
# Run all board config tests
pytest engine/tests/test_board_config.py -v

# Run specific test class
pytest engine/tests/test_board_config.py::TestBoardValidation -v
```

### Test Coverage

- Default board loading
- Property group validation
- Tile type validation
- Metadata validation
- Error handling for malformed configs
- Type alias support (station → railroad)

## Design Decisions

### 1. Why JSON?

- **Human-readable**: Easy to create and modify
- **Structured**: Clear schema with validation
- **Portable**: Can be shared and version controlled
- **Extensible**: Easy to add new fields

### 2. Why Immutable Metadata?

Using `@dataclass(frozen=True)` for BoardMetadata ensures:
- Thread safety
- Prevents accidental modification
- Clear contract: configuration is read-only

### 3. Why Support Hardcoded Board?

The hardcoded classic board:
- Serves as a reference implementation
- Enables testing without file I/O
- Provides fallback if JSON loading fails

### 4. Why 41 Tiles for Stoke?

The custom board adds a 5th property to create the "special" group, requiring 41 tiles total. This demonstrates the system's flexibility while maintaining game balance.

## Future Enhancements

Potential extensions to the board configuration system:

1. **Dynamic card decks**: Configure Chance/Community Chest cards per board
2. **Custom rules**: Per-board rule variations (e.g., different GO salary)
3. **Board validation CLI**: Command-line tool to validate JSON files
4. **Board editor**: GUI tool for creating boards visually
5. **Multiple board support**: Load multiple boards for variety in training

## Troubleshooting

### Common Issues

**Q: Board won't load**
```python
BoardValidationError: Missing required field: num_tiles
```
**A**: Ensure all metadata fields are present in your JSON.

**Q: Tile validation error**
```python
BoardValidationError: Missing tile IDs: [5, 7]
```
**A**: Ensure tile IDs are consecutive from 0 to `num_tiles - 1`.

**Q: Property group mismatch**
```python
BoardValidationError: Tile 5 property group mismatch
```
**A**: Check that tile's `colour` field matches its group in `property_groups`.

### Debugging

Enable verbose error messages:

```python
try:
    board = MonopolyBoard(board_name="custom_board")
except BoardValidationError as e:
    print(f"Validation error: {e.message}")
    if e.tile_id is not None:
        print(f"  Tile ID: {e.tile_id}")
    if e.field is not None:
        print(f"  Field: {e.field}")
```

## References

- **State Types**: `engine/state.py` - Core data structures
- **Board Config**: `engine/board_config.py` - Loading and validation
- **Board Class**: `engine/board.py` - MonopolyBoard implementation
- **Tests**: `engine/tests/test_board_config.py` - Comprehensive test suite
- **Demo**: `examples/board_configuration_demo.py` - Usage examples
