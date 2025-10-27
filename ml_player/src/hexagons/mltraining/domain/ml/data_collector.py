"""
Data Collector for ML Training.

Collects game states and actions to build training datasets.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from shared.logging import logger


class GameDataCollector:
    """Collects and stores game data for ML training."""

    def __init__(self, data_dir: str = "data/training"):
        """
        Initialize data collector.

        Args:
            data_dir: Directory to store training data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"GameDataCollector initialized with data_dir={self.data_dir}")

    def collect_sample(
        self,
        game_id: str,
        game_state: dict[str, Any],
        action: str,
        direction: str | None,
        outcome: dict[str, Any] | None = None,
        timestamp: str | None = None,
    ) -> None:
        """
        Collect a single training sample.

        Args:
            game_id: Unique game identifier
            game_state: Complete game state at time of decision
            action: Action taken
            direction: Direction for move/rotate actions
            outcome: Result of the action (optional, for reward learning)
            timestamp: ISO timestamp (optional, defaults to current time)
        """
        sample = {
            "timestamp": timestamp or datetime.utcnow().isoformat(),
            "game_id": game_id,
            "game_state": game_state,
            "action": action,
            "direction": direction,
            "outcome": outcome,
        }

        # Store in daily batches
        date_str = datetime.now().strftime("%Y-%m-%d")
        sample_file = self.data_dir / f"samples_{date_str}.jsonl"

        with open(sample_file, "a") as f:
            f.write(json.dumps(sample) + "\n")

        logger.debug(f"Collected sample for game_id={game_id}, action={action}")

    def load_samples(self, start_date: str | None = None, end_date: str | None = None) -> list[dict[str, Any]]:
        """
        Load training samples for a date range.

        Args:
            start_date: Start date (YYYY-MM-DD), default: all
            end_date: End date (YYYY-MM-DD), default: all

        Returns:
            List of training samples
        """
        samples = []

        for sample_file in sorted(self.data_dir.glob("samples_*.jsonl")):
            # Filter by date range if specified
            if start_date or end_date:
                file_date = sample_file.stem.replace("samples_", "")
                if start_date and file_date < start_date:
                    continue
                if end_date and file_date > end_date:
                    continue

            with open(sample_file) as f:
                for line in f:
                    if line.strip():
                        samples.append(json.loads(line))

        logger.info(f"Loaded {len(samples)} training samples")
        return samples

    def get_statistics(self) -> dict[str, Any]:
        """
        Get statistics about collected data.

        Returns:
            Dictionary with data statistics
        """
        all_samples = self.load_samples()

        if not all_samples:
            return {"total_samples": 0}

        # Calculate action distribution
        action_counts: dict[str, int] = {}
        game_ids = set()

        for sample in all_samples:
            action = sample["action"]
            action_counts[action] = action_counts.get(action, 0) + 1
            game_ids.add(sample["game_id"])

        return {
            "total_samples": len(all_samples),
            "unique_games": len(game_ids),
            "action_distribution": action_counts,
            "data_files": len(list(self.data_dir.glob("samples_*.jsonl"))),
        }
