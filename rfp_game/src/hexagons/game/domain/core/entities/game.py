import random
from datetime import datetime

from .position import Position
from .robot import Robot
from .princess import Princess
from .board import Board
from .cell import CellType
from ..value_objects.direction import Direction
from ..value_objects.game_status import GameStatus
from shared.logging import get_logger

logger = get_logger("Game")


class Game:
    def __init__(
        self,
        rows: int,
        cols: int,
        robot: Robot,
        princess: Princess = None,
        game_id: str = "",
        **kwargs,
    ):
        """Initialize Game."""
        self.game_id = game_id or kwargs.get("game_id", "")
        self.board = Board(rows, cols)
        self.robot = robot

        # Handle princess initialization
        if princess is not None:
            self.princess = princess
        else:
            # Default princess position at bottom-right
            self.princess = Princess(position=Position(self.board.rows - 1, self.board.cols - 1))

        # Set other fields
        self.flowers = kwargs.get("flowers", set())
        self.obstacles = kwargs.get("obstacles", set())
        self.initial_flower_count = kwargs.get("initial_flower_count", 0)
        self.flowers_delivered = kwargs.get("flowers_delivered", 0)
        self.name = kwargs.get("name", "")
        self.created_at = kwargs.get("created_at", datetime.now())
        self.updated_at = kwargs.get("updated_at", datetime.now())

        # Set initial flower count if not provided
        if self.initial_flower_count == 0:
            self.initial_flower_count = len(self.flowers)

        logger.debug(
            "Game.__init__ rows=%s cols=%s initial_flowers=%s",
            self.board.rows,
            self.board.cols,
            self.initial_flower_count,
        )

    @property
    def rows(self) -> int:
        """Get board rows for backward compatibility."""
        return self.board.rows

    @property
    def cols(self) -> int:
        """Get board cols for backward compatibility."""
        return self.board.cols

    @classmethod
    def create(cls, rows: int, cols: int) -> "Game":
        """Factory method to create a new game with fixed positions."""
        if rows < 3 or rows > 50 or cols < 3 or cols > 50:
            raise ValueError("Game size must be between 3x3 and 50x50")

        # Robot always at top-left
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)

        # Princess always at bottom-right
        princess = Princess(position=Position(rows - 1, cols - 1))

        total_cells = rows * cols
        max_flowers = max(1, int(total_cells * 0.1))
        num_obstacles = int(total_cells * 0.3)

        # Generate all positions except robot and princess
        all_positions = [Position(r, c) for r in range(rows) for c in range(cols)]
        all_positions = [p for p in all_positions if p != robot.position and p != princess.position]
        random.shuffle(all_positions)

        # Place flowers (up to 10% of board)
        num_flowers = random.randint(1, min(max_flowers, len(all_positions)))
        flowers = {all_positions.pop() for _ in range(num_flowers)}

        # Place obstacles (around 30% of board)
        obstacles = {all_positions.pop() for _ in range(min(num_obstacles, len(all_positions)))}

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
        """Check if a position is within game boundaries."""
        valid = self.board.is_valid_position(position)
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
        logger.debug(
            "get_status flowers_delivered=%s initial=%s status=%s",
            self.flowers_delivered,
            self.initial_flower_count,
            status,
        )
        return status

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert game to dictionary representation for API compatibility."""
        logger.debug("to_dict rows=%s cols=%s", self.board.rows, self.board.cols)

        board_dict = self.board.to_dict(
            robot_position=self.robot.position,
            princess_position=self.princess.position,
            flowers_positions=self.flowers,
            obstacles_positions=self.obstacles,
        )

        return {
            "board": board_dict,
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
