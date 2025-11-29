"""
Visualize recorded games from training.

Loads and displays games recorded during training to analyze
strategy development and agent behavior.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
import argparse


# Monopoly board configuration
BOARD_TILES = [
    "GO", "Mediterranean Avenue", "Community Chest", "Baltic Avenue", "Income Tax",
    "Reading Railroad", "Oriental Avenue", "Chance", "Vermont Avenue", "Connecticut Avenue",
    "Jail/Just Visiting", "St. Charles Place", "Electric Company", "States Avenue", "Virginia Avenue",
    "Pennsylvania Railroad", "St. James Place", "Community Chest", "Tennessee Avenue", "New York Avenue",
    "Free Parking", "Kentucky Avenue", "Chance", "Indiana Avenue", "Illinois Avenue",
    "B&O Railroad", "Atlantic Avenue", "Ventnue Avenue", "Water Works", "Marvin Gardens",
    "Go To Jail", "Pacific Avenue", "North Carolina Avenue", "Community Chest", "Pennsylvania Avenue",
    "Short Line Railroad", "Chance", "Park Place", "Luxury Tax", "Boardwalk"
]

# Color groups for properties
PROPERTY_COLORS = {
    1: "brown", 3: "brown",
    6: "lightblue", 8: "lightblue", 9: "lightblue",
    11: "pink", 13: "pink", 14: "pink",
    16: "orange", 18: "orange", 19: "orange",
    21: "red", 23: "red", 24: "red",
    26: "yellow", 27: "yellow", 29: "yellow",
    31: "green", 32: "green", 34: "green",
    37: "darkblue", 39: "darkblue"
}

# Player colors for display
PLAYER_COLORS = [
    '\033[91m',  # Red
    '\033[92m',  # Green
    '\033[93m',  # Yellow
    '\033[94m',  # Blue
    '\033[95m',  # Magenta
    '\033[96m',  # Cyan
]
RESET_COLOR = '\033[0m'


def load_game(filepath: Path) -> Dict:
    """Load a recorded game from JSON."""
    with open(filepath, 'r') as f:
        return json.load(f)


def list_games(recordings_dir: Path) -> List[Path]:
    """List all recorded game files."""
    return sorted(recordings_dir.glob("game_*.json"))


def display_game_summary(game: Dict):
    """Display summary information about a game."""
    print("\n" + "="*80)
    print(f"GAME SUMMARY")
    print("="*80)
    print(f"Game ID: {game['game_id']}")
    print(f"Training Iteration: {game['game_iteration']}")
    print(f"Game Length: {game['game_length']} steps")
    print(f"Winner: {game['winner_id']}")
    print(f"\nParticipants:")
    for i, participant in enumerate(game['participants']):
        final_reward = game['final_rewards'].get(participant, 0.0)
        alpha = game['alpha_values'].get(participant, 0.0)
        color = PLAYER_COLORS[i % len(PLAYER_COLORS)]
        print(f"  {color}{participant}{RESET_COLOR}: α={alpha:.3f}, Final Reward={final_reward:.1f}")
    print("="*80 + "\n")


def display_step(step: Dict, step_num: int, total_steps: int):
    """Display a single game step."""
    player_id = step['player_id']
    action_name = step['action_name']
    reward = step['reward']

    # Get player data
    player_cash = step['player_cash']
    player_positions = step['player_positions']
    property_owners = {int(k): v for k, v in step['property_owners'].items()}
    houses = {int(k): v for k, v in step['houses'].items()}

    # Header
    print(f"\n{'─'*80}")
    print(f"Step {step_num + 1}/{total_steps}")
    print(f"{'─'*80}")

    # Action
    color = PLAYER_COLORS[player_id % len(PLAYER_COLORS)]
    print(f"{color}Player {player_id}{RESET_COLOR} → {action_name} (reward: {reward:+.2f})")

    # Player positions and cash
    print(f"\nPlayer Status:")
    for pid in sorted(player_cash.keys()):
        pid_int = int(pid)
        cash = player_cash[pid]
        position = player_positions[pid]
        tile_name = BOARD_TILES[position]

        color = PLAYER_COLORS[pid_int % len(PLAYER_COLORS)]
        print(f"  {color}Player {pid_int}{RESET_COLOR}: ${cash:.0f} @ {tile_name} (pos {position})")

    # Property ownership summary
    ownership_by_player = {}
    for tile_id, owner_id in property_owners.items():
        owner_int = int(owner_id)
        if owner_int not in ownership_by_player:
            ownership_by_player[owner_int] = []

        num_houses = houses.get(tile_id, 0)
        house_str = ""
        if num_houses > 0:
            if num_houses == 5:
                house_str = " [HOTEL]"
            else:
                house_str = f" [{num_houses}H]"

        tile_name = BOARD_TILES[tile_id] if tile_id < len(BOARD_TILES) else f"Tile {tile_id}"
        ownership_by_player[owner_int].append(f"{tile_name}{house_str}")

    if ownership_by_player:
        print(f"\nProperty Ownership:")
        for owner_id in sorted(ownership_by_player.keys()):
            color = PLAYER_COLORS[owner_id % len(PLAYER_COLORS)]
            props = ownership_by_player[owner_id]
            print(f"  {color}Player {owner_id}{RESET_COLOR}: {len(props)} properties")
            for prop in props[:5]:  # Show first 5
                print(f"    - {prop}")
            if len(props) > 5:
                print(f"    ... and {len(props) - 5} more")


def replay_game(game: Dict, pause_mode: bool = False, step_range: Optional[tuple] = None):
    """Replay a game step-by-step."""
    steps = game['steps']

    if step_range:
        start, end = step_range
        steps = steps[start:end]
        print(f"\nShowing steps {start} to {end} of {len(game['steps'])}")

    for i, step in enumerate(steps):
        display_step(step, i, len(steps))

        if pause_mode:
            response = input("\nPress Enter for next step (or 'q' to quit): ")
            if response.lower() == 'q':
                break


def show_game_statistics(game: Dict):
    """Show aggregate statistics for a game."""
    steps = game['steps']

    # Action frequency
    action_counts = {}
    for step in steps:
        action = step['action_name']
        action_counts[action] = action_counts.get(action, 0) + 1

    # Reward progression by player
    player_rewards = {}
    for step in steps:
        player_id = step['player_id']
        if player_id not in player_rewards:
            player_rewards[player_id] = []
        player_rewards[player_id].append(step['reward'])

    # Cash progression
    final_step = steps[-1]
    final_cash = final_step['player_cash']

    print("\n" + "="*80)
    print("GAME STATISTICS")
    print("="*80)

    print(f"\nAction Frequency:")
    for action, count in sorted(action_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {action}: {count}")

    print(f"\nReward Summary:")
    for player_id in sorted(player_rewards.keys()):
        rewards = player_rewards[player_id]
        total = sum(rewards)
        avg = total / len(rewards) if rewards else 0
        color = PLAYER_COLORS[int(player_id) % len(PLAYER_COLORS)]
        print(f"  {color}Player {player_id}{RESET_COLOR}: Total={total:+.1f}, Avg={avg:+.3f}, Steps={len(rewards)}")

    print(f"\nFinal Cash:")
    for player_id in sorted(final_cash.keys()):
        cash = final_cash[player_id]
        color = PLAYER_COLORS[int(player_id) % len(PLAYER_COLORS)]
        print(f"  {color}Player {player_id}{RESET_COLOR}: ${cash:.0f}")

    print("="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Visualize recorded Monopoly games")
    parser.add_argument(
        '--recordings-dir',
        type=Path,
        default=Path('recordings'),
        help='Directory containing recorded games'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all recorded games'
    )
    parser.add_argument(
        '--game',
        type=int,
        help='Game index to visualize (0-based)'
    )
    parser.add_argument(
        '--file',
        type=Path,
        help='Specific game file to visualize'
    )
    parser.add_argument(
        '--pause',
        action='store_true',
        help='Pause after each step (interactive mode)'
    )
    parser.add_argument(
        '--start-step',
        type=int,
        default=0,
        help='Starting step to display'
    )
    parser.add_argument(
        '--end-step',
        type=int,
        help='Ending step to display (exclusive)'
    )
    parser.add_argument(
        '--stats-only',
        action='store_true',
        help='Show only statistics, not step-by-step replay'
    )

    args = parser.parse_args()

    # List games
    if args.list:
        games = list_games(args.recordings_dir)
        print(f"\nFound {len(games)} recorded games in {args.recordings_dir}:")
        for i, game_path in enumerate(games):
            # Parse filename: game_IIIIIII_GGGG.json
            parts = game_path.stem.split('_')
            iteration = int(parts[1])
            game_id = int(parts[2])
            print(f"  [{i}] Iteration {iteration}, Game {game_id} - {game_path.name}")
        return

    # Load game
    if args.file:
        game_path = args.file
    elif args.game is not None:
        games = list_games(args.recordings_dir)
        if args.game >= len(games):
            print(f"Error: Game index {args.game} out of range (0-{len(games)-1})")
            return
        game_path = games[args.game]
    else:
        # Default: show most recent game
        games = list_games(args.recordings_dir)
        if not games:
            print(f"No recorded games found in {args.recordings_dir}")
            return
        game_path = games[-1]
        print(f"Showing most recent game: {game_path.name}")

    game = load_game(game_path)

    # Display game
    display_game_summary(game)
    show_game_statistics(game)

    if not args.stats_only:
        step_range = None
        if args.end_step is not None:
            step_range = (args.start_step, args.end_step)
        elif args.start_step > 0:
            step_range = (args.start_step, len(game['steps']))

        replay_game(game, pause_mode=args.pause, step_range=step_range)


if __name__ == "__main__":
    main()
