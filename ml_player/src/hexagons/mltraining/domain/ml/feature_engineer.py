"""
Enhanced Feature Engineering for ML Models.

This is a proposed implementation with ~72 features that capture:
- Directional awareness (what's in each direction)
- Task context (collection vs delivery phase)
- Path quality (obstacles blocking paths)
- Multi-flower strategy (nearest-first logic)

To use: Replace src/hexagons/mlplayer/domain/ml/feature_engineer.py
"""

from typing import Any
import numpy as np
from collections import defaultdict


class FeatureEngineer:
    """Enhanced feature extraction with spatial and strategic awareness."""

    @staticmethod
    def extract_features(game_state: dict[str, Any]) -> np.ndarray:
        """
        Extract enhanced feature vector from game state.

        Total features: ~72
        - Basic info: 12 features
        - Directional awareness: 32 features (8 per direction × 4 directions)
        - Task context: 10 features
        - Path quality: 8 features
        - Multi-flower strategy: 6 features
        - Orientation: 4 features (one-hot)

        Args:
            game_state: Raw game state dictionary

        Returns:
            NumPy array of 72 features
        """
        board = game_state["board"]
        robot = game_state["robot"]
        princess = game_state["princess"]

        features = []

        # ============================================================
        # BASIC INFO (12 features)
        # ============================================================
        features.append(float(board["rows"]))
        features.append(float(board["cols"]))
        features.append(float(robot["position"]["row"]))
        features.append(float(robot["position"]["col"]))
        features.append(float(len(robot["flowers_collected"])))
        features.append(float(len(robot["flowers_delivered"])))
        features.append(float(robot["flowers_collection_capacity"]))
        features.append(float(len(robot["obstacles_cleaned"])))
        features.append(float(princess["position"]["row"]))
        features.append(float(princess["position"]["col"]))

        flowers_positions = board.get("flowers_positions", [])
        obstacles_positions = board.get("obstacles_positions", [])
        features.append(float(len(flowers_positions)))
        features.append(float(len(obstacles_positions)))

        # ============================================================
        # DIRECTIONAL AWARENESS (32 features = 8 per direction × 4)
        # ============================================================
        robot_pos = (robot["position"]["row"], robot["position"]["col"])
        directions = ["NORTH", "SOUTH", "EAST", "WEST"]

        for direction in directions:
            # 1. Adjacent cell type (5 features - one-hot)
            adjacent_pos = FeatureEngineer._get_adjacent_position(robot_pos, direction)
            cell_type = FeatureEngineer._get_cell_type(
                adjacent_pos, flowers_positions, obstacles_positions,
                princess["position"], board
            )
            features.extend(FeatureEngineer._one_hot_cell_type(cell_type))

            # 2. Distance to nearest flower in this direction (1 feature)
            features.append(
                FeatureEngineer._nearest_in_direction(
                    robot_pos, direction, flowers_positions
                )
            )

            # 3. Distance to nearest obstacle in this direction (1 feature)
            features.append(
                FeatureEngineer._nearest_in_direction(
                    robot_pos, direction, obstacles_positions
                )
            )

            # 4. Is this direction towards nearest flower? (1 feature)
            if flowers_positions:
                nearest_flower = FeatureEngineer._find_nearest(
                    robot_pos, flowers_positions
                )
                features.append(
                    1.0 if FeatureEngineer._is_direction_towards(
                        robot_pos, direction, nearest_flower
                    ) else 0.0
                )
            else:
                features.append(0.0)

        # ============================================================
        # TASK CONTEXT (10 features)
        # ============================================================
        has_uncollected_flowers = len(flowers_positions) > 0
        has_collected_flowers = len(robot["flowers_collected"]) > 0
        all_flowers_picked = len(flowers_positions) == 0 and has_collected_flowers
        at_capacity = len(robot["flowers_collected"]) >= robot["flowers_collection_capacity"]

        # Game phase indicators
        features.append(1.0 if has_uncollected_flowers else 0.0)  # Collection phase
        features.append(1.0 if all_flowers_picked else 0.0)  # Delivery phase
        features.append(1.0 if at_capacity else 0.0)  # At capacity

        # Progress metric
        total_flowers = board.get("initial_flowers_count", len(flowers_positions))
        if total_flowers > 0:
            features.append(len(robot["flowers_delivered"]) / total_flowers)
        else:
            features.append(1.0)

        # Task priorities
        princess_pos = (princess["position"]["row"], princess["position"]["col"])

        if flowers_positions:
            nearest_flower = FeatureEngineer._find_nearest(robot_pos, flowers_positions)
            features.append(
                FeatureEngineer._manhattan_distance(robot_pos, nearest_flower)
            )
        else:
            features.append(0.0)

        features.append(
            FeatureEngineer._manhattan_distance(robot_pos, princess_pos)
        )

        # Obstacles blocking path to nearest target
        if flowers_positions:
            nearest_flower = FeatureEngineer._find_nearest(robot_pos, flowers_positions)
            features.append(
                float(FeatureEngineer._obstacles_in_line(
                    robot_pos, nearest_flower, obstacles_positions
                ))
            )
        else:
            features.append(
                float(FeatureEngineer._obstacles_in_line(
                    robot_pos, princess_pos, obstacles_positions
                ))
            )

        # Capacity utilization
        if robot["flowers_collection_capacity"] > 0:
            features.append(
                len(robot["flowers_collected"]) / robot["flowers_collection_capacity"]
            )
        else:
            features.append(0.0)

        features.append(1.0 if len(robot["flowers_collected"]) < robot["flowers_collection_capacity"] else 0.0)
        features.append(1.0 if all_flowers_picked and has_collected_flowers else 0.0)

        # ============================================================
        # PATH QUALITY (8 features)
        # ============================================================
        # To nearest flower (if any)
        if flowers_positions:
            nearest_flower = FeatureEngineer._find_nearest(robot_pos, flowers_positions)
            manhattan = FeatureEngineer._manhattan_distance(robot_pos, nearest_flower)
            obstacles_count = FeatureEngineer._obstacles_in_line(
                robot_pos, nearest_flower, obstacles_positions
            )
            features.append(manhattan)
            features.append(float(obstacles_count))
            features.append(manhattan + obstacles_count * 2.0)  # Estimated path length
        else:
            features.extend([0.0, 0.0, 0.0])

        # To princess
        manhattan_princess = FeatureEngineer._manhattan_distance(robot_pos, princess_pos)
        obstacles_to_princess = FeatureEngineer._obstacles_in_line(
            robot_pos, princess_pos, obstacles_positions
        )
        features.append(manhattan_princess)
        features.append(float(obstacles_to_princess))
        features.append(manhattan_princess + obstacles_to_princess * 2.0)

        # Path clearance (0.0 to 1.0)
        total_cells = board["rows"] * board["cols"]
        obstacle_density = len(obstacles_positions) / total_cells if total_cells > 0 else 0.0
        features.append(1.0 - obstacle_density)

        # Is there a clear path? (heuristic)
        features.append(1.0 if obstacle_density < 0.3 else 0.0)

        # ============================================================
        # MULTI-FLOWER STRATEGY (6 features)
        # ============================================================
        if flowers_positions:
            # Distances to nearest 3 flowers
            distances = sorted([
                FeatureEngineer._manhattan_distance(robot_pos,
                    (f["row"], f["col"]))
                for f in flowers_positions
            ])

            features.append(distances[0] if len(distances) > 0 else 0.0)
            features.append(distances[1] if len(distances) > 1 else 0.0)
            features.append(distances[2] if len(distances) > 2 else 0.0)

            # Average distance to all flowers
            features.append(sum(distances) / len(distances) if distances else 0.0)

            # Total estimated path (sum of distances - greedy TSP approximation)
            features.append(sum(distances))

            # Flower spread (max - min distance)
            if len(distances) > 1:
                features.append(distances[-1] - distances[0])
            else:
                features.append(0.0)
        else:
            features.extend([0.0] * 6)

        # ============================================================
        # ORIENTATION (4 features - one-hot)
        # ============================================================
        orientation = robot.get("orientation", "NORTH")
        features.append(1.0 if orientation == "NORTH" else 0.0)
        features.append(1.0 if orientation == "SOUTH" else 0.0)
        features.append(1.0 if orientation == "EAST" else 0.0)
        features.append(1.0 if orientation == "WEST" else 0.0)

        return np.array(features, dtype=np.float32)

    # ================================================================
    # HELPER METHODS
    # ================================================================

    @staticmethod
    def _get_adjacent_position(pos: tuple[int, int], direction: str) -> tuple[int, int]:
        """Get position adjacent to current position in given direction."""
        row, col = pos
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
        pos: tuple[int, int],
        flowers: list[dict],
        obstacles: list[dict],
        princess_pos: dict,
        board: dict
    ) -> str:
        """Determine what's at a given position."""
        row, col = pos

        # Out of bounds?
        if row < 0 or row >= board["rows"] or col < 0 or col >= board["cols"]:
            return "out_of_bounds"

        # Princess?
        if row == princess_pos["row"] and col == princess_pos["col"]:
            return "princess"

        # Flower?
        for flower in flowers:
            if flower["row"] == row and flower["col"] == col:
                return "flower"

        # Obstacle?
        for obstacle in obstacles:
            if obstacle["row"] == row and obstacle["col"] == col:
                return "obstacle"

        return "empty"

    @staticmethod
    def _one_hot_cell_type(cell_type: str) -> list[float]:
        """One-hot encode cell type."""
        types = ["empty", "flower", "obstacle", "princess", "out_of_bounds"]
        return [1.0 if cell_type == t else 0.0 for t in types]

    @staticmethod
    def _manhattan_distance(pos1: tuple[int, int], pos2: tuple[int, int]) -> float:
        """Calculate Manhattan distance."""
        return float(abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]))

    @staticmethod
    def _find_nearest(
        robot_pos: tuple[int, int],
        targets: list[dict]
    ) -> tuple[int, int]:
        """Find nearest target position."""
        if not targets:
            return robot_pos

        min_dist = float('inf')
        nearest = None

        for target in targets:
            target_pos = (target["row"], target["col"])
            dist = FeatureEngineer._manhattan_distance(robot_pos, target_pos)
            if dist < min_dist:
                min_dist = dist
                nearest = target_pos

        return nearest if nearest else robot_pos

    @staticmethod
    def _nearest_in_direction(
        robot_pos: tuple[int, int],
        direction: str,
        targets: list[dict]
    ) -> float:
        """Find distance to nearest target in given direction."""
        if not targets:
            return 0.0

        min_dist = float('inf')

        for target in targets:
            target_pos = (target["row"], target["col"])

            # Check if target is in the specified direction
            if direction == "NORTH" and target_pos[0] < robot_pos[0]:
                dist = FeatureEngineer._manhattan_distance(robot_pos, target_pos)
                min_dist = min(min_dist, dist)
            elif direction == "SOUTH" and target_pos[0] > robot_pos[0]:
                dist = FeatureEngineer._manhattan_distance(robot_pos, target_pos)
                min_dist = min(min_dist, dist)
            elif direction == "EAST" and target_pos[1] > robot_pos[1]:
                dist = FeatureEngineer._manhattan_distance(robot_pos, target_pos)
                min_dist = min(min_dist, dist)
            elif direction == "WEST" and target_pos[1] < robot_pos[1]:
                dist = FeatureEngineer._manhattan_distance(robot_pos, target_pos)
                min_dist = min(min_dist, dist)

        return float(min_dist) if min_dist != float('inf') else 0.0

    @staticmethod
    def _is_direction_towards(
        robot_pos: tuple[int, int],
        direction: str,
        target_pos: tuple[int, int]
    ) -> bool:
        """Check if moving in direction brings robot closer to target."""
        dr = target_pos[0] - robot_pos[0]
        dc = target_pos[1] - robot_pos[1]

        if direction == "NORTH":
            return dr < 0
        elif direction == "SOUTH":
            return dr > 0
        elif direction == "EAST":
            return dc > 0
        elif direction == "WEST":
            return dc < 0

        return False

    @staticmethod
    def _obstacles_in_line(
        pos1: tuple[int, int],
        pos2: tuple[int, int],
        obstacles: list[dict]
    ) -> int:
        """Count obstacles in the bounding box between two positions."""
        min_row = min(pos1[0], pos2[0])
        max_row = max(pos1[0], pos2[0])
        min_col = min(pos1[1], pos2[1])
        max_col = max(pos1[1], pos2[1])

        count = 0
        for obs in obstacles:
            if (min_row <= obs["row"] <= max_row and
                min_col <= obs["col"] <= max_col):
                count += 1

        return count

    @staticmethod
    def get_feature_names() -> list[str]:
        """Get human-readable feature names (72 total)."""
        names = [
            # Basic (12)
            "board_rows", "board_cols",
            "robot_row", "robot_col",
            "flowers_collected", "flowers_delivered",
            "flowers_capacity", "obstacles_cleaned",
            "princess_row", "princess_col",
            "flowers_remaining", "obstacles_remaining",
        ]

        # Directional awareness (32 = 8 × 4)
        for direction in ["north", "south", "east", "west"]:
            names.extend([
                f"{direction}_cell_empty",
                f"{direction}_cell_flower",
                f"{direction}_cell_obstacle",
                f"{direction}_cell_princess",
                f"{direction}_cell_oob",
                f"{direction}_nearest_flower",
                f"{direction}_nearest_obstacle",
                f"{direction}_towards_target",
            ])

        # Task context (10)
        names.extend([
            "phase_collection",
            "phase_delivery",
            "at_capacity",
            "progress_ratio",
            "moves_to_nearest_flower",
            "moves_to_princess",
            "obstacles_blocking_path",
            "capacity_utilization",
            "can_pick_more",
            "should_deliver",
        ])

        # Path quality (8)
        names.extend([
            "path_to_flower_manhattan",
            "path_to_flower_obstacles",
            "path_to_flower_estimated",
            "path_to_princess_manhattan",
            "path_to_princess_obstacles",
            "path_to_princess_estimated",
            "path_clearance",
            "has_clear_path",
        ])

        # Multi-flower strategy (6)
        names.extend([
            "nearest_flower_dist",
            "second_nearest_flower_dist",
            "third_nearest_flower_dist",
            "avg_flower_dist",
            "total_collection_path",
            "flower_spread",
        ])

        # Orientation (4)
        names.extend([
            "orientation_north",
            "orientation_south",
            "orientation_east",
            "orientation_west",
        ])

        return names

    # Keep existing encode_action and decode_action methods
    # (Same as current implementation - 24 action classes)

    @staticmethod
    def encode_action(action: str, direction: str | None = None) -> int:
        """Encode action as integer label (same as current)."""
        # ... (keep existing implementation)
        pass

    @staticmethod
    def decode_action(label: int) -> tuple[str, str | None]:
        """Decode integer label back to action (same as current)."""
        # ... (keep existing implementation)
        pass
