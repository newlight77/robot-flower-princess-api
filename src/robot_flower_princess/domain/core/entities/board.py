from dataclasses import dataclass, field
import random
from datetime import datetime
from .position import Position
from .robot import Robot
from .princess import Princess
from .cell import CellType
from ..value_objects.direction import Direction
from ..value_objects.game_status import GameStatus
from ....logging import get_logger

logger = get_logger("Board")


@dataclass
class Board:
    rows: int
    cols: int
    robot: Robot
    princess: Princess
    flowers: set[Position] = field(default_factory=set)
    obstacles: set[Position] = field(default_factory=set)
    initial_flower_count: int = 0
    flowers_delivered: int = 0
    name: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        self.initial_flower_count = len(self.flowers)
        logger.debug("Board.__post_init__ rows=%s cols=%s initial_flowers=%s", self.rows, self.cols, self.initial_flower_count)

    @classmethod
    def create(cls, rows: int, cols: int) -> "Board":
        """Factory method to create a new board with fixed positions."""
        if rows < 3 or rows > 50 or cols < 3 or cols > 50:
            raise ValueError("Board size must be between 3x3 and 50x50")

        # Robot always at top-left
        robot_pos = Position(0, 0)

        # Princess always at bottom-right
        princess_pos = Position(rows - 1, cols - 1)
        princess = Princess(position=princess_pos)

        total_cells = rows * cols
        max_flowers = max(1, int(total_cells * 0.1))
        num_obstacles = int(total_cells * 0.3)

        # Generate all positions except robot and princess
        all_positions = [Position(r, c) for r in range(rows) for c in range(cols)]
        all_positions = [p for p in all_positions if p != robot_pos and p != princess_pos]
        random.shuffle(all_positions)

        # Place flowers (up to 10% of board)
        num_flowers = random.randint(1, min(max_flowers, len(all_positions)))
        flowers = {all_positions.pop() for _ in range(num_flowers)}

        # Place obstacles (around 30% of board)
        obstacles = {all_positions.pop() for _ in range(min(num_obstacles, len(all_positions)))}

        robot = Robot(position=robot_pos, orientation=Direction.EAST)

        return cls(
            rows=rows,
            cols=cols,
            robot=robot,
            princess=princess,
            flowers=flowers,
            obstacles=obstacles,
        )

    def get_cell_type(self, position: Position) -> CellType:
        """Get the type of cell at the given position."""
        logger.debug("get_cell_type position=%s", position)
        if position == self.robot.position:
            return CellType.ROBOT
        if position == self.princess.position:
            return CellType.PRINCESS
        if position in self.flowers:
            return CellType.FLOWER
        if position in self.obstacles:
            return CellType.OBSTACLE
        return CellType.EMPTY

    def is_valid_position(self, position: Position) -> bool:
        """Check if a position is within board boundaries."""
        valid = 0 <= position.row < self.rows and 0 <= position.col < self.cols
        logger.debug("is_valid_position position=%s valid=%s", position, valid)
        return valid

    def is_empty(self, position: Position) -> bool:
        """Check if a position is empty."""
        empty = self.get_cell_type(position) == CellType.EMPTY
        logger.debug("is_empty position=%s empty=%s", position, empty)
        return empty

    def get_status(self) -> GameStatus:
        """Determine the current game status."""
        status = (
            GameStatus.VICTORY
            if self.flowers_delivered == self.initial_flower_count and self.initial_flower_count > 0
            else GameStatus.IN_PROGRESS
        )
        logger.debug("get_status flowers_delivered=%s initial=%s status=%s", self.flowers_delivered, self.initial_flower_count, status)
        return status

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now()

    @property
    def princess_position(self) -> Position:
        """Backward compatibility property for princess position."""
        return self.princess.position

    def to_dict(self) -> dict:
        """Convert board to dictionary representation for API compatibility."""
        logger.debug("to_dict rows=%s cols=%s", self.rows, self.cols)
        grid = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                pos = Position(r, c)
                cell = self.get_cell_type(pos)

                emoji_map = {
                    CellType.ROBOT: "🤖",
                    CellType.PRINCESS: "👑",
                    CellType.FLOWER: "🌸",
                    CellType.OBSTACLE: "🗑️",
                    CellType.EMPTY: "⬜",
                }
                row.append(emoji_map[cell])
            grid.append(row)

        return {
            "rows": self.rows,
            "cols": self.cols,
            "grid": grid,
            "robot": {
                "position": {"row": self.robot.position.row, "col": self.robot.position.col},
                "orientation": self.robot.orientation.value,
                "flowers_held": self.robot.flowers_held,
                "max_flowers": self.robot.max_flowers,
            },
            "princess_position": {
                "row": self.princess.position.row,
                "col": self.princess.position.col,
            },
            "flowers_remaining": len(self.flowers),
            "flowers_delivered": self.flowers_delivered,
            "total_flowers": self.initial_flower_count,
            "status": self.get_status().value,
        }

    def to_game_model_dict(self) -> dict:
        """Convert board to dictionary representation matching the game model JSON structure."""
        logger.debug("to_game_model_dict rows=%s cols=%s", self.rows, self.cols)
        grid = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                pos = Position(r, c)
                cell = self.get_cell_type(pos)

                emoji_map = {
                    CellType.ROBOT: "🤖",
                    CellType.PRINCESS: "👑",
                    CellType.FLOWER: "🌸",
                    CellType.OBSTACLE: "🗑️",
                    CellType.EMPTY: "⬜",
                }
                row.append(emoji_map[cell])
            grid.append(row)

        return {
            "board": {
                "rows": self.rows,
                "cols": self.cols,
                "grid": grid,
            },
            "robot": {
                "position": {"row": self.robot.position.row, "col": self.robot.position.col},
                "orientation": self.robot.orientation.value,
                "flowers": {
                    "collected": self.robot.flowers_collected,
                    "delivered": self.robot.flowers_delivered,
                    "collection_capacity": self.robot.max_flowers,
                },
                "obstacles": {
                    "cleaned": self.robot.obstacles_cleaned,
                },
                "executed_actions": self.robot.executed_actions,
            },
            "princess": {
                "position": {"row": self.princess.position.row, "col": self.princess.position.col},
                "flowers_received": self.princess.flowers_received,
                "mood": self.princess.mood,
            },
            "obstacles": {
                "remaining": len(self.obstacles),
                "total": len(self.obstacles) + len(self.robot.obstacles_cleaned),
            },
            "flowers": {
                "remaining": len(self.flowers),
                "total": self.initial_flower_count,
            },
            "status": self.get_status().value,
            "created_at": self.created_at.isoformat() + "Z",
            "updated_at": self.updated_at.isoformat() + "Z",
        }
