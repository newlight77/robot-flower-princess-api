from dataclasses import dataclass
from ..ports.game_repository import GameRepository
from ...domain.services.game_service import GameService
from ..core.exceptions.game_exceptions import GameException
from ..core.value_objects.direction import Direction
from ..core.entities.game import Game
from ..ports.mltraining_data_collector import MLTrainingDataCollectorPort
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
    def __init__(self, repository: GameRepository, data_collector: MLTrainingDataCollectorPort):
        self.logger = get_logger(self)
        self.logger.debug("Initializing PickFlowerUseCase repository=%r", repository)
        self.repository = repository
        self.data_collector = data_collector

    def execute(self, command: PickFlowerCommand) -> PickFlowerResult:
        """Pick a flower from an adjacent cell."""
        self.logger.info("execute: PickFlowerCommand game_id=%s direction=%s", command.game_id, command.direction)
        game = self.repository.get(command.game_id)
        if game is None:
            raise ValueError(f"Game {command.game_id} not found")

        state_before = game.to_dict()

        try:
            # rotate robot to the requested direction first
            GameService.rotate_robot(game, command.direction)
            GameService.pick_flower(game)
            self.repository.save(command.game_id, game)

            result = PickFlowerResult(
                success=True,
                game=game,
            )
            try:
                self.data_collector.collect_action(
                    game_id=command.game_id,
                    game_state=state_before,
                    action="pick",
                    direction=command.direction.value,
                    outcome={"success": True, "message": "action performed successfully"},
                )
            except Exception:
                pass
            return result
        except GameException:
            result = PickFlowerResult(
                success=False,
                game=game,
            )
            try:
                self.data_collector.collect_action(
                    game_id=command.game_id,
                    game_state=state_before,
                    action="pick",
                    direction=command.direction.value,
                    outcome={"success": False, "message": "failed"},
                )
            except Exception:
                pass
            return result
