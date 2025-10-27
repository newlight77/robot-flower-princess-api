"""
ML Proxy Player - Delegates decision-making to the ML Player service.

This player acts as a proxy, forwarding game state to the ML Player service
and returning the predicted actions. It allows seamless integration of the
external ML Player service into the autoplay system.
"""

from typing import List, Optional, Tuple

from hexagons.aiplayer.domain.ports.ml_player_client import MLPlayerClientPort
from hexagons.game.domain.core.entities.game import Game
from hexagons.game.domain.core.value_objects.direction import Direction
from hexagons.game.domain.core.value_objects.game_status import GameStatus
from shared.logging import get_logger


logger = get_logger("MLProxyPlayer")


class MLProxyPlayer:
    """
    ML Proxy Player that delegates to the ML Player service.

    This player doesn't implement its own solving logic. Instead, it:
    1. Converts the game state to the required format
    2. Calls the ML Player service via HttpMLPlayerClient
    3. Returns the predicted action

    This allows the ML Player service (with its hybrid heuristic/ML approach)
    to be used as a strategy in the autoplay system.
    """

    def __init__(self, ml_client: MLPlayerClientPort, strategy: str = "default"):
        """
        Initialize ML Proxy Player.

        Args:
            ml_client: Client for communicating with ML Player service
            strategy: Strategy to use ("default", "aggressive", "conservative")
        """
        self.ml_client = ml_client
        self.strategy = strategy

    def solve(self, game: Game) -> List[Tuple[str, Direction]]:
        """
        Solve the game by delegating to ML Player service.

        Args:
            game: Current game state

        Returns:
            List of action tuples (action_type, direction)

        Note:
            This method is synchronous but calls async ML client internally.
            In practice, this would be called from an async context in the use case.
        """
        # This is a placeholder - the actual implementation will be async
        # The solve method will be called from an async use case context
        raise NotImplementedError("MLProxyPlayer.solve() should be called via async solve_async() method")

    async def solve_async(self, game: Game, game_id: str) -> List[Tuple[str, Direction]]:
        """
        Async version of solve that calls the ML Player service.

        Args:
            game: Current game state
            game_id: Game identifier

        Returns:
            List of action tuples (action_type, direction)
        """
        logger.info(f"MLProxyPlayer.solve_async: Game {game.to_dict()}")
        # Convert game state to format expected by ML Player
        game_state = self._convert_game_to_state(game)

        logger.info(f"MLProxyPlayer.solve_async: Game state {game_state}")

        # Get prediction from ML Player service
        try:
            logger.info(
                f"MLProxyPlayer.solve_async: Predicting action game_id={game_id} with strategy strategy={self.strategy}"
            )

            prediction: dict = await self.ml_client.predict_action(
                game_id=game_id, strategy=self.strategy, game_state=game_state
            )

            logger.info(f"MLProxyPlayer.solve_async: Prediction {prediction}")

            # Convert prediction to action tuple
            action: str = prediction["action"]
            direction_str: str = prediction.get("direction")
            direction: Optional[Direction] = Direction(direction_str.lower()) if direction_str else None

            # Return single action (ML Player returns one action at a time)
            logger.info(f"MLProxyPlayer.solve_async: Returning action={action} and direction={direction}")
            return [(action, direction)]

        except Exception as e:
            # If ML Player service fails, return empty list
            # The autoplay will stop gracefully
            logger.error(f"MLProxyPlayer.solve_async: ML Player service error: {e}")
            return []

    def _convert_game_to_state(self, game: Game) -> dict:
        """
        Convert Game entity to the format expected by ML Player service.

        Args:
            game: Game entity

        Returns:
            Dictionary with game state
        """
        # Determine game status
        logger.info(f"MLProxyPlayer._convert_game_to_state: Determining game status={game.get_status()}")

        game_status = game.get_status()
        if game_status == GameStatus.VICTORY:
            status = "Victory"
        elif game_status == GameStatus.GAME_OVER:
            status = "Game Over"
        else:
            status = "In Progress"

        logger.info(f"MLProxyPlayer._convert_game_to_state: Returning game state={status}")

        return {
            "game_id": game.game_id,
            "status": status,
            "board": game.board.to_dict(),
            "robot": game.robot.to_dict(),
            "princess": game.princess.to_dict(),
        }

    @property
    def name(self) -> str:
        """Get player name for logging."""
        return f"ML Proxy Player ({self.strategy} strategy)"
