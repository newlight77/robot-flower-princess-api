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
        robot_position: Position,
        princess_position: Position,
        flowers_positions: set[Position],
        obstacles_positions: set[Position],
    ) -> list[list[str]]:
        """Generate the grid representation with emojis."""
        grid = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                pos = Position(r, c)

                if pos == robot_position:
                    cell = "🤖"
                elif pos == princess_position:
                    cell = "👑"
                elif pos in flowers_positions:
                    cell = "🌸"
                elif pos in obstacles_positions:
                    cell = "🗑️"
                else:
                    cell = "⬜"

                row.append(cell)
            grid.append(row)
        return grid

    def to_dict(
        self,
        robot_position: Position = None,
        princess_position: Position = None,
        flowers_positions: set[Position] = None,
        obstacles_positions: set[Position] = None,
    ) -> dict:
        """Convert board to dictionary representation."""
        grid = self.get_grid(
            robot_position or Position(0, 0),
            princess_position or Position(self.rows - 1, self.cols - 1),
            flowers_positions or set(),
            obstacles_positions or set(),
        )

        return {
            "rows": self.rows,
            "cols": self.cols,
            "grid": grid,
        }
