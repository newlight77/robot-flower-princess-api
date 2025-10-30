from abc import ABC, abstractmethod
from typing import Any


class MLTrainingDataCollectorPort(ABC):
    """Port for collecting gameplay data samples for ML training service."""

    @abstractmethod
    def collect_action(
        self,
        game_id: str,
        game_state: dict[str, Any],
        action: str,
        direction: str | None,
        outcome: dict[str, Any],
    ) -> None:
        """Collect one gameplay action sample."""
        pass
