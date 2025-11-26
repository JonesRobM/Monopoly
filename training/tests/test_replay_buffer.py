"""
Unit tests for PPOReplayBuffer.

Tests experience storage and batch generation.
"""

import pytest
import numpy as np
import torch
from training.replay_buffer import PPOReplayBuffer


def create_dummy_observation():
    """Create a dummy observation dictionary."""
    return {
        'property_tokens': np.random.rand(40, 8).astype(np.float32),
        'player_tokens': np.random.rand(4, 8).astype(np.float32),
        'game_token': np.random.rand(1, 5).astype(np.float32),
    }


class TestPPOReplayBuffer:
    """Test suite for PPOReplayBuffer."""

    def test_initialization(self):
        """Test buffer initialization."""
        buffer = PPOReplayBuffer(max_size=1000)
        assert buffer.max_size == 1000
        assert buffer.size() == 0

    def test_add_single_transition(self):
        """Test adding a single transition."""
        buffer = PPOReplayBuffer()

        obs = create_dummy_observation()
        buffer.add(obs, action=5, reward=1.0, value=0.5, log_prob=-0.1, done=False)

        assert buffer.size() == 1

    def test_add_multiple_transitions(self):
        """Test adding multiple transitions."""
        buffer = PPOReplayBuffer()

        for i in range(10):
            obs = create_dummy_observation()
            buffer.add(obs, action=i, reward=float(i), value=0.5,
                      log_prob=-0.1, done=False)

        assert buffer.size() == 10

    def test_episode_boundary_tracking(self):
        """Test that episode boundaries are tracked."""
        buffer = PPOReplayBuffer()

        # Add first episode (5 steps)
        for i in range(4):
            buffer.add(create_dummy_observation(), i, 1.0, 0.5, -0.1, done=False)
        buffer.add(create_dummy_observation(), 4, 1.0, 0.5, -0.1, done=True)

        # Add second episode (3 steps)
        for i in range(2):
            buffer.add(create_dummy_observation(), i, 1.0, 0.5, -0.1, done=False)
        buffer.add(create_dummy_observation(), 2, 1.0, 0.5, -0.1, done=True)

        assert buffer.num_episodes() == 2

    def test_max_size_overflow(self):
        """Test that buffer respects max_size."""
        buffer = PPOReplayBuffer(max_size=5)

        # Add 10 transitions
        for i in range(10):
            buffer.add(create_dummy_observation(), i, float(i), 0.5, -0.1, done=False)

        # Should only keep last 5
        assert buffer.size() == 5

    def test_get_batch_shape(self):
        """Test that get_batch returns correct shapes."""
        buffer = PPOReplayBuffer()

        # Add some transitions
        for i in range(10):
            obs = create_dummy_observation()
            buffer.add(obs, action=i, reward=float(i), value=0.5,
                      log_prob=-0.1, done=(i == 9))

        batch = buffer.get_batch(batch_size=5)

        assert batch['property_tokens'].shape == (5, 40, 8)
        assert batch['player_tokens'].shape == (5, 4, 8)
        assert batch['game_token'].shape == (5, 1, 5)
        assert batch['actions'].shape == (5,)
        assert batch['old_log_probs'].shape == (5,)
        assert batch['rewards'].shape == (5,)
        assert batch['values'].shape == (5,)
        assert batch['advantages'].shape == (5,)
        assert batch['returns'].shape == (5,)

    def test_get_batch_full_buffer(self):
        """Test getting full buffer as batch."""
        buffer = PPOReplayBuffer()

        # Add 10 transitions
        for i in range(10):
            buffer.add(create_dummy_observation(), i, float(i), 0.5, -0.1, done=False)

        batch = buffer.get_batch(batch_size=None)

        assert batch['actions'].shape[0] == 10

    def test_gae_computation(self):
        """Test GAE computation."""
        buffer = PPOReplayBuffer()

        # Add simple episode with known rewards and values
        rewards = torch.FloatTensor([1.0, 2.0, 3.0, 0.0])
        values = torch.FloatTensor([0.5, 1.0, 1.5, 0.0])
        dones = torch.FloatTensor([0.0, 0.0, 0.0, 1.0])

        advantages, returns = buffer._compute_gae(
            rewards, values, dones,
            gamma=0.99, gae_lambda=0.95
        )

        assert advantages.shape == rewards.shape
        assert returns.shape == rewards.shape

        # Returns should be advantages + values
        assert torch.allclose(returns, advantages + values, atol=1e-5)

    def test_clear_buffer(self):
        """Test clearing the buffer."""
        buffer = PPOReplayBuffer()

        # Add transitions
        for i in range(10):
            buffer.add(create_dummy_observation(), i, float(i), 0.5, -0.1, done=False)

        assert buffer.size() == 10

        buffer.clear()

        assert buffer.size() == 0
        assert buffer.num_episodes() == 0

    def test_empty_buffer_get_batch_raises(self):
        """Test that getting batch from empty buffer raises error."""
        buffer = PPOReplayBuffer()

        with pytest.raises(ValueError, match="Buffer is empty"):
            buffer.get_batch()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
