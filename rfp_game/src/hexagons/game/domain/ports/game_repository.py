from abc import ABC, abstractmethod
from typing import Optional, List

from ..core.entities.game import Game


class GameRepository(ABC):
    """Port for game persistence."""

    @abstractmethod
    def save(self, game_id: str, game: Game) -> None:
        """Save a game."""
        pass

    @abstractmethod
    def get(self, game_id: str) -> Optional[Game]:
        """Retrieve a game by ID."""
        pass

    @abstractmethod
    def delete(self, game_id: str) -> None:
        """Delete a game."""
        pass

    @abstractmethod
    def exists(self, game_id: str) -> bool:
        """Check if a game exists."""
        pass

    @abstractmethod
    def get_games(self, limit: int = 10, status: str = "") -> List[tuple[str, Game]]:
        """Get the last N games, optionally filtered by status."""
        pass
