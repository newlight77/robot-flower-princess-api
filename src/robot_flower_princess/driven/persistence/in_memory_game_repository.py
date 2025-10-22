from typing import Optional, Dict, List
from ...domain.ports.game_repository import GameRepository
from ...domain.core.entities.game import Game
from ...domain.core.entities.game_history import GameHistory
from ...logging import get_logger

logger = get_logger("InMemoryGameRepository")


class InMemoryGameRepository(GameRepository):
    """In-memory implementation of game repository."""

    def __init__(self) -> None:
        self._games: Dict[str, Game] = {}
        self._histories: Dict[str, GameHistory] = {}
        logger.debug("InMemoryGameRepository initialized")

    def save(self, game_id: str, board: Game) -> None:
        logger.info("save game_id=%s", game_id)
        self._games[game_id] = board

    def get(self, game_id: str) -> Optional[Game]:
        logger.debug("get game_id=%s found=%s", game_id, game_id in self._games)
        return self._games.get(game_id)

    def delete(self, game_id: str) -> None:
        logger.info("delete game_id=%s", game_id)
        if game_id in self._games:
            del self._games[game_id]
        if game_id in self._histories:
            del self._histories[game_id]

    def exists(self, game_id: str) -> bool:
        exists = game_id in self._games
        logger.debug("exists game_id=%s exists=%s", game_id, exists)
        return exists

    def save_history(self, game_id: str, history: GameHistory) -> None:
        logger.info("save_history game_id=%s entries=%s", game_id, len(history.actions) if history else 0)
        self._histories[game_id] = history

    def get_history(self, game_id: str) -> Optional[GameHistory]:
        logger.debug("get_history game_id=%s found=%s", game_id, game_id in self._histories)
        return self._histories.get(game_id)

    def get_games(self, limit: int = 10, status: str = "") -> List[tuple[str, Game]]:
        """Get the last N games, optionally filtered by status."""
        logger.info("get_games limit=%s status=%s", limit, status)
        filtered_games = []
        for game_id, board in self._games.items():
            board_status = board.get_status()
            if status is None or board_status.value == status:
                filtered_games.append((game_id, board))

        # Return the last N filtered games
        return filtered_games[-limit:] if len(filtered_games) > limit else filtered_games
