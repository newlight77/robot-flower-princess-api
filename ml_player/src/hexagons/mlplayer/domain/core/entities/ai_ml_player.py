"""
AI ML Player - Hybrid approach combining heuristics with ML-ready architecture.

This player uses weighted heuristics for the MVP, designed for future ML upgrade.
The architecture supports:
- Current: Heuristic-based decision making with tuned weights
- Future: Replace heuristics with trained ML models (sklearn, pytorch, etc.)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from hexagons.mlplayer.domain.core.value_objects import StrategyConfig


@dataclass
class BoardState:
    """Simplified board state representation for ML player."""

    rows: int
    cols: int
    robot_position: Tuple[int, int]
    robot_orientation: str  # "NORTH", "SOUTH", "EAST", "WEST"
    robot_flowers_held: int
    robot_max_capacity: int
    princess_position: Tuple[int, int]
    flowers: List[Tuple[int, int]]
    obstacles: List[Tuple[int, int]]
    flowers_delivered: int

    def to_feature_vector(self) -> List[float]:
        """
        Convert board state to feature vector for ML.

        Future: This will be input to ML model.
        Current: Used for weighted scoring.
        """
        features = [
            float(self.rows),
            float(self.cols),
            float(self.robot_position[0]),
            float(self.robot_position[1]),
            float(self.robot_flowers_held),
            float(self.robot_max_capacity),
            float(self.princess_position[0]),
            float(self.princess_position[1]),
            float(len(self.flowers)),
            float(len(self.obstacles)),
            float(self.flowers_delivered),
            # Derived features
            self._distance_to_princess(),
            self._closest_flower_distance(),
            self._obstacle_density(),
        ]
        return features

    def _distance_to_princess(self) -> float:
        """Manhattan distance to princess."""
        return float(abs(self.robot_position[0] - self.princess_position[0]) + abs(
            self.robot_position[1] - self.princess_position[1]
        ))

    def _closest_flower_distance(self) -> float:
        """Distance to closest flower."""
        if not self.flowers:
            return 0.0
        distances = [
            abs(self.robot_position[0] - f[0]) + abs(self.robot_position[1] - f[1])
            for f in self.flowers
        ]
        return float(min(distances))

    def _obstacle_density(self) -> float:
        """Obstacle density around robot."""
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                pos = (self.robot_position[0] + dr, self.robot_position[1] + dc)
                if pos in self.obstacles:
                    count += 1
        return count / 9.0  # Normalize to [0, 1]


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

    def __init__(self, config: Optional[StrategyConfig] = None):
        """
        Initialize ML player with configuration.

        Args:
            config: Strategy configuration (weights, hyperparameters)
        """
        self.config = config or StrategyConfig.default()
        self.model = None  # Future: Load trained ML model here

    def evaluate_board(self, state: BoardState) -> float:
        """
        Evaluate board state and return a score.

        MVP: Uses weighted heuristics
        Future: Replace with ML model prediction

        Args:
            state: Current board state

        Returns:
            Score (higher is better)
        """
        if self.model is not None:
            # Future: Use ML model
            # features = state.to_feature_vector()
            # return self.model.predict([features])[0]
            pass

        # Current: Heuristic evaluation
        score = 0.0

        # Distance to nearest flower
        if state.flowers and state.robot_flowers_held < state.robot_max_capacity:
            min_flower_dist = min(
                abs(state.robot_position[0] - f[0]) + abs(state.robot_position[1] - f[1])
                for f in state.flowers
            )
            score += self.config.distance_to_flower_weight * min_flower_dist

        # Distance to princess (when holding flowers)
        if state.robot_flowers_held > 0:
            princess_dist = state._distance_to_princess()
            score += self.config.distance_to_princess_weight * princess_dist

        # Obstacle density penalty
        obstacle_density = state._obstacle_density()
        score += self.config.obstacle_density_weight * obstacle_density

        # Flower clustering bonus
        if len(state.flowers) > 1:
            # Calculate average pairwise distance between flowers
            total_dist = 0
            count = 0
            for i, f1 in enumerate(state.flowers):
                for f2 in state.flowers[i + 1 :]:
                    dist = abs(f1[0] - f2[0]) + abs(f1[1] - f2[1])
                    total_dist += dist
                    count += 1
            if count > 0:
                avg_dist = total_dist / count
                # Lower average distance = more clustered = bonus
                cluster_score = 1.0 / (1.0 + avg_dist)
                score += self.config.flower_cluster_bonus * cluster_score

        return score

    def select_action(self, state: BoardState) -> Tuple[str, Optional[str]]:
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

        # If at princess with flowers → give
        if (
            state.robot_position == state.princess_position
            and state.robot_flowers_held > 0
        ):
            return ("give", None)

        # If at flower and not full → pick
        if (
            state.robot_position in state.flowers
            and state.robot_flowers_held < state.robot_max_capacity
        ):
            return ("pick", None)

        # If holding flowers → move toward princess
        if state.robot_flowers_held > 0:
            direction = self._get_direction_to_target(
                state.robot_position, state.princess_position
            )
            return ("move", direction)

        # Otherwise → move toward nearest flower
        if state.flowers:
            nearest_flower = min(
                state.flowers,
                key=lambda f: abs(state.robot_position[0] - f[0])
                + abs(state.robot_position[1] - f[1]),
            )
            direction = self._get_direction_to_target(state.robot_position, nearest_flower)
            return ("move", direction)

        # Default: do nothing (shouldn't reach here)
        return ("move", state.robot_orientation)

    def _get_direction_to_target(
        self, current: Tuple[int, int], target: Tuple[int, int]
    ) -> str:
        """Get direction to move toward target."""
        dr = target[0] - current[0]
        dc = target[1] - current[1]

        # Prioritize vertical or horizontal based on larger difference
        if abs(dr) > abs(dc):
            return "SOUTH" if dr > 0 else "NORTH"
        else:
            return "EAST" if dc > 0 else "WEST"

    def plan_sequence(
        self, state: BoardState, horizon: Optional[int] = None
    ) -> List[Tuple[str, Optional[str]]]:
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

    def get_config(self) -> Dict:
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
        raise NotImplementedError("ML model loading will be implemented in future version")

    def save_model(self, model_path: str) -> None:
        """
        Save the current ML model.

        Future implementation for model persistence.
        """
        raise NotImplementedError("ML model saving will be implemented in future version")
