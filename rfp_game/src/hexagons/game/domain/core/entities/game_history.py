from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from ..value_objects.action_type import ActionType
from ..value_objects.direction import Direction


@dataclass
class Action:
    action_type: ActionType
    direction: Direction | None = None
    success: bool = True
    message: str = ""


@dataclass
class GameHistory:
    game_id: str = ""
    actions: List[Action] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def add_action(self, action: Action | None) -> None:
        """Record an action."""
        if action:
            self.actions.append(action)
            self.updated_at = datetime.now()

    @property
    def actions_count(self) -> int:
        """Get the total number of actions."""
        return len(self.actions)

    def to_dict(self) -> dict:
        """Convert history to dictionary."""
        return {
            "game_id": self.game_id,
            "actions_count": self.actions_count,
            "created_at": self.created_at.isoformat() + "Z",
            "updated_at": self.updated_at.isoformat() + "Z",
            "actions": [
                {
                    "action_type": action.action_type.value,
                    "direction": action.direction.value if action.direction else None,
                    "success": action.success,
                    "message": action.message,
                }
                for action in self.actions
            ],
        }
