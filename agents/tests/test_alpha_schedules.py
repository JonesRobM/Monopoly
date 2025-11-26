"""
Unit tests for alpha annealing schedules.

Tests linear and exponential decay schedules with per-agent configurations.
"""

import pytest
import numpy as np
from agents.alpha_schedules import AlphaSchedule, create_alpha_schedule, ALPHA_CONFIGS


class TestAlphaSchedule:
    """Test suite for AlphaSchedule."""

    def test_initialization(self):
        """Test schedule initialization."""
        schedule = AlphaSchedule(
            alpha_initial=0.8,
            alpha_final=0.2,
            total_games=1000,
            schedule_type="linear"
        )
        assert schedule.alpha_initial == 0.8
        assert schedule.alpha_final == 0.2
        assert schedule.total_games == 1000

    def test_invalid_alpha_range(self):
        """Test that invalid alpha values raise ValueError."""
        with pytest.raises(ValueError, match="alpha_initial must be in"):
            AlphaSchedule(1.5, 0.2, 1000)

        with pytest.raises(ValueError, match="alpha_final must be in"):
            AlphaSchedule(0.8, -0.1, 1000)

    def test_invalid_alpha_ordering(self):
        """Test that alpha_initial < alpha_final raises ValueError."""
        with pytest.raises(ValueError, match="alpha_initial must be >= alpha_final"):
            AlphaSchedule(0.2, 0.8, 1000)

    def test_linear_decay_start(self):
        """Test linear decay at start."""
        schedule = AlphaSchedule(0.8, 0.2, 1000, "linear")
        alpha = schedule.get_alpha(0)
        assert abs(alpha - 0.8) < 0.01

    def test_linear_decay_end(self):
        """Test linear decay at end."""
        schedule = AlphaSchedule(0.8, 0.2, 1000, "linear")
        alpha = schedule.get_alpha(1000)
        assert abs(alpha - 0.2) < 0.01

    def test_linear_decay_middle(self):
        """Test linear decay at midpoint."""
        schedule = AlphaSchedule(0.8, 0.2, 1000, "linear")
        alpha = schedule.get_alpha(500)
        expected = 0.8 - (0.8 - 0.2) * 0.5  # 0.5
        assert abs(alpha - expected) < 0.01

    def test_linear_decay_beyond_total(self):
        """Test that alpha stays at final value beyond total_games."""
        schedule = AlphaSchedule(0.8, 0.2, 1000, "linear")
        alpha = schedule.get_alpha(2000)
        assert abs(alpha - 0.2) < 0.01

    def test_exponential_decay_start(self):
        """Test exponential decay at start."""
        schedule = AlphaSchedule(0.8, 0.1, 1000, "exponential")
        alpha = schedule.get_alpha(0)
        assert abs(alpha - 0.8) < 0.01

    def test_exponential_decay_end(self):
        """Test exponential decay at end."""
        schedule = AlphaSchedule(0.8, 0.1, 1000, "exponential")
        alpha = schedule.get_alpha(1000)
        assert abs(alpha - 0.1) < 0.01

    def test_exponential_decay_faster_than_linear(self):
        """Test that exponential decay is faster than linear initially."""
        linear = AlphaSchedule(0.8, 0.2, 1000, "linear")
        exponential = AlphaSchedule(0.8, 0.2, 1000, "exponential")

        # At 25% through, exponential should be lower
        linear_alpha = linear.get_alpha(250)
        exp_alpha = exponential.get_alpha(250)

        assert exp_alpha < linear_alpha

    def test_invalid_schedule_type(self):
        """Test that invalid schedule type raises ValueError."""
        schedule = AlphaSchedule(0.8, 0.2, 1000, "invalid")
        with pytest.raises(ValueError, match="Unknown schedule_type"):
            schedule.get_alpha(500)


class TestAlphaConfigsFactory:
    """Test factory function and configurations."""

    def test_create_alpha_schedule_alice(self):
        """Test creating Alice's schedule."""
        schedule = create_alpha_schedule("alice", total_games=10000)
        assert schedule.alpha_initial == 0.8
        assert schedule.alpha_final == 0.5
        assert schedule.schedule_type == "linear"

    def test_create_alpha_schedule_jack(self):
        """Test creating Jack's schedule."""
        schedule = create_alpha_schedule("jack", total_games=10000)
        assert schedule.alpha_initial == 0.7
        assert schedule.alpha_final == 0.05
        assert schedule.schedule_type == "exponential"

    def test_create_alpha_schedule_invalid_agent(self):
        """Test that invalid agent ID raises ValueError."""
        with pytest.raises(ValueError, match="Unknown agent_id"):
            create_alpha_schedule("invalid_agent", total_games=10000)

    def test_all_configs_present(self):
        """Test that all 10 agents have configurations."""
        expected_agents = [
            'alice', 'bob', 'charlie', 'dee', 'ethel',
            'frankie', 'greta', 'harry', 'irene', 'jack'
        ]

        for agent_id in expected_agents:
            assert agent_id in ALPHA_CONFIGS, f"{agent_id} missing from ALPHA_CONFIGS"

    def test_all_configs_valid(self):
        """Test that all configs have valid values."""
        for agent_id, (initial, final, schedule_type) in ALPHA_CONFIGS.items():
            assert 0 <= initial <= 1, f"{agent_id} invalid initial"
            assert 0 <= final <= 1, f"{agent_id} invalid final"
            assert initial >= final, f"{agent_id} initial < final"
            assert schedule_type in ["linear", "exponential"], f"{agent_id} invalid type"

    def test_alice_stays_rule_based(self):
        """Test that Alice maintains high alpha (rule-based)."""
        schedule = create_alpha_schedule("alice", total_games=10000)

        # Even at end, Alice should have relatively high alpha
        final_alpha = schedule.get_alpha(10000)
        assert final_alpha >= 0.5

    def test_jack_becomes_chaotic(self):
        """Test that Jack's alpha drops very low (chaotic/learned)."""
        schedule = create_alpha_schedule("jack", total_games=10000)

        # At end, Jack should have very low alpha
        final_alpha = schedule.get_alpha(10000)
        assert final_alpha <= 0.1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
