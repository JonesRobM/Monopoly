"""
Heuristic policy functions for each of the 10 agent archetypes.

Each agent has a heuristic policy that applies behavioral biases to
action probabilities. These are combined with learned policies using
the hybrid policy approach (alpha × heuristic + (1-alpha) × learned).

Heuristic policies implement the personality traits defined in player_behaviours.json.
"""

import numpy as np
from typing import Dict, Set, Optional, List
from engine.state import GameState, PropertyGroup
from engine.board import MonopolyBoard
from engine.actions import ActionType, ActionEncoder


class HeuristicPolicy:
    """Base class for heuristic policies with common utility functions."""

    def __init__(self, board: MonopolyBoard, action_encoder: ActionEncoder):
        """
        Initialize heuristic policy.

        Args:
            board: Monopoly board instance
            action_encoder: Action encoder for decoding action IDs
        """
        self.board = board
        self.action_encoder = action_encoder

    def get_action_probabilities(self, state: GameState, player_id: int,
                                action_mask: np.ndarray) -> np.ndarray:
        """
        Get heuristic action probabilities.

        Args:
            state: Current game state
            player_id: ID of acting player
            action_mask: Legal action mask

        Returns:
            Probability distribution over actions (normalized)
        """
        raise NotImplementedError("Subclasses must implement get_action_probabilities")

    def _get_current_tile_id(self, state: GameState, player_id: int) -> int:
        """Get the tile ID where player is currently standing."""
        return state.players[player_id].position

    def _is_property_in_groups(self, tile_id: int, groups: List[PropertyGroup]) -> bool:
        """Check if tile belongs to any of the specified property groups."""
        tile = self.board.get_tile(tile_id)
        if tile.property_info is None:
            return False
        return tile.property_info.group in groups

    def _blocks_opponent_monopoly(self, state: GameState, player_id: int,
                                 tile_id: int) -> bool:
        """Check if buying this tile would block an opponent's monopoly."""
        tile = self.board.get_tile(tile_id)
        if tile.property_info is None:
            return False

        property_group = tile.property_info.group
        group_tiles = self.board.get_group_tiles(property_group)

        # Check each opponent
        for other_player_id in range(len(state.players)):
            if other_player_id == player_id:
                continue

            other_props = state.players[other_player_id].owned_properties

            # Count how many tiles of this group the opponent owns
            opponent_group_count = len(other_props & set(group_tiles))

            # If opponent owns all except this one tile, buying blocks them
            if opponent_group_count == len(group_tiles) - 1:
                return True

        return False

    def _calculate_simple_roi(self, tile_id: int) -> float:
        """
        Calculate simple ROI estimate for a property.

        ROI = base_rent / purchase_price

        Returns:
            ROI as a fraction (e.g., 0.1 = 10% ROI)
        """
        tile = self.board.get_tile(tile_id)
        if tile.property_info is None:
            return 0.0

        if tile.property_info.purchase_price == 0:
            return 0.0

        return tile.property_info.base_rent / tile.property_info.purchase_price


class AliceHeuristic(HeuristicPolicy):
    """
    Alice - Money Maximiser

    Behavioral traits:
    - Very conservative unless ROI is high
    - Rarely builds houses; only when cash buffer > threshold
    - Low trade activity; only for strong net-positive liquidity
    - Risk tolerance: Low
    """

    CASH_THRESHOLD = 1000
    BUILD_CASH_THRESHOLD = 800
    MIN_ROI = 0.10

    def get_action_probabilities(self, state: GameState, player_id: int,
                                action_mask: np.ndarray) -> np.ndarray:
        """Apply Alice's conservative heuristic biases."""
        probs = action_mask.astype(np.float32)  # Start with uniform over legal actions

        player = state.players[player_id]
        current_tile_id = self._get_current_tile_id(state, player_id)

        # BUY_PROPERTY: Only if cash > threshold AND ROI > min
        buy_action = self.action_encoder.BUY_PROPERTY_START
        if action_mask[buy_action] > 0:
            roi = self._calculate_simple_roi(current_tile_id)
            if player.cash < self.CASH_THRESHOLD or roi < self.MIN_ROI:
                # Strong bias to DECLINE
                decline_action = self.action_encoder.DECLINE_PURCHASE
                if action_mask[decline_action] > 0:
                    probs[decline_action] *= 5.0

        # BUILD_HOUSE: Suppress unless cash > high threshold
        for action_id in range(self.action_encoder.BUILD_HOUSE_START,
                              self.action_encoder.SELL_HOUSE_START):
            if action_mask[action_id] > 0:
                if player.cash < self.BUILD_CASH_THRESHOLD:
                    probs[action_id] *= 0.1

        # TRADE: Decline unless highly favorable (implement when trades active)
        # For now, bias toward DECLINE_TRADE
        decline_trade_action = self.action_encoder.DECLINE_TRADE_ACTION
        if action_mask[decline_trade_action] > 0:
            probs[decline_trade_action] *= 3.0

        # Normalize
        total = probs.sum()
        if total > 0:
            probs /= total

        return probs


class BobHeuristic(HeuristicPolicy):
    """
    Bob - High-Value Acquirer

    Behavioral traits:
    - Aggressive on red/green/dark-blue sets
    - High priority once controlling a high-value set
    - Trades to secure key monopolies
    - Risk tolerance: High
    """

    TARGET_GROUPS = [PropertyGroup.RED, PropertyGroup.GREEN, PropertyGroup.DARK_BLUE]

    def get_action_probabilities(self, state: GameState, player_id: int,
                                action_mask: np.ndarray) -> np.ndarray:
        """Apply Bob's aggressive high-value property biases."""
        probs = action_mask.astype(np.float32)

        current_tile_id = self._get_current_tile_id(state, player_id)

        # BUY_PROPERTY: Strong bias if on target tiles
        buy_action = self.action_encoder.BUY_PROPERTY_START
        if action_mask[buy_action] > 0:
            if self._is_property_in_groups(current_tile_id, self.TARGET_GROUPS):
                probs[buy_action] *= 10.0

        # BUILD_HOUSE: Strong bias if building on target properties
        for action_id in range(self.action_encoder.BUILD_HOUSE_START,
                              self.action_encoder.SELL_HOUSE_START):
            if action_mask[action_id] > 0:
                property_id = action_id - self.action_encoder.BUILD_HOUSE_START
                if self._is_property_in_groups(property_id, self.TARGET_GROUPS):
                    probs[action_id] *= 5.0

        # ACCEPT_TRADE: Boost if completes target monopoly (implement when trades active)

        # Normalize
        total = probs.sum()
        if total > 0:
            probs /= total

        return probs


class CharlieHeuristic(HeuristicPolicy):
    """
    Charlie - Infrastructure Collector

    Behavioral traits:
    - Buys infrastructure first, streets second
    - Trades aggressively for railways/utilities
    - Low priority on building houses
    - Risk tolerance: Medium
    """

    TARGET_GROUPS = [PropertyGroup.RAILROAD, PropertyGroup.UTILITY]

    def get_action_probabilities(self, state: GameState, player_id: int,
                                action_mask: np.ndarray) -> np.ndarray:
        """Apply Charlie's infrastructure-focused biases."""
        probs = action_mask.astype(np.float32)

        current_tile_id = self._get_current_tile_id(state, player_id)

        # BUY_PROPERTY: Very strong bias for railroads/utilities
        buy_action = self.action_encoder.BUY_PROPERTY_START
        if action_mask[buy_action] > 0:
            if self._is_property_in_groups(current_tile_id, self.TARGET_GROUPS):
                probs[buy_action] *= 15.0  # Very strong bias

        # BUILD_HOUSE: Low priority
        for action_id in range(self.action_encoder.BUILD_HOUSE_START,
                              self.action_encoder.SELL_HOUSE_START):
            if action_mask[action_id] > 0:
                probs[action_id] *= 0.3

        # Normalize
        total = probs.sum()
        if total > 0:
            probs /= total

        return probs


class DeeHeuristic(HeuristicPolicy):
    """
    Dee - Trade Specialist

    Behavioral traits:
    - Focuses on trade leverage
    - Seeks arbitrage opportunities
    - Neutral property buying
    - Risk tolerance: Medium
    """

    def get_action_probabilities(self, state: GameState, player_id: int,
                                action_mask: np.ndarray) -> np.ndarray:
        """Apply Dee's trade-focused biases."""
        probs = action_mask.astype(np.float32)

        # Most behavior will come from learned policy
        # Heuristic is relatively neutral except for trade actions

        # ACCEPT_TRADE: Boost if favorable (implement when trades active)
        # OFFER_TRADE: Boost trade offers generally

        # For now, relatively uniform distribution
        # Trade biasing will be implemented when trade system is active

        # Normalize
        total = probs.sum()
        if total > 0:
            probs /= total

        return probs


class EthelHeuristic(HeuristicPolicy):
    """
    Ethel - Property Hoarder

    Behavioral traits:
    - Buys everything except very low ROI
    - Prefers breadth over depth
    - Rare trades; avoids losing tiles
    - Risk tolerance: High
    """

    MIN_ROI = 0.05  # Very low threshold

    def get_action_probabilities(self, state: GameState, player_id: int,
                                action_mask: np.ndarray) -> np.ndarray:
        """Apply Ethel's property-hoarding biases."""
        probs = action_mask.astype(np.float32)

        current_tile_id = self._get_current_tile_id(state, player_id)

        # BUY_PROPERTY: Strong bias unless ROI is terrible
        buy_action = self.action_encoder.BUY_PROPERTY_START
        if action_mask[buy_action] > 0:
            roi = self._calculate_simple_roi(current_tile_id)
            if roi >= self.MIN_ROI:
                probs[buy_action] *= 8.0

        # BUILD_HOUSE: Low priority - breadth over depth
        for action_id in range(self.action_encoder.BUILD_HOUSE_START,
                              self.action_encoder.SELL_HOUSE_START):
            if action_mask[action_id] > 0:
                probs[action_id] *= 0.2

        # DECLINE_TRADE: Strong bias - doesn't like losing tiles
        decline_trade_action = self.action_encoder.DECLINE_TRADE_ACTION
        if action_mask[decline_trade_action] > 0:
            probs[decline_trade_action] *= 5.0

        # Normalize
        total = probs.sum()
        if total > 0:
            probs /= total

        return probs


class FrankieHeuristic(HeuristicPolicy):
    """
    Frankie - Development Maximiser

    Behavioral traits:
    - Very aggressive building (3-4 houses per tile)
    - Buys aggressively to complete sets
    - Trades to complete sets
    - Risk tolerance: High
    """

    def get_action_probabilities(self, state: GameState, player_id: int,
                                action_mask: np.ndarray) -> np.ndarray:
        """Apply Frankie's development-focused biases."""
        probs = action_mask.astype(np.float32)

        # BUY_PROPERTY: Boost if helps complete a set
        buy_action = self.action_encoder.BUY_PROPERTY_START
        if action_mask[buy_action] > 0:
            probs[buy_action] *= 5.0  # Generally aggressive buying

        # BUILD_HOUSE: Very strong bias
        for action_id in range(self.action_encoder.BUILD_HOUSE_START,
                              self.action_encoder.SELL_HOUSE_START):
            if action_mask[action_id] > 0:
                probs[action_id] *= 10.0  # Very aggressive building

        # BUILD_HOTEL: Very strong bias
        for action_id in range(self.action_encoder.BUILD_HOTEL_START,
                              self.action_encoder.SELL_HOTEL_START):
            if action_mask[action_id] > 0:
                probs[action_id] *= 10.0

        # Normalize
        total = probs.sum()
        if total > 0:
            probs /= total

        return probs


class GretaHeuristic(HeuristicPolicy):
    """
    Greta - Monopoly Completer

    Behavioral traits:
    - Strong early-game focus on completing sets
    - Accelerates building after completing a set
    - Strategic trades to complete sets only
    - Risk tolerance: Medium
    """

    def get_action_probabilities(self, state: GameState, player_id: int,
                                action_mask: np.ndarray) -> np.ndarray:
        """Apply Greta's monopoly-completion biases."""
        probs = action_mask.astype(np.float32)

        current_tile_id = self._get_current_tile_id(state, player_id)

        # BUY_PROPERTY: Strong bias if helps complete a monopoly
        buy_action = self.action_encoder.BUY_PROPERTY_START
        if action_mask[buy_action] > 0:
            # Check if buying this would complete or progress toward monopoly
            probs[buy_action] *= 7.0

        # BUILD_HOUSE: Strong bias if already has monopolies
        player_monopoly_count = self._count_monopolies(state, player_id)
        if player_monopoly_count > 0:
            for action_id in range(self.action_encoder.BUILD_HOUSE_START,
                                  self.action_encoder.SELL_HOUSE_START):
                if action_mask[action_id] > 0:
                    probs[action_id] *= 6.0

        # ACCEPT_TRADE: Boost if completes monopoly (implement when trades active)

        # Normalize
        total = probs.sum()
        if total > 0:
            probs /= total

        return probs

    def _count_monopolies(self, state: GameState, player_id: int) -> int:
        """Count number of monopolies player currently owns."""
        player_props = state.players[player_id].owned_properties
        count = 0

        for group in PropertyGroup:
            if group in [PropertyGroup.RAILROAD, PropertyGroup.UTILITY, PropertyGroup.SPECIAL]:
                continue

            group_tiles = self.board.get_group_tiles(group)
            if set(group_tiles).issubset(player_props):
                count += 1

        return count


class HarryHeuristic(HeuristicPolicy):
    """
    Harry - Resource Denial Player

    Behavioral traits:
    - Buys tiles primarily to deny others
    - Trades only when it weakens opponents
    - Low building priority (defensive)
    - Risk tolerance: Medium
    """

    def get_action_probabilities(self, state: GameState, player_id: int,
                                action_mask: np.ndarray) -> np.ndarray:
        """Apply Harry's blocking/denial biases."""
        probs = action_mask.astype(np.float32)

        current_tile_id = self._get_current_tile_id(state, player_id)

        # BUY_PROPERTY: Strong bias if it blocks an opponent
        buy_action = self.action_encoder.BUY_PROPERTY_START
        if action_mask[buy_action] > 0:
            if self._blocks_opponent_monopoly(state, player_id, current_tile_id):
                probs[buy_action] *= 10.0  # Very strong blocking bias

        # BUILD_HOUSE: Low priority - defensive player
        for action_id in range(self.action_encoder.BUILD_HOUSE_START,
                              self.action_encoder.SELL_HOUSE_START):
            if action_mask[action_id] > 0:
                probs[action_id] *= 0.4

        # DECLINE_TRADE: Strong bias unless it weakens opponents
        decline_trade_action = self.action_encoder.DECLINE_TRADE_ACTION
        if action_mask[decline_trade_action] > 0:
            probs[decline_trade_action] *= 4.0

        # Normalize
        total = probs.sum()
        if total > 0:
            probs /= total

        return probs


class IreneHeuristic(HeuristicPolicy):
    """
    Irene - Risk-Balanced Investor

    Behavioral traits:
    - Buys moderate-risk, moderate-reward streets
    - Disciplined 2-house strategy
    - Moderate ROI-driven trades
    - Risk tolerance: Medium
    """

    MODERATE_ROI_MIN = 0.08
    MODERATE_ROI_MAX = 0.15
    IDEAL_HOUSES_PER_PROPERTY = 2

    def get_action_probabilities(self, state: GameState, player_id: int,
                                action_mask: np.ndarray) -> np.ndarray:
        """Apply Irene's balanced, disciplined biases."""
        probs = action_mask.astype(np.float32)

        current_tile_id = self._get_current_tile_id(state, player_id)

        # BUY_PROPERTY: Boost if moderate ROI
        buy_action = self.action_encoder.BUY_PROPERTY_START
        if action_mask[buy_action] > 0:
            roi = self._calculate_simple_roi(current_tile_id)
            if self.MODERATE_ROI_MIN <= roi <= self.MODERATE_ROI_MAX:
                probs[buy_action] *= 6.0

        # BUILD_HOUSE: Disciplined 2-house strategy
        # Boost building up to 2 houses, suppress beyond that
        for action_id in range(self.action_encoder.BUILD_HOUSE_START,
                              self.action_encoder.SELL_HOUSE_START):
            if action_mask[action_id] > 0:
                property_id = action_id - self.action_encoder.BUILD_HOUSE_START
                prop_state = state.properties.get(property_id)
                if prop_state:
                    if prop_state.num_houses < self.IDEAL_HOUSES_PER_PROPERTY:
                        probs[action_id] *= 4.0  # Boost up to 2 houses
                    else:
                        probs[action_id] *= 0.5  # Suppress beyond 2

        # Normalize
        total = probs.sum()
        if total > 0:
            probs /= total

        return probs


class JackHeuristic(HeuristicPolicy):
    """
    Jack - Hyper-Aggressive Player

    Behavioral traits:
    - Buys nearly everything to flip later
    - Hyper-aggressive 3-5 house strategy
    - Opportunistic trades
    - Risk tolerance: Very High
    """

    def get_action_probabilities(self, state: GameState, player_id: int,
                                action_mask: np.ndarray) -> np.ndarray:
        """Apply Jack's chaotic hyper-aggressive biases."""
        probs = action_mask.astype(np.float32)

        # BUY_PROPERTY: Very aggressive buying
        buy_action = self.action_encoder.BUY_PROPERTY_START
        if action_mask[buy_action] > 0:
            probs[buy_action] *= 12.0  # Very high bias

        # BUILD_HOUSE: Hyper-aggressive
        for action_id in range(self.action_encoder.BUILD_HOUSE_START,
                              self.action_encoder.SELL_HOUSE_START):
            if action_mask[action_id] > 0:
                probs[action_id] *= 8.0

        # BUILD_HOTEL: Hyper-aggressive
        for action_id in range(self.action_encoder.BUILD_HOTEL_START,
                              self.action_encoder.SELL_HOTEL_START):
            if action_mask[action_id] > 0:
                probs[action_id] *= 8.0

        # ACCEPT_TRADE: Opportunistic (implement when trades active)

        # Normalize
        total = probs.sum()
        if total > 0:
            probs /= total

        return probs


# Factory function to get heuristic for an agent
def get_heuristic_policy(agent_id: str, board: MonopolyBoard,
                        action_encoder: ActionEncoder) -> HeuristicPolicy:
    """
    Get heuristic policy instance for an agent.

    Args:
        agent_id: Agent ID (e.g., 'alice', 'bob', ...)
        board: Monopoly board instance
        action_encoder: Action encoder instance

    Returns:
        HeuristicPolicy instance for the agent

    Raises:
        ValueError: If agent_id is not recognized
    """
    heuristics = {
        'alice': AliceHeuristic,
        'bob': BobHeuristic,
        'charlie': CharlieHeuristic,
        'dee': DeeHeuristic,
        'ethel': EthelHeuristic,
        'frankie': FrankieHeuristic,
        'greta': GretaHeuristic,
        'harry': HarryHeuristic,
        'irene': IreneHeuristic,
        'jack': JackHeuristic,
    }

    if agent_id not in heuristics:
        raise ValueError(f"Unknown agent_id: {agent_id}. Must be one of {list(heuristics.keys())}")

    return heuristics[agent_id](board, action_encoder)
