from dataclasses import dataclass
from typing import Set
from ..ports.game_repository import GameRepository
from ...domain.services.game_service import GameService
from ..core.exceptions.game_exceptions import GameException
from ..core.value_objects.direction import Direction
from ..core.entities.game import Game
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

        try:
            # rotate robot to the requested direction first
            GameService.rotate_robot(game, command.direction)
            GameService.pick_flower(game)
            self.repository.save(command.game_id, game)

            return PickFlowerResult(
                success=True,
                game=game,
            )
        except GameException as e:
            return PickFlowerResult(
                success=False,
                game=game,
            )
