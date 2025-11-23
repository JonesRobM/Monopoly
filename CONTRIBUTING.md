# Contributing to Monopoly AI

Thank you for your interest in contributing to Monopoly AI! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.12 or higher
- Git
- Make (optional, but recommended)

### Getting Started

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/JonesRobM/monopoly-ai.git
   cd monopoly-ai
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Verify installation**
   ```bash
   pytest
   ```

## Development Workflow

### Making Changes

1. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following the project's coding standards
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests**
   ```bash
   make test
   # or
   pytest
   ```

4. **Format and lint your code**
   ```bash
   make format
   make lint
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```

6. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Coding Standards

### Python Style

- **Python Version**: 3.12+
- **Line Length**: 100 characters
- **Formatter**: Black
- **Linter**: Ruff (or Flake8)
- **Type Checker**: MyPy

### Code Quality

1. **Type Hints**: All functions must have type hints
   ```python
   def calculate_rent(state: GameState, property_id: int) -> int:
       ...
   ```

2. **Docstrings**: Use Google-style docstrings
   ```python
   def purchase_property(state: GameState, player_id: int, property_id: int, price: int) -> GameState:
       """
       Purchase a property for a player.

       Args:
           state: Current game state
           player_id: ID of purchasing player
           property_id: ID of property to purchase
           price: Purchase price

       Returns:
           Updated game state with property purchased
       """
       ...
   ```

3. **Pure Functions**: Prefer pure functions for game logic
   - No side effects
   - Same input → same output
   - Easy to test

4. **Immutability**: Use dataclasses with `frozen=True` or deepcopy for state updates
   ```python
   from dataclasses import dataclass
   from copy import deepcopy

   @dataclass(frozen=True)
   class PropertyInfo:
       tile_id: int
       name: str
       purchase_price: int
   ```

### Testing

1. **Test Coverage**: Aim for >90% coverage
2. **Test Types**:
   - Unit tests for individual functions
   - Integration tests for complete workflows
   - Mark tests appropriately:
     ```python
     @pytest.mark.unit
     def test_player_initialization():
         ...

     @pytest.mark.integration
     def test_complete_game():
         ...
     ```

3. **Test Structure**:
   ```python
   class TestFeatureName:
       """Tests for feature X."""

       def test_basic_case(self):
           """Test basic functionality."""
           ...

       def test_edge_case(self):
           """Test edge case handling."""
           ...
   ```

4. **Fixtures**: Use pytest fixtures for common setup
   ```python
   @pytest.fixture
   def game_state():
       """Create a basic game state for testing."""
       players = [PlayerState(player_id=0, name="Player 1")]
       return GameState(players=players)
   ```

## Project Architecture

### Directory Structure

```
monopoly-ai/
├── engine/          # Pure game logic (no RL knowledge)
│   ├── state.py
│   ├── board.py
│   ├── rules.py
│   ├── cards.py
│   ├── actions.py
│   ├── transitions.py
│   └── tests/
├── env/             # RL environment wrapper
│   ├── pettingzoo_api.py
│   ├── encoding.py
│   └── action_masking.py
├── agents/          # Agent implementations (future)
└── training/        # Training loops (future)
```

### Design Principles

1. **Deterministic Core**
   - All randomness uses seeded RNG
   - Fixed seed = reproducible game

2. **Separation of Concerns**
   - `engine/`: Game rules (no RL)
   - `env/`: RL interface (no game logic)
   - `agents/`: Policies
   - `training/`: Optimization

3. **Pure Functions**
   - State transitions are pure
   - Easy to test and reason about

4. **Type Safety**
   - Comprehensive type hints
   - Run `mypy` before committing

## Pull Request Guidelines

### Before Submitting

- [ ] Tests pass (`make test`)
- [ ] Code is formatted (`make format`)
- [ ] Linting passes (`make lint`)
- [ ] Type checking passes (`make type-check`)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if applicable)

### PR Description

Include:
- **What**: Brief description of changes
- **Why**: Motivation for changes
- **How**: Implementation approach
- **Testing**: How you tested the changes

Example:
```markdown
## What
Implement auction bidding mechanism

## Why
Required for Phase 2 baseline agents

## How
- Added `AuctionState` to track active auctions
- Implemented bidding validation in `rules.py`
- Added auction transition functions

## Testing
- Added 15 unit tests for auction logic
- Added integration test for complete auction flow
- All tests pass
```

## Common Tasks

### Running Tests

```bash
# All tests
make test

# With coverage
make test-cov

# Fast (parallel)
make test-fast

# Specific test file
pytest engine/tests/test_state.py

# Specific test
pytest engine/tests/test_state.py::TestPlayerState::test_player_initialization
```

### Formatting and Linting

```bash
# Format code
make format

# Check formatting
make format-check

# Run linters
make lint

# Type check
make type-check
```

### Example Usage

```bash
# Run example script
make example

# Start interactive shell
make shell
```

## Questions or Issues?

- **Bug Reports**: Open an issue with:
  - Description of the bug
  - Steps to reproduce
  - Expected vs actual behavior
  - Python version and OS

- **Feature Requests**: Open an issue describing:
  - The feature
  - Use case
  - Proposed implementation (optional)

- **Questions**: Open a discussion or issue

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
