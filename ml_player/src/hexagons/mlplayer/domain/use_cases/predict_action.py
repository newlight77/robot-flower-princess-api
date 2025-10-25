"""Use case for predicting next action using ML player."""

from dataclasses import dataclass
from typing import Optional

from hexagons.mlplayer.domain.core.entities import AIMLPlayer, BoardState
from hexagons.mlplayer.domain.core.value_objects import StrategyConfig
from hexagons.mlplayer.domain.ports.game_client import GameClientPort


@dataclass
class PredictActionCommand:
    """Command for predicting action."""

    strategy: str  # "default", "aggressive", "conservative"
    game_id: str
    status: str
    board: dict
    robot: dict
    princess: dict
    obstacles: dict
    flowers: dict


@dataclass
class PredictActionResult:
    """Result of action prediction."""
    game_id: str
    action: str
    direction: Optional[str]
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
        game_state = await self.game_client.get_game_state(command.game_id)

        # Convert to BoardState
        board_state = self._convert_to_board_state(game_state)

        # Get configuration
        config = self._get_config(command.strategy)

        # Create ML player
        player = AIMLPlayer(config)

        # Evaluate board
        score = player.evaluate_board(board_state)

        # Predict action
        action, direction = player.select_action(board_state)

        # Calculate confidence (simplified for MVP)
        # Future: Use ML model's prediction confidence
        confidence = self._calculate_confidence(board_state, action)

        return PredictActionResult(
            action=action,
            direction=direction,
            confidence=confidence,
            board_score=score,
            config_used=config.to_dict(),
        )

    def _convert_to_board_state(self, game_state: dict) -> BoardState:
        """Convert game state dict to BoardState."""
        robot = game_state["robot"]
        board = game_state["board"]

        return BoardState(
            rows=board["rows"],
            cols=board["cols"],
            robot_position=(robot["position"]["row"], robot["position"]["col"]),
            robot_orientation=robot["orientation"],
            robot_flowers_held=robot["flowers"]["held"],
            robot_max_capacity=robot["flowers"]["capacity"],
            princess_position=(
                game_state["princess"]["position"]["row"],
                game_state["princess"]["position"]["col"],
            ),
            flowers=[
                (f["row"], f["col"]) for f in game_state.get("flowers", {}).get("positions", [])
            ],
            obstacles=[
                (o["row"], o["col"])
                for o in game_state.get("obstacles", {}).get("positions", [])
            ],
            flowers_delivered=game_state["princess"]["flowers"]["delivered"],
        )

    def _get_config(self, strategy: str) -> StrategyConfig:
        """Get strategy configuration based on strategy name."""
        if strategy == "aggressive":
            return StrategyConfig.aggressive()
        elif strategy == "conservative":
            return StrategyConfig.conservative()
        else:
            return StrategyConfig.default()

    def _calculate_confidence(self, board_state: BoardState, action: str) -> float:
        """
        Calculate confidence score for the predicted action.

        MVP: Simple heuristic-based confidence
        Future: Use ML model's prediction probability
        """
        # Simple confidence based on board state
        confidence = 0.5  # Base confidence

        # Higher confidence if clear path
        if board_state._obstacle_density() < 0.2:
            confidence += 0.2

        # Higher confidence if close to target
        if action == "pick" and board_state.robot_position in board_state.flowers:
            confidence += 0.3
        elif action == "give" and board_state.robot_position == board_state.princess_position:
            confidence += 0.3

        return min(1.0, confidence)
