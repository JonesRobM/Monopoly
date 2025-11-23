# Monopoly AI

A reproducible, multi-agent Monopoly environment for reinforcement learning research.

## Status

**Phase 1: Rules Engine - ✅ COMPLETE**

- 📦 Full game engine implementation (~2,700 lines)
- 🧪 101 passing tests (100% success rate)
- 🎯 PettingZoo-compatible environment
- 🔢 562-action discrete space with masking
- 📊 ~450-dimensional observation space
- ⚡ 0.26s test suite runtime

## Overview

This project implements a complete Monopoly game engine with a PettingZoo-compatible interface for training multi-agent reinforcement learning algorithms. The implementation emphasizes:

- **Deterministic core**: Fixed RNG seeds produce reproducible games
- **Pure functions**: Testable, side-effect-free state transitions
- **Action masking**: Prevents invalid moves during RL training
- **Multi-agent first**: Designed for simultaneous policy learning

## Project Structure

```
monopoly-ai/
├── engine/                 # Core game engine
│   ├── state.py           # Game state structures
│   ├── board.py           # Monopoly board (40 or 41 tiles)
│   ├── board_config.py    # Board configuration loader
│   ├── boards/            # Board configurations (JSON)
│   ├── rules.py           # Game rules and validation
│   ├── cards.py           # Chance and Community Chest
│   ├── actions.py         # Action space definition
│   ├── transitions.py     # Pure state transition functions
│   └── tests/             # Unit and integration tests
├── env/                   # RL environment wrappers
│   ├── pettingzoo_api.py  # PettingZoo AEC environment
│   ├── encoding.py        # State → observation encoding
│   ├── action_masking.py  # Legal action masks
│   └── utils.py           # Utilities
├── visualization/         # Graphical rendering (pygame)
│   ├── renderer.py        # Main renderer
│   ├── board_layout.py    # Board geometry
│   ├── tile_renderer.py   # Tile rendering
│   ├── player_renderer.py # Player pieces and buildings
│   ├── animation.py       # Animation system
│   ├── info_panel.py      # Game state display
│   ├── colors.py          # Color definitions
│   └── tests/             # Visualization tests
├── agents/                # Agent implementations (future)
├── training/              # Training scripts (future)
├── analysis/              # Evaluation tools (future)
├── examples/              # Demo scripts
└── requirements.txt       # Python dependencies
```

## Installation

### Prerequisites

- Python 3.12+
- pip

### Quick Start

```bash
# Clone the repository
cd monopoly-ai

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package with dependencies
pip install -e .

# Run tests to verify installation
pytest

# Try the example
python example_usage.py
```

### Development Installation

```bash
# Install with all development dependencies
pip install -e ".[dev]"

# Or install specific extras
pip install -e ".[rl]"      # For RL training
pip install -e ".[analysis]" # For analysis tools
pip install -e ".[all]"      # Everything
```

## Usage

### Basic Environment Usage

```python
from env import MonopolyEnv
import numpy as np

# Create environment with 4 players
env = MonopolyEnv(num_players=4, seed=42)

# Reset environment
env.reset()

# Game loop
for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()

    if termination or truncation:
        action = None
    else:
        # Get legal action mask
        action_mask = observation["action_mask"]

        # Sample random legal action (replace with your agent)
        legal_actions = np.where(action_mask > 0.5)[0]
        action = np.random.choice(legal_actions)

    env.step(action)
```

### Using Game Engine Directly

```python
from engine import MonopolyBoard, GameState, PlayerState, GameConfig, RulesEngine
from engine import move_player, purchase_property

# Create board and rules
board = MonopolyBoard()
config = GameConfig(num_players=2, seed=42)
rules = RulesEngine(board, config)

# Initialize game state
players = [
    PlayerState(player_id=0, name="Player 1"),
    PlayerState(player_id=1, name="Player 2")
]
state = GameState(players=players)

# Move player 0 to position 5
state = move_player(state, player_id=0, new_position=5, go_salary=200)

# Purchase Reading Railroad (tile 5)
if rules.can_buy_property(state, 0, 5):
    price = board.get_purchase_price(5)
    state = purchase_property(state, 0, 5, price)
```

## Testing

Run all tests:

```bash
pytest
```

Run specific test categories:

```bash
# Unit tests only
pytest engine/tests/test_state.py
pytest engine/tests/test_board.py

# Integration tests
pytest engine/tests/test_integration.py

# With coverage
pytest --cov=engine --cov=env --cov-report=html
```

## Game Rules

### Implemented Features

- ✅ 40-tile standard Monopoly board
- ✅ 2-6 player support
- ✅ Property ownership and rent calculation
- ✅ Monopoly detection (color set completion)
- ✅ Building houses and hotels with even building rules
- ✅ Mortgaging and unmortgaging
- ✅ Chance and Community Chest cards
- ✅ Jail mechanics (roll doubles, pay fine, use card)
- ✅ Bankruptcy and game-over detection
- ✅ Deterministic dice rolls with seeded RNG

### Simplified Features (MVP)

- ⚠️ **Auctions**: Simplified bidding (template-based)
- ⚠️ **Trading**: Template-based trades (not free-form)
- ⚠️ **Card effects**: Subset of standard cards implemented

### Not Yet Implemented

- ❌ Free Parking pool (optional house rule)
- ❌ Natural language trade negotiation
- ❌ Human-in-the-loop play

## Visualization

The project includes a complete graphical visualization system using pygame. Watch AI agents play in real-time with:

- Full board rendering with property colors
- Animated player movement
- Houses and hotels display
- Property ownership indicators
- Real-time game state panel
- Message notifications

### Running Visualization Demos

```bash
# Interactive visualization demo
python examples/demo_visualization.py

# Watch AI agents play with visualization
python examples/demo_env_with_viz.py --players 4 --step-delay 0.5
```

### Using Visualization in Code

```python
from env import MonopolyEnv

# Create environment with pygame rendering
env = MonopolyEnv(num_players=4, render_mode="pygame")

# Game loop
env.reset()
for _ in range(100):
    action = agent.select_action(env.observe(env.agent_selection))
    env.step(action)
    env.render()  # Shows graphical window

env.close()
```

See `visualization/README.md` for detailed documentation.

## State Representation

### Observation Space (~450 dimensions for 4 players)

- **Player state** (per player):
  - Position: 40-dim one-hot encoding
  - Cash: normalized float
  - Jail status: binary + turns in jail
  - Get out of jail cards: count

- **Property state** (40 properties):
  - Ownership: one-hot per property (unowned + 6 players)
  - Houses: 0-5 (normalized)
  - Mortgaged: binary

- **Game state**:
  - Turn number: normalized
  - Doubles count
  - Houses/hotels remaining

### Action Space (562 discrete actions)

- Buy/decline property purchase
- Auction bidding (10 bid levels)
- Build/sell houses and hotels (per property)
- Mortgage/unmortgage properties
- Trade offers (50 templates × target players)
- Jail actions (pay, use card, roll)
- End turn

## Development Roadmap

### Phase 1: Rules Engine ✅ (Completed)

- Complete engine implementation
- Full unit test coverage
- Deterministic integration tests

### Phase 2: Baseline Agents (Next)

- Random agent
- Heuristic agents:
  - Greedy buyer
  - Conservative player
  - Aggressive builder
- Auction bidding logic

### Phase 3: RL Training

- PPO with action masking
- Self-play training loop
- Elo rating system
- Performance benchmarks

### Phase 4: Strategy Diversity

- Population-based training (PBT)
- MAP-Elites for behavioral diversity
- Strategy clustering and visualization

## Design Principles

1. **Deterministic Core**: All randomness uses seeded RNG for reproducibility
2. **Pure Functions**: Transitions are side-effect free and independently testable
3. **Separation of Concerns**:
   - `engine/` → Game logic
   - `env/` → RL interface
   - `agents/` → Agent implementations
   - `training/` → Training loops
4. **Type Safety**: Comprehensive type hints throughout
5. **Test Coverage**: Unit and integration tests for all components

## Performance Targets

- **Speed**: 1,000+ steps/second (single thread)
- **Memory**: <100MB per environment instance
- **Determinism**: 100% reproducible with fixed seeds

## Development Tools

This project uses modern Python development tools:

- **Packaging**: `pyproject.toml` (PEP 518/621)
- **Formatting**: `black` (100 char line length)
- **Linting**: `ruff` (faster alternative to flake8)
- **Type Checking**: `mypy` (strict mode)
- **Testing**: `pytest` with coverage reporting
- **Pre-commit**: Automated checks before commits
- **CI/CD**: GitHub Actions workflow

### Quick Commands

```bash
make install-dev  # Install with dev dependencies
make test         # Run all tests
make test-cov     # Run tests with coverage
make format       # Format code with black/ruff
make lint         # Run all linters
make type-check   # Run mypy type checking
make clean        # Clean build artifacts
```

See `CONTRIBUTING.md` for detailed development guidelines.

## Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for guidelines.

This project follows these coding standards:

- Python 3.12+ with comprehensive type hints
- Black code formatting (100 char lines)
- Ruff linting with strict rules
- MyPy type checking
- 90%+ test coverage requirement
- Google-style docstrings

## Troubleshooting

### NumPy Warnings on Windows

If you see warnings about "MINGW-W64" or "experimental" when running the examples on Windows:

```
Warning: Numpy built with MINGW-W64 on Windows 64 bits is experimental...
```

**These warnings are harmless** but annoying. They come from NumPy's experimental Windows build.

**Solutions:**

1. **Suppress warnings in your script** (already done in `example_usage.py`):
   ```python
   import warnings
   warnings.filterwarnings("ignore", message=".*MINGW-W64.*")
   warnings.filterwarnings("ignore", category=RuntimeWarning, module="numpy")
   ```

2. **Use environment variable**:
   ```bash
   # Windows PowerShell
   $env:PYTHONWARNINGS="ignore::RuntimeWarning"
   python example_usage.py

   # Windows CMD
   set PYTHONWARNINGS=ignore::RuntimeWarning
   python example_usage.py
   ```

3. **Install a different NumPy build** (if issues persist):
   ```bash
   pip uninstall numpy
   pip install numpy --only-binary :all:
   ```

### Import Errors

If you get import errors, make sure you've installed the package:
```bash
pip install -e .
```

### Test Failures

If tests fail, ensure you're in the project root directory:
```bash
cd /path/to/monopoly-ai
pytest
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## References

- [PettingZoo Documentation](https://pettingzoo.farama.org/)
- [Gymnasium Documentation](https://gymnasium.farama.org/)
- Standard Monopoly rules (Hasbro)

## Acknowledgments

Built following architectural principles from:
- OpenSpiel multi-agent game framework
- PettingZoo AEC API design
- Population-based training research
