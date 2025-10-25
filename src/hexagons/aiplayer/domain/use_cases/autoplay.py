from dataclasses import dataclass
from typing import Set
from copy import deepcopy
from hexagons.game.domain.ports.game_repository import GameRepository
from hexagons.aiplayer.domain.core.entities.game_solver_player import GameSolverPlayer
from hexagons.game.domain.core.value_objects.action_type import ActionType
from hexagons.game.domain.core.entities.game_history import Action, GameHistory
from hexagons.game.domain.core.entities.board import Board
from hexagons.game.domain.core.entities.robot import Robot
from hexagons.game.domain.core.entities.princess import Princess
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.services.game_service import GameService
from shared.logging import get_logger


@dataclass
class AutoplayCommand:
    game_id: str


@dataclass
class AutoplayResult:
    success: bool
    actions_taken: int
    board: Board
    robot: Robot
    princess: Princess
    flowers: Set[Position]
    obstacles: Set[Position]
    status: str
    message: str


class AutoplayUseCase:
    def __init__(self, repository: GameRepository):
        self.logger = get_logger(self)
        self.logger.debug("Initializing AutoplayUseCase repository=%r", repository)
        self.repository = repository

    def execute(self, command: AutoplayCommand) -> AutoplayResult:
        """Let AI solve the game automatically."""
        self.logger.info("execute: AutoplayCommand game_id=%s", command.game_id)
        board = self.repository.get(command.game_id)
        if board is None:
            raise ValueError(f"Game {command.game_id} not found")

        history = self.repository.get_history(command.game_id)
        if history is None:
            history = GameHistory(game_id=command.game_id)

        # Create a copy for the solver
        board_copy = deepcopy(board)

        try:
            # Get solution from AI
            actions = GameSolverPlayer.solve(board_copy)

            # Apply actions to original board
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
                    history.add_action(action)

                elif action_type == "move":
                    GameService.move_robot(board)
                    action = Action(
                        action_type=ActionType.MOVE,
                        direction=direction or board.robot.orientation,
                        success=True,
                        message="AI: Moved",
                    )
                    history.add_action(action)

                elif action_type == "pick":
                    GameService.pick_flower(board)
                    action = Action(
                        action_type=ActionType.PICK,
                        direction=direction or board.robot.orientation,
                        success=True,
                        message="AI: Picked flower",
                    )
                    history.add_action(action)

                elif action_type == "drop":
                    GameService.drop_flower(board)
                    action = Action(
                        action_type=ActionType.DROP,
                        direction=direction or board.robot.orientation,
                        success=True,
                        message="AI: Dropped flower",
                    )
                    history.add_action(action)

                elif action_type == "give":
                    GameService.give_flowers(board)
                    action = Action(
                        action_type=ActionType.GIVE,
                        direction=direction or board.robot.orientation,
                        success=True,
                        message="AI: Gave flowers",
                    )
                    history.add_action(action)

                elif action_type == "clean":
                    GameService.clean_obstacle(board)
                    action = Action(
                        action_type=ActionType.CLEAN,
                        direction=direction or board.robot.orientation,
                        success=True,
                        message="AI: Cleaned obstacle",
                    )
                    history.add_action(action)

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
                board=board.board,
                robot=board.robot,
                princess=board.princess,
                flowers=board.flowers,
                obstacles=board.obstacles,
                status=board.get_status().value,
                message=message,
            )

        except Exception as e:
            return AutoplayResult(
                success=False,
                actions_taken=0,
                board=board.board,
                robot=board.robot,
                princess=board.princess,
                flowers=board.flowers,
                obstacles=board.obstacles,
                status=board.get_status().value,
                message=f"AI failed: {str(e)}",
            )
