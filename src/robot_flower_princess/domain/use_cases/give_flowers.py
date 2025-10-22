from dataclasses import dataclass
from ..ports.game_repository import GameRepository
from ...domain.services.game_service import GameService
from ..core.value_objects.action_type import ActionType
from ..core.entities.game_history import Action, GameHistory
from ..core.exceptions.game_exceptions import GameException
from ..core.value_objects.direction import Direction
from ...logging import get_logger


@dataclass
class GiveFlowersCommand:
    game_id: str
    direction: Direction


@dataclass
class GiveFlowersResult:
    success: bool
    board_state: dict
    message: str
    game_model: dict


class GiveFlowersUseCase:
    def __init__(self, repository: GameRepository):
        self.logger = get_logger(self)
        self.logger.debug("Initializing GiveFlowersUseCase repository=%r", repository)
        self.repository = repository

    def execute(self, command: GiveFlowersCommand) -> GiveFlowersResult:
        """Give flowers to the princess."""
        self.logger.info("execute: GiveFlowersCommand game_id=%s direction=%s", command.game_id, command.direction)
        board = self.repository.get(command.game_id)
        if board is None:
            raise ValueError(f"Game {command.game_id} not found")

        history = self.repository.get_history(command.game_id)
        if history is None:
            history = GameHistory()

        try:
            GameService.rotate_robot(board, command.direction)
            GameService.give_flowers(board)
            self.repository.save(command.game_id, board)

            status = board.get_status().value
            message = f"Flowers delivered! ({board.flowers_delivered}/{board.initial_flower_count})"
            if status == "victory":
                message = "Victory! All flowers delivered to the princess!"

            action = Action(
                action_type=ActionType.GIVE, direction=command.direction, success=True, message=message
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return GiveFlowersResult(success=True, board=board.to_dict(), message=message)
        except GameException as e:
            action = Action(
                action_type=ActionType.GIVE, direction=command.direction, success=False, message=str(e)
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return GiveFlowersResult(
                success=False,
                board=board.to_dict(),
                message=f"Game Over: {str(e)}"
            )
