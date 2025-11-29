#!/usr/bin/env python
"""
Quick test to verify round-based game termination works correctly.
"""

from env import MonopolyEnv

def test_rounds():
    """Test that games end after max_rounds."""
    print("Testing round-based game termination...")
    print("="*60)

    # Create environment with 4 players, max 3 rounds
    max_rounds = 3
    num_players = 4

    env = MonopolyEnv(
        num_players=num_players,
        seed=42,
        max_rounds=max_rounds,
        render_mode=None
    )

    env.reset()

    print(f"\nConfiguration:")
    print(f"  Players: {num_players}")
    print(f"  Max rounds: {max_rounds}")
    print(f"  Expected turns at termination: {max_rounds * num_players} = {max_rounds} rounds × {num_players} players")
    print(f"\nRunning game...\n")

    step_count = 0
    last_round = -1

    # Run game loop
    for agent_name in env.agent_iter():
        obs, reward, termination, truncation, info = env.last()

        # Track round progression
        if env.state and env.state.round_number != last_round:
            last_round = env.state.round_number
            print(f"Round {last_round} started (Turn {env.state.turn_number})")

        if termination or truncation:
            action = None
        else:
            # Take random legal action
            action_mask = obs['action_mask']
            legal_actions = [i for i, legal in enumerate(action_mask) if legal]
            if legal_actions:
                action = legal_actions[0]  # Just take first legal action
            else:
                action = 0

        env.step(action)
        step_count += 1

        # Check if game ended
        if all(env.terminations.values()):
            break

    # Verify results
    final_state = env.state
    print(f"\n{'='*60}")
    print(f"Game completed!")
    print(f"  Final round: {final_state.round_number}")
    print(f"  Final turn: {final_state.turn_number}")
    print(f"  Total steps: {step_count}")
    print(f"  Truncated: {any(env.truncations.values())}")
    print(f"  Game over: {final_state.game_over}")

    # Verify truncation occurred at correct round
    if final_state.round_number >= max_rounds:
        print(f"\n[SUCCESS] Game ended at round {final_state.round_number} (max was {max_rounds})")
    else:
        print(f"\n[FAILURE] Game ended at round {final_state.round_number}, expected {max_rounds}")

    print("="*60)

if __name__ == "__main__":
    test_rounds()
