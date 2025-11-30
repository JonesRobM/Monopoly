#!/usr/bin/env python
"""
Play Monopoly against trained AI agents.

Allows a human player to compete against trained agents in an interactive game.
"""

import sys
import argparse
from pathlib import Path
import torch

from engine.board import MonopolyBoard
from engine.actions import ActionEncoder
from env.pettingzoo_api import MonopolyEnv
from agents.base_agent import create_all_agents
from models.transformer import MonopolyTransformer
from models.tokenizer import MonopolyTokenizer
from training.ppo_trainer import PPOTrainer


class HumanPlayer:
    """Human player interface."""

    def __init__(self, name: str = "Human"):
        self.name = name
        self.agent_id = "human"

    def get_action(self, env, observation, action_mask):
        """
        Get action from human player via console input.

        Args:
            env: Game environment
            observation: Current observation (not used for human)
            action_mask: Legal action mask

        Returns:
            Selected action index
        """
        state = env.state
        current_player_id = env.agent_to_player_id[env.agent_selection]
        player = state.players[current_player_id]

        # Display game state
        self._display_state(state, player, current_player_id)

        # Get legal actions
        legal_actions = []
        for action_idx in range(len(action_mask)):
            if action_mask[action_idx] == 1:
                action_name = env.action_encoder.decode_action_name(action_idx)
                legal_actions.append((action_idx, action_name))

        # Display legal actions
        print(f"\n{'='*80}")
        print(f"LEGAL ACTIONS ({len(legal_actions)} available):")
        print(f"{'='*80}")

        for i, (action_idx, action_name) in enumerate(legal_actions):
            print(f"  [{i}] {action_name}")

        # Get input
        while True:
            try:
                choice = input(f"\nSelect action [0-{len(legal_actions)-1}] (or 'q' to quit): ").strip()

                if choice.lower() == 'q':
                    print("Quitting game...")
                    sys.exit(0)

                choice_idx = int(choice)

                if 0 <= choice_idx < len(legal_actions):
                    action_idx, action_name = legal_actions[choice_idx]
                    print(f"\n→ You selected: {action_name}")
                    return action_idx
                else:
                    print(f"❌ Invalid choice. Please enter 0-{len(legal_actions)-1}")

            except ValueError:
                print("❌ Please enter a number")
            except KeyboardInterrupt:
                print("\nQuitting game...")
                sys.exit(0)

    def _display_state(self, state, player, player_id):
        """Display current game state."""
        print(f"\n{'='*80}")
        print(f"ROUND {state.round_number}, TURN {state.turn_number} - YOUR TURN")
        print(f"{'='*80}")

        # Your status
        print(f"\n🎮 YOUR STATUS:")
        print(f"  💰 Cash: ${player.cash}")
        print(f"  📍 Position: {self._get_tile_name(state, player.position)}")
        print(f"  🏠 Properties: {len(player.owned_properties)}")

        if player.owned_properties:
            print(f"\n  Your Properties:")
            for tile_id in sorted(player.owned_properties)[:10]:  # Show first 10
                prop_state = state.properties.get(tile_id)
                tile_name = self._get_tile_name(state, tile_id)

                if prop_state:
                    houses_str = ""
                    if prop_state.num_houses > 0:
                        if prop_state.num_houses == 5:
                            houses_str = " [HOTEL]"
                        else:
                            houses_str = f" [{prop_state.num_houses}H]"

                    mortgage_str = " [MORTGAGED]" if prop_state.is_mortgaged else ""
                    print(f"    • {tile_name}{houses_str}{mortgage_str}")

            if len(player.owned_properties) > 10:
                print(f"    ... and {len(player.owned_properties) - 10} more")

        # Opponents status
        print(f"\n👥 OPPONENTS:")
        for i, p in enumerate(state.players):
            if i != player_id and not p.is_bankrupt:
                print(f"  {self._get_player_name(i)}: ${p.cash}, "
                      f"{len(p.owned_properties)} properties, "
                      f"@ {self._get_tile_name(state, p.position)}")

        # Game stats
        active_players = sum(1 for p in state.players if not p.is_bankrupt)
        print(f"\n📊 GAME: Round {state.round_number}/50, {active_players} players active")

    def _get_tile_name(self, state, tile_id):
        """Get tile name from board."""
        # Simple tile names (you can enhance this)
        tile_names = [
            "GO", "Mediterranean Ave", "Community Chest", "Baltic Ave", "Income Tax",
            "Reading Railroad", "Oriental Ave", "Chance", "Vermont Ave", "Connecticut Ave",
            "Jail", "St. Charles Place", "Electric Company", "States Ave", "Virginia Ave",
            "Pennsylvania Railroad", "St. James Place", "Community Chest", "Tennessee Ave", "New York Ave",
            "Free Parking", "Kentucky Ave", "Chance", "Indiana Ave", "Illinois Ave",
            "B&O Railroad", "Atlantic Ave", "Ventnue Ave", "Water Works", "Marvin Gardens",
            "Go To Jail", "Pacific Ave", "North Carolina Ave", "Community Chest", "Pennsylvania Ave",
            "Short Line", "Chance", "Park Place", "Luxury Tax", "Boardwalk"
        ]

        if 0 <= tile_id < len(tile_names):
            return tile_names[tile_id]
        return f"Tile {tile_id}"

    def _get_player_name(self, player_id):
        """Get player name."""
        names = ["Alice", "Bob", "Charlie", "Dee", "Ethel", "Frankie"]
        if 0 <= player_id < len(names):
            return names[player_id]
        return f"Player {player_id}"


def load_trained_agents(checkpoint_dir: Path, config_path: Path, device: str = "cpu"):
    """
    Load trained agents from checkpoints.

    Args:
        checkpoint_dir: Directory containing checkpoints
        config_path: Path to player_behaviours.json
        device: Device to load models on

    Returns:
        Dictionary of loaded agents
    """
    board = MonopolyBoard()
    action_encoder = ActionEncoder(board)

    # Create agents
    agents = create_all_agents(
        json_path=config_path,
        board=board,
        action_encoder=action_encoder,
        total_training_games=10000
    )

    # Load models and checkpoints for each agent
    for agent_id, agent in agents.items():
        # Initialize model
        tokenizer = MonopolyTokenizer(board)
        model = MonopolyTransformer(
            num_actions=action_encoder.num_actions,
            device=device
        )

        agent.tokenizer = tokenizer
        agent.model = model

        # Try to load checkpoint
        checkpoint_path = checkpoint_dir / agent_id / "model.pt"
        if checkpoint_path.exists():
            try:
                model.load_state_dict(torch.load(checkpoint_path, map_location=device))
                print(f"✓ Loaded checkpoint for {agent_id}")
            except Exception as e:
                print(f"⚠ Could not load checkpoint for {agent_id}: {e}")
                print(f"  {agent_id} will use heuristics only")
        else:
            print(f"ℹ No checkpoint found for {agent_id}, using heuristics only")

    return agents


def play_game(agents: dict, num_opponents: int = 3, max_rounds: int = 50,
              checkpoint_dir: Path = None, device: str = "cpu"):
    """
    Play an interactive game.

    Args:
        agents: Dictionary of trained agents
        num_opponents: Number of AI opponents (1-5)
        max_rounds: Maximum rounds per game
        checkpoint_dir: Directory with checkpoints
        device: Device for models
    """
    # Select random opponents
    import random
    agent_ids = list(agents.keys())
    random.shuffle(agent_ids)
    selected_opponents = agent_ids[:num_opponents]

    print(f"\n{'='*80}")
    print(f"STARTING GAME: You vs {', '.join(selected_opponents)}")
    print(f"{'='*80}\n")

    # Create environment
    env = MonopolyEnv(
        num_players=num_opponents + 1,
        max_rounds=max_rounds,
        render_mode=None
    )

    # Map agents to player IDs
    player_agents = {}
    player_agents[0] = HumanPlayer()  # Human is player 0

    for i, opponent_id in enumerate(selected_opponents):
        player_agents[i + 1] = agents[opponent_id]

    # Reset environment
    env.reset()

    step_count = 0
    max_steps = max_rounds * (num_opponents + 1) * 20  # Safety limit

    # Game loop
    while not all(env.terminations.values()) and step_count < max_steps:
        step_count += 1

        # Get current agent
        current_agent_name = env.agent_selection
        player_id = env.agent_to_player_id[current_agent_name]
        current_agent = player_agents[player_id]

        # Get observation and mask
        observation, reward, termination, truncation, info = env.last()

        if termination or truncation:
            env.step(None)
            continue

        action_mask = info.get('action_mask')

        # Get action
        if isinstance(current_agent, HumanPlayer):
            # Human player
            action = current_agent.get_action(env, observation, action_mask)
        else:
            # AI agent
            action = current_agent.get_action(
                observation=observation,
                action_mask=action_mask,
                state=env.state,
                player_id=player_id,
                deterministic=True  # Use best action, not sampling
            )

            action_name = env.action_encoder.decode_action_name(action)
            print(f"\n🤖 {current_agent.name} ({current_agent.agent_id}): {action_name}")

        # Take action
        env.step(action)

        # Check for game end
        if all(env.terminations.values()):
            break

    # Game over
    print(f"\n{'='*80}")
    print(f"GAME OVER!")
    print(f"{'='*80}")

    # Find winner
    max_cash = -float('inf')
    winner_id = None

    for i, player in enumerate(env.state.players):
        if not player.is_bankrupt:
            total_value = player.cash
            # Add property values
            for tile_id in player.owned_properties:
                prop_state = env.state.properties.get(tile_id)
                if prop_state:
                    total_value += 100  # Simplified property value

            print(f"\n{player_agents[i].name}: ${player.cash}, "
                  f"{len(player.owned_properties)} properties")

            if total_value > max_cash:
                max_cash = total_value
                winner_id = i

    if winner_id is not None:
        winner = player_agents[winner_id]
        if isinstance(winner, HumanPlayer):
            print(f"\n🎉 YOU WIN! Congratulations!")
        else:
            print(f"\n😔 {winner.name} ({winner.agent_id}) wins!")

    print(f"\n{'='*80}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Play Monopoly against trained AI agents")

    parser.add_argument(
        "--checkpoint_dir",
        type=str,
        default="models/checkpoints",
        help="Directory containing agent checkpoints"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/player_behaviours.json",
        help="Path to agent configuration"
    )
    parser.add_argument(
        "--opponents",
        type=int,
        default=3,
        choices=[1, 2, 3, 4, 5],
        help="Number of AI opponents"
    )
    parser.add_argument(
        "--max_rounds",
        type=int,
        default=50,
        help="Maximum rounds per game"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        choices=["cpu", "cuda"],
        help="Device for model inference"
    )

    args = parser.parse_args()

    # Print banner
    print("\n" + "="*80)
    print(" "*25 + "MONOPOLY: HUMAN VS AI")
    print("="*80)
    print(f"\nLoading trained agents from {args.checkpoint_dir}...")

    # Load agents
    try:
        agents = load_trained_agents(
            checkpoint_dir=Path(args.checkpoint_dir),
            config_path=Path(args.config),
            device=args.device
        )
    except Exception as e:
        print(f"\n❌ Error loading agents: {e}")
        print("\nMake sure you have:")
        print(f"  1. Trained agents with checkpoints in {args.checkpoint_dir}/")
        print(f"  2. Config file at {args.config}")
        sys.exit(1)

    print(f"\nLoaded {len(agents)} agents successfully!")
    print(f"\nStarting game with {args.opponents} AI opponents...")

    # Play game
    try:
        play_game(
            agents=agents,
            num_opponents=args.opponents,
            max_rounds=args.max_rounds,
            checkpoint_dir=Path(args.checkpoint_dir),
            device=args.device
        )
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user. Thanks for playing!")
        sys.exit(0)

    # Ask if they want to play again
    while True:
        response = input("\nPlay another game? (y/n): ").strip().lower()
        if response == 'y':
            play_game(
                agents=agents,
                num_opponents=args.opponents,
                max_rounds=args.max_rounds,
                checkpoint_dir=Path(args.checkpoint_dir),
                device=args.device
            )
        elif response == 'n':
            print("\nThanks for playing!")
            break
        else:
            print("Please enter 'y' or 'n'")


if __name__ == "__main__":
    main()
