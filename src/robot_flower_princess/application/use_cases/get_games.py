from dataclasses import dataclass
from typing import List, Optional
from ..ports.game_repository import GameRepository

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
        self.repository = repository

    def execute(self, query: GetGamesQuery) -> GetGamesResult:
        """Get the last N games, optionally filtered by status."""
        games = self.repository.get_games(query.limit, query.status)

        game_summaries = []
        for game_id, board in games:
            game_summaries.append(GameSummary(
                game_id=game_id,
                status=board.get_status().value,
                board=board.to_dict()
            ))

        return GetGamesResult(games=game_summaries)
