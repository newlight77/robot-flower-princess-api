from dataclasses import dataclass
from ..ports.game_repository import GameRepository
from ...domain.services.game_service import GameService
from ..core.value_objects.action_type import ActionType
from ..core.entities.game_history import Action, GameHistory
from ..core.exceptions.game_exceptions import GameException
from ..core.value_objects.direction import Direction
from ...logging import get_logger


@dataclass
class DropFlowerCommand:
    game_id: str
    direction: Direction


@dataclass
class DropFlowerResult:
    success: bool
    board_state: dict
    message: str
    game_model: dict


class DropFlowerUseCase:
    def __init__(self, repository: GameRepository):
        self.logger = get_logger(self)
        self.logger.debug("Initializing DropFlowerUseCase repository=%r", repository)
        self.repository = repository

    def execute(self, command: DropFlowerCommand) -> DropFlowerResult:
        """Drop a flower on an adjacent empty cell."""
        self.logger.info("execute: DropFlowerCommand game_id=%s direction=%s", command.game_id, command.direction)
        board = self.repository.get(command.game_id)
        if board is None:
            raise ValueError(f"Game {command.game_id} not found")

        history = self.repository.get_history(command.game_id)
        if history is None:
            history = GameHistory()

        try:
            GameService.rotate_robot(board, command.direction)
            GameService.drop_flower(board)
            self.repository.save(command.game_id, board)

            action = Action(
                action_type=ActionType.DROP,
                direction=command.direction,
                success=True,
                message=f"Dropped flower (holding {board.robot.flowers_held})",
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return DropFlowerResult(
                success=True,
                board_state=board.to_dict(),
                message=f"Flower dropped successfully (holding {board.robot.flowers_held})",
                game_model=board.to_game_model_dict(),
            )
        except GameException as e:
            action = Action(
                action_type=ActionType.DROP, direction=command.direction, success=False, message=str(e)
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return DropFlowerResult(
                success=False, board_state=board.to_dict(), message=f"Game Over: {str(e)}", game_model=board.to_game_model_dict()
            )
