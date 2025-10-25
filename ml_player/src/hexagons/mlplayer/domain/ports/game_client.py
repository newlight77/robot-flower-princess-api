"""Port for communicating with the game service."""

from abc import ABC, abstractmethod
from typing import Dict


class GameClientPort(ABC):
    """
    Port for fetching game state from the main game service.

    This allows the ML player to remain decoupled from the game implementation.
    """

    @abstractmethod
    async def get_game_state(self, game_id: str) -> Dict:
        """
        Fetch current game state from the game service.

        Args:
            game_id: Game identifier

        Returns:
            Dictionary containing game state
        """
        pass

    @abstractmethod
    async def execute_action(self, game_id: str, action: str, direction: str = None) -> Dict:
        """
        Execute an action in the game.

        Args:
            game_id: Game identifier
            action: Action type (move, pick, drop, give, clean, rotate)
            direction: Direction for the action (if applicable)

        Returns:
            Result of the action
        """
        pass
