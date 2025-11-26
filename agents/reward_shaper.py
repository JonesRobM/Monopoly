"""
Custom reward shaping for individual agent personalities.

Each agent has a unique reward function composed of 6 weighted components:
1. cash: Change in cash (Δcash)
2. rent_yield: Actual rent collected this turn
3. property_count: Change in properties owned (with mortgage penalties)
4. development: Change in houses/hotels built
5. trade_value: Economic value of trades (property value + cash)
6. monopoly_completion: Strategic bonuses for monopoly-related actions

Each agent's priority_weights determine how these components are combined.
"""

from typing import Dict, Set, Optional, Tuple
import numpy as np

from engine.state import GameState, PlayerState, PropertyState
from engine.board import MonopolyBoard


class CustomRewardShaper:
    """
    Per-agent custom reward calculator.

    Computes rewards based on agent-specific priority weights and
    behavioral objectives. Each of the 10 agents uses the same reward
    components but with different weights.
    """

    # Monopoly completion reward magnitudes
    MONOPOLY_COMPLETE_REWARD = 1000.0
    MONOPOLY_BLOCK_REWARD = 300.0
    OPPONENT_MONOPOLY_PENALTY = -500.0

    # Mortgage penalties
    MORTGAGE_PENALTY = -0.5
    UNMORTGAGE_REWARD = 0.5

    def __init__(self, board: MonopolyBoard, priority_weights: Dict[str, float]):
        """
        Initialize custom reward shaper.

        Args:
            board: Monopoly board instance
            priority_weights: Dict with keys: cash, rent_yield, property_count,
                            development, trade_value, monopoly_completion
        """
        self.board = board
        self.weights = priority_weights

        # Validate weights
        required_keys = {
            'cash', 'rent_yield', 'property_count',
            'development', 'trade_value', 'monopoly_completion'
        }
        if not required_keys.issubset(self.weights.keys()):
            raise ValueError(f"Missing required weight keys. Need: {required_keys}")

    def calculate_reward(self, state: GameState, player_id: int,
                        prev_state: GameState) -> float:
        """
        Calculate total reward for a player given state transition.

        Args:
            state: Current game state
            player_id: ID of player to calculate reward for
            prev_state: Previous game state

        Returns:
            Total weighted reward
        """
        # Calculate each component
        cash_reward = self._calculate_cash_reward(state, prev_state, player_id)
        rent_reward = self._calculate_rent_yield_reward(state, prev_state, player_id)
        property_reward = self._calculate_property_count_reward(state, prev_state, player_id)
        development_reward = self._calculate_development_reward(state, prev_state, player_id)
        trade_reward = self._calculate_trade_value_reward(state, prev_state, player_id)
        monopoly_reward = self._calculate_monopoly_completion_reward(state, prev_state, player_id)

        # Apply weights
        total_reward = (
            self.weights['cash'] * cash_reward +
            self.weights['rent_yield'] * rent_reward +
            self.weights['property_count'] * property_reward +
            self.weights['development'] * development_reward +
            self.weights['trade_value'] * trade_reward +
            self.weights['monopoly_completion'] * monopoly_reward
        )

        return total_reward

    def _calculate_cash_reward(self, state: GameState, prev_state: GameState,
                               player_id: int) -> float:
        """
        Calculate reward from cash change (Δcash).

        Rewards/penalties for:
        - Buying properties (negative)
        - Collecting rent (positive)
        - Passing GO (positive)
        - Paying taxes (negative)

        Returns:
            Change in cash
        """
        current_cash = state.players[player_id].cash
        prev_cash = prev_state.players[player_id].cash

        return float(current_cash - prev_cash)

    def _calculate_rent_yield_reward(self, state: GameState, prev_state: GameState,
                                    player_id: int) -> float:
        """
        Calculate reward from actual rent collected this turn.

        This is inferred from cash increases that aren't from passing GO
        or other known sources. In practice, the environment should track
        rent collection explicitly.

        Note: This is a simplified implementation. A full implementation
        would track rent collection events explicitly in the game state.

        Returns:
            Estimated rent collected (positive) or paid (negative)
        """
        # TODO: This requires explicit rent tracking in game state
        # For now, return 0 - implement when game state tracks rent events
        return 0.0

    def _calculate_property_count_reward(self, state: GameState, prev_state: GameState,
                                        player_id: int) -> float:
        """
        Calculate reward from property ownership changes.

        Rewards:
        - +1 for acquiring a property
        - -1 for losing a property
        - -0.5 for mortgaging a property
        - +0.5 for unmortgaging a property

        Returns:
            Property count change reward
        """
        current_props = state.players[player_id].owned_properties
        prev_props = prev_state.players[player_id].owned_properties

        # Property acquisitions/losses
        gained_props = current_props - prev_props
        lost_props = prev_props - current_props

        reward = float(len(gained_props) - len(lost_props))

        # Check for mortgage changes
        for tile_id in current_props & prev_props:  # Properties owned in both states
            current_prop = state.properties.get(tile_id)
            prev_prop = prev_state.properties.get(tile_id)

            if current_prop and prev_prop:
                # Newly mortgaged
                if current_prop.is_mortgaged and not prev_prop.is_mortgaged:
                    reward += self.MORTGAGE_PENALTY
                # Newly unmortgaged
                elif not current_prop.is_mortgaged and prev_prop.is_mortgaged:
                    reward += self.UNMORTGAGE_REWARD

        return reward

    def _calculate_development_reward(self, state: GameState, prev_state: GameState,
                                     player_id: int) -> float:
        """
        Calculate reward from development changes (houses/hotels).

        Rewards:
        - +1 for each house built
        - -1 for each house sold
        - +1 for hotel built (counts as one development step)
        - -1 for hotel sold

        Returns:
            Development level change
        """
        reward = 0.0

        owned_props = state.players[player_id].owned_properties

        for tile_id in owned_props:
            current_prop = state.properties.get(tile_id)
            prev_prop = prev_state.properties.get(tile_id)

            if current_prop and prev_prop:
                # Change in number of houses (0-5, where 5 = hotel)
                house_delta = current_prop.num_houses - prev_prop.num_houses
                reward += float(house_delta)

        return reward

    def _calculate_trade_value_reward(self, state: GameState, prev_state: GameState,
                                     player_id: int) -> float:
        """
        Calculate reward from trade value (economic component only).

        Value = (Σ property_values_received - Σ property_values_given) + cash_delta

        Property value = purchase_price + (num_houses × house_cost)

        Note: This requires explicit trade tracking in game state.
        For now, returns 0 - implement when trades are tracked.

        Returns:
            Economic value of trades this turn
        """
        # TODO: Requires explicit trade tracking in game state
        # For now, return 0 - implement when trade system is active
        return 0.0

    def _calculate_monopoly_completion_reward(self, state: GameState,
                                             prev_state: GameState,
                                             player_id: int) -> float:
        """
        Calculate reward from monopoly-related strategic actions.

        Rewards:
        - +1000 if you completed a monopoly this turn
        - +300 if you blocked an opponent from completing a monopoly
        - -500 if an opponent completed a monopoly this turn

        Returns:
            Monopoly completion reward
        """
        reward = 0.0

        # Check if player completed a monopoly
        if self._completed_monopoly(state, prev_state, player_id):
            reward += self.MONOPOLY_COMPLETE_REWARD

        # Check if player blocked an opponent
        if self._blocked_opponent_monopoly(state, prev_state, player_id):
            reward += self.MONOPOLY_BLOCK_REWARD

        # Check if any opponent completed a monopoly
        for other_player_id in range(len(state.players)):
            if other_player_id != player_id:
                if self._completed_monopoly(state, prev_state, other_player_id):
                    reward += self.OPPONENT_MONOPOLY_PENALTY

        return reward

    def _completed_monopoly(self, state: GameState, prev_state: GameState,
                           player_id: int) -> bool:
        """
        Check if player completed a monopoly this turn.

        Returns True if player owns a complete color group now but didn't before.
        """
        current_monopolies = self._get_monopolies(state, player_id)
        prev_monopolies = self._get_monopolies(prev_state, player_id)

        return len(current_monopolies) > len(prev_monopolies)

    def _blocked_opponent_monopoly(self, state: GameState, prev_state: GameState,
                                  player_id: int) -> bool:
        """
        Check if player blocked an opponent from completing a monopoly.

        Returns True if player acquired a property that prevents an opponent
        from completing a color group.
        """
        current_props = state.players[player_id].owned_properties
        prev_props = prev_state.players[player_id].owned_properties

        # Properties gained this turn
        gained_props = current_props - prev_props

        if not gained_props:
            return False

        # Check if any gained property blocks an opponent
        for tile_id in gained_props:
            tile = self.board.get_tile(tile_id)
            if tile.property_info is None:
                continue

            property_group = tile.property_info.group
            group_tiles = self.board.get_group_tiles(property_group)

            # Check each opponent
            for other_player_id in range(len(state.players)):
                if other_player_id == player_id:
                    continue

                other_props = state.players[other_player_id].owned_properties

                # Count how many tiles of this group the opponent owns
                opponent_group_count = len(other_props & set(group_tiles))

                # If opponent owns all except this one tile, it's a block
                if opponent_group_count == len(group_tiles) - 1:
                    return True

        return False

    def _get_monopolies(self, state: GameState, player_id: int) -> Set[str]:
        """
        Get set of color groups where player owns all properties.

        Returns:
            Set of PropertyGroup names (e.g., {'red', 'orange'})
        """
        player_props = state.players[player_id].owned_properties
        monopolies = set()

        # Check each property group
        from engine.state import PropertyGroup
        for group in PropertyGroup:
            if group in [PropertyGroup.RAILROAD, PropertyGroup.UTILITY, PropertyGroup.SPECIAL]:
                continue  # Skip non-monopolizable groups

            group_tiles = self.board.get_group_tiles(group)

            # If player owns all tiles in group, it's a monopoly
            if set(group_tiles).issubset(player_props):
                monopolies.add(group.value)

        return monopolies
