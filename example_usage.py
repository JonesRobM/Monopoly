"""
Example usage of the Monopoly AI environment.

This script demonstrates:
1. Basic environment usage with random agents
2. Direct engine usage
3. Deterministic game reproduction
"""

import numpy as np
from env import MonopolyEnv
from engine import (
    MonopolyBoard, GameState, PlayerState, GameConfig,
    RulesEngine, move_player, purchase_property
)


def example_environment_usage():
    """Example: Using the PettingZoo environment with random agents."""
    print("\n" + "="*60)
    print("Example 1: PettingZoo Environment with Random Agents")
    print("="*60)

    # Create environment
    env = MonopolyEnv(num_players=4, seed=42, render_mode="human")
    env.reset()

    # Play for 20 turns
    for i in range(20):
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

        if env.state.game_over:
            break

    print(f"\nGame ended after {env.state.turn_number} turns")
    if env.state.winner is not None:
        print(f"Winner: Player {env.state.winner}")


def example_engine_usage():
    """Example: Using the game engine directly."""
    print("\n" + "="*60)
    print("Example 2: Direct Engine Usage")
    print("="*60)

    # Create board and rules
    board = MonopolyBoard()
    config = GameConfig(num_players=2, seed=42)
    rules = RulesEngine(board, config)

    # Initialize game
    players = [
        PlayerState(player_id=0, name="Alice"),
        PlayerState(player_id=1, name="Bob")
    ]
    state = GameState(players=players)

    print(f"\nInitial state:")
    print(f"  Alice: ${state.players[0].cash} at position {state.players[0].position}")
    print(f"  Bob: ${state.players[1].cash} at position {state.players[1].position}")

    # Alice moves to Mediterranean Avenue (position 1)
    print(f"\nAlice moves to position 1 (Mediterranean Avenue)...")
    state = move_player(state, player_id=0, new_position=1, go_salary=200)

    # Alice buys Mediterranean Avenue
    if rules.can_buy_property(state, 0, 1):
        price = board.get_purchase_price(1)
        print(f"Alice buys Mediterranean Avenue for ${price}")
        state = purchase_property(state, 0, 1, price)

    # Bob moves to position 1 and pays rent
    print(f"\nBob moves to position 1...")
    state = move_player(state, player_id=1, new_position=1, go_salary=200)

    rent = rules.calculate_rent(state, 1)
    print(f"Bob pays ${rent} rent to Alice")

    from engine.transitions import transfer_cash
    state = transfer_cash(state, 1, 0, rent)

    print(f"\nFinal state:")
    print(f"  Alice: ${state.players[0].cash}, owns {len(state.players[0].owned_properties)} properties")
    print(f"  Bob: ${state.players[1].cash}, owns {len(state.players[1].owned_properties)} properties")


def example_deterministic_reproduction():
    """Example: Demonstrating deterministic game reproduction."""
    print("\n" + "="*60)
    print("Example 3: Deterministic Game Reproduction")
    print("="*60)

    def play_game(seed):
        """Play a game with the given seed and return final positions."""
        env = MonopolyEnv(num_players=2, seed=seed, render_mode=None)
        env.reset()

        for _ in range(50):
            for agent in env.agent_iter():
                obs, reward, term, trunc, info = env.last()

                if term or trunc:
                    action = None
                else:
                    action_mask = obs["action_mask"]
                    legal = np.where(action_mask > 0.5)[0]
                    action = np.random.choice(legal) if len(legal) > 0 else 0

                env.step(action)

                if env.state.game_over:
                    break

            if env.state.game_over:
                break

        return tuple(p.position for p in env.state.players), tuple(p.cash for p in env.state.players)

    # Play same game twice with same seed
    seed = 12345
    np.random.seed(seed)
    result1 = play_game(seed)

    np.random.seed(seed)
    result2 = play_game(seed)

    print(f"\nGame 1 result: positions={result1[0]}, cash={result1[1]}")
    print(f"Game 2 result: positions={result2[0]}, cash={result2[1]}")
    print(f"\nResults match: {result1 == result2}")


if __name__ == "__main__":
    # Run examples
    example_environment_usage()
    example_engine_usage()
    example_deterministic_reproduction()

    print("\n" + "="*60)
    print("All examples completed successfully!")
    print("="*60)
