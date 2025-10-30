"""Use case for predicting next action using ML player."""

from dataclasses import dataclass

from hexagons.mlplayer.domain.core.entities import AIMLPlayer
from hexagons.mlplayer.domain.core.value_objects import GameState, StrategyConfig
from shared.logging import get_logger

logger = get_logger("PredictActionUseCase")


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
        logger.info(f"PredictActionUseCase.convert_to_game_state: Converting game state to game_id={game_id}")
        # logger.info(f"PredictActionUseCase.convert_to_game_state: Robot={robot}")
        # logger.info(f"PredictActionUseCase.convert_to_game_state: Princess={princess}")
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
                "flowers_positions": [{"row": f["row"], "col": f["col"]} for f in board.get("flowers_positions", [])],
                "obstacles_positions": [
                    {"row": o["row"], "col": o["col"]} for o in board.get("obstacles_positions", [])
                ],
                "initial_flowers_count": board["initial_flowers_count"],
                "initial_obstacles_count": board["initial_obstacles_count"],
            },
            robot={
                "position": {"row": robot["position"]["row"], "col": robot["position"]["col"]},
                "orientation": robot["orientation"],
                "flowers_collected": [{"row": f["row"], "col": f["col"]} for f in robot["flowers_collected"]],
                "flowers_delivered": [{"row": f["row"], "col": f["col"]} for f in robot["flowers_delivered"]],
                "flowers_collection_capacity": robot["flowers_collection_capacity"],
                "obstacles_cleaned": [{"row": o["row"], "col": o["col"]} for o in robot["obstacles_cleaned"]],
                "executed_actions": [
                    {
                        "type": a.get("type", "unknown"),
                        "direction": a.get("direction", "NORTH"),  # Default direction
                        "success": a.get("success", True),  # Default to True if not present
                        "message": a.get("message", ""),  # Default to empty string if not present
                    }
                    for a in robot.get("executed_actions", [])
                ],
            },
            princess={
                "position": {
                    "row": princess["position"]["row"],
                    "col": princess["position"]["col"],
                },
                "flowers_received": [{"row": f["row"], "col": f["col"]} for f in princess["flowers_received"]],
                "mood": princess["mood"],
            },
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
    1. Receives game state from command (passed via API request)
    2. Converts it to GameState
    3. Uses AIMLPlayer to predict action
    4. Returns the prediction (action is executed by MLProxyPlayer in rfp_game)
    """

    def execute(self, command: PredictActionCommand) -> PredictActionResult:
        """
        Execute prediction use case.

        Args:
            command: Prediction command with game state

        Returns:
            Prediction result with recommended action
        """
        # Convert command data to GameState
        logger.info(f"PredictActionUseCase.execute: Converting game state to GameState for game_id={command.game_id}")
        game_state: GameState = command.convert_to_game_state()
        logger.info(f"PredictActionUseCase.execute: GameState converted {game_state.to_dict()}")

        # Get configuration
        logger.info(f"PredictActionUseCase.execute: Getting configuration for strategy={command.strategy}")
        config: StrategyConfig = self._get_config(command.strategy)

        # Create ML player
        logger.info("PredictActionUseCase.execute: Creating ML player")
        player: AIMLPlayer = AIMLPlayer(config)

        # Evaluate board
        logger.info("PredictActionUseCase.execute: Evaluating board")
        score: float = player.evaluate_game(game_state)

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
        if action == "pick" and game_state.robot["position"] in game_state.board["flowers_positions"]:
            confidence += 0.3
        elif action == "give" and game_state.robot["position"] == game_state.princess["position"]:
            confidence += 0.3

        return min(1.0, confidence)
