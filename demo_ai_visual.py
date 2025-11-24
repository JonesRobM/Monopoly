"""
Demo: Watch AI agents play Monopoly with visualization.

Simple script that shows AI agents playing on a visual board.
Press ESC to exit.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pygame
import random
from engine.board import MonopolyBoard
from engine.state import GameState, PlayerState, PropertyState
from visualization.renderer import MonopolyRenderer


def create_initial_game_state(num_players: int = 4) -> GameState:
    """Create initial game state with players at GO."""
    players = [
        PlayerState(
            player_id=i,
            name=f"AI Player {i}",
            position=0,
            cash=1500,
            owned_properties=set()
        )
        for i in range(num_players)
    ]

    return GameState(
        players=players,
        current_player_idx=0,
        turn_number=0,
        properties={},
        houses_remaining=32,
        hotels_remaining=12
    )


def simulate_turn(state: GameState, board: MonopolyBoard) -> GameState:
    """Simulate one turn of gameplay."""
    current_player_idx = state.current_player_idx
    current_player = state.players[current_player_idx]

    # Roll dice
    dice_roll = random.randint(2, 12)
    new_position = (current_player.position + dice_roll) % board.num_tiles

    # Update player position
    current_player.position = new_position

    # Pass GO bonus
    if new_position < current_player.position:
        current_player.cash += 200

    # Simple AI: Buy property if affordable and unowned
    tile = board.get_tile(new_position)
    if board.is_purchasable(new_position):
        if new_position not in state.properties:
            price = board.get_purchase_price(new_position)
            if current_player.cash >= price:
                current_player.cash -= price
                current_player.owned_properties.add(new_position)
                state.properties[new_position] = PropertyState(
                    tile_id=new_position,
                    owner=current_player_idx,
                    num_houses=0
                )
        else:
            # Pay rent if owned by another player
            property_state = state.properties[new_position]
            if property_state.owner != current_player_idx:
                owner = state.players[property_state.owner]
                # Simple rent calculation
                rent = 10 * (property_state.num_houses + 1)
                if current_player.cash >= rent:
                    current_player.cash -= rent
                    owner.cash += rent

    # Advance to next player
    state.current_player_idx = (state.current_player_idx + 1) % len(state.players)
    if state.current_player_idx == 0:
        state.turn_number += 1

    return state


def main():
    """Run the visual demo."""
    print("="*60)
    print("Monopoly AI - Visual Demo")
    print("="*60)
    print("\nPress ESC to exit")
    print("Starting game with 4 AI players...\n")

    # Create game components
    board = MonopolyBoard()
    renderer = MonopolyRenderer(board, window_width=1200, enable_animation=True)
    state = create_initial_game_state(num_players=4)

    # Game loop
    running = True
    turn_delay = 1000  # milliseconds between turns

    renderer.add_message("Game Started! Watch the AI agents play...")

    last_turn_time = pygame.time.get_ticks()

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Simulate turn
        current_time = pygame.time.get_ticks()
        if current_time - last_turn_time > turn_delay:
            old_position = state.players[state.current_player_idx].position
            state = simulate_turn(state, board)
            new_position = state.players[state.current_player_idx].position

            # Add message
            prev_player_idx = (state.current_player_idx - 1) % len(state.players)
            player_name = state.players[prev_player_idx].name
            renderer.add_message(
                f"{player_name} moved to {board.get_tile(new_position).name}"
            )

            last_turn_time = current_time

        # Render
        renderer.render(state)

        # Stop after 50 turns
        if state.turn_number >= 50:
            renderer.add_message("Demo complete! Game ended after 50 turns.")
            renderer.render(state)
            pygame.time.wait(3000)
            running = False

    print("\nDemo finished!")
    print(f"Final state after {state.turn_number} turns:")
    for player in state.players:
        print(f"  {player.name}: ${player.cash}, {len(player.owned_properties)} properties")

    renderer.close()


if __name__ == "__main__":
    main()
