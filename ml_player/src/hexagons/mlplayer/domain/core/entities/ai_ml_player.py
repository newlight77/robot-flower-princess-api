"""
AI ML Player - Hybrid approach combining heuristics with machine learning.

This player uses trained ML models when available, with heuristics as fallback.
The architecture supports:
- Primary: Trained ML models (Random Forest, Gradient Boosting)
- Fallback: Heuristic-based decision making
"""

from typing import Any

from hexagons.mlplayer.domain.core.value_objects import StrategyConfig
from hexagons.mlplayer.domain.ml import FeatureEngineer, ModelRegistry
from shared.logging import logger

from ..value_objects.game_state import GameState


class AIMLPlayer:
    """
    ML-based AI player with hybrid approach.

    Primary: Uses trained ML models for action prediction
    Fallback: Uses weighted heuristics when no model available

    Architecture:
    - evaluate_board(): Scores current state (ML model or heuristics)
    - select_action(): Chooses best action (ML prediction or rule-based)
    - plan_sequence(): Plans ahead (ML-guided or search + heuristics)
    """

    def __init__(self, config: StrategyConfig | None = None, model_path: str | None = None):
        """
        Initialize ML player with configuration.

        Args:
            config: Strategy configuration (weights, hyperparameters)
            model_path: Optional path to specific model, otherwise loads best model
        """
        self.config = config or StrategyConfig.default()

        # Try to load trained ML model
        self.model: Any | None = None
        self.model_metadata = None
        self.feature_engineer = FeatureEngineer()
        self.use_ml = False
        logger.info(f"AIMLPlayer.init: Initializing with config={self.config.to_dict()}")
        try:
            registry = ModelRegistry()
            logger.info(f"AIMLPlayer.init: Model registry initialized: {registry}")
            if model_path:
                # Load specific model
                import os
                logger.info(f"AIMLPlayer.init: Loading specific model: {model_path}")
                model_name = os.path.splitext(os.path.basename(model_path))[0]
                self.model = registry.load_model(model_name)
                logger.info(f"AIMLPlayer.init: Loaded specific model: {model_name}")
                self.use_ml = True
            else:
                # Load best model
                logger.info("AIMLPlayer.init: Loading best model")
                self.model, self.model_metadata = registry.load_best_model()
                if self.model:
                    logger.info(
                        f"AIMLPlayer.init: Loaded best model: {self.model_metadata.name} "
                        f"ML model loaded: {self.model_metadata.name} "
                        f"(accuracy={self.model_metadata.test_accuracy:.4f})"
                    )
                    self.use_ml = True
                else:
                    logger.warning("No trained model found, using heuristics")
        except Exception as e:
            logger.warning(f"Failed to load ML model: {e}, using heuristics")
            self.model = None
            self.use_ml = False

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
                abs(state.robot["position"]["row"] - f["row"]) + abs(state.robot["position"]["col"] - f["col"])
                for f in state.board["flowers_positions"]
            )
            logger.info(f"AIMLPlayer.evaluate_board: Distance to nearest flower={min_flower_dist}")
            score += self.config.distance_to_flower_weight * min_flower_dist

        # Distance to princess (when holding flowers)
        if len(state.robot["flowers_delivered"]) > 0:
            princess_dist = state._distance_to_princess(state.robot["position"], state.princess["position"])
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

        Primary: Uses trained ML model for prediction
        Fallback: Uses rule-based decision tree with heuristics

        Args:
            state: Current board state

        Returns:
            Tuple of (action_type, direction) e.g. ("move", "NORTH")
        """
        logger.info("AIMLPlayer.select_action: Selecting action for state")

        # Try ML prediction first
        if self.use_ml and self.model is not None:
            try:
                action, direction = self._predict_with_ml(state)
                logger.info(f"ML prediction: {action} {direction or ''}")
                return (action, direction)
            except Exception as e:
                logger.warning(f"ML prediction failed: {e}, falling back to heuristics")

        # Fallback to heuristics
        return self._select_action_heuristic(state)

    def _predict_with_ml(self, state: GameState) -> tuple[str, str | None]:
        """
        Predict action using trained ML model.

        Args:
            state: Current game state

        Returns:
            Tuple of (action, direction)
        """
        # Extract features
        features = self.feature_engineer.extract_features(state.to_dict())

        # Predict action label
        label = self.model.predict([features])[0]

        # Decode action
        action, direction = self.feature_engineer.decode_action(int(label))

        return (action, direction)

    def _select_action_heuristic(self, state: GameState) -> tuple[str, str | None]:
        """
        Select action using heuristics (fallback).

        Args:
            state: Current game state

        Returns:
            Tuple of (action, direction)
        """
        logger.info("Using heuristic action selection")

        # If next to princess with flowers → give
        if (
            state.robot["position"] in self._get_adjacent_positions(state.princess["position"])
            and len(state.robot["flowers_collected"]) > 0
        ):
            return ("give", None)

        # If at flower and not full → pick
        robot_pos = state.robot["position"]
        for flower_pos in state.board["flowers_positions"]:
            if (
                robot_pos["row"] == flower_pos["row"]
                and robot_pos["col"] == flower_pos["col"]
                and len(state.robot["flowers_collected"]) < state.robot["flowers_collection_capacity"]
            ):
                return ("pick", None)

        # If holding flowers → move toward princess
        if len(state.robot["flowers_collected"]) > 0:
            direction = self._get_direction_to_target(state.robot["position"], state.princess["position"])
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
        logger.info(f"AIMLPlayer._get_direction_to_target: Getting direction to target={current} -> {target}")

        dr = target["row"] - current["row"]
        dc = target["col"] - current["col"]

        # Prioritize vertical or horizontal based on larger difference
        if abs(dr) > abs(dc):
            return "SOUTH" if dr > 0 else "NORTH"
        else:
            return "EAST" if dc > 0 else "WEST"

    def plan_sequence(self, state: GameState, horizon: int | None = None) -> list[tuple[str, str | None]]:
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
        logger.info(f"AIMLPlayer.plan_sequence: Planning sequence for state={state.to_dict()} with horizon={horizon}")

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

    def get_model_info(self) -> dict[str, Any]:
        """
        Get information about the loaded model.

        Returns:
            Dictionary with model information
        """
        if self.model_metadata:
            return {
                "model_loaded": True,
                "model_name": self.model_metadata.name,
                "model_type": self.model_metadata.model_type,
                "test_accuracy": self.model_metadata.test_accuracy,
                "train_samples": self.model_metadata.train_samples,
                "created_at": self.model_metadata.created_at,
            }
        return {
            "model_loaded": False,
            "fallback_mode": "heuristics",
        }

    def _get_adjacent_positions(self, position: tuple[int, int], state: GameState) -> list[tuple[int, int]]:
        """Get all valid adjacent empty positions."""
        adjacent_positions = [
            {"row": position["row"] + 1, "col": position["col"]},
            {"row": position["row"] - 1, "col": position["col"]},
            {"row": position["row"], "col": position["col"] + 1},
            {"row": position["row"], "col": position["col"] - 1},
        ]

        # filter out positions that are out of bounds
        adjacent_positions = [p for p in adjacent_positions
            if p["row"] >= 0
            and p["row"] < state.board["rows"]
            and p["col"] >= 0
            and p["col"] < state.board["cols"]
        ]

        # # filter out positions that are obstacles
        # adjacent_positions = [p for p in adjacent_positions if p not in state.board["obstacles_positions"]]

        # # filter out positions that are flowers
        # adjacent_positions = [p for p in adjacent_positions if p not in state.board["flowers_positions"]]

        # # filter out positions that are princess
        # adjacent_positions = [p for p in adjacent_positions if p not in state.princess["position"]]

        # # filter out positions that are robot
        # adjacent_positions = [p for p in adjacent_positions if p not in state.robot["position"]]

        return adjacent_positions
