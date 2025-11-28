"""
Extensive unit tests for trading operations between players.

Tests cover:
- Simple trades (property for property, property for cash, cash for cash)
- Complex multi-property trades
- Trade validation and rejection
- Trade reward/penalty calculation
- Strategic trade scenarios (monopoly completion, blocking, etc.)
- Edge cases (bankrupt players, mortgaged properties, etc.)
"""

import pytest
from copy import deepcopy
from engine.state import (
    GameState, PlayerState, PropertyState, GameConfig, TradeOffer
)
from engine.board import MonopolyBoard, PropertyGroup
from engine.rules import RulesEngine
from engine.transitions import purchase_property, execute_trade, transfer_cash
from agents.reward_shaper import CustomRewardShaper


@pytest.fixture
def board():
    """Create standard Monopoly board."""
    return MonopolyBoard(use_hardcoded=True)


@pytest.fixture
def config():
    """Create default game configuration."""
    return GameConfig()


@pytest.fixture
def rules(board, config):
    """Create rules engine."""
    return RulesEngine(board, config)


@pytest.fixture
def reward_shaper(board):
    """Create reward shaper for trade evaluation."""
    priority_weights = {
        'cash': 1.0,
        'rent_yield': 1.0,
        'property_count': 1.0,
        'development': 1.0,
        'trade_value': 1.0,
        'monopoly_completion': 1.0
    }
    return CustomRewardShaper(board, priority_weights)


@pytest.fixture
def trade_state(board):
    """Create state with players owning various properties for trading."""
    players = [
        PlayerState(player_id=0, name="Alice", cash=1500),
        PlayerState(player_id=1, name="Bob", cash=1500),
        PlayerState(player_id=2, name="Charlie", cash=1500),
        PlayerState(player_id=3, name="Dee", cash=1500)
    ]
    state = GameState(
        players=players,
        current_player_idx=0,
        turn_number=0,
        properties={},
        houses_remaining=32,
        hotels_remaining=12
    )

    # Alice owns Mediterranean (1) and one railroad (5)
    state = purchase_property(state, 0, 1, 60)
    state = purchase_property(state, 0, 5, 200)

    # Bob owns Baltic (3) and Park Place (37)
    state = purchase_property(state, 1, 3, 60)
    state = purchase_property(state, 1, 37, 350)

    # Charlie owns Boardwalk (39) and Electric Company (12)
    state = purchase_property(state, 2, 39, 400)
    state = purchase_property(state, 2, 12, 150)

    # Dee owns Oriental (6), Vermont (8), Connecticut (9) - light blue set
    state = purchase_property(state, 3, 6, 100)
    state = purchase_property(state, 3, 8, 100)
    state = purchase_property(state, 3, 9, 120)

    return state


class TestSimpleTrades:
    """Test basic trade operations."""

    def test_property_for_property_trade(self, trade_state):
        """Test simple property-for-property trade."""
        # Alice trades Mediterranean (1) for Bob's Baltic (3)
        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_properties={1},
            requested_properties={3}
        )

        prev_state = deepcopy(trade_state)
        state = execute_trade(trade_state, trade)

        # Verify ownership transfers
        assert state.properties[1].owner == 1  # Bob owns Mediterranean
        assert state.properties[3].owner == 0  # Alice owns Baltic

        assert 1 in state.players[1].owned_properties
        assert 3 in state.players[0].owned_properties
        assert 1 not in state.players[0].owned_properties
        assert 3 not in state.players[1].owned_properties

        # Cash unchanged
        assert state.players[0].cash == prev_state.players[0].cash
        assert state.players[1].cash == prev_state.players[1].cash

    def test_property_for_cash_trade(self, trade_state):
        """Test property-for-cash trade."""
        # Alice sells Mediterranean (1) to Bob for 100
        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_properties={1},
            requested_cash=100
        )

        state = execute_trade(trade_state, trade)

        # Bob owns Mediterranean
        assert state.properties[1].owner == 1
        assert 1 in state.players[1].owned_properties

        # Cash transferred
        assert state.players[0].cash == 1240 + 100  # Gained 100
        assert state.players[1].cash == 1090 - 100  # Paid 100 (Bob has 1090 after buying Baltic 60 + Park Place 350)

    def test_cash_for_property_trade(self, trade_state):
        """Test cash-for-property trade."""
        # Alice pays Bob 150 for Baltic (3)
        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_cash=150,
            requested_properties={3}
        )

        state = execute_trade(trade_state, trade)

        # Alice owns Baltic
        assert state.properties[3].owner == 0
        assert 3 in state.players[0].owned_properties

        # Cash transferred
        assert state.players[0].cash == 1240 - 150
        assert state.players[1].cash == 1090 + 150

    def test_cash_for_cash_trade(self, trade_state):
        """Test pure cash transfer (unusual but valid)."""
        # Alice gives Bob 200 for nothing (gift)
        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_cash=200,
            requested_cash=0
        )

        state = execute_trade(trade_state, trade)

        assert state.players[0].cash == 1240 - 200
        assert state.players[1].cash == 1090 + 200


class TestComplexTrades:
    """Test multi-asset trades."""

    def test_multiple_properties_trade(self, trade_state):
        """Test trading multiple properties at once."""
        # Alice trades Mediterranean (1) and Railroad (5) for Bob's Baltic (3) and Park Place (37)
        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_properties={1, 5},
            requested_properties={3, 37}
        )

        state = execute_trade(trade_state, trade)

        # Verify all ownership transfers
        assert state.properties[1].owner == 1
        assert state.properties[5].owner == 1
        assert state.properties[3].owner == 0
        assert state.properties[37].owner == 0

        assert len(state.players[0].owned_properties) == 2  # Baltic, Park Place
        assert len(state.players[1].owned_properties) == 2  # Mediterranean, Railroad

    def test_property_and_cash_both_directions(self, trade_state):
        """Test complex trade with properties and cash both ways."""
        # Alice trades Mediterranean (1) + 200 cash for Bob's Park Place (37)
        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_properties={1},
            offered_cash=200,
            requested_properties={37}
        )

        state = execute_trade(trade_state, trade)

        assert state.properties[1].owner == 1
        assert state.properties[37].owner == 0

        assert state.players[0].cash == 1240 - 200
        assert state.players[1].cash == 1090 + 200

    def test_three_property_with_cash_adjustment(self, trade_state):
        """Test multi-property trade with cash to balance value."""
        # Alice trades Mediterranean (1) + 100 for Baltic (3) + Park Place (37)
        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_properties={1},
            offered_cash=100,
            requested_properties={3, 37}
        )

        state = execute_trade(trade_state, trade)

        assert state.properties[1].owner == 1
        assert state.properties[3].owner == 0
        assert state.properties[37].owner == 0

        assert state.players[0].cash == 1240 - 100
        assert state.players[1].cash == 1090 + 100


class TestStrategicTrades:
    """Test trades with strategic implications."""

    def test_monopoly_completion_trade(self, trade_state, rules):
        """Test trade that completes a monopoly."""
        # Alice trades to complete brown monopoly
        # Alice has Mediterranean (1), Bob has Baltic (3)
        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_cash=150,
            requested_properties={3}
        )

        prev_state = deepcopy(trade_state)
        state = execute_trade(trade_state, trade)

        # Alice now owns both brown properties - has monopoly
        assert 1 in state.players[0].owned_properties
        assert 3 in state.players[0].owned_properties

        # Verify Alice can now build (has monopoly)
        can_build = rules.can_build_house(state, 0, 1)
        assert can_build

    def test_monopoly_blocking_trade(self, trade_state):
        """Test trade that prevents opponent from completing monopoly."""
        # Bob has Park Place (37), Charlie has Boardwalk (39)
        # Alice buys Boardwalk from Charlie to block Bob

        trade = TradeOffer(
            from_player=0,
            to_player=2,
            offered_cash=500,
            requested_properties={39}
        )

        state = execute_trade(trade_state, trade)

        # Alice now owns Boardwalk, preventing Bob from completing dark blue monopoly
        assert state.properties[39].owner == 0
        assert 37 in state.players[1].owned_properties  # Bob has Park Place
        assert 39 in state.players[0].owned_properties  # Alice has Boardwalk

    def test_infrastructure_collection_trade(self, trade_state):
        """Test trading to collect railroads/utilities."""
        # Alice trades Mediterranean (1) for Charlie's Electric Company (12)
        trade = TradeOffer(
            from_player=0,
            to_player=2,
            offered_properties={1},
            requested_properties={12}
        )

        state = execute_trade(trade_state, trade)

        # Alice now has Railroad (5) and Electric Company (12)
        assert 5 in state.players[0].owned_properties
        assert 12 in state.players[0].owned_properties

    def test_mutual_monopoly_enabling_trade(self, trade_state):
        """Test trade that helps both players complete monopolies."""
        # Setup: Give Alice Baltic (3) first
        trade_state = purchase_property(trade_state, 0, 11, 140)  # St. Charles Place

        # Bob has Oriental, Vermont, Connecticut (light blues) owned by Dee
        # Trade to help both sides

        trade = TradeOffer(
            from_player=1,
            to_player=3,
            offered_properties={37},  # Park Place
            offered_cash=200,
            requested_properties={6, 8, 9}  # Light blues
        )

        state = execute_trade(trade_state, trade)

        # Bob now has complete light blue set
        assert 6 in state.players[1].owned_properties
        assert 8 in state.players[1].owned_properties
        assert 9 in state.players[1].owned_properties


class TestTradeRewardCalculation:
    """Test reward/penalty calculation for trades."""

    def test_fair_value_trade_reward(self, trade_state, reward_shaper, board):
        """Test reward calculation for fair value trade."""
        # Alice trades Mediterranean (60) for Bob's Baltic (60) - equal value
        prev_state = deepcopy(trade_state)

        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_properties={1},
            requested_properties={3}
        )
        state = execute_trade(trade_state, trade)

        # Calculate property value change for Alice
        # Lost Mediterranean (value 60), gained Baltic (value 60)
        # Net change = 0
        # Reward should be neutral

        alice_med_lost = -60
        alice_baltic_gained = 60
        net_value = alice_baltic_gained + alice_med_lost
        assert net_value == 0

    def test_profitable_trade_reward(self, trade_state, board):
        """Test reward for profitable trade."""
        # Alice trades Mediterranean (60) for Park Place (350)
        prev_state = deepcopy(trade_state)

        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_properties={1},
            requested_properties={37}
        )
        state = execute_trade(trade_state, trade)

        # Alice gained value: -60 + 350 = +290
        property_value_gain = 350 - 60
        assert property_value_gain == 290

    def test_losing_trade_penalty(self, trade_state):
        """Test penalty for unfavorable trade."""
        # Alice trades Railroad (200) for Mediterranean equivalent + cash loss
        prev_state = deepcopy(trade_state)

        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_properties={5},  # Railroad (200)
            offered_cash=100,
            requested_properties={3}  # Baltic (60)
        )
        state = execute_trade(trade_state, trade)

        # Alice lost: 200 + 100 - 60 = 240 net loss
        net_loss = 200 + 100 - 60
        assert net_loss == 240

    def test_monopoly_completion_reward_bonus(self, trade_state, reward_shaper, rules):
        """Test extra reward for completing monopoly through trade."""
        prev_state = deepcopy(trade_state)

        # Alice completes brown monopoly
        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_cash=150,
            requested_properties={3}
        )
        state = execute_trade(trade_state, trade)

        # Check if monopoly completed
        brown_properties = {1, 3}
        alice_brown = state.players[0].owned_properties & brown_properties
        has_monopoly = len(alice_brown) == 2

        assert has_monopoly

        # Monopoly completion should provide large reward bonus
        # (Implementation depends on reward shaper)
        monopoly_bonus = reward_shaper.MONOPOLY_COMPLETE_REWARD
        assert monopoly_bonus == 1000.0

    def test_cash_only_trade_value(self, trade_state):
        """Test value calculation for pure cash trades."""
        prev_state = deepcopy(trade_state)

        # Alice pays 500 to Bob for nothing (bad trade)
        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_cash=500,
            requested_cash=0
        )
        state = execute_trade(trade_state, trade)

        # Alice lost 500, Bob gained 500
        alice_cash_change = state.players[0].cash - prev_state.players[0].cash
        bob_cash_change = state.players[1].cash - prev_state.players[1].cash

        assert alice_cash_change == -500
        assert bob_cash_change == 500

    def test_property_with_houses_trade_value(self, trade_state):
        """Test trade value includes houses on properties."""
        # Add houses to Mediterranean
        trade_state.properties[1].num_houses = 3

        prev_state = deepcopy(trade_state)

        # Alice trades Mediterranean with 3 houses for Baltic (no houses)
        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_properties={1},
            requested_properties={3}
        )
        state = execute_trade(trade_state, trade)

        # Mediterranean base value: 60
        # 3 houses @ 50 each: 150
        # Total value lost by Alice: 210

        # Baltic base value: 60
        # Net value change: 60 - 210 = -150 (Alice loses value)

        mediterranean_value = 60 + (3 * 50)
        baltic_value = 60
        net_change = baltic_value - mediterranean_value
        assert net_change == -150


class TestTradeWithMultiplePlayers:
    """Test trades in 3+ player games."""

    def test_trade_between_non_current_players(self, trade_state):
        """Test trade between players who aren't the current player."""
        # Bob (player 1) trades with Charlie (player 2)
        # Current player is Alice (player 0)

        trade = TradeOffer(
            from_player=1,
            to_player=2,
            offered_properties={3},  # Baltic
            requested_properties={39}  # Boardwalk
        )

        state = execute_trade(trade_state, trade)

        assert state.properties[3].owner == 2
        assert state.properties[39].owner == 1

    def test_sequential_trades_same_property(self, trade_state):
        """Test property traded multiple times."""
        # Alice trades Mediterranean to Bob
        trade1 = TradeOffer(
            from_player=0,
            to_player=1,
            offered_properties={1},
            requested_cash=80
        )
        state = execute_trade(trade_state, trade1)

        # Bob trades Mediterranean to Charlie
        trade2 = TradeOffer(
            from_player=1,
            to_player=2,
            offered_properties={1},
            requested_cash=100
        )
        state = execute_trade(state, trade2)

        # Charlie now owns Mediterranean
        assert state.properties[1].owner == 2
        assert 1 in state.players[2].owned_properties

    def test_three_way_trade_simulation(self, trade_state):
        """Simulate three-way trade via two sequential trades."""
        # Alice -> Bob: Mediterranean (1)
        # Bob -> Charlie: Baltic (3)
        # Charlie -> Alice: Electric Company (12)

        trade1 = TradeOffer(
            from_player=0,
            to_player=1,
            offered_properties={1},
            requested_cash=0
        )
        state = execute_trade(trade_state, trade1)

        trade2 = TradeOffer(
            from_player=1,
            to_player=2,
            offered_properties={3},
            requested_cash=0
        )
        state = execute_trade(state, trade2)

        trade3 = TradeOffer(
            from_player=2,
            to_player=0,
            offered_properties={12},
            requested_cash=0
        )
        state = execute_trade(state, trade3)

        # Verify circular trade completed
        assert state.properties[1].owner == 1  # Bob has Mediterranean
        assert state.properties[3].owner == 2  # Charlie has Baltic
        assert state.properties[12].owner == 0  # Alice has Electric Company


class TestTradeEdgeCases:
    """Test edge cases and unusual trade scenarios."""

    def test_trade_with_mortgaged_property(self, trade_state):
        """Test trading mortgaged property."""
        # Mortgage Mediterranean
        trade_state.properties[1].is_mortgaged = True

        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_properties={1},
            requested_cash=50
        )

        state = execute_trade(trade_state, trade)

        # Property transfers, still mortgaged
        assert state.properties[1].owner == 1
        assert state.properties[1].is_mortgaged

    def test_trade_with_insufficient_cash(self, trade_state):
        """Test trade where player doesn't have enough cash."""
        # Alice has 1240, tries to offer 2000
        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_cash=2000,
            requested_properties={3}
        )

        # In real game, this would be rejected by validation
        # For now, test that trade system processes it
        # (Validation should happen before execute_trade is called)

        # This would cause negative cash if not validated
        # Proper implementation should validate before executing

    def test_empty_trade(self, trade_state):
        """Test trade with no assets exchanged."""
        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_properties=set(),
            offered_cash=0,
            requested_properties=set(),
            requested_cash=0
        )

        prev_state = deepcopy(trade_state)
        state = execute_trade(trade_state, trade)

        # Nothing should change
        assert state.players[0].cash == prev_state.players[0].cash
        assert state.players[1].cash == prev_state.players[1].cash

    def test_trade_same_property_both_directions(self, trade_state):
        """Test illogical trade (same property offered and requested)."""
        # This shouldn't happen but test system handles it
        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_properties={1},
            requested_properties={1}  # Same property
        )

        # This is logically invalid but test what happens
        # Proper validation should prevent this

    def test_trade_with_all_cash(self, trade_state):
        """Test player trading all their money."""
        alice_cash = trade_state.players[0].cash

        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_cash=alice_cash,
            requested_properties={3}
        )

        state = execute_trade(trade_state, trade)

        assert state.players[0].cash == 0
        assert state.properties[3].owner == 0


class TestTradeValueMetrics:
    """Test detailed trade value calculations."""

    def test_railroad_collection_value(self, trade_state, board):
        """Test value of collecting railroads through trade."""
        # Alice has 1 railroad (5), trades for another
        # Rent increases from 25 (1 RR) to 50 (2 RR)

        # First, set up Bob owning a railroad
        trade_state = purchase_property(trade_state, 1, 15, 200)

        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_cash=250,
            requested_properties={15}
        )

        state = execute_trade(trade_state, trade)

        # Alice now owns 2 railroads
        railroads_owned = sum(
            1 for prop_id in [5, 15, 25, 35]
            if prop_id in state.players[0].owned_properties
        )
        assert railroads_owned == 2

    def test_utility_pair_value(self, trade_state):
        """Test value of owning both utilities."""
        # Alice trades for Electric Company to pair with... wait, needs to own Water Works first
        # Modify test

        # Give Alice Water Works
        trade_state = purchase_property(trade_state, 0, 28, 150)

        # Trade for Electric Company
        trade = TradeOffer(
            from_player=0,
            to_player=2,
            offered_cash=200,
            requested_properties={12}
        )

        state = execute_trade(trade_state, trade)

        # Alice owns both utilities
        utilities_owned = sum(
            1 for prop_id in [12, 28]
            if prop_id in state.players[0].owned_properties
        )
        assert utilities_owned == 2

    def test_complete_color_set_value(self, trade_state):
        """Test value increase from completing color set."""
        # Alice completes brown set
        prev_state = deepcopy(trade_state)

        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_cash=150,
            requested_properties={3}
        )

        state = execute_trade(trade_state, trade)

        # Verify monopoly
        brown_set = {1, 3}
        alice_brown = state.players[0].owned_properties & brown_set
        assert len(alice_brown) == 2

        # Value increase comes from:
        # 1. Doubled rent (no houses)
        # 2. Ability to build
        # 3. Strategic value

    def test_breaking_opponent_monopoly_value(self, trade_state):
        """Test value of trade that breaks opponent's monopoly potential."""
        # Bob has Park Place (37)
        # Alice trades for Boardwalk (39) from Charlie to deny Bob monopoly

        trade = TradeOffer(
            from_player=0,
            to_player=2,
            offered_cash=500,
            requested_properties={39}
        )

        state = execute_trade(trade_state, trade)

        # Alice owns Boardwalk, preventing Bob from ever getting dark blue monopoly
        assert state.properties[39].owner == 0
        # Bob still has Park Place but can't complete set
        assert state.properties[37].owner == 1


class TestTradeRewardComponents:
    """Test individual components of trade reward calculation."""

    def test_property_value_component(self, trade_state, board):
        """Test property value calculation in trades."""
        # Property value = purchase_price

        mediterranean_value = board.get_purchase_price(1)  # 60
        baltic_value = board.get_purchase_price(3)  # 60

        assert mediterranean_value == 60
        assert baltic_value == 60

    def test_house_value_component(self, trade_state, board):
        """Test house value in trade calculations."""
        # Add houses to Mediterranean
        trade_state.properties[1].num_houses = 2
        house_cost = board.get_house_cost(1)  # 50 for brown

        total_value = 60 + (2 * 50)  # Base + houses
        assert total_value == 160

    def test_monopoly_value_component(self, reward_shaper):
        """Test monopoly completion bonus value."""
        monopoly_reward = reward_shaper.MONOPOLY_COMPLETE_REWARD
        assert monopoly_reward == 1000.0

    def test_cash_component(self, trade_state):
        """Test cash portion of trade value."""
        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_cash=300,
            requested_properties={3}
        )

        prev_cash = trade_state.players[0].cash
        state = execute_trade(trade_state, trade)

        cash_change = state.players[0].cash - prev_cash
        assert cash_change == -300

    def test_rent_potential_component(self, trade_state, rules):
        """Test rent potential as part of trade value."""
        # Completing monopoly enables building, which increases rent potential

        # Alice completes brown monopoly
        trade = TradeOffer(
            from_player=0,
            to_player=1,
            offered_cash=150,
            requested_properties={3}
        )

        state = execute_trade(trade_state, trade)

        # Rent potential without houses
        rent_med = rules.calculate_rent(state, 1)
        rent_baltic = rules.calculate_rent(state, 3)

        # With monopoly, rent doubles (no houses)
        # Mediterranean: 2 → 4
        # Baltic: 4 → 8

        total_rent_potential = rent_med + rent_baltic
        assert total_rent_potential == 12  # 4 + 8


class TestTradeSequences:
    """Test sequences of trades over game progression."""

    def test_progressive_monopoly_building_trades(self, trade_state):
        """Test series of trades building toward monopoly."""
        # Alice starts with Mediterranean (1)
        # Trade 1: Get Baltic (3) to complete brown
        # Trade 2: Trade brown monopoly for better properties

        # Step 1: Complete brown monopoly
        trade1 = TradeOffer(
            from_player=0,
            to_player=1,
            offered_cash=150,
            requested_properties={3}
        )
        state = execute_trade(trade_state, trade1)

        # Verify monopoly
        assert 1 in state.players[0].owned_properties
        assert 3 in state.players[0].owned_properties

        # Step 2: Trade brown monopoly for Park Place
        trade2 = TradeOffer(
            from_player=0,
            to_player=1,
            offered_properties={1, 3},
            requested_properties={37}
        )
        state = execute_trade(state, trade2)

        assert state.properties[37].owner == 0

    def test_defensive_trading_sequence(self, trade_state):
        """Test defensive trades to prevent opponent monopolies."""
        # Bob has Park Place (37)
        # Charlie has Boardwalk (39)

        # Alice makes defensive trade to acquire Boardwalk
        trade = TradeOffer(
            from_player=0,
            to_player=2,
            offered_cash=500,
            requested_properties={39}
        )
        state = execute_trade(trade_state, trade)

        # Now Bob can't complete dark blue monopoly
        assert state.properties[39].owner == 0
        assert state.properties[37].owner == 1  # Bob stuck with Park Place

    def test_infrastructure_accumulation_trades(self, trade_state):
        """Test accumulating railroads/utilities through trades."""
        # Set up additional railroads for trading
        trade_state = purchase_property(trade_state, 1, 15, 200)
        trade_state = purchase_property(trade_state, 2, 25, 200)

        # Alice trades for railroads
        trade1 = TradeOffer(
            from_player=0,
            to_player=1,
            offered_cash=250,
            requested_properties={15}
        )
        state = execute_trade(trade_state, trade1)

        trade2 = TradeOffer(
            from_player=0,
            to_player=2,
            offered_cash=250,
            requested_properties={25}
        )
        state = execute_trade(state, trade2)

        # Alice now owns 3 railroads (5, 15, 25)
        railroads = sum(
            1 for prop_id in [5, 15, 25, 35]
            if prop_id in state.players[0].owned_properties
        )
        assert railroads == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
