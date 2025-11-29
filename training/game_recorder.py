"""
Game recorder for capturing 1% of games for visualization.

Records game states, actions, and rewards to analyze strategy development.
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class GameStep:
    """Single step in a recorded game."""
    step_number: int
    player_id: int
    action: int
    action_name: str
    reward: float
    # Store minimal state info for visualization
    player_cash: Dict[int, float]
    player_positions: Dict[int, int]
    property_owners: Dict[int, int]  # tile_id -> player_id
    houses: Dict[int, int]  # tile_id -> num_houses (0-5)


@dataclass
class RecordedGame:
    """Complete recorded game."""
    game_id: int
    game_iteration: int  # Which training iteration
    participants: List[str]  # Agent IDs
    winner_id: str
    final_rewards: Dict[str, float]
    steps: List[Dict[str, Any]]  # Serialized GameSteps
    alpha_values: Dict[str, float]  # Alpha at time of game
    game_length: int  # Number of steps


class GameRecorder:
    """
    Records 1% of games for visualization and analysis.

    Saves game trajectories to JSON files for later analysis of
    strategy development over training.
    """

    def __init__(
        self,
        save_dir: Path,
        sample_rate: float = 0.01,
        seed: Optional[int] = None
    ):
        """
        Initialize game recorder.

        Args:
            save_dir: Directory to save recorded games
            sample_rate: Fraction of games to record (default 0.01 = 1%)
            seed: Random seed for sampling
        """
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)

        self.sample_rate = sample_rate
        self.rng = random.Random(seed)

        self.games_seen = 0
        self.games_recorded = 0

        # Current recording state
        self.recording = False
        self.current_game: Optional[RecordedGame] = None
        self.current_steps: List[GameStep] = []

    def should_record_game(self) -> bool:
        """
        Decide whether to record this game (1% probability).

        Returns:
            True if game should be recorded
        """
        return self.rng.random() < self.sample_rate

    def start_recording(
        self,
        game_id: int,
        game_iteration: int,
        participants: List[str],
        alpha_values: Dict[str, float]
    ):
        """
        Start recording a new game.

        Args:
            game_id: Unique game identifier
            game_iteration: Training iteration number
            participants: List of agent IDs in this game
            alpha_values: Current alpha values for each agent
        """
        self.games_seen += 1

        if not self.should_record_game():
            self.recording = False
            return

        self.recording = True
        self.games_recorded += 1
        self.current_steps = []

        # Create placeholder game record
        self.current_game = RecordedGame(
            game_id=game_id,
            game_iteration=game_iteration,
            participants=participants,
            winner_id="",  # Will be set on finish
            final_rewards={},
            steps=[],
            alpha_values=alpha_values,
            game_length=0
        )

    def record_step(
        self,
        step_number: int,
        player_id: int,
        action: int,
        action_name: str,
        reward: float,
        state: Any  # GameState or dict
    ):
        """
        Record a single step in the game.

        Args:
            step_number: Step number in game
            player_id: Player taking action
            action: Action index
            action_name: Human-readable action name
            reward: Reward received
            state: Current game state (GameState object or dict)
        """
        if not self.recording:
            return

        # Extract minimal state info for visualization
        # Handle both GameState objects and dicts
        if hasattr(state, 'players'):
            # GameState object
            player_cash = {p.player_id: p.cash for p in state.players}
            player_positions = {p.player_id: p.position for p in state.players}
            # Derive property ownership from properties dict
            property_owners = {}
            houses = {}
            if hasattr(state, 'properties'):
                for tile_id, prop_state in state.properties.items():
                    if hasattr(prop_state, 'owner') and prop_state.owner is not None:
                        property_owners[tile_id] = prop_state.owner
                    if hasattr(prop_state, 'num_houses'):
                        houses[tile_id] = prop_state.num_houses
        else:
            # Dict representation
            player_cash = {i: p['cash'] for i, p in enumerate(state.get('players', []))}
            player_positions = {i: p['position'] for i, p in enumerate(state.get('players', []))}
            property_owners = state.get('property_owners', {})
            houses = state.get('houses', {})

        step = GameStep(
            step_number=step_number,
            player_id=player_id,
            action=action,
            action_name=action_name,
            reward=reward,
            player_cash=player_cash,
            player_positions=player_positions,
            property_owners=property_owners,
            houses=houses
        )

        self.current_steps.append(step)

    def finish_recording(
        self,
        winner_id: str,
        final_rewards: Dict[str, float]
    ):
        """
        Finish recording current game and save to disk.

        Args:
            winner_id: Agent ID of winner
            final_rewards: Final rewards for all participants
        """
        if not self.recording or self.current_game is None:
            return

        # Complete the game record
        self.current_game.winner_id = winner_id
        self.current_game.final_rewards = final_rewards
        self.current_game.game_length = len(self.current_steps)
        self.current_game.steps = [asdict(step) for step in self.current_steps]

        # Save to file
        self._save_game(self.current_game)

        # Reset recording state
        self.recording = False
        self.current_game = None
        self.current_steps = []

    def _save_game(self, game: RecordedGame):
        """
        Save recorded game to JSON file.

        Args:
            game: RecordedGame to save
        """
        filename = f"game_{game.game_iteration:06d}_{game.game_id:04d}.json"
        filepath = self.save_dir / filename

        # Convert to dict and save
        game_dict = asdict(game)

        with open(filepath, 'w') as f:
            json.dump(game_dict, f, indent=2)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get recording statistics.

        Returns:
            Dict with recording stats
        """
        return {
            'games_seen': self.games_seen,
            'games_recorded': self.games_recorded,
            'sample_rate': self.sample_rate,
            'recording_percentage':
                100.0 * self.games_recorded / self.games_seen if self.games_seen > 0 else 0.0
        }

    def load_game(self, filepath: Path) -> RecordedGame:
        """
        Load a recorded game from file.

        Args:
            filepath: Path to game JSON file

        Returns:
            RecordedGame object
        """
        with open(filepath, 'r') as f:
            game_dict = json.load(f)

        # Reconstruct RecordedGame
        # Steps stay as dicts (don't need to reconstruct GameStep objects)
        return RecordedGame(**game_dict)

    def list_recorded_games(self) -> List[Path]:
        """
        List all recorded game files.

        Returns:
            List of paths to recorded games, sorted by iteration
        """
        return sorted(self.save_dir.glob("game_*.json"))

    def get_games_by_iteration(self, min_iter: int, max_iter: int) -> List[Path]:
        """
        Get recorded games within iteration range.

        Args:
            min_iter: Minimum iteration (inclusive)
            max_iter: Maximum iteration (inclusive)

        Returns:
            List of game files in range
        """
        games = []
        for filepath in self.list_recorded_games():
            # Parse iteration from filename: game_IIIIIII_GGGG.json
            parts = filepath.stem.split('_')
            if len(parts) >= 2:
                iteration = int(parts[1])
                if min_iter <= iteration <= max_iter:
                    games.append(filepath)
        return games


if __name__ == "__main__":
    # Quick test
    from pathlib import Path

    recorder = GameRecorder(Path("test_recordings"), sample_rate=1.0, seed=42)

    # Test recording
    recorder.start_recording(
        game_id=1,
        game_iteration=100,
        participants=['alice', 'bob', 'charlie', 'dee'],
        alpha_values={'alice': 0.75, 'bob': 0.6, 'charlie': 0.5, 'dee': 0.65}
    )

    # Mock state
    mock_state = {
        'players': [
            {'cash': 1500, 'position': 5},
            {'cash': 1200, 'position': 12},
            {'cash': 1800, 'position': 20},
            {'cash': 1000, 'position': 30}
        ],
        'property_owners': {5: 0, 12: 1, 20: 2},
        'houses': {5: 0, 12: 2, 20: 1}
    }

    recorder.record_step(0, 0, 5, "BUY_PROPERTY", 10.0, mock_state)
    recorder.record_step(1, 1, 10, "BUILD_HOUSE", 15.0, mock_state)

    recorder.finish_recording('alice', {'alice': 100.0, 'bob': -20.0, 'charlie': 30.0, 'dee': -10.0})

    print(f"Stats: {recorder.get_stats()}")
    print(f"Recorded games: {len(recorder.list_recorded_games())}")
