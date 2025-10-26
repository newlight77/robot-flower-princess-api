from dataclasses import dataclass
from typing import Set, Literal, Optional
from copy import deepcopy
from hexagons.game.domain.ports.game_repository import GameRepository
from hexagons.aiplayer.domain.core.entities.ai_greedy_player import AIGreedyPlayer
from hexagons.aiplayer.domain.core.entities.ai_optimal_player import AIOptimalPlayer
from hexagons.aiplayer.domain.core.entities.ml_proxy_player import MLProxyPlayer
from hexagons.aiplayer.domain.ports.ml_player_client import MLPlayerClientPort
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.entities.board import Board
from hexagons.game.domain.core.entities.robot import Robot
from hexagons.game.domain.core.entities.princess import Princess
from hexagons.game.domain.core.entities.position import Position
from hexagons.game.domain.services.game_service import GameService
from shared.logging import get_logger


AIStrategy = Literal["greedy", "optimal", "ml"]


@dataclass
class AutoplayCommand:
    game_id: str
    strategy: AIStrategy = "greedy"  # Default to safe & reliable strategy


@dataclass
class AutoplayResult:
    success: bool
    actions_taken: int
    game: "Game"  # Import Game from hexagons.game.domain.core.entities.game
    message: str


class AutoplayUseCase:
    def __init__(self, repository: GameRepository, ml_client: Optional[MLPlayerClientPort] = None):
        self.logger = get_logger(self)
        self.logger.debug("Initializing AutoplayUseCase repository=%r ml_client=%r", repository, ml_client)
        self.repository = repository
        self.ml_client = ml_client

    async def execute(self, command: AutoplayCommand) -> AutoplayResult:
        """Let AI solve the game automatically."""
        self.logger.info(
            "execute: AutoplayCommand game_id=%s strategy=%s", command.game_id, command.strategy
        )
        board = self.repository.get(command.game_id)
        if board is None:
            raise ValueError(f"Game {command.game_id} not found")

        # Create a copy for the solver
        board_copy = deepcopy(board)

        try:
            # Select AI player based on strategy
            if command.strategy == "optimal":
                # Fast & efficient (25% fewer actions, but 13% lower success rate)
                actions = AIOptimalPlayer.solve(board_copy)
                strategy_name = "Optimal AI (A* + Planning)"
            elif command.strategy == "ml":
                # ML Player (hybrid heuristic/ML approach)
                if self.ml_client is None:
                    raise ValueError("ML Player client not configured. Cannot use 'ml' strategy.")

                # ML Player works iteratively (one action at a time)
                # We'll execute actions as they come
                ml_player = MLProxyPlayer(self.ml_client, strategy="default")
                actions = await ml_player.solve_async(board_copy, command.game_id)
                strategy_name = "ML Player (Hybrid)"
            else:  # "greedy" (default)
                # Safe & reliable (75% success rate)
                actions = AIGreedyPlayer.solve(board_copy)
                strategy_name = "Greedy AI (Safe)"

            self.logger.info("Using %s, generated %d actions", strategy_name, len(actions))

            # Apply actions to original board
            for action_type, direction in actions:
                # Always rotate to the solver-provided direction first (if provided)
                if direction is not None:
                    GameService.rotate_robot(board, direction)

                if action_type == "rotate":
                    dir_str = direction.value if direction is not None else "unknown"

                elif action_type == "move":
                    GameService.move_robot(board)

                elif action_type == "pick":
                    GameService.pick_flower(board)

                elif action_type == "drop":
                    GameService.drop_flower(board)

                elif action_type == "give":
                    GameService.give_flowers(board)

                elif action_type == "clean":
                    GameService.clean_obstacle(board)

            self.repository.save(command.game_id, board)

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
                game=board,
                message=message,
            )

        except Exception as e:
            return AutoplayResult(
                success=False,
                actions_taken=0,
                game=board,
                message=f"AI failed: {str(e)}",
            )
