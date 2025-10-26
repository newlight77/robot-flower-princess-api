from dataclasses import dataclass
from typing import List, Optional
from ..ports.game_repository import GameRepository
from ..core.entities.game import Game
from shared.logging import get_logger


@dataclass
class GetGamesQuery:
    limit: int = 10
    status: Optional[str] = None


@dataclass
class GetGamesResult:
    games: List[Game]
    total: int
    message: str


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

        return GetGamesResult(
            games=games,
            total=len(games),
            message=f"Games retrieved successfully: {len(games)} games",
        )
