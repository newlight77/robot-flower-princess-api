from dataclasses import dataclass
from .position import Position
from ..value_objects.direction import Direction


@dataclass
class Robot:
    position: Position
    orientation: Direction = Direction.EAST
    flowers_held: int = 0
    max_flowers: int = 12

    def move_to(self, new_position: Position) -> None:
        self.position = new_position

    def rotate(self, direction: Direction) -> None:
        self.orientation = direction

    def pick_flower(self) -> None:
        if self.flowers_held >= self.max_flowers:
            raise ValueError(f"Cannot hold more than {self.max_flowers} flowers")
        self.flowers_held += 1

    def drop_flower(self) -> None:
        if self.flowers_held == 0:
            raise ValueError("No flowers to drop")
        self.flowers_held -= 1

    def give_flowers(self) -> int:
        count = self.flowers_held
        self.flowers_held = 0
        return count

    def can_clean(self) -> bool:
        return self.flowers_held == 0

    def can_pick(self) -> bool:
        return self.flowers_held < self.max_flowers
