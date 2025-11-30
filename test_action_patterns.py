"""
Test to identify what actions agents are taking during long turns.

This will show the action sequences when turns exceed 10 actions.
"""

import json
from pathlib import Path
from training.multi_agent_trainer import MultiAgentTrainer


def test_action_patterns():
    """Run a few games and capture action patterns."""
    print("="*60)
    print("Action Pattern Analysis")
    print("="*60)

    # Load agent configs
    config_path = Path("config/player_behaviours.json")
    with open(config_path) as f:
        data = json.load(f)
        agent_configs = {player['id']: player for player in data['players']}

    # Create trainer
    trainer = MultiAgentTrainer(
        agent_configs=agent_configs,
        checkpoint_dir=Path("models/checkpoints"),
        log_dir=Path("logs"),
        recording_dir=Path("recordings"),
        update_frequency=20,
        seed=42,
        watch_mode=False,
        min_players=4,
        max_players=4
    )

    print("\nRunning 3 games to capture action patterns...")
    print("Watch for 'WARNING' messages showing action sequences\n")

    try:
        trainer.train(num_games=3)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
    print("Analysis complete!")
    print("="*60)
    print("\nCheck the WARNING messages above to see what actions")
    print("agents are repeatedly taking.")


if __name__ == "__main__":
    test_action_patterns()
