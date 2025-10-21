from dataclasses import dataclass
from ..ports.game_repository import GameRepository
from ...domain.services.game_service import GameService
from ..core.value_objects.action_type import ActionType
from ..core.entities.game_history import Action, GameHistory
from ..core.exceptions.game_exceptions import GameException
from ..core.value_objects.direction import Direction
from ...logging import get_logger


@dataclass
class MoveRobotCommand:
    game_id: str
    direction: Direction


@dataclass
class MoveRobotResult:
    success: bool
    board_state: dict
    message: str
    game_model: dict


class MoveRobotUseCase:
    def __init__(self, repository: GameRepository):
        self.logger = get_logger(self)
        self.logger.debug("Initializing MoveRobotUseCase repository=%r", repository)
        self.repository = repository

    def execute(self, command: MoveRobotCommand) -> MoveRobotResult:
        """Move the robot in the direction it's facing."""
        self.logger.info("execute: MoveRobotCommand game_id=%s direction=%s", command.game_id, command.direction)
        board = self.repository.get(command.game_id)
        if board is None:
            raise ValueError(f"Game {command.game_id} not found")

        history = self.repository.get_history(command.game_id)
        if history is None:
            history = GameHistory()

        # Apply the supplied direction first
        try:
            GameService.rotate_robot(board, command.direction)
            GameService.move_robot(board)
            self.repository.save(command.game_id, board)

            status = board.get_status().value
            message = "Move successful"
            if status == "victory":
                message = "Victory! All flowers delivered!"

            action = Action(
                action_type=ActionType.MOVE, direction=command.direction, success=True, message=message
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return MoveRobotResult(success=True, board_state=board.to_dict(), message=message, game_model=board.to_game_model_dict())
        except GameException as e:
            action = Action(
                action_type=ActionType.MOVE, direction=command.direction, success=False, message=str(e)
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return MoveRobotResult(
                success=False, board_state=board.to_dict(), message=f"Game Over: {str(e)}", game_model=board.to_game_model_dict()
            )
