from dataclasses import dataclass
from ..ports.game_repository import GameRepository
from ...domain.services.game_service import GameService
from ...domain.value_objects.action_type import ActionType
from ...domain.entities.game_history import Action
from ...domain.exceptions.game_exceptions import GameException


@dataclass
class MoveRobotCommand:
    game_id: str


@dataclass
class MoveRobotResult:
    success: bool
    board_state: dict
    message: str


class MoveRobotUseCase:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, command: MoveRobotCommand) -> MoveRobotResult:
        """Move the robot in the direction it's facing."""
        board = self.repository.get(command.game_id)
        if board is None:
            raise ValueError(f"Game {command.game_id} not found")

        history = self.repository.get_history(command.game_id)
        orientation = board.robot.orientation

        try:
            GameService.move_robot(board)
            self.repository.save(command.game_id, board)

            status = board.get_status().value
            message = "Move successful"
            if status == "victory":
                message = "Victory! All flowers delivered!"

            action = Action(
                action_type=ActionType.MOVE, direction=orientation, success=True, message=message
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return MoveRobotResult(success=True, board_state=board.to_dict(), message=message)
        except GameException as e:
            action = Action(
                action_type=ActionType.MOVE, direction=orientation, success=False, message=str(e)
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return MoveRobotResult(
                success=False, board_state=board.to_dict(), message=f"Game Over: {str(e)}"
            )
