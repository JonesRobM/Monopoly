# Monopoly AI Visualization Guide

Complete guide to the graphical visualization system for watching AI agents play Monopoly.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [API Reference](#api-reference)
5. [Examples](#examples)
6. [Customization](#customization)
7. [Performance](#performance)
8. [Troubleshooting](#troubleshooting)

## Overview

The visualization module provides real-time graphical rendering of Monopoly games using pygame. It's designed to:

- Work seamlessly with the PettingZoo environment
- Support both 40-tile classic and 41-tile custom boards
- Provide smooth animations for player movement
- Display complete game state information
- Remain optional (headless mode for training)

### Key Features

- **Board Rendering**: All tiles with proper colors and labels
- **Player Pieces**: Up to 6 color-coded players
- **Property Display**: Ownership indicators and buildings
- **Animation**: Smooth player movement with easing
- **Info Panel**: Real-time stats (cash, properties, status)
- **Messages**: Temporary notifications for game events

## Quick Start

### Minimal Example

```python
from engine.board import MonopolyBoard
from engine.state import GameState, PlayerState
from visualization.renderer import MonopolyRenderer

# Create board and renderer
board = MonopolyBoard()
renderer = MonopolyRenderer(board)

# Create game state
players = [PlayerState(player_id=i, name=f"Player {i}") for i in range(4)]
game_state = GameState(players=players)

# Render loop
running = True
while running:
    running = renderer.handle_events()
    renderer.render(game_state)

renderer.close()
```

### With PettingZoo Environment

```python
from env.pettingzoo_api import MonopolyEnv

# Create environment with pygame rendering
env = MonopolyEnv(num_players=4, render_mode="pygame")

env.reset()
for _ in range(100):
    # Get action from agent
    obs = env.observe(env.agent_selection)
    action = agent.select_action(obs)

    # Step and render
    env.step(action)
    env.render()

env.close()
```

### Running Demos

```bash
# All demos with menu
python examples/demo_visualization.py

# Specific demo
python examples/demo_visualization.py
# Then choose from menu:
#   1. Static Board - See properties, houses, hotels
#   2. Animated Movement - Watch smooth player movement
#   3. Messages - See game event notifications
#   4. Interactive - Press SPACE to advance turns

# AI agents with visualization
python examples/demo_env_with_viz.py --players 4 --step-delay 0.5
```

## Architecture

### Module Structure

```
visualization/
├── __init__.py           # Exports MonopolyRenderer, BoardLayout
├── renderer.py           # Main renderer (coordinates all components)
├── board_layout.py       # Tile position calculations
├── tile_renderer.py      # Renders individual tiles
├── player_renderer.py    # Player pieces, buildings, ownership
├── animation.py          # Animation system with easing
├── info_panel.py         # Info panels and messages
├── colors.py             # Color definitions
└── tests/                # Unit tests
```

### Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| `MonopolyRenderer` | Coordinates rendering, manages pygame window |
| `BoardLayout` | Calculates tile positions and geometry |
| `TileRenderer` | Draws individual tiles with correct styling |
| `PlayerRenderer` | Draws player pieces on tiles |
| `BuildingRenderer` | Draws houses and hotels on properties |
| `OwnershipIndicator` | Shows property ownership markers |
| `AnimationManager` | Manages smooth animations |
| `InfoPanel` | Displays player stats and game info |
| `MessageDisplay` | Shows temporary event messages |

### Design Principles

1. **Separation**: Visualization is completely separate from game logic
2. **Optional**: Can run headless for training (no rendering overhead)
3. **Deterministic Core**: Rendering doesn't affect game state
4. **Type Safety**: Full type hints throughout
5. **Testability**: Pure calculation functions tested independently

## API Reference

### MonopolyRenderer

Main rendering class.

```python
class MonopolyRenderer:
    def __init__(
        self,
        board: MonopolyBoard,
        window_width: int = 1200,
        window_height: int = 800,
        enable_animation: bool = True,
        fps: int = 60
    )
```

**Parameters:**
- `board`: MonopolyBoard instance with tile configuration
- `window_width`: Window width in pixels
- `window_height`: Window height in pixels
- `enable_animation`: Enable smooth animations for movement
- `fps`: Target frames per second

**Methods:**

```python
def render(self, game_state: GameState) -> None
    """Render current game state to screen."""

def handle_events(self) -> bool
    """Handle pygame events. Returns False if window closed."""

def add_message(self, message: str) -> None
    """Add temporary on-screen message (2 second display)."""

def save_screenshot(self, filename: str) -> None
    """Save current rendering to image file."""

def close(self) -> None
    """Cleanup and close renderer."""
```

**Example:**

```python
renderer = MonopolyRenderer(board, enable_animation=True)

# Game loop
while renderer.handle_events():
    # Update game logic
    # ...

    # Render
    renderer.render(game_state)

    # Optional: Add messages
    if player_bought_property:
        renderer.add_message(f"Player {pid} bought {property_name}")

renderer.close()
```

### BoardLayout

Calculates tile positions for square board layout.

```python
class BoardLayout:
    def __init__(self, num_tiles: int, board_size: int = 800)
```

**Methods:**

```python
def get_tile_position(self, tile_id: int) -> TilePosition
    """Get position and dimensions of a tile."""

def get_tile_center(self, tile_id: int) -> Tuple[int, int]
    """Get center coordinates of a tile."""

def get_player_offset(
    self,
    tile_id: int,
    player_idx: int,
    num_players: int
) -> Tuple[int, int]
    """Get offset for player pieces (automatic spacing)."""

def get_center_area(self) -> Tuple[int, int, int, int]
    """Get center area coordinates (x, y, width, height)."""
```

**TilePosition:**

```python
@dataclass(frozen=True)
class TilePosition:
    tile_id: int
    x: int          # Top-left x coordinate
    y: int          # Top-left y coordinate
    width: int      # Tile width
    height: int     # Tile height
    side: str       # "bottom", "left", "top", "right"
    is_corner: bool # True for corner tiles
```

### AnimationManager

Manages smooth player movement animations.

```python
class AnimationManager:
    def add_player_move(
        self,
        player_id: int,
        from_position: int,
        to_position: int,
        from_coords: Tuple[int, int],
        to_coords: Tuple[int, int],
        duration: float = 0.5
    ) -> None

    def get_player_position(
        self,
        player_id: int,
        default_coords: Tuple[int, int]
    ) -> Tuple[int, int]

    def is_animating(self) -> bool

    def clear(self) -> None
```

## Examples

### Example 1: Static Display

Show a game state without animation.

```python
from engine.board import MonopolyBoard
from engine.state import GameState, PlayerState, PropertyState
from visualization.renderer import MonopolyRenderer

board = MonopolyBoard()
renderer = MonopolyRenderer(board, enable_animation=False)

# Create interesting game state
players = [
    PlayerState(player_id=0, position=0, cash=1500, owned_properties={1, 3}),
    PlayerState(player_id=1, position=10, cash=1200, owned_properties={6, 8, 9}),
    PlayerState(player_id=2, position=24, cash=800, owned_properties={16, 18, 19}),
]

properties = {
    1: PropertyState(tile_id=1, owner=0, num_houses=0),
    3: PropertyState(tile_id=3, owner=0, num_houses=0),
    6: PropertyState(tile_id=6, owner=1, num_houses=1),
    8: PropertyState(tile_id=8, owner=1, num_houses=1),
    9: PropertyState(tile_id=9, owner=1, num_houses=2),
    16: PropertyState(tile_id=16, owner=2, num_houses=3),
    18: PropertyState(tile_id=18, owner=2, num_houses=4),
    19: PropertyState(tile_id=19, owner=2, num_houses=5),  # Hotel
}

game_state = GameState(players=players, properties=properties)

# Display
while renderer.handle_events():
    renderer.render(game_state)

renderer.close()
```

### Example 2: Animated Movement

Move players smoothly around the board.

```python
import time
from engine.board import MonopolyBoard
from engine.state import GameState, PlayerState
from visualization.renderer import MonopolyRenderer

board = MonopolyBoard()
renderer = MonopolyRenderer(board, enable_animation=True)

players = [PlayerState(player_id=0, position=0)]
game_state = GameState(players=players)

# Move player around the board
for position in range(40):
    game_state.players[0].position = position
    renderer.render(game_state)

    # Wait for animation
    time.sleep(0.5)

    if not renderer.handle_events():
        break

renderer.close()
```

### Example 3: With Messages

Display game events with messages.

```python
from engine.board import MonopolyBoard
from engine.state import GameState, PlayerState
from visualization.renderer import MonopolyRenderer
import time

board = MonopolyBoard()
renderer = MonopolyRenderer(board)

players = [PlayerState(player_id=0, position=0)]
game_state = GameState(players=players)

events = [
    (0, "Player 0 rolls 4, 3"),
    (1, "Player 0 moves to position 7"),
    (2, "Player 0 buys Oriental Avenue"),
]

start_time = time.time()
while renderer.handle_events():
    current_time = time.time() - start_time

    # Check for events
    for event_time, message in events:
        if abs(current_time - event_time) < 0.1:
            renderer.add_message(message)

    renderer.render(game_state)

    if current_time > 5:
        break

renderer.close()
```

### Example 4: Screenshot Capture

Capture game state as images.

```python
from engine.board import MonopolyBoard
from engine.state import GameState, PlayerState
from visualization.renderer import MonopolyRenderer

board = MonopolyBoard()
renderer = MonopolyRenderer(board)

players = [PlayerState(player_id=i, position=i*10) for i in range(4)]
game_state = GameState(players=players)

# Render and capture
renderer.render(game_state)
renderer.save_screenshot("monopoly_state.png")

renderer.close()
```

## Customization

### Custom Colors

Modify `visualization/colors.py`:

```python
# Change player colors
PLAYER_COLORS = [
    (255, 100, 100),  # Light red
    (100, 100, 255),  # Light blue
    # ... etc
]

# Change property colors
PROPERTY_COLORS[PropertyGroup.BROWN] = (150, 75, 0)
```

### Custom Window Size

```python
# Larger window
renderer = MonopolyRenderer(board, window_width=1600, window_height=1000)

# Smaller window
renderer = MonopolyRenderer(board, window_width=800, window_height=600)
```

### Disable Animation

```python
# No animations (instant movement)
renderer = MonopolyRenderer(board, enable_animation=False)
```

### Custom Animation Speed

Modify animation duration when creating animations:

```python
# In animation.py or custom code
animation_manager.add_player_move(
    player_id=0,
    from_position=0,
    to_position=10,
    from_coords=(100, 100),
    to_coords=(200, 200),
    duration=1.0  # Slower (default is 0.5)
)
```

## Performance

### Benchmarks

- **Target FPS**: 60
- **Typical FPS**: 55-60 with 6 players and animations
- **Memory Usage**: ~50MB for renderer
- **Startup Time**: <1 second

### Optimization Tips

1. **Disable Animation for Speed**:
   ```python
   renderer = MonopolyRenderer(board, enable_animation=False)
   ```

2. **Lower FPS**:
   ```python
   renderer = MonopolyRenderer(board, fps=30)
   ```

3. **Smaller Window**:
   ```python
   renderer = MonopolyRenderer(board, window_width=800, window_height=600)
   ```

4. **Headless Mode for Training**:
   ```python
   env = MonopolyEnv(render_mode=None)  # No rendering overhead
   ```

## Troubleshooting

### Common Issues

#### 1. Pygame Not Found

```
ModuleNotFoundError: No module named 'pygame'
```

**Solution:**
```bash
pip install pygame
```

#### 2. Window Not Responding

If the window freezes, ensure you're calling `handle_events()`:

```python
while running:
    running = renderer.handle_events()  # Important!
    renderer.render(game_state)
```

#### 3. Slow Performance

- Reduce window size
- Disable animations
- Lower FPS target
- Check system resources

#### 4. Display Issues on High DPI Screens

On Windows with high DPI:

```python
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)
```

Add before pygame initialization.

#### 5. Tiles Not Aligned

Verify board has correct number of tiles:

```python
# Check board tile count
print(f"Board has {board.num_tiles} tiles")

# Should be 40 or 41
assert board.num_tiles in [40, 41]
```

### Debug Mode

Enable pygame debug info:

```python
import pygame
pygame.init()
print(pygame.display.Info())
```

## Integration with PettingZoo

### Render Modes

The MonopolyEnv supports three render modes:

```python
# Pygame graphical rendering
env = MonopolyEnv(render_mode="pygame")

# ANSI text rendering (console)
env = MonopolyEnv(render_mode="ansi")

# Human-readable text
env = MonopolyEnv(render_mode="human")

# No rendering (headless)
env = MonopolyEnv(render_mode=None)
```

### Render Loop

```python
env = MonopolyEnv(num_players=4, render_mode="pygame")
env.reset()

for agent in env.agent_iter():
    obs, reward, term, trunc, info = env.last()

    if term or trunc:
        action = None
    else:
        action = agent.select_action(obs)

    env.step(action)
    env.render()  # Updates pygame window

env.close()
```

### Controlling Render Speed

```python
import time

for _ in range(100):
    action = agent.select_action(obs)
    env.step(action)
    env.render()

    time.sleep(0.5)  # 0.5 second delay between steps
```

## Testing

Run visualization tests:

```bash
# All visualization tests
pytest visualization/tests/ -v

# Specific test file
pytest visualization/tests/test_board_layout.py -v
pytest visualization/tests/test_colors.py -v
pytest visualization/tests/test_animation.py -v
```

## Future Enhancements

Potential future additions (not currently implemented):

- Dice roll animations with 3D dice
- Card draw animations
- Trade negotiation UI overlay
- Property detail tooltips
- Click-to-inspect features
- Replay system with timeline scrubbing
- Video recording to MP4
- Theme/skin customization
- Accessibility features (colorblind modes, high contrast)
- Sound effects
- Zoom and pan controls
- Multiple camera views

## Additional Resources

- `visualization/README.md` - Module overview
- `examples/demo_visualization.py` - Interactive demos
- `examples/demo_env_with_viz.py` - AI agent visualization
- Project README - Overall architecture
- CLAUDE.md - Project philosophy and constraints

## License

See LICENSE_INFO.md in project root (Apache 2.0).
