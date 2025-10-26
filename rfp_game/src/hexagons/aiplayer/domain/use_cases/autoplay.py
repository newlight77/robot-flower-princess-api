from dataclasses import dataclass
from typing import Literal, Optional
from copy import deepcopy
from hexagons.game.domain.ports.game_repository import GameRepository
from hexagons.aiplayer.domain.core.entities.ai_greedy_player import AIGreedyPlayer
from hexagons.aiplayer.domain.core.entities.ai_optimal_player import AIOptimalPlayer
from hexagons.aiplayer.domain.core.entities.ml_proxy_player import MLProxyPlayer
from hexagons.aiplayer.domain.ports.ml_player_client import MLPlayerClientPort
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.services.game_service import GameService
from shared.logging import get_logger

logger = get_logger("autoplay_use_case")
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
        self.repository = repository
        self.ml_client = ml_client

    async def execute(self, command: AutoplayCommand) -> AutoplayResult:
        """Let AI solve the game automatically."""
        logger.info(
            "execute: AutoplayCommand game_id=%s strategy=%s", command.game_id, command.strategy
        )
        game = self.repository.get(command.game_id)
        if game is None:
            raise ValueError(f"Game {command.game_id} not found")

        # Create a copy for the solver
        game_copy = deepcopy(game)

        logger.info(f"AutoplayUseCase.execute: Game copy {game_copy.to_dict()}")

        try:
            # Select AI player based on strategy
            if command.strategy == "optimal":
                # Fast & efficient (25% fewer actions, but 13% lower success rate)
                actions = AIOptimalPlayer.solve(game_copy)
                strategy_name = "Optimal AI (A* + Planning)"
            elif command.strategy == "ml":
                # ML Player (hybrid heuristic/ML approach)
                if self.ml_client is None:
                    raise ValueError("ML Player client not configured. Cannot use 'ml' strategy.")

                # ML Player works iteratively (one action at a time)
                # We'll execute actions as they come
                ml_player = MLProxyPlayer(self.ml_client, strategy="default")
                actions = await ml_player.solve_async(game_copy, command.game_id)
                strategy_name = "ML Player (Hybrid)"
            else:  # "greedy" (default)
                # Safe & reliable (75% success rate)
                actions = AIGreedyPlayer.solve(game_copy)
                strategy_name = "Greedy AI (Safe)"

            self.logger.info("Using %s, generated %d actions", strategy_name, len(actions))

            # Apply actions to original board
            for action_type, direction in actions:
                # Always rotate to the solver-provided direction first (if provided)
                if direction is not None:
                    GameService.rotate_robot(game, direction)

                if action_type == "rotate":
                    GameService.rotate_robot(game, direction)

                elif action_type == "move":
                    GameService.move_robot(game)

                elif action_type == "pick":
                    GameService.pick_flower(game)

                elif action_type == "drop":
                    GameService.drop_flower(game)

                elif action_type == "give":
                    GameService.give_flowers(game)

                elif action_type == "clean":
                    GameService.clean_obstacle(game)

            self.repository.save(command.game_id, game)

            status = game.get_status().value
            success = status == "victory"
            message = (
                "AI completed the game successfully!"
                if success
                else "AI attempted to solve but couldn't complete"
            )

            return AutoplayResult(
                success=success,
                actions_taken=len(actions),
                game=game,
                message=message,
            )

        except Exception as e:
            return AutoplayResult(
                success=False,
                actions_taken=0,
                game=game,
                message=f"AI failed: {str(e)}",
            )
