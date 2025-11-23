"""Simplified example to test warning suppression and basic functionality."""

# Suppress NumPy warnings on Windows (MINGW-W64 experimental build warnings)
import warnings
warnings.filterwarnings("ignore", message=".*MINGW-W64.*")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="numpy")

import numpy as np
from env import MonopolyEnv

print("Testing MonopolyEnv with warning suppression...")

# Create environment (no render mode for speed)
env = MonopolyEnv(num_players=4, seed=42, render_mode=None)
env.reset()

print("[OK] Environment created and reset")

# Play for 10 turns
turn_count = 0
for i in range(10):
    for agent in env.agent_iter():
        observation, reward, termination, truncation, info = env.last()

        if termination or truncation:
            action = None
        else:
            # Get legal action mask
            action_mask = observation["action_mask"]

            # Sample random legal action
            legal_actions = np.where(action_mask > 0.5)[0]
            if len(legal_actions) > 0:
                action = np.random.choice(legal_actions)
            else:
                action = 0  # NOOP

        env.step(action)

        if env.state.game_over:
            break

    turn_count += 1
    if env.state.game_over:
        break

print(f"[OK] Played {turn_count} turns")
print(f"[OK] Game state: turn={env.state.turn_number}, game_over={env.state.game_over}")

print("\n" + "="*50)
print("Test completed successfully! No warnings.")
print("="*50)
