"""
Multi-agent training coordinator for 10-agent Monopoly RL system.

Manages training loop with random agent selection, experience collection,
model updates, and evaluation tracking.
"""

import random
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import numpy as np
import torch

from agents.base_agent import RLAgent
from agents.reward_shaper import CustomRewardShaper
from agents.heuristics import get_heuristic_policy
from agents.alpha_schedules import AlphaSchedule, ALPHA_CONFIGS
from models.tokenizer import StateTokenizer
from models.transformer import MonopolyTransformer
from training.replay_buffer import PPOReplayBuffer
from training.ppo_trainer import PPOTrainer
from training.evaluator import Evaluator
from training.game_recorder import GameRecorder

from env import MonopolyEnv
from engine.board import MonopolyBoard
from engine.actions import ActionEncoder


class MultiAgentTrainer:
    """
    Coordinates training for 10-agent Monopoly RL system.

    Handles:
    - Random agent selection (4-6 per game)
    - Game execution via PettingZoo
    - Experience collection
    - PPO updates every N games
    - Alpha annealing
    - Evaluation and recording
    """

    def __init__(
        self,
        agent_configs: Dict[str, Dict],
        checkpoint_dir: Path,
        log_dir: Path,
        recording_dir: Path,
        update_frequency: int = 10,
        log_frequency: int = 100,
        checkpoint_frequency: int = 1000,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        seed: Optional[int] = None,
        watch_mode: bool = False,
        max_turns: int = 1000,
        min_players: int = 4,
        max_players: int = 6,
        render_mode: Optional[str] = None
    ):
        """
        Initialize multi-agent trainer.

        Args:
            agent_configs: Dict of agent configurations from player_behaviours.json
            checkpoint_dir: Directory for model checkpoints
            log_dir: Directory for training logs
            recording_dir: Directory for recorded games
            update_frequency: Update models every N games
            log_frequency: Log metrics every N games
            checkpoint_frequency: Save checkpoints every N games
            device: Device for training (cuda/cpu)
            seed: Random seed
            watch_mode: If True, print detailed turn-by-turn information
            max_turns: Maximum turns per game
            min_players: Minimum players per game
            max_players: Maximum players per game
            render_mode: Rendering mode (pygame, human, ansi, or None)
        """
        self.agent_configs = agent_configs
        self.checkpoint_dir = Path(checkpoint_dir)
        self.log_dir = Path(log_dir)
        self.recording_dir = Path(recording_dir)

        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.update_frequency = update_frequency
        self.log_frequency = log_frequency
        self.checkpoint_frequency = checkpoint_frequency
        self.device = device
        self.watch_mode = watch_mode
        self.max_turns = max_turns
        self.min_players = min_players
        self.max_players = max_players
        self.render_mode = render_mode

        # Set seeds
        self.seed = seed
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            torch.manual_seed(seed)

        # Initialize components
        self.board = MonopolyBoard()  # Create standard Monopoly board
        self.action_encoder = ActionEncoder()  # Create action encoder
        self.tokenizer = StateTokenizer(board=self.board)
        self.agents: Dict[str, RLAgent] = {}
        self.replay_buffers: Dict[str, PPOReplayBuffer] = {}
        self.ppo_trainers: Dict[str, PPOTrainer] = {}

        # Initialize all 10 agents
        self._initialize_agents()

        # Evaluation and recording
        agent_ids = list(self.agents.keys())
        self.evaluator = Evaluator(agent_ids, log_dir=self.log_dir)
        self.game_recorder = GameRecorder(
            save_dir=self.recording_dir,
            sample_rate=0.01,
            seed=seed
        )

        # Training state
        self.game_iteration = 0
        self.total_steps = 0

    def _initialize_agents(self):
        """Initialize all 10 agents with models, buffers, and trainers."""
        for agent_id, config in self.agent_configs.items():
            print(f"Initializing agent: {agent_id} ({config['name']})")

            # Create agent (it creates reward_shaper, heuristic_policy, alpha_schedule internally)
            agent = RLAgent(
                agent_id=agent_id,
                agent_config=config,
                board=self.board,
                action_encoder=self.action_encoder,
                total_training_games=10000  # Will be updated in train()
            )

            # Create model
            model = MonopolyTransformer(
                num_actions=562,
                d_model=128,
                nhead=4,
                num_layers=3
            ).to(self.device)

            # Create replay buffer
            replay_buffer = PPOReplayBuffer(max_size=10000)

            # Create PPO trainer
            ppo_trainer = PPOTrainer(
                model=model,
                learning_rate=3e-4,
                clip_epsilon=0.2,
                value_coef=0.5,
                entropy_coef=0.01,
                max_grad_norm=0.5,
                num_epochs=4,
                minibatch_size=64
            )

            # Attach model, tokenizer, and replay buffer to agent
            agent.model = model
            agent.tokenizer = self.tokenizer
            agent.replay_buffer = replay_buffer

            self.agents[agent_id] = agent
            self.replay_buffers[agent_id] = replay_buffer
            self.ppo_trainers[agent_id] = ppo_trainer

    def select_game_participants(self) -> List[str]:
        """
        Randomly select agents for a game based on min_players and max_players.

        Returns:
            List of agent IDs
        """
        num_players = random.randint(self.min_players, self.max_players)
        agent_ids = list(self.agents.keys())
        return random.sample(agent_ids, num_players)

    def run_game(
        self,
        participants: List[str],
        env_seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Run a single game with selected agents.

        Args:
            participants: List of agent IDs
            env_seed: Seed for environment

        Returns:
            Dict with game results
        """
        num_players = len(participants)

        # Print game start
        print(f"\n[Game {self.game_iteration}] Starting with {num_players} players: {', '.join(participants)}")

        # Get player display names (use agent names)
        player_display_names = [self.agents[agent_id].name for agent_id in participants]

        # Create environment
        env = MonopolyEnv(
            num_players=num_players,
            seed=env_seed,
            max_turns=self.max_turns,
            render_mode=self.render_mode,
            player_names=player_display_names
        )
        env.reset()

        # Map agent IDs to player indices
        agent_to_player = {agent_id: i for i, agent_id in enumerate(participants)}
        player_to_agent = {i: agent_id for agent_id, i in agent_to_player.items()}

        # Start recording if selected
        alpha_values = {
            agent_id: self.agents[agent_id].alpha_schedule.get_alpha(self.game_iteration)
            for agent_id in participants
        }
        self.game_recorder.start_recording(
            game_id=self.game_iteration,
            game_iteration=self.game_iteration,
            participants=participants,
            alpha_values=alpha_values
        )

        # Track game state
        prev_states = {}  # For reward calculation
        episode_rewards = {agent_id: 0.0 for agent_id in participants}
        step_count = 0
        turn_count = 0
        last_turn_report = 0

        # Game loop
        for agent_name in env.agent_iter():
            observation, reward, termination, truncation, info = env.last()

            # Get player index and agent ID
            player_id = int(agent_name.split('_')[1])
            agent_id = player_to_agent[player_id]
            agent = self.agents[agent_id]

            # Determine action
            if termination or truncation:
                action = None
            else:
                # Get current state from environment
                current_state = env.state
                prev_state = prev_states.get(agent_id)

                # Get observation components
                obs_dict = observation

                # Get action from agent
                action_mask = obs_dict['action_mask']
                action = agent.get_action(
                    obs_dict,
                    action_mask,
                    current_state,
                    player_id,
                    deterministic=False
                )

                # Calculate custom reward
                if prev_state is not None and current_state is not None:
                    custom_reward = agent.calculate_reward(
                        current_state,
                        prev_state,
                        player_id
                    )
                else:
                    custom_reward = 0.0

                episode_rewards[agent_id] += custom_reward

                # Get value estimate and log prob using tokenizer
                if agent.tokenizer is not None:
                    # Tokenize state
                    property_tokens, player_tokens, game_token = agent.tokenizer.tokenize(current_state, player_id)

                    # Get model device
                    model_device = next(agent.model.parameters()).device

                    # Convert to tensors and add batch dimension, create directly on target device
                    property_tokens = torch.tensor(property_tokens, dtype=torch.float32, device=model_device).unsqueeze(0)
                    player_tokens = torch.tensor(player_tokens, dtype=torch.float32, device=model_device).unsqueeze(0)
                    game_token = torch.tensor(game_token, dtype=torch.float32, device=model_device).unsqueeze(0)

                    # Get value estimate and log prob (combined call for efficiency)
                    with torch.no_grad():
                        _, log_prob_tensor, value_tensor = agent.model.get_action_and_value(property_tokens, player_tokens, game_token)
                        value = value_tensor.item()
                        log_prob = log_prob_tensor.item()
                else:
                    # Fallback if no tokenizer
                    value = 0.0
                    log_prob = -1.0

                # Store experience
                agent.store_experience(
                    obs_dict,
                    action,
                    custom_reward,
                    value,
                    log_prob,
                    done=False
                )

                # Record step for visualization
                if current_state is not None:
                    action_name = f"ACTION_{action}"  # Could map to readable names
                    self.game_recorder.record_step(
                        step_number=step_count,
                        player_id=player_id,
                        action=action,
                        action_name=action_name,
                        reward=custom_reward,
                        state=current_state
                    )

                step_count += 1

                # Print progress in watch mode - show every action
                if self.watch_mode and current_state is not None:
                    print(f"  Step {step_count}: {agent_id} (player {player_id}) - Turn {current_state.turn_number}")
                    current_turn = current_state.turn_number
                    if current_turn > turn_count:
                        turn_count = current_turn

                # Update previous state
                if current_state is not None:
                    prev_states[agent_id] = current_state

            # Step environment
            env.step(action)

            # Render the game state after each action when in render mode
            if self.render_mode is not None:
                env.render()

            # Progress indicator every 50 steps (not in watch mode)
            if not self.watch_mode and step_count > 0 and step_count % 50 == 0:
                if env.state is not None:
                    current_turn = env.state.turn_number
                    active_players = sum(1 for p in env.state.players if not p.is_bankrupt)
                    print(f"  Step {step_count}, Turn {current_turn}, {active_players}/{num_players} players active")

        # Determine winner (player with most cash + property value)
        final_state = env.state
        if final_state is not None and hasattr(final_state, 'players'):
            player_values = []
            for i, player in enumerate(final_state.players):
                if not player.is_bankrupt:
                    # Simple valuation: cash + properties * 100
                    value = player.cash + len(player.properties) * 100
                    player_values.append((i, value))

            if player_values:
                winner_player_id = max(player_values, key=lambda x: x[1])[0]
                winner_id = player_to_agent[winner_player_id]
            else:
                # All bankrupt, first player wins
                winner_id = participants[0]
        else:
            winner_id = participants[0]

        # Finish recording
        self.game_recorder.finish_recording(
            winner_id=winner_id,
            final_rewards=episode_rewards
        )

        # Print game summary
        final_turn = final_state.turn_number if final_state is not None else 0
        print(f"[Game {self.game_iteration}] Finished! Winner: {winner_id}, Turns: {final_turn}, Steps: {step_count}")

        # Close environment (clean up renderer if applicable)
        env.close()

        return {
            'participants': participants,
            'winner': winner_id,
            'rewards': episode_rewards,
            'steps': step_count
        }

    def update_models(self):
        """Update all agent models using PPO."""
        print(f"\n[Game {self.game_iteration}] Updating models...")

        for agent_id, agent in self.agents.items():
            replay_buffer = self.replay_buffers[agent_id]
            ppo_trainer = self.ppo_trainers[agent_id]

            # Skip if buffer too small
            if replay_buffer.size() < 64:
                continue

            # Get full batch
            batch = replay_buffer.get_batch(batch_size=None)

            # Update model
            losses = ppo_trainer.update(batch)

            # Clear buffer
            replay_buffer.clear()

            print(f"  {agent_id}: policy_loss={losses['policy_loss']:.4f}, "
                  f"value_loss={losses['value_loss']:.4f}, "
                  f"entropy={losses['entropy']:.4f}")

    def train(
        self,
        num_games: int,
        start_game: int = 0
    ):
        """
        Main training loop.

        Args:
            num_games: Total number of games to train
            start_game: Starting game iteration (for resuming)
        """
        print(f"\n{'='*60}")
        print(f"Starting Training: {num_games} games")
        print(f"Update frequency: every {self.update_frequency} games")
        print(f"Log frequency: every {self.log_frequency} games")
        print(f"Checkpoint frequency: every {self.checkpoint_frequency} games")
        print(f"Device: {self.device}")
        print(f"{'='*60}\n")

        # Update alpha schedules with actual total games
        for agent in self.agents.values():
            agent.alpha_schedule.total_games = num_games

        self.game_iteration = start_game

        for game_num in range(start_game, start_game + num_games):
            self.game_iteration = game_num

            # Select participants
            participants = self.select_game_participants()

            # Run game
            game_result = self.run_game(
                participants,
                env_seed=None  # Random each game
            )

            # Record result
            self.evaluator.record_game_result(
                participants=game_result['participants'],
                winner_id=game_result['winner'],
                rewards=game_result['rewards']
            )

            # Update alpha values for all agents
            for agent in self.agents.values():
                agent.current_game_iteration = self.game_iteration

            # Print maximum rewards every 10 games
            if (game_num + 1) % 10 == 0:
                self.evaluator.print_max_rewards(game_iteration=game_num + 1)

            # Update models every N games
            if (game_num + 1) % self.update_frequency == 0:
                self.update_models()

            # Log metrics every N games
            if (game_num + 1) % self.log_frequency == 0:
                print(f"\n{'='*60}")
                print(f"Game {game_num + 1}/{start_game + num_games}")
                print(f"{'='*60}")
                self.evaluator.log_metrics(game_iteration=game_num + 1, verbose=True)

                # Print alpha values
                print("\nAlpha values:")
                for agent_id, agent in self.agents.items():
                    alpha = agent.alpha_schedule.get_alpha(game_num)
                    print(f"  {agent_id}: {alpha:.4f}")

                print(f"{'='*60}\n")

            # Save checkpoints every N games
            if (game_num + 1) % self.checkpoint_frequency == 0:
                self.save_checkpoints(game_num + 1)

        print("\n" + "="*60)
        print("Training Complete!")
        print("="*60)

        # Final evaluation
        self.evaluator.log_metrics(game_iteration=start_game + num_games, verbose=True)

        # Save final checkpoints
        self.save_checkpoints(start_game + num_games)

    def save_checkpoints(self, game_iteration: int):
        """
        Save model checkpoints for all agents.

        Args:
            game_iteration: Current game iteration
        """
        print(f"\n[Game {game_iteration}] Saving checkpoints...")

        for agent_id, agent in self.agents.items():
            checkpoint = {
                'model_state_dict': agent.model.state_dict(),
                'optimizer_state_dict': self.ppo_trainers[agent_id].optimizer.state_dict(),
                'game_iteration': game_iteration,
                'alpha': agent.alpha_schedule.get_alpha(game_iteration),
                'win_rate': self.evaluator.get_win_rate(agent_id)
            }

            filepath = self.checkpoint_dir / f"{agent_id}_{game_iteration:06d}.pt"
            torch.save(checkpoint, filepath)

        print(f"  Saved checkpoints to {self.checkpoint_dir}")

        # Save evaluator history
        history_path = self.checkpoint_dir / f"history_{game_iteration:06d}.json"
        self.evaluator.save_history(history_path)

    def load_checkpoint(self, game_iteration: int):
        """
        Load model checkpoints for all agents.

        Args:
            game_iteration: Game iteration to load
        """
        print(f"\nLoading checkpoints from game {game_iteration}...")

        for agent_id, agent in self.agents.items():
            filepath = self.checkpoint_dir / f"{agent_id}_{game_iteration:06d}.pt"

            if not filepath.exists():
                print(f"  Warning: Checkpoint not found for {agent_id}")
                continue

            checkpoint = torch.load(filepath, map_location=self.device)

            agent.model.load_state_dict(checkpoint['model_state_dict'])
            self.ppo_trainers[agent_id].optimizer.load_state_dict(
                checkpoint['optimizer_state_dict']
            )

            print(f"  Loaded {agent_id}: alpha={checkpoint['alpha']:.4f}, "
                  f"win_rate={checkpoint['win_rate']:.3f}")

        # Load evaluator history
        history_path = self.checkpoint_dir / f"history_{game_iteration:06d}.json"
        if history_path.exists():
            self.evaluator.load_history(history_path)

        self.game_iteration = game_iteration


if __name__ == "__main__":
    # Quick test
    import json

    # Load agent configs
    config_path = Path("config/player_behaviours.json")
    with open(config_path) as f:
        agent_configs = json.load(f)

    # Create trainer
    trainer = MultiAgentTrainer(
        agent_configs=agent_configs,
        checkpoint_dir=Path("models/checkpoints"),
        log_dir=Path("logs"),
        recording_dir=Path("recordings"),
        seed=42
    )

    # Run short test
    trainer.train(num_games=10)

    print("\nTest complete!")
