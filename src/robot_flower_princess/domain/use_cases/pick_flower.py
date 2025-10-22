from dataclasses import dataclass
from ..ports.game_repository import GameRepository
from ...domain.services.game_service import GameService
from ..core.value_objects.action_type import ActionType
from ..core.entities.game_history import Action, GameHistory
from ..core.exceptions.game_exceptions import GameException
from ..core.value_objects.direction import Direction
from ...logging import get_logger


@dataclass
class PickFlowerCommand:
    game_id: str
    direction: Direction


@dataclass
class PickFlowerResult:
    success: bool
    board_state: dict
    message: str
    game_model: dict


class PickFlowerUseCase:
    def __init__(self, repository: GameRepository):
        self.logger = get_logger(self)
        self.logger.debug("Initializing PickFlowerUseCase repository=%r", repository)
        self.repository = repository

    def execute(self, command: PickFlowerCommand) -> PickFlowerResult:
        """Pick a flower from an adjacent cell."""
        self.logger.info("execute: PickFlowerCommand game_id=%s direction=%s", command.game_id, command.direction)
        board = self.repository.get(command.game_id)
        if board is None:
            raise ValueError(f"Game {command.game_id} not found")

        history = self.repository.get_history(command.game_id)
        if history is None:
            history = GameHistory()

        try:
            # rotate robot to the requested direction first
            GameService.rotate_robot(board, command.direction)
            GameService.pick_flower(board)
            self.repository.save(command.game_id, board)

            action = Action(
                action_type=ActionType.PICK,
                direction=command.direction,
                success=True,
                message=f"Picked flower (holding {board.robot.flowers_held})",
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return PickFlowerResult(
                success=True,
                board=board.to_dict(),
                message=f"Flower picked successfully (holding {board.robot.flowers_held})"
            )
        except GameException as e:
            action = Action(
                action_type=ActionType.PICK, direction=command.direction, success=False, message=str(e)
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return PickFlowerResult(
                success=False,
                board=board.to_dict(),
                message=f"Game Over: {str(e)}"
            )
