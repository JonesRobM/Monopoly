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
                        prev_state: GameState, action_type=None) -> float:
        """
        Calculate total reward for a player given state transition.

        Args:
            state: Current game state
            player_id: ID of player to calculate reward for
            prev_state: Previous game state
            action_type: Optional action type to apply action-specific rewards

        Returns:
            Total weighted reward (clipped to [-10, 10] for stability)
        """
        # Calculate sparse reward components (original large-scale rewards)
        cash_reward = self._calculate_cash_reward(state, prev_state, player_id)
        rent_reward = self._calculate_rent_yield_reward(state, prev_state, player_id)
        property_reward = self._calculate_property_count_reward(state, prev_state, player_id)
        development_reward = self._calculate_development_reward(state, prev_state, player_id)
        trade_reward = self._calculate_trade_value_reward(state, prev_state, player_id)
        monopoly_reward = self._calculate_monopoly_completion_reward(state, prev_state, player_id)

        # Apply weights to sparse components
        sparse_reward = (
            self.weights['cash'] * cash_reward +
            self.weights['rent_yield'] * rent_reward +
            self.weights['property_count'] * property_reward +
            self.weights['development'] * development_reward +
            self.weights['trade_value'] * trade_reward +
            self.weights['monopoly_completion'] * monopoly_reward
        )

        # DENSE REWARD SHAPING: Add continuous feedback every step
        dense_reward = self._calculate_dense_step_reward(state, prev_state, player_id)

        # Combine sparse and dense rewards
        total_reward = sparse_reward + dense_reward

        # Action cost: penalty for each action to encourage turn efficiency
        # This prevents agents from taking unlimited actions per turn
        # END_TURN and forced actions (ROLL_DICE, etc.) have no penalty
        from engine.actions import ActionType
        if action_type and action_type not in [ActionType.END_TURN, ActionType.ROLL_DICE,
                                                 ActionType.ROLL_FOR_JAIL, ActionType.NOOP]:
            # CURRICULUM FIX: Stronger penalty for optional actions (0.05 -> 0.3)
            # Encourages agents to END_TURN quickly rather than taking many optional actions
            total_reward -= 0.3

        # Bonus for ending turn efficiently
        if action_type == ActionType.END_TURN:
            total_reward += 0.5

        # CRITICAL FIX: Clip rewards to stable range for PPO
        # Prevents massive reward swings from breaking learning
        clipped_reward = float(max(-10.0, min(10.0, total_reward)))

        return clipped_reward

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

    def _calculate_dense_step_reward(self, state: GameState, prev_state: GameState,
                                     player_id: int) -> float:
        """
        Calculate dense reward for continuous learning signal.

        Provides small rewards every step to help with credit assignment.
        These rewards are much smaller than sparse event rewards but more frequent.

        Components:
        - Cash ratio improvement (normalized by total cash in game)
        - Property portfolio value increase
        - Strategic positioning (owning properties in valuable groups)
        - Monopoly progress (number of properties in near-complete color sets)

        Returns:
            Dense reward value (typically in [-1, +1] range)
        """
        dense_reward = 0.0

        # 1. Relative cash position improvement
        # Compare our cash ratio to average (normalized 0-1)
        current_player = state.players[player_id]
        prev_player = prev_state.players[player_id]

        total_cash_current = sum(p.cash for p in state.players if not p.is_bankrupt)
        total_cash_prev = sum(p.cash for p in prev_state.players if not p.is_bankrupt)

        if total_cash_current > 0 and total_cash_prev > 0:
            cash_ratio_now = current_player.cash / total_cash_current
            cash_ratio_prev = prev_player.cash / total_cash_prev
            cash_improvement = (cash_ratio_now - cash_ratio_prev) * 2.0  # Scale to ~[-0.5, +0.5]
            dense_reward += cash_improvement

        # 2. Property portfolio value (weighted by monopoly potential)
        portfolio_value_now = self._calculate_portfolio_value(state, player_id)
        portfolio_value_prev = self._calculate_portfolio_value(prev_state, player_id)
        portfolio_improvement = (portfolio_value_now - portfolio_value_prev) * 0.1
        dense_reward += portfolio_improvement

        # 3. Monopoly progress reward (encourage moving toward monopolies)
        monopoly_progress_now = self._calculate_monopoly_progress(state, player_id)
        monopoly_progress_prev = self._calculate_monopoly_progress(prev_state, player_id)
        progress_delta = (monopoly_progress_now - monopoly_progress_prev) * 0.5
        dense_reward += progress_delta

        # 4. Strategic positioning: small bonus if owning properties opponents land on
        # (approximated by owning diverse property groups)
        diversity_now = len(self._get_property_groups_owned(state, player_id))
        diversity_prev = len(self._get_property_groups_owned(prev_state, player_id))
        diversity_reward = (diversity_now - diversity_prev) * 0.2
        dense_reward += diversity_reward

        # CURRICULUM ENHANCEMENTS: Additional dense rewards for tactical learning
        # 5. High-value position rewards (Boardwalk, Park Place, Railroads)
        position_value_reward = self._calculate_position_value_bonus(state, prev_state, player_id)
        dense_reward += position_value_reward

        # 6. Cash buffer maintenance (encourage keeping healthy reserves)
        cash_buffer_reward = self._calculate_cash_buffer_bonus(state, player_id)
        dense_reward += cash_buffer_reward

        return dense_reward

    def _calculate_portfolio_value(self, state: GameState, player_id: int) -> float:
        """
        Calculate total value of player's property portfolio.

        Value = sum of property base values + development value
        Higher for properties in near-complete or complete monopolies.

        Returns:
            Normalized portfolio value
        """
        player = state.players[player_id]
        total_value = 0.0

        for tile_id in player.owned_properties:
            tile = self.board.get_tile(tile_id)
            if tile.property_info is None:
                continue

            # Base property value
            base_value = tile.property_info.purchase_price / 100.0  # Normalize to ~[0, 4]

            # Development multiplier
            prop_state = state.properties.get(tile_id)
            if prop_state:
                development_multiplier = 1.0 + (prop_state.num_houses * 0.5)
                total_value += base_value * development_multiplier

        return total_value

    def _calculate_monopoly_progress(self, state: GameState, player_id: int) -> float:
        """
        Calculate progress toward completing monopolies.

        Awards partial credit for owning 1 or 2 properties in a color group.

        Returns:
            Progress score (higher = closer to monopolies)
        """
        from engine.state import PropertyGroup

        player = state.players[player_id]
        progress = 0.0

        for group in PropertyGroup:
            if group in [PropertyGroup.RAILROAD, PropertyGroup.UTILITY, PropertyGroup.SPECIAL]:
                continue

            group_tiles = self.board.get_group_tiles(group)
            owned_count = len(set(group_tiles) & player.owned_properties)
            total_count = len(group_tiles)

            if total_count > 0:
                # Award partial credit: 0.33 for 1/3, 0.66 for 2/3, 1.0 for 3/3
                progress += (owned_count / total_count)

        return progress

    def _get_property_groups_owned(self, state: GameState, player_id: int) -> Set:
        """
        Get set of property groups where player owns at least one property.

        Returns:
            Set of PropertyGroup enums
        """
        from engine.state import PropertyGroup

        player = state.players[player_id]
        groups = set()

        for tile_id in player.owned_properties:
            tile = self.board.get_tile(tile_id)
            if tile.property_info is not None:
                groups.add(tile.property_info.group)

        return groups

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

    def _calculate_position_value_bonus(self, state: GameState, prev_state: GameState,
                                       player_id: int) -> float:
        """
        Small bonus for owning high-value properties (Boardwalk, Park Place, Railroads).

        CURRICULUM ENHANCEMENT: Helps tactical learning by rewarding acquisition
        of strategically valuable positions.

        Returns:
            Small reward (typically 0-0.5) for owning valuable properties
        """
        # High-value property tile IDs
        # Boardwalk (39), Park Place (37), Railroads (5, 15, 25, 35)
        high_value_tiles = {39, 37, 5, 15, 25, 35}

        current_props = state.players[player_id].owned_properties
        prev_props = prev_state.players[player_id].owned_properties

        # Check if we gained any high-value properties this turn
        gained_props = current_props - prev_props
        high_value_gained = gained_props & high_value_tiles

        if high_value_gained:
            # Small reward per high-value property acquired
            return len(high_value_gained) * 0.3

        return 0.0

    def _calculate_cash_buffer_bonus(self, state: GameState, player_id: int) -> float:
        """
        Small bonus for maintaining healthy cash reserves.

        CURRICULUM ENHANCEMENT: Encourages tactical cash management
        (don't spend everything, maintain liquidity).

        Returns:
            Small reward (+0.1) if cash > $500, else 0
        """
        player = state.players[player_id]

        # Reward maintaining healthy cash buffer
        if player.cash >= 500:
            return 0.1

        return 0.0
