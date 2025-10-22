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
from ...logging import get_logger


@dataclass
class CreateGameCommand:
    rows: int
    cols: int
    name: str = ""


@dataclass
class CreateGameResult:
    game_id: str
    board: Board
    robot: Robot
    princess: Princess
    flowers: Set[Position]
    obstacles: Set[Position]
    status: str
    message: str
    created_at: datetime
    updated_at: datetime


class CreateGameUseCase:
    def __init__(self, repository: GameRepository):
        self.logger = get_logger(self)
        self.logger.debug("Initializing CreateGameUseCase repository=%r", repository)
        self.repository = repository

    def execute(self, command: CreateGameCommand) -> CreateGameResult:
        """Create a new game with the specified board size."""
        self.logger.info("execute: CreateGameCommand rows=%s cols=%s name=%s", command.rows, command.cols, command.name)
        game: Game = Game.create(rows=command.rows, cols=command.cols)

        # Set the game name if provided
        if command.name:
            game.name = command.name
        else:
            game.name = f"Game-{command.rows}x{command.cols}"

        game_id = str(uuid.uuid4())
        game.game_id = game_id

        # Save game and initialize history
        self.repository.save(game_id, game)
        history = GameHistory(game_id=game_id)
        history.add_action(action=None)
        self.repository.save_history(game_id, history)

        return CreateGameResult(
            game_id=game_id,
            board=game.board,
            robot=game.robot,
            princess=game.princess,
            flowers=game.flowers,
            obstacles=game.obstacles,
            status=game.get_status().value,
            message="Game created successfully",
            created_at=game.created_at,
            updated_at=game.updated_at
        )
