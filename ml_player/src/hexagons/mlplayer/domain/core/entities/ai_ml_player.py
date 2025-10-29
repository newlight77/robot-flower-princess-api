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

    def evaluate_game(self, state: GameState) -> float:
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
        flowers = state_dict["board"].get("flowers_positions", [])
        logger.info(f"🤖 ML Prediction - Robot at ({robot_pos['row']},{robot_pos['col']}) facing {robot_orient}")
        logger.info(f"🚧 ML Prediction - Obstacles: {obstacles}")
        logger.info(f"🌺 ML Prediction - Flowers: {flowers}")

        # Log action validity features (features 72-77, always at these indices)
        action_validity_start = 72  # Fixed index - action validity always starts at feature 72
        strategic_features_start = 78  # Strategic features start at 78

        # Extract strategic features
        blocked_with_flowers = features[strategic_features_start] if len(features) > strategic_features_start else 0.0

        logger.info(
            f"🎯 ML Prediction - Action Validity: "
            f"can_move={features[action_validity_start]:.1f}, "
            f"can_pick={features[action_validity_start+1]:.1f}, "
            f"can_give={features[action_validity_start+2]:.1f}, "
            f"can_clean={features[action_validity_start+3]:.1f}, "
            f"can_drop={features[action_validity_start+4]:.1f}, "
            f"should_rotate={features[action_validity_start+5]:.1f}, "
            f"blocked_with_flowers={blocked_with_flowers:.1f}"
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
        can_drop = features[action_validity_start + 4]
        # should_rotate = features[action_validity_start + 5]

        # PRIORITY OVERRIDE: Always pick flowers when available (optimal strategy)
        # This overcomes training data imbalance where "pick" is rare (4.6% of samples)
        if can_pick == 1.0:
            logger.info("🌸 PRIORITY: Flower ahead! Overriding to 'pick' (optimal strategy)")
            action = "pick"
            direction = None
            return action, direction

        # PRIORITY OVERRIDE: Always give flowers when at princess and able to give
        # Ensures delivery is not missed due to model bias
        if can_give == 1.0:
            logger.info("👑 PRIORITY: At princess with flowers! Overriding to 'give'")
            action = "give"
            direction = None
            return action, direction

        # PRIORITY OVERRIDE: If blocked by obstacle while carrying flowers and can drop, prioritize drop
        # This allows the robot to clear the way for cleaning the obstacle
        if blocked_with_flowers == 1.0 and can_drop == 1.0:
            logger.info("📦 PRIORITY: Blocked by obstacle while carrying flowers! Overriding to 'drop' to clear path")
            action = "drop"
            direction = None
            return action, direction

        # PRIORITY OVERRIDE: If carrying flowers and can drop, check if we need to drop to clear path
        # This is critical when blocked by obstacles - we need to drop before cleaning
        has_flowers = len(state_dict["robot"].get("flowers_collected", [])) > 0
        if has_flowers and can_drop == 1.0:
            obstacles_positions = state_dict["board"].get("obstacles_positions", [])
            robot_pos = state_dict["robot"]["position"]

            # Check all 4 directions for nearby obstacles (adjacent cells)
            has_nearby_obstacle = False
            nearby_obstacle_dirs = []
            for check_dir in ["NORTH", "SOUTH", "EAST", "WEST"]:
                adj_pos = self._get_adjacent_position((robot_pos["row"], robot_pos["col"]), check_dir)
                for obstacle in obstacles_positions:
                    if obstacle["row"] == adj_pos[0] and obstacle["col"] == adj_pos[1]:
                        has_nearby_obstacle = True
                        nearby_obstacle_dirs.append(check_dir)
                        break

            # Check if robot cannot move in current direction (blocked)
            cannot_move_current_dir = can_move == 0.0

            # If we have nearby obstacle OR are blocked in current direction, prioritize dropping
            # (This handles both cases: directly facing obstacle, and just rotated to find drop location)
            if has_nearby_obstacle or cannot_move_current_dir:
                logger.info(
                    f"📦 PRIORITY: Carrying flowers ({len(state_dict['robot'].get('flowers_collected', []))} flowers), "
                    f"can_drop={can_drop:.1f}, nearby_obstacles={nearby_obstacle_dirs}, "
                    f"can_move={can_move:.1f}! Overriding to 'drop' to enable obstacle cleaning"
                )
                action = "drop"
                direction = None
                return action, direction

        # PRIORITY OVERRIDE: If we can move toward target, prefer moving over rotating
        # Prevents unnecessary rotation when already facing the right direction
        if action == "rotate" and can_move == 1.0:
            robot_pos = state_dict["robot"]["position"]
            has_flowers = len(state_dict["robot"].get("flowers_collected", [])) > 0

            # Determine target
            if has_flowers:
                target = state_dict["princess"]["position"]
            else:
                flowers_positions = state_dict["board"].get("flowers_positions", [])
                if flowers_positions:
                    target = min(
                        flowers_positions,
                        key=lambda f: abs(robot_pos["row"] - f["row"]) + abs(robot_pos["col"] - f["col"]),
                    )
                else:
                    target = state_dict["princess"]["position"]

            # Check if current orientation moves toward target
            dx = target["col"] - robot_pos["col"]
            dy = target["row"] - robot_pos["row"]

            current_moves_toward_target = False
            if robot_orient == "NORTH" and dy < 0:  # Moving NORTH toward target
                current_moves_toward_target = True
            elif robot_orient == "SOUTH" and dy > 0:  # Moving SOUTH toward target
                current_moves_toward_target = True
            elif robot_orient == "EAST" and dx > 0:  # Moving EAST toward target
                current_moves_toward_target = True
            elif robot_orient == "WEST" and dx < 0:  # Moving WEST toward target
                current_moves_toward_target = True

            # If already facing toward target and can move, prioritize moving!
            if current_moves_toward_target:
                logger.info(
                    f"🚀 PRIORITY: Already facing {robot_orient} toward target (dx={dx}, dy={dy})! "
                    f"Overriding 'rotate' to 'move' (can_move={can_move:.1f})"
                )
                action = "move"
                direction = None
                return action, direction

        # Override invalid predictions
        if action == "rotate":
            # PRIORITY: If blocked by obstacle while carrying flowers, use heuristic to find drop location
            if blocked_with_flowers == 1.0:
                logger.warning(
                    "🚫 PRIORITY: Blocked by obstacle while carrying flowers! "
                    "Must drop flowers first. Using heuristic to find empty cell..."
                )
                # Use heuristic to find best direction (should prefer directions with empty cells)
                # Pass seeking_drop_location=True to prioritize empty cells for dropping
                direction = self._find_best_rotation_direction(state_dict, robot_orient, seeking_drop_location=True)
                logger.info(f"🔧 Override: Choosing 'rotate' to {direction} to find drop location")
                # Continue with rotation - don't return yet, let normal flow handle it
            # If path is blocked and obstacle can be cleaned, prefer cleaning over rotating
            elif can_move == 0.0 and can_clean == 1.0:
                logger.info("🧹 PRIORITY: Obstacle ahead and cannot move. Overriding 'rotate' to 'clean'")
                action = "clean"
                direction = None
                return action, direction

            # Check if direction is valid
            if direction == robot_orient:
                # Don't rotate to the same direction we're already facing!
                logger.warning(f"⚠️  Model predicted 'rotate {direction}' but already facing {robot_orient}! Overriding...")
                # Find a different direction (check if we're seeking drop location)
                drop_seeking = blocked_with_flowers == 1.0
                direction = self._find_best_rotation_direction(state_dict, robot_orient, seeking_drop_location=drop_seeking)
                logger.info(f"🔧 Override: Choosing 'rotate' to {direction} instead")
            else:
                # Check if this rotation is optimal toward target
                robot_pos = state_dict["robot"]["position"]
                has_flowers = len(state_dict["robot"].get("flowers_collected", [])) > 0

                # Determine target
                if has_flowers:
                    target = state_dict["princess"]["position"]
                else:
                    flowers_positions = state_dict["board"].get("flowers_positions", [])
                    if flowers_positions:
                        target = min(
                            flowers_positions,
                            key=lambda f: abs(robot_pos["row"] - f["row"]) + abs(robot_pos["col"] - f["col"]),
                        )
                    else:
                        target = state_dict["princess"]["position"]

                # Calculate required movement
                dx = target["col"] - robot_pos["col"]
                dy = target["row"] - robot_pos["row"]

                # Check if predicted direction moves AWAY from target (bad rotation)
                moves_away = False
                if direction == "NORTH" and dy > 0:  # Target is SOUTH, but rotating NORTH
                    moves_away = True
                elif direction == "SOUTH" and dy < 0:  # Target is NORTH, but rotating SOUTH
                    moves_away = True
                elif direction == "EAST" and dx < 0:  # Target is WEST, but rotating EAST
                    moves_away = True
                elif direction == "WEST" and dx > 0:  # Target is EAST, but rotating WEST
                    moves_away = True

                # Also check if we're perpendicular when we need primary movement in one axis
                # (e.g., need SOUTH primarily (dy=2) but rotating EAST/WEST)
                perpendicular_when_direct_needed = False
                abs_dx = abs(dx)
                abs_dy = abs(dy)

                # If primary movement is vertical (dy >> dx) and rotating horizontal, it's suboptimal
                if abs_dy > abs_dx * 1.5 and direction in ["EAST", "WEST"]:
                    perpendicular_when_direct_needed = True
                # If primary movement is horizontal (dx >> dy) and rotating vertical, it's suboptimal
                elif abs_dx > abs_dy * 1.5 and direction in ["NORTH", "SOUTH"]:
                    perpendicular_when_direct_needed = True
                # Exact alignment cases (dx=0 or dy=0)
                elif dx == 0 and direction in ["EAST", "WEST"]:  # Need vertical movement but rotating horizontal
                    perpendicular_when_direct_needed = True
                elif dy == 0 and direction in ["NORTH", "SOUTH"]:  # Need horizontal movement but rotating vertical
                    perpendicular_when_direct_needed = True

                if moves_away or perpendicular_when_direct_needed:
                    logger.warning(
                        f"⚠️  Model predicted 'rotate {direction}' but target requires different direction "
                        f"(dx={dx}, dy={dy})! Overriding with heuristic..."
                    )
                    drop_seeking = blocked_with_flowers == 1.0
                    direction = self._find_best_rotation_direction(state_dict, robot_orient, seeking_drop_location=drop_seeking)
                    logger.info(f"🔧 Override: Using heuristic rotation to {direction}")

        elif action == "move" and can_move == 0.0:
            logger.warning("⚠️  Model predicted 'move' but can_move=0.0! Overriding...")
            # Prefer clean if obstacle ahead, otherwise rotate to a DIFFERENT direction
            if can_clean == 1.0:
                action = "clean"
                logger.info("🔧 Override: Choosing 'clean' (obstacle ahead)")
            else:
                action = "rotate"
                # Find a different direction to rotate to (not current orientation)
                drop_seeking = blocked_with_flowers == 1.0
                direction = self._find_best_rotation_direction(state_dict, robot_orient, seeking_drop_location=drop_seeking)
                logger.info(f"🔧 Override: Choosing 'rotate' to {direction}")

        elif action == "pick" and can_pick == 0.0:
            logger.warning("⚠️  Model predicted 'pick' but can_pick=0.0! Overriding...")
            if can_move == 1.0:
                action = "move"
                direction = None
                logger.info("🔧 Override: Choosing 'move' instead")
            else:
                action = "rotate"
                drop_seeking = blocked_with_flowers == 1.0
                direction = self._find_best_rotation_direction(state_dict, robot_orient, seeking_drop_location=drop_seeking)
                logger.info(f"🔧 Override: Choosing 'rotate' to {direction}")

        elif action == "drop" and can_drop == 0.0:
            logger.warning("⚠️  Model predicted 'drop' but can_drop=0.0! Overriding...")
            if can_move == 1.0:
                action = "move"
                direction = None
                logger.info("🔧 Override: Choosing 'move' (no flowers to drop)")
            else:
                action = "rotate"
                drop_seeking = blocked_with_flowers == 1.0
                direction = self._find_best_rotation_direction(state_dict, robot_orient, seeking_drop_location=drop_seeking)
                logger.info(f"🔧 Override: Choosing 'rotate' to {direction}")

        elif action == "give" and can_give == 0.0:
            logger.warning("⚠️  Model predicted 'give' but can_give=0.0! Overriding...")
            if can_move == 1.0:
                action = "move"
                direction = None
                logger.info("🔧 Override: Choosing 'move' toward princess")
            else:
                action = "rotate"
                drop_seeking = blocked_with_flowers == 1.0
                direction = self._find_best_rotation_direction(state_dict, robot_orient, seeking_drop_location=drop_seeking)
                logger.info(f"🔧 Override: Choosing 'rotate' to {direction}")

        elif action == "clean" and can_clean == 0.0:
            logger.warning("⚠️  Model predicted 'clean' but can_clean=0.0! Overriding...")
            if can_move == 1.0:
                action = "move"
                direction = None
                logger.info("🔧 Override: Choosing 'move' (no obstacle)")
            elif can_drop == 1.0:
                action = "drop"
                direction = None
                logger.info("🔧 Override: Choosing 'drop' (no obstacle)")
            else:
                action = "rotate"
                direction = self._find_best_rotation_direction(state_dict, robot_orient)
                logger.info(f"🔧 Override: Choosing 'rotate' to {direction} (no obstacle)")

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

    def _find_best_rotation_direction(self, state_dict: dict, current_orientation: str, seeking_drop_location: bool = False) -> str:
        """
        Find the best direction to rotate to when the current path is blocked.
        Uses advanced heuristics: path lookahead, distance weighting, obstacle avoidance.

        Args:
            state_dict: Game state dictionary
            current_orientation: Current robot orientation
            seeking_drop_location: If True, prioritize directions with empty cells (for dropping flowers)

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

            # === IMMEDIATE CELL SCORING ===
            forward_pos = self._get_adjacent_position((robot_pos["row"], robot_pos["col"]), direction)
            cell_type = self._get_cell_type(forward_pos, flowers_positions, obstacles_positions, princess_pos, board)

            # SPECIAL MODE: Seeking drop location (blocked with flowers, need to drop)
            if seeking_drop_location:
                # Prioritize empty cells above all else (except boundaries/obstacles)
                if cell_type == "empty":
                    score += 300.0  # MASSIVE bonus for empty cell when seeking drop location!
                    logger.info(f"📦 [DROP MODE] Direction {direction} has EMPTY CELL ahead! Bonus +300")
                elif cell_type == "flower":
                    score += 50.0  # Lower priority than empty cells when dropping
                    logger.info(f"🌸 [DROP MODE] Direction {direction} has FLOWER ahead! Bonus +50")
                elif cell_type == "princess":
                    score += 50.0  # Can't drop on princess anyway
                    logger.info(f"👑 [DROP MODE] Direction {direction} has PRINCESS ahead! Bonus +50")
                elif cell_type == "obstacle":
                    score -= 100.0  # Heavy penalty - obstacles block dropping
                    logger.info(f"🚧 [DROP MODE] Direction {direction} has OBSTACLE ahead! Penalty -100")
                elif cell_type == "boundary":
                    score -= 200.0  # Very bad: edge of map
                    logger.info(f"🚫 [DROP MODE] Direction {direction} is BOUNDARY! Penalty -200")
            else:
                # NORMAL MODE: Standard scoring
                # HIGHEST PRIORITY: Flower directly ahead
                if cell_type == "flower":
                    score += 200.0  # MASSIVE bonus for flower directly ahead!
                    logger.info(f"🌸 Direction {direction} has FLOWER ahead! Bonus +200")
                elif cell_type == "empty":
                    score += 20.0  # Good: clear path (increased from 15.0 to break ties)
                elif cell_type == "obstacle":
                    score -= 40.0  # Bad: obstacle blocking (increased penalty)
                elif cell_type == "princess" and has_flowers:
                    score += 150.0  # Excellent: can deliver flowers!
                elif cell_type == "boundary":
                    score -= 50.0  # Very bad: edge of map

            # === PATH LOOKAHEAD (check 2-3 cells ahead) ===
            lookahead_bonus = 0.0
            current_pos = forward_pos
            for depth in range(1, 4):  # Look 1-3 cells ahead
                current_pos = self._get_adjacent_position(current_pos, direction)
                lookahead_cell = self._get_cell_type(current_pos, flowers_positions, obstacles_positions, princess_pos, board)

                if seeking_drop_location:
                    # When seeking drop location, prioritize empty cells in lookahead
                    if lookahead_cell == "empty":
                        lookahead_bonus += 100.0 / depth  # Massive bonus for empty cells when dropping
                    elif lookahead_cell == "flower":
                        lookahead_bonus += 20.0 / depth  # Lower priority
                    elif lookahead_cell == "obstacle":
                        lookahead_bonus -= 30.0 / depth  # Heavy penalty for obstacles
                    elif lookahead_cell == "boundary":
                        break  # Stop lookahead at boundary
                else:
                    # Normal mode: standard lookahead scoring
                    if lookahead_cell == "flower":
                        lookahead_bonus += 50.0 / depth  # Closer flowers = higher bonus
                    elif lookahead_cell == "empty":
                        lookahead_bonus += 3.0 / depth  # Clear path ahead
                    elif lookahead_cell == "obstacle":
                        lookahead_bonus -= 10.0 / depth  # Obstacles ahead are bad
                    elif lookahead_cell == "boundary":
                        break  # Stop lookahead at boundary

            score += lookahead_bonus

            # === DISTANCE-WEIGHTED TARGETING ===
            # When seeking drop location, prioritize empty cells over target distance
            # (we need to drop flowers before we can move toward targets anyway)
            if not seeking_drop_location:
                # Choose target based on game state
                if has_flowers:
                    target = princess_pos
                    target_weight = 5.0  # High priority when delivering
                else:
                    # Find nearest flower (Manhattan distance)
                    if flowers_positions:
                        nearest_flower = min(
                            flowers_positions,
                            key=lambda f: abs(robot_pos["row"] - f["row"]) + abs(robot_pos["col"] - f["col"]),
                        )
                        target = nearest_flower
                        target_weight = 8.0  # Very high priority when collecting (increased from 4.0)
                    else:
                        target = princess_pos
                        target_weight = 2.0

                # Calculate Manhattan distance to target
                dx = target["col"] - robot_pos["col"]
                dy = target["row"] - robot_pos["row"]

                # Reward directions that reduce distance to target
                # CRITICAL: When both dx and dy are non-zero, we need BOTH directions!
                # Give bonus to the direction that matches the axis, regardless of magnitude
                if direction == "NORTH" and dy < 0:
                    bonus = max(abs(dy), abs(dx)) * target_weight
                    # SPECIAL CASE: If target is directly in this direction (dx=0 or dy is the only movement needed)
                    if dx == 0:  # Target is directly NORTH/SOUTH
                        bonus *= 2.0  # Double bonus for direct line!
                    score += bonus
                    logger.info(f"🎯 Direction {direction} moves toward target (dy={dy}, dx={dx}) bonus={bonus:.1f}")
                elif direction == "SOUTH" and dy > 0:
                    bonus = max(abs(dy), abs(dx)) * target_weight
                    if dx == 0:  # Target is directly SOUTH/NORTH
                        bonus *= 2.0  # Double bonus for direct line!
                    score += bonus
                    logger.info(f"🎯 Direction {direction} moves toward target (dy={dy}, dx={dx}) bonus={bonus:.1f}")
                elif direction == "EAST" and dx > 0:
                    bonus = max(abs(dx), abs(dy)) * target_weight
                    if dy == 0:  # Target is directly EAST/WEST
                        bonus *= 2.0  # Double bonus for direct line!
                    score += bonus
                    logger.info(f"🎯 Direction {direction} moves toward target (dx={dx}, dy={dy}) bonus={bonus:.1f}")
                elif direction == "WEST" and dx < 0:
                    bonus = max(abs(dx), abs(dy)) * target_weight
                    if dy == 0:  # Target is directly EAST/WEST
                        bonus *= 2.0  # Double bonus for direct line!
                    score += bonus
                    logger.info(f"🎯 Direction {direction} moves toward target (dx={dx}, dy={dy}) bonus={bonus:.1f}")

                # ANTI-LOOP: If moving in this direction would take us AWAY from target, penalize heavily
                if direction == "NORTH" and dy > 0:  # Going NORTH when target is SOUTH
                    score -= 50.0
                    logger.info(f"🔄 Direction {direction} moves AWAY from target! Penalty -50")
                elif direction == "SOUTH" and dy < 0:  # Going SOUTH when target is NORTH
                    score -= 50.0
                    logger.info(f"🔄 Direction {direction} moves AWAY from target! Penalty -50")
                elif direction == "EAST" and dx < 0:  # Going EAST when target is WEST
                    score -= 50.0
                    logger.info(f"🔄 Direction {direction} moves AWAY from target! Penalty -50")
                elif direction == "WEST" and dx > 0:  # Going WEST when target is EAST
                    score -= 50.0
                    logger.info(f"🔄 Direction {direction} moves AWAY from target! Penalty -50")
            else:
                # DROP MODE: Lower priority for target distance (empty cells are more important)
                # Still give some bonus for moving toward princess (eventual goal after dropping)
                if has_flowers:
                    target = princess_pos
                    target_weight = 1.0  # Lower weight in drop mode
                else:
                    # When not carrying flowers, we shouldn't be in drop mode, but handle gracefully
                    target_weight = 0.5

                dx = target["col"] - robot_pos["col"]
                dy = target["row"] - robot_pos["row"]

                # Give smaller bonuses when seeking drop location
                if direction == "NORTH" and dy < 0:
                    score += max(abs(dy), abs(dx)) * target_weight * 0.5  # Reduced bonus
                elif direction == "SOUTH" and dy > 0:
                    score += max(abs(dy), abs(dx)) * target_weight * 0.5
                elif direction == "EAST" and dx > 0:
                    score += max(abs(dx), abs(dy)) * target_weight * 0.5
                elif direction == "WEST" and dx < 0:
                    score += max(abs(dx), abs(dy)) * target_weight * 0.5

            # === NEARBY FLOWER BONUS ===
            # Give bonus for directions that have flowers within 2-3 cells
            # (Lower priority when seeking drop location)
            if not seeking_drop_location:
                nearby_flower_bonus = 0.0
                for flower in flowers_positions:
                    flower_dx = flower["col"] - robot_pos["col"]
                    flower_dy = flower["row"] - robot_pos["row"]
                    flower_dist = abs(flower_dx) + abs(flower_dy)

                    # Check if this direction leads toward this flower
                    moves_toward_flower = False
                    if direction == "NORTH" and flower_dy < 0:
                        moves_toward_flower = True
                    elif direction == "SOUTH" and flower_dy > 0:
                        moves_toward_flower = True
                    elif direction == "EAST" and flower_dx > 0:
                        moves_toward_flower = True
                    elif direction == "WEST" and flower_dx < 0:
                        moves_toward_flower = True

                    if moves_toward_flower and flower_dist <= 5:
                        nearby_flower_bonus += 15.0 / max(flower_dist, 1)

                score += nearby_flower_bonus

            direction_scores[direction] = score

        # Pick the best direction
        if direction_scores:
            best_direction = max(direction_scores, key=direction_scores.get)
            best_score = direction_scores[best_direction]
            logger.info(f"🧭 Best rotation: {best_direction} (score={best_score:.1f})")

            # Log all scores for debugging
            sorted_scores = sorted(direction_scores.items(), key=lambda x: x[1], reverse=True)
            logger.info(f"📊 Direction scores: {', '.join([f'{d}={s:.1f}' for d, s in sorted_scores])}")

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
        """
        Determine what type of cell is at the given position.

        Returns: "flower", "obstacle", "princess", "empty", or "boundary"
        """
        row, col = pos

        # Check bounds first (most common case for lookahead)
        if row < 0 or row >= board["rows"] or col < 0 or col >= board["cols"]:
            return "boundary"

        # Check flowers first (highest priority for navigation)
        for flower in flowers:
            if flower["row"] == row and flower["col"] == col:
                return "flower"

        # Check obstacles
        for obstacle in obstacles:
            if obstacle["row"] == row and obstacle["col"] == col:
                return "obstacle"

        # Check princess
        if princess_pos["row"] == row and princess_pos["col"] == col:
            return "princess"

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

        logger.info(f"AIMLPlayer.plan_sequence: Planned sequence={actions}")
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
