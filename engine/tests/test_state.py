"""
Unit tests for game state structures.
"""

import pytest
from engine.state import (
    GameState, PlayerState, PropertyState, GameConfig,
    PropertyInfo, PropertyGroup, TileType, AuctionState
)


class TestPlayerState:
    """Tests for PlayerState class."""

    def test_player_initialization(self):
        """Test player is initialized with correct defaults."""
        player = PlayerState(player_id=0, name="Player 1")

        assert player.player_id == 0
        assert player.name == "Player 1"
        assert player.position == 0
        assert player.cash == 1500
        assert not player.is_in_jail
        assert player.jail_turns == 0
        assert player.get_out_of_jail_cards == 0
        assert not player.is_bankrupt
        assert len(player.owned_properties) == 0

    def test_can_afford(self):
        """Test can_afford method."""
        player = PlayerState(player_id=0, name="Player 1", cash=500)

        assert player.can_afford(500)
        assert player.can_afford(400)
        assert not player.can_afford(501)
        assert not player.can_afford(1000)

    def test_total_wealth(self):
        """Test total_wealth calculation."""
        player = PlayerState(player_id=0, name="Player 1", cash=500)
        player.owned_properties = {1, 3, 5}

        property_values = {1: 100, 3: 150, 5: 200}
        wealth = player.total_wealth(property_values)

        assert wealth == 950  # 500 + 100 + 150 + 200


class TestPropertyState:
    """Tests for PropertyState class."""

    def test_property_initialization(self):
        """Test property is initialized with correct defaults."""
        prop = PropertyState(tile_id=1)

        assert prop.tile_id == 1
        assert prop.owner is None
        assert prop.num_houses == 0
        assert not prop.is_mortgaged

    def test_can_build(self):
        """Test can_build method."""
        prop = PropertyState(tile_id=1, num_houses=0)
        assert prop.can_build()

        prop.num_houses = 4
        assert prop.can_build()

        prop.num_houses = 5  # Hotel
        assert not prop.can_build()

        prop.num_houses = 3
        prop.is_mortgaged = True
        assert not prop.can_build()

    def test_can_sell(self):
        """Test can_sell method."""
        prop = PropertyState(tile_id=1, num_houses=0)
        assert not prop.can_sell()

        prop.num_houses = 1
        assert prop.can_sell()

        prop.num_houses = 5
        assert prop.can_sell()


class TestGameState:
    """Tests for GameState class."""

    def test_game_initialization(self):
        """Test game state is initialized correctly."""
        players = [
            PlayerState(player_id=0, name="Player 1"),
            PlayerState(player_id=1, name="Player 2"),
        ]

        state = GameState(players=players)

        assert len(state.players) == 2
        assert state.current_player_idx == 0
        assert state.turn_number == 0
        assert len(state.properties) == 0
        assert state.last_dice_roll == (0, 0)
        assert state.doubles_count == 0
        assert not state.game_over
        assert state.winner is None
        assert state.houses_remaining == 32
        assert state.hotels_remaining == 12

    def test_current_player(self):
        """Test current_player method."""
        players = [
            PlayerState(player_id=0, name="Player 1"),
            PlayerState(player_id=1, name="Player 2"),
        ]

        state = GameState(players=players, current_player_idx=0)
        assert state.current_player().player_id == 0

        state.current_player_idx = 1
        assert state.current_player().player_id == 1

    def test_active_players(self):
        """Test active_players method."""
        players = [
            PlayerState(player_id=0, name="Player 1"),
            PlayerState(player_id=1, name="Player 2", is_bankrupt=True),
            PlayerState(player_id=2, name="Player 3"),
        ]

        state = GameState(players=players)
        active = state.active_players()

        assert len(active) == 2
        assert active[0].player_id == 0
        assert active[1].player_id == 2

    def test_is_doubles(self):
        """Test is_doubles method."""
        players = [PlayerState(player_id=0, name="Player 1")]
        state = GameState(players=players)

        state.last_dice_roll = (3, 3)
        assert state.is_doubles()

        state.last_dice_roll = (2, 4)
        assert not state.is_doubles()

        state.last_dice_roll = (6, 6)
        assert state.is_doubles()

    def test_check_winner(self):
        """Test check_winner method."""
        players = [
            PlayerState(player_id=0, name="Player 1"),
            PlayerState(player_id=1, name="Player 2"),
            PlayerState(player_id=2, name="Player 3"),
        ]

        state = GameState(players=players)

        # No winner yet
        assert state.check_winner() is None

        # Two players bankrupt
        state.players[1].is_bankrupt = True
        state.players[2].is_bankrupt = True

        # Player 0 wins
        assert state.check_winner() == 0


class TestGameConfig:
    """Tests for GameConfig class."""

    def test_config_defaults(self):
        """Test config default values."""
        config = GameConfig()

        assert config.num_players == 4
        assert config.starting_cash == 1500
        assert config.go_salary == 200
        assert config.max_turns == 1000
        assert not config.enable_free_parking_pool
        assert not config.enable_double_go_salary
        assert config.jail_fine == 50
        assert config.max_jail_turns == 3
        assert config.seed is None

    def test_config_validation(self):
        """Test config validation."""
        config = GameConfig(num_players=4)
        config.validate()  # Should not raise

        with pytest.raises(ValueError):
            config = GameConfig(num_players=1)
            config.validate()

        with pytest.raises(ValueError):
            config = GameConfig(num_players=7)
            config.validate()

        with pytest.raises(ValueError):
            config = GameConfig(starting_cash=0)
            config.validate()

        with pytest.raises(ValueError):
            config = GameConfig(go_salary=-100)
            config.validate()


class TestPropertyInfo:
    """Tests for PropertyInfo class."""

    def test_property_info(self):
        """Test PropertyInfo initialization."""
        prop = PropertyInfo(
            tile_id=1,
            name="Mediterranean Avenue",
            group=PropertyGroup.BROWN,
            purchase_price=60,
            base_rent=2,
            rent_with_1_house=10,
            rent_with_2_houses=30,
            rent_with_3_houses=90,
            rent_with_4_houses=160,
            rent_with_hotel=250,
            house_cost=50,
            mortgage_value=30
        )

        assert prop.tile_id == 1
        assert prop.name == "Mediterranean Avenue"
        assert prop.group == PropertyGroup.BROWN
        assert prop.purchase_price == 60
        assert prop.mortgage_value == 30

    def test_get_rent(self):
        """Test rent calculation."""
        prop = PropertyInfo(
            tile_id=1,
            name="Test Property",
            group=PropertyGroup.BROWN,
            purchase_price=60,
            base_rent=2,
            rent_with_1_house=10,
            rent_with_2_houses=30,
            rent_with_3_houses=90,
            rent_with_4_houses=160,
            rent_with_hotel=250,
            house_cost=50,
            mortgage_value=30
        )

        assert prop.get_rent(0) == 2
        assert prop.get_rent(1) == 10
        assert prop.get_rent(2) == 30
        assert prop.get_rent(3) == 90
        assert prop.get_rent(4) == 160
        assert prop.get_rent(5) == 250

        with pytest.raises(ValueError):
            prop.get_rent(6)

        with pytest.raises(ValueError):
            prop.get_rent(-1)


class TestAuctionState:
    """Tests for AuctionState class."""

    def test_auction_initialization(self):
        """Test auction state initialization."""
        auction = AuctionState(property_id=5)

        assert auction.property_id == 5
        assert not auction.active
        assert auction.current_bid == 0
        assert auction.current_bidder is None
        assert len(auction.remaining_bidders) == 0
        assert len(auction.passed_players) == 0

    def test_auction_with_bidders(self):
        """Test auction with bidders."""
        auction = AuctionState(
            property_id=5,
            active=True,
            remaining_bidders=[0, 1, 2, 3]
        )

        assert auction.active
        assert len(auction.remaining_bidders) == 4
        assert 0 in auction.remaining_bidders
        assert 3 in auction.remaining_bidders
