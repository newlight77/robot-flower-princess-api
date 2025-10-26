import copy
from dataclasses import dataclass, field
from typing import Literal
from .position import Position
from typing import List

@dataclass
class Princess:
    position: Position
    flowers_received: List[Position] = field(default_factory=list)
    mood: Literal["happy", "sad", "angry", "neutral"] = "neutral"

    def receive_flowers(self, flowers: List[Position]) -> None:
        """Receive flowers from the robot and update mood accordingly."""
        self.flowers_received = copy.deepcopy(flowers)
        self._update_mood()

    def _update_mood(self) -> None:
        """Update mood based on flowers received."""
        if len(self.flowers_received) == 0:
            self.mood = "sad"
        elif len(self.flowers_received) < 3:
            self.mood = "neutral"
        elif len(self.flowers_received) < 6:
            self.mood = "happy"
        else:
            self.mood = "happy"  # Very happy with many flowers

    def to_dict(self) -> dict:
        """Convert princess to dictionary representation."""
        return {
            "position": {"row": self.position.row, "col": self.position.col},
            "flowers_received": [flower.to_dict() for flower in self.flowers_received],
            "mood": self.mood,
        }
