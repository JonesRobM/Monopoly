"""
Demo script showing PettingZoo environment with visualization.

Demonstrates how to use the Monopoly environment with pygame rendering
to watch AI agents play in real-time.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame
import time
from env.pettingzoo_api import MonopolyEnv
from agents.random_agent import RandomAgent


class SimpleAgent:
    """
    Simple agent that takes random valid actions.

    This is a placeholder until proper heuristic agents are implemented.
    """

    def __init__(self, player_id: int):
        """
        Initialize agent.

        Args:
            player_id: Agent's player ID
        """
        self.player_id = player_id

    def select_action(self, observation: dict) -> int:
        """
        Select an action based on observation.

        Args:
            observation: Observation dict with 'observation' and 'action_mask'

        Returns:
            Action ID
        """
        import numpy as np

        action_mask = observation['action_mask']

        # Get valid actions
        valid_actions = np.where(action_mask > 0)[0]

        if len(valid_actions) == 0:
            # No valid actions, return 0 (shouldn't happen with proper masking)
            return 0

        # Select random valid action
        return np.random.choice(valid_actions)


def run_game_with_visualization(
    num_players: int = 4,
    max_steps: int = 500,
    step_delay: float = 0.5,
    render_fps: int = 60
):
    """
    Run a game with visualization.

    Args:
        num_players: Number of players
        max_steps: Maximum steps to run
        step_delay: Delay between steps in seconds
        render_fps: Rendering FPS
    """
    print("="*60)
    print("Monopoly AI - Environment with Visualization")
    print("="*60)
    print(f"Players: {num_players}")
    print(f"Max steps: {max_steps}")
    print(f"Step delay: {step_delay}s")
    print()
    print("Press ESC or close window to stop")
    print("="*60)
    print()

    # Create environment with pygame rendering
    env = MonopolyEnv(
        num_players=num_players,
        seed=42,
        render_mode="pygame"
    )

    # Create agents
    agents = [SimpleAgent(i) for i in range(num_players)]

    # Reset environment
    env.reset()

    # Initial render
    env.render()

    # Game loop
    step_count = 0
    last_step_time = time.time()
    running = True

    try:
        while running and step_count < max_steps and not env.state.game_over:
            # Handle pygame events
            if env.renderer is not None:
                running = env.renderer.handle_events()

            # Check if enough time has passed for next step
            current_time = time.time()
            if current_time - last_step_time >= step_delay:
                # Get current agent
                agent_name = env.agent_selection
                agent_idx = env.possible_agents.index(agent_name)
                agent = agents[agent_idx]

                # Get observation
                obs = env.observe(agent_name)

                # Select action
                action = agent.select_action(obs)

                # Take step
                env.step(action)

                # Render
                env.render()

                step_count += 1
                last_step_time = current_time

                # Print step info
                if step_count % 10 == 0:
                    print(f"Step {step_count}: Turn {env.state.turn_number}, "
                          f"Current player: {env.state.current_player_idx}")

            else:
                # Just render while waiting
                if env.renderer is not None:
                    env.render()
                    pygame.time.wait(int(1000 / render_fps))

    except KeyboardInterrupt:
        print("\n\nGame interrupted by user")

    # Final render
    print(f"\n\nGame finished after {step_count} steps")
    print(f"Turn number: {env.state.turn_number}")

    if env.state.game_over:
        if env.state.winner is not None:
            print(f"Winner: Player {env.state.winner}")
        else:
            print("Game over - no winner")
    else:
        print("Game stopped before completion")

    # Show final state for a bit
    if running:
        print("\nShowing final state for 5 seconds...")
        end_time = time.time() + 5.0
        while running and time.time() < end_time:
            if env.renderer is not None:
                running = env.renderer.handle_events()
                env.render()
            pygame.time.wait(int(1000 / render_fps))

    # Cleanup
    env.close()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run Monopoly game with visualization"
    )
    parser.add_argument(
        "--players",
        type=int,
        default=4,
        help="Number of players (2-6)"
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=500,
        help="Maximum number of steps"
    )
    parser.add_argument(
        "--step-delay",
        type=float,
        default=0.5,
        help="Delay between steps in seconds"
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=60,
        help="Rendering FPS"
    )

    args = parser.parse_args()

    # Validate
    if not 2 <= args.players <= 6:
        print("Error: Number of players must be between 2 and 6")
        return

    # Run game
    run_game_with_visualization(
        num_players=args.players,
        max_steps=args.max_steps,
        step_delay=args.step_delay,
        render_fps=args.fps
    )


if __name__ == "__main__":
    main()
