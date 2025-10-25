from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from ..ports.game_repository import GameRepository
from ..core.entities.board import Board
from shared.logging import get_logger


@dataclass
class GetGamesQuery:
    limit: int = 10
    status: Optional[str] = None


@dataclass
class GameSummary:
    game_id: str
    status: str
    board: Board
    created_at: datetime
    updated_at: datetime


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
        status = query.status if query.status is not None else "in_progress"
        self.logger.info(
            "execute: GetGamesQuery limit=%s status=%r final status=%s",
            query.limit,
            query.status,
            status,
        )
        games = self.repository.get_games(query.limit, status)

        game_summaries = []
        for game_id, game in games:
            game_summaries.append(
                GameSummary(
                    game_id=game_id,
                    status=game.get_status().value,
                    board=game.board,
                    created_at=game.created_at,
                    updated_at=game.updated_at,
                )
            )

        return GetGamesResult(games=game_summaries)
