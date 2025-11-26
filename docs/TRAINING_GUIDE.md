# Training Guide: 10-Agent Monopoly RL System

## Overview

This guide explains how to train the 10-agent Monopoly RL system. The system trains 10 distinct agent personalities (Alice through Jack) using a hybrid approach combining behavioral heuristics with learned policies.

---

## System Architecture

### Core Components

1. **10 Agent Personalities** - Each with unique behavioral archetypes
2. **Custom Reward Functions** - Per-agent priority weights for 6 reward components
3. **Hybrid Policies** - Blend heuristic biases with learned behavior (alpha annealing)
4. **Structured Transformer** - 128-dim model with 4 heads, 3 layers
5. **PPO Training** - Proximal Policy Optimization with separate replay buffers
6. **Game Recording** - 1% of games saved for strategy visualization

### Agent Personalities

| Agent | Strategy | Alpha Schedule | Key Traits |
|-------|----------|----------------|------------|
| **Alice** | Conservative money maximiser | 0.8 → 0.5 | High ROI threshold, cash buffer |
| **Bob** | High-value acquirer | 0.7 → 0.3 | Prefers expensive properties |
| **Charlie** | Infrastructure collector | 0.6 → 0.3 | Railroads & utilities focus |
| **Dee** | Trade specialist | 0.5 → 0.2 | Arbitrage and negotiation |
| **Ethel** | Property hoarder | 0.7 → 0.2 | Aggressive buying |
| **Frankie** | Development maximiser | 0.6 → 0.1 | Heavy building |
| **Greta** | Monopoly completer | 0.6 → 0.2 | Color set focus |
| **Harry** | Resource denial | 0.7 → 0.3 | Blocking strategies |
| **Irene** | Balanced investor | 0.5 → 0.2 | Moderate approach |
| **Jack** | Hyper-aggressive | 0.7 → 0.05 | Maximum risk-taking |

**Alpha Annealing**: Agents start rule-based (high alpha) and gradually become more learned (low alpha). Alice stays conservative (0.5), while Jack becomes highly chaotic (0.05).

---

## Reward Functions

Each agent has unique priority weights for 6 reward components:

### 1. Cash Reward (`w_cash`)
- Measures: Δcash between states
- Tracks immediate financial gains/losses

### 2. Rent Yield (`w_rent`)
- Measures: Actual rent collected during turn
- Incentivizes income generation

### 3. Property Count (`w_property`)
- Measures: Δproperties owned
- Penalties: -0.5 when mortgaging, +0.5 when unmortgaging
- Encourages property acquisition

### 4. Development (`w_development`)
- Measures: Δhouses/hotels
- +1 for building, -1 for selling
- Promotes infrastructure investment

### 5. Trade Value (`w_trade`)
- Measures: Economic value difference + strategic bonuses
- Captures gains from trades

### 6. Monopoly Completion (`w_monopoly`)
- **+1000**: Agent completes a monopoly (game-changing)
- **+300**: Agent blocks opponent's monopoly
- **-500**: Opponent completes a monopoly
- Emphasizes strategic play

**Example (Alice - Conservative):**
```json
{
  "cash": 1.0,
  "rent_yield": 0.8,
  "property_count": 0.5,
  "development": 0.3,
  "trade_value": 0.4,
  "monopoly_completion": 0.7
}
```

---

## Hybrid Policy System

### Policy Combination Formula
```
action_probs = alpha(t) × heuristic_probs + (1-alpha(t)) × learned_probs
```

**Where:**
- `alpha(t)`: Annealing coefficient (decreases over training)
- `heuristic_probs`: Behavioral biases (multiplicative on action mask)
- `learned_probs`: Neural network policy output

### Example Heuristic (Alice)
```python
# Conservative buying
if cash < $1000 or ROI < 10%:
    probs[DECLINE] *= 5.0  # Strong bias toward declining

# Suppress building unless safe
if cash < $800:
    probs[BUILD_HOUSE] *= 0.1  # Strong suppression
```

### Alpha Schedules

**Linear decay:**
```python
alpha(t) = start_alpha - (start_alpha - end_alpha) * (t / total_games)
```

**Exponential decay:**
```python
alpha(t) = end_alpha + (start_alpha - end_alpha) * exp(-decay_rate * t)
```

---

## Training Protocol

### Setup (Once Complete)

**1. Environment Setup:**
```bash
# Install dependencies
pip install -e .
pip install torch pytest

# Verify installation
pytest agents/tests/ models/tests/ training/tests/ -v
# Expected: 75/75 tests passing
```

**2. Configuration:**
- Agent configs: `config/player_behaviours.json`
- Reward weights defined per agent
- Alpha schedules defined in `agents/alpha_schedules.py`

### Training Execution (Planned)

**Command (once train.py implemented):**
```bash
python train.py \
    --num_games 10000 \
    --update_frequency 10 \
    --log_frequency 100 \
    --checkpoint_frequency 1000 \
    --checkpoint_dir models/checkpoints \
    --log_dir logs \
    --recording_dir recordings \
    --seed 42
```

**Parameters:**
- `num_games`: Total training games (10,000 recommended for initial run)
- `update_frequency`: PPO update every N games (default: 10)
- `log_frequency`: Log metrics every N games (default: 100)
- `checkpoint_frequency`: Save models every N games (default: 1000)
- `seed`: Random seed for reproducibility

### Training Loop (Overview)

**Per Game:**
1. Select 4-6 random agents from the 10
2. Initialize PettingZoo environment
3. Each agent selects actions using hybrid policy
4. Record experiences to per-agent replay buffers
5. Calculate custom rewards using per-agent reward shapers
6. If recording this game (1% chance), save full trajectory

**Every 10 Games:**
1. For each agent with sufficient experiences:
   - Sample batch from replay buffer
   - Compute GAE (Generalized Advantage Estimation)
   - Run 4 PPO epochs:
     - Compute policy loss (clipped surrogate)
     - Compute value loss
     - Add entropy bonus
     - Update model with gradient clipping
2. Update alpha values (annealing)
3. Clear replay buffers

**Every 100 Games:**
1. Log metrics:
   - Win rates per agent
   - Average rewards (all-time + last 100)
   - Alpha values
   - Training losses
2. Print summary to console

**Every 1000 Games:**
1. Save model checkpoints for all 10 agents
2. Save evaluation metrics
3. Save training history

---

## Monitoring Training

### Key Metrics

**Win Rates:**
- Expected: ~10% per agent if balanced (10 agents total)
- May diverge as strategies evolve
- Track over rolling 100-game windows

**Average Rewards:**
- Should generally increase over training
- Different baseline per agent (due to reward weights)
- Track both all-time and recent (last 100 games)

**Alpha Values:**
- Decrease according to schedules
- Alice: 0.8 → 0.5 (stays rule-based)
- Jack: 0.7 → 0.05 (becomes learned)

**Training Losses:**
- Policy loss: Should stabilize after initial learning
- Value loss: Should decrease over training
- Entropy: Gradually decreases (exploration → exploitation)

### Expected Training Behavior

**Games 0-999 (Early):**
- Strong heuristic influence (high alpha)
- Agents play according to archetypes
- Win rates roughly balanced
- Low variance in strategies

**Games 1000-4999 (Middle):**
- Gradual learning phase
- Alpha annealing in progress
- Strategy refinement
- Increasing diversity

**Games 5000+ (Late):**
- Mostly learned policies (low alpha)
- Emergent strategies
- Alice remains conservative (alpha=0.5)
- Jack becomes chaotic (alpha=0.05)

---

## Saved Outputs

### Directory Structure (After Training)

```
monopoly-ai/
├── models/
│   └── checkpoints/
│       ├── alice_001000.pt
│       ├── bob_001000.pt
│       ├── ...
│       └── jack_010000.pt
│
├── logs/
│   ├── metrics_000100.json
│   ├── metrics_000200.json
│   ├── ...
│   └── training_history.json
│
└── recordings/
    ├── game_000050_0001.json  # 1% sample
    ├── game_000123_0002.json
    └── ...
```

### Checkpoint Files (.pt)

Each checkpoint contains:
- Model state dict (transformer weights)
- Optimizer state
- Game iteration number
- Alpha value at checkpoint
- Win rate at checkpoint

### Metrics Files (.json)

Each metrics file contains:
```json
{
  "game_iteration": 100,
  "win_rates": {
    "alice": 0.10,
    "bob": 0.12,
    ...
  },
  "average_rewards": {
    "alice": 45.2,
    "bob": 38.7,
    ...
  },
  "alpha_values": {
    "alice": 0.78,
    "bob": 0.67,
    ...
  },
  "training_losses": {
    "alice": {"policy": 0.25, "value": 12.3, "entropy": 1.8},
    ...
  }
}
```

### Recorded Games (.json)

Each recorded game (1% sample) contains:
```json
{
  "game_id": 1,
  "game_iteration": 100,
  "participants": ["alice", "bob", "charlie", "dee"],
  "winner_id": "alice",
  "final_rewards": {...},
  "alpha_values": {...},
  "game_length": 156,
  "steps": [
    {
      "step_number": 0,
      "player_id": 0,
      "action": 5,
      "action_name": "BUY_PROPERTY",
      "reward": 10.0,
      "player_cash": {...},
      "player_positions": {...},
      "property_owners": {...},
      "houses": {...}
    },
    ...
  ]
}
```

Use these recordings to:
- Visualize strategy development over training
- Analyze decision-making patterns
- Compare early vs late game behavior
- Debug unexpected strategies

---

## Troubleshooting

### Common Issues

**1. Tests Failing**
```bash
# Re-run tests with verbose output
pytest agents/tests/ models/tests/ training/tests/ -v

# Check specific component
pytest agents/tests/test_reward_shaper.py -v
```

**2. Memory Issues**
- Reduce batch size in PPO trainer (default: 64)
- Reduce replay buffer max size (default: 10,000)
- Train fewer agents simultaneously (select 4 instead of 6 per game)

**3. Slow Training**
- Enable GPU if available (model automatically uses CUDA)
- Reduce update frequency (update every 20 games instead of 10)
- Disable verbose logging

**4. Diverging Policies**
- Check reward weights in `player_behaviours.json`
- Verify alpha schedules aren't too aggressive
- Reduce PPO learning rate (default: 3e-4)
- Increase entropy coefficient for more exploration

**5. No Strategy Diversity**
- Ensure reward weights differ significantly between agents
- Check heuristic biases are implemented correctly
- Verify alpha annealing is working (print alpha values)

---

## Next Steps

### Completing the System

**Remaining Implementation (5-8 hours):**

1. **`training/multi_agent_trainer.py`** (3-4 hours)
   - Main training loop coordinator
   - Random agent selection (4-6 per game)
   - Game execution via PettingZoo environment
   - Experience collection from all agents
   - Model updates every 10 games
   - Alpha annealing coordination
   - Integration with GameRecorder

2. **`train.py`** (1-2 hours)
   - CLI argument parsing
   - Load all 10 agents from config
   - Initialize models, replay buffers, PPO trainers
   - Run training loop
   - Checkpoint management

3. **Integration Testing** (1-2 hours)
   - End-to-end test (100 game simulation)
   - Verify tokenizer → transformer → actions
   - Validate reward calculations
   - Test model updates
   - Verify recording system

### Running Full Training

Once complete:
```bash
# Quick test (100 games)
python train.py --num_games 100 --log_frequency 10

# Short training (1,000 games, ~30 min)
python train.py --num_games 1000

# Full training (10,000 games, ~5 hours)
python train.py --num_games 10000

# Extended training (50,000 games, ~24 hours)
python train.py --num_games 50000
```

### Analyzing Results

**1. View Training Progress:**
```bash
# Check latest metrics
cat logs/metrics_010000.json | python -m json.tool

# Plot win rates over time (future)
python analysis/plot_win_rates.py --log_dir logs
```

**2. Compare Strategies:**
```bash
# Load recorded games
python analysis/compare_strategies.py \
    --recordings recordings/ \
    --agent alice \
    --iterations 0-1000,9000-10000
```

**3. Visualize Games:**
```bash
# Replay recorded game with visualization
python examples/replay_recorded_game.py \
    --game recordings/game_009500_0042.json \
    --render
```

---

## References

- **Implementation Report**: `docs/FINAL_IMPLEMENTATION_REPORT.md`
- **Testing Summary**: `docs/TESTING_SUMMARY.md`
- **Agent Behaviors**: `config/player_behaviours.json`
- **PettingZoo Docs**: https://pettingzoo.farama.org/

---

**Last Updated:** 2025-11-26
**Status:** System 80% complete, training infrastructure ready
**Tests:** 75/75 passing
