from dataclasses import dataclass
from ..ports.game_repository import GameRepository
from ...domain.services.game_service import GameService
from ...domain.value_objects.action_type import ActionType
from ...domain.entities.game_history import Action
from ...domain.exceptions.game_exceptions import GameException


@dataclass
class DropFlowerCommand:
    game_id: str


@dataclass
class DropFlowerResult:
    success: bool
    board_state: dict
    message: str


class DropFlowerUseCase:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, command: DropFlowerCommand) -> DropFlowerResult:
        """Drop a flower on an adjacent empty cell."""
        board = self.repository.get(command.game_id)
        if board is None:
            raise ValueError(f"Game {command.game_id} not found")

        history = self.repository.get_history(command.game_id)
        orientation = board.robot.orientation

        try:
            GameService.drop_flower(board)
            self.repository.save(command.game_id, board)

            action = Action(
                action_type=ActionType.DROP,
                direction=orientation,
                success=True,
                message=f"Dropped flower (holding {board.robot.flowers_held})",
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return DropFlowerResult(
                success=True,
                board_state=board.to_dict(),
                message=f"Flower dropped successfully (holding {board.robot.flowers_held})",
            )
        except GameException as e:
            action = Action(
                action_type=ActionType.DROP, direction=orientation, success=False, message=str(e)
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return DropFlowerResult(
                success=False, board_state=board.to_dict(), message=f"Game Over: {str(e)}"
            )
