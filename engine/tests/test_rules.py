"""
Unit tests for game rules engine.
"""

import pytest
from engine.state import GameState, PlayerState, PropertyState, GameConfig
from engine.board import MonopolyBoard, PropertyGroup
from engine.rules import RulesEngine


@pytest.fixture
def board():
    """Create board fixture."""
    return MonopolyBoard()


@pytest.fixture
def config():
    """Create config fixture."""
    return GameConfig()


@pytest.fixture
def rules(board, config):
    """Create rules engine fixture."""
    return RulesEngine(board, config)


class TestRentCalculation:
    """Tests for rent calculation."""

    def test_basic_property_rent(self, rules):
        """Test basic property rent without monopoly."""
        players = [
            PlayerState(player_id=0, name="Player 1")
        ]
        players[0].owned_properties = {1}
        properties = {1: PropertyState(tile_id=1, owner=0, num_houses=0)}
        state = GameState(players=players, properties=properties)

        rent = rules.calculate_rent(state, 1)
        assert rent == 2  # Mediterranean base rent

    def test_monopoly_doubles_rent(self, rules):
        """Test rent doubles with monopoly and no houses."""
        players = [PlayerState(player_id=0, name="Player 1")]
        players[0].owned_properties = {1, 3}  # Both brown properties
        properties = {
            1: PropertyState(tile_id=1, owner=0, num_houses=0),
            3: PropertyState(tile_id=3, owner=0, num_houses=0)
        }
        state = GameState(players=players, properties=properties)

        rent = rules.calculate_rent(state, 1)
        assert rent == 4  # Base rent (2) × 2

    def test_rent_with_houses(self, rules):
        """Test rent with houses."""
        players = [PlayerState(player_id=0, name="Player 1")]
        players[0].owned_properties = {1, 3}
        properties = {
            1: PropertyState(tile_id=1, owner=0, num_houses=2),
            3: PropertyState(tile_id=3, owner=0, num_houses=0)
        }
        state = GameState(players=players, properties=properties)

        rent = rules.calculate_rent(state, 1)
        assert rent == 30  # Mediterranean with 2 houses

    def test_rent_with_hotel(self, rules):
        """Test rent with hotel."""
        players = [PlayerState(player_id=0, name="Player 1")]
        players[0].owned_properties = {1, 3}
        properties = {
            1: PropertyState(tile_id=1, owner=0, num_houses=5),  # Hotel
            3: PropertyState(tile_id=3, owner=0, num_houses=0)
        }
        state = GameState(players=players, properties=properties)

        rent = rules.calculate_rent(state, 1)
        assert rent == 250  # Mediterranean with hotel

    def test_no_rent_on_mortgaged(self, rules):
        """Test no rent on mortgaged property."""
        players = [PlayerState(player_id=0, name="Player 1")]
        players[0].owned_properties = {1}
        properties = {1: PropertyState(tile_id=1, owner=0, is_mortgaged=True)}
        state = GameState(players=players, properties=properties)

        rent = rules.calculate_rent(state, 1)
        assert rent == 0

    def test_railroad_rent(self, rules):
        """Test railroad rent calculation."""
        players = [PlayerState(player_id=0, name="Player 1")]
        players[0].owned_properties = {5, 15}  # 2 railroads
        properties = {
            5: PropertyState(tile_id=5, owner=0),
            15: PropertyState(tile_id=15, owner=0)
        }
        state = GameState(players=players, properties=properties)

        rent = rules.calculate_rent(state, 5)
        assert rent == 50  # 2 railroads

    def test_utility_rent(self, rules):
        """Test utility rent calculation."""
        players = [PlayerState(player_id=0, name="Player 1")]
        players[0].owned_properties = {12}  # 1 utility
        properties = {12: PropertyState(tile_id=12, owner=0)}
        state = GameState(players=players, properties=properties)

        rent = rules.calculate_rent(state, 12, dice_roll=7)
        assert rent == 28  # 7 × 4


class TestBuildingRules:
    """Tests for building rules."""

    def test_can_build_with_monopoly(self, rules):
        """Test can build when owning monopoly."""
        players = [PlayerState(player_id=0, name="Player 1", cash=1000)]
        players[0].owned_properties = {1, 3}  # Brown monopoly
        properties = {
            1: PropertyState(tile_id=1, owner=0, num_houses=0),
            3: PropertyState(tile_id=3, owner=0, num_houses=0)
        }
        state = GameState(players=players, properties=properties)

        assert rules.can_build_house(state, 0, 1)

    def test_cannot_build_without_monopoly(self, rules):
        """Test cannot build without monopoly."""
        players = [PlayerState(player_id=0, name="Player 1", cash=1000)]
        players[0].owned_properties = {1}  # Only 1 of 2 brown properties
        properties = {1: PropertyState(tile_id=1, owner=0, num_houses=0)}
        state = GameState(players=players, properties=properties)

        assert not rules.can_build_house(state, 0, 1)

    def test_cannot_build_on_mortgaged(self, rules):
        """Test cannot build on mortgaged property."""
        players = [PlayerState(player_id=0, name="Player 1", cash=1000)]
        players[0].owned_properties = {1, 3}
        properties = {
            1: PropertyState(tile_id=1, owner=0, is_mortgaged=True),
            3: PropertyState(tile_id=3, owner=0, num_houses=0)
        }
        state = GameState(players=players, properties=properties)

        assert not rules.can_build_house(state, 0, 1)

    def test_must_build_evenly(self, rules):
        """Test must build evenly across monopoly."""
        players = [PlayerState(player_id=0, name="Player 1", cash=1000)]
        players[0].owned_properties = {1, 3}
        properties = {
            1: PropertyState(tile_id=1, owner=0, num_houses=2),
            3: PropertyState(tile_id=3, owner=0, num_houses=0)
        }
        state = GameState(players=players, properties=properties)

        # Cannot build on property 1 (already has 2 more than property 3)
        assert not rules.can_build_house(state, 0, 1)

        # Can build on property 3
        assert rules.can_build_house(state, 0, 3)

    def test_cannot_build_without_cash(self, rules):
        """Test cannot build without enough cash."""
        players = [PlayerState(player_id=0, name="Player 1", cash=10)]
        players[0].owned_properties = {1, 3}
        properties = {
            1: PropertyState(tile_id=1, owner=0, num_houses=0),
            3: PropertyState(tile_id=3, owner=0, num_houses=0)
        }
        state = GameState(players=players, properties=properties)

        # Mediterranean houses cost $50
        assert not rules.can_build_house(state, 0, 1)

    def test_cannot_exceed_hotel(self, rules):
        """Test cannot build beyond hotel."""
        players = [PlayerState(player_id=0, name="Player 1", cash=1000)]
        players[0].owned_properties = {1, 3}
        properties = {
            1: PropertyState(tile_id=1, owner=0, num_houses=5),  # Hotel
            3: PropertyState(tile_id=3, owner=0, num_houses=0)
        }
        state = GameState(players=players, properties=properties)

        assert not rules.can_build_house(state, 0, 1)

    def test_can_sell_house(self, rules):
        """Test can sell house."""
        players = [PlayerState(player_id=0, name="Player 1")]
        players[0].owned_properties = {1, 3}
        properties = {
            1: PropertyState(tile_id=1, owner=0, num_houses=2),
            3: PropertyState(tile_id=3, owner=0, num_houses=0)
        }
        state = GameState(players=players, properties=properties)

        assert rules.can_sell_house(state, 0, 1)

    def test_must_sell_evenly(self, rules):
        """Test must sell evenly across monopoly."""
        players = [PlayerState(player_id=0, name="Player 1")]
        players[0].owned_properties = {1, 3}
        properties = {
            1: PropertyState(tile_id=1, owner=0, num_houses=0),
            3: PropertyState(tile_id=3, owner=0, num_houses=2)
        }
        state = GameState(players=players, properties=properties)

        # Cannot sell from property 1 (has fewer houses)
        assert not rules.can_sell_house(state, 0, 1)

        # Can sell from property 3 (has most houses)
        assert rules.can_sell_house(state, 0, 3)


class TestMortgageRules:
    """Tests for mortgage rules."""

    def test_can_mortgage_unencumbered(self, rules):
        """Test can mortgage property without houses."""
        players = [PlayerState(player_id=0, name="Player 1")]
        players[0].owned_properties = {1}
        properties = {1: PropertyState(tile_id=1, owner=0, num_houses=0)}
        state = GameState(players=players, properties=properties)

        assert rules.can_mortgage(state, 0, 1)

    def test_cannot_mortgage_with_houses(self, rules):
        """Test cannot mortgage property with houses."""
        players = [PlayerState(player_id=0, name="Player 1")]
        players[0].owned_properties = {1}
        properties = {1: PropertyState(tile_id=1, owner=0, num_houses=2)}
        state = GameState(players=players, properties=properties)

        assert not rules.can_mortgage(state, 0, 1)

    def test_cannot_mortgage_already_mortgaged(self, rules):
        """Test cannot mortgage already mortgaged property."""
        players = [PlayerState(player_id=0, name="Player 1")]
        players[0].owned_properties = {1}
        properties = {1: PropertyState(tile_id=1, owner=0, is_mortgaged=True)}
        state = GameState(players=players, properties=properties)

        assert not rules.can_mortgage(state, 0, 1)

    def test_can_unmortgage_with_cash(self, rules):
        """Test can unmortgage with sufficient cash."""
        players = [PlayerState(player_id=0, name="Player 1", cash=50)]
        players[0].owned_properties = {1}
        properties = {1: PropertyState(tile_id=1, owner=0, is_mortgaged=True)}
        state = GameState(players=players, properties=properties)

        # Mediterranean mortgage value is $30, unmortgage is $33 (110%)
        assert rules.can_unmortgage(state, 0, 1)

    def test_cannot_unmortgage_without_cash(self, rules):
        """Test cannot unmortgage without sufficient cash."""
        players = [PlayerState(player_id=0, name="Player 1", cash=10)]
        players[0].owned_properties = {1}
        properties = {1: PropertyState(tile_id=1, owner=0, is_mortgaged=True)}
        state = GameState(players=players, properties=properties)

        assert not rules.can_unmortgage(state, 0, 1)


class TestPurchaseRules:
    """Tests for purchase rules."""

    def test_can_buy_unowned_property(self, rules):
        """Test can buy unowned property."""
        players = [PlayerState(player_id=0, name="Player 1", cash=100)]
        state = GameState(players=players, properties={})

        assert rules.can_buy_property(state, 0, 1)  # Mediterranean ($60)

    def test_cannot_buy_owned_property(self, rules):
        """Test cannot buy owned property."""
        players = [PlayerState(player_id=0, name="Player 1", cash=100)]
        properties = {1: PropertyState(tile_id=1, owner=1)}
        state = GameState(players=players, properties=properties)

        assert not rules.can_buy_property(state, 0, 1)

    def test_cannot_buy_without_cash(self, rules):
        """Test cannot buy without sufficient cash."""
        players = [PlayerState(player_id=0, name="Player 1", cash=50)]
        state = GameState(players=players, properties={})

        assert not rules.can_buy_property(state, 0, 1)  # Mediterranean ($60)


class TestAssetCalculation:
    """Tests for asset and wealth calculation."""

    def test_total_assets(self, rules):
        """Test total assets calculation."""
        players = [PlayerState(player_id=0, name="Player 1", cash=500)]
        players[0].owned_properties = {1, 3}
        properties = {
            1: PropertyState(tile_id=1, owner=0, num_houses=2),
            3: PropertyState(tile_id=3, owner=0, num_houses=0)
        }
        state = GameState(players=players, properties=properties)

        assets = rules.get_total_assets(state, 0)

        # Cash (500) + mortgage values (30 + 30) + house value (50/2 * 2) = 610
        assert assets == 610

    def test_net_worth(self, rules):
        """Test net worth calculation."""
        players = [PlayerState(player_id=0, name="Player 1", cash=500)]
        players[0].owned_properties = {1, 3}
        properties = {
            1: PropertyState(tile_id=1, owner=0, num_houses=0),
            3: PropertyState(tile_id=3, owner=0, num_houses=0)
        }
        state = GameState(players=players, properties=properties)

        net_worth = rules.calculate_net_worth(state, 0)

        # Cash (500) + property prices (60 + 60) = 620
        assert net_worth == 620


class TestMonopolyDetection:
    """Tests for monopoly detection."""

    def test_has_brown_monopoly(self, rules):
        """Test brown property monopoly."""
        players = [PlayerState(player_id=0, name="Player 1")]
        players[0].owned_properties = {1, 3}
        state = GameState(players=players)

        monopolies = rules.get_property_groups_owned(state, 0)
        assert PropertyGroup.BROWN in monopolies

    def test_no_monopoly_partial(self, rules):
        """Test no monopoly with partial ownership."""
        players = [PlayerState(player_id=0, name="Player 1")]
        players[0].owned_properties = {1}  # Only 1 of 2
        state = GameState(players=players)

        monopolies = rules.get_property_groups_owned(state, 0)
        assert PropertyGroup.BROWN not in monopolies

    def test_railroad_monopoly(self, rules):
        """Test railroad monopoly (all 4)."""
        players = [PlayerState(player_id=0, name="Player 1")]
        players[0].owned_properties = {5, 15, 25, 35}
        state = GameState(players=players)

        monopolies = rules.get_property_groups_owned(state, 0)
        assert PropertyGroup.RAILROAD in monopolies

    def test_utility_monopoly(self, rules):
        """Test utility monopoly (both utilities)."""
        players = [PlayerState(player_id=0, name="Player 1")]
        players[0].owned_properties = {12, 28}
        state = GameState(players=players)

        monopolies = rules.get_property_groups_owned(state, 0)
        assert PropertyGroup.UTILITY in monopolies
