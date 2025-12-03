"""
Training Log Analyzer

Parses training log files (console output) to extract and visualize:
- Game progression (steps, rounds, turns)
- Phase transitions
- Warnings and errors
- Training speed and performance
- Model update confirmations

Usage:
    python analyze_training_logs.py logs/training_20250102_143022.log
    python analyze_training_logs.py logs/*.log  # Analyze all logs
    python analyze_training_logs.py --watch logs/training_log.txt  # Monitor live
"""

import re
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


@dataclass
class GameEvent:
    """Single game from training logs."""
    game_num: int
    participants: List[str]
    num_players: int
    winner: Optional[str] = None
    rounds: Optional[int] = None
    turns: Optional[int] = None
    steps: Optional[int] = None
    phase: Optional[int] = None
    max_rounds: Optional[int] = None
    max_actions_multiplier: Optional[int] = None
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    step_samples: List[Tuple[int, int, int, int]] = field(default_factory=list)  # (step, round, turn, active)


@dataclass
class PhaseTransition:
    """Phase transition event."""
    game_num: int
    from_phase: int
    to_phase: int
    old_rounds: int
    new_rounds: int
    old_actions: str
    new_actions: str


@dataclass
class ModelUpdate:
    """Model update event."""
    game_num: int
    agents_updated: List[str]
    buffer_sizes: Dict[str, int]
    losses: Dict[str, Dict[str, float]]  # agent -> {policy_loss, value_loss, entropy}


@dataclass
class TrainingRun:
    """Complete training run analysis."""
    log_file: Path
    start_game: int
    end_game: int
    total_games: int
    games: List[GameEvent]
    phase_transitions: List[PhaseTransition]
    model_updates: List[ModelUpdate]
    warnings_count: int
    errors_count: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[timedelta] = None


class TrainingLogParser:
    """Parse training log files."""

    # Regex patterns for log parsing
    GAME_START = re.compile(r'\[Game (\d+)\] Starting with (\d+) players?: (.+)')
    GAME_END = re.compile(r'\[Game (\d+)\] Finished! Winner: (\w+), Rounds: (\d+), Turns: (\d+), Steps: (\d+)')
    STEP_PROGRESS = re.compile(r'Step (\d+), Round (\d+), Turn (\d+), (\d+)/(\d+) players active')
    PHASE_TRANSITION = re.compile(
        r'CURRICULUM PHASE TRANSITION: Phase (\d+) → Phase (\d+)\s*\n'
        r'.*Increasing max_rounds: (\d+) → (\d+)\s*\n'
        r'.*Increasing max_actions_per_turn: (.+) → (.+)',
        re.MULTILINE
    )
    MODEL_UPDATE_START = re.compile(r'\[Game (\d+)\] Updating models...')
    MODEL_UPDATE_AGENT = re.compile(r'Updating (\w+)...')
    MODEL_BUFFER_SIZE = re.compile(r'Buffer size: (\d+)')
    MODEL_LOSSES = re.compile(r'(\w+): policy_loss=([\d.]+), value_loss=([\d.]+), entropy=([\d.]+)')
    WARNING = re.compile(r'WARNING: (.+)')
    ERROR = re.compile(r'ERROR: (.+)')
    GAME_ENDING = re.compile(r'Game ending: (.+)')

    def __init__(self, log_file: Path):
        """Initialize parser with log file."""
        self.log_file = log_file
        self.games: List[GameEvent] = []
        self.phase_transitions: List[PhaseTransition] = []
        self.model_updates: List[ModelUpdate] = []
        self.current_game: Optional[GameEvent] = None
        self.current_update: Optional[ModelUpdate] = None
        self.current_update_agent: Optional[str] = None

    def parse(self) -> TrainingRun:
        """Parse the log file and return TrainingRun object."""
        if not self.log_file.exists():
            raise FileNotFoundError(f"Log file not found: {self.log_file}")

        print(f"Parsing log file: {self.log_file}")

        with open(self.log_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        lines = content.split('\n')

        # Parse line by line
        for i, line in enumerate(lines):
            self._parse_line(line, lines, i)

        # Finalize current game if exists
        if self.current_game:
            self.games.append(self.current_game)

        # Calculate derived statistics
        start_game = self.games[0].game_num if self.games else 0
        end_game = self.games[-1].game_num if self.games else 0
        total_games = len(self.games)

        # Count warnings and errors
        warnings_count = sum(len(g.warnings) for g in self.games)
        errors_count = sum(len(g.errors) for g in self.games)

        return TrainingRun(
            log_file=self.log_file,
            start_game=start_game,
            end_game=end_game,
            total_games=total_games,
            games=self.games,
            phase_transitions=self.phase_transitions,
            model_updates=self.model_updates,
            warnings_count=warnings_count,
            errors_count=errors_count
        )

    def _parse_line(self, line: str, all_lines: List[str], line_idx: int):
        """Parse a single line of the log."""
        # Game start
        match = self.GAME_START.search(line)
        if match:
            # Save previous game
            if self.current_game:
                self.games.append(self.current_game)

            game_num = int(match.group(1))
            num_players = int(match.group(2))
            participants = [p.strip() for p in match.group(3).split(',')]

            # Determine phase
            phase = self._get_phase(game_num)
            max_rounds = {1: 15, 2: 25, 3: 50}[phase]
            max_actions_mult = {1: 10, 2: 20, 3: 50}[phase]

            self.current_game = GameEvent(
                game_num=game_num,
                participants=participants,
                num_players=num_players,
                phase=phase,
                max_rounds=max_rounds,
                max_actions_multiplier=max_actions_mult
            )
            return

        # Game end
        match = self.GAME_END.search(line)
        if match and self.current_game:
            self.current_game.winner = match.group(2)
            self.current_game.rounds = int(match.group(3))
            self.current_game.turns = int(match.group(4))
            self.current_game.steps = int(match.group(5))
            return

        # Step progress
        match = self.STEP_PROGRESS.search(line)
        if match and self.current_game:
            step = int(match.group(1))
            round_num = int(match.group(2))
            turn = int(match.group(3))
            active = int(match.group(4))
            self.current_game.step_samples.append((step, round_num, turn, active))
            return

        # Phase transition
        match = self.PHASE_TRANSITION.search(line)
        if match:
            transition = PhaseTransition(
                game_num=int(all_lines[line_idx - 2].split()[1].rstrip(']')) if line_idx > 1 else 0,
                from_phase=int(match.group(1)),
                to_phase=int(match.group(2)),
                old_rounds=int(match.group(3)),
                new_rounds=int(match.group(4)),
                old_actions=match.group(5),
                new_actions=match.group(6)
            )
            self.phase_transitions.append(transition)
            return

        # Model update start
        match = self.MODEL_UPDATE_START.search(line)
        if match:
            if self.current_update:
                self.model_updates.append(self.current_update)

            self.current_update = ModelUpdate(
                game_num=int(match.group(1)),
                agents_updated=[],
                buffer_sizes={},
                losses={}
            )
            return

        # Model update - agent
        match = self.MODEL_UPDATE_AGENT.search(line)
        if match and self.current_update:
            self.current_update_agent = match.group(1)
            self.current_update.agents_updated.append(self.current_update_agent)
            return

        # Model update - buffer size
        match = self.MODEL_BUFFER_SIZE.search(line)
        if match and self.current_update and self.current_update_agent:
            self.current_update.buffer_sizes[self.current_update_agent] = int(match.group(1))
            return

        # Model update - losses
        match = self.MODEL_LOSSES.search(line)
        if match and self.current_update:
            agent = match.group(1)
            self.current_update.losses[agent] = {
                'policy_loss': float(match.group(2)),
                'value_loss': float(match.group(3)),
                'entropy': float(match.group(4))
            }
            return

        # Warnings
        match = self.WARNING.search(line)
        if match and self.current_game:
            self.current_game.warnings.append(match.group(1))
            return

        # Errors
        match = self.ERROR.search(line)
        if match and self.current_game:
            self.current_game.errors.append(match.group(1))
            return

        # Game ending reasons
        match = self.GAME_ENDING.search(line)
        if match and self.current_game:
            self.current_game.warnings.append(f"Game ending: {match.group(1)}")
            return

    def _get_phase(self, game_num: int) -> int:
        """Determine curriculum phase for a game number."""
        if game_num < 1000:
            return 1
        elif game_num < 3000:
            return 2
        else:
            return 3


class TrainingLogAnalyzer:
    """Analyze and visualize training runs."""

    def __init__(self, training_run: TrainingRun):
        """Initialize analyzer."""
        self.run = training_run

    def print_summary(self):
        """Print text summary of training run."""
        print("\n" + "="*80)
        print("TRAINING LOG ANALYSIS SUMMARY")
        print("="*80)

        print(f"\n📄 Log File: {self.run.log_file.name}")
        print(f"📊 Games: {self.run.start_game} → {self.run.end_game} ({self.run.total_games} games)")

        if self.run.duration:
            print(f"⏱️  Duration: {self.run.duration}")

        # Phase distribution
        phase_counts = defaultdict(int)
        for game in self.run.games:
            if game.phase:
                phase_counts[game.phase] += 1

        print(f"\n📈 Curriculum Phases:")
        for phase in sorted(phase_counts.keys()):
            count = phase_counts[phase]
            pct = 100 * count / self.run.total_games
            max_rds = {1: 15, 2: 25, 3: 50}[phase]
            max_acts = {1: 10, 2: 20, 3: 50}[phase]
            print(f"   Phase {phase}: {count:4d} games ({pct:5.1f}%) - {max_rds} rds, {max_acts}× actions")

        # Phase transitions
        if self.run.phase_transitions:
            print(f"\n🔄 Phase Transitions: {len(self.run.phase_transitions)}")
            for trans in self.run.phase_transitions:
                print(f"   Game {trans.game_num}: Phase {trans.from_phase}→{trans.to_phase} "
                      f"({trans.old_rounds}→{trans.new_rounds} rds, {trans.old_actions}→{trans.new_actions})")

        # Model updates
        if self.run.model_updates:
            print(f"\n🔧 Model Updates: {len(self.run.model_updates)}")
            print(f"   Games: {[u.game_num for u in self.run.model_updates[:5]]}{'...' if len(self.run.model_updates) > 5 else ''}")

        # Game statistics
        completed_games = [g for g in self.run.games if g.steps is not None]
        if completed_games:
            avg_steps = np.mean([g.steps for g in completed_games])
            avg_rounds = np.mean([g.rounds for g in completed_games if g.rounds])
            avg_turns = np.mean([g.turns for g in completed_games if g.turns])

            print(f"\n📊 Game Statistics (completed games):")
            print(f"   Average steps/game: {avg_steps:.1f}")
            print(f"   Average rounds/game: {avg_rounds:.1f}")
            print(f"   Average turns/game: {avg_turns:.1f}")

        # Warnings and errors
        if self.run.warnings_count > 0 or self.run.errors_count > 0:
            print(f"\n⚠️  Issues Detected:")
            print(f"   Warnings: {self.run.warnings_count}")
            print(f"   Errors: {self.run.errors_count}")

            # Most common warnings
            all_warnings = defaultdict(int)
            for game in self.run.games:
                for warning in game.warnings:
                    # Normalize warning text
                    if "Turn exceeded" in warning:
                        all_warnings["Turn exceeded max actions"] += 1
                    elif "reached max_rounds" in warning:
                        all_warnings["Reached max_rounds"] += 1
                    elif "only one player remaining" in warning:
                        all_warnings["Only one player remaining"] += 1
                    else:
                        all_warnings[warning[:50]] += 1

            if all_warnings:
                print(f"\n   Most common warnings:")
                for warning, count in sorted(all_warnings.items(), key=lambda x: -x[1])[:5]:
                    print(f"      • {warning}: {count} occurrences")

        print("\n" + "="*80)

    def plot_game_progression(self, save_path: Optional[Path] = None):
        """Plot game length progression over training."""
        fig, axes = plt.subplots(3, 1, figsize=(14, 12))

        # Prepare data
        game_nums = [g.game_num for g in self.run.games if g.steps is not None]
        steps = [g.steps for g in self.run.games if g.steps is not None]
        rounds = [g.rounds for g in self.run.games if g.rounds is not None]
        turns = [g.turns for g in self.run.games if g.turns is not None]
        phases = [g.phase for g in self.run.games if g.steps is not None]

        # Define phase colors
        phase_colors = {1: '#ff9999', 2: '#99ccff', 3: '#99ff99'}

        # Plot 1: Steps per game
        ax1 = axes[0]
        ax1.scatter(game_nums, steps, c=[phase_colors[p] for p in phases], alpha=0.6, s=20)

        # Rolling average
        if len(steps) > 50:
            rolling_steps = pd.Series(steps).rolling(window=50, min_periods=1).mean()
            ax1.plot(game_nums, rolling_steps, 'b-', linewidth=2, label='50-game avg')

        # Add phase transitions
        for trans in self.run.phase_transitions:
            ax1.axvline(trans.game_num, color='red', linestyle='--', alpha=0.5, linewidth=2)

        ax1.set_xlabel('Game Number')
        ax1.set_ylabel('Steps per Game')
        ax1.set_title('Game Length (Steps) Over Training')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Rounds per game
        ax2 = axes[1]
        if rounds:
            rounds_game_nums = [g.game_num for g in self.run.games if g.rounds is not None]
            rounds_phases = [g.phase for g in self.run.games if g.rounds is not None]
            ax2.scatter(rounds_game_nums, rounds, c=[phase_colors[p] for p in rounds_phases], alpha=0.6, s=20)

            if len(rounds) > 50:
                rolling_rounds = pd.Series(rounds).rolling(window=50, min_periods=1).mean()
                ax2.plot(rounds_game_nums, rolling_rounds, 'b-', linewidth=2, label='50-game avg')

            # Add max_rounds lines for each phase
            for phase in [1, 2, 3]:
                max_rds = {1: 15, 2: 25, 3: 50}[phase]
                ax2.axhline(max_rds, color=phase_colors[phase], linestyle=':', alpha=0.5,
                           label=f'Phase {phase} max')

        for trans in self.run.phase_transitions:
            ax2.axvline(trans.game_num, color='red', linestyle='--', alpha=0.5, linewidth=2)

        ax2.set_xlabel('Game Number')
        ax2.set_ylabel('Rounds per Game')
        ax2.set_title('Game Length (Rounds) Over Training')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Plot 3: Turns per game
        ax3 = axes[2]
        if turns:
            turns_game_nums = [g.game_num for g in self.run.games if g.turns is not None]
            turns_phases = [g.phase for g in self.run.games if g.turns is not None]
            ax3.scatter(turns_game_nums, turns, c=[phase_colors[p] for p in turns_phases], alpha=0.6, s=20)

            if len(turns) > 50:
                rolling_turns = pd.Series(turns).rolling(window=50, min_periods=1).mean()
                ax3.plot(turns_game_nums, rolling_turns, 'b-', linewidth=2, label='50-game avg')

        for trans in self.run.phase_transitions:
            ax3.axvline(trans.game_num, color='red', linestyle='--', alpha=0.5, linewidth=2)

        ax3.set_xlabel('Game Number')
        ax3.set_ylabel('Turns per Game')
        ax3.set_title('Game Length (Turns) Over Training')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved plot to {save_path}")
        else:
            plt.show()

    def plot_warnings_timeline(self, save_path: Optional[Path] = None):
        """Plot warnings and issues over time."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

        # Count warnings per game
        warning_counts = []
        game_nums = []
        turn_exceeded_counts = []
        max_rounds_counts = []

        for game in self.run.games:
            game_nums.append(game.game_num)
            warning_counts.append(len(game.warnings))

            turn_exceeded = sum(1 for w in game.warnings if "Turn exceeded" in w)
            max_rounds = sum(1 for w in game.warnings if "reached max_rounds" in w)

            turn_exceeded_counts.append(turn_exceeded)
            max_rounds_counts.append(max_rounds)

        # Plot 1: All warnings
        ax1.scatter(game_nums, warning_counts, alpha=0.5, s=30)

        if len(warning_counts) > 50:
            rolling_warnings = pd.Series(warning_counts).rolling(window=50, min_periods=1).mean()
            ax1.plot(game_nums, rolling_warnings, 'r-', linewidth=2, label='50-game avg')

        for trans in self.run.phase_transitions:
            ax1.axvline(trans.game_num, color='red', linestyle='--', alpha=0.5, linewidth=2)

        ax1.set_xlabel('Game Number')
        ax1.set_ylabel('Warnings per Game')
        ax1.set_title('Warnings Over Training')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Specific warning types
        ax2.scatter(game_nums, turn_exceeded_counts, alpha=0.5, s=30, label='Turn exceeded', color='orange')
        ax2.scatter(game_nums, max_rounds_counts, alpha=0.5, s=30, label='Max rounds reached', color='purple')

        for trans in self.run.phase_transitions:
            ax2.axvline(trans.game_num, color='red', linestyle='--', alpha=0.5, linewidth=2, label='Phase transition')

        ax2.set_xlabel('Game Number')
        ax2.set_ylabel('Count per Game')
        ax2.set_title('Specific Warning Types Over Training')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved plot to {save_path}")
        else:
            plt.show()

    def export_to_csv(self, output_path: Path):
        """Export parsed data to CSV for further analysis."""
        data = []

        for game in self.run.games:
            data.append({
                'game_num': game.game_num,
                'num_players': game.num_players,
                'phase': game.phase,
                'max_rounds': game.max_rounds,
                'max_actions_multiplier': game.max_actions_multiplier,
                'winner': game.winner,
                'rounds': game.rounds,
                'turns': game.turns,
                'steps': game.steps,
                'warning_count': len(game.warnings),
                'error_count': len(game.errors),
                'turn_exceeded_warnings': sum(1 for w in game.warnings if "Turn exceeded" in w),
                'max_rounds_reached': sum(1 for w in game.warnings if "reached max_rounds" in w)
            })

        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        print(f"Exported data to {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Analyze Monopoly RL training logs')
    parser.add_argument('log_files', nargs='+', type=str, help='Path to log file(s)')
    parser.add_argument('--output-dir', type=str, default='analysis_output',
                       help='Directory for output plots and CSVs')
    parser.add_argument('--no-plots', action='store_true', help='Skip generating plots')

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    # Parse each log file
    for log_path_str in args.log_files:
        log_path = Path(log_path_str)

        if not log_path.exists():
            print(f"❌ Log file not found: {log_path}")
            continue

        try:
            # Parse log
            parser = TrainingLogParser(log_path)
            training_run = parser.parse()

            # Analyze
            analyzer = TrainingLogAnalyzer(training_run)
            analyzer.print_summary()

            # Export CSV
            csv_path = output_dir / f"{log_path.stem}_analysis.csv"
            analyzer.export_to_csv(csv_path)

            # Generate plots
            if not args.no_plots:
                plot1_path = output_dir / f"{log_path.stem}_progression.png"
                analyzer.plot_game_progression(save_path=plot1_path)

                plot2_path = output_dir / f"{log_path.stem}_warnings.png"
                analyzer.plot_warnings_timeline(save_path=plot2_path)

            print(f"\n✅ Analysis complete for {log_path.name}\n")

        except Exception as e:
            print(f"❌ Error analyzing {log_path}: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
