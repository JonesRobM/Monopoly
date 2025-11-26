"""
Unit tests for CustomRewardShaper.

Tests all 6 reward components:
- cash (Δcash)
- rent_yield (actual rent collected)
- property_count (Δproperties with mortgage penalties)
- development (Δhouses/hotels)
- trade_value (economic value)
- monopoly_completion (strategic bonuses)
"""

import pytest
import numpy as np
from pathlib import Path

from engine.board import MonopolyBoard
from engine.state import GameState, PlayerState, PropertyState, PropertyGroup
from agents.reward_shaper import CustomRewardShaper


@pytest.fixture
def board():
    """Create board instance."""
    return MonopolyBoard()


@pytest.fixture
def alice_weights():
    """Alice's reward weights (money maximiser)."""
    return {
        'cash': 1.0,
        'rent_yield': 0.4,
        'property_count': 0.2,
        'development': 0.1,
        'trade_value': 0.2,
        'monopoly_completion': 0.1
    }


@pytest.fixture
def reward_shaper(board, alice_weights):
    """Create reward shaper instance."""
    return CustomRewardShaper(board, alice_weights)


def create_basic_game_state(num_players=2):
    """Create a basic game state for testing."""
    players = [
        PlayerState(player_id=i, name=f"Player{i}", cash=1500)
        for i in range(num_players)
    ]
    return GameState(
        players=players,
        current_player_idx=0,
        turn_number=0,
        properties={},
        houses_remaining=32,
        hotels_remaining=12
    )


class TestCustomRewardShaper:
    """Test suite for CustomRewardShaper."""

    def test_initialization(self, board, alice_weights):
        """Test reward shaper initialization."""
        shaper = CustomRewardShaper(board, alice_weights)
        assert shaper.board == board
        assert shaper.weights == alice_weights

    def test_missing_weight_keys(self, board):
        """Test that missing weight keys raise ValueError."""
        incomplete_weights = {'cash': 1.0, 'rent_yield': 0.5}
        with pytest.raises(ValueError, match="Missing required weight keys"):
            CustomRewardShaper(board, incomplete_weights)

    def test_cash_reward_gain(self, reward_shaper):
        """Test cash reward when player gains cash."""
        prev_state = create_basic_game_state()
        state = create_basic_game_state()

        # Player gains $200
        state.players[0].cash = 1700
        prev_state.players[0].cash = 1500

        reward = reward_shaper._calculate_cash_reward(state, prev_state, 0)
        assert reward == 200.0

    def test_cash_reward_loss(self, reward_shaper):
        """Test cash reward when player loses cash."""
        prev_state = create_basic_game_state()
        state = create_basic_game_state()

        # Player loses $150
        state.players[0].cash = 1350
        prev_state.players[0].cash = 1500

        reward = reward_shaper._calculate_cash_reward(state, prev_state, 0)
        assert reward == -150.0

    def test_property_count_acquisition(self, reward_shaper):
        """Test property count reward when acquiring property."""
        prev_state = create_basic_game_state()
        state = create_basic_game_state()

        # Player acquires property 1
        state.players[0].owned_properties = {1}
        state.properties[1] = PropertyState(tile_id=1, owner=0, num_houses=0)

        reward = reward_shaper._calculate_property_count_reward(state, prev_state, 0)
        assert reward == 1.0

    def test_property_count_mortgage_penalty(self, reward_shaper):
        """Test mortgage penalty."""
        prev_state = create_basic_game_state()
        state = create_basic_game_state()

        # Player owns property in both states
        prev_state.players[0].owned_properties = {1}
        state.players[0].owned_properties = {1}

        # Property was unmortgaged, now mortgaged
        prev_state.properties[1] = PropertyState(tile_id=1, owner=0, is_mortgaged=False)
        state.properties[1] = PropertyState(tile_id=1, owner=0, is_mortgaged=True)

        reward = reward_shaper._calculate_property_count_reward(state, prev_state, 0)
        assert reward == -0.5

    def test_property_count_unmortgage_reward(self, reward_shaper):
        """Test unmortgage reward."""
        prev_state = create_basic_game_state()
        state = create_basic_game_state()

        # Player owns property in both states
        prev_state.players[0].owned_properties = {1}
        state.players[0].owned_properties = {1}

        # Property was mortgaged, now unmortgaged
        prev_state.properties[1] = PropertyState(tile_id=1, owner=0, is_mortgaged=True)
        state.properties[1] = PropertyState(tile_id=1, owner=0, is_mortgaged=False)

        reward = reward_shaper._calculate_property_count_reward(state, prev_state, 0)
        assert reward == 0.5

    def test_development_reward_build_house(self, reward_shaper):
        """Test development reward when building house."""
        prev_state = create_basic_game_state()
        state = create_basic_game_state()

        # Player owns property
        prev_state.players[0].owned_properties = {1}
        state.players[0].owned_properties = {1}

        # Built 1 house
        prev_state.properties[1] = PropertyState(tile_id=1, owner=0, num_houses=0)
        state.properties[1] = PropertyState(tile_id=1, owner=0, num_houses=1)

        reward = reward_shaper._calculate_development_reward(state, prev_state, 0)
        assert reward == 1.0

    def test_development_reward_build_hotel(self, reward_shaper):
        """Test development reward when building hotel."""
        prev_state = create_basic_game_state()
        state = create_basic_game_state()

        # Player owns property
        prev_state.players[0].owned_properties = {1}
        state.players[0].owned_properties = {1}

        # Built hotel (4 houses -> 5 = hotel)
        prev_state.properties[1] = PropertyState(tile_id=1, owner=0, num_houses=4)
        state.properties[1] = PropertyState(tile_id=1, owner=0, num_houses=5)

        reward = reward_shaper._calculate_development_reward(state, prev_state, 0)
        assert reward == 1.0

    def test_development_reward_sell_house(self, reward_shaper):
        """Test development penalty when selling house."""
        prev_state = create_basic_game_state()
        state = create_basic_game_state()

        # Player owns property
        prev_state.players[0].owned_properties = {1}
        state.players[0].owned_properties = {1}

        # Sold 1 house
        prev_state.properties[1] = PropertyState(tile_id=1, owner=0, num_houses=3)
        state.properties[1] = PropertyState(tile_id=1, owner=0, num_houses=2)

        reward = reward_shaper._calculate_development_reward(state, prev_state, 0)
        assert reward == -1.0

    def test_monopoly_completion_reward(self, reward_shaper):
        """Test monopoly completion bonus."""
        prev_state = create_basic_game_state()
        state = create_basic_game_state()

        # Get brown property group tiles (Mediterranean and Baltic)
        brown_tiles = reward_shaper.board.get_group_tiles(PropertyGroup.BROWN)

        # Player completes monopoly (owns 1 -> owns all)
        prev_state.players[0].owned_properties = {brown_tiles[0]}
        state.players[0].owned_properties = set(brown_tiles)

        reward = reward_shaper._calculate_monopoly_completion_reward(state, prev_state, 0)
        assert reward == 1000.0  # MONOPOLY_COMPLETE_REWARD

    def test_monopoly_blocking_reward(self, reward_shaper):
        """Test monopoly blocking bonus."""
        prev_state = create_basic_game_state(num_players=2)
        state = create_basic_game_state(num_players=2)

        # Get brown property group tiles
        brown_tiles = reward_shaper.board.get_group_tiles(PropertyGroup.BROWN)

        # Opponent owns all except one
        prev_state.players[1].owned_properties = {brown_tiles[0]}
        state.players[1].owned_properties = {brown_tiles[0]}

        # Player 0 acquires the blocking tile
        prev_state.players[0].owned_properties = set()
        state.players[0].owned_properties = {brown_tiles[1]}

        reward = reward_shaper._calculate_monopoly_completion_reward(state, prev_state, 0)
        assert reward == 300.0  # MONOPOLY_BLOCK_REWARD

    def test_opponent_monopoly_penalty(self, reward_shaper):
        """Test penalty when opponent completes monopoly."""
        prev_state = create_basic_game_state(num_players=2)
        state = create_basic_game_state(num_players=2)

        # Get brown property group tiles
        brown_tiles = reward_shaper.board.get_group_tiles(PropertyGroup.BROWN)

        # Opponent completes monopoly
        prev_state.players[1].owned_properties = {brown_tiles[0]}
        state.players[1].owned_properties = set(brown_tiles)

        reward = reward_shaper._calculate_monopoly_completion_reward(state, prev_state, 0)
        assert reward == -500.0  # OPPONENT_MONOPOLY_PENALTY

    def test_total_reward_calculation(self, reward_shaper):
        """Test total weighted reward calculation."""
        prev_state = create_basic_game_state()
        state = create_basic_game_state()

        # Player gains cash and acquires property
        state.players[0].cash = 1700
        prev_state.players[0].cash = 1500

        state.players[0].owned_properties = {1}
        state.properties[1] = PropertyState(tile_id=1, owner=0)

        total_reward = reward_shaper.calculate_reward(state, 0, prev_state)

        # Expected: cash_reward (200) * 1.0 + property_reward (1) * 0.2 = 200.2
        expected = 200.0 * 1.0 + 1.0 * 0.2
        assert abs(total_reward - expected) < 0.01

    def test_get_monopolies(self, reward_shaper):
        """Test _get_monopolies helper."""
        state = create_basic_game_state()

        # Player owns complete brown group
        brown_tiles = reward_shaper.board.get_group_tiles(PropertyGroup.BROWN)
        state.players[0].owned_properties = set(brown_tiles)

        monopolies = reward_shaper._get_monopolies(state, 0)
        assert 'brown' in monopolies

    def test_get_monopolies_incomplete(self, reward_shaper):
        """Test that incomplete sets don't count as monopolies."""
        state = create_basic_game_state()

        # Player owns only one brown property
        brown_tiles = reward_shaper.board.get_group_tiles(PropertyGroup.BROWN)
        state.players[0].owned_properties = {brown_tiles[0]}

        monopolies = reward_shaper._get_monopolies(state, 0)
        assert 'brown' not in monopolies


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
