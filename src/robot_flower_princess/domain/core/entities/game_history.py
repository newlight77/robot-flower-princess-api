from dataclasses import dataclass, field
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
    actions: List[Action] = field(default_factory=list)
    game_states: List[dict] = field(default_factory=list)

    def add_action(self, action: Action | None, game_state: dict) -> None:
        """Record an action and the resulting game state."""
        if action:
            self.actions.append(action)
        self.game_states.append(game_state)

    def to_dict(self) -> dict:
        """Convert history to dictionary."""
        return {
            "total_actions": len(self.actions),
            "actions": [
                {
                    "action_type": action.action_type.value,
                    "direction": action.direction.value if action.direction else None,
                    "success": action.success,
                    "message": action.message,
                }
                for action in self.actions
            ],
            "game_states": self.game_states,
        }
