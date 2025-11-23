"""
Integration tests for full game simulation.

Tests complete game scenarios with deterministic RNG to ensure
reproducible game outcomes.
"""

import pytest
import random
from engine.state import GameState, PlayerState, PropertyState, GameConfig
from engine.board import MonopolyBoard
from engine.rules import RulesEngine
from engine.cards import create_card_decks
from engine.transitions import (
    move_player, purchase_property, transfer_cash, advance_turn, bankrupt_player
)


class TestDeterministicGame:
    """Tests for deterministic game behavior."""

    def test_game_with_fixed_seed_is_reproducible(self):
        """Test that games with same seed produce same results."""
        seed = 42

        # Play first game
        random.seed(seed)
        result1 = self._simulate_simple_game(seed)

        # Play second game with same seed
        random.seed(seed)
        result2 = self._simulate_simple_game(seed)

        # Results should be identical
        assert result1 == result2

    def _simulate_simple_game(self, seed):
        """Simulate a simple game and return final state hash."""
        players = [
            PlayerState(player_id=0, name="Player 1"),
            PlayerState(player_id=1, name="Player 2")
        ]
        state = GameState(players=players)

        # Simulate 10 turns
        rng = random.Random(seed)
        for _ in range(10):
            # Roll dice
            dice1 = rng.randint(1, 6)
            dice2 = rng.randint(1, 6)
            total = dice1 + dice2

            player_id = state.current_player_idx
            new_pos = (state.players[player_id].position + total) % 40

            state = move_player(state, player_id, new_pos)
            state = advance_turn(state)

        # Return hash of final positions and cash
        return (
            tuple(p.position for p in state.players),
            tuple(p.cash for p in state.players)
        )


class TestCompleteGameFlow:
    """Tests for complete game flow."""

    @pytest.fixture
    def game_setup(self):
        """Setup a game with board, rules, and initial state."""
        board = MonopolyBoard(use_hardcoded=True)
        config = GameConfig(num_players=2, seed=42)
        rules = RulesEngine(board, config)

        players = [
            PlayerState(player_id=0, name="Player 1", cash=1500),
            PlayerState(player_id=1, name="Player 2", cash=1500)
        ]
        state = GameState(players=players)

        return board, rules, state

    def test_purchase_and_rent_flow(self, game_setup):
        """Test purchasing property and paying rent."""
        board, rules, state = game_setup

        # Player 0 buys Mediterranean Avenue
        state = purchase_property(state, 0, 1, 60)

        assert state.players[0].cash == 1440  # 1500 - 60
        assert state.properties[1].owner == 0

        # Player 1 lands on Mediterranean and pays rent
        rent = rules.calculate_rent(state, 1)
        state = transfer_cash(state, 1, 0, rent)

        assert state.players[1].cash == 1498  # 1500 - 2
        assert state.players[0].cash == 1442  # 1440 + 2

    def test_monopoly_rent_increase(self, game_setup):
        """Test rent increase with monopoly."""
        board, rules, state = game_setup

        # Player 0 buys both brown properties
        state = purchase_property(state, 0, 1, 60)  # Mediterranean
        state = purchase_property(state, 0, 3, 60)  # Baltic

        # Rent on Mediterranean should double with monopoly
        rent = rules.calculate_rent(state, 1)
        assert rent == 4  # Base rent (2) × 2

    def test_bankruptcy_scenario(self, game_setup):
        """Test bankruptcy when player cannot pay."""
        board, rules, state = game_setup

        # Player 0 has very little cash
        state.players[0].cash = 10

        # Player 0 goes bankrupt
        state = bankrupt_player(state, 0)

        assert state.players[0].is_bankrupt
        assert state.players[0].cash == 0
        assert state.game_over
        assert state.winner == 1

    def test_game_over_conditions(self, game_setup):
        """Test various game over conditions."""
        board, rules, state = game_setup

        # Initially not game over
        assert not state.game_over
        assert state.winner is None

        # One player bankrupt -> game over
        state.players[0].is_bankrupt = True
        winner = state.check_winner()

        assert winner == 1

    def test_multiple_property_transactions(self, game_setup):
        """Test multiple property purchases and transfers."""
        board, rules, state = game_setup

        # Player 0 buys several properties
        properties_to_buy = [1, 3, 5, 6]  # Mediterranean, Baltic, Reading RR, Oriental

        for prop_id in properties_to_buy:
            price = board.get_purchase_price(prop_id)
            state = purchase_property(state, 0, prop_id, price)

        assert len(state.players[0].owned_properties) == 4
        assert all(state.properties[pid].owner == 0 for pid in properties_to_buy)

        # Verify cash deduction
        total_cost = sum(board.get_purchase_price(pid) for pid in properties_to_buy)
        expected_cash = 1500 - total_cost
        assert state.players[0].cash == expected_cash


class TestCardDeck:
    """Integration tests for card deck functionality."""

    def test_chance_deck_deterministic(self):
        """Test Chance deck is deterministic with seed."""
        chance1, _ = create_card_decks(seed=42)
        chance2, _ = create_card_decks(seed=42)

        # Draw 5 cards from each
        cards1 = [chance1.draw() for _ in range(5)]
        cards2 = [chance2.draw() for _ in range(5)]

        # Should be identical
        assert [c.card_id for c in cards1] == [c.card_id for c in cards2]

    def test_deck_reshuffles_when_empty(self):
        """Test deck reshuffles discard pile when empty."""
        chance, _ = create_card_decks(seed=42)

        # Draw all cards (16 Chance cards)
        drawn_cards = []
        for _ in range(16):
            card = chance.draw()
            drawn_cards.append(card.card_id)

        # Deck should be empty, discard pile full (minus GOOJ cards)
        assert len(chance.deck) == 0

        # Drawing another card should trigger reshuffle
        card = chance.draw()
        assert card is not None

        # Deck should now have cards again
        assert len(chance.deck) > 0

    def test_get_out_of_jail_cards_held(self):
        """Test Get Out of Jail cards are held separately."""
        chance, _ = create_card_decks(seed=123)

        # Find and draw GOOJ card
        drawn = None
        for _ in range(20):  # Draw enough to likely get GOOJ
            card = chance.draw()
            if card.effect.name == "GET_OUT_OF_JAIL":
                drawn = card
                break

        if drawn:
            # GOOJ card should be in held_cards, not discard
            assert drawn.card_id in chance.held_cards
            assert drawn.card_id not in chance.discard


class TestFullGameSimulation:
    """Tests for complete game simulation."""

    def test_simple_two_player_game(self):
        """Test a simple 2-player game for several turns."""
        board = MonopolyBoard(use_hardcoded=True)
        config = GameConfig(num_players=2, seed=12345)
        rules = RulesEngine(board, config)

        players = [
            PlayerState(player_id=0, name="Player 1"),
            PlayerState(player_id=1, name="Player 2")
        ]
        state = GameState(players=players)

        rng = random.Random(12345)

        # Simulate 50 turns
        for turn in range(50):
            if state.game_over:
                break

            player_id = state.current_player_idx
            player = state.players[player_id]

            # Skip bankrupt players
            if player.is_bankrupt:
                state = advance_turn(state)
                continue

            # Roll dice
            dice1 = rng.randint(1, 6)
            dice2 = rng.randint(1, 6)
            total = dice1 + dice2
            state.last_dice_roll = (dice1, dice2)

            # Move player
            new_pos = (player.position + total) % 40
            state = move_player(state, player_id, new_pos, go_salary=config.go_salary)

            # Try to buy property if unowned and purchasable
            current_tile = state.players[player_id].position
            if board.is_purchasable(current_tile):
                if rules.can_buy_property(state, player_id, current_tile):
                    price = board.get_purchase_price(current_tile)
                    # Buy if affordable
                    if player.cash >= price:
                        state = purchase_property(state, player_id, current_tile, price)

            # Advance turn
            state = advance_turn(state)

        # Game should have progressed
        assert state.turn_number == 50
        # At least one player should own some properties
        total_properties = sum(len(p.owned_properties) for p in state.players)
        assert total_properties > 0

    def test_four_player_game(self):
        """Test a 4-player game."""
        config = GameConfig(num_players=4, seed=99999)

        players = [
            PlayerState(player_id=i, name=f"Player {i+1}")
            for i in range(4)
        ]
        state = GameState(players=players)

        # All players should start at GO
        assert all(p.position == 0 for p in state.players)

        # All players should start with starting cash
        assert all(p.cash == config.starting_cash for p in state.players)

        # Simulate turns
        rng = random.Random(99999)
        for _ in range(100):
            if state.game_over:
                break

            player_id = state.current_player_idx

            # Simple move
            total = rng.randint(2, 12)
            new_pos = (state.players[player_id].position + total) % 40
            state = move_player(state, player_id, new_pos)

            state = advance_turn(state)

        # Game should have progressed
        assert state.turn_number >= 4  # At least one round


class TestPropertyDevelopment:
    """Integration tests for property development."""

    def test_build_houses_on_monopoly(self):
        """Test building houses on a monopoly."""
        board = MonopolyBoard(use_hardcoded=True)
        config = GameConfig()
        rules = RulesEngine(board, config)

        players = [PlayerState(player_id=0, name="Player 1", cash=2000)]
        players[0].owned_properties = {1, 3}  # Brown monopoly

        properties = {
            1: PropertyState(tile_id=1, owner=0, num_houses=0),
            3: PropertyState(tile_id=3, owner=0, num_houses=0)
        }

        state = GameState(players=players, properties=properties, houses_remaining=32)

        # Can build on both properties
        assert rules.can_build_house(state, 0, 1)
        assert rules.can_build_house(state, 0, 3)

        # Build house on property 1
        from engine.transitions import build_house
        state = build_house(state, 0, 1, 50)

        assert state.properties[1].num_houses == 1
        assert state.houses_remaining == 31

        # Now must build on property 3 before building another on property 1
        assert not rules.can_build_house(state, 0, 1)
        assert rules.can_build_house(state, 0, 3)

    def test_mortgage_and_unmortgage_cycle(self):
        """Test mortgaging and unmortgaging a property."""
        board = MonopolyBoard(use_hardcoded=True)

        players = [PlayerState(player_id=0, name="Player 1", cash=100)]
        players[0].owned_properties = {1}

        properties = {1: PropertyState(tile_id=1, owner=0)}

        state = GameState(players=players, properties=properties)

        # Mortgage property
        from engine.transitions import mortgage_property
        mortgage_value = board.get_mortgage_value(1)
        state = mortgage_property(state, 0, 1, mortgage_value)

        assert state.properties[1].is_mortgaged
        assert state.players[0].cash == 130  # 100 + 30

        # Unmortgage property
        from engine.transitions import unmortgage_property
        state = unmortgage_property(state, 0, 1, mortgage_value)

        assert not state.properties[1].is_mortgaged
        assert state.players[0].cash == 97  # 130 - 33 (110% of 30)
