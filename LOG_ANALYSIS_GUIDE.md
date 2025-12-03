# Training Log Analysis Guide

## Overview

The `analyze_training_logs.py` script parses console output from training runs to extract and visualize:
- Game progression (steps, rounds, turns per game)
- Curriculum phase transitions
- Warnings and error patterns
- Model update tracking
- Training speed and completion statistics

## Quick Start

### 1. Capture Training Logs

**During training**, redirect output to a log file:

```bash
# Single run with timestamp
python train.py 2>&1 | Tee-Object -FilePath "logs/training_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# Or simple redirect
python train.py > logs/training_log.txt 2>&1
```

### 2. Analyze Logs

**After training** (or during, for completed games):

```bash
# Analyze single log file
python analyze_training_logs.py logs/training_20250102_143022.log

# Analyze multiple logs
python analyze_training_logs.py logs/training_*.log

# Custom output directory
python analyze_training_logs.py logs/training_log.txt --output-dir results/
```

## Output Files

The analyzer generates:

### 📊 **CSV Export**: `{logname}_analysis.csv`
Contains per-game data:
- Game number, players, phase
- Steps, rounds, turns
- Warning and error counts
- Specific warning types

### 📈 **Progression Plot**: `{logname}_progression.png`
Three subplots showing:
1. Steps per game over training
2. Rounds per game (with phase max_rounds lines)
3. Turns per game

All with:
- Phase-colored scatter points
- 50-game rolling averages
- Phase transition markers (red vertical lines)

### ⚠️ **Warnings Plot**: `{logname}_warnings.png`
Two subplots showing:
1. Total warnings per game over time
2. Specific warning types (turn exceeded, max rounds reached)

## What Gets Extracted

### From Console Output:

```
[Game 810] Starting with 5 players: irene, jack, bob, charlie, harry
```
→ Game number, player count, participants

```
Step 2600, Round 5, Turn 20, 4/4 players active
```
→ Step/round/turn progression samples

```
[Game 812] Finished! Winner: alice, Rounds: 15, Turns: 245, Steps: 2800
```
→ Game completion stats

```
WARNING: Turn exceeded 50 actions, forcing END_TURN
```
→ Warning tracking

```
CURRICULUM PHASE TRANSITION: Phase 1 → Phase 2
Increasing max_rounds: 15 → 25
Increasing max_actions_per_turn: 10× players → 20× players
```
→ Phase transition detection

```
[Game 820] Updating models...
  Updating alice...
    Buffer size: 5000
  alice: policy_loss=0.1234, value_loss=0.5678, entropy=0.0234
```
→ Model update tracking with losses

## Example Usage

### Scenario 1: Monitor Long Training Run

```bash
# Start training with logging
python train.py --num_games 5000 2>&1 | Tee-Object -FilePath logs/training_5k_run.log

# In another terminal, analyze periodically
python analyze_training_logs.py logs/training_5k_run.log
```

### Scenario 2: Compare Multiple Runs

```bash
# Run 1
python train.py --num_games 1000 > logs/run1_baseline.log 2>&1

# Run 2 with different config
python train.py --num_games 1000 > logs/run2_modified.log 2>&1

# Compare both
python analyze_training_logs.py logs/run1_baseline.log logs/run2_modified.log
```

### Scenario 3: Resume Training Analysis

```bash
# Resume training from checkpoint 812
python train.py --resume 812 --num_games 10000 > logs/training_resume_812.log 2>&1

# Analyze the resumed run
python analyze_training_logs.py logs/training_resume_812.log --output-dir analysis_resume_812/
```

## Understanding the Output

### Summary Report

```
📄 Log File: training_20250102_143022.log
📊 Games: 812 → 1050 (238 games)

📈 Curriculum Phases:
   Phase 1: 188 games ( 79.0%) - 15 rds, 10× actions
   Phase 2:  50 games ( 21.0%) - 25 rds, 20× actions

🔄 Phase Transitions: 1
   Game 1000: Phase 1→2 (15→25 rds, 10× players→20× players)

📊 Game Statistics:
   Average steps/game: 2450.3
   Average rounds/game: 12.4
   Average turns/game: 185.6

⚠️  Issues Detected:
   Warnings: 45
   Errors: 0

   Most common warnings:
      • Turn exceeded max actions: 38 occurrences
      • Reached max_rounds: 7 occurrences
```

### Key Insights to Look For:

1. **Game Length Trends**
   - Are games getting shorter (better play)?
   - Sudden spikes (stuck agents)?
   - Phase transition effects?

2. **Warning Patterns**
   - "Turn exceeded" warnings decreasing = agents learning to end turns
   - "Reached max_rounds" = games too long for current phase
   - Spikes after phase transitions = expected adaptation period

3. **Phase Transitions**
   - Do metrics change smoothly or spike?
   - Are warnings clustered around transitions?

4. **Model Updates**
   - Consistent loss trends?
   - Buffer sizes growing appropriately?

## Integration with JSON Analysis

Combine with the JSON-based notebooks for complete picture:

```python
# 1. Parse training logs for game-level metrics
python analyze_training_logs.py logs/training_log.txt

# 2. Open Jupyter notebooks for detailed analysis
jupyter notebook analyze_curriculum_training.ipynb

# 3. Cross-reference findings
# - Log analysis: game length, warnings, phase transitions
# - JSON analysis: win rates, rewards, agent performance
```

## Tips

### Faster Analysis
```bash
# Skip plots if you just want the CSV
python analyze_training_logs.py logs/*.log --no-plots
```

### Monitoring Live Training
```bash
# Terminal 1: Training
python train.py 2>&1 | Tee-Object -FilePath logs/training_live.log

# Terminal 2: Watch log grow
tail -f logs/training_live.log  # Linux/Mac
Get-Content logs/training_live.log -Wait  # PowerShell

# Terminal 3: Periodic analysis
while True; do
    python analyze_training_logs.py logs/training_live.log --no-plots
    sleep 300  # Every 5 minutes
done
```

### Custom Analysis
Load the CSV into pandas for custom queries:

```python
import pandas as pd

df = pd.read_csv('analysis_output/training_log_analysis.csv')

# Games that hit max_rounds
max_rounds_games = df[df['max_rounds_reached'] > 0]

# Average steps by phase
avg_steps = df.groupby('phase')['steps'].mean()

# Warning rate by game number
df['warning_rate'] = df['warning_count'] / df['steps']
```

## Troubleshooting

**"Log file not found"**
- Check path is correct
- Ensure you redirected stdout during training

**"No games found in log"**
- Log might be from middle of a game
- Check log format matches expected patterns

**Missing data in plots**
- Some games might not have completed (interrupted training)
- CSV will show `None` for incomplete game stats

**Memory issues with large logs**
- Process in chunks (split log file by date)
- Use `--no-plots` and analyze CSV separately
