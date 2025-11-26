"""
Structured Transformer architecture for Monopoly RL.

Processes game state as sequences of entity tokens (properties, players, game)
using multi-head self-attention. Each entity type is embedded to a common
d_model dimension and processed through transformer layers.

Architecture:
- Input: 45-47 tokens (40 properties + 4-6 players + 1 game state)
- Token embeddings: Project features to d_model=128
- Positional encoding: For properties (board position matters)
- 3 Transformer encoder layers (4 attention heads each)
- Attention pooling: Aggregate sequence to single vector
- Actor head: 562 action logits
- Critic head: 1 value estimate
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Tuple, Optional
import math


class PositionalEncoding(nn.Module):
    """
    Sinusoidal positional encoding for board positions.

    Uses standard transformer positional encoding formula.
    """

    def __init__(self, d_model: int, max_positions: int = 40):
        """
        Initialize positional encoding.

        Args:
            d_model: Model dimension
            max_positions: Maximum number of positions (40 tiles)
        """
        super().__init__()

        # Create positional encoding matrix
        pe = torch.zeros(max_positions, d_model)
        position = torch.arange(0, max_positions, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))

        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)

        self.register_buffer('pe', pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Add positional encoding to input.

        Args:
            x: Input tensor (batch, seq_len, d_model)

        Returns:
            Input with positional encoding added (batch, seq_len, d_model)
        """
        seq_len = x.size(1)
        return x + self.pe[:seq_len, :].unsqueeze(0)


class AttentionPooling(nn.Module):
    """
    Learnable attention-based pooling to aggregate sequence.

    Computes attention weights over sequence and returns weighted sum.
    """

    def __init__(self, d_model: int):
        """
        Initialize attention pooling.

        Args:
            d_model: Model dimension
        """
        super().__init__()
        self.attention_weights = nn.Linear(d_model, 1)

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Pool sequence using learned attention.

        Args:
            x: Input sequence (batch, seq_len, d_model)
            mask: Optional mask (batch, seq_len) - 1 for valid, 0 for padding

        Returns:
            Pooled vector (batch, d_model)
        """
        # Compute attention scores
        scores = self.attention_weights(x).squeeze(-1)  # (batch, seq_len)

        # Apply mask if provided
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)

        # Softmax to get attention weights
        weights = F.softmax(scores, dim=1)  # (batch, seq_len)

        # Weighted sum
        pooled = torch.sum(x * weights.unsqueeze(-1), dim=1)  # (batch, d_model)

        return pooled


class MonopolyTransformer(nn.Module):
    """
    Structured transformer model for Monopoly.

    Processes game state as structured token sequences with self-attention.
    Outputs action logits and value estimate for actor-critic RL.
    """

    def __init__(self, property_feature_dim: int = 8,
                 player_feature_dim: int = 8,
                 game_feature_dim: int = 5,
                 d_model: int = 128,
                 nhead: int = 4,
                 num_layers: int = 3,
                 dim_feedforward: int = 512,
                 dropout: float = 0.1,
                 num_actions: int = 562,
                 max_players: int = 6):
        """
        Initialize Monopoly transformer.

        Args:
            property_feature_dim: Dimension of property token features
            player_feature_dim: Dimension of player token features
            game_feature_dim: Dimension of game token features
            d_model: Model dimension (embedding size)
            nhead: Number of attention heads
            num_layers: Number of transformer layers
            dim_feedforward: Dimension of feedforward network
            dropout: Dropout probability
            num_actions: Number of discrete actions (562)
            max_players: Maximum number of players (for padding)
        """
        super().__init__()

        self.d_model = d_model
        self.num_actions = num_actions
        self.max_players = max_players

        # Token embedding layers (project features to d_model)
        self.property_embed = nn.Linear(property_feature_dim, d_model)
        self.player_embed = nn.Linear(player_feature_dim, d_model)
        self.game_embed = nn.Linear(game_feature_dim, d_model)

        # Positional encoding for properties (board position matters)
        self.positional_encoding = PositionalEncoding(d_model, max_positions=40)

        # Transformer encoder layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            activation='relu',
            batch_first=True  # (batch, seq, feature) format
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer,
            num_layers=num_layers
        )

        # Attention pooling to aggregate sequence
        self.attention_pooling = AttentionPooling(d_model)

        # Actor head (policy)
        self.actor_head = nn.Sequential(
            nn.Linear(d_model, 256),
            nn.ReLU(),
            nn.Linear(256, num_actions)
        )

        # Critic head (value function)
        self.critic_head = nn.Sequential(
            nn.Linear(d_model, 256),
            nn.ReLU(),
            nn.Linear(256, 1)
        )

        # Initialize weights
        self.apply(self._init_weights)

    def _init_weights(self, module):
        """Initialize model weights."""
        if isinstance(module, nn.Linear):
            nn.init.xavier_uniform_(module.weight)
            if module.bias is not None:
                nn.init.zeros_(module.bias)

    def forward(self, property_tokens: torch.Tensor,
                player_tokens: torch.Tensor,
                game_token: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass.

        Args:
            property_tokens: Property tokens (batch, 40, property_feature_dim)
            player_tokens: Player tokens (batch, num_players, player_feature_dim)
            game_token: Game token (batch, 1, game_feature_dim)

        Returns:
            Tuple of (action_logits, value):
            - action_logits: (batch, num_actions)
            - value: (batch, 1)
        """
        batch_size = property_tokens.size(0)
        num_players = player_tokens.size(1)

        # Embed tokens to d_model
        prop_embedded = self.property_embed(property_tokens)  # (batch, 40, d_model)
        player_embedded = self.player_embed(player_tokens)    # (batch, num_players, d_model)
        game_embedded = self.game_embed(game_token)           # (batch, 1, d_model)

        # Add positional encoding to properties (board position matters)
        prop_embedded = self.positional_encoding(prop_embedded)

        # Concatenate all tokens into single sequence
        # Sequence: [40 properties | num_players players | 1 game]
        all_tokens = torch.cat([prop_embedded, player_embedded, game_embedded], dim=1)
        # Shape: (batch, 41 + num_players, d_model)

        # Create attention mask (no masking for now - all tokens attend to all)
        # For variable num_players, we'd mask padded player slots
        seq_len = all_tokens.size(1)

        # Transformer encoder
        encoded = self.transformer_encoder(all_tokens)  # (batch, seq_len, d_model)

        # Attention pooling to aggregate sequence
        pooled = self.attention_pooling(encoded)  # (batch, d_model)

        # Actor-Critic heads
        action_logits = self.actor_head(pooled)  # (batch, num_actions)
        value = self.critic_head(pooled)         # (batch, 1)

        return action_logits, value

    def get_action_and_value(self, property_tokens: torch.Tensor,
                            player_tokens: torch.Tensor,
                            game_token: torch.Tensor,
                            action_mask: Optional[torch.Tensor] = None,
                            deterministic: bool = False) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Get action, log probability, and value estimate.

        Args:
            property_tokens: Property tokens (batch, 40, property_feature_dim)
            player_tokens: Player tokens (batch, num_players, player_feature_dim)
            game_token: Game token (batch, 1, game_feature_dim)
            action_mask: Legal action mask (batch, num_actions)
            deterministic: If True, return argmax action

        Returns:
            Tuple of (action, log_prob, value):
            - action: (batch,)
            - log_prob: (batch,)
            - value: (batch, 1)
        """
        action_logits, value = self.forward(property_tokens, player_tokens, game_token)

        # Apply action mask (set illegal actions to -inf)
        if action_mask is not None:
            masked_logits = action_logits + (action_mask - 1) * 1e10
        else:
            masked_logits = action_logits

        # Get action distribution
        probs = F.softmax(masked_logits, dim=-1)

        if deterministic:
            # Take argmax
            action = torch.argmax(probs, dim=-1)
        else:
            # Sample from distribution
            action = torch.multinomial(probs, num_samples=1).squeeze(-1)

        # Compute log probability
        log_probs = F.log_softmax(masked_logits, dim=-1)
        log_prob = log_probs.gather(-1, action.unsqueeze(-1)).squeeze(-1)

        return action, log_prob, value

    def get_action_logits(self, property_tokens: torch.Tensor,
                         player_tokens: torch.Tensor,
                         game_token: torch.Tensor) -> torch.Tensor:
        """
        Get action logits only (for use in RLAgent).

        Args:
            property_tokens: Property tokens (batch, 40, property_feature_dim)
            player_tokens: Player tokens (batch, num_players, player_feature_dim)
            game_token: Game token (batch, 1, game_feature_dim)

        Returns:
            Action logits (batch, num_actions)
        """
        action_logits, _ = self.forward(property_tokens, player_tokens, game_token)
        return action_logits

    def get_value(self, property_tokens: torch.Tensor,
                 player_tokens: torch.Tensor,
                 game_token: torch.Tensor) -> torch.Tensor:
        """
        Get value estimate only.

        Args:
            property_tokens: Property tokens (batch, 40, property_feature_dim)
            player_tokens: Player tokens (batch, num_players, player_feature_dim)
            game_token: Game token (batch, 1, game_feature_dim)

        Returns:
            Value estimate (batch, 1)
        """
        _, value = self.forward(property_tokens, player_tokens, game_token)
        return value


def create_model(num_players: int = 4, d_model: int = 128, nhead: int = 4,
                num_layers: int = 3) -> MonopolyTransformer:
    """
    Factory function to create Monopoly transformer model.

    Args:
        num_players: Number of players in game
        d_model: Model dimension
        nhead: Number of attention heads
        num_layers: Number of transformer layers

    Returns:
        MonopolyTransformer instance
    """
    return MonopolyTransformer(
        property_feature_dim=8,
        player_feature_dim=8,
        game_feature_dim=5,
        d_model=d_model,
        nhead=nhead,
        num_layers=num_layers,
        num_actions=562,
        max_players=num_players
    )
