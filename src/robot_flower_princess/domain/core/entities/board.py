from dataclasses import dataclass
from .position import Position


@dataclass
class Board:
    """Represents the game board grid."""

    rows: int
    cols: int

    def __init__(self, rows: int, cols: int):
        """Initialize board with dimensions."""
        self.rows = rows
        self.cols = cols

    def is_valid_position(self, position: Position) -> bool:
        """Check if a position is within board boundaries."""
        return 0 <= position.row < self.rows and 0 <= position.col < self.cols

    def get_grid(
        self,
        robot_pos: Position,
        princess_pos: Position,
        flowers: set[Position],
        obstacles: set[Position],
    ) -> list[list[str]]:
        """Generate the grid representation with emojis."""
        grid = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                pos = Position(r, c)

                if pos == robot_pos:
                    cell = "🤖"
                elif pos == princess_pos:
                    cell = "👑"
                elif pos in flowers:
                    cell = "🌸"
                elif pos in obstacles:
                    cell = "🗑️"
                else:
                    cell = "⬜"

                row.append(cell)
            grid.append(row)
        return grid

    def to_dict(
        self,
        robot_pos: Position = None,
        princess_pos: Position = None,
        flowers: set[Position] = None,
        obstacles: set[Position] = None,
    ) -> dict:
        """Convert board to dictionary representation."""
        grid = self.get_grid(
            robot_pos or Position(0, 0),
            princess_pos or Position(self.rows - 1, self.cols - 1),
            flowers or set(),
            obstacles or set(),
        )

        return {
            "rows": self.rows,
            "cols": self.cols,
            "grid": grid,
        }
