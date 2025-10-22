from dataclasses import dataclass
from typing import Set
from ..ports.game_repository import GameRepository
from ...domain.services.game_service import GameService
from ..core.value_objects.action_type import ActionType
from ..core.entities.game_history import Action, GameHistory
from ..core.exceptions.game_exceptions import GameException
from ..core.value_objects.direction import Direction
from ..core.entities.board import Board
from ..core.entities.robot import Robot
from ..core.entities.princess import Princess
from ..core.entities.position import Position
from ...logging import get_logger


@dataclass
class GiveFlowersCommand:
    game_id: str
    direction: Direction


@dataclass
class GiveFlowersResult:
    success: bool
    board: Board
    robot: Robot
    princess: Princess
    flowers: Set[Position]
    obstacles: Set[Position]
    status: str
    message: str


class GiveFlowersUseCase:
    def __init__(self, repository: GameRepository):
        self.logger = get_logger(self)
        self.logger.debug("Initializing GiveFlowersUseCase repository=%r", repository)
        self.repository = repository

    def execute(self, command: GiveFlowersCommand) -> GiveFlowersResult:
        """Give flowers to the princess."""
        self.logger.info(
            "execute: GiveFlowersCommand game_id=%s direction=%s",
            command.game_id,
            command.direction,
        )
        board = self.repository.get(command.game_id)
        if board is None:
            raise ValueError(f"Game {command.game_id} not found")

        history = self.repository.get_history(command.game_id)
        if history is None:
            history = GameHistory(game_id=command.game_id)

        try:
            GameService.rotate_robot(board, command.direction)
            GameService.give_flowers(board)
            self.repository.save(command.game_id, board)

            status = board.get_status().value
            message = f"Flowers delivered! ({board.flowers_delivered}/{board.initial_flower_count})"
            if status == "victory":
                message = "Victory! All flowers delivered to the princess!"

            action = Action(
                action_type=ActionType.GIVE,
                direction=command.direction,
                success=True,
                message=message,
            )
            history.add_action(action)
            self.repository.save_history(command.game_id, history)

            return GiveFlowersResult(
                success=True,
                board=board.board,
                robot=board.robot,
                princess=board.princess,
                flowers=board.flowers,
                obstacles=board.obstacles,
                status=status,
                message=message,
            )
        except GameException as e:
            action = Action(
                action_type=ActionType.GIVE,
                direction=command.direction,
                success=False,
                message=str(e),
            )
            history.add_action(action)
            self.repository.save_history(command.game_id, history)

            return GiveFlowersResult(
                success=False,
                board=board.board,
                robot=board.robot,
                princess=board.princess,
                flowers=board.flowers,
                obstacles=board.obstacles,
                status=board.get_status().value,
                message=f"Game Over: {str(e)}",
            )
