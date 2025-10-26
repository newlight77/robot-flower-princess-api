from dataclasses import dataclass
import uuid
from datetime import datetime
from typing import Set
from ..ports.game_repository import GameRepository
from ..core.entities.game import Game
from ..core.entities.board import Board
from ..core.entities.robot import Robot
from ..core.entities.princess import Princess
from ..core.entities.position import Position
from ..core.entities.game_history import GameHistory
from shared.logging import get_logger


@dataclass
class CreateGameCommand:
    rows: int
    cols: int
    name: str = ""


@dataclass
class CreateGameResult:
    game: Game
    message: str


class CreateGameUseCase:
    def __init__(self, repository: GameRepository):
        self.logger = get_logger(self)
        self.logger.debug("Initializing CreateGameUseCase repository=%r", repository)
        self.repository = repository

    def execute(self, command: CreateGameCommand) -> CreateGameResult:
        """Create a new game with the specified board size."""
        self.logger.info(
            "execute: CreateGameCommand rows=%s cols=%s name=%s",
            command.rows,
            command.cols,
            command.name,
        )
        game: Game = Game.create(rows=command.rows, cols=command.cols)
        if command.name:
            game.name = command.name

        # Save game
        self.repository.save(game.game_id, game)

        return CreateGameResult(
            game=game,
            message="Game created successfully",
        )
