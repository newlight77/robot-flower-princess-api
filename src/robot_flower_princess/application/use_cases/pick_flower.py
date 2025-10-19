from dataclasses import dataclass
from ..ports.game_repository import GameRepository
from ...domain.services.game_service import GameService
from ...domain.value_objects.action_type import ActionType
from ...domain.entities.game_history import Action
from ...domain.exceptions.game_exceptions import GameException


@dataclass
class PickFlowerCommand:
    game_id: str


@dataclass
class PickFlowerResult:
    success: bool
    board_state: dict
    message: str


class PickFlowerUseCase:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, command: PickFlowerCommand) -> PickFlowerResult:
        """Pick a flower from an adjacent cell."""
        board = self.repository.get(command.game_id)
        if board is None:
            raise ValueError(f"Game {command.game_id} not found")

        history = self.repository.get_history(command.game_id)
        orientation = board.robot.orientation

        try:
            GameService.pick_flower(board)
            self.repository.save(command.game_id, board)

            action = Action(
                action_type=ActionType.PICK,
                direction=orientation,
                success=True,
                message=f"Picked flower (holding {board.robot.flowers_held})",
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return PickFlowerResult(
                success=True,
                board_state=board.to_dict(),
                message=f"Flower picked successfully (holding {board.robot.flowers_held})",
            )
        except GameException as e:
            action = Action(
                action_type=ActionType.PICK, direction=orientation, success=False, message=str(e)
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return PickFlowerResult(
                success=False, board_state=board.to_dict(), message=f"Game Over: {str(e)}"
            )
