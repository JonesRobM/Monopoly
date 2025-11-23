"""
Action space definition for Monopoly.

Defines all possible actions a player can take in the game.
Uses discrete action encoding with action masking for RL.
"""

from dataclasses import dataclass
from enum import IntEnum, auto
from typing import Optional, List


class ActionType(IntEnum):
    """
    High-level action types.

    Values are IntEnum for easier encoding in RL action space.
    """
    # Purchase decisions
    BUY_PROPERTY = 0
    DECLINE_PURCHASE = 1

    # Auction actions
    AUCTION_BID = 2
    AUCTION_PASS = 3

    # Building actions
    BUILD_HOUSE = 4
    SELL_HOUSE = 5
    BUILD_HOTEL = 6
    SELL_HOTEL = 7

    # Mortgage actions
    MORTGAGE_PROPERTY = 8
    UNMORTGAGE_PROPERTY = 9

    # Trading actions
    OFFER_TRADE = 10
    ACCEPT_TRADE = 11
    DECLINE_TRADE = 12

    # Jail actions
    PAY_JAIL_FINE = 13
    USE_JAIL_CARD = 14
    ROLL_FOR_JAIL = 15

    # Turn management
    ROLL_DICE = 16
    END_TURN = 17

    # Bankruptcy
    DECLARE_BANKRUPTCY = 18

    # No-op (for internal state transitions)
    NOOP = 19


@dataclass(frozen=True)
class Action:
    """
    Represents a single action in the game.

    This is the high-level action representation.
    For RL, actions are encoded as discrete integers.
    """
    action_type: ActionType
    property_id: Optional[int] = None  # For building, mortgage, trade
    target_player: Optional[int] = None  # For trades
    bid_amount: Optional[int] = None  # For auctions
    trade_template_id: Optional[int] = None  # For trade offers
    cash_amount: Optional[int] = None  # For cash in trades

    def __str__(self) -> str:
        """Human-readable action description."""
        base = f"{self.action_type.name}"
        if self.property_id is not None:
            base += f"(property={self.property_id})"
        if self.target_player is not None:
            base += f"(target={self.target_player})"
        if self.bid_amount is not None:
            base += f"(bid=${self.bid_amount})"
        if self.cash_amount is not None:
            base += f"(cash=${self.cash_amount})"
        return base


class ActionEncoder:
    """
    Encodes/decodes actions to/from discrete integers for RL.

    Action space structure:
    - 0-1: BUY/DECLINE property
    - 2-11: AUCTION_BID with 10 bid levels (pass = special action)
    - 12: AUCTION_PASS
    - 13-52: BUILD_HOUSE on property (40 properties)
    - 53-92: SELL_HOUSE from property (40 properties)
    - 93-132: BUILD_HOTEL on property (40 properties)
    - 133-172: SELL_HOTEL from property (40 properties)
    - 173-212: MORTGAGE_PROPERTY (40 properties)
    - 213-252: UNMORTGAGE_PROPERTY (40 properties)
    - 253-552: OFFER_TRADE (simplified templates × target players)
    - 553: ACCEPT_TRADE
    - 554: DECLINE_TRADE
    - 555: PAY_JAIL_FINE
    - 556: USE_JAIL_CARD
    - 557: ROLL_FOR_JAIL
    - 558: ROLL_DICE
    - 559: END_TURN
    - 560: DECLARE_BANKRUPTCY
    - 561: NOOP

    Total action space size: 562
    """

    # Action space boundaries
    BUY_PROPERTY_START = 0
    DECLINE_PURCHASE = 1
    AUCTION_BID_START = 2
    AUCTION_BID_END = 11
    AUCTION_PASS = 12
    BUILD_HOUSE_START = 13
    SELL_HOUSE_START = 53
    BUILD_HOTEL_START = 93
    SELL_HOTEL_START = 133
    MORTGAGE_START = 173
    UNMORTGAGE_START = 213
    OFFER_TRADE_START = 253
    OFFER_TRADE_END = 552
    ACCEPT_TRADE = 553
    DECLINE_TRADE_ACTION = 554
    PAY_JAIL_FINE = 555
    USE_JAIL_CARD = 556
    ROLL_FOR_JAIL = 557
    ROLL_DICE = 558
    END_TURN_ACTION = 559
    DECLARE_BANKRUPTCY_ACTION = 560
    NOOP_ACTION = 561

    ACTION_SPACE_SIZE = 562

    # Auction bid levels (in dollars)
    AUCTION_BID_LEVELS = [10, 20, 50, 100, 150, 200, 250, 300, 400, 500]

    # Trade template configuration
    NUM_TRADE_TEMPLATES = 50  # Simplified trade templates
    MAX_PLAYERS = 6

    def __init__(self, num_players: int = 4):
        """
        Initialize action encoder.

        Args:
            num_players: Number of players in the game (2-6)
        """
        if not 2 <= num_players <= 6:
            raise ValueError("Number of players must be between 2 and 6")
        self.num_players = num_players

    def encode(self, action: Action) -> int:
        """
        Encode an Action object to a discrete integer.

        Args:
            action: Action object to encode

        Returns:
            Integer in range [0, ACTION_SPACE_SIZE)
        """
        action_type = action.action_type

        if action_type == ActionType.BUY_PROPERTY:
            return self.BUY_PROPERTY_START
        elif action_type == ActionType.DECLINE_PURCHASE:
            return self.DECLINE_PURCHASE
        elif action_type == ActionType.AUCTION_BID:
            bid_idx = self._get_bid_index(action.bid_amount)
            return self.AUCTION_BID_START + bid_idx
        elif action_type == ActionType.AUCTION_PASS:
            return self.AUCTION_PASS
        elif action_type == ActionType.BUILD_HOUSE:
            return self.BUILD_HOUSE_START + action.property_id
        elif action_type == ActionType.SELL_HOUSE:
            return self.SELL_HOUSE_START + action.property_id
        elif action_type == ActionType.BUILD_HOTEL:
            return self.BUILD_HOTEL_START + action.property_id
        elif action_type == ActionType.SELL_HOTEL:
            return self.SELL_HOTEL_START + action.property_id
        elif action_type == ActionType.MORTGAGE_PROPERTY:
            return self.MORTGAGE_START + action.property_id
        elif action_type == ActionType.UNMORTGAGE_PROPERTY:
            return self.UNMORTGAGE_START + action.property_id
        elif action_type == ActionType.OFFER_TRADE:
            template_offset = action.trade_template_id * (self.num_players - 1)
            player_offset = action.target_player if action.target_player < action.target_player else action.target_player - 1
            return self.OFFER_TRADE_START + template_offset + player_offset
        elif action_type == ActionType.ACCEPT_TRADE:
            return self.ACCEPT_TRADE
        elif action_type == ActionType.DECLINE_TRADE:
            return self.DECLINE_TRADE_ACTION
        elif action_type == ActionType.PAY_JAIL_FINE:
            return self.PAY_JAIL_FINE
        elif action_type == ActionType.USE_JAIL_CARD:
            return self.USE_JAIL_CARD
        elif action_type == ActionType.ROLL_FOR_JAIL:
            return self.ROLL_FOR_JAIL
        elif action_type == ActionType.ROLL_DICE:
            return self.ROLL_DICE
        elif action_type == ActionType.END_TURN:
            return self.END_TURN_ACTION
        elif action_type == ActionType.DECLARE_BANKRUPTCY:
            return self.DECLARE_BANKRUPTCY_ACTION
        elif action_type == ActionType.NOOP:
            return self.NOOP_ACTION
        else:
            raise ValueError(f"Unknown action type: {action_type}")

    def decode(self, action_id: int) -> Action:
        """
        Decode a discrete integer to an Action object.

        Args:
            action_id: Integer in range [0, ACTION_SPACE_SIZE)

        Returns:
            Action object
        """
        if action_id < 0 or action_id >= self.ACTION_SPACE_SIZE:
            raise ValueError(f"Invalid action ID: {action_id}")

        if action_id == self.BUY_PROPERTY_START:
            return Action(ActionType.BUY_PROPERTY)
        elif action_id == self.DECLINE_PURCHASE:
            return Action(ActionType.DECLINE_PURCHASE)
        elif self.AUCTION_BID_START <= action_id <= self.AUCTION_BID_END:
            bid_idx = action_id - self.AUCTION_BID_START
            bid_amount = self.AUCTION_BID_LEVELS[bid_idx]
            return Action(ActionType.AUCTION_BID, bid_amount=bid_amount)
        elif action_id == self.AUCTION_PASS:
            return Action(ActionType.AUCTION_PASS)
        elif self.BUILD_HOUSE_START <= action_id < self.SELL_HOUSE_START:
            property_id = action_id - self.BUILD_HOUSE_START
            return Action(ActionType.BUILD_HOUSE, property_id=property_id)
        elif self.SELL_HOUSE_START <= action_id < self.BUILD_HOTEL_START:
            property_id = action_id - self.SELL_HOUSE_START
            return Action(ActionType.SELL_HOUSE, property_id=property_id)
        elif self.BUILD_HOTEL_START <= action_id < self.SELL_HOTEL_START:
            property_id = action_id - self.BUILD_HOTEL_START
            return Action(ActionType.BUILD_HOTEL, property_id=property_id)
        elif self.SELL_HOTEL_START <= action_id < self.MORTGAGE_START:
            property_id = action_id - self.SELL_HOTEL_START
            return Action(ActionType.SELL_HOTEL, property_id=property_id)
        elif self.MORTGAGE_START <= action_id < self.UNMORTGAGE_START:
            property_id = action_id - self.MORTGAGE_START
            return Action(ActionType.MORTGAGE_PROPERTY, property_id=property_id)
        elif self.UNMORTGAGE_START <= action_id < self.OFFER_TRADE_START:
            property_id = action_id - self.UNMORTGAGE_START
            return Action(ActionType.UNMORTGAGE_PROPERTY, property_id=property_id)
        elif self.OFFER_TRADE_START <= action_id <= self.OFFER_TRADE_END:
            offset = action_id - self.OFFER_TRADE_START
            template_id = offset // (self.num_players - 1)
            player_offset = offset % (self.num_players - 1)
            # Convert back to actual player ID (skipping current player)
            # This is simplified - actual implementation needs current player context
            return Action(ActionType.OFFER_TRADE, trade_template_id=template_id, target_player=player_offset)
        elif action_id == self.ACCEPT_TRADE:
            return Action(ActionType.ACCEPT_TRADE)
        elif action_id == self.DECLINE_TRADE_ACTION:
            return Action(ActionType.DECLINE_TRADE)
        elif action_id == self.PAY_JAIL_FINE:
            return Action(ActionType.PAY_JAIL_FINE)
        elif action_id == self.USE_JAIL_CARD:
            return Action(ActionType.USE_JAIL_CARD)
        elif action_id == self.ROLL_FOR_JAIL:
            return Action(ActionType.ROLL_FOR_JAIL)
        elif action_id == self.ROLL_DICE:
            return Action(ActionType.ROLL_DICE)
        elif action_id == self.END_TURN_ACTION:
            return Action(ActionType.END_TURN)
        elif action_id == self.DECLARE_BANKRUPTCY_ACTION:
            return Action(ActionType.DECLARE_BANKRUPTCY)
        elif action_id == self.NOOP_ACTION:
            return Action(ActionType.NOOP)
        else:
            raise ValueError(f"Unable to decode action ID: {action_id}")

    def _get_bid_index(self, bid_amount: int) -> int:
        """Get the index of the bid amount in AUCTION_BID_LEVELS."""
        try:
            return self.AUCTION_BID_LEVELS.index(bid_amount)
        except ValueError:
            raise ValueError(f"Invalid bid amount: {bid_amount}. Must be one of {self.AUCTION_BID_LEVELS}")

    def get_action_space_size(self) -> int:
        """Get the size of the discrete action space."""
        return self.ACTION_SPACE_SIZE


# Trade templates for compressed action space
@dataclass(frozen=True)
class TradeTemplate:
    """
    Simplified trade template to compress action space.

    Instead of arbitrary trades, we use parameterized templates.
    """
    template_id: int
    description: str
    # Template parameters define what can be traded
    # Will be expanded in full implementation
    offer_property_count: int = 0  # Number of properties offered
    request_property_count: int = 0  # Number of properties requested
    cash_range: tuple[int, int] = (0, 0)  # (min_cash, max_cash)


def create_trade_templates() -> List[TradeTemplate]:
    """
    Create simplified trade templates.

    This is a simplified version - full implementation would have
    more sophisticated templates covering common trade patterns.
    """
    templates = []

    # Template 0-9: Single property for cash
    for i in range(10):
        templates.append(TradeTemplate(
            template_id=i,
            description=f"Single property for cash (tier {i})",
            offer_property_count=1,
            request_property_count=0,
            cash_range=(i * 50, (i + 1) * 50)
        ))

    # Template 10-19: Cash for single property
    for i in range(10):
        templates.append(TradeTemplate(
            template_id=10 + i,
            description=f"Cash for single property (tier {i})",
            offer_property_count=0,
            request_property_count=1,
            cash_range=(i * 50, (i + 1) * 50)
        ))

    # Template 20-29: Property swap
    for i in range(10):
        templates.append(TradeTemplate(
            template_id=20 + i,
            description=f"Property swap {i}",
            offer_property_count=1,
            request_property_count=1,
            cash_range=(0, i * 20)
        ))

    # Template 30-39: Two properties for one
    for i in range(10):
        templates.append(TradeTemplate(
            template_id=30 + i,
            description=f"Two properties for one (tier {i})",
            offer_property_count=2,
            request_property_count=1,
            cash_range=(0, 0)
        ))

    # Template 40-49: One property for two
    for i in range(10):
        templates.append(TradeTemplate(
            template_id=40 + i,
            description=f"One property for two (tier {i})",
            offer_property_count=1,
            request_property_count=2,
            cash_range=(0, 0)
        ))

    return templates
