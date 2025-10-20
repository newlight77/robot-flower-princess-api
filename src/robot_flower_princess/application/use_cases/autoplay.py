from dataclasses import dataclass
from copy import deepcopy
from ..ports.game_repository import GameRepository
from ...infrastructure.ai.solver import GameSolver
from ...domain.value_objects.action_type import ActionType
from ...domain.entities.game_history import Action, GameHistory


@dataclass
class AutoplayCommand:
    game_id: str


@dataclass
class AutoplayResult:
    success: bool
    actions_taken: int
    board_state: dict
    message: str


class AutoplayUseCase:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def execute(self, command: AutoplayCommand) -> AutoplayResult:
        """Let AI solve the game automatically."""
        board = self.repository.get(command.game_id)
        if board is None:
            raise ValueError(f"Game {command.game_id} not found")

        history = self.repository.get_history(command.game_id)
        if history is None:
            history = GameHistory()

        # Create a copy for the solver
        board_copy = deepcopy(board)

        try:
            # Get solution from AI
            actions = GameSolver.solve(board_copy)

            # Apply actions to original board
            from ...domain.services.game_service import GameService

            for action_type, direction in actions:
                # Always rotate to the solver-provided direction first (if provided)
                if direction is not None:
                    GameService.rotate_robot(board, direction)

                if action_type == "rotate":
                    dir_str = direction.value if direction is not None else "unknown"
                    action = Action(
                        action_type=ActionType.ROTATE,
                        direction=direction,
                        success=True,
                        message=f"AI: Rotated to {dir_str}",
                    )
                    history.add_action(action, board.to_dict())

                elif action_type == "move":
                    GameService.move_robot(board)
                    action = Action(
                        action_type=ActionType.MOVE,
                        direction=direction or board.robot.orientation,
                        success=True,
                        message="AI: Moved",
                    )
                    history.add_action(action, board.to_dict())

                elif action_type == "pick":
                    GameService.pick_flower(board)
                    action = Action(
                        action_type=ActionType.PICK,
                        direction=direction or board.robot.orientation,
                        success=True,
                        message="AI: Picked flower",
                    )
                    history.add_action(action, board.to_dict())

                elif action_type == "give":
                    GameService.give_flowers(board)
                    action = Action(
                        action_type=ActionType.GIVE,
                        direction=direction or board.robot.orientation,
                        success=True,
                        message="AI: Gave flowers",
                    )
                    history.add_action(action, board.to_dict())

            self.repository.save(command.game_id, board)
            self.repository.save_history(command.game_id, history)

            status = board.get_status().value
            success = status == "victory"
            message = (
                "AI completed the game successfully!"
                if success
                else "AI attempted to solve but couldn't complete"
            )

            return AutoplayResult(
                success=success,
                actions_taken=len(actions),
                board_state=board.to_dict(),
                message=message,
            )

        except Exception as e:
            return AutoplayResult(
                success=False,
                actions_taken=0,
                board_state=board.to_dict(),
                message=f"AI failed: {str(e)}",
            )
