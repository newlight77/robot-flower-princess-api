"""
Gameplay data collector adapter.

Collects gameplay data for ML training.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from shared.logging import get_logger

logger = get_logger("gameplay_data_collector")


class GameplayDataCollector:
    """Collects gameplay data for ML training."""

    def __init__(self, data_dir: str = "data/gameplay"):
        """
        Initialize the gameplay data collector.

        Args:
            data_dir: Directory to store collected data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.enabled = os.getenv("ENABLE_DATA_COLLECTION", "false").lower() == "true"
        logger.info(f"GameplayDataCollector initialized: enabled={self.enabled}, data_dir={data_dir}")

    def collect_action(
        self,
        game_id: str,
        game_state: dict[str, Any],
        action: str,
        direction: str | None,
        outcome: dict[str, Any],
    ) -> None:
        """
        Collect a gameplay action sample.

        Args:
            game_id: Unique game identifier
            game_state: Current game state before action
            action: Action taken (move, rotate, pick, drop, give, clean)
            direction: Direction for the action (if applicable)
            outcome: Result of the action (success, message, etc.)
        """
        if not self.enabled:
            return

        try:
            sample = {
                "game_id": game_id,
                "timestamp": datetime.now().isoformat(),
                "game_state": game_state,
                "action": action,
                "direction": direction,
                "outcome": outcome,
            }

            # Save to daily file
            filename = f"gameplay_{datetime.now().strftime('%Y%m%d')}.jsonl"
            filepath = self.data_dir / filename

            with open(filepath, "a", encoding="utf-8") as f:
                f.write(json.dumps(sample) + "\n")

            logger.debug(f"Collected gameplay sample: game_id={game_id}, action={action}, direction={direction}")

        except Exception as e:
            logger.error(f"Failed to collect gameplay data: {e}")

    def get_statistics(self) -> dict[str, Any]:
        """
        Get statistics about collected data.

        Returns:
            Dictionary with statistics
        """
        if not self.enabled:
            return {"enabled": False, "message": "Data collection is disabled"}

        try:
            total_samples = 0
            data_files = []

            for filepath in self.data_dir.glob("gameplay_*.jsonl"):
                data_files.append(filepath.name)
                with open(filepath, "r", encoding="utf-8") as f:
                    total_samples += sum(1 for _ in f)

            return {
                "enabled": True,
                "total_samples": total_samples,
                "data_files": len(data_files),
                "files": data_files,
                "data_dir": str(self.data_dir),
            }

        except Exception as e:
            logger.error(f"Failed to get data collection statistics: {e}")
            return {"enabled": True, "error": str(e)}
