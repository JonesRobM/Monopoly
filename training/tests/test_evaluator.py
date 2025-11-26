"""
Unit tests for Evaluator.

Tests metrics tracking and logging.
"""

import pytest
import json
from pathlib import Path
from training.evaluator import Evaluator


@pytest.fixture
def evaluator():
    """Create evaluator instance."""
    agent_ids = ['alice', 'bob', 'charlie', 'dee']
    return Evaluator(agent_ids, log_dir=None)


class TestEvaluator:
    """Test suite for Evaluator."""

    def test_initialization(self):
        """Test evaluator initialization."""
        agent_ids = ['alice', 'bob', 'charlie']
        evaluator = Evaluator(agent_ids)

        assert evaluator.agent_ids == agent_ids
        assert all(evaluator.games_played[aid] == 0 for aid in agent_ids)
        assert all(evaluator.wins[aid] == 0 for aid in agent_ids)

    def test_record_single_game(self, evaluator):
        """Test recording a single game result."""
        participants = ['alice', 'bob', 'charlie']
        winner = 'alice'
        rewards = {'alice': 100.0, 'bob': -20.0, 'charlie': 30.0}

        evaluator.record_game_result(participants, winner, rewards)

        assert evaluator.games_played['alice'] == 1
        assert evaluator.wins['alice'] == 1
        assert evaluator.total_rewards['alice'] == [100.0]

    def test_record_multiple_games(self, evaluator):
        """Test recording multiple games."""
        # Game 1: Alice wins
        evaluator.record_game_result(
            ['alice', 'bob'],
            'alice',
            {'alice': 100.0, 'bob': -50.0}
        )

        # Game 2: Bob wins
        evaluator.record_game_result(
            ['alice', 'bob'],
            'bob',
            {'alice': 20.0, 'bob': 80.0}
        )

        assert evaluator.games_played['alice'] == 2
        assert evaluator.wins['alice'] == 1
        assert evaluator.wins['bob'] == 1

    def test_win_rate_calculation(self, evaluator):
        """Test win rate calculation."""
        # Alice plays 4 games, wins 3
        for i in range(3):
            evaluator.record_game_result(
                ['alice', 'bob'],
                'alice',
                {'alice': 100.0, 'bob': 0.0}
            )

        evaluator.record_game_result(
            ['alice', 'bob'],
            'bob',
            {'alice': 20.0, 'bob': 80.0}
        )

        win_rate = evaluator.get_win_rate('alice')
        assert abs(win_rate - 0.75) < 0.01  # 3/4 = 0.75

    def test_win_rate_no_games(self, evaluator):
        """Test win rate when no games played."""
        win_rate = evaluator.get_win_rate('alice')
        assert win_rate == 0.0

    def test_average_reward_calculation(self, evaluator):
        """Test average reward calculation."""
        evaluator.record_game_result(
            ['alice', 'bob'],
            'alice',
            {'alice': 100.0, 'bob': 0.0}
        )

        evaluator.record_game_result(
            ['alice', 'bob'],
            'alice',
            {'alice': 200.0, 'bob': 0.0}
        )

        avg_reward = evaluator.get_average_reward('alice')
        assert abs(avg_reward - 150.0) < 0.01  # (100 + 200) / 2

    def test_average_reward_last_n(self, evaluator):
        """Test average reward over last N games."""
        # Record 10 games with increasing rewards
        for i in range(10):
            evaluator.record_game_result(
                ['alice', 'bob'],
                'alice',
                {'alice': float(i * 10), 'bob': 0.0}
            )

        # Average of last 3: (70 + 80 + 90) / 3 = 80
        avg_last_3 = evaluator.get_average_reward('alice', last_n=3)
        assert abs(avg_last_3 - 80.0) < 0.01

    def test_get_all_win_rates(self, evaluator):
        """Test getting win rates for all agents."""
        evaluator.record_game_result(
            ['alice', 'bob', 'charlie'],
            'alice',
            {'alice': 100.0, 'bob': 0.0, 'charlie': 0.0}
        )

        win_rates = evaluator.get_all_win_rates()

        assert 'alice' in win_rates
        assert 'bob' in win_rates
        assert win_rates['alice'] == 1.0
        assert win_rates['bob'] == 0.0

    def test_get_summary_stats(self, evaluator):
        """Test getting summary statistics."""
        # Record a few games
        for i in range(5):
            evaluator.record_game_result(
                ['alice', 'bob'],
                'alice',
                {'alice': 100.0, 'bob': 0.0}
            )

        stats = evaluator.get_summary_stats()

        assert 'alice' in stats
        assert stats['alice']['games_played'] == 5
        assert stats['alice']['wins'] == 5
        assert stats['alice']['win_rate'] == 1.0

    def test_game_history_tracking(self, evaluator):
        """Test that game history is tracked."""
        evaluator.record_game_result(
            ['alice', 'bob'],
            'alice',
            {'alice': 100.0, 'bob': 0.0}
        )

        assert len(evaluator.game_history) == 1
        assert evaluator.game_history[0]['winner'] == 'alice'
        assert evaluator.game_history[0]['participants'] == ['alice', 'bob']

    def test_log_metrics_no_crash(self, evaluator):
        """Test that log_metrics doesn't crash."""
        # Record some games
        evaluator.record_game_result(
            ['alice', 'bob'],
            'alice',
            {'alice': 100.0, 'bob': 0.0}
        )

        # Should not raise exception
        evaluator.log_metrics(game_iteration=10, verbose=False)

    def test_save_and_load_history(self, evaluator, tmp_path):
        """Test saving and loading game history."""
        # Record games
        evaluator.record_game_result(
            ['alice', 'bob'],
            'alice',
            {'alice': 100.0, 'bob': 0.0}
        )

        evaluator.record_game_result(
            ['alice', 'bob'],
            'bob',
            {'alice': 20.0, 'bob': 80.0}
        )

        # Save
        filepath = tmp_path / "history.json"
        evaluator.save_history(filepath)

        # Create new evaluator and load
        new_evaluator = Evaluator(['alice', 'bob', 'charlie', 'dee'])
        new_evaluator.load_history(filepath)

        assert new_evaluator.games_played['alice'] == 2
        assert new_evaluator.wins['alice'] == 1
        assert len(new_evaluator.game_history) == 2

    def test_save_metrics_with_log_dir(self, tmp_path):
        """Test saving metrics to log directory."""
        log_dir = tmp_path / "logs"
        evaluator = Evaluator(['alice', 'bob'], log_dir=log_dir)

        evaluator.record_game_result(
            ['alice', 'bob'],
            'alice',
            {'alice': 100.0, 'bob': 0.0}
        )

        evaluator.log_metrics(game_iteration=100, verbose=False)

        # Check that metrics file was created
        metrics_file = log_dir / "metrics_000100.json"
        assert metrics_file.exists()

        # Load and verify
        with open(metrics_file, 'r') as f:
            metrics = json.load(f)

        assert metrics['game_iteration'] == 100
        assert 'win_rates' in metrics
        assert 'alice' in metrics['win_rates']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
