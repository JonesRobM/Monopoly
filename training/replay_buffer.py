"""
PPO Replay Buffer for experience storage.

Stores trajectories from game episodes for PPO updates. Each agent
has its own separate replay buffer.

Stores:
- Observations (tokenized state)
- Actions taken
- Rewards received (custom per-agent rewards)
- Value estimates
- Log probabilities
- Done flags
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
import torch


class PPOReplayBuffer:
    """
    Replay buffer for PPO algorithm.

    Stores experience from multiple game episodes and provides batches
    for PPO updates. Implements Generalized Advantage Estimation (GAE).
    """

    def __init__(self, max_size: int = 10000):
        """
        Initialize replay buffer.

        Args:
            max_size: Maximum number of transitions to store
        """
        self.max_size = max_size

        # Storage
        self.observations: List[Dict[str, np.ndarray]] = []
        self.actions: List[int] = []
        self.rewards: List[float] = []
        self.values: List[float] = []
        self.log_probs: List[float] = []
        self.dones: List[bool] = []

        # Episode boundaries
        self.episode_starts: List[int] = [0]

    def add(self, observation: Dict[str, np.ndarray], action: int,
            reward: float, value: float, log_prob: float, done: bool):
        """
        Add a transition to the buffer.

        Args:
            observation: Dictionary with property_tokens, player_tokens, game_token
            action: Action taken
            reward: Reward received
            value: Value estimate from critic
            log_prob: Log probability of action
            done: Whether episode ended
        """
        if len(self.observations) >= self.max_size:
            # Remove oldest transition
            self.observations.pop(0)
            self.actions.pop(0)
            self.rewards.pop(0)
            self.values.pop(0)
            self.log_probs.pop(0)
            self.dones.pop(0)

        self.observations.append(observation)
        self.actions.append(action)
        self.rewards.append(reward)
        self.values.append(value)
        self.log_probs.append(log_prob)
        self.dones.append(done)

        if done:
            self.episode_starts.append(len(self.observations))

    def get_batch(self, batch_size: Optional[int] = None) -> Dict[str, torch.Tensor]:
        """
        Get a batch of experiences for training.

        Args:
            batch_size: If None, return all experiences

        Returns:
            Dictionary with tensors for training:
            - property_tokens: (batch, 40, property_feature_dim)
            - player_tokens: (batch, num_players, player_feature_dim)
            - game_token: (batch, 1, game_feature_dim)
            - actions: (batch,)
            - old_log_probs: (batch,)
            - rewards: (batch,)
            - values: (batch,)
            - advantages: (batch,)
            - returns: (batch,)
            - dones: (batch,)
        """
        if len(self.observations) == 0:
            raise ValueError("Buffer is empty")

        # Get all or sample
        if batch_size is None or batch_size >= len(self.observations):
            indices = list(range(len(self.observations)))
        else:
            indices = np.random.choice(len(self.observations), batch_size, replace=False)

        # Extract observations
        property_tokens = []
        player_tokens = []
        game_tokens = []

        for idx in indices:
            obs = self.observations[idx]
            property_tokens.append(obs['property_tokens'])
            player_tokens.append(obs['player_tokens'])
            game_tokens.append(obs['game_token'])

        # Convert to tensors
        batch = {
            'property_tokens': torch.FloatTensor(np.array(property_tokens)),
            'player_tokens': torch.FloatTensor(np.array(player_tokens)),
            'game_token': torch.FloatTensor(np.array(game_tokens)),
            'actions': torch.LongTensor([self.actions[i] for i in indices]),
            'old_log_probs': torch.FloatTensor([self.log_probs[i] for i in indices]),
            'rewards': torch.FloatTensor([self.rewards[i] for i in indices]),
            'values': torch.FloatTensor([self.values[i] for i in indices]),
            'dones': torch.FloatTensor([float(self.dones[i]) for i in indices]),
        }

        # Compute advantages and returns using GAE
        advantages, returns = self._compute_gae(
            torch.FloatTensor(self.rewards),
            torch.FloatTensor(self.values),
            torch.FloatTensor([float(d) for d in self.dones]),
            gamma=0.99,
            gae_lambda=0.95
        )

        batch['advantages'] = advantages[indices]
        batch['returns'] = returns[indices]

        return batch

    def _compute_gae(self, rewards: torch.Tensor, values: torch.Tensor,
                    dones: torch.Tensor, gamma: float = 0.99,
                    gae_lambda: float = 0.95) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Compute Generalized Advantage Estimation (GAE).

        Args:
            rewards: Reward tensor (T,)
            values: Value estimates (T,)
            dones: Done flags (T,)
            gamma: Discount factor
            gae_lambda: GAE lambda parameter

        Returns:
            Tuple of (advantages, returns)
        """
        T = len(rewards)
        advantages = torch.zeros(T)
        returns = torch.zeros(T)

        # Compute advantages using GAE
        gae = 0
        for t in reversed(range(T)):
            if t == T - 1:
                next_value = 0
            else:
                next_value = values[t + 1]

            # TD error
            delta = rewards[t] + gamma * next_value * (1 - dones[t]) - values[t]

            # GAE
            gae = delta + gamma * gae_lambda * (1 - dones[t]) * gae
            advantages[t] = gae

        # Returns = advantages + values
        returns = advantages + values

        return advantages, returns

    def clear(self):
        """Clear all stored experiences."""
        self.observations.clear()
        self.actions.clear()
        self.rewards.clear()
        self.values.clear()
        self.log_probs.clear()
        self.dones.clear()
        self.episode_starts = [0]

    def size(self) -> int:
        """Get number of transitions in buffer."""
        return len(self.observations)

    def num_episodes(self) -> int:
        """Get number of complete episodes in buffer."""
        return len(self.episode_starts) - 1
