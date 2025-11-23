"""
Unit tests for state transition functions.
"""

import pytest
from engine.state import GameState, PlayerState, PropertyState, GameConfig
from engine.transitions import (
    move_player, transfer_cash, purchase_property, build_house, sell_house,
    mortgage_property, unmortgage_property, send_to_jail, release_from_jail,
    bankrupt_player, advance_turn
)


class TestMovePlayer:
    """Tests for move_player transition."""

    def test_move_forward(self):
        """Test moving player forward."""
        players = [PlayerState(player_id=0, name="Player 1", position=5)]
        state = GameState(players=players)

        new_state = move_player(state, 0, 10, collect_go=False)

        assert new_state.players[0].position == 10
        assert state.players[0].position == 5  # Original unchanged

    def test_collect_go_salary(self):
        """Test collecting GO salary when passing GO."""
        players = [PlayerState(player_id=0, name="Player 1", position=35, cash=1000)]
        state = GameState(players=players)

        # Move from 35 to 5 (passes GO)
        new_state = move_player(state, 0, 5, collect_go=True, go_salary=200)

        assert new_state.players[0].position == 5
        assert new_state.players[0].cash == 1200  # 1000 + 200

    def test_land_on_go(self):
        """Test landing exactly on GO."""
        players = [PlayerState(player_id=0, name="Player 1", position=35, cash=1000)]
        state = GameState(players=players)

        # Move to GO
        new_state = move_player(state, 0, 0, collect_go=True, go_salary=200)

        assert new_state.players[0].position == 0
        assert new_state.players[0].cash == 1200

    def test_no_go_salary_when_disabled(self):
        """Test not collecting GO salary when disabled."""
        players = [PlayerState(player_id=0, name="Player 1", position=35, cash=1000)]
        state = GameState(players=players)

        new_state = move_player(state, 0, 5, collect_go=False)

        assert new_state.players[0].position == 5
        assert new_state.players[0].cash == 1000  # No change


class TestTransferCash:
    """Tests for transfer_cash transition."""

    def test_transfer_between_players(self):
        """Test transferring cash between two players."""
        players = [
            PlayerState(player_id=0, name="Player 1", cash=1000),
            PlayerState(player_id=1, name="Player 2", cash=500)
        ]
        state = GameState(players=players)

        new_state = transfer_cash(state, 0, 1, 200)

        assert new_state.players[0].cash == 800
        assert new_state.players[1].cash == 700

    def test_transfer_from_bank(self):
        """Test receiving money from bank."""
        players = [PlayerState(player_id=0, name="Player 1", cash=1000)]
        state = GameState(players=players)

        new_state = transfer_cash(state, -1, 0, 200)

        assert new_state.players[0].cash == 1200

    def test_transfer_to_bank(self):
        """Test paying money to bank."""
        players = [PlayerState(player_id=0, name="Player 1", cash=1000)]
        state = GameState(players=players)

        new_state = transfer_cash(state, 0, -1, 200)

        assert new_state.players[0].cash == 800


class TestPurchaseProperty:
    """Tests for purchase_property transition."""

    def test_purchase_unowned_property(self):
        """Test purchasing an unowned property."""
        players = [PlayerState(player_id=0, name="Player 1", cash=1000)]
        state = GameState(players=players, properties={})

        new_state = purchase_property(state, 0, 1, 60)

        assert new_state.players[0].cash == 940
        assert 1 in new_state.players[0].owned_properties
        assert new_state.properties[1].owner == 0
        assert new_state.properties[1].tile_id == 1

    def test_purchase_creates_property_state(self):
        """Test that purchasing creates PropertyState if not exists."""
        players = [PlayerState(player_id=0, name="Player 1", cash=1000)]
        state = GameState(players=players, properties={})

        new_state = purchase_property(state, 0, 5, 200)

        assert 5 in new_state.properties
        assert new_state.properties[5].owner == 0
        assert new_state.properties[5].tile_id == 5


class TestBuildHouse:
    """Tests for build_house transition."""

    def test_build_first_house(self):
        """Test building the first house."""
        players = [PlayerState(player_id=0, name="Player 1", cash=1000)]
        properties = {1: PropertyState(tile_id=1, owner=0, num_houses=0)}
        state = GameState(players=players, properties=properties, houses_remaining=32)

        new_state = build_house(state, 0, 1, 50)

        assert new_state.players[0].cash == 950
        assert new_state.properties[1].num_houses == 1
        assert new_state.houses_remaining == 31

    def test_build_hotel(self):
        """Test upgrading 4 houses to hotel."""
        players = [PlayerState(player_id=0, name="Player 1", cash=1000)]
        properties = {1: PropertyState(tile_id=1, owner=0, num_houses=4)}
        state = GameState(
            players=players,
            properties=properties,
            houses_remaining=32,
            hotels_remaining=12
        )

        new_state = build_house(state, 0, 1, 50)

        assert new_state.players[0].cash == 950
        assert new_state.properties[1].num_houses == 5  # Hotel
        assert new_state.houses_remaining == 36  # 4 houses returned
        assert new_state.hotels_remaining == 11


class TestSellHouse:
    """Tests for sell_house transition."""

    def test_sell_house(self):
        """Test selling a house."""
        players = [PlayerState(player_id=0, name="Player 1", cash=1000)]
        properties = {1: PropertyState(tile_id=1, owner=0, num_houses=2)}
        state = GameState(players=players, properties=properties, houses_remaining=30)

        new_state = sell_house(state, 0, 1, 50)

        assert new_state.players[0].cash == 1025  # 1000 + 50/2
        assert new_state.properties[1].num_houses == 1
        assert new_state.houses_remaining == 31

    def test_sell_hotel(self):
        """Test downgrading hotel to 4 houses."""
        players = [PlayerState(player_id=0, name="Player 1", cash=1000)]
        properties = {1: PropertyState(tile_id=1, owner=0, num_houses=5)}
        state = GameState(
            players=players,
            properties=properties,
            houses_remaining=32,
            hotels_remaining=11
        )

        new_state = sell_house(state, 0, 1, 50)

        assert new_state.players[0].cash == 1025
        assert new_state.properties[1].num_houses == 4
        assert new_state.houses_remaining == 28  # 4 houses used
        assert new_state.hotels_remaining == 12  # Hotel returned


class TestMortgageProperty:
    """Tests for mortgage_property transition."""

    def test_mortgage_property(self):
        """Test mortgaging a property."""
        players = [PlayerState(player_id=0, name="Player 1", cash=100)]
        properties = {1: PropertyState(tile_id=1, owner=0, is_mortgaged=False)}
        state = GameState(players=players, properties=properties)

        new_state = mortgage_property(state, 0, 1, 30)

        assert new_state.properties[1].is_mortgaged
        assert new_state.players[0].cash == 130  # 100 + 30


class TestUnmortgageProperty:
    """Tests for unmortgage_property transition."""

    def test_unmortgage_property(self):
        """Test unmortgaging a property."""
        players = [PlayerState(player_id=0, name="Player 1", cash=100)]
        properties = {1: PropertyState(tile_id=1, owner=0, is_mortgaged=True)}
        state = GameState(players=players, properties=properties)

        # Unmortgage costs 110% of mortgage value
        new_state = unmortgage_property(state, 0, 1, 30)

        assert not new_state.properties[1].is_mortgaged
        assert new_state.players[0].cash == 67  # 100 - 33 (110% of 30)


class TestJailTransitions:
    """Tests for jail-related transitions."""

    def test_send_to_jail(self):
        """Test sending player to jail."""
        players = [PlayerState(player_id=0, name="Player 1", position=25)]
        state = GameState(players=players, doubles_count=2)

        new_state = send_to_jail(state, 0)

        assert new_state.players[0].position == 10  # Jail tile
        assert new_state.players[0].is_in_jail
        assert new_state.players[0].jail_turns == 0
        assert new_state.doubles_count == 0  # Reset doubles

    def test_release_from_jail(self):
        """Test releasing player from jail."""
        players = [
            PlayerState(
                player_id=0,
                name="Player 1",
                position=10,
                is_in_jail=True,
                jail_turns=2
            )
        ]
        state = GameState(players=players)

        new_state = release_from_jail(state, 0)

        assert not new_state.players[0].is_in_jail
        assert new_state.players[0].jail_turns == 0
        assert new_state.players[0].position == 10  # Still on jail tile


class TestBankruptPlayer:
    """Tests for bankrupt_player transition."""

    def test_bankrupt_to_bank(self):
        """Test player going bankrupt to bank."""
        players = [
            PlayerState(player_id=0, name="Player 1", cash=50)
        ]
        players[0].owned_properties = {1, 3}
        properties = {
            1: PropertyState(tile_id=1, owner=0, num_houses=2),
            3: PropertyState(tile_id=3, owner=0, num_houses=0)
        }
        state = GameState(
            players=players,
            properties=properties,
            houses_remaining=30
        )

        new_state = bankrupt_player(state, 0, creditor_id=None)

        assert new_state.players[0].is_bankrupt
        assert new_state.players[0].cash == 0
        assert len(new_state.players[0].owned_properties) == 0

        # Properties returned to bank
        assert new_state.properties[1].owner is None
        assert new_state.properties[3].owner is None

        # Houses returned
        assert new_state.properties[1].num_houses == 0
        assert new_state.houses_remaining == 32

    def test_bankrupt_to_creditor(self):
        """Test player going bankrupt to another player."""
        players = [
            PlayerState(player_id=0, name="Player 1", cash=50),
            PlayerState(player_id=1, name="Player 2", cash=1000)
        ]
        players[0].owned_properties = {1, 3}
        properties = {
            1: PropertyState(tile_id=1, owner=0),
            3: PropertyState(tile_id=3, owner=0)
        }
        state = GameState(players=players, properties=properties)

        new_state = bankrupt_player(state, 0, creditor_id=1)

        assert new_state.players[0].is_bankrupt
        assert new_state.players[0].cash == 0
        assert len(new_state.players[0].owned_properties) == 0

        # Properties transferred to creditor
        assert new_state.properties[1].owner == 1
        assert new_state.properties[3].owner == 1
        assert 1 in new_state.players[1].owned_properties
        assert 3 in new_state.players[1].owned_properties

        # Cash transferred
        assert new_state.players[1].cash == 1050

    def test_game_over_on_bankruptcy(self):
        """Test game ends when only one player remains."""
        players = [
            PlayerState(player_id=0, name="Player 1", cash=0),
            PlayerState(player_id=1, name="Player 2", cash=1000)
        ]
        state = GameState(players=players)

        new_state = bankrupt_player(state, 0)

        assert new_state.game_over
        assert new_state.winner == 1


class TestAdvanceTurn:
    """Tests for advance_turn transition."""

    def test_advance_to_next_player(self):
        """Test advancing to next player."""
        players = [
            PlayerState(player_id=0, name="Player 1"),
            PlayerState(player_id=1, name="Player 2"),
            PlayerState(player_id=2, name="Player 3")
        ]
        state = GameState(players=players, current_player_idx=0, turn_number=5)

        new_state = advance_turn(state)

        assert new_state.current_player_idx == 1
        assert new_state.turn_number == 6
        assert new_state.doubles_count == 0

    def test_advance_wraps_around(self):
        """Test turn advances wrap around to first player."""
        players = [
            PlayerState(player_id=0, name="Player 1"),
            PlayerState(player_id=1, name="Player 2"),
            PlayerState(player_id=2, name="Player 3")
        ]
        state = GameState(players=players, current_player_idx=2, turn_number=10)

        new_state = advance_turn(state)

        assert new_state.current_player_idx == 0
        assert new_state.turn_number == 11

    def test_skip_bankrupt_players(self):
        """Test turn skips bankrupt players."""
        players = [
            PlayerState(player_id=0, name="Player 1"),
            PlayerState(player_id=1, name="Player 2", is_bankrupt=True),
            PlayerState(player_id=2, name="Player 3")
        ]
        state = GameState(players=players, current_player_idx=0)

        new_state = advance_turn(state)

        # Should skip player 1 (bankrupt) and go to player 2
        assert new_state.current_player_idx == 2
