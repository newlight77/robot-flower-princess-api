import random
from dataclasses import dataclass
from typing import TYPE_CHECKING
from .position import Position

if TYPE_CHECKING:
    pass


@dataclass
class Board:
    """Represents the game board grid with all positions."""

    rows: int
    cols: int
    grid: list[list[Position]]
    robot_position: Position
    princess_position: Position
    flowers_positions: set[Position]
    obstacles_positions: set[Position]
    initial_flowers_count: int
    initial_obstacles_count: int

    def __init__(self, rows: int, cols: int, robot_position: Position, princess_position: Position):
        """Initialize board with dimensions, robot/princess positions, and generate random flowers/obstacles."""
        self.rows = rows
        self.cols = cols
        self.robot_position = robot_position
        self.princess_position = princess_position

        # Create all positions in the board
        self.grid = [[Position(r, c) for c in range(cols)] for r in range(rows)]

        # Generate random flowers and obstacles
        total_cells = rows * cols
        max_flowers = max(1, int(total_cells * 0.1))
        num_obstacles = int(total_cells * 0.3)

        # Get all available positions (excluding robot and princess)
        # Flatten the 2D positions list
        all_positions = [pos for row in self.grid for pos in row]
        available_positions = [
            p for p in all_positions if p != robot_position and p != princess_position
        ]
        random.shuffle(available_positions)

        # Place flowers (up to 10% of board)
        num_flowers = random.randint(1, min(max_flowers, len(available_positions)))
        self.flowers_positions = {available_positions.pop() for _ in range(num_flowers)}

        # Place obstacles (around 30% of board)
        self.obstacles_positions = {
            available_positions.pop() for _ in range(min(num_obstacles, len(available_positions)))
        }

        # Store initial counts
        self.initial_flowers_count = len(self.flowers_positions)
        self.initial_obstacles_count = len(self.obstacles_positions)

    def is_valid_position(self, position: Position) -> bool:
        """Check if a position is within board boundaries."""
        return 0 <= position.row < self.rows and 0 <= position.col < self.cols

    def move_robot(self, new_position: Position) -> None:
        """Update robot position on the board."""
        self.robot_position = new_position

    def pick_flower(self, position: Position) -> None:
        """Remove a flower from the board."""
        self.flowers_positions.discard(position)

    def drop_flower(self, position: Position) -> None:
        """Add a flower to the board."""
        self.flowers_positions.add(position)

    def clean_obstacle(self, position: Position) -> None:
        """Remove an obstacle from the board."""
        self.obstacles_positions.discard(position)

    def get_grid(self) -> list[list[str]]:
        """Generate the grid representation with emojis."""
        grid = []
        for row_positions in self.grid:
            row = []
            for pos in row_positions:
                if pos == self.robot_position:
                    cell = "🤖"
                elif pos == self.princess_position:
                    cell = "👑"
                elif pos in self.flowers_positions:
                    cell = "🌸"
                elif pos in self.obstacles_positions:
                    cell = "🗑️"
                else:
                    cell = "⬜"

                row.append(cell)
            grid.append(row)
        return grid

    def to_dict(self) -> dict:
        """Convert board to dictionary representation."""
        grid = self.get_grid()

        return {
            "rows": self.rows,
            "cols": self.cols,
            "grid": grid,
            "robot_position": {
                "row": self.robot_position.row,
                "col": self.robot_position.col,
            },
            "princess_position": {
                "row": self.princess_position.row,
                "col": self.princess_position.col,
            },
            "flowers_positions": [{"row": p.row, "col": p.col} for p in self.flowers_positions],
            "obstacles_positions": [{"row": p.row, "col": p.col} for p in self.obstacles_positions],
            "initial_flowers_count": self.initial_flowers_count,
            "initial_obstacles_count": self.initial_obstacles_count,
        }
