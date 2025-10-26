from dataclasses import dataclass, field
from typing import List
from .position import Position
from ..value_objects.direction import Direction
from ..value_objects.action import Action, ActionType


@dataclass
class Robot:
    position: Position
    orientation: Direction = Direction.EAST
    max_flowers: int = 12
    flowers_collected: List[Position] = field(default_factory=list)
    flowers_delivered: List[Position] = field(default_factory=list)
    obstacles_cleaned: List[Position] = field(default_factory=list)
    executed_actions: List[Action] = field(default_factory=list)

    def move_to(self, new_position: Position) -> None:
        self.position = new_position

    def rotate(self, direction: Direction) -> None:
        self.orientation = direction

    def pick_flower(self, flower_position: Position = None) -> Action:
        action = Action(action_type=ActionType.PICK, direction=self.orientation, flower_position=flower_position)
        self.add_executed_action(action)

        if len(self.flowers_collected) >= self.max_flowers:
            action.message = f"Cannot hold more than {self.max_flowers} flowers"
            return action
        if not flower_position:
            action.message = "No flower to pick"
            return action

        self.flowers_collected.append(flower_position)
        return action

    def drop_flower(self, drop_position: Position = None) -> Action:
        action = Action(action_type=ActionType.DROP, direction=self.orientation, drop_position=drop_position)
        self.add_executed_action(action)

        if len(self.flowers_collected) == 0:
            action.message = "No flowers to drop"
            return action
        if not drop_position:
            action.message = "No position to drop flowers"
            return action

        self.flowers_collected.remove(drop_position)
        return action

    def give_flowers(self, princess_position: Position = None) -> Action:
        action = Action(action_type=ActionType.GIVE, direction=self.orientation, princess_position=princess_position)
        self.add_executed_action(action)

        """Give all collected flowers to princess. Returns count of flowers delivered."""
        if len(self.flowers_collected) == 0:
            action.message = "No flowers to give"
            return action
        if not princess_position:
            action.message = "No princess to give flowers to"
            return action

        self.flowers_delivered.extend(self.flowers_collected)
        self.flowers_collected.clear()

        return action

    def clean_obstacle(self, obstacle_position: Position) -> Action:
        action = Action(action_type=ActionType.CLEAN, direction=self.orientation, obstacle_position=obstacle_position)
        self.add_executed_action(action)

        if len(self.flowers_collected) > 0:
            action.message = "Cannot clean obstacle while holding flowers"
            return action

        self.obstacles_cleaned.append(obstacle_position)
        return action

    def can_clean(self) -> bool:
        return len(self.flowers_collected) == 0

    def can_pick(self) -> bool:
        return len(self.flowers_collected) < self.max_flowers

    @property
    def flowers_held(self) -> int:
        """Return the number of flowers currently held."""
        return len(self.flowers_collected)

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
            "executed_actions": [action.to_dict() for action in self.executed_actions],
        }
