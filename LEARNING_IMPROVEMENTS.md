# Learning Improvements - Tier 1 Critical Fixes

**Date**: 2025-11-29
**Status**: ✅ Implemented
**Impact**: High - Should significantly improve agent learning

---

## 🎯 Problem Summary

Agents were showing **minimal learning progress** after 129 games:
- Win rates: 10-30% (essentially random for 5-player games)
- Reward variance: EXTREMELY high (std dev 176-518, range -1432 to +1904)
- No improvement over time (recent vs overall performance nearly identical)
- Reward signals disconnected from actual game success

---

## ✅ Implemented Fixes

### **1. Reward Clipping** ⚠️⚠️⚠️ (CRITICAL)

**File**: `agents/reward_shaper.py:60-112`

**Problem**: Rewards spanning from -1432 to +1904 are **catastrophic for PPO**:
- PPO expects rewards roughly in [-10, +10] range
- Huge rewards → massive policy updates → unstable learning
- Value function cannot accurately predict such wild swings

**Solution**: Clip ALL rewards to `[-10, +10]` range

```python
# Line 108-110
clipped_reward = float(max(-10.0, min(10.0, total_reward)))
return clipped_reward
```

**Expected Impact**:
- Stable policy updates
- Value function can actually learn
- Reduced gradient explosions

---

### **2. Dense Step Rewards** ⚠️⚠️ (HIGH PRIORITY)

**File**: `agents/reward_shaper.py:324-452`

**Problem**: Sparse rewards only come on rare events:
- Monopoly completion: +1000 (but only after 20+ turns)
- Property purchase: +1 (rare)
- Agents can't learn causal relationships (which actions led to rewards?)

**Solution**: Add continuous feedback EVERY step with 4 components:

1. **Cash Ratio Improvement** (±0.5): Relative cash position vs other players
2. **Portfolio Value Change** (±0.3): Property value considering monopoly potential
3. **Monopoly Progress** (±0.5): Partial credit for moving toward complete color sets
4. **Strategic Diversity** (±0.2): Owning properties across multiple groups

```python
# New functions added:
def _calculate_dense_step_reward(...)  # Line 324
def _calculate_portfolio_value(...)     # Line 378
def _calculate_monopoly_progress(...)   # Line 407
def _get_property_groups_owned(...)     # Line 435
```

**Example Dense Rewards**:
- Bought 2nd property in a 3-property color set → +0.33 progress reward
- Cash increased from 20% to 25% of total game cash → +0.1 cash improvement
- Built house on monopoly → +0.2 portfolio value increase

**Expected Impact**:
- Much better credit assignment (agents know WHICH actions help)
- Faster initial learning
- More strategic play emerges

---

### **3. Discount Factor Tuning** ⚠️ (MODERATE PRIORITY)

**File**: `training/replay_buffer.py:133-143`

**Problem**: γ=0.99 means effective horizon = 1/(1-0.99) = **100 steps**
- Monopoly games last ~50 rounds × 5-10 actions = 250-500 steps
- But most rewards should credit recent actions, not ancient ones

**Solution**: Reduced γ from 0.99 → **0.95**
- New effective horizon = 1/(1-0.95) = **20 steps**
- Better for games where consequences are more immediate

```python
# Line 141
gamma=0.95,  # Reduced from 0.99 for shorter-horizon games
```

**Expected Impact**:
- Better credit assignment for recent actions
- Reduced "credit diffusion" to irrelevant early actions

---

### **4. Diagnostic Logging** 📊 (MONITORING)

**Files**:
- `training/evaluator.py:178-234` (new method)
- `training/multi_agent_trainer.py:558-559, 580-581` (integration)

**Added**: Comprehensive reward statistics printed every 100 games

**New Metrics Logged**:
- Mean, Std Dev, Min, Max, Range per agent
- Reward clipping detection (% of rewards hitting boundaries)
- Warnings if >50% of rewards are clipped

**Example Output**:
```
================================================================================
Reward Diagnostics at Game 500 (last 100 games)
================================================================================
Agent        Mean       Std        Min        Max        Range
--------------------------------------------------------------------------------
alice          2.34       3.21     -8.45       9.87      18.32
bob           -1.23       4.56     -9.99       7.65      17.64
...
================================================================================
Reward Clipping: 127/500 (25.4%) at boundaries
================================================================================
```

**Expected Impact**:
- Early detection of learning issues
- Visibility into whether rewards are properly scaled
- Ability to tune hyperparameters based on data

---

## 📈 Expected Results

After these fixes + running **10,000 games**:

### **Short Term (1,000 games)**:
- ✅ Reward variance should decrease (std < 5.0)
- ✅ Win rates should start diverging (15-25% range, not all ~20%)
- ✅ Some agents should show clear learning curves

### **Medium Term (5,000 games)**:
- ✅ Clear performance hierarchy emerges
- ✅ Some agents reach >30% win rate
- ✅ Reward-to-win correlation improves
- ✅ Agents learn to END_TURN efficiently

### **Long Term (10,000+ games)**:
- ✅ Stable win rates (best agents >35%)
- ✅ Strategic play observable (buying to complete monopolies)
- ✅ Different agent personalities emerge

---

## 🧪 Testing

Run a test training session to verify fixes:

```bash
# Quick test (200 games to check for errors)
python train.py --num_games 200 --max_rounds 50 --log_frequency 50

# Full training run
python train.py --num_games 10000 --max_rounds 50 --update_frequency 10
```

**Watch for**:
1. Reward stats in diagnostics (should be in [-10, +10])
2. No errors from new reward calculation functions
3. Learning curves starting to diverge after 1000 games

---

## 🔧 Potential Adjustments

If learning is **still slow** after 1,000 games:

### **Adjust Dense Reward Weights**:
```python
# In _calculate_dense_step_reward(), line 354-374
cash_improvement * 3.0      # Increase from 2.0 to emphasize cash
portfolio_improvement * 0.2  # Increase from 0.1 for property value
progress_delta * 1.0         # Increase from 0.5 for monopoly progress
```

### **Adjust Clip Limits**:
If >70% of rewards hitting boundaries:
```python
# Line 110 - increase clip range
clipped_reward = float(max(-20.0, min(20.0, total_reward)))
```

### **Reduce Gamma Further**:
If learning very long-term strategies:
```python
# Line 141 - reduce to emphasize recent actions more
gamma=0.90,  # Instead of 0.95
```

---

## 📝 Summary of Changes

| File | Lines Changed | Description |
|------|---------------|-------------|
| `agents/reward_shaper.py` | 60-112 | Added reward clipping to [-10, +10] |
| `agents/reward_shaper.py` | 324-452 | Added dense step rewards (4 components) |
| `training/replay_buffer.py` | 141 | Reduced γ from 0.99 → 0.95 |
| `training/evaluator.py` | 178-234 | Added reward diagnostics method |
| `training/multi_agent_trainer.py` | 558-559, 580-581 | Integrated diagnostic logging |

**Total**: ~180 lines added/modified

---

## 🎓 Key Takeaways

**What We Learned**:
1. **Reward scale matters A LOT** for PPO - clip to reasonable ranges
2. **Dense rewards > Sparse rewards** for faster learning
3. **Discount factor should match game horizon** (not always 0.99!)
4. **Diagnostic logging is essential** to catch issues early

**Next Steps**:
1. ✅ Run 10,000 game training session
2. Monitor diagnostics every 100 games
3. If still not learning well after 1,000 games, consider:
   - Curriculum learning (start with shorter games)
   - Intrinsic motivation bonuses
   - Reducing action space complexity

---

**Generated**: 2025-11-29
**By**: Claude Code (Sonnet 4.5)
