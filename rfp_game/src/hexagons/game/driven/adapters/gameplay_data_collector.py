"""
Gameplay data collector adapter.

Collects gameplay data for ML training by delegating to ML Training service.
"""

from datetime import datetime
from typing import Any

import httpx
from shared.logging import get_logger

logger = get_logger("gameplay_data_collector")


class GameplayDataCollector:
    """Collects gameplay data by sending it to ML Training service for storage."""

    def __init__(
        self,
        ml_training_url: str,
        timeout: float,
        data_collection_enabled: bool,
    ):
        """
        Initialize the gameplay data collector.

        Args:
            ml_training_url: Base URL of ML Training service (defaults to env var ML_TRAINING_SERVICE_URL)
            timeout: HTTP request timeout in seconds
            data_collection_enabled: Whether to enable data collection
        """
        self.ml_training_url = ml_training_url
        self.timeout = timeout
        self.enabled = data_collection_enabled

        logger.info(
            f"GameplayDataCollector initialized: enabled={self.enabled}, ml_training_url={self.ml_training_url}"
        )

    def collect_action(
        self,
        game_id: str,
        game_state: dict[str, Any],
        action: str,
        direction: str | None,
        outcome: dict[str, Any],
    ) -> None:
        """
        Collect a gameplay action sample by sending it to ML Training service.

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
            # Prepare payload
            payload = {
                "game_id": game_id,
                "timestamp": datetime.now().isoformat(),
                "game_state": game_state,
                "action": action,
                "direction": direction,
                "outcome": outcome,
            }

            # Send to ML Training service
            url = f"{self.ml_training_url}/api/ml-training/collect"

            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()

                result = response.json()
                logger.debug(
                    f"Data collected successfully: game_id={game_id}, action={action}, "
                    f"total_samples={result.get('samples_collected', 'unknown')}"
                )

        except httpx.TimeoutException:
            logger.warning(f"Timeout sending gameplay data to ML Training service (game_id={game_id})")
        except httpx.HTTPError as e:
            logger.warning(f"HTTP error sending gameplay data to ML Training: {e} (game_id={game_id})")
        except Exception as e:
            logger.error(f"Failed to collect gameplay data: {e} (game_id={game_id})")

    def get_statistics(self) -> dict[str, Any]:
        """
        Get statistics about collected data from ML Training service.

        Returns:
            Dictionary with statistics
        """
        if not self.enabled:
            return {"enabled": False, "message": "Data collection is disabled"}

        # Statistics are now managed by ML Training service
        # This is just a placeholder for backward compatibility
        return {
            "enabled": True,
            "message": "Data collection delegated to ML Training service",
            "ml_training_url": self.ml_training_url,
        }
