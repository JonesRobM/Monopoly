"""
Game rules and logic for Monopoly.

Contains functions for calculating rent, validating actions,
and determining legal moves.
"""

from typing import List, Set, Optional, Tuple
from engine.state import GameState, PlayerState, PropertyState, GameConfig
from engine.board import MonopolyBoard, PropertyGroup
from engine.actions import Action, ActionType


class RulesEngine:
    """
    Encapsulates all Monopoly game rules.

    Provides methods for rent calculation, action validation,
    and game rule enforcement.
    """

    def __init__(self, board: MonopolyBoard, config: GameConfig):
        """
        Initialize rules engine.

        Args:
            board: Monopoly board
            config: Game configuration
        """
        self.board = board
        self.config = config

    def calculate_rent(self, state: GameState, property_id: int,
                       dice_roll: Optional[int] = None) -> int:
        """
        Calculate rent owed for landing on a property.

        Args:
            state: Current game state
            property_id: ID of property landed on
            dice_roll: Dice roll value (needed for utilities)

        Returns:
            Rent amount owed
        """
        tile = self.board.get_tile(property_id)
        prop_state = state.properties.get(property_id)

        if not prop_state or prop_state.owner is None:
            return 0

        # No rent on mortgaged properties
        if prop_state.is_mortgaged:
            return 0

        owner_id = prop_state.owner

        # Property
        if tile.property_info:
            prop_info = tile.property_info
            group = prop_info.group

            # Check if owner has monopoly
            has_monopoly = self.board.has_monopoly(
                state.players[owner_id].owned_properties,
                group
            )

            # If no houses and has monopoly, double rent
            if prop_state.num_houses == 0 and has_monopoly:
                return prop_info.base_rent * 2
            else:
                return prop_info.get_rent(prop_state.num_houses)

        # Railroad
        elif tile.railroad_info:
            # Count railroads owned by same player
            railroads_owned = sum(
                1 for rail_id in self.board.get_group_tiles(PropertyGroup.RAILROAD)
                if state.properties.get(rail_id) and
                state.properties[rail_id].owner == owner_id
            )
            return tile.railroad_info.get_rent(railroads_owned)

        # Utility
        elif tile.utility_info:
            if dice_roll is None:
                raise ValueError("Dice roll required for utility rent calculation")

            # Count utilities owned by same player
            utilities_owned = sum(
                1 for util_id in self.board.get_group_tiles(PropertyGroup.UTILITY)
                if state.properties.get(util_id) and
                state.properties[util_id].owner == owner_id
            )
            return tile.utility_info.get_rent(dice_roll, utilities_owned)

        return 0

    def can_build_house(self, state: GameState, player_id: int,
                        property_id: int) -> bool:
        """
        Check if a player can build a house on a property.

        Args:
            state: Current game state
            player_id: ID of player attempting to build
            property_id: ID of property to build on

        Returns:
            True if building is allowed
        """
        # Get property info
        tile = self.board.get_tile(property_id)
        if not tile.property_info:
            return False

        prop_info = tile.property_info
        prop_state = state.properties.get(property_id)

        if not prop_state or prop_state.owner != player_id:
            return False

        # Can't build on mortgaged property
        if prop_state.is_mortgaged:
            return False

        # Must own all properties in the group (monopoly)
        player = state.players[player_id]
        if not self.board.has_monopoly(player.owned_properties, prop_info.group):
            return False

        # Can't exceed 5 houses (hotel)
        if prop_state.num_houses >= 5:
            return False

        # Check if houses/hotels available
        if prop_state.num_houses == 4:
            if state.hotels_remaining <= 0:
                return False
        else:
            if state.houses_remaining <= 0:
                return False

        # Must build evenly across the group
        group_tiles = self.board.get_group_tiles(prop_info.group)
        min_houses = min(
            state.properties.get(tid, PropertyState(tid)).num_houses
            for tid in group_tiles
            if state.properties.get(tid) and state.properties[tid].owner == player_id
        )

        if prop_state.num_houses > min_houses:
            return False

        # Check if player can afford
        if not player.can_afford(prop_info.house_cost):
            return False

        return True

    def can_sell_house(self, state: GameState, player_id: int,
                       property_id: int) -> bool:
        """
        Check if a player can sell a house from a property.

        Args:
            state: Current game state
            player_id: ID of player attempting to sell
            property_id: ID of property to sell from

        Returns:
            True if selling is allowed
        """
        # Get property info
        tile = self.board.get_tile(property_id)
        if not tile.property_info:
            return False

        prop_info = tile.property_info
        prop_state = state.properties.get(property_id)

        if not prop_state or prop_state.owner != player_id:
            return False

        # Must have houses to sell
        if prop_state.num_houses == 0:
            return False

        # Must sell evenly across the group
        group_tiles = self.board.get_group_tiles(prop_info.group)
        max_houses = max(
            state.properties.get(tid, PropertyState(tid)).num_houses
            for tid in group_tiles
            if state.properties.get(tid) and state.properties[tid].owner == player_id
        )

        if prop_state.num_houses < max_houses:
            return False

        return True

    def can_mortgage(self, state: GameState, player_id: int,
                     property_id: int) -> bool:
        """
        Check if a player can mortgage a property.

        Args:
            state: Current game state
            player_id: ID of player attempting to mortgage
            property_id: ID of property to mortgage

        Returns:
            True if mortgage is allowed
        """
        prop_state = state.properties.get(property_id)

        if not prop_state or prop_state.owner != player_id:
            return False

        # Can't mortgage if already mortgaged
        if prop_state.is_mortgaged:
            return False

        # Can't mortgage if has houses/hotels
        if prop_state.num_houses > 0:
            return False

        return True

    def can_unmortgage(self, state: GameState, player_id: int,
                       property_id: int) -> bool:
        """
        Check if a player can unmortgage a property.

        Args:
            state: Current game state
            player_id: ID of player attempting to unmortgage
            property_id: ID of property to unmortgage

        Returns:
            True if unmortgage is allowed
        """
        prop_state = state.properties.get(property_id)

        if not prop_state or prop_state.owner != player_id:
            return False

        # Must be mortgaged
        if not prop_state.is_mortgaged:
            return False

        # Check if player can afford (110% of mortgage value)
        mortgage_value = self.board.get_mortgage_value(property_id)
        unmortgage_cost = int(mortgage_value * 1.1)

        player = state.players[player_id]
        if not player.can_afford(unmortgage_cost):
            return False

        return True

    def can_buy_property(self, state: GameState, player_id: int,
                         property_id: int) -> bool:
        """
        Check if a player can buy a property.

        Args:
            state: Current game state
            player_id: ID of player attempting to buy
            property_id: ID of property to buy

        Returns:
            True if purchase is allowed
        """
        # Check if property is purchasable
        if not self.board.is_purchasable(property_id):
            return False

        # Check if unowned
        prop_state = state.properties.get(property_id)
        if prop_state and prop_state.owner is not None:
            return False

        # Check if player can afford
        price = self.board.get_purchase_price(property_id)
        player = state.players[player_id]

        return player.can_afford(price)

    def get_total_assets(self, state: GameState, player_id: int) -> int:
        """
        Calculate total assets of a player (cash + property values).

        Args:
            state: Current game state
            player_id: ID of player

        Returns:
            Total asset value
        """
        player = state.players[player_id]
        total = player.cash

        for prop_id in player.owned_properties:
            # Add mortgage value (conservative estimate)
            total += self.board.get_mortgage_value(prop_id)

            # Add house value
            prop_state = state.properties.get(prop_id)
            if prop_state and prop_state.num_houses > 0:
                tile = self.board.get_tile(prop_id)
                if tile.property_info:
                    # Houses sell for half price
                    house_value = tile.property_info.house_cost // 2
                    if prop_state.num_houses == 5:
                        # Hotel
                        total += house_value
                    else:
                        total += house_value * prop_state.num_houses

        return total

    def is_bankrupt(self, state: GameState, player_id: int) -> bool:
        """
        Check if a player is bankrupt (cannot pay debts even by liquidating).

        Args:
            state: Current game state
            player_id: ID of player

        Returns:
            True if player is bankrupt
        """
        # For now, simplified check
        return self.get_total_assets(state, player_id) <= 0

    def get_legal_actions(self, state: GameState, player_id: int) -> List[ActionType]:
        """
        Get list of legal action types for a player.

        Args:
            state: Current game state
            player_id: ID of player

        Returns:
            List of legal action types
        """
        legal = []
        player = state.players[player_id]

        # If player's turn
        if state.current_player_idx == player_id:
            # In jail
            if player.is_in_jail:
                legal.append(ActionType.ROLL_FOR_JAIL)
                if player.can_afford(self.config.jail_fine):
                    legal.append(ActionType.PAY_JAIL_FINE)
                if player.get_out_of_jail_cards > 0:
                    legal.append(ActionType.USE_JAIL_CARD)
            else:
                # Normal turn
                legal.append(ActionType.ROLL_DICE)

                # Building/selling
                for prop_id in player.owned_properties:
                    if self.can_build_house(state, player_id, prop_id):
                        legal.append(ActionType.BUILD_HOUSE)
                        break

                for prop_id in player.owned_properties:
                    if self.can_sell_house(state, player_id, prop_id):
                        legal.append(ActionType.SELL_HOUSE)
                        break

                # Mortgage/unmortgage
                for prop_id in player.owned_properties:
                    if self.can_mortgage(state, player_id, prop_id):
                        legal.append(ActionType.MORTGAGE_PROPERTY)
                        break

                for prop_id in player.owned_properties:
                    if self.can_unmortgage(state, player_id, prop_id):
                        legal.append(ActionType.UNMORTGAGE_PROPERTY)
                        break

                # Can always end turn (in some game phases)
                legal.append(ActionType.END_TURN)

        # Auction
        if state.auction and state.auction.active:
            if player_id in state.auction.remaining_bidders:
                legal.append(ActionType.AUCTION_BID)
                legal.append(ActionType.AUCTION_PASS)

        # Trade
        if state.pending_trade and state.pending_trade.to_player == player_id:
            legal.append(ActionType.ACCEPT_TRADE)
            legal.append(ActionType.DECLINE_TRADE)

        return legal

    def get_property_groups_owned(self, state: GameState,
                                  player_id: int) -> List[PropertyGroup]:
        """
        Get list of property groups where player has a monopoly.

        Args:
            state: Current game state
            player_id: ID of player

        Returns:
            List of property groups owned
        """
        player = state.players[player_id]
        monopolies = []

        for group in PropertyGroup:
            if self.board.has_monopoly(player.owned_properties, group):
                monopolies.append(group)

        return monopolies

    def calculate_net_worth(self, state: GameState, player_id: int) -> int:
        """
        Calculate net worth for ranking at end of game.

        Args:
            state: Current game state
            player_id: ID of player

        Returns:
            Net worth value
        """
        player = state.players[player_id]
        net_worth = player.cash

        # Add property purchase prices
        for prop_id in player.owned_properties:
            # Unmortgaged properties count at purchase price
            prop_state = state.properties.get(prop_id)
            if prop_state and not prop_state.is_mortgaged:
                net_worth += self.board.get_purchase_price(prop_id)

            # Add house/hotel value
            if prop_state and prop_state.num_houses > 0:
                tile = self.board.get_tile(prop_id)
                if tile.property_info:
                    house_cost = tile.property_info.house_cost
                    if prop_state.num_houses == 5:
                        net_worth += house_cost  # Hotel
                    else:
                        net_worth += house_cost * prop_state.num_houses

        return net_worth

    def get_game_phase(self, state: GameState) -> str:
        """
        Determine current game phase.

        Args:
            state: Current game state

        Returns:
            Phase name: "roll", "purchase", "auction", "trade", "end_turn", "game_over"
        """
        if state.game_over:
            return "game_over"

        if state.auction and state.auction.active:
            return "auction"

        if state.pending_trade and state.pending_trade.is_pending:
            return "trade"

        player = state.current_player()

        if player.is_in_jail:
            return "jail"

        # Simplified - would need more state to track exact phase
        return "roll"
