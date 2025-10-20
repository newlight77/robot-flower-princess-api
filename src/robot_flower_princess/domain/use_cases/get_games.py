from dataclasses import dataclass
from typing import List, Optional
from ..ports.game_repository import GameRepository
from ...logging import get_logger


@dataclass
class GetGamesQuery:
    limit: int = 10
    status: Optional[str] = None


@dataclass
class GameSummary:
    game_id: str
    status: str
    board: dict


@dataclass
class GetGamesResult:
    games: List[GameSummary]


class GetGamesUseCase:
    def __init__(self, repository: GameRepository):
        self.logger = get_logger(self)
        self.logger.debug("Initializing GetGamesUseCase repository=%r", repository)
        self.repository = repository

    def execute(self, query: GetGamesQuery) -> GetGamesResult:
        """Get the last N games, optionally filtered by status."""
        self.logger.info("execute: GetGamesQuery limit=%s status=%r", query.limit, query.status)
        status = query.status if query.status is not None else ""
        games = self.repository.get_games(query.limit, status)

        game_summaries = []
        for game_id, board in games:
            game_summaries.append(
                GameSummary(game_id=game_id, status=board.get_status().value, board=board.to_dict())
            )

        return GetGamesResult(games=game_summaries)
