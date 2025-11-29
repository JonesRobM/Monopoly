"""
Base RL agent class for Monopoly.

Each of the 10 agent archetypes is an instance of RLAgent with:
- Unique reward weights (from player_behaviours.json)
- Unique heuristic policy
- Unique alpha annealing schedule
- Separate model checkpoint
- Separate replay buffer
"""

import json
import numpy as np
import torch
from pathlib import Path
from typing import Dict, Optional, Any

from engine.state import GameState
from engine.board import MonopolyBoard
from engine.actions import ActionEncoder

from agents.reward_shaper import CustomRewardShaper
from agents.heuristics import get_heuristic_policy, HeuristicPolicy
from agents.alpha_schedules import create_alpha_schedule, AlphaSchedule


class RLAgent:
    """
    RL agent with custom reward function and hybrid policy.

    Combines heuristic biases with learned policy:
        action_probs = alpha × heuristic + (1-alpha) × learned
    """

    def __init__(self, agent_id: str, agent_config: Dict[str, Any],
                 board: MonopolyBoard, action_encoder: ActionEncoder,
                 total_training_games: int):
        """
        Initialize RL agent.

        Args:
            agent_id: Agent ID (e.g., 'alice', 'bob', ...)
            agent_config: Configuration dict from player_behaviours.json
            board: Monopoly board instance
            action_encoder: Action encoder instance
            total_training_games: Total number of training games (for alpha annealing)
        """
        self.agent_id = agent_id
        self.name = agent_config['name']
        self.strategy_type = agent_config['strategy_type']
        self.objective = agent_config['objective']

        self.board = board
        self.action_encoder = action_encoder

        # Reward shaper with custom weights
        self.reward_weights = agent_config['priority_weights']
        self.reward_shaper = CustomRewardShaper(board, self.reward_weights)

        # Heuristic policy
        self.heuristic_policy: HeuristicPolicy = get_heuristic_policy(
            agent_id, board, action_encoder
        )

        # Alpha schedule
        self.alpha_schedule: AlphaSchedule = create_alpha_schedule(
            agent_id, total_training_games
        )
        self.current_game_iteration = 0

        # Model (will be initialized later with transformer architecture)
        self.model: Optional[Any] = None  # PyTorch model

        # Tokenizer (will be initialized later)
        self.tokenizer: Optional[Any] = None

        # Replay buffer (will be initialized later)
        self.replay_buffer: Optional[Any] = None

        # Training statistics
        self.total_games_played = 0
        self.total_wins = 0
        self.total_rewards = []

    @classmethod
    def from_json(cls, agent_id: str, json_path: Path, board: MonopolyBoard,
                  action_encoder: ActionEncoder, total_training_games: int) -> 'RLAgent':
        """
        Create agent from player_behaviours.json file.

        Args:
            agent_id: Agent ID to load (e.g., 'alice')
            json_path: Path to player_behaviours.json
            board: Monopoly board instance
            action_encoder: Action encoder instance
            total_training_games: Total number of training games

        Returns:
            RLAgent instance

        Raises:
            ValueError: If agent_id not found in JSON
            FileNotFoundError: If JSON file doesn't exist
        """
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Find agent config
        agent_config = None
        for player in data['players']:
            if player['id'] == agent_id:
                agent_config = player
                break

        if agent_config is None:
            raise ValueError(f"Agent ID '{agent_id}' not found in {json_path}")

        return cls(agent_id, agent_config, board, action_encoder, total_training_games)

    def calculate_reward(self, state: GameState, prev_state: GameState,
                        player_id: int, action_type=None) -> float:
        """
        Calculate reward for this agent given state transition.

        Uses agent's custom reward weights.

        Args:
            state: Current game state
            prev_state: Previous game state
            player_id: Player ID in the game (not agent_id)
            action_type: Optional action type for action-specific rewards

        Returns:
            Weighted reward value
        """
        return self.reward_shaper.calculate_reward(state, player_id, prev_state, action_type)

    def get_action(self, observation: np.ndarray, action_mask: np.ndarray,
                   state: GameState, player_id: int,
                   deterministic: bool = False) -> int:
        """
        Get action using hybrid policy (heuristic + learned).

        action_probs = alpha × heuristic_probs + (1-alpha) × learned_probs

        Args:
            observation: Encoded observation vector
            action_mask: Legal action mask
            state: Current game state (for heuristic)
            player_id: Player ID in the game
            deterministic: If True, return argmax instead of sampling

        Returns:
            Action ID
        """
        # Get current alpha
        alpha = self.alpha_schedule.get_alpha(self.current_game_iteration)

        # Get heuristic probabilities
        heuristic_probs = self.heuristic_policy.get_action_probabilities(
            state, player_id, action_mask
        )

        # Get learned probabilities (from model)
        if self.model is not None and self.tokenizer is not None:
            # Tokenize state
            property_tokens, player_tokens, game_token = self.tokenizer.tokenize(state, player_id)

            # Get model device
            model_device = next(self.model.parameters()).device

            # Convert to tensors and add batch dimension, create directly on target device
            property_tokens = torch.tensor(property_tokens, dtype=torch.float32, device=model_device).unsqueeze(0)
            player_tokens = torch.tensor(player_tokens, dtype=torch.float32, device=model_device).unsqueeze(0)
            game_token = torch.tensor(game_token, dtype=torch.float32, device=model_device).unsqueeze(0)

            # Get logits from model
            with torch.no_grad():
                learned_logits = self.model.get_action_logits(property_tokens, player_tokens, game_token)
                learned_logits = learned_logits.squeeze(0).cpu().numpy()

            # Apply action mask
            masked_logits = learned_logits + (action_mask - 1) * 1e10
            learned_probs = self._softmax(masked_logits)
        else:
            # If no model yet, use uniform over legal actions
            learned_probs = action_mask / action_mask.sum()

        # Hybrid policy
        action_probs = alpha * heuristic_probs + (1 - alpha) * learned_probs

        # Normalize (should already be normalized, but ensure)
        action_probs = action_probs / action_probs.sum()

        # Sample or take argmax
        if deterministic:
            action = int(np.argmax(action_probs))
        else:
            action = int(np.random.choice(len(action_probs), p=action_probs))

        return action

    def store_experience(self, observation: np.ndarray, action: int,
                        reward: float, value: float, log_prob: float,
                        done: bool):
        """
        Store experience in replay buffer.

        Args:
            observation: Observation vector
            action: Action taken
            reward: Reward received
            value: Value estimate from critic
            log_prob: Log probability of action
            done: Whether episode ended
        """
        if self.replay_buffer is not None:
            self.replay_buffer.add(observation, action, reward, value, log_prob, done)

    def update_model(self):
        """
        Update model using PPO algorithm.

        Called after accumulating sufficient experience (e.g., 10 games).
        """
        if self.model is not None and self.replay_buffer is not None:
            # PPO update logic (will be implemented in training module)
            pass

    def update_game_iteration(self, game_iteration: int):
        """
        Update current game iteration for alpha annealing.

        Args:
            game_iteration: Current game iteration
        """
        self.current_game_iteration = game_iteration

    def get_current_alpha(self) -> float:
        """Get current alpha value."""
        return self.alpha_schedule.get_alpha(self.current_game_iteration)

    def record_game_result(self, won: bool, total_reward: float):
        """
        Record game statistics.

        Args:
            won: Whether agent won the game
            total_reward: Total reward accumulated in game
        """
        self.total_games_played += 1
        if won:
            self.total_wins += 1
        self.total_rewards.append(total_reward)

    def get_win_rate(self) -> float:
        """Get agent's win rate."""
        if self.total_games_played == 0:
            return 0.0
        return self.total_wins / self.total_games_played

    def get_average_reward(self) -> float:
        """Get agent's average reward per game."""
        if len(self.total_rewards) == 0:
            return 0.0
        return np.mean(self.total_rewards)

    def save_checkpoint(self, checkpoint_dir: Path):
        """
        Save agent checkpoint (model weights, statistics).

        Args:
            checkpoint_dir: Directory to save checkpoint
        """
        agent_dir = checkpoint_dir / self.agent_id
        agent_dir.mkdir(parents=True, exist_ok=True)

        # Save model weights (implement when model is added)
        if self.model is not None:
            # torch.save(self.model.state_dict(), agent_dir / "model.pt")
            pass

        # Save statistics
        stats = {
            'total_games_played': self.total_games_played,
            'total_wins': self.total_wins,
            'total_rewards': self.total_rewards[-100:],  # Keep last 100
            'current_game_iteration': self.current_game_iteration,
        }

        with open(agent_dir / "stats.json", 'w') as f:
            json.dump(stats, f, indent=2)

    def load_checkpoint(self, checkpoint_dir: Path):
        """
        Load agent checkpoint (model weights, statistics).

        Args:
            checkpoint_dir: Directory containing checkpoint
        """
        agent_dir = checkpoint_dir / self.agent_id

        # Load model weights (implement when model is added)
        if self.model is not None:
            # model_path = agent_dir / "model.pt"
            # if model_path.exists():
            #     self.model.load_state_dict(torch.load(model_path))
            pass

        # Load statistics
        stats_path = agent_dir / "stats.json"
        if stats_path.exists():
            with open(stats_path, 'r') as f:
                stats = json.load(f)

            self.total_games_played = stats['total_games_played']
            self.total_wins = stats['total_wins']
            self.total_rewards = stats['total_rewards']
            self.current_game_iteration = stats['current_game_iteration']

    @staticmethod
    def _softmax(x: np.ndarray) -> np.ndarray:
        """Compute softmax with numerical stability."""
        exp_x = np.exp(x - np.max(x))
        return exp_x / exp_x.sum()


def create_all_agents(json_path: Path, board: MonopolyBoard,
                     action_encoder: ActionEncoder,
                     total_training_games: int) -> Dict[str, RLAgent]:
    """
    Create all 10 agents from player_behaviours.json.

    Args:
        json_path: Path to player_behaviours.json
        board: Monopoly board instance
        action_encoder: Action encoder instance
        total_training_games: Total number of training games

    Returns:
        Dictionary mapping agent_id to RLAgent instance
    """
    with open(json_path, 'r') as f:
        data = json.load(f)

    agents = {}
    for player_config in data['players']:
        agent_id = player_config['id']
        agent = RLAgent(agent_id, player_config, board, action_encoder, total_training_games)
        agents[agent_id] = agent

    return agents
