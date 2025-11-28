"""
Evaluation metrics tracking for multi-agent training.

Tracks per-agent statistics:
- Win rates
- Average rewards per game
- Games played
- Training progress

Logs metrics periodically during training.
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


class Evaluator:
    """
    Tracks and logs evaluation metrics for all agents.

    Maintains statistics across training and provides
    periodic logging and visualization support.
    """

    def __init__(self, agent_ids: List[str], log_dir: Optional[Path] = None):
        """
        Initialize evaluator.

        Args:
            agent_ids: List of all agent IDs
            log_dir: Directory to save logs (optional)
        """
        self.agent_ids = agent_ids
        self.log_dir = log_dir

        if log_dir:
            log_dir.mkdir(parents=True, exist_ok=True)

        # Per-agent statistics
        self.games_played = {agent_id: 0 for agent_id in agent_ids}
        self.wins = {agent_id: 0 for agent_id in agent_ids}
        self.total_rewards = {agent_id: [] for agent_id in agent_ids}

        # Per-game reward tracking for ALL agents (None if didn't play)
        self.game_rewards = {agent_id: [] for agent_id in agent_ids}
        self.max_rewards = {agent_id: None for agent_id in agent_ids}

        # Game history
        self.game_history = []

    def record_game_result(self, participants: List[str], winner_id: str,
                          rewards: Dict[str, float]):
        """
        Record result of a single game.

        Args:
            participants: List of agent IDs that participated
            winner_id: ID of winning agent
            rewards: Dictionary mapping agent_id to total reward in game
        """
        # Update stats for participating agents
        for agent_id in participants:
            self.games_played[agent_id] += 1
            self.total_rewards[agent_id].append(rewards[agent_id])

            if agent_id == winner_id:
                self.wins[agent_id] += 1

        # Store rewards for ALL agents (None for non-participants)
        for agent_id in self.agent_ids:
            if agent_id in participants:
                reward = rewards[agent_id]
                self.game_rewards[agent_id].append(reward)

                # Update max reward
                if self.max_rewards[agent_id] is None or reward > self.max_rewards[agent_id]:
                    self.max_rewards[agent_id] = reward
            else:
                # Agent didn't play this game - store None for masking
                self.game_rewards[agent_id].append(None)

        # Record game history
        self.game_history.append({
            'participants': participants,
            'winner': winner_id,
            'rewards': rewards
        })

    def get_win_rate(self, agent_id: str) -> float:
        """
        Get win rate for an agent.

        Args:
            agent_id: Agent ID

        Returns:
            Win rate (0-1)
        """
        if self.games_played[agent_id] == 0:
            return 0.0
        return self.wins[agent_id] / self.games_played[agent_id]

    def get_average_reward(self, agent_id: str, last_n: Optional[int] = None) -> float:
        """
        Get average reward for an agent.

        Args:
            agent_id: Agent ID
            last_n: If provided, average over last N games only

        Returns:
            Average reward per game
        """
        rewards = self.total_rewards[agent_id]

        if len(rewards) == 0:
            return 0.0

        if last_n is not None:
            rewards = rewards[-last_n:]

        return np.mean(rewards)

    def get_all_win_rates(self) -> Dict[str, float]:
        """Get win rates for all agents."""
        return {agent_id: self.get_win_rate(agent_id) for agent_id in self.agent_ids}

    def get_all_average_rewards(self, last_n: Optional[int] = None) -> Dict[str, float]:
        """Get average rewards for all agents."""
        return {
            agent_id: self.get_average_reward(agent_id, last_n)
            for agent_id in self.agent_ids
        }

    def get_max_reward(self, agent_id: str) -> Optional[float]:
        """
        Get maximum reward achieved by an agent.

        Args:
            agent_id: Agent ID

        Returns:
            Maximum reward, or None if agent hasn't played
        """
        return self.max_rewards[agent_id]

    def get_all_max_rewards(self) -> Dict[str, Optional[float]]:
        """Get maximum rewards for all agents."""
        return dict(self.max_rewards)

    def print_max_rewards(self, game_iteration: int):
        """
        Print maximum rewards for all agents.

        Args:
            game_iteration: Current game iteration
        """
        print(f"\n{'='*60}")
        print(f"Maximum Rewards at Game {game_iteration}")
        print(f"{'='*60}")
        print(f"{'Agent':<12} {'Max Reward':<15} {'Games Played':<12}")
        print(f"{'-'*60}")

        for agent_id in sorted(self.agent_ids):
            max_reward = self.max_rewards[agent_id]
            games = self.games_played[agent_id]

            if max_reward is not None:
                print(f"{agent_id:<12} {max_reward:>12.2f}    {games:<12}")
            else:
                print(f"{agent_id:<12} {'N/A':>12}    {games:<12}")

        print(f"{'='*60}\n")

    def log_metrics(self, game_iteration: int, verbose: bool = True):
        """
        Log current metrics.

        Args:
            game_iteration: Current game iteration
            verbose: If True, print to console
        """
        win_rates = self.get_all_win_rates()
        avg_rewards = self.get_all_average_rewards(last_n=100)

        if verbose:
            print(f"\n{'='*60}")
            print(f"Metrics at Game {game_iteration}")
            print(f"{'='*60}")
            print(f"{'Agent':<12} {'Games':<8} {'Win Rate':<12} {'Avg Reward (last 100)':<20}")
            print(f"{'-'*60}")

            for agent_id in self.agent_ids:
                games = self.games_played[agent_id]
                win_rate = win_rates[agent_id]
                avg_reward = avg_rewards[agent_id]

                print(f"{agent_id:<12} {games:<8} {win_rate:>6.1%}     {avg_reward:>10.2f}")

            print(f"{'='*60}\n")

        # Save to file if log_dir provided
        if self.log_dir:
            metrics = {
                'game_iteration': game_iteration,
                'win_rates': win_rates,
                'average_rewards': avg_rewards,
                'games_played': dict(self.games_played),
                'wins': dict(self.wins),
            }

            log_file = self.log_dir / f"metrics_{game_iteration:06d}.json"
            with open(log_file, 'w') as f:
                json.dump(metrics, f, indent=2)

    def get_summary_stats(self) -> Dict[str, Dict[str, float]]:
        """
        Get summary statistics for all agents.

        Returns:
            Dictionary mapping agent_id to stats dict
        """
        stats = {}

        for agent_id in self.agent_ids:
            stats[agent_id] = {
                'games_played': self.games_played[agent_id],
                'wins': self.wins[agent_id],
                'win_rate': self.get_win_rate(agent_id),
                'avg_reward_all': self.get_average_reward(agent_id),
                'avg_reward_last_100': self.get_average_reward(agent_id, last_n=100),
            }

        return stats

    def save_history(self, filepath: Path):
        """
        Save full game history to JSON.

        Args:
            filepath: Path to save history
        """
        history_data = {
            'agent_ids': self.agent_ids,
            'games_played': dict(self.games_played),
            'wins': dict(self.wins),
            'game_history': self.game_history,
            'game_rewards': {k: v for k, v in self.game_rewards.items()},  # Include None values
            'max_rewards': dict(self.max_rewards),
        }

        with open(filepath, 'w') as f:
            json.dump(history_data, f, indent=2)

    def load_history(self, filepath: Path):
        """
        Load game history from JSON.

        Args:
            filepath: Path to load history from
        """
        with open(filepath, 'r') as f:
            history_data = json.load(f)

        self.games_played = history_data['games_played']
        self.wins = history_data['wins']
        self.game_history = history_data['game_history']

        # Load game_rewards and max_rewards if available (backwards compatibility)
        if 'game_rewards' in history_data:
            self.game_rewards = history_data['game_rewards']
        else:
            # Reconstruct from game_history for backwards compatibility
            self.game_rewards = {agent_id: [] for agent_id in self.agent_ids}
            for game in self.game_history:
                for agent_id in self.agent_ids:
                    if agent_id in game['participants']:
                        self.game_rewards[agent_id].append(game['rewards'][agent_id])
                    else:
                        self.game_rewards[agent_id].append(None)

        if 'max_rewards' in history_data:
            self.max_rewards = history_data['max_rewards']
        else:
            # Reconstruct max_rewards
            self.max_rewards = {agent_id: None for agent_id in self.agent_ids}
            for agent_id in self.agent_ids:
                valid_rewards = [r for r in self.game_rewards[agent_id] if r is not None]
                if valid_rewards:
                    self.max_rewards[agent_id] = max(valid_rewards)

        # Reconstruct total_rewards from history
        self.total_rewards = {agent_id: [] for agent_id in self.agent_ids}
        for game in self.game_history:
            for agent_id, reward in game['rewards'].items():
                if agent_id in self.total_rewards:
                    self.total_rewards[agent_id].append(reward)
