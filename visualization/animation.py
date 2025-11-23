"""
Animation system for Monopoly visualization.

Handles smooth transitions for player movement and other animated effects.
"""

from typing import Tuple, Optional, List
from dataclasses import dataclass
import time


@dataclass
class Animation:
    """Base class for animations."""
    start_time: float
    duration: float  # seconds
    is_complete: bool = False

    def update(self, current_time: float) -> float:
        """
        Update animation state.

        Args:
            current_time: Current time in seconds

        Returns:
            Progress from 0.0 to 1.0
        """
        elapsed = current_time - self.start_time
        progress = min(elapsed / self.duration, 1.0)

        if progress >= 1.0:
            self.is_complete = True

        return progress


@dataclass
class PlayerMoveAnimation(Animation):
    """Animation for player piece movement."""
    player_id: int
    from_position: int
    to_position: int
    from_coords: Tuple[int, int]
    to_coords: Tuple[int, int]

    def get_current_position(self, progress: float) -> Tuple[int, int]:
        """
        Get interpolated position.

        Args:
            progress: Animation progress (0.0 to 1.0)

        Returns:
            Current (x, y) coordinates
        """
        # Use easing function for smooth animation
        eased_progress = self._ease_in_out(progress)

        x = int(self.from_coords[0] + (self.to_coords[0] - self.from_coords[0]) * eased_progress)
        y = int(self.from_coords[1] + (self.to_coords[1] - self.from_coords[1]) * eased_progress)

        return x, y

    @staticmethod
    def _ease_in_out(t: float) -> float:
        """
        Ease-in-out cubic interpolation.

        Args:
            t: Input value (0.0 to 1.0)

        Returns:
            Eased value (0.0 to 1.0)
        """
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2


class AnimationManager:
    """
    Manages all active animations.

    Tracks player movements and other animated effects,
    updating them each frame.
    """

    def __init__(self):
        """Initialize animation manager."""
        self.active_animations: List[Animation] = []
        self.player_move_animations: dict[int, PlayerMoveAnimation] = {}

    def add_player_move(
        self,
        player_id: int,
        from_position: int,
        to_position: int,
        from_coords: Tuple[int, int],
        to_coords: Tuple[int, int],
        duration: float = 0.5
    ) -> None:
        """
        Add a player movement animation.

        Args:
            player_id: Player ID
            from_position: Starting tile position
            to_position: Ending tile position
            from_coords: Starting (x, y) coordinates
            to_coords: Ending (x, y) coordinates
            duration: Animation duration in seconds
        """
        # Cancel any existing animation for this player
        if player_id in self.player_move_animations:
            old_anim = self.player_move_animations[player_id]
            if old_anim in self.active_animations:
                self.active_animations.remove(old_anim)

        # Create new animation
        animation = PlayerMoveAnimation(
            start_time=time.time(),
            duration=duration,
            player_id=player_id,
            from_position=from_position,
            to_position=to_position,
            from_coords=from_coords,
            to_coords=to_coords
        )

        self.active_animations.append(animation)
        self.player_move_animations[player_id] = animation

    def update(self) -> None:
        """Update all active animations."""
        current_time = time.time()

        # Update all animations
        for animation in self.active_animations[:]:
            animation.update(current_time)

            # Remove completed animations
            if animation.is_complete:
                self.active_animations.remove(animation)

                # Remove from player animation tracking
                if isinstance(animation, PlayerMoveAnimation):
                    if animation.player_id in self.player_move_animations:
                        if self.player_move_animations[animation.player_id] == animation:
                            del self.player_move_animations[animation.player_id]

    def get_player_position(
        self,
        player_id: int,
        default_coords: Tuple[int, int]
    ) -> Tuple[int, int]:
        """
        Get current animated position for a player.

        Args:
            player_id: Player ID
            default_coords: Default coordinates if no animation

        Returns:
            Current (x, y) coordinates
        """
        if player_id in self.player_move_animations:
            animation = self.player_move_animations[player_id]
            current_time = time.time()
            progress = animation.update(current_time)
            return animation.get_current_position(progress)

        return default_coords

    def is_animating(self) -> bool:
        """
        Check if any animations are active.

        Returns:
            True if animations are running
        """
        return len(self.active_animations) > 0

    def clear(self) -> None:
        """Clear all animations."""
        self.active_animations.clear()
        self.player_move_animations.clear()
