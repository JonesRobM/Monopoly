"""
Tests for animation system.

Verifies animation timing and interpolation.
"""

import pytest
import time
from visualization.animation import (
    Animation, PlayerMoveAnimation, AnimationManager
)


class TestAnimation:
    """Tests for Animation base class."""

    def test_animation_init(self):
        """Test animation initialization."""
        start_time = time.time()
        anim = Animation(start_time=start_time, duration=1.0)

        assert anim.start_time == start_time
        assert anim.duration == 1.0
        assert not anim.is_complete

    def test_animation_update_progress(self):
        """Test animation update calculates correct progress."""
        start_time = time.time()
        anim = Animation(start_time=start_time, duration=1.0)

        # At start
        progress = anim.update(start_time)
        assert progress == 0.0
        assert not anim.is_complete

        # Halfway
        progress = anim.update(start_time + 0.5)
        assert progress == pytest.approx(0.5)
        assert not anim.is_complete

        # Complete
        progress = anim.update(start_time + 1.0)
        assert progress == 1.0
        assert anim.is_complete

        # After complete
        progress = anim.update(start_time + 2.0)
        assert progress == 1.0
        assert anim.is_complete


class TestPlayerMoveAnimation:
    """Tests for PlayerMoveAnimation."""

    def test_init(self):
        """Test player move animation initialization."""
        start_time = time.time()
        anim = PlayerMoveAnimation(
            start_time=start_time,
            duration=0.5,
            player_id=0,
            from_position=0,
            to_position=5,
            from_coords=(100, 100),
            to_coords=(200, 200)
        )

        assert anim.player_id == 0
        assert anim.from_position == 0
        assert anim.to_position == 5
        assert anim.from_coords == (100, 100)
        assert anim.to_coords == (200, 200)

    def test_get_current_position_start(self):
        """Test position at start of animation."""
        start_time = time.time()
        anim = PlayerMoveAnimation(
            start_time=start_time,
            duration=0.5,
            player_id=0,
            from_position=0,
            to_position=5,
            from_coords=(100, 100),
            to_coords=(200, 200)
        )

        x, y = anim.get_current_position(0.0)
        assert x == 100
        assert y == 100

    def test_get_current_position_end(self):
        """Test position at end of animation."""
        start_time = time.time()
        anim = PlayerMoveAnimation(
            start_time=start_time,
            duration=0.5,
            player_id=0,
            from_position=0,
            to_position=5,
            from_coords=(100, 100),
            to_coords=(200, 200)
        )

        x, y = anim.get_current_position(1.0)
        assert x == 200
        assert y == 200

    def test_get_current_position_middle(self):
        """Test position in middle of animation."""
        start_time = time.time()
        anim = PlayerMoveAnimation(
            start_time=start_time,
            duration=0.5,
            player_id=0,
            from_position=0,
            to_position=5,
            from_coords=(100, 100),
            to_coords=(200, 200)
        )

        x, y = anim.get_current_position(0.5)
        # With easing, middle position won't be exactly 150
        # but should be between start and end
        assert 100 <= x <= 200
        assert 100 <= y <= 200

    def test_ease_in_out(self):
        """Test easing function."""
        # At start
        assert PlayerMoveAnimation._ease_in_out(0.0) == 0.0

        # At end
        assert PlayerMoveAnimation._ease_in_out(1.0) == 1.0

        # In middle - should be close to 0.5 but not exact due to easing
        mid = PlayerMoveAnimation._ease_in_out(0.5)
        assert 0.4 <= mid <= 0.6


class TestAnimationManager:
    """Tests for AnimationManager."""

    def test_init(self):
        """Test animation manager initialization."""
        manager = AnimationManager()

        assert len(manager.active_animations) == 0
        assert len(manager.player_move_animations) == 0

    def test_add_player_move(self):
        """Test adding player move animation."""
        manager = AnimationManager()

        manager.add_player_move(
            player_id=0,
            from_position=0,
            to_position=5,
            from_coords=(100, 100),
            to_coords=(200, 200),
            duration=0.5
        )

        assert len(manager.active_animations) == 1
        assert 0 in manager.player_move_animations
        assert manager.is_animating()

    def test_add_player_move_replaces_existing(self):
        """Test adding new animation replaces old one for same player."""
        manager = AnimationManager()

        # Add first animation
        manager.add_player_move(
            player_id=0,
            from_position=0,
            to_position=5,
            from_coords=(100, 100),
            to_coords=(200, 200),
            duration=0.5
        )

        # Add second animation for same player
        manager.add_player_move(
            player_id=0,
            from_position=5,
            to_position=10,
            from_coords=(200, 200),
            to_coords=(300, 300),
            duration=0.5
        )

        # Should only have one animation
        assert len(manager.active_animations) == 1
        assert manager.player_move_animations[0].to_position == 10

    def test_get_player_position_no_animation(self):
        """Test getting position when no animation exists."""
        manager = AnimationManager()

        pos = manager.get_player_position(0, (150, 150))
        assert pos == (150, 150)

    def test_get_player_position_with_animation(self):
        """Test getting position with active animation."""
        manager = AnimationManager()

        manager.add_player_move(
            player_id=0,
            from_position=0,
            to_position=5,
            from_coords=(100, 100),
            to_coords=(200, 200),
            duration=0.5
        )

        pos = manager.get_player_position(0, (150, 150))
        # Should get animated position, not default
        assert pos != (150, 150)

    def test_clear(self):
        """Test clearing all animations."""
        manager = AnimationManager()

        manager.add_player_move(
            player_id=0,
            from_position=0,
            to_position=5,
            from_coords=(100, 100),
            to_coords=(200, 200)
        )
        manager.add_player_move(
            player_id=1,
            from_position=10,
            to_position=15,
            from_coords=(300, 300),
            to_coords=(400, 400)
        )

        assert len(manager.active_animations) == 2

        manager.clear()

        assert len(manager.active_animations) == 0
        assert len(manager.player_move_animations) == 0
        assert not manager.is_animating()

    def test_is_animating(self):
        """Test is_animating flag."""
        manager = AnimationManager()

        assert not manager.is_animating()

        manager.add_player_move(
            player_id=0,
            from_position=0,
            to_position=5,
            from_coords=(100, 100),
            to_coords=(200, 200)
        )

        assert manager.is_animating()

        manager.clear()

        assert not manager.is_animating()
