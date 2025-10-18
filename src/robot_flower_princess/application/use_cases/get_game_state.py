from dataclasses import dataclass
from ..ports.game_repository import GameRepository

@dataclass
class GetGameStateQuery:
    game_id: str

@dataclass
class GetGameStateResult:
    board_state: dict

class GetGameStateUseCase:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, query: GetGameStateQuery) -> GetGameStateResult:
        """Get the current state of a game."""
        board = self.repository.get(query.game_id)
        if board is None:
            raise ValueError(f"Game {query.game_id} not found")

        return GetGameStateResult(
            board_state=board.to_dict()
        )
