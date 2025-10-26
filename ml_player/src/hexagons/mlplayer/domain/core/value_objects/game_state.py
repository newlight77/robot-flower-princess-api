"""
Game State - Simplified board state representation for ML player.
"""
from typing import Any, Dict, List, Tuple
from shared.logging import logger

class GameState:
    """Game State - Simplified board state representation for ML player.

    This is a simplified representation of the game state for the ML player.
    It is used to store the game state and to convert it to a feature vector for the ML model.
    """
    game_id: str
    board: Any
    robot: Any
    princess: Any

    def __init__(self, game_id: str, board: Any, robot: Any, princess: Any):

        logger.info(f"GameState.__init__: Initializing GameState game_id={game_id}")
        logger.info(f"GameState.__init__: Initializing GameState robot={robot}")
        logger.info(f"GameState.__init__: Initializing GameState princess={princess}")
        logger.info(f"GameState.__init__: Initializing GameState board={board}")

        self.game_id = game_id
        self.board = board
        self.robot = robot
        self.princess = princess


    def to_feature_vector(self) -> List[float]:
        """
        Convert game state to feature vector for ML.

        Future: This will be input to ML model.
        Current: Used for weighted scoring.
        """
        logger.info(f"GameState.to_feature_vector: Converting board state to feature vector={self.to_dict()}")
        features = [
            float(self.board["rows"]), # rows
            float(self.board["cols"]), # cols
            float(self.robot["position"]["row"]), # robot_position_row
            float(self.robot["position"]["col"]), # robot_position_col
            float(len(self.robot["flowers_collected"])), # flowers_collected_count
            float(len(self.robot["flowers_delivered"])), # flowers_delivered_count
            float(self.robot["flowers_collection_capacity"]), # flowers_collection_capacity
            float(len(self.robot["obstacles_cleaned"])), # obstacles_cleaned_count
            float(len(self.board["flowers_positions"])), # flowers_positions_count
            float(len(self.board["obstacles_positions"])), # obstacles_positions_count
            float(self.board["initial_flowers_count"] - len(self.robot["flowers_collected"])), # flowers_remaining
            float(self.board["initial_obstacles_count"] - len(self.robot["obstacles_cleaned"])), # obstacles_remaining
            float(len(self.robot["executed_actions"])), # executed_actions_count

            # Derived features
            self._distance_to_princess(), # distance_to_princess
            self._closest_flower_distance(), # closest_flower_distance
            self._obstacle_density(), # obstacle_density
        ]
        return features

    def _distance_to_princess(self) -> float:
        """Manhattan distance to princess."""
        logger.info(f"GameState._distance_to_princess: Distance to princess={self.robot['position']} -> {self.princess['position']}")
        return float(abs(self.robot["position"]["row"] - self.princess["position"]["row"]) + abs(
            self.robot["position"]["col"] - self.princess["position"]["col"]
        ))

    def _closest_flower_distance(self) -> float:
        """Distance to closest flower."""
        if not self.board["flowers_positions"] or len(self.board["flowers_positions"]) == 0:
            return 0.0
        logger.info(f"GameState._closest_flower_distance: Distance to closest flower={len(self.board['flowers_positions'])}")
        distances = [
            abs(self.robot["position"]["row"] - f["row"]) + abs(self.robot["position"]["col"] - f["col"])
            for f in self.board["flowers_positions"]
        ]
        return float(min(distances))

    def _obstacle_density(self) -> float:
        """Obstacle density around robot."""
        logger.info(f"GameState._obstacle_density: Obstacle density={len(self.board['obstacles_positions'])}")
        obstacle_count = len(self.board["obstacles_positions"])
        return obstacle_count / (self.board["rows"] * self.board["cols"])  # Normalize to [0, 1]

    def to_dict(self) -> dict:
        """Convert GameState to dictionary."""
        logger.info(f"GameState.to_dict: Converting GameState game_id={self.game_id}")
        game_state = {
            "game_id": self.game_id,
            "board": {
                "rows": self.board["rows"],
                "cols": self.board["cols"],
                "grid": self.board["grid"],
                "robot_position": {
                    "row": self.robot["position"]["row"],
                    "col": self.robot["position"]["col"]
                },
                "princess_position": {
                    "row": self.princess["position"]["row"],
                    "col": self.princess["position"]["col"]
                },
                "flowers_positions": [{"row": f["row"], "col": f["col"]} for f in self.board["flowers_positions"]],
                "obstacles_positions": [{"row": o["row"], "col": o["col"]} for o in self.board["obstacles_positions"]],
                "initial_flowers_count": self.board["initial_flowers_count"],
                "initial_obstacles_count": self.board["initial_obstacles_count"],
            },
            "robot": {
                "position": {"row": self.robot["position"]["row"], "col": self.robot["position"]["col"]},
                "orientation": self.robot["orientation"],
                "flowers_collected": [{"row": f["row"], "col": f["col"]} for f in self.robot["flowers_collected"]],
                "flowers_delivered": [{"row": f["row"], "col": f["col"]} for f in self.robot["flowers_delivered"]],
                "flowers_collection_capacity": self.robot["flowers_collection_capacity"],
                "obstacles_cleaned": [{"row": o["row"], "col": o["col"]} for o in self.robot["obstacles_cleaned"]],
                "executed_actions": [{"type": a["type"], "direction": a["direction"], "success": a["success"], "message": a["message"]} for a in self.robot["executed_actions"]],
            },
            "princess": {
                "position": {"row": self.princess["position"]["row"], "col": self.princess["position"]["col"]},
                "flowers_received": [{"row": f["row"], "col": f["col"]} for f in self.princess["flowers_received"]],
                "mood": self.princess["mood"],
            },
        }

        logger.info(f"GameState.to_dict: GameState converted to dictionary={game_state}")

        return game_state