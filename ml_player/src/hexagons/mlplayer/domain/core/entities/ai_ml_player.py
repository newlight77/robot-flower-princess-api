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
from shared.logging import get_logger

from ..value_objects.game_state import GameState

logger = get_logger("AIMLPlayer")


class AIMLPlayer:
    """
    ML-based AI player with hybrid approach.

    Primary: Uses trained ML models for action prediction
    Fallback: Uses weighted heuristics when no model available

    Architecture:
    - evaluate_game(): Scores current state (ML model or heuristics)
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

    def _evaluate_game(self, state: GameState) -> float:
        """
        Evaluate board state and return a score.

        MVP: Uses weighted heuristics
        Future: Replace with ML model prediction

        Args:
            state: Current board state

        Returns:
            Score (higher is better)
        """
        logger.info(f"AIMLPlayer.evaluate_game: Evaluating game={state.to_dict()}")

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
            logger.info(f"AIMLPlayer.evaluate_game: Distance to nearest flower={min_flower_dist}")
            score += self.config.distance_to_flower_weight * min_flower_dist

        # Distance to princess (when holding flowers)
        if len(state.robot["flowers_delivered"]) > 0:
            princess_dist = state._distance_to_princess(state.robot["position"], state.princess["position"])
            logger.info(f"AIMLPlayer.evaluate_game: Distance to princess={princess_dist}")
            score += self.config.distance_to_princess_weight * princess_dist

        # Obstacle density penalty
        obstacle_density = state._obstacle_density()
        logger.info(f"AIMLPlayer.evaluate_game: Obstacle density={obstacle_density}")
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
                logger.info(f"AIMLPlayer.evaluate_game: Flower clustering bonus={cluster_score}")
                score += self.config.flower_cluster_bonus * cluster_score

        logger.info(f"AIMLPlayer.evaluate_game: Heuristic evaluation score={score}")

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
                logger.info(f"AIMLPlayer.select_action: ML prediction: {action} {direction or ''}")
                return (action, direction)
            except Exception as e:
                logger.warning(f"AIMLPlayer.select_action: ML prediction failed: {e}, falling back to heuristics")

        # Fallback to heuristics
        logger.info("AIMLPlayer.select_action: Falling back to heuristics")
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
        state_dict = state.to_dict()
        features = self.feature_engineer.extract_features(state_dict)

        # Log key state info for debugging
        robot_pos = state_dict["robot"]["position"]
        robot_orient = state_dict["robot"]["orientation"]
        obstacles = state_dict["board"].get("obstacles_positions", [])
        logger.info(f"🤖 ML Prediction - Robot at ({robot_pos['row']},{robot_pos['col']}) facing {robot_orient}")
        logger.info(f"🚧 ML Prediction - Obstacles: {obstacles}")

        # Log action validity features (last 6 features)
        action_validity_start = len(features) - 6
        logger.info(
            f"🎯 ML Prediction - Action Validity: "
            f"can_move={features[action_validity_start]:.1f}, "
            f"can_clean={features[action_validity_start+3]:.1f}, "
            f"should_rotate={features[action_validity_start+5]:.1f}"
        )

        # Predict action label
        label = self.model.predict([features])[0]
        logger.info(f"📊 ML Prediction - Model output label: {label}")

        # Decode action
        action, direction = self.feature_engineer.decode_action(int(label))
        logger.info(f"🔮 ML Prediction - Decoded: action={action}, direction={direction}")

        # CRITICAL: Validate prediction against action validity features
        # Extract action validity flags
        can_move = features[action_validity_start]
        can_pick = features[action_validity_start + 1]
        can_give = features[action_validity_start + 2]
        can_clean = features[action_validity_start + 3]
        # can_drop = features[action_validity_start + 4]
        # should_rotate = features[action_validity_start + 5]

        # Override invalid predictions
        if action == "rotate" and direction == robot_orient:
            # Don't rotate to the same direction we're already facing!
            logger.warning(f"⚠️  Model predicted 'rotate {direction}' but already facing {robot_orient}! Overriding...")
            # Find a different direction
            direction = self._find_best_rotation_direction(state_dict, robot_orient)
            logger.info(f"🔧 Override: Choosing 'rotate' to {direction} instead")

        elif action == "move" and can_move == 0.0:
            logger.warning("⚠️  Model predicted 'move' but can_move=0.0! Overriding...")
            # Prefer clean if obstacle ahead, otherwise rotate to a DIFFERENT direction
            if can_clean == 1.0:
                action = "clean"
                logger.info("🔧 Override: Choosing 'clean' (obstacle ahead)")
            else:
                action = "rotate"
                # Find a different direction to rotate to (not current orientation)
                direction = self._find_best_rotation_direction(state_dict, robot_orient)
                logger.info(f"🔧 Override: Choosing 'rotate' to {direction}")

        elif action == "pick" and can_pick == 0.0:
            logger.warning("⚠️  Model predicted 'pick' but can_pick=0.0! Overriding...")
            if can_move == 1.0:
                action = "move"
                direction = None
                logger.info("🔧 Override: Choosing 'move' instead")
            else:
                action = "rotate"
                direction = self._find_best_rotation_direction(state_dict, robot_orient)
                logger.info(f"🔧 Override: Choosing 'rotate' to {direction}")

        elif action == "give" and can_give == 0.0:
            logger.warning("⚠️  Model predicted 'give' but can_give=0.0! Overriding...")
            if can_move == 1.0:
                action = "move"
                direction = None
                logger.info("🔧 Override: Choosing 'move' toward princess")
            else:
                action = "rotate"
                direction = self._find_best_rotation_direction(state_dict, robot_orient)
                logger.info(f"🔧 Override: Choosing 'rotate' to {direction}")

        elif action == "clean" and can_clean == 0.0:
            logger.warning("⚠️  Model predicted 'clean' but can_clean=0.0! Overriding...")
            if can_move == 1.0:
                action = "move"
                direction = None
                logger.info("🔧 Override: Choosing 'move' (no obstacle)")
            else:
                action = "rotate"
                direction = self._find_best_rotation_direction(state_dict, robot_orient)
                logger.info(f"🔧 Override: Choosing 'rotate' to {direction}")

        logger.info(f"✅ AIMLPlayer._predict_with_ml: Final action={action} and direction={direction}")
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
            state.robot["position"] in self._get_adjacent_positions(state.princess["position"], state)
            and len(state.robot["flowers_collected"]) > 0
        ):
            logger.info(
                f"AIMLPlayer._select_action_heuristic: Giving flowers to princess at {state.princess['position']}"
            )
            return ("give", None)

        # If at flower and not full → pick
        robot_pos = state.robot["position"]
        for flower_pos in state.board["flowers_positions"]:
            if (
                robot_pos["row"] == flower_pos["row"]
                and robot_pos["col"] == flower_pos["col"]
                and len(state.robot["flowers_collected"]) < state.robot["flowers_collection_capacity"]
            ):
                logger.info(f"AIMLPlayer._select_action_heuristic: Picking flower at {robot_pos}")
                return ("pick", None)

        # Check if current orientation is blocked by obstacle
        current_orientation = state.robot.get("orientation", "NORTH").upper()  # Normalize to uppercase
        if self._is_path_blocked(state.robot["position"], current_orientation, state):
            logger.info(
                f"AIMLPlayer._select_action_heuristic: Path blocked in orientation {current_orientation}, rotating"
            )
            # Try to find a clear direction
            for direction in ["NORTH", "SOUTH", "EAST", "WEST"]:
                if not self._is_path_blocked(state.robot["position"], direction, state):
                    return ("rotate", direction)
            # If all directions blocked, try to clean
            return ("clean", None)

        # If holding flowers → move toward princess
        if len(state.robot["flowers_collected"]) > 0:
            direction = self._get_direction_to_target(state.robot["position"], state.princess["position"])
            # Check if path is clear before moving
            if not self._is_path_blocked(state.robot["position"], direction, state):
                return ("move", direction)
            else:
                logger.info(
                    f"AIMLPlayer._select_action_heuristic: Path blocked toward princess, rotating to {direction}"
                )
                return ("rotate", direction)

        # Otherwise → move toward nearest flower
        if state.board["flowers_positions"]:
            nearest_flower = min(
                state.board["flowers_positions"],
                key=lambda f: abs(state.robot["position"]["row"] - f["row"])
                + abs(state.robot["position"]["col"] - f["col"]),
            )
            direction = self._get_direction_to_target(state.robot["position"], nearest_flower)
            # Check if path is clear before moving
            if not self._is_path_blocked(state.robot["position"], direction, state):
                return ("move", direction)
            else:
                logger.info(f"AIMLPlayer._select_action_heuristic: Path blocked toward flower, rotating to {direction}")
                return ("rotate", direction)

        # Default: rotate to find a clear path
        return ("rotate", "NORTH")

    def _find_best_rotation_direction(self, state_dict: dict, current_orientation: str) -> str:
        """
        Find the best direction to rotate to when the current path is blocked.
        Prefers directions that are clear and move toward the goal.

        Args:
            state_dict: Game state dictionary
            current_orientation: Current robot orientation

        Returns:
            Direction string (NORTH, SOUTH, EAST, WEST)
        """
        robot_pos = state_dict["robot"]["position"]
        flowers_positions = state_dict["board"].get("flowers_positions", [])
        obstacles_positions = state_dict["board"].get("obstacles_positions", [])
        princess_pos = state_dict["princess"]["position"]
        board = state_dict["board"]
        has_flowers = len(state_dict["robot"].get("flowers_collected", [])) > 0

        # All possible directions
        all_directions = ["NORTH", "SOUTH", "EAST", "WEST"]

        # Score each direction
        direction_scores = {}
        for direction in all_directions:
            if direction == current_orientation.upper():
                continue  # Don't rotate to the same direction

            score = 0.0

            # Check if path is clear in this direction
            forward_pos = self._get_adjacent_position((robot_pos["row"], robot_pos["col"]), direction)
            cell_type = self._get_cell_type(forward_pos, flowers_positions, obstacles_positions, princess_pos, board)

            # Heavily prefer clear paths
            if cell_type in ["empty", "flower"]:
                score += 10.0

            # If has flowers, prefer directions toward princess
            if has_flowers:
                target = princess_pos
            else:
                # Prefer directions toward nearest flower
                if flowers_positions:
                    nearest_flower = min(
                        flowers_positions,
                        key=lambda f: abs(robot_pos["row"] - f["row"]) + abs(robot_pos["col"] - f["col"]),
                    )
                    target = nearest_flower
                else:
                    target = princess_pos

            # Calculate if this direction moves toward target
            # Weight score by the actual distance in that axis
            dx = target["col"] - robot_pos["col"]
            dy = target["row"] - robot_pos["row"]

            # Score proportional to distance (prioritize the primary direction)
            if direction == "NORTH" and dy < 0:
                score += abs(dy) * 2.0  # Weight by vertical distance
            elif direction == "SOUTH" and dy > 0:
                score += abs(dy) * 2.0
            elif direction == "EAST" and dx > 0:
                score += abs(dx) * 2.0  # Weight by horizontal distance
            elif direction == "WEST" and dx < 0:
                score += abs(dx) * 2.0

            direction_scores[direction] = score

        # Pick the best direction, or fallback to any direction different from current
        if direction_scores:
            best_direction = max(direction_scores, key=direction_scores.get)
            logger.info(f"🧭 Best rotation direction: {best_direction} (score={direction_scores[best_direction]:.1f})")
            return best_direction
        else:
            # Fallback: just pick any direction different from current
            for direction in all_directions:
                if direction != current_orientation.upper():
                    logger.info(f"🧭 Fallback rotation direction: {direction}")
                    return direction
            return "NORTH"  # Ultimate fallback

    @staticmethod
    def _get_adjacent_position(pos: tuple[int, int], direction: str) -> tuple[int, int]:
        """Get position adjacent to current position in given direction."""
        row, col = pos
        direction = direction.upper()
        if direction == "NORTH":
            return (row - 1, col)
        elif direction == "SOUTH":
            return (row + 1, col)
        elif direction == "EAST":
            return (row, col + 1)
        elif direction == "WEST":
            return (row, col - 1)
        return pos

    @staticmethod
    def _get_cell_type(
        pos: tuple[int, int], flowers: list[dict], obstacles: list[dict], princess_pos: dict, board: dict
    ) -> str:
        """Determine what type of cell is at the given position."""
        row, col = pos

        # Check bounds
        if row < 0 or row >= board["rows"] or col < 0 or col >= board["cols"]:
            return "boundary"

        # Check princess
        if princess_pos["row"] == row and princess_pos["col"] == col:
            return "princess"

        # Check obstacles
        for obstacle in obstacles:
            if obstacle["row"] == row and obstacle["col"] == col:
                return "obstacle"

        # Check flowers
        for flower in flowers:
            if flower["row"] == row and flower["col"] == col:
                return "flower"

        return "empty"

    def _is_path_blocked(self, position: dict, direction: str, state: GameState) -> bool:
        """
        Check if the path in the given direction is blocked by an obstacle or boundary.

        Args:
            position: Current position
            direction: Direction to check (case-insensitive)
            state: Game state

        Returns:
            True if path is blocked, False otherwise
        """
        # Calculate target position based on direction
        target_row = position["row"]
        target_col = position["col"]

        direction = direction.upper()  # Normalize to uppercase

        if direction == "NORTH":
            target_row -= 1
        elif direction == "SOUTH":
            target_row += 1
        elif direction == "EAST":
            target_col += 1
        elif direction == "WEST":
            target_col -= 1

        # Check if out of bounds
        if target_row < 0 or target_row >= state.board["rows"] or target_col < 0 or target_col >= state.board["cols"]:
            return True

        # Check if obstacle at target position
        for obstacle in state.board.get("obstacles_positions", []):
            if obstacle["row"] == target_row and obstacle["col"] == target_col:
                return True

        # Check if princess at target position (can't move into princess)
        princess_pos = state.princess["position"]
        if princess_pos["row"] == target_row and princess_pos["col"] == target_col:
            return True

        return False

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

    def _plan_sequence(self, state: GameState, horizon: int | None = None) -> list[tuple[str, str | None]]:
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

        logger.info(f"AIMLPlayer.plan_sequence: Planned sequence={actions}")
        return actions

    def _get_config(self) -> dict:
        """Get current configuration."""
        return self.config.to_dict()

    def _get_model_info(self) -> dict[str, Any]:
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
        adjacent_positions = [
            p
            for p in adjacent_positions
            if p["row"] >= 0 and p["row"] < state.board["rows"] and p["col"] >= 0 and p["col"] < state.board["cols"]
        ]

        # # filter out positions that are obstacles
        # adjacent_positions = [p for p in adjacent_positions if p not in state.board["obstacles_positions"]]

        # # filter out positions that are flowers
        # adjacent_positions = [p for p in adjacent_positions if p not in state.board["flowers_positions"]]

        # # filter out positions that are princess
        # adjacent_positions = [p for p in adjacent_positions if p not in state.princess["position"]]

        # # filter out positions that are robot
        # adjacent_positions = [p for p in adjacent_positions if p not in state.robot["position"]]

        logger.info(f"AIMLPlayer._get_adjacent_positions: Adjacent positions={adjacent_positions}")
        return adjacent_positions
