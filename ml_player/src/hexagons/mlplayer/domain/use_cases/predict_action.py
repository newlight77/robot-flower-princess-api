"""Use case for predicting next action using ML player."""

from dataclasses import dataclass

from hexagons.mlplayer.domain.core.entities import AIMLPlayer, GameState
from hexagons.mlplayer.domain.core.value_objects import StrategyConfig
from hexagons.mlplayer.domain.ports.game_client import GameClientPort
from shared.logging import logger


@dataclass
class PredictActionCommand:
    """Command for predicting action."""

    strategy: str  # "default", "aggressive", "conservative"
    game_id: str
    board: dict
    robot: dict
    princess: dict
    obstacles: dict
    flowers: dict

    def convert_to_game_state(self) -> GameState:
        """Convert game state dict to GameState."""

        game_id, board, robot, princess = self.game_id, self.board, self.robot, self.princess
        logger.info(
            f"PredictActionUseCase.convert_to_game_state: Converting game state to game_id={game_id}"
        )
        logger.info(f"PredictActionUseCase.convert_to_game_state: Robot={robot}")
        logger.info(f"PredictActionUseCase.convert_to_game_state: Princess={princess}")
        # logger.info(f"PredictActionUseCase.convert_to_game_state: Board={board}")
        # logger.info(f"PredictActionUseCase.convert_to_game_state: Game={game}")

        game = GameState(
            game_id=game_id,
            board={
                "rows": board["rows"],
                "cols": board["cols"],
                "grid": board["grid"],
                "robot_position": {
                    "row": board["robot_position"]["row"],
                    "col": board["robot_position"]["col"],
                },
                "princess_position": {
                    "row": board["princess_position"]["row"],
                    "col": board["princess_position"]["col"],
                },
                "flowers_positions": [
                    {"row": f["row"], "col": f["col"]} for f in board.get("flowers_positions", [])
                ],
                "obstacles_positions": [
                    {"row": o["row"], "col": o["col"]} for o in board.get("obstacles_positions", [])
                ],
                "initial_flowers_count": board["initial_flowers_count"],
                "initial_obstacles_count": board["initial_obstacles_count"],
            },
            robot={
                "position": {"row": robot["position"]["row"], "col": robot["position"]["col"]},
                "orientation": robot["orientation"],
                "flowers_collected": [
                    {"row": f["row"], "col": f["col"]} for f in robot["flowers_collected"]
                ],
                "flowers_delivered": [
                    {"row": f["row"], "col": f["col"]} for f in robot["flowers_delivered"]
                ],
                "flowers_collection_capacity": robot["flowers_collection_capacity"],
                "obstacles_cleaned": [
                    {"row": o["row"], "col": o["col"]} for o in robot["obstacles_cleaned"]
                ],
                "executed_actions": [
                    {
                        "type": a["type"],
                        "direction": a["direction"],
                        "success": a["success"],
                        "message": a["message"],
                    }
                    for a in robot["executed_actions"]
                ],
            },
            princess={
                "position": {
                    "row": princess["position"]["row"],
                    "col": princess["position"]["col"],
                },
                "flowers_received": [
                    {"row": f["row"], "col": f["col"]} for f in princess["flowers_received"]
                ],
                "mood": princess["mood"],
            },
        )
        logger.info(
            f"PredictActionUseCase.convert_to_game_state: GameState converted from dictionary: {game.to_dict()}"
        )
        return game


@dataclass
class PredictActionResult:
    """Result of action prediction."""

    game_id: str
    action: str
    direction: str | None
    confidence: float
    board_score: float
    config_used: dict


class PredictActionUseCase:
    """
    Use case for predicting the next best action using the ML player.

    This use case:
    1. Fetches current game state
    2. Converts it to BoardState
    3. Uses AIMLPlayer to predict action
    4. Returns the prediction
    """

    def __init__(self, game_client: GameClientPort):
        """
        Initialize use case.

        Args:
            game_client: Client for fetching game state
        """
        self.game_client = game_client

    async def execute(self, command: PredictActionCommand) -> PredictActionResult:
        """
        Execute prediction use case.

        Args:
            command: Prediction command

        Returns:
            Prediction result
        """
        # Fetch game state
        logger.info(
            f"PredictActionUseCase.execute: Fetching game state for game_id={command.game_id}"
        )
        game_state: dict = await self.game_client.get_game_state(command.game_id)

        # Convert to BoardState
        logger.info(
            f"PredictActionUseCase.execute: Converting game state to GameState {command.game_id}"
        )
        game_state: GameState = command.convert_to_game_state()
        logger.info(f"PredictActionUseCase.execute: GameState {game_state.to_dict()}")

        # Get configuration
        logger.info(
            f"PredictActionUseCase.execute: Getting configuration for strategy={command.strategy}"
        )
        config: StrategyConfig = self._get_config(command.strategy)

        # Create ML player
        logger.info("PredictActionUseCase.execute: Creating ML player")
        player: AIMLPlayer = AIMLPlayer(config)

        # Evaluate board
        logger.info("PredictActionUseCase.execute: Evaluating board")
        score: float = player.evaluate_board(game_state)

        # Predict action
        logger.info("PredictActionUseCase.execute: Predicting action")
        action, direction = player.select_action(game_state)

        # Calculate confidence (simplified for MVP)
        # Future: Use ML model's prediction confidence
        logger.info("PredictActionUseCase.execute: Calculating confidence")
        confidence: float = self._calculate_confidence(game_state, action)

        return PredictActionResult(
            game_id=command.game_id,
            action=action,
            direction=direction,
            confidence=confidence,
            board_score=score,
            config_used=config.to_dict(),
        )

    def _get_config(self, strategy: str) -> StrategyConfig:
        """Get strategy configuration based on strategy name."""
        if strategy == "aggressive":
            return StrategyConfig.aggressive()
        elif strategy == "conservative":
            return StrategyConfig.conservative()
        else:
            return StrategyConfig.default()

    def _calculate_confidence(self, game_state: GameState, action: str) -> float:
        """
        Calculate confidence score for the predicted action.

        MVP: Simple heuristic-based confidence
        Future: Use ML model's prediction probability
        """
        # Simple confidence based on board state
        confidence = 0.5  # Base confidence

        # Higher confidence if clear path
        if game_state._obstacle_density() < 0.2:
            confidence += 0.2

        # Higher confidence if close to target
        if action == "pick" and game_state.robot_position in game_state.flowers:
            confidence += 0.3
        elif action == "give" and game_state.robot.position == game_state.princess.position:
            confidence += 0.3

        return min(1.0, confidence)
