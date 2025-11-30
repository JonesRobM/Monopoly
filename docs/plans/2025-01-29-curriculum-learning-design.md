# Curriculum Learning + Credit Assignment Design

**Date:** 2025-01-29
**Status:** Approved
**Goal:** Fix static learning behavior in multi-agent Monopoly RL system

## Problem Statement

Agents show no learning improvement over training:
- Win rates and rewards plateau immediately (< 500 games)
- Agents are very predictable/deterministic
- No exploration or strategic evolution observed

**Root Causes:**
1. **Credit assignment crisis:** 500-2000 step games with gamma=0.95 (20-step horizon)
2. **Data starvation:** Only 4-6 episodes per agent per update, buffers cleared
3. **Insufficient exploration:** High alpha values (60-80% heuristic), low entropy (0.01)
4. **Weak learning signal:** RL contribution too small to matter

## Design Philosophy

**Heuristics = Personality/Strategy (Primary)**
- Heuristics define each agent's character and strategic approach
- Maintain 60-80% heuristic influence
- Preserve agent differentiation

**RL = Tactical Optimization (Secondary)**
- RL learns tactical improvements within heuristic framework
- Focus on timing, bidding, cash management decisions
- 20-40% contribution but makes meaningful improvements

## Solution: Curriculum Learning + Credit Assignment Fix

### Section 1: Curriculum Phase Structure

**Three-Phase Progression:**

**Phase 1 - "Fast Games" (0-1000 games):**
- Maximum 15 rounds per game (~150-300 steps)
- Agents learn basic property acquisition and simple monopoly completion
- Faster feedback loops make credit assignment tractable
- Games finish in bankruptcy or round limit

**Phase 2 - "Medium Games" (1000-3000 games):**
- Maximum 25 rounds per game (~250-500 steps)
- Agents learn building strategies and property development
- More complex economic dynamics emerge
- Begins to resemble real Monopoly pacing

**Phase 3 - "Full Games" (3000+ games):**
- Maximum 50 rounds per game (current setting)
- Full Monopoly experience with long-term strategy
- Agents apply skills learned in earlier phases
- Ongoing training for refinement

**Automatic Phase Transitions:**
The trainer automatically advances phases based on game count. No manual intervention needed.

### Section 2: Credit Assignment Improvements

**Gamma Adjustment:**
Increase discount factor from 0.95 to 0.98. This extends the effective horizon from ~20 steps to ~50 steps.

**Enhanced Dense Rewards:**
Add intermediate reward signals to guide learning:
1. **Position value rewards:** Small positive reward for landing on/owning valuable positions
2. **Monopoly progress rewards:** Incremental rewards for getting closer to monopolies (+5 for 2nd property in color group)
3. **Cash buffer rewards:** Small positive reward for maintaining healthy cash reserves (+0.1 per turn when cash > $500)
4. **Strategic positioning:** Reward for blocking opponent monopolies

Dense rewards scaled small (0.1-1.0 range) to complement sparse rewards (10-1000 range).

**Buffer Accumulation Strategy:**
- Increase buffer size: 10K → 50K transitions per agent
- **Don't clear buffers after updates** - keep accumulating
- Only remove oldest transitions when buffer is full (rolling window)
- Each agent accumulates ~40-60 games worth of experience

**GAE Parameters:**
Keep GAE lambda at 0.95. Higher gamma + GAE improves long-term value estimation.

### Section 3: Exploration Enhancements

**Philosophy:**
Heuristics remain the **primary strategy driver** (60-80% influence). RL learns **tactical optimizations**.

**Alpha Schedules - Heuristic-Primary:**
```
alice:   0.8 → 0.6  (very conservative, mostly heuristic)
bob:     0.7 → 0.5  (high-value focus maintained)
charlie: 0.7 → 0.5  (infrastructure collector stays consistent)
dee:     0.6 → 0.4  (balanced)
ethel:   0.6 → 0.4  (balanced)
frankie: 0.7 → 0.5  (aggressive builder maintained)
greta:   0.6 → 0.4  (balanced)
harry:   0.7 → 0.5  (opportunistic nature preserved)
irene:   0.6 → 0.4  (balanced)
jack:    0.5 → 0.3  (most RL influence, but still heuristic-guided)
```

**Entropy Coefficient:**
Increase from 0.01 → 0.05. This drives exploration in the **tactical space** while following heuristic strategy.

**Targeted RL Learning:**
The 20-40% RL contribution focuses on:
- Optimal timing for property purchases
- Smart auction bidding
- When to mortgage vs. hold cash
- Building timing and sequencing

### Section 4: Training Loop Modifications

**Update Frequency:**
Change from every 10 games to every **20 games**.
- Each agent plays ~8-12 games between updates (more data)
- More stable gradients from diverse experiences

**Buffer Management:**
```
OLD: Collect 10 games → Update → CLEAR buffer → Repeat
NEW: Collect experiences continuously → Update every 20 games → KEEP buffer
```

**Buffer Details:**
- Size: 50K transitions per agent
- Rolling window: Remove oldest when full
- Buffer fills after ~100 games, maintains rolling window thereafter

**Batch Size Optimization:**
- Increase minibatch size: 64 → 128
- Keep 4 PPO epochs
- ~30-40 minibatches per update with full buffer

**Curriculum Phase Evaluation:**
Every 100 games, log:
- Average game length (should increase across phases)
- Win rate distribution (should stay diverse)
- Average reward per phase (should improve within each phase)
- Action diversity scores

### Section 5: Implementation Details

**File Changes:**

**1. `training/multi_agent_trainer.py`:**
- Add `get_max_rounds_for_phase()` method
- Modify `run_game()` to use dynamic max_rounds
- Remove `replay_buffer.clear()` in `update_models()`
- Update frequency: 10 → 20 games
- Line 164: `entropy_coef=0.01` → `entropy_coef=0.05`

**2. `training/replay_buffer.py`:**
- Line 29: `max_size`: 10000 → 50000
- Line 141: `gamma=0.95` → `gamma=0.98`

**3. `training/ppo_trainer.py`:**
- Line 36: `minibatch_size`: 64 → 128

**4. `agents/alpha_schedules.py`:**
- Update `ALPHA_CONFIGS` with revised values

**5. `agents/reward_shaper.py`:**
- Add dense reward methods:
  - `_calculate_position_value_reward()`
  - `_calculate_monopoly_progress_reward()`
  - `_calculate_cash_buffer_reward()`
- Integrate into `calculate_reward()` with small weights

**Curriculum Implementation Example:**
```python
def get_max_rounds_for_phase(self, game_iteration: int) -> int:
    """Get max rounds based on curriculum phase."""
    if game_iteration < 1000:
        return 15  # Phase 1
    elif game_iteration < 3000:
        return 25  # Phase 2
    else:
        return 50  # Phase 3
```

## Expected Outcomes

1. **Phase 1 (0-1000 games):** Agents establish basic learning, rewards begin increasing
2. **Phase 2 (1000-3000 games):** Strategic diversity emerges, win rates stabilize but differentiate
3. **Phase 3 (3000+ games):** Refined tactical play, continued gradual improvement

## Success Metrics

- Rewards increase within each phase
- Win rates differentiate by agent personality
- Action diversity scores show tactical variation
- Agents make observably better tactical decisions (auction bids, building timing)

## Risks & Mitigations

**Risk:** Short games in Phase 1 might teach bad habits
**Mitigation:** Dense rewards emphasize long-term value even in short games

**Risk:** 50K buffers might cause memory issues
**Mitigation:** Monitor memory usage, can reduce to 30K if needed

**Risk:** Higher gamma might cause instability
**Mitigation:** GAE helps stabilize, can roll back to 0.96 if issues arise
