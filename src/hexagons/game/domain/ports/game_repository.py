from abc import ABC, abstractmethod
from typing import Optional, List

from ..core.entities.game import Game
from ..core.entities.game_history import GameHistory


class GameRepository(ABC):
    """Port for game persistence."""

    @abstractmethod
    def save(self, game_id: str, board: Game) -> None:
        """Save a game board."""
        pass

    @abstractmethod
    def get(self, game_id: str) -> Optional[Game]:
        """Retrieve a game board by ID."""
        pass

    @abstractmethod
    def delete(self, game_id: str) -> None:
        """Delete a game board."""
        pass

    @abstractmethod
    def exists(self, game_id: str) -> bool:
        """Check if a game exists."""
        pass

    @abstractmethod
    def save_history(self, game_id: str, history: GameHistory) -> None:
        """Save game history."""
        pass

    @abstractmethod
    def get_history(self, game_id: str) -> Optional[GameHistory]:
        """Get game history."""
        pass

    @abstractmethod
    def get_games(self, limit: int = 10, status: str = "") -> List[tuple[str, Game]]:
        """Get the last N games, optionally filtered by status."""
        pass
