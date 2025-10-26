from dataclasses import dataclass
from ..ports.game_repository import GameRepository
from ...domain.services.game_service import GameService
from ..core.exceptions.game_exceptions import GameException
from ..core.value_objects.direction import Direction
from ..core.entities.game import Game
from shared.logging import get_logger


@dataclass
class GiveFlowersCommand:
    game_id: str
    direction: Direction


@dataclass
class GiveFlowersResult:
    success: bool
    game: Game


class GiveFlowersUseCase:
    def __init__(self, repository: GameRepository):
        self.logger = get_logger(self)
        self.logger.debug("Initializing GiveFlowersUseCase repository=%r", repository)
        self.repository = repository

    def execute(self, command: GiveFlowersCommand) -> GiveFlowersResult:
        """Give flowers to the princess."""
        self.logger.info(
            "execute: GiveFlowersCommand game_id=%s direction=%s",
            command.game_id,
            command.direction,
        )
        game = self.repository.get(command.game_id)
        if game is None:
            raise ValueError(f"Game {command.game_id} not found")

        try:
            GameService.rotate_robot(game, command.direction)
            GameService.give_flowers(game)
            self.repository.save(command.game_id, game)

            return GiveFlowersResult(
                success=True,
                game=game,
            )
        except GameException:
            return GiveFlowersResult(
                success=False,
                game=game,
            )
