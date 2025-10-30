from abc import ABC, abstractmethod
from typing import Any


class GameplayDataCollectorPort(ABC):
    """Port for collecting gameplay data samples for ML training."""

    @abstractmethod
    def collect_action(
        self,
        game_id: str,
        game_state: dict[str, Any],
        action: str,
        direction: str | None,
        outcome: dict[str, Any],
    ) -> None:
        """Collect one gameplay action sample.

        Args:
            game_id: Unique game identifier
            game_state: Current game state before action
            action: Action taken (move, rotate, pick, drop, give, clean)
            direction: Direction for the action (if applicable)
            outcome: Result of the action (success, message, etc.)
        """
        pass
