"""Minimal test of environment step functionality."""

# Suppress warnings
import warnings
warnings.filterwarnings("ignore", message=".*MINGW-W64.*")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="numpy")

import numpy as np
from env import MonopolyEnv

print("Creating environment...")
env = MonopolyEnv(num_players=2, seed=42, render_mode=None)
env.reset()
print("[OK] Environment created and reset")

print("\nTrying to take 5 steps...")
step_count = 0

for agent in env.agent_iter():
    if step_count >= 5:
        break

    observation, reward, termination, truncation, info = env.last()

    if termination or truncation:
        print(f"[INFO] Agent {agent} terminated/truncated")
        action = None
    else:
        # Get legal action mask
        action_mask = observation["action_mask"]
        legal_actions = np.where(action_mask > 0.5)[0]

        if len(legal_actions) > 0:
            action = legal_actions[0]  # Just take first legal action
            print(f"[OK] Step {step_count}: Agent {agent} taking action {action}")
        else:
            action = 0
            print(f"[WARN] Step {step_count}: No legal actions for {agent}")

    env.step(action)
    step_count += 1

print(f"\n[OK] Successfully completed {step_count} steps")
print("="*50)
print("Environment test successful!")
print("="*50)
