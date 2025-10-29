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
        Predict action using trained ML model with priority-based decision tree.

        Simplified approach following greedy player structure:
        1. Priority checks (pick, give, drop when blocked)
        2. ML prediction
        3. Validate and fix invalid predictions
        4. Simplify rotation using pathfinding hints

        Args:
            state: Current game state

        Returns:
            Tuple of (action, direction)
        """
        # Extract features and state info
        state_dict = state.to_dict()
        features = self.feature_engineer.extract_features(state_dict)
        robot_pos = state_dict["robot"]["position"]
        robot_orient = state_dict["robot"]["orientation"]
        has_flowers = len(state_dict["robot"].get("flowers_collected", [])) > 0

        # Extract action validity flags (fixed indices)
        action_validity_start = 72
        strategic_features_start = 78
        can_move = features[action_validity_start]
        can_pick = features[action_validity_start + 1]
        can_give = features[action_validity_start + 2]
        can_clean = features[action_validity_start + 3]
        can_drop = features[action_validity_start + 4]
        blocked_with_flowers = features[strategic_features_start] if len(features) > strategic_features_start else 0.0

        logger.info(
            f"🤖 State: pos=({robot_pos['row']},{robot_pos['col']}) facing={robot_orient}, "
            f"flowers={has_flowers}, can_move={can_move:.1f}, can_pick={can_pick:.1f}, "
            f"can_give={can_give:.1f}, can_clean={can_clean:.1f}, can_drop={can_drop:.1f}, "
            f"blocked_with_flowers={blocked_with_flowers:.1f}"
        )

        # ============================================================
        # PRIORITY-BASED DECISION TREE (similar to greedy player)
        # ============================================================

        # Priority 1: PICK - Always pick when flower is directly ahead
        if can_pick == 1.0:
            logger.info("🌸 PRIORITY: Flower ahead! → PICK")
            return ("pick", None)

        # Priority 2: GIVE - Always give when at princess with flowers
        if can_give == 1.0:
            logger.info("👑 PRIORITY: At princess with flowers! → GIVE")
            return ("give", None)

        # Priority 3: DROP - When blocked by obstacle while carrying flowers
        # (Need to drop before cleaning obstacle)
        if blocked_with_flowers == 1.0 and can_drop == 1.0:
            logger.info("📦 PRIORITY: Blocked with flowers! → DROP")
            return ("drop", None)

        # Priority 3b: DROP - Carrying flowers, can drop, and nearby obstacle blocking path
        if has_flowers and can_drop == 1.0:
            if self._has_nearby_obstacle(robot_pos, state_dict) or can_move == 0.0:
                logger.info("📦 PRIORITY: Carrying flowers, nearby obstacle → DROP")
                return ("drop", None)

        # Priority 4: CLEAN - Blocked by obstacle and can clean
        if can_move == 0.0 and can_clean == 1.0:
            logger.info("🧹 PRIORITY: Obstacle ahead, can clean → CLEAN")
            return ("clean", None)

        # Priority 5: MOVE - Already facing target and can move
        if self._is_facing_target(robot_pos, robot_orient, has_flowers, state_dict) and can_move == 1.0:
            logger.info(f"🚀 PRIORITY: Facing target, can move → MOVE")
            return ("move", None)

        # ============================================================
        # ML PREDICTION (for navigation decisions)
        # ============================================================

        # Predict action label from ML model
        label = self.model.predict([features])[0]
        action, direction = self.feature_engineer.decode_action(int(label))
        logger.info(f"📊 ML Prediction: {action} {direction or ''}")

        # ============================================================
        # VALIDATE AND FIX INVALID PREDICTIONS
        # ============================================================

        # Fix invalid predictions by mapping to valid actions
        if action == "pick" and can_pick == 0.0:
            action, direction = self._fix_invalid_action("pick", can_move, can_clean, blocked_with_flowers, robot_orient, state_dict)
        elif action == "give" and can_give == 0.0:
            action, direction = self._fix_invalid_action("give", can_move, can_clean, blocked_with_flowers, robot_orient, state_dict)
        elif action == "drop" and can_drop == 0.0:
            action, direction = self._fix_invalid_action("drop", can_move, can_clean, blocked_with_flowers, robot_orient, state_dict)
        elif action == "clean" and can_clean == 0.0:
            action, direction = self._fix_invalid_action("clean", can_move, can_clean, blocked_with_flowers, robot_orient, state_dict)
        elif action == "move" and can_move == 0.0:
            if can_clean == 1.0:
                action, direction = "clean", None
            else:
                action, direction = self._get_rotation_toward_target(robot_pos, robot_orient, has_flowers, state_dict, blocked_with_flowers)
        elif action == "rotate":
            # Fix rotation: don't rotate to same direction, use better direction if needed
            if direction == robot_orient:
                action, direction = self._get_rotation_toward_target(robot_pos, robot_orient, has_flowers, state_dict, blocked_with_flowers)
            elif self._is_rotation_suboptimal(direction, robot_pos, has_flowers, state_dict):
                action, direction = self._get_rotation_toward_target(robot_pos, robot_orient, has_flowers, state_dict, blocked_with_flowers)

        logger.info(f"✅ Final action: {action} {direction or ''}")
        return (action, direction)

    def _has_nearby_obstacle(self, robot_pos: dict, state_dict: dict) -> bool:
        """Check if there's an obstacle in any adjacent direction."""
        obstacles_positions = state_dict["board"].get("obstacles_positions", [])
        for check_dir in ["NORTH", "SOUTH", "EAST", "WEST"]:
            adj_pos = self._get_adjacent_position((robot_pos["row"], robot_pos["col"]), check_dir)
            for obstacle in obstacles_positions:
                if obstacle["row"] == adj_pos[0] and obstacle["col"] == adj_pos[1]:
                    return True
        return False

    def _is_facing_target(self, robot_pos: dict, robot_orient: str, has_flowers: bool, state_dict: dict) -> bool:
        """Check if current orientation moves toward the target."""
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

        dx = target["col"] - robot_pos["col"]
        dy = target["row"] - robot_pos["row"]

        if robot_orient == "NORTH" and dy < 0:
            return True
        elif robot_orient == "SOUTH" and dy > 0:
            return True
        elif robot_orient == "EAST" and dx > 0:
            return True
        elif robot_orient == "WEST" and dx < 0:
            return True
        return False

    def _fix_invalid_action(
        self, invalid_action: str, can_move: float, can_clean: float,
        blocked_with_flowers: float, robot_orient: str, state_dict: dict
    ) -> tuple[str, str | None]:
        """Fix invalid action prediction by mapping to valid alternative."""
        if invalid_action == "pick":
            if can_move == 1.0:
                return ("move", None)
        elif invalid_action == "give":
            if can_move == 1.0:
                return ("move", None)
        elif invalid_action == "drop":
            if can_move == 1.0:
                return ("move", None)
        elif invalid_action == "clean":
            if can_move == 1.0:
                return ("move", None)
            elif blocked_with_flowers == 1.0:
                return ("drop", None)

        # Default: rotate toward target
        robot_pos = state_dict["robot"]["position"]
        has_flowers = len(state_dict["robot"].get("flowers_collected", [])) > 0
        return self._get_rotation_toward_target(robot_pos, robot_orient, has_flowers, state_dict, blocked_with_flowers)

    def _get_rotation_toward_target(
        self, robot_pos: dict, robot_orient: str, has_flowers: bool,
        state_dict: dict, blocked_with_flowers: float
    ) -> tuple[str, str | None]:
        """Get rotation direction toward target, using simplified heuristic."""
        seeking_drop_location = blocked_with_flowers == 1.0
        direction = self._find_best_rotation_direction(state_dict, robot_orient, seeking_drop_location=seeking_drop_location)
        return ("rotate", direction)

    def _is_rotation_suboptimal(self, direction: str, robot_pos: dict, has_flowers: bool, state_dict: dict) -> bool:
        """Check if rotation moves away from target or is suboptimal."""
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

        dx = target["col"] - robot_pos["col"]
        dy = target["row"] - robot_pos["row"]

        # Check if rotation moves away from target
        if direction == "NORTH" and dy > 0:
            return True
        elif direction == "SOUTH" and dy < 0:
            return True
        elif direction == "EAST" and dx < 0:
            return True
        elif direction == "WEST" and dx > 0:
            return True

        # Check if perpendicular when direct movement needed
        abs_dx, abs_dy = abs(dx), abs(dy)
        if abs_dy > abs_dx * 1.5 and direction in ["EAST", "WEST"]:
            return True
        elif abs_dx > abs_dy * 1.5 and direction in ["NORTH", "SOUTH"]:
            return True
        elif dx == 0 and direction in ["EAST", "WEST"]:
            return True
        elif dy == 0 and direction in ["NORTH", "SOUTH"]:
            return True

        return False

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
