"""
Card system for Monopoly.

Defines Chance and Community Chest cards with their effects.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional
import random


class CardType(Enum):
    """Type of card deck."""
    CHANCE = "chance"
    COMMUNITY_CHEST = "community_chest"


class CardEffect(Enum):
    """Types of card effects."""
    MOVE_TO = auto()  # Move to specific tile
    MOVE_BACK = auto()  # Move backward N spaces
    ADVANCE_TO_NEAREST = auto()  # Advance to nearest railroad/utility
    COLLECT_MONEY = auto()  # Collect money from bank
    PAY_MONEY = auto()  # Pay money to bank
    COLLECT_FROM_PLAYERS = auto()  # Each player pays you
    PAY_EACH_PLAYER = auto()  # You pay each player
    GET_OUT_OF_JAIL = auto()  # Get out of jail free card
    GO_TO_JAIL = auto()  # Go directly to jail
    REPAIRS = auto()  # Pay for street repairs (per house/hotel)


@dataclass(frozen=True)
class Card:
    """Represents a Chance or Community Chest card."""
    card_id: int
    card_type: CardType
    description: str
    effect: CardEffect

    # Effect parameters
    target_tile: Optional[int] = None  # For MOVE_TO
    spaces_back: Optional[int] = None  # For MOVE_BACK
    amount: Optional[int] = None  # For COLLECT/PAY_MONEY
    per_player_amount: Optional[int] = None  # For player interactions
    house_cost: Optional[int] = None  # For REPAIRS
    hotel_cost: Optional[int] = None  # For REPAIRS
    nearest_type: Optional[str] = None  # For ADVANCE_TO_NEAREST ("railroad" or "utility")


class CardDeck:
    """Manages a deck of Monopoly cards with shuffle and draw mechanics."""

    def __init__(self, card_type: CardType, seed: Optional[int] = None):
        """
        Initialize a card deck.

        Args:
            card_type: Type of deck (Chance or Community Chest)
            seed: Random seed for deterministic shuffling
        """
        self.card_type = card_type
        self.rng = random.Random(seed)
        self.cards = self._create_deck()
        self.deck: List[int] = list(range(len(self.cards)))
        self.discard: List[int] = []
        self.held_cards: List[int] = []  # Get out of jail cards held by players
        self.shuffle()

    def _create_deck(self) -> List[Card]:
        """Create the appropriate deck based on type."""
        if self.card_type == CardType.CHANCE:
            return self._create_chance_deck()
        else:
            return self._create_community_chest_deck()

    def _create_chance_deck(self) -> List[Card]:
        """Create the 16 Chance cards."""
        return [
            Card(0, CardType.CHANCE, "Advance to Go (Collect $200)", CardEffect.MOVE_TO, target_tile=0),
            Card(1, CardType.CHANCE, "Advance to Illinois Ave.", CardEffect.MOVE_TO, target_tile=24),
            Card(2, CardType.CHANCE, "Advance to St. Charles Place", CardEffect.MOVE_TO, target_tile=11),
            Card(3, CardType.CHANCE, "Advance token to nearest Utility. If unowned, you may buy it from the Bank. If owned, pay owner 10× dice roll.", CardEffect.ADVANCE_TO_NEAREST, nearest_type="utility"),
            Card(4, CardType.CHANCE, "Advance token to nearest Railroad. If unowned, you may buy it from the Bank. If owned, pay owner twice the rental.", CardEffect.ADVANCE_TO_NEAREST, nearest_type="railroad"),
            Card(5, CardType.CHANCE, "Advance token to nearest Railroad. If unowned, you may buy it from the Bank. If owned, pay owner twice the rental.", CardEffect.ADVANCE_TO_NEAREST, nearest_type="railroad"),
            Card(6, CardType.CHANCE, "Bank pays you dividend of $50", CardEffect.COLLECT_MONEY, amount=50),
            Card(7, CardType.CHANCE, "Get Out of Jail Free", CardEffect.GET_OUT_OF_JAIL),
            Card(8, CardType.CHANCE, "Go Back 3 Spaces", CardEffect.MOVE_BACK, spaces_back=3),
            Card(9, CardType.CHANCE, "Go to Jail. Go directly to Jail. Do not pass Go, do not collect $200", CardEffect.GO_TO_JAIL),
            Card(10, CardType.CHANCE, "Make general repairs on all your property: For each house pay $25, For each hotel pay $100", CardEffect.REPAIRS, house_cost=25, hotel_cost=100),
            Card(11, CardType.CHANCE, "Pay poor tax of $15", CardEffect.PAY_MONEY, amount=15),
            Card(12, CardType.CHANCE, "Take a trip to Reading Railroad", CardEffect.MOVE_TO, target_tile=5),
            Card(13, CardType.CHANCE, "Take a walk on the Boardwalk. Advance to Boardwalk", CardEffect.MOVE_TO, target_tile=39),
            Card(14, CardType.CHANCE, "You have been elected Chairman of the Board. Pay each player $50", CardEffect.PAY_EACH_PLAYER, per_player_amount=50),
            Card(15, CardType.CHANCE, "Your building loan matures. Collect $150", CardEffect.COLLECT_MONEY, amount=150),
        ]

    def _create_community_chest_deck(self) -> List[Card]:
        """Create the 16 Community Chest cards."""
        return [
            Card(0, CardType.COMMUNITY_CHEST, "Advance to Go (Collect $200)", CardEffect.MOVE_TO, target_tile=0),
            Card(1, CardType.COMMUNITY_CHEST, "Bank error in your favor. Collect $200", CardEffect.COLLECT_MONEY, amount=200),
            Card(2, CardType.COMMUNITY_CHEST, "Doctor's fees. Pay $50", CardEffect.PAY_MONEY, amount=50),
            Card(3, CardType.COMMUNITY_CHEST, "From sale of stock you get $50", CardEffect.COLLECT_MONEY, amount=50),
            Card(4, CardType.COMMUNITY_CHEST, "Get Out of Jail Free", CardEffect.GET_OUT_OF_JAIL),
            Card(5, CardType.COMMUNITY_CHEST, "Go to Jail. Go directly to jail. Do not pass Go, do not collect $200", CardEffect.GO_TO_JAIL),
            Card(6, CardType.COMMUNITY_CHEST, "Grand Opera Night. Collect $50 from every player", CardEffect.COLLECT_FROM_PLAYERS, per_player_amount=50),
            Card(7, CardType.COMMUNITY_CHEST, "Holiday Fund matures. Receive $100", CardEffect.COLLECT_MONEY, amount=100),
            Card(8, CardType.COMMUNITY_CHEST, "Income tax refund. Collect $20", CardEffect.COLLECT_MONEY, amount=20),
            Card(9, CardType.COMMUNITY_CHEST, "It is your birthday. Collect $10 from every player", CardEffect.COLLECT_FROM_PLAYERS, per_player_amount=10),
            Card(10, CardType.COMMUNITY_CHEST, "Life insurance matures. Collect $100", CardEffect.COLLECT_MONEY, amount=100),
            Card(11, CardType.COMMUNITY_CHEST, "Hospital fees. Pay $100", CardEffect.PAY_MONEY, amount=100),
            Card(12, CardType.COMMUNITY_CHEST, "School fees. Pay $150", CardEffect.PAY_MONEY, amount=150),
            Card(13, CardType.COMMUNITY_CHEST, "Receive $25 consultancy fee", CardEffect.COLLECT_MONEY, amount=25),
            Card(14, CardType.COMMUNITY_CHEST, "You are assessed for street repairs: Pay $40 per house and $115 per hotel", CardEffect.REPAIRS, house_cost=40, hotel_cost=115),
            Card(15, CardType.COMMUNITY_CHEST, "You have won second prize in a beauty contest. Collect $10", CardEffect.COLLECT_MONEY, amount=10),
        ]

    def shuffle(self) -> None:
        """Shuffle the deck."""
        self.rng.shuffle(self.deck)

    def draw(self) -> Card:
        """
        Draw a card from the deck.

        Returns:
            The drawn card.
        """
        if not self.deck:
            # Reshuffle discard pile into deck
            self.deck = self.discard[:]
            self.discard = []
            self.shuffle()

        if not self.deck:
            raise RuntimeError("No cards available to draw")

        card_id = self.deck.pop(0)
        card = self.cards[card_id]

        # Get out of jail cards are held by players, not discarded
        if card.effect != CardEffect.GET_OUT_OF_JAIL:
            self.discard.append(card_id)
        else:
            self.held_cards.append(card_id)

        return card

    def return_card(self, card_id: int) -> None:
        """
        Return a get out of jail card to the deck.

        Args:
            card_id: ID of the card to return
        """
        if card_id in self.held_cards:
            self.held_cards.remove(card_id)
            self.discard.append(card_id)

    def get_card(self, card_id: int) -> Card:
        """Get a specific card by ID."""
        return self.cards[card_id]

    def reset(self, seed: Optional[int] = None) -> None:
        """Reset the deck to initial state."""
        if seed is not None:
            self.rng = random.Random(seed)
        self.deck = list(range(len(self.cards)))
        self.discard = []
        self.held_cards = []
        self.shuffle()


def create_card_decks(seed: Optional[int] = None) -> tuple[CardDeck, CardDeck]:
    """
    Create both Chance and Community Chest decks.

    Args:
        seed: Random seed for deterministic deck creation

    Returns:
        Tuple of (chance_deck, community_chest_deck)
    """
    if seed is not None:
        chance_seed = seed
        cc_seed = seed + 1
    else:
        chance_seed = None
        cc_seed = None

    chance = CardDeck(CardType.CHANCE, chance_seed)
    community_chest = CardDeck(CardType.COMMUNITY_CHEST, cc_seed)

    return chance, community_chest
