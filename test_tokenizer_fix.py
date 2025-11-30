"""
Test script to verify tokenizer padding fix.

Verifies that player_tokens have consistent shapes across games
with different player counts.
"""

import numpy as np
from engine.board import MonopolyBoard
from models.tokenizer import StateTokenizer
from env import MonopolyEnv


def test_consistent_shapes():
    """Test that tokenizer produces consistent shapes for different player counts."""
    print("Testing tokenizer padding fix...")
    print("="*60)

    board = MonopolyBoard()
    tokenizer = StateTokenizer(board=board, max_players=6)

    # Test with different player counts
    for num_players in [4, 5, 6]:
        print(f"\nTesting with {num_players} players:")

        # Create environment
        env = MonopolyEnv(num_players=num_players, seed=42)
        env.reset()

        # Get state
        state = env.state

        # Tokenize for each player
        for player_id in range(num_players):
            property_tokens, player_tokens, game_token = tokenizer.tokenize(state, player_id)

            print(f"  Player {player_id}:")
            print(f"    property_tokens shape: {property_tokens.shape} (expected: (40, 8))")
            print(f"    player_tokens shape:   {player_tokens.shape} (expected: (6, 8))")
            print(f"    game_token shape:      {game_token.shape} (expected: (1, 5))")

            # Verify shapes
            assert property_tokens.shape == (40, 8), f"Wrong property_tokens shape: {property_tokens.shape}"
            assert player_tokens.shape == (6, 8), f"Wrong player_tokens shape: {player_tokens.shape}"
            assert game_token.shape == (1, 5), f"Wrong game_token shape: {game_token.shape}"

            # Verify padding (players beyond num_players should be all zeros)
            for padded_player_id in range(num_players, 6):
                assert np.all(player_tokens[padded_player_id] == 0), \
                    f"Padded player {padded_player_id} should be all zeros"

        env.close()
        print(f"  [OK] All players have consistent shapes with {num_players} players")

    print("\n" + "="*60)
    print("[OK] All tests passed! Tokenizer produces consistent shapes.")
    print("  Player tokens are always (6, 8), padded with zeros for games with <6 players.")


def test_batch_creation():
    """Test that we can create batches from mixed player count observations."""
    print("\n\nTesting batch creation with mixed player counts...")
    print("="*60)

    board = MonopolyBoard()
    tokenizer = StateTokenizer(board=board, max_players=6)

    # Collect observations from games with different player counts
    all_property_tokens = []
    all_player_tokens = []
    all_game_tokens = []

    for num_players in [4, 5, 6, 4, 5]:  # Mixed
        env = MonopolyEnv(num_players=num_players, seed=42 + num_players)
        env.reset()
        state = env.state

        property_tokens, player_tokens, game_token = tokenizer.tokenize(state, 0)
        all_property_tokens.append(property_tokens)
        all_player_tokens.append(player_tokens)
        all_game_tokens.append(game_token)

        env.close()

    # Try to create numpy arrays (this would fail before the fix)
    try:
        property_batch = np.array(all_property_tokens)
        player_batch = np.array(all_player_tokens)
        game_batch = np.array(all_game_tokens)

        print(f"\n[OK] Successfully created batches:")
        print(f"  property_batch shape: {property_batch.shape} (expected: (5, 40, 8))")
        print(f"  player_batch shape:   {player_batch.shape} (expected: (5, 6, 8))")
        print(f"  game_batch shape:     {game_batch.shape} (expected: (5, 1, 5))")

        assert property_batch.shape == (5, 40, 8)
        assert player_batch.shape == (5, 6, 8)
        assert game_batch.shape == (5, 1, 5)

        print("\n" + "="*60)
        print("[OK] Batch creation test passed!")

    except Exception as e:
        print(f"\n[FAILED] FAILED to create batches: {e}")
        raise


if __name__ == "__main__":
    test_consistent_shapes()
    test_batch_creation()
    print("\n" + "="*60)
    print("ALL TESTS PASSED!")
    print("The tokenizer padding fix is working correctly.")
    print("="*60)
