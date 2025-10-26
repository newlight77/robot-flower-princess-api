from datetime import datetime
import uuid

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
        game_id: str = str(uuid.uuid4()),
        name: str = "",
    ):
        """Initialize Game."""
        self.game_id = game_id
        self.name = name
        self.robot = robot

        # Handle princess initialization
        if princess is not None:
            self.princess = princess
        else:
            # Default princess position at bottom-right
            self.princess = Princess(position=Position(rows - 1, cols - 1))

        # Create board with robot and princess positions (board generates flowers/obstacles)
        self.board = Board(rows, cols, self.robot.position, self.princess.position)

        # Set other fields
        self.flowers_delivered = 0
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

        logger.debug("Game.__init__ rows=%s cols=%s", self.board.rows, self.board.cols)

    @property
    def rows(self) -> int:
        """Get board rows for backward compatibility."""
        return self.board.rows

    @property
    def cols(self) -> int:
        """Get board cols for backward compatibility."""
        return self.board.cols

    @property
    def flowers(self) -> set[Position]:
        """Get flowers positions from board."""
        return self.board.flowers_positions

    @flowers.setter
    def flowers(self, value: set[Position]) -> None:
        """Set flowers positions on board."""
        self.board.flowers_positions = value

    @property
    def obstacles(self) -> set[Position]:
        """Get obstacles positions from board."""
        return self.board.obstacles_positions

    @obstacles.setter
    def obstacles(self, value: set[Position]) -> None:
        """Set obstacles positions on board."""
        self.board.obstacles_positions = value

    @classmethod
    def create(cls, rows: int, cols: int, name: str = "") -> "Game":
        """Factory method to create a new game with fixed positions."""
        if rows < 3 or rows > 50 or cols < 3 or cols > 50:
            raise ValueError("Game size must be between 3x3 and 50x50")

        # Set the game name if provided
        if name is None or name == "":
            name = f"Game-{rows}x{cols}"

        # Robot always at top-left
        robot = Robot(position=Position(0, 0), orientation=Direction.EAST)

        # Princess always at bottom-right
        princess = Princess(position=Position(rows - 1, cols - 1))

        # Board will generate random flowers and obstacles
        return cls(
            rows=rows,
            cols=cols,
            robot=robot,
            princess=princess,
            name=name,
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

        board_dict = self.board.to_dict()

        return {
            "id": self.game_id,
            "name": self.name,
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
                "remaining": self.board.initial_obstacles_count - len(self.robot.obstacles_cleaned),
                "total": self.board.initial_obstacles_count,
            },
            "flowers": {
                "remaining": self.board.initial_flowers_count - len(self.robot.flowers_collected),
                "total": self.board.initial_flowers_count,
            },
            "status": self.get_status().value,
            "created_at": self.created_at.isoformat() + "Z",
            "updated_at": self.updated_at.isoformat() + "Z",
        }
