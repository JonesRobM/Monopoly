# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Curriculum learning system with 3-phase training (15/25/50 rounds)
- Enhanced credit assignment (gamma 0.98, 50K buffer size)
- Dense reward shaping (position value, cash buffer bonuses)
- END_TURN incentives to improve turn efficiency
- Action counter fix (only counts active player's actions)
- Comprehensive PyPI packaging configuration

### Changed
- Increased action limit from 10 to 20 per turn
- Update frequency increased from 10 to 20 games
- Entropy coefficient increased from 0.01 to 0.05
- Minibatch size increased from 64 to 128
- Heuristic-primary alpha schedules (0.5-0.8 -> 0.3-0.6)
- Action penalty increased from 0.05 to 0.3
- Added +0.5 bonus for END_TURN action

### Fixed
- Action masking to prevent NOOP during active gameplay
- Unicode encoding errors in console output
- Phase-based action restrictions enforcement
- Buffer retention across training updates

## [0.1.0] - 2025-01-30

### Added
- Complete Monopoly game engine with PettingZoo AEC API
- PPO-based multi-agent training system
- 10 configurable heuristic agents with diverse strategies
- Action masking for legal move enforcement
- Game recording and replay system
- Evaluation metrics and Elo tracking
- Alpha scheduling for heuristic-RL policy mixing
- Template-based trading system
- Comprehensive test suite

[Unreleased]: https://github.com/JonesRobM/monopoly-ai/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/JonesRobM/monopoly-ai/releases/tag/v0.1.0
