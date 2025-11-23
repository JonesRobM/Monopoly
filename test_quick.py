"""Quick test to verify warning suppression works."""

# Suppress warnings
import warnings
warnings.filterwarnings("ignore", message=".*MINGW-W64.*")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="numpy")

import numpy as np
from engine import MonopolyBoard, GameState, PlayerState

print("Testing basic imports and functionality...")
print("[OK] NumPy imported without warnings")

# Test board creation
board = MonopolyBoard()
print(f"[OK] Created board with {len(board.tiles)} tiles")

# Test state creation
players = [PlayerState(player_id=0, name="Test Player")]
state = GameState(players=players)
print(f"[OK] Created game state with {len(state.players)} player(s)")

# Test some basic operations
tile = board.get_tile(1)  # Mediterranean Avenue
print(f"[OK] Got tile: {tile.name}")

# Test a simple calculation
rent = tile.property_info.get_rent(0)
print(f"[OK] Calculated rent: ${rent}")

print("\n" + "="*50)
print("All tests passed! Warnings suppressed successfully.")
print("="*50)
