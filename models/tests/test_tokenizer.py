"""
Unit tests for StateTokenizer.

Tests tokenization of game state into structured sequences.
"""

import pytest
import numpy as np
from engine.board import MonopolyBoard
from engine.state import GameState, PlayerState, PropertyState, TileType
from models.tokenizer import StateTokenizer


@pytest.fixture
def board():
    """Create board instance."""
    return MonopolyBoard()


@pytest.fixture
def tokenizer(board):
    """Create tokenizer instance."""
    return StateTokenizer(board, num_players=4)


def create_test_game_state(num_players=4):
    """Create a test game state."""
    players = [
        PlayerState(
            player_id=i,
            name=f"Player{i}",
            cash=1500 - i * 100,  # Varying cash
            position=i * 10,  # Different positions
            is_in_jail=(i == 2),  # Player 2 in jail
            jail_turns=(3 if i == 2 else 0)
        )
        for i in range(num_players)
    ]

    # Add some properties
    properties = {
        1: PropertyState(tile_id=1, owner=0, num_houses=2, is_mortgaged=False),
        3: PropertyState(tile_id=3, owner=1, num_houses=0, is_mortgaged=True),
        6: PropertyState(tile_id=6, owner=0, num_houses=4, is_mortgaged=False),
    }

    players[0].owned_properties = {1, 6}
    players[1].owned_properties = {3}

    return GameState(
        players=players,
        current_player_idx=0,
        turn_number=42,
        doubles_count=1,
        properties=properties,
        houses_remaining=25,
        hotels_remaining=10
    )


class TestStateTokenizer:
    """Test suite for StateTokenizer."""

    def test_initialization(self, board):
        """Test tokenizer initialization."""
        tokenizer = StateTokenizer(board, num_players=4, max_cash=10000.0)
        assert tokenizer.board == board
        assert tokenizer.num_players == 4
        assert tokenizer.max_cash == 10000.0

    def test_feature_dimensions(self, tokenizer):
        """Test that feature dimensions are calculated correctly."""
        prop_dim, player_dim, game_dim = tokenizer.get_feature_dims()
        assert prop_dim == 8  # Expected property feature dim
        assert player_dim == 8  # Expected player feature dim
        assert game_dim == 5  # Expected game feature dim

    def test_property_tokens_shape(self, tokenizer):
        """Test property tokens have correct shape."""
        state = create_test_game_state()
        property_tokens = tokenizer.tokenize_properties(state)

        assert property_tokens.shape == (40, 8)
        assert property_tokens.dtype == np.float32

    def test_property_tokens_normalization(self, tokenizer):
        """Test that property token values are normalized."""
        state = create_test_game_state()
        property_tokens = tokenizer.tokenize_properties(state)

        # All values should be in [0, 1]
        assert np.all(property_tokens >= 0)
        assert np.all(property_tokens <= 1)

    def test_property_owner_encoding(self, tokenizer):
        """Test property owner encoding."""
        state = create_test_game_state()
        property_tokens = tokenizer.tokenize_properties(state)

        # Tile 1 owned by player 0
        # owner_id = 1 (player 0 + 1) / 7 ≈ 0.143
        assert property_tokens[1, 0] > 0  # Has owner
        assert property_tokens[1, 0] < 0.3  # Owner 0

        # Tile 0 (GO) not owned
        assert property_tokens[0, 0] == 0  # No owner

    def test_property_houses_encoding(self, tokenizer):
        """Test property houses encoding."""
        state = create_test_game_state()
        property_tokens = tokenizer.tokenize_properties(state)

        # Tile 1 has 2 houses (2/5 = 0.4)
        assert abs(property_tokens[1, 1] - 0.4) < 0.01

        # Tile 6 has 4 houses (4/5 = 0.8)
        assert abs(property_tokens[6, 1] - 0.8) < 0.01

    def test_property_mortgage_encoding(self, tokenizer):
        """Test property mortgage encoding."""
        state = create_test_game_state()
        property_tokens = tokenizer.tokenize_properties(state)

        # Tile 3 is mortgaged
        assert property_tokens[3, 2] == 1.0

        # Tile 1 is not mortgaged
        assert property_tokens[1, 2] == 0.0

    def test_player_tokens_shape(self, tokenizer):
        """Test player tokens have correct shape."""
        state = create_test_game_state()
        player_tokens = tokenizer.tokenize_players(state, observing_player_id=0)

        assert player_tokens.shape == (4, 8)
        assert player_tokens.dtype == np.float32

    def test_player_tokens_normalization(self, tokenizer):
        """Test that player token values are normalized."""
        state = create_test_game_state()
        player_tokens = tokenizer.tokenize_players(state, observing_player_id=0)

        # All values should be in [0, 1]
        assert np.all(player_tokens >= 0)
        assert np.all(player_tokens <= 1)

    def test_player_cash_encoding(self, tokenizer):
        """Test player cash encoding."""
        state = create_test_game_state()
        player_tokens = tokenizer.tokenize_players(state, observing_player_id=0)

        # Player 0 has $1500 cash
        expected = min(1500 / 10000.0, 1.0)  # 0.15
        assert abs(player_tokens[0, 0] - expected) < 0.01

    def test_player_jail_encoding(self, tokenizer):
        """Test player jail encoding."""
        state = create_test_game_state()
        player_tokens = tokenizer.tokenize_players(state, observing_player_id=0)

        # Player 2 is in jail
        assert player_tokens[2, 2] == 1.0  # is_in_jail
        assert player_tokens[2, 3] == 1.0  # jail_turns (3/3 = 1.0)

        # Player 0 not in jail
        assert player_tokens[0, 2] == 0.0

    def test_player_current_player_flag(self, tokenizer):
        """Test current player identification flag."""
        state = create_test_game_state()
        player_tokens = tokenizer.tokenize_players(state, observing_player_id=1)

        # Player 1 is observing, so should have flag set
        assert player_tokens[1, 6] == 1.0

        # Others should not
        assert player_tokens[0, 6] == 0.0
        assert player_tokens[2, 6] == 0.0

    def test_game_token_shape(self, tokenizer):
        """Test game token has correct shape."""
        state = create_test_game_state()
        game_token = tokenizer.tokenize_game(state)

        assert game_token.shape == (1, 5)
        assert game_token.dtype == np.float32

    def test_game_token_turn_encoding(self, tokenizer):
        """Test turn number encoding."""
        state = create_test_game_state()
        game_token = tokenizer.tokenize_game(state)

        # Turn 42 / 1000 = 0.042
        expected = min(42 / 1000.0, 1.0)
        assert abs(game_token[0, 0] - expected) < 0.01

    def test_game_token_doubles_encoding(self, tokenizer):
        """Test doubles count encoding."""
        state = create_test_game_state()
        game_token = tokenizer.tokenize_game(state)

        # Doubles count = 1, normalized by 3 -> 0.333
        expected = 1 / 3.0
        assert abs(game_token[0, 1] - expected) < 0.01

    def test_full_tokenization(self, tokenizer):
        """Test full tokenization pipeline."""
        state = create_test_game_state()
        property_tokens, player_tokens, game_token = tokenizer.tokenize(state, 0)

        assert property_tokens.shape == (40, 8)
        assert player_tokens.shape == (4, 8)
        assert game_token.shape == (1, 5)

    def test_sequence_length(self, tokenizer):
        """Test total sequence length calculation."""
        seq_len = tokenizer.get_total_sequence_length()
        assert seq_len == 40 + 4 + 1  # 45 tokens for 4-player game

    def test_variable_num_players(self, board):
        """Test tokenizer with different number of players."""
        for num_players in [2, 4, 6]:
            tokenizer = StateTokenizer(board, num_players=num_players)

            players = [PlayerState(player_id=i, name=f"P{i}") for i in range(num_players)]
            state = GameState(players=players, properties={})

            player_tokens = tokenizer.tokenize_players(state, 0)
            assert player_tokens.shape[0] == num_players

            seq_len = tokenizer.get_total_sequence_length()
            assert seq_len == 40 + num_players + 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
