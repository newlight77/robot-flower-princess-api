from typing import Optional, Dict, List
from ...application.ports.game_repository import GameRepository
from ...domain.entities.board import Board
from ...domain.entities.game_history import GameHistory
from ...domain.value_objects.game_status import GameStatus

class InMemoryGameRepository(GameRepository):
    """In-memory implementation of game repository."""

    def __init__(self) -> None:
        self._games: Dict[str, Board] = {}
        self._histories: Dict[str, GameHistory] = {}

    def save(self, game_id: str, board: Board) -> None:
        self._games[game_id] = board

    def get(self, game_id: str) -> Optional[Board]:
        return self._games.get(game_id)

    def delete(self, game_id: str) -> None:
        if game_id in self._games:
            del self._games[game_id]
        if game_id in self._histories:
            del self._histories[game_id]

    def exists(self, game_id: str) -> bool:
        return game_id in self._games

    def save_history(self, game_id: str, history: GameHistory) -> None:
        self._histories[game_id] = history

    def get_history(self, game_id: str) -> Optional[GameHistory]:
        return self._histories.get(game_id)

    def get_ended_games(self, limit: int = 10) -> List[tuple[str, Board]]:
        """Get the last N games that have ended (victory or game_over)."""
        ended_games = []
        for game_id, board in self._games.items():
            status = board.get_status()
            if status in [GameStatus.VICTORY, GameStatus.GAME_OVER]:
                ended_games.append((game_id, board))

        # Sort by game_id (assuming newer games have higher IDs or different ordering)
        # For simplicity, we'll return the last N games from the dict
        # In a real implementation, you might want to track creation/end timestamps
        return list(self._games.items())[-limit:] if len(ended_games) > limit else ended_games
