"""
PPO (Proximal Policy Optimization) trainer.

Implements PPO algorithm for updating agent models:
- Clipped surrogate objective
- Value function loss
- Entropy bonus
- Multiple epochs per batch

Each agent has its own PPOTrainer instance that updates its model
using experiences from its replay buffer.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import Dict, Optional
from models.transformer import MonopolyTransformer


class PPOTrainer:
    """
    PPO trainer for a single agent's model.

    Performs PPO updates using experiences from agent's replay buffer.
    """

    def __init__(self, model: MonopolyTransformer,
                 learning_rate: float = 3e-4,
                 clip_epsilon: float = 0.2,
                 value_coef: float = 0.5,
                 entropy_coef: float = 0.01,
                 max_grad_norm: float = 0.5,
                 num_epochs: int = 4,
                 minibatch_size: int = 64):
        """
        Initialize PPO trainer.

        Args:
            model: MonopolyTransformer model to train
            learning_rate: Learning rate for optimizer
            clip_epsilon: PPO clipping parameter
            value_coef: Coefficient for value loss
            entropy_coef: Coefficient for entropy bonus
            max_grad_norm: Maximum gradient norm for clipping
            num_epochs: Number of epochs per PPO update
            minibatch_size: Size of minibatches for updates
        """
        self.model = model
        self.clip_epsilon = clip_epsilon
        self.value_coef = value_coef
        self.entropy_coef = entropy_coef
        self.max_grad_norm = max_grad_norm
        self.num_epochs = num_epochs
        self.minibatch_size = minibatch_size

        # Optimizer
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)

        # Training statistics
        self.total_updates = 0
        self.policy_losses = []
        self.value_losses = []
        self.entropy_losses = []

    def update(self, batch: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """
        Perform PPO update on a batch of experiences.

        Args:
            batch: Dictionary with:
                - property_tokens: (batch, 40, property_feature_dim)
                - player_tokens: (batch, num_players, player_feature_dim)
                - game_token: (batch, 1, game_feature_dim)
                - actions: (batch,)
                - old_log_probs: (batch,)
                - advantages: (batch,)
                - returns: (batch,)

        Returns:
            Dictionary with loss statistics
        """
        batch_size = batch['property_tokens'].size(0)

        # Normalize advantages
        advantages = batch['advantages']
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        # Statistics for logging
        epoch_policy_losses = []
        epoch_value_losses = []
        epoch_entropy_losses = []

        # Multiple epochs of updates
        for epoch in range(self.num_epochs):
            # Create minibatches
            indices = np.arange(batch_size)
            np.random.shuffle(indices)

            for start in range(0, batch_size, self.minibatch_size):
                end = min(start + self.minibatch_size, batch_size)
                mb_indices = indices[start:end]

                # Extract minibatch
                mb_property_tokens = batch['property_tokens'][mb_indices]
                mb_player_tokens = batch['player_tokens'][mb_indices]
                mb_game_token = batch['game_token'][mb_indices]
                mb_actions = batch['actions'][mb_indices]
                mb_old_log_probs = batch['old_log_probs'][mb_indices]
                mb_advantages = advantages[mb_indices]
                mb_returns = batch['returns'][mb_indices]

                # Forward pass
                action_logits, values = self.model(
                    mb_property_tokens,
                    mb_player_tokens,
                    mb_game_token
                )

                # Compute log probabilities
                log_probs = torch.log_softmax(action_logits, dim=-1)
                mb_log_probs = log_probs.gather(-1, mb_actions.unsqueeze(-1)).squeeze(-1)

                # Compute probability ratio
                ratio = torch.exp(mb_log_probs - mb_old_log_probs)

                # Clipped surrogate loss
                surr1 = ratio * mb_advantages
                surr2 = torch.clamp(ratio, 1.0 - self.clip_epsilon, 1.0 + self.clip_epsilon) * mb_advantages
                policy_loss = -torch.min(surr1, surr2).mean()

                # Value loss
                value_loss = 0.5 * ((values.squeeze(-1) - mb_returns) ** 2).mean()

                # Entropy bonus
                probs = torch.softmax(action_logits, dim=-1)
                entropy = -(probs * log_probs).sum(dim=-1).mean()
                entropy_loss = -self.entropy_coef * entropy

                # Total loss
                total_loss = policy_loss + self.value_coef * value_loss + entropy_loss

                # Backpropagation
                self.optimizer.zero_grad()
                total_loss.backward()

                # Gradient clipping
                nn.utils.clip_grad_norm_(self.model.parameters(), self.max_grad_norm)

                self.optimizer.step()

                # Record losses
                epoch_policy_losses.append(policy_loss.item())
                epoch_value_losses.append(value_loss.item())
                epoch_entropy_losses.append(-entropy_loss.item())

        self.total_updates += 1

        # Average losses over all epochs
        stats = {
            'policy_loss': np.mean(epoch_policy_losses),
            'value_loss': np.mean(epoch_value_losses),
            'entropy': np.mean(epoch_entropy_losses),
            'total_updates': self.total_updates
        }

        return stats

    def save_checkpoint(self, filepath: str):
        """
        Save model and optimizer state.

        Args:
            filepath: Path to save checkpoint
        """
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'total_updates': self.total_updates,
        }
        torch.save(checkpoint, filepath)

    def load_checkpoint(self, filepath: str):
        """
        Load model and optimizer state.

        Args:
            filepath: Path to load checkpoint from
        """
        checkpoint = torch.load(filepath)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.total_updates = checkpoint.get('total_updates', 0)
