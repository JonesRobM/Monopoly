"""
Pure transition functions for Monopoly game state.

All functions are pure (no side effects) and deterministic (given same inputs,
produce same outputs). This makes them easily testable.
"""

from typing import Tuple, Optional, List
from copy import deepcopy
from engine.state import GameState, PlayerState, PropertyState, AuctionState, TradeOffer
from engine.board import MonopolyBoard
from engine.cards import Card, CardEffect


def move_player(state: GameState, player_id: int, new_position: int,
                collect_go: bool = True, go_salary: int = 200) -> GameState:
    """
    Move a player to a new position.

    Args:
        state: Current game state
        player_id: ID of player to move
        new_position: New tile position (0-39)
        collect_go: Whether to collect GO salary if passing/landing on GO
        go_salary: Amount to collect for passing GO

    Returns:
        Updated game state
    """
    new_state = deepcopy(state)
    player = new_state.players[player_id]

    old_position = player.position

    # Check if player passes or lands on GO
    if collect_go:
        if new_position < old_position or new_position == 0:
            # Passed or landed on GO
            player.cash += go_salary

    player.position = new_position % 40

    return new_state


def transfer_cash(state: GameState, from_player: int, to_player: int,
                  amount: int) -> GameState:
    """
    Transfer cash between two players.

    Args:
        state: Current game state
        from_player: Player giving cash (or -1 for bank)
        to_player: Player receiving cash (or -1 for bank)
        amount: Amount to transfer

    Returns:
        Updated game state
    """
    new_state = deepcopy(state)

    if from_player >= 0:
        new_state.players[from_player].cash -= amount
    if to_player >= 0:
        new_state.players[to_player].cash += amount

    return new_state


def purchase_property(state: GameState, player_id: int, property_id: int,
                      price: int) -> GameState:
    """
    Purchase a property.

    Args:
        state: Current game state
        player_id: ID of purchasing player
        property_id: ID of property to purchase
        price: Purchase price

    Returns:
        Updated game state
    """
    new_state = deepcopy(state)

    # Deduct cash
    new_state.players[player_id].cash -= price

    # Transfer ownership
    if property_id not in new_state.properties:
        new_state.properties[property_id] = PropertyState(tile_id=property_id)

    new_state.properties[property_id].owner = player_id
    new_state.players[player_id].owned_properties.add(property_id)

    return new_state


def build_house(state: GameState, player_id: int, property_id: int,
                house_cost: int) -> GameState:
    """
    Build a house on a property.

    Args:
        state: Current game state
        player_id: ID of building player
        property_id: ID of property to build on
        house_cost: Cost of building a house

    Returns:
        Updated game state
    """
    new_state = deepcopy(state)

    # Deduct cash
    new_state.players[player_id].cash -= house_cost

    # Add house
    prop = new_state.properties[property_id]
    if prop.num_houses < 4:
        prop.num_houses += 1
        new_state.houses_remaining -= 1
    else:
        # Upgrade to hotel
        prop.num_houses = 5
        new_state.houses_remaining += 4  # Return 4 houses
        new_state.hotels_remaining -= 1

    return new_state


def sell_house(state: GameState, player_id: int, property_id: int,
               house_cost: int) -> GameState:
    """
    Sell a house from a property.

    Args:
        state: Current game state
        player_id: ID of selling player
        property_id: ID of property to sell from
        house_cost: Cost of a house (sell for half)

    Returns:
        Updated game state
    """
    new_state = deepcopy(state)

    prop = new_state.properties[property_id]

    if prop.num_houses == 5:
        # Downgrade hotel to 4 houses
        prop.num_houses = 4
        new_state.hotels_remaining += 1
        new_state.houses_remaining -= 4
        new_state.players[player_id].cash += house_cost // 2
    elif prop.num_houses > 0:
        # Sell a house
        prop.num_houses -= 1
        new_state.houses_remaining += 1
        new_state.players[player_id].cash += house_cost // 2

    return new_state


def mortgage_property(state: GameState, player_id: int, property_id: int,
                      mortgage_value: int) -> GameState:
    """
    Mortgage a property.

    Args:
        state: Current game state
        player_id: ID of player mortgaging
        property_id: ID of property to mortgage
        mortgage_value: Mortgage value of the property

    Returns:
        Updated game state
    """
    new_state = deepcopy(state)

    # Mark as mortgaged
    new_state.properties[property_id].is_mortgaged = True

    # Collect mortgage value
    new_state.players[player_id].cash += mortgage_value

    return new_state


def unmortgage_property(state: GameState, player_id: int, property_id: int,
                        mortgage_value: int) -> GameState:
    """
    Unmortgage a property.

    Args:
        state: Current game state
        player_id: ID of player unmortgaging
        property_id: ID of property to unmortgage
        mortgage_value: Mortgage value (pay 110% to unmortgage)

    Returns:
        Updated game state
    """
    new_state = deepcopy(state)

    # Pay unmortgage cost (110% of mortgage value)
    unmortgage_cost = int(mortgage_value * 1.1)
    new_state.players[player_id].cash -= unmortgage_cost

    # Mark as unmortgaged
    new_state.properties[property_id].is_mortgaged = False

    return new_state


def send_to_jail(state: GameState, player_id: int) -> GameState:
    """
    Send a player to jail.

    Args:
        state: Current game state
        player_id: ID of player to jail

    Returns:
        Updated game state
    """
    new_state = deepcopy(state)

    player = new_state.players[player_id]
    player.position = 10  # Jail tile
    player.is_in_jail = True
    player.jail_turns = 0
    new_state.doubles_count = 0  # Reset doubles

    return new_state


def release_from_jail(state: GameState, player_id: int) -> GameState:
    """
    Release a player from jail.

    Args:
        state: Current game state
        player_id: ID of player to release

    Returns:
        Updated game state
    """
    new_state = deepcopy(state)

    player = new_state.players[player_id]
    player.is_in_jail = False
    player.jail_turns = 0

    return new_state


def start_auction(state: GameState, property_id: int,
                  eligible_players: List[int]) -> GameState:
    """
    Start an auction for a property.

    Args:
        state: Current game state
        property_id: ID of property to auction
        eligible_players: List of player IDs who can bid

    Returns:
        Updated game state
    """
    new_state = deepcopy(state)

    new_state.auction = AuctionState(
        property_id=property_id,
        active=True,
        current_bid=0,
        current_bidder=None,
        remaining_bidders=eligible_players.copy(),
        passed_players=set()
    )

    return new_state


def auction_bid(state: GameState, player_id: int, bid_amount: int) -> GameState:
    """
    Place a bid in an auction.

    Args:
        state: Current game state
        player_id: ID of bidding player
        bid_amount: Bid amount

    Returns:
        Updated game state
    """
    new_state = deepcopy(state)

    auction = new_state.auction
    if auction and auction.active:
        auction.current_bid = bid_amount
        auction.current_bidder = player_id

    return new_state


def auction_pass(state: GameState, player_id: int) -> GameState:
    """
    Pass on an auction.

    Args:
        state: Current game state
        player_id: ID of passing player

    Returns:
        Updated game state
    """
    new_state = deepcopy(state)

    auction = new_state.auction
    if auction and auction.active:
        if player_id in auction.remaining_bidders:
            auction.remaining_bidders.remove(player_id)
        auction.passed_players.add(player_id)

        # End auction if only one bidder remains
        if len(auction.remaining_bidders) <= 1:
            auction.active = False

    return new_state


def complete_auction(state: GameState) -> GameState:
    """
    Complete an auction and transfer property to winner.

    Args:
        state: Current game state

    Returns:
        Updated game state
    """
    new_state = deepcopy(state)

    auction = new_state.auction
    if auction and not auction.active and auction.current_bidder is not None:
        # Transfer property
        new_state = purchase_property(
            new_state,
            auction.current_bidder,
            auction.property_id,
            auction.current_bid
        )

        # Clear auction
        new_state.auction = None

    return new_state


def execute_trade(state: GameState, trade: TradeOffer) -> GameState:
    """
    Execute a trade between two players.

    Args:
        state: Current game state
        trade: Trade offer to execute

    Returns:
        Updated game state
    """
    new_state = deepcopy(state)

    from_player = trade.from_player
    to_player = trade.to_player

    # Transfer properties from offerer to recipient
    for prop_id in trade.offered_properties:
        prop = new_state.properties[prop_id]
        prop.owner = to_player
        new_state.players[from_player].owned_properties.remove(prop_id)
        new_state.players[to_player].owned_properties.add(prop_id)

    # Transfer properties from recipient to offerer
    for prop_id in trade.requested_properties:
        prop = new_state.properties[prop_id]
        prop.owner = from_player
        new_state.players[to_player].owned_properties.remove(prop_id)
        new_state.players[from_player].owned_properties.add(prop_id)

    # Transfer cash
    if trade.offered_cash > 0:
        new_state = transfer_cash(new_state, from_player, to_player, trade.offered_cash)
    if trade.requested_cash > 0:
        new_state = transfer_cash(new_state, to_player, from_player, trade.requested_cash)

    # Clear pending trade
    new_state.pending_trade = None

    return new_state


def bankrupt_player(state: GameState, player_id: int,
                    creditor_id: Optional[int] = None) -> GameState:
    """
    Bankrupt a player and transfer assets.

    Args:
        state: Current game state
        player_id: ID of player going bankrupt
        creditor_id: ID of creditor (None if bank)

    Returns:
        Updated game state
    """
    new_state = deepcopy(state)

    player = new_state.players[player_id]
    player.is_bankrupt = True

    # Transfer all properties
    for prop_id in list(player.owned_properties):
        prop = new_state.properties[prop_id]

        if creditor_id is not None:
            # Transfer to creditor
            prop.owner = creditor_id
            new_state.players[creditor_id].owned_properties.add(prop_id)
        else:
            # Return to bank (unowned)
            prop.owner = None
            # Clear houses/hotels
            if prop.num_houses > 0:
                if prop.num_houses == 5:
                    new_state.hotels_remaining += 1
                else:
                    new_state.houses_remaining += prop.num_houses
                prop.num_houses = 0
            # Unmortgage
            prop.is_mortgaged = False

        player.owned_properties.remove(prop_id)

    # Transfer cash to creditor
    if creditor_id is not None:
        new_state.players[creditor_id].cash += player.cash

    player.cash = 0

    # Check for game over
    active_players = [p for p in new_state.players if not p.is_bankrupt]
    if len(active_players) == 1:
        new_state.game_over = True
        new_state.winner = active_players[0].player_id

    return new_state


def advance_turn(state: GameState) -> GameState:
    """
    Advance to the next player's turn.

    Args:
        state: Current game state

    Returns:
        Updated game state
    """
    new_state = deepcopy(state)

    # Reset doubles count if not rolling again
    new_state.doubles_count = 0

    # Move to next non-bankrupt player
    while True:
        new_state.current_player_idx = (new_state.current_player_idx + 1) % len(new_state.players)
        if not new_state.players[new_state.current_player_idx].is_bankrupt:
            break

    new_state.turn_number += 1

    return new_state


def apply_card_effect(state: GameState, player_id: int, card: Card,
                      dice_roll: Optional[int] = None) -> GameState:
    """
    Apply the effect of a Chance or Community Chest card.

    Args:
        state: Current game state
        player_id: ID of player who drew the card
        card: Card that was drawn
        dice_roll: Last dice roll (needed for utility rent calculation)

    Returns:
        Updated game state
    """
    new_state = deepcopy(state)
    player = new_state.players[player_id]

    if card.effect == CardEffect.MOVE_TO:
        new_state = move_player(new_state, player_id, card.target_tile)

    elif card.effect == CardEffect.MOVE_BACK:
        new_position = (player.position - card.spaces_back) % 40
        new_state = move_player(new_state, player_id, new_position, collect_go=False)

    elif card.effect == CardEffect.COLLECT_MONEY:
        player.cash += card.amount

    elif card.effect == CardEffect.PAY_MONEY:
        player.cash -= card.amount

    elif card.effect == CardEffect.COLLECT_FROM_PLAYERS:
        for other_player in new_state.players:
            if other_player.player_id != player_id and not other_player.is_bankrupt:
                other_player.cash -= card.per_player_amount
                player.cash += card.per_player_amount

    elif card.effect == CardEffect.PAY_EACH_PLAYER:
        for other_player in new_state.players:
            if other_player.player_id != player_id and not other_player.is_bankrupt:
                player.cash -= card.per_player_amount
                other_player.cash += card.per_player_amount

    elif card.effect == CardEffect.GET_OUT_OF_JAIL:
        player.get_out_of_jail_cards += 1

    elif card.effect == CardEffect.GO_TO_JAIL:
        new_state = send_to_jail(new_state, player_id)

    elif card.effect == CardEffect.REPAIRS:
        total_cost = 0
        for prop_id in player.owned_properties:
            prop = new_state.properties.get(prop_id)
            if prop and prop.num_houses > 0:
                if prop.num_houses == 5:
                    total_cost += card.hotel_cost
                else:
                    total_cost += card.house_cost * prop.num_houses
        player.cash -= total_cost

    elif card.effect == CardEffect.ADVANCE_TO_NEAREST:
        # Simplified - would need board reference for full implementation
        pass  # TODO: Implement nearest railroad/utility logic

    return new_state
