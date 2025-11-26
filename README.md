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

**Phase 2: 10-Agent RL System - ✅ COMPLETE**

- 🤖 10 distinct agent personalities (Alice → Jack)
- 🎯 Custom per-agent reward functions (6 weighted components)
- 🧠 Hybrid heuristic + learned policies (alpha annealing)
- 🏗️ Structured transformer architecture (128-dim, 4 heads, 3 layers)
- 📚 Complete PPO training infrastructure
- 🎮 Multi-agent training coordinator (game loop, updates, checkpointing)
- 💾 Game recording system (1% sample for visualization)
- 🚀 CLI entry point with full argument parsing
- ✅ 75/75 unit tests passing (~17s runtime)
- 📝 28 implementation files (~4,500 lines)
- 🎓 Ready to train!

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
├── agents/                # 10-agent RL system
│   ├── reward_shaper.py   # Custom per-agent reward functions
│   ├── heuristics.py      # Behavioral policy biases (10 agents)
│   ├── alpha_schedules.py # Per-agent annealing schedules
│   ├── base_agent.py      # RLAgent class (hybrid policies)
│   └── tests/             # 34 unit tests
├── models/                # Neural network architectures
│   ├── tokenizer.py       # State → structured tokens
│   ├── transformer.py     # MonopolyTransformer (128-dim)
│   └── tests/             # 18 unit tests
├── training/              # Training infrastructure
│   ├── replay_buffer.py   # PPO replay buffer with GAE
│   ├── ppo_trainer.py     # PPO update algorithm
│   ├── evaluator.py       # Metrics tracking (win rates, rewards)
│   ├── game_recorder.py   # Game recording for visualization
│   └── tests/             # 23 unit tests
├── config/                # Configuration files
│   └── player_behaviours.json  # 10 agent configurations
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

## 10-Agent RL System

The project includes a sophisticated multi-agent RL training system with 10 distinct agent personalities, each learning optimal strategies given their behavioral archetype.

### Agent Personalities

Each agent has a unique strategy profile:

- **Alice** - Conservative money maximiser (ROI > 10%, high cash buffer)
- **Bob** - High-value property acquirer (prefers red/green/dark-blue)
- **Charlie** - Infrastructure collector (railroads & utilities focus)
- **Dee** - Trade specialist (arbitrage and negotiation)
- **Ethel** - Property hoarder (aggressive buyer)
- **Frankie** - Development maximiser (heavy building)
- **Greta** - Monopoly completer (color set focus)
- **Harry** - Resource denial (blocking strategies)
- **Irene** - Balanced investor (moderate approach)
- **Jack** - Hyper-aggressive (maximum risk-taking)

### Architecture

**Hybrid Policy System:**
```
action_probs = alpha(t) × heuristic_probs + (1-alpha(t)) × learned_probs
```

- **Heuristics**: Per-agent behavioral biases (multiplicative on action probabilities)
- **Alpha Annealing**: Per-agent schedules (Alice: 0.8→0.5, Jack: 0.7→0.05)
- Agents gradually shift from rule-based to learned behavior

**Custom Reward Functions:**

Each agent has unique priority weights for 6 reward components:

1. **cash**: Δcash (immediate financial impact)
2. **rent_yield**: Actual rent collected
3. **property_count**: Δproperties with mortgage penalties (±0.5)
4. **development**: Δhouses/hotels (+1/-1)
5. **trade_value**: Economic property value + cash
6. **monopoly_completion**: Large strategic bonuses
   - +1000 for completing a monopoly
   - +300 for blocking opponents
   - -500 when opponent completes

**Model Architecture:**

- **Tokenizer**: Structured state representation
  - 40 property tokens (owner, houses, mortgage, group, price, position, rent)
  - 4-6 player tokens (cash, position, jail, properties, current_player)
  - 1 game token (turn, doubles, houses/hotels remaining)
- **Transformer**: MonopolyTransformer (d_model=128, 4 heads, 3 layers)
  - Positional encoding for properties
  - Attention pooling aggregation
  - Actor head (562 action logits) + Critic head (1 value estimate)

**Training Protocol:**

- Random 4-6 agents selected per game
- Separate replay buffers per agent
- PPO updates every 10 games
- Track win rates and rewards every 100 games
- Checkpoint models every 1000 games
- 1% of games recorded for strategy visualization

### Running Tests

```bash
# Run all 10-agent system tests
pytest agents/tests/ models/tests/ training/tests/ -v

# Expected: 75/75 tests passing (~17s runtime)
```

See `docs/FINAL_IMPLEMENTATION_REPORT.md` for complete documentation.

### Starting Training

**Quick Start:**
```bash
# Test run (100 games, ~5 minutes)
python train.py --num_games 100 --log_frequency 10

# Short training (1,000 games, ~30 minutes)
python train.py --num_games 1000

# Full training (10,000 games, ~5 hours)
python train.py --num_games 10000 \
    --checkpoint_frequency 1000 \
    --checkpoint_dir models/checkpoints \
    --log_dir logs \
    --recording_dir recordings
```

**What Happens During Training:**

1. Each game randomly selects 4-6 agents from the 10
2. Agents play using hybrid policies (heuristic + learned)
3. Custom rewards calculated per agent
4. 1% of games recorded for visualization
5. Models updated every 10 games using PPO
6. Metrics logged every 100 games
7. Checkpoints saved every 1000 games

**Monitor Progress:**
```bash
# View latest metrics
cat logs/metrics_010000.json | python -m json.tool

# Check win rates and alpha values
grep "win_rate" logs/metrics_*.json
```

**Detailed Guide:** See `docs/TRAINING_GUIDE.md` for:
- Complete architecture explanation
- Reward function details
- Alpha annealing schedules
- Monitoring metrics
- Troubleshooting tips

## Development Roadmap

### Phase 1: Rules Engine ✅ (Completed)

- Complete engine implementation
- Full unit test coverage
- Deterministic integration tests

### Phase 2: 10-Agent RL System ✅ (Complete)

- ✅ 10 distinct agent personalities (Alice → Jack)
- ✅ Custom reward functions (6 components per agent)
  - cash, rent_yield, property_count, development, trade_value, monopoly_completion
- ✅ Behavioral heuristics (per-agent biases)
- ✅ Hybrid policy architecture (alpha × heuristic + (1-alpha) × learned)
- ✅ Structured transformer model (128-dim, 4 heads, 3 layers)
- ✅ PPO training infrastructure (replay buffer, trainer, evaluator)
- ✅ Multi-agent training coordinator (game loop, updates, checkpointing)
- ✅ Game recording system (1% sample for visualization)
- ✅ Main entry point with CLI (`train.py`)
- ✅ Comprehensive unit tests (75/75 passing)
- ✅ Complete documentation (TRAINING_GUIDE.md)

**Ready to train!** Run `python train.py --num_games 10000` to begin.

### Phase 3: Full Training & Analysis (Next)

- Run training (10,000+ games)
- Analyze win rates and strategy evolution
- Visualize recorded games
- Compare agent strategies
- Performance benchmarking

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
