"""
Tests for board layout calculator.

Verifies correct positioning of tiles for both 40 and 41 tile boards.
"""

import pytest
from visualization.board_layout import BoardLayout, TilePosition


class TestBoardLayout:
    """Tests for BoardLayout class."""

    def test_init_40_tiles(self):
        """Test initialization with 40 tiles (classic)."""
        layout = BoardLayout(num_tiles=40, board_size=800)

        assert layout.num_tiles == 40
        assert layout.board_size == 800
        assert len(layout.tile_positions) == 40

    def test_init_41_tiles(self):
        """Test initialization with 41 tiles (Stoke-on-Trent)."""
        layout = BoardLayout(num_tiles=41, board_size=800)

        assert layout.num_tiles == 41
        assert layout.board_size == 800
        assert len(layout.tile_positions) == 41

    def test_init_invalid_tiles(self):
        """Test initialization with invalid number of tiles."""
        with pytest.raises(ValueError, match="Unsupported number of tiles"):
            BoardLayout(num_tiles=35, board_size=800)

    def test_corner_tiles_40(self):
        """Test corner tiles are correctly marked for 40-tile board."""
        layout = BoardLayout(num_tiles=40, board_size=800)

        # Classic Monopoly corners: 0 (GO), 10 (Jail), 20 (Free Parking), 30 (Go To Jail)
        corners = [0, 10, 20, 30]

        for tile_id in corners:
            pos = layout.get_tile_position(tile_id)
            assert pos.is_corner, f"Tile {tile_id} should be a corner"

        # Check non-corners
        for tile_id in range(40):
            if tile_id not in corners:
                pos = layout.get_tile_position(tile_id)
                assert not pos.is_corner, f"Tile {tile_id} should not be a corner"

    def test_corner_tiles_41(self):
        """Test corner tiles for 41-tile board."""
        layout = BoardLayout(num_tiles=41, board_size=800)

        # Corners should be at positions 0, 10, 21, 31
        corners = [0, 10, 21, 31]

        for tile_id in corners:
            pos = layout.get_tile_position(tile_id)
            assert pos.is_corner, f"Tile {tile_id} should be a corner"

    def test_tile_sides_40(self):
        """Test tiles are on correct sides for 40-tile board."""
        layout = BoardLayout(num_tiles=40, board_size=800)

        # Bottom: 0-10
        for i in range(11):
            assert layout.get_tile_position(i).side == "bottom"

        # Left: 11-19
        for i in range(11, 20):
            assert layout.get_tile_position(i).side == "left"

        # Top: 20-30
        for i in range(20, 31):
            assert layout.get_tile_position(i).side == "top"

        # Right: 31-39
        for i in range(31, 40):
            assert layout.get_tile_position(i).side == "right"

    def test_get_tile_position(self):
        """Test get_tile_position returns valid positions."""
        layout = BoardLayout(num_tiles=40, board_size=800)

        for tile_id in range(40):
            pos = layout.get_tile_position(tile_id)

            assert isinstance(pos, TilePosition)
            assert pos.tile_id == tile_id
            assert 0 <= pos.x < 800
            assert 0 <= pos.y < 800
            assert pos.width > 0
            assert pos.height > 0

    def test_get_tile_position_invalid(self):
        """Test get_tile_position with invalid ID."""
        layout = BoardLayout(num_tiles=40, board_size=800)

        with pytest.raises(ValueError, match="Invalid tile ID"):
            layout.get_tile_position(50)

    def test_get_tile_center(self):
        """Test get_tile_center returns center coordinates."""
        layout = BoardLayout(num_tiles=40, board_size=800)

        for tile_id in range(40):
            pos = layout.get_tile_position(tile_id)
            center_x, center_y = layout.get_tile_center(tile_id)

            expected_x = pos.x + pos.width // 2
            expected_y = pos.y + pos.height // 2

            assert center_x == expected_x
            assert center_y == expected_y

    def test_get_player_offset(self):
        """Test get_player_offset for multiple players."""
        layout = BoardLayout(num_tiles=40, board_size=800)

        # Single player - no offset
        offset_x, offset_y = layout.get_player_offset(0, 0, 1)
        assert offset_x == 0
        assert offset_y == 0

        # Multiple players - should have different offsets
        offsets = []
        for i in range(4):
            offset = layout.get_player_offset(0, i, 4)
            offsets.append(offset)

        # All offsets should be different
        assert len(set(offsets)) == 4

    def test_get_center_area(self):
        """Test get_center_area returns valid rectangle."""
        layout = BoardLayout(num_tiles=40, board_size=800)

        x, y, width, height = layout.get_center_area()

        assert x > 0
        assert y > 0
        assert width > 0
        assert height > 0
        assert x + width <= 800
        assert y + height <= 800

    def test_all_positions_within_bounds(self):
        """Test all tile positions are within board bounds."""
        layout = BoardLayout(num_tiles=40, board_size=800)

        for tile_id in range(40):
            pos = layout.get_tile_position(tile_id)

            assert pos.x >= 0
            assert pos.y >= 0
            assert pos.x + pos.width <= 800
            assert pos.y + pos.height <= 800

    def test_corner_sizes_equal(self):
        """Test all corner tiles have equal size."""
        layout = BoardLayout(num_tiles=40, board_size=800)

        corners = [0, 10, 20, 30]
        corner_sizes = []

        for tile_id in corners:
            pos = layout.get_tile_position(tile_id)
            corner_sizes.append((pos.width, pos.height))

        # All corners should be square and same size
        assert len(set(corner_sizes)) == 1
        width, height = corner_sizes[0]
        assert width == height  # Square

    def test_different_board_sizes(self):
        """Test layout works with different board sizes."""
        for board_size in [600, 800, 1000]:
            layout = BoardLayout(num_tiles=40, board_size=board_size)

            assert layout.board_size == board_size
            assert len(layout.tile_positions) == 40

            # All positions should be within bounds
            for tile_id in range(40):
                pos = layout.get_tile_position(tile_id)
                assert pos.x + pos.width <= board_size
                assert pos.y + pos.height <= board_size
