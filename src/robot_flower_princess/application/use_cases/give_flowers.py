from dataclasses import dataclass
from ..ports.game_repository import GameRepository
from ...domain.services.game_service import GameService
from ...domain.value_objects.action_type import ActionType
from ...domain.entities.game_history import Action
from ...domain.exceptions.game_exceptions import GameException

@dataclass
class GiveFlowersCommand:
    game_id: str

@dataclass
class GiveFlowersResult:
    success: bool
    board_state: dict
    message: str

class GiveFlowersUseCase:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, command: GiveFlowersCommand) -> GiveFlowersResult:
        """Give flowers to the princess."""
        board = self.repository.get(command.game_id)
        if board is None:
            raise ValueError(f"Game {command.game_id} not found")

        history = self.repository.get_history(command.game_id)
        orientation = board.robot.orientation

        try:
            GameService.give_flowers(board)
            self.repository.save(command.game_id, board)

            status = board.get_status().value
            message = f"Flowers delivered! ({board.flowers_delivered}/{board.initial_flower_count})"
            if status == "victory":
                message = "Victory! All flowers delivered to the princess!"

            action = Action(
                action_type=ActionType.GIVE,
                direction=orientation,
                success=True,
                message=message
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return GiveFlowersResult(
                success=True,
                board_state=board.to_dict(),
                message=message
            )
        except GameException as e:
            action = Action(
                action_type=ActionType.GIVE,
                direction=orientation,
                success=False,
                message=str(e)
            )
            history.add_action(action, board.to_dict())
            self.repository.save_history(command.game_id, history)

            return GiveFlowersResult(
                success=False,
                board_state=board.to_dict(),
                message=f"Game Over: {str(e)}"
            )
