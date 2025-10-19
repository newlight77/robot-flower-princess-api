from dataclasses import dataclass
from typing import List
from ..ports.game_repository import GameRepository

@dataclass
class GetEndedGamesQuery:
    limit: int = 10

@dataclass
class GameSummary:
    game_id: str
    status: str
    board: dict

@dataclass
class GetEndedGamesResult:
    games: List[GameSummary]

class GetEndedGamesUseCase:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, query: GetEndedGamesQuery) -> GetEndedGamesResult:
        """Get the last N games that have ended."""
        ended_games = self.repository.get_ended_games(query.limit)

        game_summaries = []
        for game_id, board in ended_games:
            game_summaries.append(GameSummary(
                game_id=game_id,
                status=board.get_status().value,
                board=board.to_dict()
            ))

        return GetEndedGamesResult(games=game_summaries)
