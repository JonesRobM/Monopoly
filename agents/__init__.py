"""
Multi-agent RL system for Monopoly.

This module provides infrastructure for training 10 distinct RL agents,
each with unique behavioral profiles and reward functions.

Components:
- CustomRewardShaper: Per-agent reward calculation (6 weighted components)
- HeuristicPolicy: Behavioral biases for each agent
- AlphaSchedule: Annealing schedules for hybrid policy mixing
- RLAgent: Main agent class tying everything together
"""

from agents.reward_shaper import CustomRewardShaper
from agents.heuristics import get_heuristic_policy, HeuristicPolicy
from agents.alpha_schedules import create_alpha_schedule, AlphaSchedule, ALPHA_CONFIGS
from agents.base_agent import RLAgent, create_all_agents

__all__ = [
    'CustomRewardShaper',
    'get_heuristic_policy',
    'HeuristicPolicy',
    'create_alpha_schedule',
    'AlphaSchedule',
    'ALPHA_CONFIGS',
    'RLAgent',
    'create_all_agents',
]
