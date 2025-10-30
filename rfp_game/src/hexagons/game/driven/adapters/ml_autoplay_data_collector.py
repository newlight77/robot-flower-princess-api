"""
MLTraining data collector adapter.

Collects gameplay data for ML training by delegating to ML Training service.
"""

from datetime import datetime
from typing import Any

import httpx
from shared.logging import get_logger
from ...domain.ports.ml_autoplay_data_collector import MLAutoplayDataCollectorPort

logger = get_logger("mltraining_data_collector")


class MLAutoplayDataCollector(MLAutoplayDataCollectorPort):
    """Collects gameplay data by sending it to ML Training service for storage."""

    def __init__(
        self,
        ml_training_url: str,
        timeout: float,
        data_collection_enabled: bool,
    ):
        self.ml_training_url = ml_training_url
        self.timeout = timeout
        self.enabled = data_collection_enabled

        logger.info(f"MLAutoplayDataCollector initialized: enabled={self.enabled}, ml_training_url={self.ml_training_url}")

    def collect_action(
        self,
        game_id: str,
        game_state: dict[str, Any],
        action: str,
        direction: str | None,
        outcome: dict[str, Any],
    ) -> None:
        logger.info(
            f"Collecting gameplay data: game_id={game_id}, action={action}, direction={direction}, outcome={outcome}"
        )
        if not self.enabled:
            logger.info(
                f"Data collection is disabled, skipping collection: game_id={game_id}, action={action}, direction={direction}, outcome={outcome}"
            )
            return

        try:
            payload = {
                "game_id": game_id,
                "timestamp": datetime.now().isoformat(),
                "game_state": game_state,
                "action": action,
                "direction": direction,
                "outcome": outcome,
            }

            url = f"{self.ml_training_url}/api/ml-training/collect"
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()

                result = response.json()
                logger.info(
                    f"Data collected successfully: game_id={game_id}, action={action}, total_samples={result.get('samples_collected', 'unknown')}"
                )

        except httpx.TimeoutException:
            logger.warning(f"Timeout sending gameplay data to ML Training service (game_id={game_id})")
        except httpx.HTTPError as e:
            logger.warning(f"HTTP error sending gameplay data to ML Training: {e} (game_id={game_id})")
        except Exception as e:
            logger.error(f"Failed to collect gameplay data: {e} (game_id={game_id})")

    def get_statistics(self) -> dict[str, Any]:
        if not self.enabled:
            return {"enabled": False, "message": "Data collection is disabled"}

        return {
            "enabled": True,
            "message": "Data collection delegated to ML Training service",
            "ml_training_url": self.ml_training_url,
        }
