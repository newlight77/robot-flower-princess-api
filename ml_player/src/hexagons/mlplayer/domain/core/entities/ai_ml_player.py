"""
AI ML Player - Hybrid approach combining heuristics with ML-ready architecture.

This player uses weighted heuristics for the MVP, designed for future ML upgrade.
The architecture supports:
- Current: Heuristic-based decision making with tuned weights
- Future: Replace heuristics with trained ML models (sklearn, pytorch, etc.)
"""


from hexagons.mlplayer.domain.core.value_objects import StrategyConfig
from shared.logging import logger

from ..value_objects.game_state import GameState


class AIMLPlayer:
    """
    ML-inspired AI player using hybrid heuristic + ML approach.

    MVP: Uses weighted heuristics with configurable parameters
    Future: Can swap heuristics with trained ML models

    Architecture:
    - evaluate_board(): Scores current state (heuristics → ML model)
    - select_action(): Chooses best action (rule-based → policy network)
    - plan_sequence(): Plans ahead (search + heuristics → planning network)
    """

    def __init__(self, config: StrategyConfig | None = None):
        """
        Initialize ML player with configuration.

        Args:
            config: Strategy configuration (weights, hyperparameters)
        """
        self.config = config or StrategyConfig.default()
        self.model = None  # Future: Load trained ML model here

    def evaluate_board(self, state: GameState) -> float:
        """
        Evaluate board state and return a score.

        MVP: Uses weighted heuristics
        Future: Replace with ML model prediction

        Args:
            state: Current board state

        Returns:
            Score (higher is better)
        """
        logger.info(f"AIMLPlayer.evaluate_board: Evaluating board={state.to_dict()}")

        if self.model is not None:
            # Future: Use ML model
            # features = state.to_feature_vector()
            # return self.model.predict([features])[0]
            pass

        # Current: Heuristic evaluation
        score = 0.0

        # Distance to nearest flower
        if (
            state.board["flowers_positions"]
            and len(state.robot["flowers_delivered"]) < state.robot["flowers_collection_capacity"]
        ):
            min_flower_dist = min(
                abs(state.robot["position"]["row"] - f["row"])
                + abs(state.robot["position"]["col"] - f["col"])
                for f in state.board["flowers_positions"]
            )
            logger.info(f"AIMLPlayer.evaluate_board: Distance to nearest flower={min_flower_dist}")
            score += self.config.distance_to_flower_weight * min_flower_dist

        # Distance to princess (when holding flowers)
        if len(state.robot["flowers_delivered"]) > 0:
            princess_dist = state._distance_to_princess(
                state.robot["position"], state.princess["position"]
            )
            logger.info(f"AIMLPlayer.evaluate_board: Distance to princess={princess_dist}")
            score += self.config.distance_to_princess_weight * princess_dist

        # Obstacle density penalty
        obstacle_density = state._obstacle_density()
        logger.info(f"AIMLPlayer.evaluate_board: Obstacle density={obstacle_density}")
        score += self.config.obstacle_density_weight * obstacle_density

        # Flower clustering bonus
        if len(state.board["flowers_positions"]) > 1:
            # Calculate average pairwise distance between flowers
            total_dist = 0
            count = 0
            for i, f1 in enumerate(state.board["flowers_positions"]):
                for f2 in state.board["flowers_positions"][i + 1 :]:
                    dist = abs(f1["row"] - f2["row"]) + abs(f1["col"] - f2["col"])
                    total_dist += dist
                    count += 1
            if count > 0:
                avg_dist = total_dist / count
                # Lower average distance = more clustered = bonus
                cluster_score = 1.0 / (1.0 + avg_dist)
                logger.info(f"AIMLPlayer.evaluate_board: Flower clustering bonus={cluster_score}")
                score += self.config.flower_cluster_bonus * cluster_score

        logger.info(f"AIMLPlayer.evaluate_board: Heuristic evaluation score={score}")

        return score

    def select_action(self, state: GameState) -> tuple[str, str | None]:
        """
        Select best action for current state.

        MVP: Rule-based decision tree with heuristics
        Future: Replace with policy network

        Args:
            state: Current board state

        Returns:
            Tuple of (action_type, direction) e.g. ("move", "NORTH")
        """
        # Simple decision tree for MVP
        # Future: Replace with neural network policy

        logger.info(f"AIMLPlayer.select_action: Selecting action for state={state.to_dict()}")

        # If next to princess with flowers → give
        if (
            state.robot["position"] in self._get_adjacent_positions(state.princess["position"])
            and len(state.robot["flowers_delivered"]) > 0
        ):
            return ("give", None)

        # If at flower and not full → pick
        if (
            state.robot["position"] in state.board["flowers_positions"]
            and len(state.robot["flowers_delivered"]) < state.robot["flowers_collection_capacity"]
        ):
            return ("pick", None)

        # If holding flowers → move toward princess
        if len(state.robot["flowers_delivered"]) > 0:
            direction = self._get_direction_to_target(
                state.robot["position"], state.princess["position"]
            )
            return ("move", direction)

        # Otherwise → move toward nearest flower
        if state.board["flowers_positions"]:
            nearest_flower = min(
                state.board["flowers_positions"],
                key=lambda f: abs(state.robot["position"]["row"] - f["row"])
                + abs(state.robot["position"]["col"] - f["col"]),
            )
            direction = self._get_direction_to_target(state.robot["position"], nearest_flower)
            return ("move", direction)

        # Default: do nothing (shouldn't reach here)
        return ("move", state.robot["orientation"])

    def _get_direction_to_target(self, current: tuple[int, int], target: tuple[int, int]) -> str:
        """Get direction to move toward target."""
        logger.info(
            f"AIMLPlayer._get_direction_to_target: Getting direction to target={current} -> {target}"
        )

        dr = target["row"] - current["row"]
        dc = target["col"] - current["col"]

        # Prioritize vertical or horizontal based on larger difference
        if abs(dr) > abs(dc):
            return "SOUTH" if dr > 0 else "NORTH"
        else:
            return "EAST" if dc > 0 else "WEST"

    def plan_sequence(
        self, state: GameState, horizon: int | None = None
    ) -> list[tuple[str, str | None]]:
        """
        Plan a sequence of actions.

        MVP: Greedy lookahead with heuristic evaluation
        Future: Replace with planning network or Monte Carlo Tree Search

        Args:
            state: Current board state
            horizon: Planning horizon (default: from config)

        Returns:
            List of actions
        """
        logger.info(
            f"AIMLPlayer.plan_sequence: Planning sequence for state={state.to_dict()} with horizon={horizon}"
        )

        horizon = horizon or self.config.lookahead_depth
        actions = []

        # Simple greedy planning for MVP
        # Future: Implement more sophisticated planning (MCTS, learned planner)
        for _ in range(horizon):
            action = self.select_action(state)
            actions.append(action)
            # In real implementation, we'd simulate the action and update state
            # For MVP, we just return the first action
            break

        return actions

    def get_config(self) -> dict:
        """Get current configuration."""
        return self.config.to_dict()

    def load_model(self, model_path: str) -> None:
        """
        Load a trained ML model.

        Future implementation:
        - Load sklearn model: joblib.load(model_path)
        - Load pytorch model: torch.load(model_path)
        - Load tensorflow model: tf.keras.models.load_model(model_path)
        """
        logger.info(f"AIMLPlayer.load_model: Loading model from={model_path}")
        raise NotImplementedError("ML model loading will be implemented in future version")

    def save_model(self, model_path: str) -> None:
        """
        Save the current ML model.

        Future implementation for model persistence.
        """
        logger.info(f"AIMLPlayer.save_model: Saving model to={model_path}")
        raise NotImplementedError("ML model saving will be implemented in future version")

    def _get_adjacent_positions(self, position: tuple[int, int]) -> list[tuple[int, int]]:
        """Get all valid adjacent empty positions."""
        adjacent_positions = [
            {"row": position["row"] + 1, "col": position["col"]},
            {"row": position["row"] - 1, "col": position["col"]},
            {"row": position["row"], "col": position["col"] + 1},
            {"row": position["row"], "col": position["col"] - 1},
        ]

        return adjacent_positions
