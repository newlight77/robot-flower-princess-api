from dataclasses import dataclass
from ..ports.game_repository import GameRepository
from ...logging import get_logger


@dataclass
class GetGameStateQuery:
    game_id: str


@dataclass
class GetGameStateResult:
    board_state: dict


class GetGameStateUseCase:
    def __init__(self, repository: GameRepository):
        self.logger = get_logger(self)
        self.logger.debug("Initializing GetGameStateUseCase repository=%r", repository)
        self.repository = repository

    def execute(self, query: GetGameStateQuery) -> GetGameStateResult:
        """Get the current state of a game."""
        self.logger.info("execute: GetGameStateQuery game_id=%s", query.game_id)
        board = self.repository.get(query.game_id)
        if board is None:
            raise ValueError(f"Game {query.game_id} not found")

        return GetGameStateResult(board_state=board.to_dict())
