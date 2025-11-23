# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `NOTICE` file for Apache License 2.0 compliance
- `LICENSE_INFO.md` comprehensive license documentation
- `.license-header.txt` template for source file headers
- License section in README.md

### Changed
- Clarified project uses Apache License 2.0 (was already in LICENSE file)
- Updated all configuration files to reference Apache License 2.0
  - `pyproject.toml`: Updated license classifier
  - `setup.py`: Updated license classifier
  - `CONTRIBUTING.md`: Updated license agreement text
  - `MANIFEST.in`: Added NOTICE file

### Planned
- Phase 2: Baseline heuristic agents
- Phase 3: RL training infrastructure
- Phase 4: Population-based training and diversity metrics

## [0.1.0] - 2025-11-23

### Added - Phase 1: Rules Engine (COMPLETE)

#### Core Engine (`engine/`)
- Complete game state representation with dataclasses
  - `GameState`, `PlayerState`, `PropertyState`
  - `AuctionState`, `TradeOffer`, `GameConfig`
- Full Monopoly board implementation (40 tiles)
  - All properties with accurate rent tables
  - 4 Railroads with dynamic rent calculation
  - 2 Utilities with dice-based rent
  - Special tiles (GO, Jail, Free Parking, taxes, etc.)
- Chance and Community Chest card system
  - 16 Chance cards with all effects
  - 16 Community Chest cards with all effects
  - Deterministic shuffling with seeded RNG
- Discrete action space encoding (562 actions)
  - Property purchase decisions
  - Auction bidding (10 levels)
  - Building/selling houses and hotels
  - Mortgaging and unmortgaging
  - Trade offers (50 templates)
  - Jail actions and turn management
- Pure state transition functions
  - Player movement with GO salary
  - Property acquisition and transfer
  - House/hotel development
  - Mortgaging system
  - Jail mechanics
  - Bankruptcy handling
  - Turn rotation with skip logic
- Comprehensive rules engine
  - Rent calculation (all property types, monopolies)
  - Building rules (monopoly required, even building)
  - Mortgage validation
  - Asset and wealth calculation
  - Legal action generation

#### RL Environment (`env/`)
- PettingZoo AEC-compatible environment
  - 2-6 player support
  - Deterministic seeded gameplay
  - Standard `reset()`, `step()`, `observe()` API
- State encoding for neural networks
  - ~450-dimensional observation space
  - One-hot position encoding
  - Normalized values
- Reward shaping (sparse and dense modes)
- Action masking for stable training
  - Context-aware legal action generation
  - Building rules enforcement
  - Resource availability checking

#### Testing
- 101 comprehensive tests (100% passing)
  - 17 state structure tests
  - 19 board tests
  - 28 rules validation tests
  - 24 transition function tests
  - 13 integration tests
- Full deterministic game reproduction
- Test suite runtime: 0.26s

#### Documentation
- Complete README with examples
- Comprehensive CLAUDE.md design document
- Implementation summary
- Example usage script
- Contributing guidelines
- Development configuration files

#### Infrastructure
- Modern `pyproject.toml` configuration
- Black, Ruff, MyPy configuration
- GitHub Actions CI/CD workflow
- Makefile for common tasks
- EditorConfig for IDE consistency
- Type checking support (py.typed markers)

### Design Principles Implemented
- ✅ Deterministic core with seeded RNG
- ✅ Pure functions for all state transitions
- ✅ Separation of concerns (engine/env/agents/training)
- ✅ Comprehensive type hints throughout
- ✅ Action masking for RL stability
- ✅ Multi-agent first design
- ✅ Full test coverage

### Performance
- Test suite: 0.26s for 101 tests
- Pure functions: Zero side effects
- Type-safe: Full mypy compliance
- Memory efficient: Dataclass-based state

[Unreleased]: https://github.com/yourusername/monopoly-ai/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/monopoly-ai/releases/tag/v0.1.0
