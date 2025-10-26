from dataclasses import dataclass
from ..ports.game_repository import GameRepository
from ...domain.services.game_service import GameService
from ..core.value_objects.action_type import ActionType
from ..core.entities.game_history import Action, GameHistory
from ..core.exceptions.game_exceptions import GameException
from ..core.value_objects.direction import Direction
from ..core.entities.game import Game
from ..core.value_objects.game_status import GameStatus
from shared.logging import get_logger


@dataclass
class MoveRobotCommand:
    game_id: str
    direction: Direction


@dataclass
class MoveRobotResult:
    success: bool
    game: Game


class MoveRobotUseCase:
    def __init__(self, repository: GameRepository):
        self.logger = get_logger(self)
        self.logger.debug("Initializing MoveRobotUseCase repository=%r", repository)
        self.repository = repository

    def execute(self, command: MoveRobotCommand) -> MoveRobotResult:
        """Move the robot in the direction it's facing."""
        self.logger.info(
            "execute: MoveRobotCommand game_id=%s direction=%s", command.game_id, command.direction
        )
        game = self.repository.get(command.game_id)
        if game is None:
            raise ValueError(f"Game {command.game_id} not found")

        history = self.repository.get_history(command.game_id)
        if history is None:
            history = GameHistory(game_id=command.game_id)

        # Apply the supplied direction first
        try:
            GameService.rotate_robot(game, command.direction)
            GameService.move_robot(game)
            self.repository.save(command.game_id, game)

            action = Action(
                action_type=ActionType.MOVE,
                direction=command.direction,
                success=True,
                message="Move successful",
            )
            history.add_action(action)
            self.repository.save_history(command.game_id, history)

            return MoveRobotResult(
                success=True,
                game=game,
            )
        except GameException as e:
            action = Action(
                action_type=ActionType.MOVE,
                direction=command.direction,
                success=False,
                message=f"Game Over: {str(e)}",
            )
            history.add_action(action)
            self.repository.save_history(command.game_id, history)
            game.status = GameStatus.GAME_OVER
            self.repository.save(command.game_id, game)

            return MoveRobotResult(
                success=False,
                game=game,
            )
