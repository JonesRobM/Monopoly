"""
Model architecture for Monopoly RL agents.

Structured transformer architecture that processes game state as sequences
of entity tokens (properties, players, game state) with self-attention.

Components:
- StateTokenizer: Converts game state to structured token sequences
- MonopolyTransformer: Structured transformer with actor-critic heads
"""

from models.tokenizer import StateTokenizer
from models.transformer import MonopolyTransformer, create_model

__all__ = [
    'StateTokenizer',
    'MonopolyTransformer',
    'create_model',
]
