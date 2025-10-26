from dataclasses import dataclass
from typing import Set
from ..ports.game_repository import GameRepository
from ...domain.services.game_service import GameService
from ..core.value_objects.action_type import ActionType
from ..core.entities.game_history import Action, GameHistory
from ..core.exceptions.game_exceptions import GameException
from ..core.value_objects.direction import Direction
from ..core.value_objects.game_status import GameStatus
from shared.logging import get_logger


@dataclass
class PickFlowerCommand:
    game_id: str
    direction: Direction


@dataclass
class PickFlowerResult:
    success: bool
    game: Game


class PickFlowerUseCase:
    def __init__(self, repository: GameRepository):
        self.logger = get_logger(self)
        self.logger.debug("Initializing PickFlowerUseCase repository=%r", repository)
        self.repository = repository

    def execute(self, command: PickFlowerCommand) -> PickFlowerResult:
        """Pick a flower from an adjacent cell."""
        self.logger.info(
            "execute: PickFlowerCommand game_id=%s direction=%s", command.game_id, command.direction
        )
        game = self.repository.get(command.game_id)
        if game is None:
            raise ValueError(f"Game {command.game_id} not found")

        history = self.repository.get_history(command.game_id)
        if history is None:
            history = GameHistory(game_id=command.game_id)

        try:
            # rotate robot to the requested direction first
            GameService.rotate_robot(game, command.direction)
            GameService.pick_flower(game)
            self.repository.save(command.game_id, game)

            action = Action(
                action_type=ActionType.PICK,
                direction=command.direction,
                success=True,
                message=f"Picked flower (holding {game.robot.flowers_held})",
            )
            history.add_action(action)
            self.repository.save_history(command.game_id, history)

            return PickFlowerResult(
                success=True,
                game=game,
            )
        except GameException as e:
            action = Action(
                action_type=ActionType.PICK,
                direction=command.direction,
                success=False,
                message=f"Game Over: {str(e)}",
            )
            history.add_action(action)
            self.repository.save_history(command.game_id, history)
            game.status = GameStatus.GAME_OVER
            self.repository.save(command.game_id, game)

            return PickFlowerResult(
                success=False,
                game=game,
            )
