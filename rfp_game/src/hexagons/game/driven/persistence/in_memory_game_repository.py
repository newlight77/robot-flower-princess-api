from typing import Optional, Dict, List
from ...domain.ports.game_repository import GameRepository
from ...domain.core.entities.game import Game
from shared.logging import get_logger

logger = get_logger("InMemoryGameRepository")


class InMemoryGameRepository(GameRepository):
    """In-memory implementation of game repository."""

    def __init__(self) -> None:
        self._games: Dict[str, Game] = {}
        logger.debug("InMemoryGameRepository initialized")

    def save(self, game_id: str, game: Game) -> None:
        logger.info("save game_id=%s", game_id)
        self._games[game_id] = game

    def get(self, game_id: str) -> Optional[Game]:
        logger.debug("get game_id=%s found=%s", game_id, game_id in self._games)
        return self._games.get(game_id)

    def delete(self, game_id: str) -> None:
        logger.info("delete game_id=%s", game_id)
        if game_id in self._games:
            del self._games[game_id]

    def exists(self, game_id: str) -> bool:
        exists = game_id in self._games
        logger.debug("exists game_id=%s exists=%s", game_id, exists)
        return exists

    def get_games(self, limit: int = 10, status: str = "") -> List[tuple[str, Game]]:
        """Get the last N games, optionally filtered by status."""
        logger.info("get_games limit=%s status=%s", limit, status)
        filtered_games = []
        for game_id, game in self._games.items():
            game_status = game.get_status()
            if status is None or game_status.value == status:
                filtered_games.append((game_id, game))

        # Return the last N filtered games
        return filtered_games[-limit:] if len(filtered_games) > limit else filtered_games
