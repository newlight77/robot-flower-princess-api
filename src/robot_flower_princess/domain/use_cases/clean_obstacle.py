from dataclasses import dataclass
from ..ports.game_repository import GameRepository
from ..services.game_service import GameService
from ..core.value_objects.action_type import ActionType
from ..core.entities.game_history import Action, GameHistory
from ..core.exceptions.game_exceptions import GameException
from ..core.value_objects.direction import Direction
from ...logging import get_logger


@dataclass
class CleanObstacleCommand:
    game_id: str
    direction: Direction


@dataclass
class CleanObstacleResult:
    success: bool
    board_state: dict
    message: str
    game_model: dict


class CleanObstacleUseCase:
    def __init__(self, repository: GameRepository):
        self.logger = get_logger(self)
        self.logger.debug("Initializing CleanObstacleUseCase repository=%r", repository)
        self.repository = repository

    def execute(self, command: CleanObstacleCommand) -> CleanObstacleResult:
        """Clean an obstacle in the direction faced."""
        self.logger.info("execute: CleanObstacleCommand game_id=%s direction=%s", command.game_id, command.direction)
        board = self.repository.get(command.game_id)
        if board is None:
            raise ValueError(f"Game {command.game_id} not found")

        history = self.repository.get_history(command.game_id)
        if history is None:
            history = GameHistory()

        try:
            GameService.rotate_robot(board, command.direction)
            GameService.clean_obstacle(board)
            self.repository.save(command.game_id, board)

            action = Action(
                action_type=ActionType.CLEAN,
                direction=command.direction,
                success=True,
                message="Obstacle cleaned",
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return CleanObstacleResult(
                success=True, board_state=board.to_dict(), message="Obstacle cleaned successfully", game_model=board.to_game_model_dict()
            )
        except GameException as e:
            action = Action(
                action_type=ActionType.CLEAN, direction=command.direction, success=False, message=str(e)
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return CleanObstacleResult(
                success=False, board_state=board.to_dict(), message=f"Game Over: {str(e)}", game_model=board.to_game_model_dict()
            )
