# Tokenization Fix - 2025-11-26

## Problem

The `MonopolyTransformer` model expects three separate tokenized tensors as input:
- `property_tokens`: (batch, 40, property_features)
- `player_tokens`: (batch, num_players, player_features)
- `game_token`: (batch, 1, game_features)

But the code was passing raw observation dicts directly to the model, causing:
```
TypeError: MonopolyTransformer.get_action_logits() missing 2 required positional arguments: 'player_tokens' and 'game_token'
```

## Solution

### 1. Updated `agents/base_agent.py`

**Added import:**
```python
import torch
```

**Modified `get_action()` method (lines 163-183):**
- Checks if both `self.model` and `self.tokenizer` are available
- Tokenizes the game state using `self.tokenizer.tokenize(state, player_id)`
- Converts numpy arrays to PyTorch tensors with batch dimension
- Calls model with properly structured inputs
- Converts model output back to numpy for further processing

```python
if self.model is not None and self.tokenizer is not None:
    # Tokenize state
    property_tokens, player_tokens, game_token = self.tokenizer.tokenize(state, player_id)

    # Convert to tensors and add batch dimension
    property_tokens = torch.FloatTensor(property_tokens).unsqueeze(0)
    player_tokens = torch.FloatTensor(player_tokens).unsqueeze(0)
    game_token = torch.FloatTensor(game_token).unsqueeze(0)

    # Get logits from model
    with torch.no_grad():
        learned_logits = self.model.get_action_logits(property_tokens, player_tokens, game_token)
        learned_logits = learned_logits.squeeze(0).cpu().numpy()

    # Apply action mask
    masked_logits = learned_logits + (action_mask - 1) * 1e10
    learned_probs = self._softmax(masked_logits)
else:
    # If no model yet, use uniform over legal actions
    learned_probs = action_mask / action_mask.sum()
```

### 2. Updated `training/multi_agent_trainer.py`

**Agent Initialization (line 153):**
- Attached tokenizer to each agent after creating model and replay buffer

```python
# Attach model, tokenizer, and replay buffer to agent
agent.model = model
agent.tokenizer = self.tokenizer  # ADDED THIS LINE
agent.replay_buffer = replay_buffer
```

**Game Execution - Value & Log Prob Calculation (lines 263-286):**
- Tokenizes state before getting value estimates and action log probabilities
- Added fallback values if tokenizer is not available

```python
# Get value estimate and log prob using tokenizer
if agent.tokenizer is not None:
    # Tokenize state
    property_tokens, player_tokens, game_token = agent.tokenizer.tokenize(current_state, player_id)

    # Convert to tensors and add batch dimension
    property_tokens = torch.FloatTensor(property_tokens).unsqueeze(0)
    player_tokens = torch.FloatTensor(player_tokens).unsqueeze(0)
    game_token = torch.FloatTensor(game_token).unsqueeze(0)

    # Get value estimate
    with torch.no_grad():
        _, value = agent.model.get_action_and_value(property_tokens, player_tokens, game_token)
        value = value.item()

    # Get log prob (recompute for storage)
    with torch.no_grad():
        action_logits, _ = agent.model.get_action_and_value(property_tokens, player_tokens, game_token)
        action_probs = torch.softmax(action_logits, dim=-1)
        log_prob = torch.log(action_probs[0, action] + 1e-10).item()
else:
    # Fallback if no tokenizer
    value = 0.0
    log_prob = -1.0
```

## Testing

Once PyTorch with CUDA support is installed, run:

```bash
python train.py --num_games 10 --log_frequency 5
```

This should now execute without tokenization errors.

## Related Issue

Also installing PyTorch with CUDA 12.4 support for GPU acceleration:

```bash
.venv/Scripts/python.exe -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

This will enable training on NVIDIA GPU instead of CPU-only mode.
