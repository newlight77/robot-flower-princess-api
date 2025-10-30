from dataclasses import dataclass
from ..ports.game_repository import GameRepository
from ...domain.services.game_service import GameService
from ..core.exceptions.game_exceptions import GameException
from ..core.value_objects.direction import Direction
from ..core.entities.game import Game
from ..ports.ml_autoplay_data_collector import MLAutoplayDataCollectorPort
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
    def __init__(self, repository: GameRepository, data_collector: MLAutoplayDataCollectorPort):
        self.logger = get_logger(self)
        self.logger.debug("Initializing GiveFlowersUseCase repository=%r", repository)
        self.repository = repository
        self.data_collector = data_collector

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

        state_before = game.to_dict()

        try:
            GameService.rotate_robot(game, command.direction)
            GameService.give_flowers(game)
            self.repository.save(command.game_id, game)

            result = GiveFlowersResult(
                success=True,
                game=game,
            )
            try:
                self.data_collector.collect_action(
                    game_id=command.game_id,
                    game_state=state_before,
                    action="give",
                    direction=command.direction.value,
                    outcome={"success": True, "message": "action performed successfully"},
                )
            except Exception:
                pass
            return result
        except GameException:
            result = GiveFlowersResult(
                success=False,
                game=game,
            )
            try:
                self.data_collector.collect_action(
                    game_id=command.game_id,
                    game_state=state_before,
                    action="give",
                    direction=command.direction.value,
                    outcome={"success": False, "message": "failed"},
                )
            except Exception:
                pass
            return result
