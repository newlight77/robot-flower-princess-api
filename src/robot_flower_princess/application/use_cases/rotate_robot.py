from dataclasses import dataclass
from ..ports.game_repository import GameRepository
from ...domain.services.game_service import GameService
from ...domain.value_objects.direction import Direction
from ...domain.value_objects.action_type import ActionType
from ...domain.entities.game_history import Action
from ...domain.exceptions.game_exceptions import GameException

@dataclass
class RotateRobotCommand:
    game_id: str
    direction: Direction

@dataclass
class RotateRobotResult:
    success: bool
    board_state: dict
    message: str

class RotateRobotUseCase:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, command: RotateRobotCommand) -> RotateRobotResult:
        """Rotate the robot to face a direction."""
        board = self.repository.get(command.game_id)
        if board is None:
            raise ValueError(f"Game {command.game_id} not found")

        history = self.repository.get_history(command.game_id)

        try:
            GameService.rotate_robot(board, command.direction)
            self.repository.save(command.game_id, board)

            action = Action(
                action_type=ActionType.ROTATE,
                direction=command.direction,
                success=True,
                message=f"Rotated to face {command.direction.value}"
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return RotateRobotResult(
                success=True,
                board_state=board.to_dict(),
                message=f"Robot rotated to face {command.direction.value}"
            )
        except GameException as e:
            action = Action(
                action_type=ActionType.ROTATE,
                direction=command.direction,
                success=False,
                message=str(e)
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return RotateRobotResult(
                success=False,
                board_state=board.to_dict(),
                message=f"Game Over: {str(e)}"
            )
