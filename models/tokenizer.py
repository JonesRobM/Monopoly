"""
State tokenization for structured transformer input.

Converts Monopoly game state into structured token sequences:
- Property tokens (40): One per board tile
- Player tokens (4-6): One per player in game
- Game token (1): Global game state

Total: 45-47 tokens (depending on num_players)

Each token is a feature vector that will be embedded to d_model dimensions.
"""

import numpy as np
from typing import List, Tuple
from engine.state import GameState, PropertyState, TileType
from engine.board import MonopolyBoard


class StateTokenizer:
    """
    Tokenizes Monopoly game state into structured sequences.

    Produces separate token sequences for properties, players, and game state
    that can be processed by a transformer model.
    """

    def __init__(self, board: MonopolyBoard, num_players: int = 4,
                 max_cash: float = 10000.0):
        """
        Initialize state tokenizer.

        Args:
            board: Monopoly board instance
            num_players: Number of players in game (2-6)
            max_cash: Maximum cash for normalization
        """
        self.board = board
        self.num_players = num_players
        self.max_cash = max_cash

        # Feature dimensions
        self.property_feature_dim = self._calculate_property_feature_dim()
        self.player_feature_dim = self._calculate_player_feature_dim()
        self.game_feature_dim = self._calculate_game_feature_dim()

    def _calculate_property_feature_dim(self) -> int:
        """Calculate dimensionality of property token features."""
        # Features per property:
        # - owner_id: 1 (0 = unowned, 1-6 = player ID, normalized)
        # - num_houses: 1 (0-5, normalized)
        # - is_mortgaged: 1 (0/1)
        # - property_group_id: 1 (encoded as int, normalized)
        # - purchase_price: 1 (normalized)
        # - position_on_board: 1 (0-39, normalized)
        # - base_rent: 1 (normalized)
        # - can_develop: 1 (0/1 - whether it's developable)
        return 8

    def _calculate_player_feature_dim(self) -> int:
        """Calculate dimensionality of player token features."""
        # Features per player:
        # - cash: 1 (normalized)
        # - position: 1 (0-39, normalized)
        # - is_in_jail: 1 (0/1)
        # - jail_turns: 1 (0-3, normalized)
        # - num_owned_properties: 1 (normalized)
        # - is_bankrupt: 1 (0/1)
        # - is_current_player: 1 (0/1)
        # - get_out_of_jail_cards: 1 (normalized)
        return 8

    def _calculate_game_feature_dim(self) -> int:
        """Calculate dimensionality of game token features."""
        # Features for game state:
        # - turn_number: 1 (normalized)
        # - doubles_count: 1 (0-3, normalized)
        # - houses_remaining: 1 (normalized)
        # - hotels_remaining: 1 (normalized)
        # - num_players_active: 1 (normalized)
        return 5

    def tokenize(self, state: GameState, observing_player_id: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Tokenize game state into structured sequences.

        Args:
            state: Current game state
            observing_player_id: ID of player observing (for perspective)

        Returns:
            Tuple of (property_tokens, player_tokens, game_token):
            - property_tokens: (40, property_feature_dim)
            - player_tokens: (num_players, player_feature_dim)
            - game_token: (1, game_feature_dim)
        """
        property_tokens = self.tokenize_properties(state)
        player_tokens = self.tokenize_players(state, observing_player_id)
        game_token = self.tokenize_game(state)

        return property_tokens, player_tokens, game_token

    def tokenize_properties(self, state: GameState) -> np.ndarray:
        """
        Tokenize all 40 properties.

        Args:
            state: Current game state

        Returns:
            Property tokens (40, property_feature_dim)
        """
        tokens = np.zeros((40, self.property_feature_dim), dtype=np.float32)

        for tile_id in range(40):
            tile = self.board.get_tile(tile_id)
            prop_state = state.properties.get(tile_id)

            # Owner ID (0 = unowned, 1-7 for players, normalized to 0-1)
            if prop_state and prop_state.owner is not None:
                tokens[tile_id, 0] = (prop_state.owner + 1) / 7.0
            else:
                tokens[tile_id, 0] = 0.0

            # Number of houses (0-5, where 5 = hotel)
            if prop_state:
                tokens[tile_id, 1] = prop_state.num_houses / 5.0
            else:
                tokens[tile_id, 1] = 0.0

            # Is mortgaged
            if prop_state:
                tokens[tile_id, 2] = 1.0 if prop_state.is_mortgaged else 0.0
            else:
                tokens[tile_id, 2] = 0.0

            # Property group ID (encoded as int)
            if tile.property_info:
                # Map PropertyGroup enum to int (0-12)
                group_id = list(tile.property_info.group.__class__).index(tile.property_info.group)
                tokens[tile_id, 3] = group_id / 12.0
            else:
                tokens[tile_id, 3] = 0.0

            # Purchase price (normalized)
            if tile.property_info:
                tokens[tile_id, 4] = tile.property_info.purchase_price / 400.0  # Max is Boardwalk
            elif tile.railroad_info:
                tokens[tile_id, 4] = tile.railroad_info.purchase_price / 400.0
            elif tile.utility_info:
                tokens[tile_id, 4] = tile.utility_info.purchase_price / 400.0
            else:
                tokens[tile_id, 4] = 0.0

            # Position on board (for positional encoding)
            tokens[tile_id, 5] = tile_id / 39.0

            # Base rent (normalized)
            if tile.property_info:
                tokens[tile_id, 6] = tile.property_info.base_rent / 200.0  # Rough max
            else:
                tokens[tile_id, 6] = 0.0

            # Can develop (is it a developable property?)
            can_develop = (tile.tile_type == TileType.PROPERTY)
            tokens[tile_id, 7] = 1.0 if can_develop else 0.0

        return tokens

    def tokenize_players(self, state: GameState, observing_player_id: int) -> np.ndarray:
        """
        Tokenize all players.

        Args:
            state: Current game state
            observing_player_id: ID of observing player

        Returns:
            Player tokens (num_players, player_feature_dim)
        """
        # Determine actual number of players from state
        actual_num_players = len(state.players)
        tokens = np.zeros((actual_num_players, self.player_feature_dim), dtype=np.float32)

        for i in range(actual_num_players):
            player = state.players[i]

            # Cash (normalized)
            tokens[i, 0] = min(player.cash / self.max_cash, 1.0)

            # Position (normalized)
            tokens[i, 1] = player.position / 39.0

            # Is in jail
            tokens[i, 2] = 1.0 if player.is_in_jail else 0.0

            # Jail turns (normalized)
            tokens[i, 3] = player.jail_turns / 3.0

            # Number of owned properties (normalized)
            tokens[i, 4] = len(player.owned_properties) / 40.0

            # Is bankrupt
            tokens[i, 5] = 1.0 if player.is_bankrupt else 0.0

            # Is current player (helps agent identify itself)
            tokens[i, 6] = 1.0 if i == observing_player_id else 0.0

            # Get out of jail cards (normalized)
            tokens[i, 7] = min(player.get_out_of_jail_cards / 2.0, 1.0)

        return tokens

    def tokenize_game(self, state: GameState) -> np.ndarray:
        """
        Tokenize global game state.

        Args:
            state: Current game state

        Returns:
            Game token (1, game_feature_dim)
        """
        token = np.zeros((1, self.game_feature_dim), dtype=np.float32)

        # Turn number (normalized, assume max 1000 turns)
        token[0, 0] = min(state.turn_number / 1000.0, 1.0)

        # Doubles count (normalized)
        token[0, 1] = state.doubles_count / 3.0

        # Houses remaining (normalized)
        token[0, 2] = state.houses_remaining / 32.0

        # Hotels remaining (normalized)
        token[0, 3] = state.hotels_remaining / 12.0

        # Number of active players (non-bankrupt)
        num_active = sum(1 for p in state.players if not p.is_bankrupt)
        token[0, 4] = num_active / self.num_players

        return token

    def get_total_sequence_length(self) -> int:
        """Get total sequence length (40 properties + num_players + 1 game)."""
        return 40 + self.num_players + 1

    def get_feature_dims(self) -> Tuple[int, int, int]:
        """
        Get feature dimensions for each token type.

        Returns:
            (property_feature_dim, player_feature_dim, game_feature_dim)
        """
        return (self.property_feature_dim, self.player_feature_dim, self.game_feature_dim)
