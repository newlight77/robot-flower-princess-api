from dataclasses import dataclass
from typing import List


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

    def adjacent_positions(self) -> List["Position"]:
        return [
            self.move(1, 0),
            self.move(-1, 0),
            self.move(0, 1),
            self.move(0, -1),
        ]

    def to_dict(self) -> dict:
        """Convert position to dictionary representation."""
        return {
            "row": self.row,
            "col": self.col,
        }

    @classmethod
    def from_dict(cls, dict: dict) -> "Position":
        return cls(row=dict["row"], col=dict["col"])
