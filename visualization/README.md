# Monopoly Visualization Module

Graphical visualization system for watching AI agents play Monopoly in real-time using pygame.

## Features

- **Full Board Rendering**: Displays all 40 or 41 tiles with proper colors and labels
- **Player Pieces**: Color-coded circular pieces for up to 6 players
- **Property Ownership**: Visual indicators showing which player owns each property
- **Buildings**: Displays houses (green squares) and hotels (red rectangles) on properties
- **Smooth Animation**: Animated player movement around the board
- **Game State Panel**: Real-time display of player cash, properties, and status
- **Message System**: Temporary on-screen messages for game events
- **Multi-Board Support**: Works with both classic 40-tile and custom 41-tile boards

## Architecture

The visualization module follows the project's separation of concerns principle:

```
visualization/
├── __init__.py           # Module exports
├── renderer.py           # Main renderer coordinating all components
├── board_layout.py       # Board geometry and tile positioning
├── tile_renderer.py      # Individual tile rendering
├── player_renderer.py    # Player pieces and buildings
├── animation.py          # Animation system
├── info_panel.py         # Game state information panels
├── colors.py             # Color definitions
└── tests/                # Unit tests
```

## Usage

### Basic Usage

```python
from engine.board import MonopolyBoard
from engine.state import GameState
from visualization.renderer import MonopolyRenderer

# Create board and renderer
board = MonopolyBoard()
renderer = MonopolyRenderer(board, enable_animation=True)

# Game loop
running = True
while running:
    # Handle events
    running = renderer.handle_events()

    # Update game state
    # ... (your game logic)

    # Render
    renderer.render(game_state)

# Cleanup
renderer.close()
```

### With PettingZoo Environment

```python
from env.pettingzoo_api import MonopolyEnv

# Create environment with pygame rendering
env = MonopolyEnv(num_players=4, render_mode="pygame")

# Reset and play
env.reset()
env.render()

for _ in range(100):
    # Agent selects action
    action = agent.select_action(env.observe(env.agent_selection))

    # Take step
    env.step(action)

    # Render
    env.render()

env.close()
```

### Running Demos

```bash
# Interactive visualization demo
python examples/demo_visualization.py

# Environment with AI agents
python examples/demo_env_with_viz.py --players 4 --step-delay 0.5
```

## Components

### MonopolyRenderer

Main rendering class that coordinates all visualization components.

**Parameters:**
- `board`: MonopolyBoard instance
- `window_width`: Window width in pixels (default: 1200)
- `window_height`: Window height in pixels (default: 800)
- `enable_animation`: Enable smooth animations (default: True)
- `fps`: Target frames per second (default: 60)

**Methods:**
- `render(game_state)`: Render current game state
- `handle_events()`: Process pygame events, returns False if window closed
- `add_message(message)`: Add temporary on-screen message
- `save_screenshot(filename)`: Save current rendering to image file
- `close()`: Cleanup and close renderer

### BoardLayout

Calculates tile positions for square board layout.

**Parameters:**
- `num_tiles`: Number of tiles (40 or 41)
- `board_size`: Board size in pixels

**Methods:**
- `get_tile_position(tile_id)`: Get position and dimensions of a tile
- `get_tile_center(tile_id)`: Get center coordinates of a tile
- `get_player_offset(tile_id, player_idx, num_players)`: Get offset for player pieces
- `get_center_area()`: Get center area coordinates

### TileRenderer

Renders individual tiles with appropriate styling.

Handles:
- Properties with color bars
- Corner tiles (GO, Jail, Free Parking, Go To Jail)
- Railroads and utilities
- Chance and Community Chest
- Tax tiles
- Mortgage overlays

### PlayerRenderer

Renders player pieces as colored circles with player numbers.

Automatically spaces multiple players on the same tile.

### BuildingRenderer

Renders houses and hotels on properties.

- Houses: Small green squares (up to 4)
- Hotel: Larger red rectangle (replaces 4 houses)

### OwnershipIndicator

Shows property ownership with small colored circles matching player colors.

### AnimationManager

Manages smooth animations for player movement.

Uses ease-in-out cubic interpolation for natural-looking movement.

## Color Scheme

### Property Groups
- Brown: #8B4513
- Light Blue: #ADD8E6
- Pink: #FFC0CB
- Purple: #9370DB
- Orange: #FFA500
- Red: #DC143C
- Yellow: #FFFF00
- Green: #228B22
- Dark Blue: #00008B

### Players
- Player 0: Red
- Player 1: Blue
- Player 2: Green
- Player 3: Yellow
- Player 4: Magenta
- Player 5: Cyan

## Performance

- Target: 60 FPS for smooth visualization
- Efficient rendering using pygame surfaces
- Animations use time-based interpolation
- Supports headless mode (no rendering overhead)

## Testing

Run visualization tests:

```bash
pytest visualization/tests/ -v
```

Tests cover:
- Board layout geometry
- Color mappings
- Animation timing and interpolation

## Design Principles

1. **Deterministic Core**: Visualization is separate from game logic
2. **Optional Rendering**: Headless mode for training
3. **Type Safety**: Full type hints throughout
4. **Testability**: Pure functions where possible
5. **Performance**: 60 FPS with up to 6 players
6. **Separation of Concerns**: Each component has single responsibility

## Future Enhancements

Potential additions (not in current scope):

- Dice roll animations
- Card draw animations
- Trade negotiation overlays
- Property detail tooltips on hover
- Replay system
- Screenshot/video recording
- Theme customization
- Accessibility options (color-blind modes)

## Dependencies

- pygame >= 2.0.0
- Python >= 3.12

## License

See LICENSE_INFO.md in project root.
