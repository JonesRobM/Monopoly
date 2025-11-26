"""
Alpha annealing schedules for hybrid policy mixing.

Each agent has a per-agent alpha that controls the mixing ratio between
heuristic and learned policies:

    action_probs = alpha × heuristic_probs + (1 - alpha) × learned_probs

Alpha starts high (agents follow heuristics closely) and anneals down
over training (agents learn to deviate from heuristics when beneficial).

Different agents have different annealing schedules reflecting their
personality "rigidity":
- Alice: 0.8 → 0.5 (stays rule-based)
- Jack: 0.7 → 0.05 (becomes mostly learned/chaotic)
- Irene: 0.5 → 0.2 (balanced throughout)
"""

from typing import Dict
import numpy as np


class AlphaSchedule:
    """
    Annealing schedule for alpha parameter.

    Supports linear and exponential decay schedules.
    """

    def __init__(self, alpha_initial: float, alpha_final: float,
                 total_games: int, schedule_type: str = "linear"):
        """
        Initialize alpha schedule.

        Args:
            alpha_initial: Starting alpha value (0-1)
            alpha_final: Final alpha value (0-1)
            total_games: Total number of games for annealing
            schedule_type: "linear" or "exponential"
        """
        if not 0 <= alpha_initial <= 1:
            raise ValueError("alpha_initial must be in [0, 1]")
        if not 0 <= alpha_final <= 1:
            raise ValueError("alpha_final must be in [0, 1]")
        if alpha_initial < alpha_final:
            raise ValueError("alpha_initial must be >= alpha_final (annealing)")

        self.alpha_initial = alpha_initial
        self.alpha_final = alpha_final
        self.total_games = total_games
        self.schedule_type = schedule_type

    def get_alpha(self, game_iteration: int) -> float:
        """
        Get alpha value at a given game iteration.

        Args:
            game_iteration: Current game iteration (0-indexed)

        Returns:
            Alpha value in [alpha_final, alpha_initial]
        """
        if game_iteration >= self.total_games:
            return self.alpha_final

        progress = game_iteration / self.total_games  # 0 to 1

        if self.schedule_type == "linear":
            alpha = self.alpha_initial - (self.alpha_initial - self.alpha_final) * progress
        elif self.schedule_type == "exponential":
            # Exponential decay: alpha = initial * exp(-k * progress)
            # Solve for k such that alpha(1) = final
            # final = initial * exp(-k) => k = -ln(final / initial)
            if self.alpha_final > 0:
                k = -np.log(self.alpha_final / self.alpha_initial)
                alpha = self.alpha_initial * np.exp(-k * progress)
            else:
                # If final is 0, use linear to avoid log(0)
                alpha = self.alpha_initial * (1 - progress)
        else:
            raise ValueError(f"Unknown schedule_type: {self.schedule_type}")

        # Clamp to [alpha_final, alpha_initial]
        alpha = max(self.alpha_final, min(self.alpha_initial, alpha))

        return alpha


# Per-agent alpha configurations
# Format: agent_id -> (alpha_initial, alpha_final, schedule_type)
ALPHA_CONFIGS: Dict[str, tuple[float, float, str]] = {
    # Alice: Conservative, rule-based → stays mostly rule-based
    'alice': (0.8, 0.5, 'linear'),

    # Bob: High-value acquirer → moderate learning
    'bob': (0.7, 0.3, 'linear'),

    # Charlie: Infrastructure collector → moderate learning
    'charlie': (0.6, 0.3, 'linear'),

    # Dee: Trade specialist → learns flexibility for trades
    'dee': (0.5, 0.2, 'linear'),

    # Ethel: Property hoarder → moderate learning
    'ethel': (0.7, 0.4, 'linear'),

    # Frankie: Development maximiser → aggressive learning
    'frankie': (0.6, 0.2, 'exponential'),

    # Greta: Monopoly completer → moderate learning
    'greta': (0.6, 0.3, 'linear'),

    # Harry: Resource denial → learns to block strategically
    'harry': (0.6, 0.3, 'linear'),

    # Irene: Balanced investor → balanced throughout
    'irene': (0.5, 0.2, 'linear'),

    # Jack: Hyper-aggressive → becomes mostly learned/chaotic
    'jack': (0.7, 0.05, 'exponential'),
}


def create_alpha_schedule(agent_id: str, total_games: int) -> AlphaSchedule:
    """
    Create alpha schedule for an agent.

    Args:
        agent_id: Agent ID (e.g., 'alice', 'bob', ...)
        total_games: Total number of training games

    Returns:
        AlphaSchedule instance

    Raises:
        ValueError: If agent_id is not recognized
    """
    if agent_id not in ALPHA_CONFIGS:
        raise ValueError(f"Unknown agent_id: {agent_id}. Must be one of {list(ALPHA_CONFIGS.keys())}")

    alpha_initial, alpha_final, schedule_type = ALPHA_CONFIGS[agent_id]

    return AlphaSchedule(
        alpha_initial=alpha_initial,
        alpha_final=alpha_final,
        total_games=total_games,
        schedule_type=schedule_type
    )


def get_default_alpha_configs() -> Dict[str, tuple[float, float, str]]:
    """
    Get default alpha configurations for all agents.

    Returns:
        Dictionary mapping agent_id to (alpha_initial, alpha_final, schedule_type)
    """
    return ALPHA_CONFIGS.copy()
