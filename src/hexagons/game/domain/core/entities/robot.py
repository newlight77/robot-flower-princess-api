from dataclasses import dataclass, field
from typing import List, Dict, Any
from .position import Position
from ..value_objects.direction import Direction
from ..value_objects.action_type import ActionType


@dataclass
class Robot:
    position: Position
    orientation: Direction = Direction.EAST
    flowers_held: int = 0
    max_flowers: int = 12
    flowers_collected: List[Dict[str, Any]] = field(default_factory=list)
    flowers_delivered: List[Dict[str, Any]] = field(default_factory=list)
    obstacles_cleaned: List[Dict[str, Any]] = field(default_factory=list)
    executed_actions: List[Dict[str, Any]] = field(default_factory=list)

    def move_to(self, new_position: Position) -> None:
        self.position = new_position

    def rotate(self, direction: Direction) -> None:
        self.orientation = direction

    def pick_flower(self, flower_position: Position = None) -> None:
        if self.flowers_held >= self.max_flowers:
            raise ValueError(f"Cannot hold more than {self.max_flowers} flowers")
        self.flowers_held += 1
        if flower_position:
            self.flowers_collected.append(
                {"position": {"row": flower_position.row, "col": flower_position.col}}
            )

    def drop_flower(self, drop_position: Position = None) -> None:
        if self.flowers_held == 0:
            raise ValueError("No flowers to drop")
        self.flowers_held -= 1
        # Note: dropped flowers are not tracked in delivered list, only given flowers are

    def give_flowers(self, princess_position: Position = None) -> int:
        count = self.flowers_held
        if count > 0 and princess_position:
            # Add one entry per flower delivered
            for _ in range(count):
                self.flowers_delivered.append(
                    {"position": {"row": princess_position.row, "col": princess_position.col}}
                )
        self.flowers_held = 0
        return count

    def clean_obstacle(self, obstacle_position: Position) -> None:
        self.obstacles_cleaned.append(
            {"position": {"row": obstacle_position.row, "col": obstacle_position.col}}
        )

    def add_executed_action(self, action_type: ActionType, direction: Direction) -> None:
        """Add an action to the executed actions history."""
        self.executed_actions.append({"type": action_type.value, "direction": direction.value})

    def can_clean(self) -> bool:
        return self.flowers_held == 0

    def can_pick(self) -> bool:
        return self.flowers_held < self.max_flowers

    def to_dict(self) -> dict:
        """Convert robot to dictionary representation for API."""
        return {
            "position": {"row": self.position.row, "col": self.position.col},
            "orientation": self.orientation.value,
            "flowers": {
                "collected": self.flowers_collected,
                "delivered": self.flowers_delivered,
                "collection_capacity": self.max_flowers,
            },
            "obstacles": {
                "cleaned": self.obstacles_cleaned,
            },
            "executed_actions": self.executed_actions,
        }
