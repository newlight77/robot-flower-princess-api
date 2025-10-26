from enum import Enum
from datetime import datetime
from .direction import Direction


class ActionType(str, Enum):
    ROTATE = "rotate"
    MOVE = "move"
    PICK = "pickFlower"
    DROP = "dropFlower"
    GIVE = "giveFlower"
    CLEAN = "clean"

class Action:
    def __init__(
        self,
        action_type: ActionType,
        direction: Direction = None,
        message: str = None,
        executed_at: datetime = None,
        flower_position=None,
        drop_position=None,
        princess_position=None,
        obstacle_position=None,
    ):
        self.type = action_type
        self.direction = direction
        self.message = message
        self.executed_at = executed_at or datetime.now()
        self.flower_position = flower_position
        self.drop_position = drop_position
        self.princess_position = princess_position
        self.obstacle_position = obstacle_position

    def to_dict(self) -> dict:
        result = {
            "type": self.type.value,
            "direction": self.direction.value if self.direction else None,
            "executed_at": self.executed_at.isoformat(),
        }
        if self.message:
            result["message"] = self.message
        return result