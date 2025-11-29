"""
State representation for Monopoly game.

Defines all data structures needed to represent a complete game state.
All classes use dataclasses for immutability and type safety.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Set
from enum import Enum, IntEnum


class GamePhase(Enum):
    """
    Phases within a single turn.

    This ensures deterministic turn progression and proper action sequencing.
    Each phase restricts which actions are legal.
    """
    START = "start"  # Beginning of turn, roll dice or jail actions only
    LANDED = "landed"  # After rolling/moving, handle landing effects
    PURCHASE_DECISION = "purchase_decision"  # Decide to buy/decline unowned property
    AUCTION = "auction"  # Active auction in progress
    ACTIONS = "actions"  # Can perform optional actions (build, trade, etc)
    END_PHASE = "end_phase"  # Turn complete, must end turn


class TileType(Enum):
    """Types of tiles on the Monopoly board."""
    PROPERTY = "property"
    RAILROAD = "railroad"
    UTILITY = "utility"
    GO = "go"
    CHANCE = "chance"
    COMMUNITY_CHEST = "community_chest"
    TAX = "tax"
    JAIL = "jail"
    GOTO_JAIL = "goto_jail"
    FREE_PARKING = "free_parking"


class PropertyGroup(Enum):
    """Property color groups."""
    BROWN = "brown"
    LIGHT_BLUE = "light_blue"
    PINK = "pink"
    PURPLE = "purple"
    ORANGE = "orange"
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"
    DARK_BLUE = "dark_blue"
    SPECIAL = "special"
    RAILROAD = "railroad"
    UTILITY = "utility"


@dataclass(frozen=True)
class PropertyInfo:
    """Static information about a property tile."""
    tile_id: int
    name: str
    group: PropertyGroup
    purchase_price: int
    base_rent: int
    rent_with_1_house: int
    rent_with_2_houses: int
    rent_with_3_houses: int
    rent_with_4_houses: int
    rent_with_hotel: int
    house_cost: int
    mortgage_value: int

    def get_rent(self, num_houses: int) -> int:
        """Calculate rent based on number of houses."""
        if num_houses == 0:
            return self.base_rent
        elif num_houses == 1:
            return self.rent_with_1_house
        elif num_houses == 2:
            return self.rent_with_2_houses
        elif num_houses == 3:
            return self.rent_with_3_houses
        elif num_houses == 4:
            return self.rent_with_4_houses
        elif num_houses == 5:  # Hotel
            return self.rent_with_hotel
        else:
            raise ValueError(f"Invalid number of houses: {num_houses}")


@dataclass(frozen=True)
class RailroadInfo:
    """Static information about a railroad tile."""
    tile_id: int
    name: str
    purchase_price: int
    mortgage_value: int

    def get_rent(self, num_railroads_owned: int) -> int:
        """Calculate rent based on number of railroads owned by the same player."""
        base_rent = 25
        return base_rent * (2 ** (num_railroads_owned - 1))


@dataclass(frozen=True)
class UtilityInfo:
    """Static information about a utility tile."""
    tile_id: int
    name: str
    purchase_price: int
    mortgage_value: int

    def get_rent(self, dice_roll: int, num_utilities_owned: int) -> int:
        """Calculate rent based on dice roll and number of utilities owned."""
        multiplier = 4 if num_utilities_owned == 1 else 10
        return dice_roll * multiplier


@dataclass(frozen=True)
class TileInfo:
    """Generic tile information."""
    tile_id: int
    name: str
    tile_type: TileType
    property_info: Optional[PropertyInfo] = None
    railroad_info: Optional[RailroadInfo] = None
    utility_info: Optional[UtilityInfo] = None
    tax_amount: Optional[int] = None


@dataclass
class PropertyState:
    """Mutable state of a property tile."""
    tile_id: int
    owner: Optional[int] = None  # Player ID or None
    num_houses: int = 0  # 0-4 houses, 5 = hotel
    is_mortgaged: bool = False

    def can_build(self) -> bool:
        """Check if a house/hotel can be built."""
        return not self.is_mortgaged and self.num_houses < 5

    def can_sell(self) -> bool:
        """Check if a house/hotel can be sold."""
        return self.num_houses > 0


@dataclass
class PlayerState:
    """State of a single player."""
    player_id: int
    name: str
    position: int = 0  # Tile index (0-39)
    cash: int = 1500  # Starting cash
    is_in_jail: bool = False
    jail_turns: int = 0  # Number of turns in jail
    get_out_of_jail_cards: int = 0
    is_bankrupt: bool = False
    owned_properties: Set[int] = field(default_factory=set)  # Set of tile IDs

    def can_afford(self, amount: int) -> bool:
        """Check if player can afford a purchase."""
        return self.cash >= amount

    def total_wealth(self, property_values: Dict[int, int]) -> int:
        """Calculate total wealth (cash + property values)."""
        property_wealth = sum(property_values.get(pid, 0) for pid in self.owned_properties)
        return self.cash + property_wealth


@dataclass
class AuctionState:
    """State of an ongoing auction."""
    property_id: int
    active: bool = False
    current_bid: int = 0
    current_bidder: Optional[int] = None
    remaining_bidders: List[int] = field(default_factory=list)
    passed_players: Set[int] = field(default_factory=set)


@dataclass
class TradeOffer:
    """Represents a trade offer between players."""
    from_player: int
    to_player: int
    offered_properties: Set[int] = field(default_factory=set)
    offered_cash: int = 0
    requested_properties: Set[int] = field(default_factory=set)
    requested_cash: int = 0
    is_pending: bool = True


@dataclass
class GameState:
    """Complete state of a Monopoly game."""
    # Players
    players: List[PlayerState]
    current_player_idx: int = 0
    turn_number: int = 0
    round_number: int = 0  # Tracks complete rounds (all players take a turn)
    current_phase: GamePhase = GamePhase.START

    # Board state
    properties: Dict[int, PropertyState] = field(default_factory=dict)

    # Dice and movement
    last_dice_roll: tuple[int, int] = (0, 0)
    doubles_count: int = 0  # Consecutive doubles rolled

    # Cards
    chance_deck: List[int] = field(default_factory=list)
    chance_discard: List[int] = field(default_factory=list)
    community_chest_deck: List[int] = field(default_factory=list)
    community_chest_discard: List[int] = field(default_factory=list)

    # Auction
    auction: Optional[AuctionState] = None

    # Trade
    pending_trade: Optional[TradeOffer] = None

    # Game status
    game_over: bool = False
    winner: Optional[int] = None

    # Houses and hotels available
    houses_remaining: int = 32
    hotels_remaining: int = 12

    # Free parking pool (optional house rule)
    free_parking_pool: int = 0

    def current_player(self) -> PlayerState:
        """Get the current player."""
        return self.players[self.current_player_idx]

    def get_player(self, player_id: int) -> PlayerState:
        """Get a player by ID."""
        return self.players[player_id]

    def active_players(self) -> List[PlayerState]:
        """Get list of non-bankrupt players."""
        return [p for p in self.players if not p.is_bankrupt]

    def is_doubles(self) -> bool:
        """Check if last dice roll was doubles."""
        return self.last_dice_roll[0] == self.last_dice_roll[1]

    def check_winner(self) -> Optional[int]:
        """Check if there's a winner (only one non-bankrupt player)."""
        active = self.active_players()
        if len(active) == 1:
            return active[0].player_id
        return None


@dataclass
class GameConfig:
    """Configuration for a Monopoly game."""
    num_players: int = 4
    starting_cash: int = 1500
    go_salary: int = 200
    max_rounds: int = 50  # Game ends after this many complete rounds
    max_turns: int = 1000  # Legacy fallback (deprecated, use max_rounds)
    enable_free_parking_pool: bool = False
    enable_double_go_salary: bool = False  # Collect $400 if land exactly on GO
    jail_fine: int = 50
    max_jail_turns: int = 3
    seed: Optional[int] = None  # RNG seed for determinism

    def validate(self) -> None:
        """Validate configuration parameters."""
        if not 2 <= self.num_players <= 6:
            raise ValueError("Number of players must be between 2 and 6")
        if self.starting_cash <= 0:
            raise ValueError("Starting cash must be positive")
        if self.go_salary <= 0:
            raise ValueError("GO salary must be positive")
