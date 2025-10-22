from dataclasses import dataclass
from ..ports.game_repository import GameRepository
from ...logging import get_logger
from ..core.entities.game_history import GameHistory

@dataclass
class GetGameHistoryQuery:
    game_id: str


@dataclass
class GetGameHistoryResult:
    history: GameHistory


class GetGameHistoryUseCase:
    def __init__(self, repository: GameRepository):
        self.logger = get_logger(self)
        self.logger.debug("Initializing GetGameHistoryUseCase repository=%r", repository)
        self.repository = repository

    def execute(self, query: GetGameHistoryQuery) -> GetGameHistoryResult:
        """Get the history of a game."""
        self.logger.info("execute: GetGameHistoryQuery game_id=%s", query.game_id)
        history = self.repository.get_history(query.game_id)
        if history is None:
            raise ValueError(f"Game {query.game_id} not found")

        return GetGameHistoryResult(history=history)
