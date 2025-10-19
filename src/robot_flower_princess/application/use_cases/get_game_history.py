from dataclasses import dataclass
from ..ports.game_repository import GameRepository


@dataclass
class GetGameHistoryQuery:
    game_id: str


@dataclass
class GetGameHistoryResult:
    history: dict


class GetGameHistoryUseCase:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, query: GetGameHistoryQuery) -> GetGameHistoryResult:
        """Get the history of a game."""
        history = self.repository.get_history(query.game_id)
        if history is None:
            raise ValueError(f"Game {query.game_id} not found")

        return GetGameHistoryResult(history=history.to_dict())
