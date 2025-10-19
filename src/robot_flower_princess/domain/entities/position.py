from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    row: int
    col: int

    def move(self, row_delta: int, col_delta: int) -> "Position":
        return Position(self.row + row_delta, self.col + col_delta)

    def __hash__(self) -> int:
        return hash((self.row, self.col))

    def manhattan_distance(self, other: "Position") -> int:
        """Calculate Manhattan distance to another position."""
        return abs(self.row - other.row) + abs(self.col - other.col)
