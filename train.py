#!/usr/bin/env python
"""
Main entry point for training 10-agent Monopoly RL system.

Usage:
    python train.py --num_games 10000
    python train.py --num_games 1000 --seed 42 --checkpoint_dir models/checkpoints
    python train.py --resume 5000 --num_games 5000
"""

import argparse
import json
import sys
from pathlib import Path

import torch

from training.multi_agent_trainer import MultiAgentTrainer


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Train 10-agent Monopoly RL system",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Training parameters
    parser.add_argument(
        "--num_games",
        type=int,
        default=10000,
        help="Number of games to train"
    )
    parser.add_argument(
        "--update_frequency",
        type=int,
        default=10,
        help="Update models every N games"
    )
    parser.add_argument(
        "--log_frequency",
        type=int,
        default=100,
        help="Log metrics every N games"
    )
    parser.add_argument(
        "--checkpoint_frequency",
        type=int,
        default=1000,
        help="Save checkpoints every N games"
    )

    # Directories
    parser.add_argument(
        "--config",
        type=str,
        default="config/player_behaviours.json",
        help="Path to agent configuration JSON"
    )
    parser.add_argument(
        "--checkpoint_dir",
        type=str,
        default="models/checkpoints",
        help="Directory for model checkpoints"
    )
    parser.add_argument(
        "--log_dir",
        type=str,
        default="logs",
        help="Directory for training logs"
    )
    parser.add_argument(
        "--recording_dir",
        type=str,
        default="recordings",
        help="Directory for recorded games (1% sample)"
    )

    # Training control
    parser.add_argument(
        "--resume",
        type=int,
        default=None,
        help="Resume from checkpoint at game iteration N"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        choices=["auto", "cuda", "cpu"],
        help="Device to use for training (auto detects CUDA)"
    )

    # Game parameters
    parser.add_argument(
        "--min_players",
        type=int,
        default=4,
        help="Minimum number of players per game (4-6)"
    )
    parser.add_argument(
        "--max_players",
        type=int,
        default=6,
        help="Maximum number of players per game (4-6)"
    )
    parser.add_argument(
        "--max_rounds",
        type=int,
        default=50,
        help="Maximum rounds per game (each player takes a turn)"
    )
    parser.add_argument(
        "--max_turns",
        type=int,
        default=None,
        help="(Deprecated) Maximum turns per game before timeout"
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch games with detailed turn-by-turn output"
    )
    parser.add_argument(
        "--render",
        type=str,
        default=None,
        choices=["pygame", "human", "ansi"],
        help="Render mode: pygame (graphical), human/ansi (text), or None (no rendering)"
    )

    return parser.parse_args()


def main():
    """Main training function."""
    args = parse_args()

    # Print banner
    print("\n" + "="*70)
    print(" "*15 + "10-Agent Monopoly RL Training")
    print("="*70)
    print(f"\nConfiguration:")
    print(f"  Number of games:        {args.num_games}")
    print(f"  Update frequency:       every {args.update_frequency} games")
    print(f"  Log frequency:          every {args.log_frequency} games")
    print(f"  Checkpoint frequency:   every {args.checkpoint_frequency} games")
    print(f"  Players per game:       {args.min_players}-{args.max_players}")
    print(f"  Max rounds per game:    {args.max_rounds}")
    if args.max_turns is not None:
        print(f"  Max turns per game:     {args.max_turns} (deprecated)")
    print(f"  Watch mode:             {'Enabled' if args.watch else 'Disabled'}")
    print(f"  Render mode:            {args.render if args.render else 'None (no rendering)'}")
    print(f"  Random seed:            {args.seed if args.seed else 'None (random)'}")
    print(f"  Resume from:            {args.resume if args.resume else 'None (fresh start)'}")
    print(f"\nDirectories:")
    print(f"  Config:                 {args.config}")
    print(f"  Checkpoints:            {args.checkpoint_dir}")
    print(f"  Logs:                   {args.log_dir}")
    print(f"  Recordings:             {args.recording_dir}")

    # Determine device
    if args.device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = args.device

    print(f"  Device:                 {device}")

    if device == "cuda":
        print(f"  GPU:                    {torch.cuda.get_device_name(0)}")

    print("="*70 + "\n")

    # Validate player counts
    if not (4 <= args.min_players <= 6):
        print(f"Error: min_players must be between 4 and 6 (got {args.min_players})")
        sys.exit(1)
    if not (4 <= args.max_players <= 6):
        print(f"Error: max_players must be between 4 and 6 (got {args.max_players})")
        sys.exit(1)
    if args.min_players > args.max_players:
        print(f"Error: min_players ({args.min_players}) cannot be greater than max_players ({args.max_players})")
        sys.exit(1)

    # Load agent configurations
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        print(f"\nExpected agent configuration file at: {config_path}")
        print(f"This file should contain definitions for all 10 agents.")
        sys.exit(1)

    print(f"Loading agent configurations from {config_path}...")
    with open(config_path) as f:
        config_data = json.load(f)

    # Handle both formats: {"players": [...]} or {"alice": {...}, "bob": {...}}
    if "players" in config_data:
        # Convert array format to dict format
        agent_configs = {player['id']: player for player in config_data['players']}
    else:
        agent_configs = config_data

    print(f"Loaded {len(agent_configs)} agents:")
    for agent_id, config in agent_configs.items():
        print(f"  - {agent_id}: {config['name']} ({config['strategy_type']})")

    print()

    # Create trainer
    print("Initializing multi-agent trainer...")
    trainer = MultiAgentTrainer(
        agent_configs=agent_configs,
        checkpoint_dir=Path(args.checkpoint_dir),
        log_dir=Path(args.log_dir),
        recording_dir=Path(args.recording_dir),
        update_frequency=args.update_frequency,
        log_frequency=args.log_frequency,
        checkpoint_frequency=args.checkpoint_frequency,
        device=device,
        seed=args.seed,
        watch_mode=args.watch,
        max_rounds=args.max_rounds,
        max_turns=args.max_turns,
        min_players=args.min_players,
        max_players=args.max_players,
        render_mode=args.render
    )

    print("Trainer initialized successfully!\n")

    # Resume from checkpoint if specified
    start_game = 0
    if args.resume is not None:
        print(f"Resuming from checkpoint at game {args.resume}...")
        try:
            trainer.load_checkpoint(args.resume)
            start_game = args.resume
            print(f"Successfully resumed from game {args.resume}\n")
        except Exception as e:
            print(f"Error loading checkpoint: {e}")
            print("Starting fresh training instead.\n")

    # Start training
    try:
        trainer.train(
            num_games=args.num_games,
            start_game=start_game
        )
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user!")
        print("Saving emergency checkpoint...")
        trainer.save_checkpoints(trainer.game_iteration)
        print("Checkpoint saved. You can resume with:")
        print(f"  python train.py --resume {trainer.game_iteration} --num_games {args.num_games}")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError during training: {e}")
        import traceback
        traceback.print_exc()
        print("\nSaving emergency checkpoint...")
        trainer.save_checkpoints(trainer.game_iteration)
        sys.exit(1)

    # Training complete
    print("\n" + "="*70)
    print("Training Complete!")
    print("="*70)
    print(f"\nFinal Statistics:")
    stats = trainer.evaluator.get_summary_stats()

    print("\nWin Rates:")
    for agent_id, agent_stats in sorted(stats.items()):
        print(f"  {agent_id:10s}: {agent_stats['win_rate']:.3f} "
              f"({agent_stats['wins']}/{agent_stats['games_played']} wins)")

    print("\nAverage Rewards (last 100 games):")
    for agent_id in sorted(stats.keys()):
        avg_reward = trainer.evaluator.get_average_reward(agent_id, last_n=100)
        print(f"  {agent_id:10s}: {avg_reward:8.2f}")

    print("\nAlpha Values (final):")
    for agent_id, agent in sorted(trainer.agents.items()):
        final_alpha = agent.alpha_schedule.get_alpha(trainer.game_iteration)
        print(f"  {agent_id:10s}: {final_alpha:.4f}")

    print("\nOutputs:")
    print(f"  Checkpoints:   {args.checkpoint_dir}/")
    print(f"  Logs:          {args.log_dir}/")
    print(f"  Recordings:    {args.recording_dir}/")

    recording_stats = trainer.game_recorder.get_stats()
    print(f"\nGames Recorded: {recording_stats['games_recorded']} "
          f"({recording_stats['recording_percentage']:.1f}%)")

    print("\n" + "="*70)
    print("Next Steps:")
    print("  1. Analyze training logs:    cat logs/metrics_*.json")
    print("  2. Review recorded games:    ls recordings/")
    print("  3. Visualize strategies:     python analysis/visualize_games.py")
    print("  4. Continue training:        python train.py --resume "
          f"{trainer.game_iteration} --num_games 10000")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
