"""
Feature Engineering for ML Models.

Transforms game states into feature vectors for model training/inference.
"""

from typing import Any

import numpy as np


class FeatureEngineer:
    """Transforms game states into ML-ready feature vectors."""

    @staticmethod
    def extract_features(game_state: dict[str, Any]) -> np.ndarray:
        """
        Extract features from game state.

        Features include:
        - Board dimensions
        - Robot position and state
        - Princess position
        - Flower counts and positions
        - Obstacle counts and positions
        - Derived features (distances, densities, etc.)

        Args:
            game_state: Raw game state dictionary

        Returns:
            NumPy array of features
        """
        board = game_state["board"]
        robot = game_state["robot"]
        princess = game_state["princess"]

        features = []

        # Basic board info
        features.append(float(board["rows"]))
        features.append(float(board["cols"]))

        # Robot state
        features.append(float(robot["position"]["row"]))
        features.append(float(robot["position"]["col"]))
        features.append(float(len(robot["flowers_collected"])))
        features.append(float(len(robot["flowers_delivered"])))
        features.append(float(robot["flowers_collection_capacity"]))
        features.append(float(len(robot["obstacles_cleaned"])))

        # Princess state
        features.append(float(princess["position"]["row"]))
        features.append(float(princess["position"]["col"]))

        # Flower state
        flowers_positions = board.get("flowers_positions", [])
        features.append(float(len(flowers_positions)))

        # Obstacle state
        obstacles_positions = board.get("obstacles_positions", [])
        features.append(float(len(obstacles_positions)))

        # Derived features
        features.append(FeatureEngineer._distance_to_princess(robot, princess))
        features.append(FeatureEngineer._closest_flower_distance(robot, flowers_positions))
        features.append(FeatureEngineer._obstacle_density(obstacles_positions, board))
        features.append(FeatureEngineer._path_clearance(robot, princess, obstacles_positions))

        # Orientation encoding (one-hot)
        orientation = robot["orientation"]
        features.append(1.0 if orientation == "NORTH" else 0.0)
        features.append(1.0 if orientation == "SOUTH" else 0.0)
        features.append(1.0 if orientation == "EAST" else 0.0)
        features.append(1.0 if orientation == "WEST" else 0.0)

        return np.array(features, dtype=np.float32)

    @staticmethod
    def _distance_to_princess(robot: dict[str, Any], princess: dict[str, Any]) -> float:
        """Calculate Manhattan distance from robot to princess."""
        return float(
            abs(robot["position"]["row"] - princess["position"]["row"])
            + abs(robot["position"]["col"] - princess["position"]["col"])
        )

    @staticmethod
    def _closest_flower_distance(robot: dict[str, Any], flowers: list[dict[str, Any]]) -> float:
        """Calculate distance to closest flower."""
        if not flowers:
            return 0.0

        distances = [
            abs(robot["position"]["row"] - f["row"]) + abs(robot["position"]["col"] - f["col"]) for f in flowers
        ]
        return float(min(distances))

    @staticmethod
    def _obstacle_density(obstacles: list[dict[str, Any]], board: dict[str, Any]) -> float:
        """Calculate obstacle density."""
        total_cells = board["rows"] * board["cols"]
        return len(obstacles) / total_cells if total_cells > 0 else 0.0

    @staticmethod
    def _path_clearance(robot: dict[str, Any], princess: dict[str, Any], obstacles: list[dict[str, Any]]) -> float:
        """
        Calculate path clearance (inverse of obstacles between robot and princess).

        Returns:
            Value between 0 (completely blocked) and 1 (completely clear)
        """
        if not obstacles:
            return 1.0

        robot_pos = (robot["position"]["row"], robot["position"]["col"])
        princess_pos = (princess["position"]["row"], princess["position"]["col"])

        # Simple heuristic: count obstacles in the bounding box
        min_row = min(robot_pos[0], princess_pos[0])
        max_row = max(robot_pos[0], princess_pos[0])
        min_col = min(robot_pos[1], princess_pos[1])
        max_col = max(robot_pos[1], princess_pos[1])

        obstacles_in_path = sum(
            1 for obs in obstacles if min_row <= obs["row"] <= max_row and min_col <= obs["col"] <= max_col
        )

        bounding_box_size = (max_row - min_row + 1) * (max_col - min_col + 1)
        if bounding_box_size == 0:
            return 1.0

        return 1.0 - (obstacles_in_path / bounding_box_size)

    @staticmethod
    def encode_action(action: str, direction: str | None = None) -> int:
        """
        Encode action as integer label for classification.

        Args:
            action: Action type
            direction: Direction for move/rotate actions

        Returns:
            Integer label
        """
        # Action encoding:
        # 0-3: move (NORTH, SOUTH, EAST, WEST)
        # 4-7: rotate (NORTH, SOUTH, EAST, WEST)
        # 8-11: pick (NORTH, SOUTH, EAST, WEST)
        # 12-15: drop (NORTH, SOUTH, EAST, WEST)
        # 16-19: give (NORTH, SOUTH, EAST, WEST)
        # 20-23: clean (NORTH, SOUTH, EAST, WEST)

        if action == "move":
            if direction == "NORTH":
                return 0
            elif direction == "SOUTH":
                return 1
            elif direction == "EAST":
                return 2
            elif direction == "WEST":
                return 3
        elif action == "rotate":
            if direction == "NORTH":
                return 4
            elif direction == "SOUTH":
                return 5
            elif direction == "EAST":
                return 6
            elif direction == "WEST":
                return 7
        elif action == "pick":
            if direction == "NORTH":
                return 8
            elif direction == "SOUTH":
                return 9
            elif direction == "EAST":
                return 10
            elif direction == "WEST":
                return 11
        elif action == "drop":
            if direction == "NORTH":
                return 12
            elif direction == "SOUTH":
                return 13
            elif direction == "EAST":
                return 14
            elif direction == "WEST":
                return 15
        elif action == "give":
            if direction == "NORTH":
                return 16
            elif direction == "SOUTH":
                return 17
            elif direction == "EAST":
                return 18
            elif direction == "WEST":
                return 19
        elif action == "clean":
            if direction == "NORTH":
                return 20
            elif direction == "SOUTH":
                return 21
            elif direction == "EAST":
                return 22
            elif direction == "WEST":
                return 23

        raise ValueError(f"Unknown action: {action} with direction: {direction}")

    @staticmethod
    def decode_action(label: int) -> tuple[str, str | None]:
        """
        Decode integer label back to action and direction.

        Args:
            label: Integer label

        Returns:
            Tuple of (action, direction)
        """
        action_map = {
            0: ("move", "NORTH"),
            1: ("move", "SOUTH"),
            2: ("move", "EAST"),
            3: ("move", "WEST"),
            4: ("rotate", "NORTH"),
            5: ("rotate", "SOUTH"),
            6: ("rotate", "EAST"),
            7: ("rotate", "WEST"),
            8: ("pick", "NORTH"),
            9: ("pick", "SOUTH"),
            10: ("pick", "EAST"),
            11: ("pick", "WEST"),
            12: ("drop", "NORTH"),
            13: ("drop", "SOUTH"),
            14: ("drop", "EAST"),
            15: ("drop", "WEST"),
            16: ("give", "NORTH"),
            17: ("give", "SOUTH"),
            18: ("give", "EAST"),
            19: ("give", "WEST"),
            20: ("clean", "NORTH"),
            21: ("clean", "SOUTH"),
            22: ("clean", "EAST"),
            23: ("clean", "WEST"),
        }

        if label not in action_map:
            raise ValueError(f"Unknown label: {label}")

        return action_map[label]

    @staticmethod
    def get_feature_names() -> list[str]:
        """
        Get human-readable feature names.

        Returns:
            List of feature names
        """
        return [
            "board_rows",
            "board_cols",
            "robot_row",
            "robot_col",
            "flowers_collected",
            "flowers_delivered",
            "flowers_capacity",
            "obstacles_cleaned",
            "princess_row",
            "princess_col",
            "flowers_remaining",
            "obstacles_remaining",
            "distance_to_princess",
            "closest_flower_distance",
            "obstacle_density",
            "path_clearance",
            "orientation_north",
            "orientation_south",
            "orientation_east",
            "orientation_west",
        ]
