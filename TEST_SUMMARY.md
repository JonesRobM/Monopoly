# Comprehensive Monopoly Test Suite

## Overview

Created comprehensive unit tests for all Monopoly game operations with extensive coverage of trading mechanics and reward calculations.

**Total Tests**: 90 tests across 2 files
**Status**: ✅ All tests passing

## Test Files

### 1. `engine/tests/test_operations.py` (53 tests)

Comprehensive tests for core Monopoly operations:

#### Property Operations (6 tests)
- Basic property purchasing
- Railroad and utility purchases
- Multiple property purchases
- Monopoly set completion
- Cash deduction validation

#### Rent Calculation (8 tests)
- Basic property rent
- Monopoly rent doubling
- House/hotel rent scaling (1-5 houses)
- Railroad rent based on number owned (1-4)
- Utility rent with dice rolls
- Mortgaged property (no rent)
- Own property handling

#### Rent Payment (3 tests)
- Basic rent transfers between players
- High rent amounts (hotels)
- Multi-player game rent flows

#### House Building (5 tests)
- Single house construction
- Progressive building to hotel
- Monopoly requirement validation
- Even building rule enforcement
- House shortage scenarios

#### Mortgaging (3 tests)
- Property mortgaging mechanics
- Unmortgaging with interest (110%)
- Building restrictions on mortgaged properties

#### Jail Mechanics (5 tests)
- Sending players to jail
- Jail release mechanics
- Fine payment
- Get Out of Jail Free cards
- Jail turn tracking

#### Bankruptcy (3 tests)
- Bankruptcy to bank (properties return to unowned)
- Bankruptcy to creditor (asset transfer)
- House/hotel returns to bank

#### Movement (4 tests)
- Forward movement
- Passing GO (salary collection)
- Landing on GO
- Board wraparound (position % 40)

#### Turn Management (3 tests)
- Basic turn advancement
- Turn cycling through players
- Bankrupt player handling

#### Cash Transfers (4 tests)
- Player-to-player transfers
- Bank payments
- Bank receipts
- Large transfers

#### Game State (2 tests)
- Phase transitions
- Initial game phase

#### Property Ownership (3 tests)
- Multiple properties per player
- Property distribution
- Ownership tracking

#### Edge Cases (4 tests)
- Zero cash scenarios
- Maximum houses on properties
- Single player remaining
- Mortgaged properties with houses

---

### 2. `engine/tests/test_trades.py` (37 tests)

Extensive trade testing with reward/penalty calculations:

#### Simple Trades (4 tests)
- Property-for-property swaps
- Property-for-cash sales
- Cash-for-property purchases
- Pure cash transfers

#### Complex Trades (3 tests)
- Multi-property exchanges
- Properties and cash both directions
- Three+ property trades with cash balancing

#### Strategic Trades (4 tests)
- **Monopoly completion trades** - Completing color sets through strategic acquisition
- **Monopoly blocking trades** - Preventing opponents from completing sets
- **Infrastructure collection** - Accumulating railroads/utilities
- **Mutual benefit trades** - Trades that help both players achieve objectives

#### Trade Reward Calculation (6 tests)
- **Fair value trades** - Equal value exchanges (net reward = 0)
- **Profitable trades** - Gaining more value than given (positive reward)
- **Losing trades** - Giving more than receiving (penalty)
- **Monopoly completion bonus** - Extra reward for completing sets (+1000)
- **Cash-only trade values** - Pure monetary exchanges
- **Property with houses** - Value includes base price + (houses × cost)

#### Multi-Player Trades (3 tests)
- Trades between non-current players
- Sequential trades of same property
- Three-way circular trade simulations

#### Edge Cases (5 tests)
- Mortgaged property trades
- Insufficient cash scenarios
- Empty trades (no assets exchanged)
- Invalid trades (same property both ways)
- Trading all cash

#### Trade Value Metrics (4 tests)
- **Railroad collection value** - Rent scaling with multiple railroads
- **Utility pair value** - Owning both utilities (4× vs 10× multiplier)
- **Color set completion** - Monopoly enabling building rights
- **Opponent monopoly denial** - Strategic blocking value

#### Trade Reward Components (5 tests)
- Property value calculation (purchase price)
- House value component (base + houses × cost)
- Monopoly value bonus (+1000 reward)
- Cash component tracking
- Rent potential evaluation

#### Trade Sequences (3 tests)
- Progressive monopoly building through multiple trades
- Defensive trading to prevent opponent monopolies
- Infrastructure accumulation strategies

---

## Trade Reward System

### Value Calculation Formula

```
Trade Value =
    (Properties Received - Properties Given) +
    (Houses on Received - Houses on Given) × House Cost +
    (Cash Received - Cash Given) +
    Strategic Bonuses/Penalties
```

### Strategic Bonuses

| Event | Reward |
|-------|--------|
| Complete monopoly | +1000 |
| Block opponent monopoly | +300 |
| Opponent completes monopoly | -500 |
| Mortgage property | -0.5 |
| Unmortgage property | +0.5 |

### Property Values

- **Base value**: Purchase price
- **With houses**: Base + (num_houses × house_cost)
- **Railroads**: Rent value based on collection (25/50/100/200)
- **Utilities**: Value based on dice multiplier (4× or 10×)

### Example Trade Calculations

#### Example 1: Fair Trade
```
Alice trades Mediterranean Ave (value: 60)
Bob trades Baltic Ave (value: 60)
Net value change: 0
Reward: 0
```

#### Example 2: Profitable Trade
```
Alice trades Mediterranean Ave (60) + $200 cash
Alice receives Park Place (350)
Net value change: 350 - 60 - 200 = +90
Reward: +90
```

#### Example 3: Monopoly Completion
```
Alice trades $150
Alice receives Baltic Ave (60)
Alice now owns complete brown monopoly
Net value: -150 + 60 = -90
Monopoly bonus: +1000
Total reward: -90 + 1000 = +910
```

---

## Running the Tests

### Run all tests
```bash
pytest engine/tests/test_operations.py engine/tests/test_trades.py -v
```

### Run specific test categories
```bash
# Property operations only
pytest engine/tests/test_operations.py::TestPropertyPurchasing -v

# Trade tests only
pytest engine/tests/test_trades.py -v

# Specific test
pytest engine/tests/test_trades.py::TestTradeRewardCalculation::test_monopoly_completion_reward_bonus -v
```

### Quick test count
```bash
pytest engine/tests/test_operations.py engine/tests/test_trades.py --co -q
```

---

## Test Coverage

### Core Operations: ✅ Complete
- ✅ Property purchasing (all types)
- ✅ Rent calculation (all scenarios)
- ✅ Building mechanics
- ✅ Mortgaging
- ✅ Jail mechanics
- ✅ Bankruptcy
- ✅ Movement and turns
- ✅ Cash transfers

### Trading System: ✅ Extensive
- ✅ Simple trades (4 types)
- ✅ Complex multi-asset trades
- ✅ Strategic trades (monopoly completion/blocking)
- ✅ Reward/penalty calculations
- ✅ Multi-player scenarios
- ✅ Edge cases
- ✅ Value metrics
- ✅ Trade sequences

### Validation
- All 90 tests passing
- No warnings or errors
- Execution time: ~3 seconds

---

## Key Testing Principles Applied

1. **Deterministic**: All tests use fixed values, no randomness
2. **Isolated**: Each test is independent
3. **Comprehensive**: Edge cases and boundary conditions covered
4. **Clear**: Descriptive test names and documentation
5. **Fast**: Entire suite runs in under 3 seconds

---

## Future Test Additions

Potential areas for additional testing:
- Card effects (Chance and Community Chest)
- Auction mechanics
- Multi-turn game sequences
- AI agent decision-making
- Performance benchmarks
- Integration tests with PettingZoo environment
- Network/multiplayer scenarios

---

## Notes

- Tests use fixtures for consistent initial states
- Trade tests account for fixture property purchases in cash calculations
- Reward calculations validated against `CustomRewardShaper` class
- All monetary values match official Monopoly rules
