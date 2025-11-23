"""
Monopoly game engine.

Provides deterministic game rules, state management, and transitions.
"""

from engine.state import (
    GameState, PlayerState, PropertyState, GameConfig,
    TileType, PropertyGroup, AuctionState, TradeOffer
)
from engine.board import MonopolyBoard
from engine.rules import RulesEngine
from engine.cards import create_card_decks, CardDeck, Card, CardEffect
from engine.actions import Action, ActionType, ActionEncoder
from engine.transitions import (
    move_player, transfer_cash, purchase_property,
    build_house, sell_house, mortgage_property, unmortgage_property,
    send_to_jail, release_from_jail, bankrupt_player, advance_turn
)

__all__ = [
    # State
    "GameState",
    "PlayerState",
    "PropertyState",
    "GameConfig",
    "TileType",
    "PropertyGroup",
    "AuctionState",
    "TradeOffer",
    # Board
    "MonopolyBoard",
    # Rules
    "RulesEngine",
    # Cards
    "create_card_decks",
    "CardDeck",
    "Card",
    "CardEffect",
    # Actions
    "Action",
    "ActionType",
    "ActionEncoder",
    # Transitions
    "move_player",
    "transfer_cash",
    "purchase_property",
    "build_house",
    "sell_house",
    "mortgage_property",
    "unmortgage_property",
    "send_to_jail",
    "release_from_jail",
    "bankrupt_player",
    "advance_turn",
]
